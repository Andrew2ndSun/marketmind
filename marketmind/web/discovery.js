/* Market discovery is independent of full research: selecting a card only fills the form. */
(() => {
  const byId = id => document.getElementById(id);
  const node = (tag, text, className) => {
    const result = document.createElement(tag);
    if (text !== undefined) result.textContent = text;
    if (className) result.className = className;
    return result;
  };
  function citations(ids) {
    const box = node('div', undefined, 'radar-citations');
    for (const id of ids) {
      const link = node('a', id, 'citation');
      link.href = '#radar-source-' + id;
      link.setAttribute('aria-label', 'Inspect market evidence ' + id);
      link.addEventListener('click', () => { byId('radar-details').open = true; });
      box.append(link);
    }
    return box;
  }
  function selectStock(stock, createdAt) {
    byId('ticker').value = stock.ticker;
    byId('research-form').dataset.radarTicker = stock.ticker;
    byId('research-form').dataset.radarCreatedAt = createdAt;
    byId('question').value = `What evidence supports the market radar's ${stock.theme} theme for ${stock.ticker}, and what challenges that story?`;
    byId('status').className = '';
    byId('status').textContent = `${stock.ticker} selected from market radar. Review the question, then select Investigate.`;
    byId('report').hidden = true;
    byId('empty').hidden = false;
    currentReport = null;
    byId('stock-research').scrollIntoView({behavior:'smooth', block:'start'});
    byId('ticker').focus({preventScroll:true});
  }
  function renderRadar(data) {
    byId('radar-content').hidden = false;
    byId('radar-overview').replaceChildren(node('p', data.overview.text), citations(data.overview.evidence_ids));
    byId('radar-warnings').replaceChildren(...data.warnings.map(text => node('p', text, 'notice')));
    byId('radar-themes').replaceChildren(...data.themes.map(theme => {
      const item = node('section', undefined, 'radar-theme');
      item.append(node('h3', theme.title), node('p', theme.impact), node('p', 'Industries: ' + theme.industries.join(', '), 'helper'), citations(theme.evidence_ids));
      return item;
    }));
    byId('radar-stocks').replaceChildren(...data.stocks.map((stock, index) => {
      const item = node('article', undefined, 'radar-card');
      const quote = stock.snapshot;
      item.append(node('span', String(index + 1).padStart(2, '0'), 'radar-rank'), node('h3', stock.ticker), node('p', quote.company, 'radar-company'));
      const change = node('p', `${quote.price.toFixed(2)} ${quote.currency || ''} \u00b7 ${quote.change_pct > 0 ? '+' : ''}${quote.change_pct.toFixed(2)}%`, quote.change_pct < 0 ? 'radar-price negative' : 'radar-price positive');
      item.append(change, node('p', quote.sector || 'Sector unavailable', 'helper'), node('span', stock.theme, 'radar-theme-tag'), node('p', stock.reason, 'radar-reason'));
      const risk = node('p', undefined, 'radar-risk'); risk.append(node('strong', 'Watch for: '), node('span', stock.risk));
      item.append(risk, citations(stock.evidence_ids));
      const button = node('button', `Research ${stock.ticker} \u2192`, 'secondary radar-select');
      button.type = 'button'; button.addEventListener('click', () => selectStock(stock, data.created_at));
      item.append(button); return item;
    }));
    byId('radar-sources').replaceChildren(...data.evidence.map(source => {
      const item = node('div', undefined, 'source'); item.id = 'radar-source-' + source.id;
      item.append(node('b', source.id));
      if (source.url && /^https?:\/\//i.test(source.url)) {
        const link = node('a', source.title); link.href = source.url; link.target = '_blank'; link.rel = 'noopener noreferrer'; item.append(link);
      } else item.append(node('span', source.title));
      item.append(node('p', `${source.publisher} \u00b7 ${source.published_at || source.data?.quote_at || 'Date unavailable'}`));
      if (source.excerpt) item.append(node('p', source.excerpt));
      if (source.data) item.append(node('pre', JSON.stringify(source.data, null, 2)));
      return item;
    }));
    byId('radar-limitations').replaceChildren(...data.limitations.map(text => node('li', text)));
    byId('radar-method').textContent = `${data.scope}. Muse reviewed ${data.candidate_count} candidates and ${data.headline_count} headlines. Model: ${data.inference.model}. Input/output tokens: ${data.inference.input_tokens ?? 'unknown'} / ${data.inference.output_tokens ?? 'unknown'}. Quote times are included in each snapshot. Order is editorial, not a predicted return ranking.`;
    byId('radar-status').textContent = `Scanned ${new Date(data.created_at).toLocaleString()} \u00b7 ${data.cached ? 'cached snapshot' : 'fresh scan'} \u00b7 ${data.candidate_count} candidates ? ${data.headline_count} headlines`;
  }
  async function scan(refresh = false) {
    byId('scan-refresh').disabled = true;
    byId('radar-status').className = 'helper';
    byId('radar-status').textContent = 'Scanning market activity and economic headlines with Muse. This may take a minute...';
    try {
      const response = await fetch('/api/discovery' + (refresh ? '?refresh=true' : ''));
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'The market scan is temporarily unavailable.');
      renderRadar(data);
    } catch (error) {
      byId('radar-status').className = 'helper error';
      byId('radar-status').textContent = `${error.message} You can still research any ticker below.`;
    } finally { byId('scan-refresh').disabled = false; }
  }
  byId('scan-refresh').addEventListener('click', () => scan(true));
  scan();
})();
