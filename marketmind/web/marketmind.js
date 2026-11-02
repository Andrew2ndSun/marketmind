/* All provider content is inserted as text, never rendered as HTML. */
const $ = id => document.getElementById(id);
let currentReport = null;
const el = (tag, text, className) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
};
function claimNode(claim) {
  const node = el('div', undefined, 'claim');
  node.append(el('p', claim.text));
  for (const id of claim.evidence_ids) {
    const link = el('a', id, 'citation');
    link.href = '#source-' + id;
    link.setAttribute('aria-label', 'Inspect evidence ' + id);
    node.append(link);
  }
  return node;
}
function drawChart(history) {
  const svg = $('chart'); svg.replaceChildren();
  const values = history.map(p => p.close);
  const low = Math.min(...values), high = Math.max(...values), range = high - low || 1;
  const ns = 'http://www.w3.org/2000/svg';
  for (let i = 0; i < 4; i++) {
    const y = 15 + i * 50;
    const line = document.createElementNS(ns, 'line');
    for (const [key, value] of Object.entries({x1:0,x2:655,y1:y,y2:y,stroke:'#25333e'})) line.setAttribute(key,value);
    svg.append(line);
    const label = document.createElementNS(ns, 'text');
    label.setAttribute('x', 665); label.setAttribute('y', y + 4); label.setAttribute('fill', '#95a6b3'); label.setAttribute('font-size', '10');
    label.textContent = (high - i * range / 3).toFixed(2); svg.append(label);
  }
  const points = values.map((v,i) => `${i/(values.length-1)*650},${15+(high-v)/range*150}`).join(' ');
  const path = document.createElementNS(ns, 'polyline');
  for (const [key,value] of Object.entries({points,fill:'none',stroke:'#acedd5','stroke-width':2})) path.setAttribute(key,value);
  svg.append(path);
  $('chart-start').textContent = history[0].date;
  $('chart-end').textContent = history.at(-1).date;
}
function render(data) {
  currentReport = data;
  $('empty').hidden = true; $('report').hidden = false;
  $('company').textContent = data.company;
  $('mode-badge').textContent = 'LIVE RESEARCH / MUSE MODEL';
  $('report-meta').textContent = `${data.ticker} · ${data.metrics.bars} completed sessions · ${data.elapsed_seconds}s · ${new Date(data.created_at).toLocaleString()}`;
  $('warnings').replaceChildren(...data.quality.warnings.map(w => el('p', w, 'notice')));
  const m = data.metrics;
  const metrics = [ ['Last adjusted close', `${m.last_adjusted_close.toFixed(2)} ${data.currency || '(currency unknown)'}`],
    ['20-session return', `${m.twenty_session_return_pct}%`], ['Historical volatility · ann.', `${m.annualized_volatility_pct}%`], ['Window max drawdown', `${m.max_drawdown_pct}%`] ];
  $('metrics').replaceChildren(...metrics.map(([name,value]) => { const node=el('div',undefined,'metric');node.append(el('span',name),el('strong',value));return node; }));
  drawChart(data.price_history);
  $('summary').replaceChildren(claimNode(data.research.summary));
  for (const key of ['findings','conflicting_evidence','risks']) {
    $(key).replaceChildren(...data.research[key].map(claimNode));
    if (!data.research[key].length) $(key).append(el('p','No opposing evidence identified in the supplied material. This does not establish that none exists.','helper'));
  }
  $('unknowns').replaceChildren(...data.research.unknowns.map(text => el('li',text)));
  $('coverage').textContent = `${data.quality.citation_id_coverage_pct}% VALID CITATION IDS`;
  $('evidence').replaceChildren(...data.evidence.map(source => {
    const node = el('div',undefined,'source'); node.id='source-'+source.id;
    node.append(el('b',source.id),el('span',source.kind.toUpperCase()));
    const title = el('p');
    if (source.url && /^https?:\/\//i.test(source.url)) {
      const link=el('a',source.title);link.href=source.url;link.target='_blank';link.rel='noopener noreferrer';title.append(link);
    } else title.textContent=source.title;
    node.append(title,el('p',`${source.publisher} · Published: ${source.published_at || 'date unavailable'} · Retrieved: ${source.retrieved_at}`));
    if(source.excerpt) node.append(el('p',source.excerpt));
    if(source.data) node.append(el('pre',JSON.stringify(source.data,null,2)));
    return node;
  }));
  $('inference').textContent = `Model: ${data.inference.model}. Input/output tokens: ${data.inference.input_tokens ?? 'unknown'} / ${data.inference.output_tokens ?? 'unknown'}. Citation validity does not verify factual support.`;
  $('limitations').replaceChildren(...data.quality.limitations.map(text=>el('li',text)));
}
$('research-form').addEventListener('submit', async event => {
  event.preventDefault();
  $('run').disabled=true; $('status').className='';
  $('report').hidden=true; $('empty').hidden=true; currentReport=null;
  $('status').textContent='Collecting evidence and asking Muse to examine it. This may take a minute…';
  try {
    const response=await fetch('/api/research',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ticker:$('ticker').value,question:$('question').value,discovery_created_at:$('research-form').dataset.radarTicker === $('ticker').value.trim().toUpperCase() ? $('research-form').dataset.radarCreatedAt : undefined})});
    const data=await response.json();
    if(!response.ok) throw new Error(typeof data.detail==='string' ? data.detail : 'Check the symbol and question, then retry.');
    render(data);
    $('status').textContent='Research ready. Inspect the cited evidence and unresolved questions.';
  } catch(error) {
    $('status').textContent=error.message; $('status').className='error'; $('empty').hidden=false;
  } finally { $('run').disabled=false; }
});
$('export').addEventListener('click',()=>{
  if(!currentReport)return;
  const url=URL.createObjectURL(new Blob([JSON.stringify(currentReport,null,2)],{type:'application/json'}));
  const link=el('a');link.href=url;link.download=`marketmind-${currentReport.ticker}-${currentReport.mode}.json`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
fetch('/api/research/status').then(r=>r.json()).then(data=>{
  $('configuration').textContent=data.live_configured ? `Live model configured: ${data.model}. Availability is checked when you run research.` : 'Set MUSE_API_KEY or MODEL_API_KEY in the server environment to use Muse.';
}).catch(()=>{$('configuration').textContent='Cannot reach the API. Start the FastAPI server to run research.';});
