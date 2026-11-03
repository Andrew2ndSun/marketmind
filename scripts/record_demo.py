"""Record a captioned, real Muse walkthrough; requires optional playwright install.

Run: python scripts/record_demo.py
The app must already be running at localhost:8000 with Muse configured.
No model response is mocked. The local video is excluded from Git.
"""
import json
import shutil
from datetime import datetime, timezone

import httpx
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts"
OUTPUT.mkdir(exist_ok=True)


def caption(page, title, text):
    page.evaluate("""([title,text]) => {
      let n=document.getElementById('recording-caption');
      if(!n){ n=document.createElement('div'); n.id='recording-caption'; document.body.append(n); }
      n.style.cssText='position:fixed;bottom:16px;left:4%;right:4%;padding:16px 22px;border:1px solid #acedd5;border-radius:10px;background:#10231ff5;color:#e6edf0;font:17px/1.5 Segoe UI,sans-serif;z-index:99999;box-shadow:0 4px 20px #0008;';
      n.replaceChildren(); const b=document.createElement('strong'); b.textContent=title; b.style.color='#acedd5';
      const p=document.createElement('div');p.textContent=text;n.append(b,p);
    }""", [title,text])


def hold_until(page, started, second):
    while time.monotonic()-started < second:
        page.wait_for_timeout(min(500,max(1,(second-(time.monotonic()-started))*1000)))


# Wait for a real saved scan before starting the three-minute recording clock.
radar = httpx.get('http://127.0.0.1:8000/api/discovery', timeout=15).json()
if radar.get('status') != 'ready' or len(radar.get('stocks', [])) != 10 or radar.get('stale'):
    raise RuntimeError('Start the server and allow a fresh scheduled scan to complete before recording.')
previous = OUTPUT / 'previous-demo'
previous.mkdir(exist_ok=True)
for name in ('marketmind-demo.webm', 'demo-report.json', 'recording-receipt.json'):
    source = OUTPUT / name
    if source.exists():
        shutil.copy2(source, previous / name)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width":1280,"height":900}, record_video_dir=str(OUTPUT), record_video_size={"width":1280,"height":900})
    page = context.new_page()
    errors, research_requests = [], []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('request', lambda request: research_requests.append(request.url) if request.method == 'POST' and request.url.endswith('/api/research') else None)
    page.goto('http://127.0.0.1:8000', wait_until='networkidle')
    started = time.monotonic()
    page.locator('.radar-card').last.wait_for(state='visible', timeout=5000)
    page.locator('#market-radar').scroll_into_view_if_needed()
    caption(page, 'MarketMind | Build for Your World', 'A background Muse job scans broad economic and business news every two hours. This saved top 10 loads immediately, without another model call.')
    hold_until(page, started, 9)
    page.locator('.radar-card').first.scroll_into_view_if_needed()
    caption(page, 'Discovery starts from news, without a fixed watchlist', str(radar['headline_count'])+' recent headlines led to '+str(radar['candidate_count'])+' verified companies and ten research candidates. Each card explains a potential link, a risk and its sources.')
    hold_until(page, started, 18)
    page.locator('#radar-details').evaluate('(n)=>n.open=true')
    page.locator('#radar-method').scroll_into_view_if_needed()
    caption(page, 'Saved evidence and transparent coverage', 'Nine configured news and economic feeds cover multiple industries. This is broad feed coverage, not every story on the internet. Quotes are saved snapshots, not live prices.')
    hold_until(page, started, 26)
    page.locator('#radar-details').evaluate('(n)=>n.open=false')
    ticker = page.locator('.radar-card h3').first.inner_text()
    page.locator('.radar-select').first.click()
    if page.locator('#research-form').get_attribute('data-radar-created-at') != radar['created_at']:
        raise RuntimeError('The scheduled scan changed before selection; restart recording with the new snapshot.')
    if research_requests:
        raise RuntimeError('Selecting a stock must not start research automatically.')
    caption(page, 'My new hackathon work', 'I built the scheduled news radar, Muse integration, cited reports and validation on an earlier data-fetching foundation. Selecting a stock fills the form; I choose when to investigate.')
    hold_until(page, started, 33)
    caption(page, 'A real Muse investigation', 'This request collects stock-specific evidence and carries original sources from the saved radar into Muse. Missing inputs stay visible; no fixed report is substituted.')
    with page.expect_response(lambda response: response.url.endswith('/api/research') and response.request.method == 'POST', timeout=120000) as pending:
        page.get_by_role('button', name='Investigate').click()
    response = pending.value
    report = response.json()
    if response.status != 200:
        raise RuntimeError('Live research failed; no success video will be produced.')
    if time.monotonic()-started > 65:
        raise RuntimeError('Request exceeded the recording segment; retry rather than fabricate success.')
    source_ids = {item['id'] for item in report['evidence']}
    if not any(item.startswith('RH') for item in source_ids):
        raise RuntimeError('Selected radar headlines were not carried into real research.')
    page.locator('#report').wait_for(state='visible')
    page.locator('#report').scroll_into_view_if_needed()
    caption(page, 'A cited research brief for '+ticker, 'Muse separates observations from hypotheses. Each accepted claim references evidence IDs supplied by MarketMind; citation validation does not establish truth.')
    hold_until(page, started, 75)
    page.locator('#summary .citation').first.click()
    caption(page, 'Inspect the original evidence', 'The evidence trail shows provider data and original source links. R-prefixed IDs identify sources carried from the saved radar, rather than recycling its generated narrative.')
    hold_until(page, started, 91)
    page.locator('.findings-grid').scroll_into_view_if_needed()
    ticker_news = report['quality']['news_count']
    radar_news = sum(item['kind'] == 'headline' and item['id'].startswith('R') for item in report['evidence'])
    caption(page, 'Challenge the story', 'Supporting findings sit beside counterpoints. This run has '+str(ticker_news)+' ticker-news excerpts and '+str(radar_news)+' original radar headlines; missing evidence remains explicit.')
    hold_until(page, started, 108)
    page.locator('#risks').scroll_into_view_if_needed()
    caption(page, 'Risk and uncertainty', 'Volatility and drawdown describe a historical window. Unknowns remain visible. These are research candidates, with no orders, promised returns or personalized investment instructions.')
    hold_until(page, started, 125)
    page.locator('#report details').evaluate('(n)=>n.open=true')
    page.locator('#report details').scroll_into_view_if_needed()
    caption(page, 'Muse-only inference, inspectable execution', report['inference']['model']+' | input/output tokens: '+str(report['inference']['input_tokens'])+' / '+str(report['inference']['output_tokens'])+'. The server keeps all credentials out of the browser.')
    hold_until(page, started, 139)
    page.locator('#export').scroll_into_view_if_needed()
    caption(page, 'Export findings with their evidence', 'The JSON preserves the question, cited findings, opposing evidence, historical risk, data gaps and Muse metadata for review.')
    with page.expect_download() as pending_download:
        page.get_by_role('button', name='Export JSON').click()
    pending_download.value.save_as(str(OUTPUT/'demo-report.json'))
    hold_until(page, started, 151)
    code = (ROOT/'marketmind/discovery_store.py').read_text(encoding='utf-8')
    excerpt = code[code.index('def update_if_due'):code.index('def start_scheduler')]
    page.set_content('<body style="margin:26px;background:#0b1117;color:#e6edf0;font:15px/1.45 Consolas,monospace"><h2>New event code: durable two-hour radar schedule</h2><pre id="code" style="white-space:pre-wrap"></pre></body>')
    page.locator('#code').evaluate('(node,text)=>node.textContent=text', excerpt)
    caption(page, 'The scheduled discovery code', 'The server checks whether the two-hour scan is due, saves successful results atomically and keeps the previous list on failure. Offline tests cover scheduling, citations and failure recovery.')
    hold_until(page, started, 166)
    page.goto('http://127.0.0.1:8000', wait_until='networkidle')
    page.locator('#market-radar').scroll_into_view_if_needed()
    caption(page, 'MarketMind | discover, question, inspect', 'Broad news discovery every two hours, then evidence-led research when you choose. Built for Your World, with prior work acknowledged. Educational research only; not investment advice.')
    hold_until(page, started, 175)
    if errors or len(research_requests) != 1:
        raise RuntimeError('Recording browser checks failed.')
    video = page.video
    context.close()
    Path(video.path()).replace(OUTPUT/'marketmind-demo.webm')
    browser.close()
    receipt = {'recorded_at':datetime.now(timezone.utc).isoformat(), 'research_created_at':report['created_at'],
               'model':report['inference']['model'], 'provider':report['inference']['provider'],
               'input_tokens':report['inference']['input_tokens'], 'output_tokens':report['inference']['output_tokens'],
               'ticker':ticker, 'ticker_news_count':ticker_news, 'radar_headline_count_in_report':radar_news,
               'radar_created_at':radar['created_at'], 'scanned_headline_count':radar['headline_count'],
               'verified_company_count':radar['candidate_count'], 'scan_interval_seconds':radar['scan_interval_seconds'],
               'research_requests':len(research_requests), 'browser_errors':errors,
               'recording':'artifacts/marketmind-demo.webm', 'public_video_url':None,
               'feature_coverage':['two-hour background scan','saved ten-stock list','broad news without a fixed watchlist','source inspection','explicit research handoff','real Muse synthesis','counterpoints and risk','JSON export','event code and prior-work disclosure'],
               'note':'Real local captioned recording; no audio narration. Public hosting remains pending.'}
    (OUTPUT/'recording-receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps(receipt), flush=True)
