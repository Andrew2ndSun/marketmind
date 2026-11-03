"""News-led radar, durable scheduling and read-only front page tests."""
import json
import os
import threading
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from marketmind import discovery, discovery_store as store
from marketmind.app import create_app
from marketmind.discovery import MarketRadar, NewsDiscovery, build_scan, scan_market, validate_radar, research_context
from marketmind.discovery_data import parse_feed, collect_news, resolve_company, resolve_candidates
from marketmind.errors import ResearchUnavailable, SynthesisError

def inputs():
    now = datetime.now(timezone.utc).isoformat()
    candidates = [{"ticker":f"STK{i}","company":f"Invented company {i}","price":100.0+i,
                   "change_pct":float(i-5),"volume":100000,"currency":"USD","quote_at":now,
                   "sector":"Technology","industry":"Software"}
                  for i in range(12)]
    headlines = [{"title":"Invented economic headline","url":"https://example.com/economy",
                  "publisher":"Test source","published_at":now,"excerpt":"Invented test evidence."}]
    return candidates, headlines, []


def model_result():
    return {"overview":{"text":"Current attention has uncertain economic links.","evidence_ids":["H1"]},
            "themes":[{"title":"Economic sensitivity","impact":"A possible channel, not established causation.",
                       "industries":["Software"],"evidence_ids":["H1"]}],
            "stocks":[{"ticker":f"STK{i}","theme":"Economic sensitivity","reason":"Possible connection to the headline.",
                       "risk":"The link may not explain this price move.","evidence_ids":[f"C{i+1}","H1"]}
                      for i in range(10)]}


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        patches = [patch.dict(os.environ, {"MUSE_API_KEY": "test-secret"}, clear=True),
                   patch.object(store, "DATA_DIR", Path(temporary.name)),
                   patch.object(store, "_state", {"running": False, "last_error": None, "last_attempt_at": None}),
                   patch.object(store, "_lock", threading.Lock())]
        for item in patches:
            item.start(); self.addCleanup(item.stop)
        self.client = TestClient(create_app()); self.addCleanup(self.client.close)

    def inference(self, prompt, data, schema):
        usage = {"provider": "meta-model-api", "model": "muse-test"}
        if schema is NewsDiscovery:
            ids = [item["id"] for item in data["headlines"]]
            return NewsDiscovery(companies=[{"company": f"Invented company {i}", "ticker": f"STK{i}", "evidence_ids": [ids[0]]} for i in range(12)]), usage
        return MarketRadar.model_validate(model_result()), usage

    def build(self):
        candidates, headlines, warnings = inputs()
        with patch('marketmind.discovery.collect_news', return_value=(headlines, warnings)), patch('marketmind.discovery.resolve_candidates', return_value=(candidates, [])), patch('marketmind.discovery.complete_json', side_effect=self.inference):
            return build_scan()

    def save_scan(self):
        data = self.build()
        (store.DATA_DIR / 'latest.json').write_text(json.dumps(data), encoding='utf-8')
        return data

    def test_full_scan_is_news_led_and_returns_ten_verified_symbols(self):
        data = self.build()
        self.assertEqual(len(data['stocks']), 10)
        self.assertEqual(data['candidate_count'], 12)
        self.assertEqual(data['stocks'][0]['snapshot']['price'], 100)
        self.assertEqual(data['scan_interval_seconds'], 7200)
        self.assertIn('no fixed watchlist', data['scope'])

    def test_all_headlines_are_reviewed_in_batches_without_first_n_truncation(self):
        candidates, headlines, _ = inputs()
        headlines = [{**headlines[0], 'title': f'Headline {i}'} for i in range(171)]
        visited = []
        def complete(prompt, data, schema):
            if schema is NewsDiscovery: visited.extend(item['id'] for item in data['headlines'])
            return self.inference(prompt, data, schema)
        with patch('marketmind.discovery.collect_news', return_value=(headlines, [])), patch('marketmind.discovery.resolve_candidates', return_value=(candidates, [])), patch('marketmind.discovery.complete_json', side_effect=complete):
            result = build_scan()
        self.assertEqual(visited, [f'H{i}' for i in range(1,172)])
        self.assertEqual(result['headline_count'], 171)

    def test_duplicate_invented_and_cross_stock_citations_are_rejected(self):
        candidates,headlines,_=inputs()
        for i,candidate in enumerate(candidates,1):candidate['evidence_id']=f'C{i}'
        evidence=[{'id':c['evidence_id'],'kind':'market'} for c in candidates]+[{'id':'H1','kind':'headline'}]
        mutations = [lambda d:d['stocks'][1].update(ticker='STK0'),
                     lambda d:d['stocks'][0].update(ticker='INVENTED'),
                     lambda d:d['stocks'][0].update(evidence_ids=['C2','H1']),
                     lambda d:d['stocks'][0].update(evidence_ids=['C1','C2']),
                     lambda d:d['overview'].update(evidence_ids=['BAD']),
                     lambda d:d['themes'][0].update(evidence_ids=['C1'])]
        for mutate in mutations:
            result=model_result();mutate(result)
            with self.assertRaises(ValueError):validate_radar(MarketRadar.model_validate(result),candidates,evidence)
        result=model_result();result['stocks'].pop()
        with self.assertRaises(ValueError):MarketRadar.model_validate(result)

    def test_unknown_news_extraction_citation_is_rejected(self):
        def invalid(prompt, data, schema):
            result, usage = self.inference(prompt, data, schema)
            if schema is NewsDiscovery: result.companies[0].evidence_ids = ['H999']
            return result, usage
        with patch('marketmind.discovery.collect_news', return_value=(inputs()[1], [])), patch('marketmind.discovery.complete_json', side_effect=invalid), patch('marketmind.discovery.resolve_candidates') as resolve:
            with self.assertRaises(SynthesisError): build_scan()
            resolve.assert_not_called()

    def test_get_is_read_only_even_with_refresh_query_and_no_key(self):
        self.save_scan()
        with patch.dict(os.environ, {}, clear=True), patch('marketmind.discovery.build_scan') as build:
            for url in ['/api/discovery', '/api/discovery?refresh=true']:
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()['stocks']), 10)
                self.assertNotIn('test-secret', response.text)
            build.assert_not_called()

    def test_first_visit_pending_does_not_start_inference(self):
        with patch('marketmind.discovery.build_scan') as build:
            self.assertEqual(self.client.get('/api/discovery').json()['status'], 'pending')
            build.assert_not_called()

    def test_two_hour_schedule_persists_and_survives_memory_reset(self):
        data = self.build()
        with patch('marketmind.discovery.build_scan', return_value=data) as build:
            self.assertTrue(store.update_if_due())
            self.assertFalse(store.update_if_due())
            build.assert_called_once()
            created = datetime.fromisoformat(data['created_at'])
            with patch.object(store, 'utcnow', return_value=created+timedelta(seconds=7199)):
                self.assertFalse(store.update_if_due())
            with patch.object(store, 'utcnow', return_value=created+timedelta(seconds=7201)):
                self.assertTrue(store.update_if_due())
            self.assertEqual(build.call_count, 2)
        self.assertEqual(store.load_snapshot()['created_at'], data['created_at'])
        self.assertEqual(scan_market()['stocks'][0]['ticker'], 'STK0')

    def test_failed_update_keeps_last_good_snapshot_and_retries_after_fifteen_minutes(self):
        data = self.save_scan()
        created = datetime.fromisoformat(data['created_at'])
        with patch.object(store, 'utcnow', return_value=created+timedelta(hours=3)), patch('marketmind.discovery.build_scan', side_effect=RuntimeError('private upstream detail')) as build:
            self.assertFalse(store.update_if_due())
            self.assertFalse(store.update_if_due())
            build.assert_called_once()
            result = scan_market()
            self.assertTrue(result['stale'])
            self.assertEqual(result['stocks'], data['stocks'])
            self.assertNotIn('private upstream detail', json.dumps(result))
        with patch.object(store, 'utcnow', return_value=created+timedelta(hours=3,minutes=16)), patch('marketmind.discovery.build_scan', return_value=data):
            self.assertTrue(store.update_if_due())

    def test_concurrent_workers_do_not_start_second_scan(self):
        store._lock.acquire()
        try:
            with patch('marketmind.discovery.build_scan') as build:
                self.assertFalse(store.update_if_due())
                build.assert_not_called()
        finally: store._lock.release()

    def test_corrupt_saved_data_is_pending_and_does_not_crash_front_page(self):
        (store.DATA_DIR/'latest.json').write_text('{broken', encoding='utf-8')
        self.assertEqual(scan_market()['status'], 'pending')

    def test_missing_key_fails_before_news_collection(self):
        with patch.dict(os.environ, {}, clear=True), patch('marketmind.discovery.collect_news') as collect:
            with self.assertRaises(ResearchUnavailable): build_scan()
            collect.assert_not_called()

    def test_feed_filters_old_future_undated_and_unsafe_items(self):
        now=datetime.now(timezone.utc)
        def item(title,date,url='https://example.com/story'):
            return f'<item><title>{title}</title><link>{url}</link><pubDate>{date}</pubDate><description>&lt;b&gt;Brief excerpt&lt;/b&gt;</description></item>'
        xml='<rss><channel>'+item('Valid',format_datetime(now))+item('Old',format_datetime(now-timedelta(days=8)))+item('Future',format_datetime(now+timedelta(days=1)))+item('No date','')+item('Unsafe',format_datetime(now),'javascript:alert(1)')+'</channel></rss>'
        result=parse_feed(xml.encode(),'Test source',now)
        self.assertEqual([r['title'] for r in result],['Valid'])
        self.assertEqual(result[0]['excerpt'],'Brief excerpt')

    def test_feed_keeps_more_than_eight_recent_stories(self):
        now = datetime.now(timezone.utc)
        items = ''.join(f'<item><title>Story {i}</title><link>https://example.com/{i}</link><pubDate>{format_datetime(now)}</pubDate></item>' for i in range(25))
        self.assertEqual(len(parse_feed(('<rss><channel>'+items+'</channel></rss>').encode(), 'Test', now)),25)

    def test_news_collection_deduplicates_and_requires_recent_news(self):
        with patch('marketmind.discovery_data.fetch_headlines', return_value=inputs()[1]):
            news, _ = collect_news()
            self.assertEqual(len(news), 1)
        with patch('marketmind.discovery_data.fetch_headlines', return_value=[]):
            with self.assertRaises(ResearchUnavailable): collect_news()

    def test_company_resolution_requires_matching_identity_and_fresh_equity_quote(self):
        proposal = {'company': 'Example Company', 'ticker': 'ABC', 'evidence_ids':['H1']}
        valid = {'symbol':'ABC', 'quoteType':'EQUITY', 'regularMarketPrice':100, 'regularMarketChangePercent':2, 'regularMarketTime':datetime.now(timezone.utc).timestamp()}
        with patch('marketmind.discovery_data.yf.Search') as search, patch('marketmind.discovery_data.yf.Ticker') as ticker:
            search.return_value.quotes=[{'symbol':'ABC','quoteType':'EQUITY'}]
            ticker.return_value.get_info.return_value=valid
            self.assertEqual(resolve_company(proposal)['ticker'], 'ABC')
            for changes in [{'symbol':'OTHER'}, {'quoteType':'ETF'}, {'regularMarketPrice':0}, {'regularMarketChangePercent':float('nan')}, {'regularMarketTime':(datetime.now(timezone.utc)-timedelta(days=8)).timestamp()}]:
                ticker.return_value.get_info.return_value={**valid, **changes}
                self.assertIsNone(resolve_company(proposal))
            search.return_value.quotes=[{'symbol':'OTHER','quoteType':'EQUITY'}]
            self.assertIsNone(resolve_company(proposal))

    def test_verification_requires_at_least_ten_unique_valid_symbols(self):
        with patch('marketmind.discovery_data.resolve_company', return_value=None):
            with self.assertRaises(ResearchUnavailable): resolve_candidates([{}]*12)

    def test_selected_stock_uses_saved_original_sources_and_expires_after_day(self):
        data = self.save_scan()
        context = research_context('STK0', data['created_at'])
        self.assertEqual({item['id'] for item in context}, {'RC1','RH1'})
        self.assertTrue(all('reason' not in item for item in context))
        self.assertEqual(research_context('STK0', 'old'), [])
        self.assertEqual(research_context('INVENTED', data['created_at']), [])
        class Later(datetime):
            @classmethod
            def now(cls, tz=None): return datetime.fromisoformat(data['created_at'])+timedelta(days=2)
        with patch.object(discovery, 'datetime', Later):
            self.assertEqual(research_context('STK0', data['created_at']), [])

    def test_scheduler_starts_at_app_start_and_stops_at_shutdown(self):
        with patch('marketmind.discovery_store.start_scheduler') as start:
            stop, worker = start.return_value = (Mock(), Mock())
            with TestClient(create_app()): start.assert_called_once()
            stop.set.assert_called_once()
            worker.join.assert_called_once()

    def test_deep_research_receives_selected_radar_headlines(self):
        from marketmind.schemas import Synthesis
        from tests.fixtures import inputs as stock_inputs, completion as stock_completion
        scan=self.save_scan()
        result=Synthesis.model_validate_json(stock_completion()['choices'][0]['message']['content'])
        with patch('marketmind.research.live_inputs',side_effect=lambda ticker:stock_inputs()),patch('marketmind.research.synthesize',return_value=(result,{})) as synthesize:
            response=self.client.post('/api/research',json={'ticker':'STK0','discovery_created_at':scan['created_at']})
        self.assertEqual(response.status_code,200)
        ids={item['id'] for item in synthesize.call_args.args[1]}
        self.assertTrue({'M1','F1','RC1','RH1'} <= ids)

    def test_research_reports_expired_radar_context_instead_of_inventing_it(self):
        from marketmind.schemas import Synthesis
        from tests.fixtures import inputs as stock_inputs, completion as stock_completion
        result=Synthesis.model_validate_json(stock_completion()['choices'][0]['message']['content'])
        with patch('marketmind.research.live_inputs',side_effect=lambda ticker:stock_inputs()),patch('marketmind.research.synthesize',return_value=(result,{})):
            response=self.client.post('/api/research',json={'ticker':'AMD','discovery_created_at':'old-scan'})
        self.assertEqual(response.status_code,200)
        self.assertTrue(any('expired or changed' in text for text in response.json()['quality']['warnings']))

    def test_front_page_has_independent_radar_assets(self):
        html=self.client.get('/').text
        self.assertIn('10 stocks in the spotlight',html)
        self.assertIn('/static/discovery.js',html)
        self.assertEqual(self.client.get('/static/discovery.js').status_code,200)



if __name__=='__main__': unittest.main()
