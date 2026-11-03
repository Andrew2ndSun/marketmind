"""Record a captioned, real Muse walkthrough; requires optional playwright install.

Run: python scripts/record_demo.py
The app must already be running at localhost:8000 with Muse configured.
No model response is mocked. The local video is excluded from Git.
"""
import json
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


with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    context=browser.new_context(viewport={"width":1280,"height":900},record_video_dir=str(OUTPUT),record_video_size={"width":1280,"height":900})
    page=context.new_page()
    page.goto('http://127.0.0.1:8000',wait_until='domcontentloaded')
    started=time.monotonic()
    caption(page,'MarketMind | Build for Your World','Muse scans broad economic and business news every two hours. This saved list shows ten sourced research candidates; opening the page makes no model call.')
    hold_until(page,started,12)
    caption(page,'What I built during the hackathon','New: market radar, Muse research integration, cited reports, evidence dashboard and validation. The data-fetching foundation was adapted from an earlier prototype.')
    page.locator('.radar-card').first.wait_for(state='visible',timeout=90000)
    if time.monotonic()-started > 45:
        raise RuntimeError('Saved radar list not ready within the recording segment; let the first background scan finish before recording.')
    page.locator('.radar-card').first.scroll_into_view_if_needed()
    hold_until(page,started,25)
    page.locator('.radar-select').first.click()
    caption(page,'Live investigation | no canned output','This is a real request to Muse. Market evidence is collected first; missing news or fundamentals remain visible rather than being invented.')
    with page.expect_response(lambda response: response.url.endswith('/api/research') and response.request.method=='POST',timeout=120000) as pending:
        page.get_by_role('button',name='Investigate').click()
    response=pending.value
    report=response.json()
    if response.status!=200:
        raise RuntimeError('Live research failed; no success video will be produced.')
    if time.monotonic()-started>65:
        raise RuntimeError('Request exceeded the allotted recording segment; retry rather than fabricate success.')
    page.locator('#report').wait_for(state='visible')
    page.locator('#report').scroll_into_view_if_needed()
    caption(page,'A cited research brief','Muse separates observations from hypotheses. Every accepted claim cites an evidence ID supplied by the application.')
    hold_until(page,started,67)
    page.locator('#summary .citation').first.click()
    caption(page,'Follow a claim to its evidence','The source trail exposes the exact data, provider and retrieval time. Valid citation IDs do not automatically verify that a claim is true.')
    hold_until(page,started,85)
    page.locator('.findings-grid').scroll_into_view_if_needed()
    caption(page,'Challenge the story','Supporting observations and counterpoints are shown together. This run returned '+str(report['quality']['news_count'])+' usable news excerpts; missing news cannot establish a catalyst.')
    hold_until(page,started,104)
    page.locator('#risks').scroll_into_view_if_needed()
    caption(page,'Risk and uncertainty, not a forecast','Volatility and drawdown describe a historical window. Unknowns remain explicit. MarketMind does not place trades or give personalized investment instructions.')
    hold_until(page,started,123)
    page.locator('details').evaluate('(n)=>n.open=true')
    page.locator('details').scroll_into_view_if_needed()
    caption(page,'Inspectable Muse execution',report['inference']['model']+' | input tokens: '+str(report['inference']['input_tokens'])+' | output tokens: '+str(report['inference']['output_tokens'])+'. Credentials remain server-side.')
    hold_until(page,started,139)
    page.locator('#export').scroll_into_view_if_needed()
    caption(page,'Export the report and evidence together','The JSON export preserves the findings, their evidence IDs, risk measurements, quality gaps and model metadata for review.')
    with page.expect_download() as pending_download:
        page.get_by_role('button',name='Export JSON').click()
    pending_download.value.save_as(str(OUTPUT/'demo-report.json'))
    hold_until(page,started,150)
    code=(ROOT/'marketmind/muse.py').read_text(encoding='utf-8')
    page.set_content('<body style="margin:30px;background:#0b1117;color:#e6edf0;font:16px/1.5 Consolas,monospace"><h2>New hackathon code: marketmind/muse.py</h2><pre id="code" style="white-space:pre-wrap"></pre></body>')
    page.locator('#code').evaluate('(node,text)=>node.textContent=text',code)
    caption(page,'The new Muse integration is real code','Fixed Meta endpoint, no redirects or provider fallback, structured JSON validation, and explicit failures. Offline tests also cover invalid citations and truncated replies.')
    hold_until(page,started,165)
    page.goto('http://127.0.0.1:8000',wait_until='networkidle')
    caption(page,'MarketMind | explainable equity research','Built for Your World. New Muse-backed research experience on an acknowledged earlier data foundation. Educational research only; not investment advice.')
    hold_until(page,started,175)
    video=page.video
    context.close()
    original=Path(video.path())
    target=OUTPUT/'marketmind-demo.webm'
    original.replace(target)
    browser.close()
    receipt={'recorded_at':report['created_at'],'model':report['inference']['model'],'provider':report['inference']['provider'],
             'input_tokens':report['inference']['input_tokens'],'output_tokens':report['inference']['output_tokens'],
             'news_count':report['quality']['news_count'],'recording':'artifacts/marketmind-demo.webm',
             'public_video_url':None,'note':'Actual local recording with captions; no audio narration. Public upload and final playback review remain required.'}
    (OUTPUT/'recording-receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(receipt),flush=True)
