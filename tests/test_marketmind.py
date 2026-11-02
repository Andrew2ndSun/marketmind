"""Offline tests of the Muse-only application and evidence integrity."""
import json
import os
import unittest
from unittest.mock import patch

import httpx
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from marketmind.app import create_app
from marketmind.config import muse_settings
from marketmind.data import normalize_news, fetch_price_history
from marketmind.errors import ResearchUnavailable, SynthesisError
from marketmind.metrics import historical_metrics
from marketmind.muse import synthesize
from tests.fixtures import inputs, completion

RealClient = httpx.Client


class MarketMindTests(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(os.environ, {'MUSE_API_KEY':'test-secret'}, clear=True)
        environment.start()
        self.addCleanup(environment.stop)
        self.client = TestClient(create_app())
        self.addCleanup(self.client.close)

    def transport(self, handler):
        return patch('marketmind.muse.httpx.Client',
                     side_effect=lambda **kwargs: RealClient(**kwargs, transport=httpx.MockTransport(handler)))

    def evidence(self):
        return [{'id':'M1'}, {'id':'F1'}]

    def test_end_to_end_api_uses_muse_and_keeps_data_gaps_visible(self):
        calls=[]
        def respond(request):
            calls.append(request)
            body=json.loads(request.content)
            self.assertEqual(body['model'],'muse-spark-1.3')
            self.assertEqual(body['max_completion_tokens'],8192)
            self.assertEqual(body['reasoning_effort'],'low')
            self.assertNotIn('temperature',body)
            self.assertIn('M1',body['messages'][1]['content'])
            self.assertEqual(request.headers['authorization'],'Bearer test-secret')
            return httpx.Response(200,json=completion())
        with patch('marketmind.research.live_inputs',return_value=inputs()), self.transport(respond):
            response=self.client.post('/api/research',json={'ticker':' amd '})
        self.assertEqual(response.status_code,200)
        report=response.json()
        self.assertEqual(report['ticker'],'AMD')
        self.assertEqual(report['mode'],'live')
        self.assertEqual(report['inference']['provider'],'meta-model-api')
        self.assertEqual(report['inference']['output_tokens'],50)
        self.assertEqual(str(calls[0].url),'https://api.meta.ai/v1/chat/completions')
        self.assertFalse(report['quality']['citation_support_verified'])
        self.assertEqual(report['quality']['news_count'],0)
        self.assertTrue(report['quality']['warnings'])
        self.assertNotIn('test-secret',response.text)

    def test_muse_keys_and_fixed_endpoint(self):
        for name in ['MUSE_API_KEY','MODEL_API_KEY']:
            with self.subTest(variable=name), patch.dict(os.environ,{
                name:'muse-secret','META_API_KEY':'ignored','META_MODEL':'other-model',
                'META_BASE_URL':'https://other.example','MUSE_BASE_URL':'https://other.example',
            },clear=True):
                settings=muse_settings()
                self.assertEqual(settings.api_key,'muse-secret')
                self.assertEqual(settings.model,'muse-spark-1.3')
                self.assertNotIn('muse-secret',repr(settings))
                def respond(request):
                    self.assertEqual(str(request.url),'https://api.meta.ai/v1/chat/completions')
                    return httpx.Response(200,json=completion())
                with self.transport(respond) as client:
                    synthesize('Research question',self.evidence())
                self.assertFalse(client.call_args.kwargs['follow_redirects'])
        with patch.dict(os.environ,{'MUSE_MODEL':'gpt-other'}):
            self.assertEqual(self.client.get('/api/research/status').status_code,503)

    def test_missing_muse_key_fails_before_collecting_data(self):
        with patch.dict(os.environ,{'OPENAI_API_KEY':'ignored','META_API_KEY':'ignored'},clear=True), patch('marketmind.research.live_inputs') as collect:
            self.assertEqual(self.client.post('/api/research',json={'ticker':'AMD'}).status_code,503)
            collect.assert_not_called()

    def test_bad_inputs_and_removed_demo_parameter(self):
        for body in [{'ticker':'../../etc'}, {'ticker':'AMD','question':'   '},
                     {'ticker':'AMD','demo':True}, {'ticker':'AMD','api_key':'unaccepted'}]:
            self.assertEqual(self.client.post('/api/research',json=body).status_code,422)

    def test_invalid_citations_json_truncation_and_redirects_fail(self):
        bad_id=completion()
        bad_report=json.loads(bad_id['choices'][0]['message']['content'])
        bad_report['summary']['evidence_ids']=['INVENTED']
        bad_id['choices'][0]['message']['content']=json.dumps(bad_report)
        invalid_json=completion(); invalid_json['choices'][0]['message']['content']='not json'
        truncated=completion(); truncated['choices'][0]['finish_reason']='length'
        for payload in [bad_id,invalid_json,truncated]:
            with self.subTest(payload=payload), self.transport(lambda request: httpx.Response(200,json=payload)):
                with self.assertRaises(SynthesisError): synthesize('Research question',self.evidence())
        calls=[]
        def redirect(request):
            calls.append(request)
            return httpx.Response(302,headers={'location':'https://other.example'})
        with self.transport(redirect):
            with self.assertRaises(SynthesisError): synthesize('Research question',self.evidence())
        self.assertEqual(len(calls),1)

    def test_provider_failure_does_not_expose_response_body(self):
        with self.transport(lambda request: httpx.Response(401,json={'error':'private provider body'})), patch('marketmind.research.live_inputs',return_value=inputs()):
            response=self.client.post('/api/research',json={'ticker':'AMD'})
        self.assertEqual(response.status_code,502)
        self.assertNotIn('private provider body',response.text)
        self.assertNotIn('test-secret',response.text)

    def test_risk_math_and_invalid_history(self):
        prices=pd.Series([100.]*29+[80.],index=pd.bdate_range('2025-01-01',periods=30))
        metrics=historical_metrics(prices)
        self.assertAlmostEqual(metrics['max_drawdown_pct'],-20)
        self.assertAlmostEqual(metrics['twenty_session_return_pct'],-20)
        self.assertAlmostEqual(metrics['annualized_volatility_pct'],prices.pct_change().dropna().std()*np.sqrt(252)*100,places=2)
        duplicate=prices.copy(); duplicate.index=[prices.index[0]]*30
        for bad in [prices.iloc[:5],prices*0,prices.replace(80,np.inf),prices.replace(80,np.nan),duplicate]:
            with self.assertRaises(ResearchUnavailable): historical_metrics(bad)

    def test_market_data_excludes_today_and_rejects_split_mismatch(self):
        today=pd.Timestamp.now(tz='America/New_York').tz_localize(None).normalize()
        frame=pd.DataFrame({'Close':[100.,101.,102.]},index=pd.bdate_range(end=today,periods=3))
        with patch('marketmind.data._history',return_value=frame), patch('marketmind.data._spot_price',return_value=101):
            prices=fetch_price_history('AMD')
        self.assertTrue((prices.index < today).all())
        with patch('marketmind.data._history',return_value=frame), patch('marketmind.data._spot_price',return_value=1):
            self.assertTrue(fetch_price_history('AMD').empty)

    def test_news_formats_deduplication_and_unsafe_urls(self):
        articles=[{'content':{'title':'Modern','canonicalUrl':{'url':'https://example.com/a'},'provider':{'displayName':'Publisher'}}},
                  {'title':'Legacy','link':'https://example.com/b'}, {'title':'Bad','link':'javascript:alert(1)'},
                  {'title':'Duplicate','link':'https://example.com/b'}]
        news=normalize_news(articles)
        self.assertEqual(len(news),2)
        self.assertEqual(news[0]['publisher'],'Publisher')

    def test_dashboard_health_and_only_research_routes(self):
        self.assertEqual(self.client.get('/api/health').json()['service'],'marketmind')
        home=self.client.get('/').text
        self.assertIn('MarketMind',home)
        self.assertIn('MarketMind / Powered by Muse',home)
        self.assertNotIn('id="mode"',home)
        self.assertEqual(self.client.get('/static/marketmind.js').status_code,200)
        self.assertEqual(set(self.client.get('/openapi.json').json()['paths']),{'/api/health','/api/research/status','/api/research'})
        self.assertEqual(self.client.get('/desk').status_code,404)
        status=self.client.get('/api/research/status').json()
        self.assertTrue(status['live_configured'])
        self.assertNotIn('test-secret',json.dumps(status))


if __name__=='__main__':
    unittest.main()
