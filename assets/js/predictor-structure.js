/* Predictor-structure explorer (regression article), drawn with Plotly.
   A period filter scopes both charts: a correlation heatmap (80 predictors in dendrogram
   order with their theme, or the seven theme composites) and the cumulative IC with the
   target of the theme composites or of one theme's predictors. Years after the base period
   keep its signs and dendrogram. Loading and colours come from the shared chart helper. */
(function () {
  'use strict';

  const root = document.getElementById('predictor-structure-explorer');
  if (!root) return;

  const PERIODS = [[1998, 2021], [1998, 2003], [2004, 2008], [2009, 2013], [2014, 2018], [2019, 2021]];
  let custom = PERIODS.length; // slot of the period set with the year controls
  const DEFAULT_VISIBLE = [0, 1, 2, 3, 4, 5, 6];
  // icTheme: -1 draws the theme composites, otherwise the predictors of that theme.
  const state = { period: 0, level: 'predictor', visible: new Set(DEFAULT_VISIBLE), icTheme: -1 };
  const heatEl = root.querySelector('.pse-heat');
  const icEl = root.querySelector('.pse-ic');
  const [heatHeading, icHeading] = root.querySelectorAll('.pse-heading');
  let data = null;
  let ready=false,legendTimer,icRange=null,rendering=false,pending=false,loading;

  const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const roles=['momentum','reversal','low_volatility','size','liquidity','market','short_interest'];
  const themeColor = t => window.BlogCharts.COLORS[roles[t]];
  const label = (i) => `${data.predictors[i].sign < 0 ? '− ' : ''}${data.predictors[i].description}`;

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
    const abbrev = { 'Med./long ret.': 'M/L', 'Short-term ret.': 'ST', Volatility: 'Vol.', Trading: 'Trad.', 'Mkt corr.': 'Corr.', 'Short int.': 'SI' };
    const trace = {
      type: 'heatmap', x: names, y: names, z: matrix, zmin: -1, zmax: 1, colorscale: colorscale(), colorbar,
      texttemplate: '%{z:.2f}', xgap: 2, ygap: 2,
      customdata: data.themes.map((a) => data.themes.map((b) => `${a.name} · ${b.name}`)),
      hovertemplate: '<b>ρ = %{z:.2f}</b><br>%{customdata}<extra></extra>',
    };
    const layout = Object.assign(baseLayout(narrow ? 360 : 440), {
      margin: { l: 92, r: 10, t: 6, b: 60 },
      yaxis: { autorange: 'reversed', ticks: '', showgrid: false, zeroline: false, color: cssVar('--ink') },
      xaxis: { ticks: '', showgrid: false, zeroline: false, tickangle: 0, color: cssVar('--ink'), tickvals: names, ticktext: narrow ? names.map((n) => abbrev[n] || n) : names },
    });
    return { traces: [trace], layout };
  }

  function icChart() {
    const [from, to] = PERIODS[state.period];
    const dates = data.theme_ic.dates;
    const rows = [];
    dates.forEach((date, i) => {
      const y = Number(date.slice(0, 4));
      if (y >= from && y <= to && (!icRange || date >= icRange[0] && date <= icRange[1])) rows.push(i);
    });
    const x = rows.map((i) => dates[i]);
    const line = (name, value, style) => {
      let sum = 0;
      const y = rows.map((i) => { sum += value(i) / data.scale; return sum; });
      return Object.assign({
        type: 'scatter', mode: 'lines', x, y,
        hovertemplate: `${name}${style.detail ? '<br>cumulative IC ' : ' '}%{y:.1f} · mean IC ${(sum / rows.length).toFixed(3)}<extra></extra>`,
      }, style.trace);
    };
    const theme = state.icTheme;
    let traces;
    if (theme < 0) {
      traces = data.themes.map((t, k) => line(t.short, (i) => data.theme_ic.values[i][k], {
        trace: { name: t.short, visible: state.visible.has(k) ? true : 'legendonly', line: { color: themeColor(k), width: 2 } },
      }));
    } else {
      // Thin lines are the theme's predictors; the heavy line is its composite.
      const color = themeColor(theme);
      traces = data.predictors.flatMap((p, k) => (p.theme !== theme ? [] : [line(label(k), (i) => data.predictor_ic[k][i], {
        detail: true, trace: { opacity: 0.55, line: { color, width: 1.1 } },
      })]));
      traces.push(line(`${data.themes[theme].name} composite`, (i) => data.theme_ic.values[i][theme], {
        detail: true, trace: { line: { color: cssVar('--ink'), width: 2.4 } },
      }));
    }
    const values = traces.filter((tr) => tr.visible !== 'legendonly').flatMap((tr) => tr.y).concat(0);
    const pad = 0.05 * (Math.max(...values) - Math.min(...values));
    const range = [Math.min(...values) - pad, Math.max(...values) + pad];
    const grid = cssVar('--rule');
    // The legend sits above the plot; on a phone it wraps to four rows and needs the room.
    const top = theme >= 0 ? 10 : icEl.clientWidth <= 560 ? 96 : 50;
    const layout = Object.assign(baseLayout(theme < 0 ? 270 + top : 340), {
      margin: { l: 40, r: 12, t: top, b: 30 },
      showlegend: theme < 0, legend:{orientation:'h',x:0,y:1.02,yanchor:'bottom'},
      hovermode: theme < 0 ? 'x unified' : 'closest',
      xaxis: { range: [x[0], x[x.length - 1]], showgrid: false, linecolor: grid, ticks: '', spikecolor: cssVar('--muted-ink'), spikethickness: 1, spikedash: 'solid', showspikes: theme < 0 },
      yaxis: { range, fixedrange: true, gridcolor: grid, zerolinecolor: cssVar('--muted-ink') },
    });
    return { traces, layout };
  }

  // In the predictor view the line under the pointer stands out from its theme.
  function emphasize(curve) {
    if (state.icTheme < 0) return;
    const last = icEl.data.length - 1;
    window.Plotly.restyle(icEl, {
      opacity: icEl.data.map((_, i) => (i === last ? 1 : curve === null ? 0.55 : i === curve ? 1 : 0.25)),
      'line.width': icEl.data.map((_, i) => (i === last ? 2.4 : i === curve ? 2 : 1.1)),
    });
  }

  async function render() {
    if(rendering){pending=true;return;}rendering=true;
    try {
    const [from, to] = PERIODS[state.period];
    const period = `${from}–${to}`;
    const years=root.querySelectorAll('.pse-years select');
    if(years.length){years[0].value=from;years[1].value=to;}
    const pick=root.querySelector('.pse-lines select');
    if(pick)pick.value=String(state.icTheme);
    root.querySelector('.pse-themes').closest('.blog-chart-row').hidden=state.icTheme>=0;
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
    const span = icRange ? ic.traces[0].x[0]+' – '+ic.traces[0].x.at(-1) : period;
    icHeading.textContent = state.icTheme < 0
      ? `Cumulative sampled IC of the theme composites, ${span}`
      : `Cumulative sampled IC of the ${ic.traces.length - 1} ${data.themes[state.icTheme].name.toLowerCase()} predictors, ${span}`;
    icEl.style.height=ic.layout.height+'px';
    await window.Plotly.react(icEl, ic.traces, ic.layout, config);
    if(!ready) {
      ready=true;
      icEl.on('plotly_legendclick',e=>{clearTimeout(legendTimer);legendTimer=setTimeout(()=>{if(state.visible.has(e.curveNumber))state.visible.delete(e.curveNumber);else state.visible.add(e.curveNumber);render();},320);return false;});
      icEl.on('plotly_legenddoubleclick',e=>{clearTimeout(legendTimer);state.visible=state.visible.size===1&&state.visible.has(e.curveNumber)?new Set(DEFAULT_VISIBLE):new Set([e.curveNumber]);render();return false;});
      icEl.on('plotly_hover',e=>{const n=e.points[0].curveNumber;emphasize(n===icEl.data.length-1?null:n);});
      icEl.on('plotly_unhover',()=>emphasize(null));
      icEl.on('plotly_relayout',e=>{
        if(rendering)return;
        if(e['xaxis.autorange']){icRange=null;render();return;}
        const a=e['xaxis.range[0]']||e['xaxis.range']?.[0],b=e['xaxis.range[1]']||e['xaxis.range']?.[1];
        if(!a||!b)return;
        const [from,to]=PERIODS[state.period];
        const inPeriod=data.theme_ic.dates.filter(d=>Number(d.slice(0,4))>=from&&Number(d.slice(0,4))<=to);
        const selected=inPeriod.filter(d=>d>=String(a).slice(0,10)&&d<=String(b).slice(0,10));
        // Zooming back out to the whole period is no zoom: the heading names the period again.
        if(selected.length>=2)icRange=selected.length===inPeriod.length?null:[selected[0],selected.at(-1)];
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
    from.onchange=to.onchange=()=>{if(Number(from.value)>Number(to.value))return;PERIODS[custom]=[Number(from.value),Number(to.value)];state.period=custom;icRange=null;render();};
    // Years after the base period get their own preset; the default view stays on the base period.
    const base=data.base_period,last=data.years.at(-1),later=last>base[1];
    PERIODS[0]=[...base];
    if(later){PERIODS.push([base[1]+1,last]);custom=PERIODS.length;}
    from.value=base[0];to.value=base[1];
    if(data.predictor_ic) {
      const pick=document.createElement('select');pick.setAttribute('aria-label','Lines in the IC panel');
      pick.add(new Option('Theme composites','-1'));
      data.themes.forEach((theme,i)=>pick.add(new Option(`${theme.name} predictors`,String(i))));
      pick.onchange=()=>{state.icTheme=Number(pick.value);render();};
      const lines=root.querySelector('.pse-lines');lines.append(pick);lines.closest('.blog-chart-row').hidden=false;
    }
    const periods = root.querySelector('.pse-periods');
    PERIODS.forEach(([a, b], i) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.setAttribute('role', 'radio');
      button.dataset.period = String(i);
      button.textContent = i || later ? `${a}–${String(b).slice(2)}` : 'All years';
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
