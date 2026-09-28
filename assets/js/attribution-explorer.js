/* Period explorer of the attribution series (Part 1).
   For any window of months: each theme's return (% of capital a year, before costs) and its
   share of the book's daily variance, for the book or one leg. The JSON holds per-month sums
   (sum of daily P&L, and of P&L x book return), so any window is exact:
     return = 252 x sum / n,   share = (sx - s x S / n) / (S2 - S^2 / n),
   with S, S2 the book's sums. Legs' shares are shares of the book's variance. */
(function () {
  'use strict';

  const root = document.getElementById('attribution-explorer');
  if (!root) return;

  const PRESETS = [
    ['Full history', '1999-01', null], ['1999–2003', '1999-01', '2003-12'], ['2004–08', '2004-01', '2008-12'],
    ['2009–13', '2009-01', '2013-12'], ['2014–18', '2014-01', '2018-12'], ['2019–21', '2019-01', '2021-12'],
    ['2022–May 2026', '2022-01', null], ['2008–09 drawdown', '2008-07', '2009-09'],
    ['2020–21 drawdown', '2020-02', '2021-01'],
  ];
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const state = { from: 0, to: 0, leg: 'total', preset: 0 };
  const chart = root.querySelector('.ae-chart');
  const summary = root.querySelector('.ae-summary');
  const fromSel = root.querySelector('.ae-from');
  const toSel = root.querySelector('.ae-to');
  const presetSel = root.querySelector('.ae-preset');
  let data = null;
  let tip = null;

  const monthLabel = (m) => `${MONTHS[Number(m.slice(5)) - 1]} ${m.slice(0, 4)}`;
  const fmt = (v, d = 1) => {
    const r = Number(Math.abs(v).toFixed(d));
    return (r === 0 ? '' : v > 0 ? '+' : '−') + r.toFixed(d);
  };
  const sum = (arr, a, b) => { let t = 0; for (let i = a; i <= b; i += 1) t += arr[i]; return t; };

  // Return (% a year) and share of the book's variance (%) of one line over months a..b.
  function stats(line, a, b) {
    const n = sum(data.book.n, a, b);
    const S = sum(data.book.s, a, b) / 1e4;
    const S2 = sum(data.book.sx, a, b) / 1e4;
    const s = sum(line.s, a, b) / 1e4;
    const sx = sum(line.sx, a, b) / 1e4;
    const variance = S2 - (S * S) / n;
    return { ret: (100 * 252 * s) / n, share: (100 * (sx - (s * S) / n)) / variance, n };
  }

  function bookSummary(a, b) {
    const n = sum(data.book.n, a, b);
    const S = sum(data.book.s, a, b) / 1e4;
    const S2 = sum(data.book.sx, a, b) / 1e4;
    const mean = S / n;
    const vol = Math.sqrt((S2 - (S * S) / n) / (n - 1)) * Math.sqrt(252);
    const costs = sum(data.lines.total['Trading costs'].s, a, b) / 1e4 / n;
    return { ret: 100 * 252 * mean, net: 100 * 252 * (mean + costs), vol: 100 * vol, sharpe: (252 * mean) / vol, n };
  }

  function rows() {
    const lines = data.lines[state.leg];
    const out = [];
    data.groups.forEach((group) => {
      out.push({ kind: 'group', label: group.label });
      if (group.total && lines[group.total]) out.push({ kind: 'total', label: group.total, line: lines[group.total] });
      group.lines.forEach((name) => { if (lines[name]) out.push({ kind: 'line', label: name, line: lines[name], indent: !!group.total }); });
    });
    return out;
  }

  function niceMax(v) {
    const m = Math.max(v, 1e-9);
    const p = 10 ** Math.floor(Math.log10(m));
    return [1, 2, 2.5, 5, 10].map((k) => k * p).find((x) => x >= m);
  }

  // Round limits and a tick step giving about one tick per 70 px of panel.
  function axis(values, panelWidth) {
    const lo = Math.min(0, ...values);
    const hi = Math.max(0, ...values);
    const step = niceMax((hi - lo) / Math.max(2, Math.floor(panelWidth / 70)));
    return { lo: Math.floor(lo / step) * step, hi: Math.ceil(hi / step) * step, step };
  }

  function el(name, attrs, text) {
    const node = document.createElementNS('http://www.w3.org/2000/svg', name);
    Object.entries(attrs).forEach(([k, v]) => node.setAttribute(k, v));
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function render() {
    const a = state.from;
    const b = state.to;
    const book = bookSummary(a, b);
    const legName = { total: 'Book', long: 'Long leg', short: 'Short leg' }[state.leg];
    summary.innerHTML = `<strong>${monthLabel(data.months[a])}–${monthLabel(data.months[b])}</strong>, ${book.n.toLocaleString('en')} sessions. `
      + `Book: ${fmt(book.ret)}% a year before costs, ${fmt(book.net)}% after, ${book.vol.toFixed(1)}% volatility, Sharpe ${book.sharpe.toFixed(2)}.`
      + (state.leg === 'total' ? '' : ` Showing the ${legName.toLowerCase()}; shares are of the book's risk.`);

    const list = rows().map((r) => (r.line ? { ...r, ...stats(r.line, a, b) } : r));
    const width = Math.round(root.getBoundingClientRect().width) || 640;
    const stacked = width < 560;
    const labelW = stacked ? Math.min(190, width * 0.5) : 200;
    const rowH = 24;
    const groupH = 22;
    const top = 26;
    const panelW = stacked ? width - labelW - 8 : (width - labelW - 24) / 2;
    const bodyH = list.reduce((h, r) => h + (r.kind === 'group' ? groupH : rowH), 0);
    const panels = [
      { key: 'ret', title: 'Return (% a year)' },
      { key: 'share', title: 'Share of risk (%)' },
    ];
    const blockH = top + bodyH + 24;
    const height = stacked ? 2 * blockH + 12 : blockH;
    const svg = el('svg', { viewBox: `0 0 ${width} ${height}`, width, height, style: `width:${width}px;height:${height}px` });

    panels.forEach((panel, p) => {
      const x0 = stacked ? labelW : labelW + p * (panelW + 24);
      const y0 = stacked ? p * (blockH + 12) : 0;
      const valueRoom = 44;
      const ax = axis(list.filter((r) => r.line).map((r) => r[panel.key]), panelW);
      const scale = (v) => x0 + valueRoom * (ax.lo < 0 ? 1 : 0) + ((v - ax.lo) / (ax.hi - ax.lo)) * (panelW - valueRoom * (ax.lo < 0 ? 2 : 1));
      svg.appendChild(el('text', { x: x0, y: y0 + 14, class: 'ae-panel' }, panel.title));
      for (let t = ax.lo; t <= ax.hi + 1e-9; t += ax.step) {
        svg.appendChild(el('line', { x1: scale(t), x2: scale(t), y1: y0 + top - 4, y2: y0 + top + bodyH, class: Math.abs(t) < 1e-9 ? 'ae-zero' : 'ae-gridline' }));
        svg.appendChild(el('text', { x: scale(t), y: y0 + top + bodyH + 16, class: 'ae-tick', 'text-anchor': 'middle' }, Number(t.toFixed(4)).toString().replace('-', '−')));
      }
      let y = y0 + top;
      list.forEach((r) => {
        if (r.kind === 'group') {
          if (p === 0 || stacked) svg.appendChild(el('text', { x: 0, y: y + 15, class: 'ae-group' }, r.label.toUpperCase()));
          y += groupH;
          return;
        }
        const g = el('g', { class: 'ae-row' });
        if (r.kind === 'total') g.appendChild(el('rect', { x: 0, y, width: x0 + panelW, height: rowH, class: 'ae-band' }));
        if (p === 0 || stacked) {
          g.appendChild(el('text', { x: r.indent ? 10 : 0, y: y + 16, class: `ae-label${r.kind === 'total' ? ' ae-total' : ''}` }, r.label));
        }
        const v = r[panel.key];
        const x1 = scale(Math.min(0, v));
        const w = Math.max(Math.abs(scale(v) - scale(0)), 0.5);
        g.appendChild(el('rect', { x: x1, y: y + 5, width: w, height: rowH - 10, rx: 2, class: v >= 0 ? 'ae-pos' : 'ae-neg' }));
        // A negative label sits left of its bar unless that would reach the row labels.
        const inside = v < 0 && scale(v) - 36 < x0;
        const right = v >= 0 || inside;
        const tx = right ? Math.max(scale(v), scale(0)) + 4 : scale(v) - 4;
        g.appendChild(el('text', { x: tx, y: y + 16, class: 'ae-value', 'text-anchor': right ? 'start' : 'end' }, fmt(v)));
        g.addEventListener('mousemove', (e) => showTip(e, r));
        g.addEventListener('mouseleave', hideTip);
        svg.appendChild(g);
        y += rowH;
      });
    });
    chart.replaceChildren(svg);
  }

  function showTip(event, r) {
    if (!tip) { tip = document.createElement('div'); tip.className = 'ae-tip'; document.body.appendChild(tip); }
    tip.innerHTML = `<strong>${r.label}</strong><br>Return ${fmt(r.ret, 2)}% a year<br>Share of risk ${fmt(r.share, 1)}%`;
    tip.style.left = `${event.clientX + 12}px`;
    tip.style.top = `${event.clientY + 12}px`;
    tip.hidden = false;
  }
  function hideTip() { if (tip) tip.hidden = true; }

  function setWindow(from, to, preset) {
    state.from = Math.max(0, Math.min(from, to));
    state.to = Math.min(data.months.length - 1, Math.max(from, to));
    state.preset = preset;
    presetSel.value = String(preset);
    fromSel.value = data.months[state.from].slice(0, 4);
    toSel.value = data.months[state.to].slice(0, 4);
    render();
  }

  function init(json) {
    data = json;
    const years = [...new Set(data.months.map((m) => m.slice(0, 4)))];
    years.forEach((y) => { fromSel.add(new Option(y, y)); toSel.add(new Option(y, y)); });
    const index = (m) => { const i = data.months.indexOf(m); return i < 0 ? data.months.length - 1 : i; };
    PRESETS.forEach(([label], i) => presetSel.add(new Option(label, String(i))));
    presetSel.add(new Option('Custom years', '-1'));
    presetSel.addEventListener('change', () => {
      const i = Number(presetSel.value);
      if (i < 0) return;
      const [, from, to] = PRESETS[i];
      setWindow(index(from), to ? index(to) : data.months.length - 1, i);
    });
    const byYear = () => {
      const a = data.months.findIndex((m) => m.startsWith(fromSel.value));
      const last = data.months.map((m) => m.startsWith(toSel.value)).lastIndexOf(true);
      setWindow(a, last, -1);
    };
    fromSel.addEventListener('change', byYear);
    toSel.addEventListener('change', byYear);
    root.querySelectorAll('.ae-legs button').forEach((btn) => btn.addEventListener('click', () => {
      state.leg = btn.dataset.leg;
      root.querySelectorAll('.ae-legs button').forEach((b) => b.setAttribute('aria-checked', String(b === btn)));
      render();
    }));
    // Redraw when the column width changes; the SVG is drawn at its displayed size.
    let pending = null;
    let lastWidth = 0;
    new ResizeObserver(() => {
      const w = Math.round(root.getBoundingClientRect().width);
      if (w === lastWidth) return;
      lastWidth = w;
      cancelAnimationFrame(pending);
      pending = requestAnimationFrame(render);
    }).observe(root);
    setWindow(0, data.months.length - 1, 0);
  }

  fetch(root.dataset.source)
    .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(init)
    .catch((err) => { console.error(err); summary.textContent = 'The interactive figure could not be loaded.'; });
}());
