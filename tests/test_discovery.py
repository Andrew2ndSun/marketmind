"""Market-radar freshness, validation, caching and failure-path tests."""
import copy
import json
import os
import threading
import unittest
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from marketmind import discovery
from marketmind.app import create_app
from marketmind.discovery import MarketRadar, build_scan, scan_market, validate_radar, research_context
from marketmind.discovery_data import normalize_quotes, parse_feed, collect_market
from marketmind.errors import ResearchUnavailable, SynthesisError

RealClient = httpx.Client


def inputs():
    now = datetime.now(timezone.utc).isoformat()
    candidates = [{"ticker":f"STK{i}","company":f"Invented company {i}","price":100.0+i,
                   "change_pct":float(i-5),"volume":100000,"currency":"USD","quote_at":now,
                   "screeners":["most_actives"],"sector":"Technology","industry":"Software"}
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
        patches = [patch.dict(os.environ,{"MUSE_API_KEY":"test-secret"},clear=True),
                   patch.object(discovery,"_cached",None),patch.object(discovery,"_cached_at",0),
                   patch.object(discovery,"_lock",threading.Lock())]
        for item in patches:
            item.start();self.addCleanup(item.stop)
        self.client=TestClient(create_app());self.addCleanup(self.client.close)

    def transport(self, payload):
        def respond(request):
            self.assertEqual(str(request.url),'https://api.meta.ai/v1/chat/completions')
            self.assertIn('EXACTLY 10',json.loads(request.content)['messages'][0]['content'])
            return httpx.Response(200,json={"choices":[{"finish_reason":"stop","message":{"content":json.dumps(payload)}}],
                                          "usage":{"prompt_tokens":120,"completion_tokens":80}})
        return patch('marketmind.muse.httpx.Client',side_effect=lambda **kwargs:RealClient(**kwargs,transport=httpx.MockTransport(respond)))

    def test_full_scan_selects_ten_real_pool_symbols_with_quotes_and_sources(self):
        with patch('marketmind.discovery.collect_market',side_effect=inputs),self.transport(model_result()):
            response=self.client.get('/api/discovery')
        self.assertEqual(response.status_code,200)
        data=response.json()
        self.assertEqual(len(data['stocks']),10)
        self.assertEqual(len({stock['ticker'] for stock in data['stocks']}),10)
        self.assertEqual(data['candidate_count'],12)
        self.assertEqual(data['headline_count'],1)
        self.assertEqual(data['stocks'][0]['snapshot']['price'],100)
        self.assertEqual(data['inference']['provider'],'meta-model-api')
        self.assertNotIn('test-secret',response.text)

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

    def test_invalid_model_scan_is_502_and_not_cached(self):
        result=model_result();result['stocks'][0]['ticker']='INVENTED'
        with patch('marketmind.discovery.collect_market',side_effect=inputs),self.transport(result):
            response=self.client.get('/api/discovery')
        self.assertEqual(response.status_code,502)
        self.assertIsNone(discovery._cached)

    def test_cache_reuses_result_and_enforces_refresh_cooldown(self):
        with patch('marketmind.discovery.build_scan',return_value={'stocks':[{'ticker':'STK0'}]}) as build:
            with patch('marketmind.discovery.time.monotonic',return_value=1000):
                self.assertFalse(scan_market()['cached'])
            with patch('marketmind.discovery.time.monotonic',return_value=1020):
                cached=scan_market(refresh=True)
                self.assertTrue(cached['cached'])
                cached['stocks'][0]['ticker']='MUTATED'
                self.assertEqual(scan_market()['stocks'][0]['ticker'],'STK0')
            self.assertEqual(build.call_count,1)
            with patch('marketmind.discovery.time.monotonic',return_value=1061):
                self.assertFalse(scan_market(refresh=True)['cached'])
            self.assertEqual(build.call_count,2)
            with patch('marketmind.discovery.time.monotonic',return_value=2000):
                self.assertFalse(scan_market()['cached'])

    def test_concurrent_scan_is_rejected_without_starting_second_call(self):
        discovery._lock.acquire()
        try:
            with patch('marketmind.discovery.build_scan') as build:
                with self.assertRaises(ResearchUnavailable):scan_market()
                build.assert_not_called()
        finally:discovery._lock.release()

    def test_missing_key_fails_before_fetching_market(self):
        with patch.dict(os.environ,{},clear=True),patch('marketmind.discovery.collect_market') as collect:
            self.assertEqual(self.client.get('/api/discovery').status_code,503)
            collect.assert_not_called()

    def test_feed_filters_old_future_undated_and_unsafe_items(self):
        now=datetime.now(timezone.utc)
        def item(title,date,url='https://example.com/story'):
            return f'<item><title>{title}</title><link>{url}</link><pubDate>{date}</pubDate><description>&lt;b&gt;Brief excerpt&lt;/b&gt;</description></item>'
        xml='<rss><channel>'+item('Valid',format_datetime(now))+item('Old',format_datetime(now-timedelta(days=8)))+item('Future',format_datetime(now+timedelta(days=1)))+item('No date','')+item('Unsafe',format_datetime(now),'javascript:alert(1)')+'</channel></rss>'
        result=parse_feed(xml.encode(),'Test source',now)
        self.assertEqual([r['title'] for r in result],['Valid'])
        self.assertEqual(result[0]['excerpt'],'Brief excerpt')

    def test_quotes_filter_invalid_and_stale_and_merge_screeners(self):
        now=datetime.now(timezone.utc)
        valid={'symbol':'ABC','shortName':'Company','quoteType':'EQUITY','regularMarketPrice':100,
               'regularMarketChangePercent':2,'regularMarketTime':now.timestamp()}
        bad=[{**valid,'symbol':'ZERO','regularMarketPrice':0}, {**valid,'symbol':'OLD','regularMarketTime':(now-timedelta(days=8)).timestamp()},
             {**valid,'symbol':'NAN','regularMarketChangePercent':float('nan')}, {**valid,'symbol':'FUND','quoteType':'ETF'}]
        result=normalize_quotes([('most_actives',[valid,*bad]),('day_gainers',[valid])],now)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['screeners'],['most_actives','day_gainers'])

    def test_collection_requires_ten_candidates_and_recent_news(self):
        with patch('marketmind.discovery_data.yf.screen',return_value={'quotes':[]}),patch('marketmind.discovery_data.fetch_headlines',return_value=[]):
            with self.assertRaises(ResearchUnavailable):collect_market()
        candidates,_,_=inputs()
        with patch('marketmind.discovery_data.yf.screen',return_value={'quotes':[]}),patch('marketmind.discovery_data.fetch_headlines',return_value=[]),patch('marketmind.discovery_data.normalize_quotes',return_value=candidates),patch('marketmind.discovery_data.enrich_sector',side_effect=lambda c:c):
            with self.assertRaises(ResearchUnavailable):collect_market()

    def test_selected_stock_passes_original_sources_not_generated_claims(self):
        with patch('marketmind.discovery.collect_market',side_effect=inputs),self.transport(model_result()):
            data=scan_market()
        context=research_context('STK0',data['created_at'])
        self.assertEqual({item['id'] for item in context},{'RC1','RH1'})
        self.assertTrue(all('reason' not in item for item in context))
        self.assertEqual(research_context('INVENTED',data['created_at']),[])
        self.assertEqual(research_context('STK0','old-scan'),[])
        with patch('marketmind.discovery.time.monotonic',return_value=discovery._cached_at+901):
            self.assertEqual(research_context('STK0',data['created_at']),[])

    def test_deep_research_receives_selected_radar_headlines(self):
        from marketmind.schemas import Synthesis
        from tests.fixtures import inputs as stock_inputs, completion as stock_completion
        with patch('marketmind.discovery.collect_market',side_effect=inputs),self.transport(model_result()):
            scan=scan_market()
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


if __name__=='__main__':unittest.main()
