/* Predictor-structure explorer (regression article), drawn with Plotly.
   A period filter scopes both charts: a correlation heatmap (80 predictors in dendrogram
   order with their theme, or the seven theme composites) and each theme's cumulative IC
   with the target. Loading and colours come from the shared chart helper. */
(function () {
  'use strict';

  const root = document.getElementById('predictor-structure-explorer');
  if (!root) return;

  const PERIODS = [[1998, 2021], [1998, 2003], [2004, 2008], [2009, 2013], [2014, 2018], [2019, 2021]];
  const DEFAULT_VISIBLE = [0, 1, 2, 3, 4, 5, 6];
  const state = { period: 0, level: 'predictor', visible: new Set(DEFAULT_VISIBLE) };
  const heatEl = root.querySelector('.pse-heat');
  const icEl = root.querySelector('.pse-ic');
  const [heatHeading, icHeading] = root.querySelectorAll('.pse-heading');
  let data = null;
  let ready=false,legendTimer,icRange=null,rendering=false,pending=false,loading;

  const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const roles=['momentum','reversal','low_volatility','size','liquidity','market','short_interest'];
  const themeColor = t => window.BlogCharts.COLORS[roles[t]];

  // Date-weighted mean of yearly upper-triangle vectors over the selected period.
  function periodMean(yearly) {
    const [from, to] = PERIODS[state.period];
    const out = new Float64Array(yearly[0].length);
    let total = 0;
    data.years.forEach((year, y) => {
      if (year < from || year > to) return;
      const w = data.dates_per_year[y];
      total += w;
      yearly[y].forEach((v, k) => { out[k] += v * w; });
    });
    return out.map((v) => v / (total * data.scale));
  }

  // Full symmetric matrix from an upper-triangle vector.
  function square(upper, n) {
    const m = Array.from({ length: n }, () => new Array(n).fill(1));
    let k = 0;
    for (let i = 0; i < n; i += 1) {
      for (let j = i + 1; j < n; j += 1) { m[i][j] = upper[k]; m[j][i] = upper[k]; k += 1; }
    }
    return m;
  }

  function baseLayout(height) {
    const ink = cssVar('--ink');
    return {
      height,
      margin: { l: 10, r: 10, t: 6, b: 40 },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: cssVar('--page-surface'),
      font: { family: cssVar('--font-sans'), size: 12, color: cssVar('--muted-ink') },
      hoverlabel: { bgcolor: cssVar('--page-surface'), bordercolor: cssVar('--rule'), font: { color: ink } },
    };
  }

  const colorscale = () => [[0, window.BlogCharts.COLORS.short], [0.5, document.documentElement.dataset.theme==='dark'?'#252c34':'#f6f6f4'], [1, window.BlogCharts.COLORS.long]];
  const colorbar = {
    orientation: 'h', thickness: 8, len: 0.45, x: 1, xanchor: 'right', y: -0.02, yanchor: 'top',
    tickvals: [-1, 0, 1], outlinewidth: 0,
  };

  function predictorHeatmap() {
    const n = data.predictors.length;
    const matrix = square(periodMean(data.predictor_pairs), n);
    const order = data.predictors.map((_, i) => i).sort((a, b) => data.predictors[a].leaf - data.predictors[b].leaf);
    const pos = order.map((_, k) => 5 + 10 * k); // scipy's leaf coordinates
    const label = (i) => `${data.predictors[i].sign < 0 ? '− ' : ''}${data.predictors[i].description}`;
    const themes = order.map((i) => data.predictors[i].theme);
    const k = data.themes.length;
    const strip = data.themes.flatMap((_, t) => [[t / k, themeColor(t)], [(t + 1) / k, themeColor(t)]]);

    const dx = [];
    const dy = [];
    data.dendrogram.positions.forEach((p, l) => {
      p.forEach((v, c) => { dx.push(data.dendrogram.heights[l][c]); dy.push(v); });
      dx.push(null); dy.push(null);
    });
    const wide = heatEl.clientWidth > 560;
    const traces = [
      {
        type: 'scatter', mode: 'lines', x: dx, y: dy, xaxis: 'x2', yaxis: 'y',
        hoverinfo: 'skip', line: { color: cssVar('--muted-ink'), width: 1 },
      },
      {
        type: 'heatmap', x: [0], y: pos, z: themes.map((t) => [t + 0.5]), xaxis: 'x3', yaxis: 'y',
        zmin: 0, zmax: k, colorscale: strip, showscale: false,
        customdata: themes.map((t) => [data.themes[t].name]), hovertemplate: '%{customdata}<extra></extra>',
      },
      {
        type: 'heatmap', x: pos, y: pos, zmin: -1, zmax: 1, colorscale: colorscale(), colorbar,
        z: order.map((i) => order.map((j) => matrix[i][j])),
        text: order.map((i) => order.map((j) => `${label(i)}<br>${label(j)}`)),
        hovertemplate: '<b>ρ = %{z:.2f}</b><br>%{text}<extra></extra>',
      },
    ];
    const layout = Object.assign(baseLayout(wide ? 560 : 380), {
      xaxis: { domain: [wide ? 0.2 : 0.17, 1], visible: false },
      xaxis2: { domain: [0, wide ? 0.16 : 0.13], autorange: 'reversed', visible: false },
      xaxis3: { domain: [wide ? 0.17 : 0.14, wide ? 0.195 : 0.165], visible: false },
      yaxis: { range: [10 * n, 0], visible: false },
    });
    return { traces, layout };
  }

  function themeHeatmap() {
    const n = data.themes.length;
    const matrix = square(periodMean(data.theme_pairs), n);
    const names = data.themes.map((t) => t.short);
    // Phone columns use abbreviations; the rows keep the full short names.
    const narrow = heatEl.clientWidth <= 560;
    const abbrev = { 'Med./long ret.': 'M/L ret.', 'Short-term ret.': 'ST ret.', Volatility: 'Vol.', Trading: 'Trad.', 'Mkt corr.': 'Corr.', 'Short int.': 'SI' };
    const trace = {
      type: 'heatmap', x: names, y: names, z: matrix, zmin: -1, zmax: 1, colorscale: colorscale(), colorbar,
      texttemplate: '%{z:.2f}', xgap: 2, ygap: 2,
      customdata: data.themes.map((a) => data.themes.map((b) => `${a.name} · ${b.name}`)),
      hovertemplate: '<b>ρ = %{z:.2f}</b><br>%{customdata}<extra></extra>',
    };
    const layout = Object.assign(baseLayout(narrow ? 360 : 440), {
      margin: { l: 76, r: 10, t: 6, b: 60 },
      yaxis: { autorange: 'reversed', ticks: '', showgrid: false, zeroline: false, color: cssVar('--ink') },
      xaxis: { ticks: '', showgrid: false, zeroline: false, tickangle: 0, color: cssVar('--ink'), tickvals: names, ticktext: narrow ? names.map((n) => abbrev[n] || n) : names },
    });
    return { traces: [trace], layout };
  }

  function icChart() {
    const [from, to] = PERIODS[state.period];
    const rows = data.theme_ic.dates
      .map((date, t) => ({ date, values: data.theme_ic.values[t] }))
      .filter((r) => { const y = Number(r.date.slice(0, 4)); return y >= from && y <= to && (!icRange || r.date >= icRange[0] && r.date <= icRange[1]); });
    const x = rows.map((r) => r.date);
    const traces = data.themes.map((theme, t) => {
      let sum = 0;
      const y = rows.map((r) => { sum += r.values[t] / data.scale; return sum; });
      return {
        type: 'scatter', mode: 'lines', name: theme.short, x, y, visible:state.visible.has(t)?true:'legendonly', line: { color: themeColor(t), width: 2 },
        hovertemplate: `${theme.short} %{y:.1f} · mean IC ${(sum / rows.length).toFixed(3)}<extra></extra>`,
      };
    });
    const values = traces.filter((_,i)=>state.visible.has(i)).flatMap(tr=>tr.y).concat(0);
    const pad = 0.05 * (Math.max(...values) - Math.min(...values));
    const range = [Math.min(...values) - pad, Math.max(...values) + pad];
    const height = 320;
    const margin = { l: 40, r: 12, t: 50, b: 30 };
    const grid = cssVar('--rule');
    const layout = Object.assign(baseLayout(height), {
      margin,
      showlegend: true, legend:{orientation:'h',x:0,y:1.15},
      hovermode: 'x unified',
      xaxis: { range: [x[0], x[x.length - 1]], showgrid: false, linecolor: grid, ticks: '', spikecolor: cssVar('--muted-ink'), spikethickness: 1, spikedash: 'solid' },
      yaxis: { range, fixedrange: true, gridcolor: grid, zerolinecolor: cssVar('--muted-ink') },
    });
    return { traces, layout };
  }

  async function render() {
    if(rendering){pending=true;return;}rendering=true;
    try {
    const [from, to] = PERIODS[state.period];
    const period = `${from}–${to}`;
    const years=root.querySelectorAll('.pse-years select');
    if(years.length){years[0].value=from;years[1].value=to;}
    root.querySelectorAll('.pse-themes input').forEach((box,i)=>{box.checked=state.visible.has(i);box.style.setProperty('--swatch',themeColor(i));});
    root.querySelectorAll('[data-period]').forEach((b) => b.setAttribute('aria-checked', String(Number(b.dataset.period) === state.period)));
    root.querySelectorAll('[data-level]').forEach((b) => b.setAttribute('aria-checked', String(b.dataset.level === state.level)));
    const config = { responsive: true, displayModeBar: false };
    const heat = state.level === 'theme' ? themeHeatmap() : predictorHeatmap();
    heatEl.style.height=heat.layout.height+'px';
    heatHeading.textContent = state.level === 'theme'
      ? `Correlation between theme composites, ${period}`
      : `Correlation between the 80 predictors, ${period}`;
    window.Plotly.react(heatEl, heat.traces, heat.layout, config);
    const ic = icChart();
    icHeading.textContent = `Cumulative sampled IC, ${icRange ? ic.traces[0].x[0]+' – '+ic.traces[0].x.at(-1) : period}`;
    icEl.style.height=ic.layout.height+'px';
    await window.Plotly.react(icEl, ic.traces, ic.layout, config);
    if(!ready) {
      ready=true;
      icEl.on('plotly_legendclick',e=>{clearTimeout(legendTimer);legendTimer=setTimeout(()=>{if(state.visible.has(e.curveNumber))state.visible.delete(e.curveNumber);else state.visible.add(e.curveNumber);render();},320);return false;});
      icEl.on('plotly_legenddoubleclick',e=>{clearTimeout(legendTimer);state.visible=state.visible.size===1&&state.visible.has(e.curveNumber)?new Set(DEFAULT_VISIBLE):new Set([e.curveNumber]);render();return false;});
      icEl.on('plotly_relayout',e=>{
        if(rendering)return;
        if(e['xaxis.autorange']){icRange=null;render();return;}
        const a=e['xaxis.range[0]']||e['xaxis.range']?.[0],b=e['xaxis.range[1]']||e['xaxis.range']?.[1];
        if(!a||!b)return;
        const [from,to]=PERIODS[state.period];
        const selected=data.theme_ic.dates.filter(d=>d>=String(a).slice(0,10)&&d<=String(b).slice(0,10)&&Number(d.slice(0,4))>=from&&Number(d.slice(0,4))<=to);
        if(selected.length>=2)icRange=[selected[0],selected.at(-1)];
        render();
      });
    }
    } finally {rendering=false;if(pending){pending=false;render();}}
  }

  function start() {
    document.querySelectorAll('.predictor-list').forEach(details=>{
      const list=details.querySelector('ul');
      for(const p of data.predictors.filter(p=>p.theme===Number(details.dataset.theme))) {
        const item=document.createElement('li');item.textContent=p.description;list.append(item);
      }
    });
    const choices=root.querySelector('.pse-themes');
    data.themes.forEach((theme,i)=>{
      const label=document.createElement('label'),box=document.createElement('input'),text=document.createElement('span');
      label.className='blog-chart-check';box.type='checkbox';box.checked=state.visible.has(i);box.style.setProperty('--swatch',themeColor(i));
      box.onchange=()=>{if(box.checked)state.visible.add(i);else state.visible.delete(i);render();};
      text.textContent=theme.short;label.append(box,text);choices.append(label);
    });
    const years=document.createElement('div'),dash=document.createElement('span'),from=document.createElement('select'),to=document.createElement('select');
    years.className='blog-chart-range';dash.className='blog-chart-range-sep';dash.textContent='–';
    for(const [label,select] of [['From year',from],['To year',to]]) {select.setAttribute('aria-label',label);data.years.forEach(y=>select.add(new Option(y,y)));}
    years.append(from,dash,to);root.querySelector('.pse-years').append(years);
    from.value=data.years[0];to.value=data.years.at(-1);
    from.onchange=to.onchange=()=>{if(Number(from.value)>Number(to.value))return;PERIODS[6]=[Number(from.value),Number(to.value)];state.period=6;icRange=null;render();};
    const periods = root.querySelector('.pse-periods');
    PERIODS.forEach(([a, b], i) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.setAttribute('role', 'radio');
      button.dataset.period = String(i);
      button.textContent = i ? `${a}–${String(b).slice(2)}` : 'All years';
      button.addEventListener('click', () => { state.period = i; icRange=null;render(); });
      periods.appendChild(button);
    });
    root.querySelectorAll('[data-level]').forEach((b) => b.addEventListener('click', () => { state.level = b.dataset.level; render(); }));
    root.querySelector('.pse-status').hidden = true;
    render();
    new MutationObserver(render).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    let width=root.clientWidth;
    new ResizeObserver(()=>{if(width!==root.clientWidth){width=root.clientWidth;render();}}).observe(root);
  }

  function load() {
    if(loading)return loading;
    loading=Promise.all([window.BlogCharts.plotly(), window.BlogCharts.load(root.dataset.source)])
      .then(([, json]) => { data = json; start(); })
      .catch(() => { root.querySelector('.pse-status').textContent = 'The interactive figure could not load.'; });
    return loading;
  }

  document.querySelectorAll('.predictor-list').forEach(details=>details.addEventListener('toggle',()=>{if(details.open)load();}));
  window.BlogCharts.whenVisible(root,load);
}());
