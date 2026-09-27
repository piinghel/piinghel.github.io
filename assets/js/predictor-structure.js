/* Predictor-structure explorer (regression article), drawn with Plotly.
   A period filter scopes both charts: a correlation heatmap (80 predictors in dendrogram
   order with their theme, or the seven theme composites) and each theme's cumulative IC
   with the target. Plotly loads only when the figure scrolls into view. */
(function () {
  'use strict';

  const root = document.getElementById('predictor-structure-explorer');
  if (!root) return;

  const PERIODS = [[1998, 2021], [1998, 2003], [2004, 2008], [2009, 2013], [2014, 2018], [2019, 2021]];
  const state = { period: 0, level: 'predictor' };
  const heatEl = root.querySelector('.pse-heat');
  const icEl = root.querySelector('.pse-ic');
  const [heatHeading, icHeading] = root.querySelectorAll('.pse-heading');
  let data = null;

  const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const themeColor = (t) => cssVar(`--theme-${t + 1}`);

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
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: { family: cssVar('--font-sans'), size: 12, color: cssVar('--muted-ink') },
      hoverlabel: { bgcolor: cssVar('--page-surface'), bordercolor: cssVar('--rule'), font: { color: ink } },
    };
  }

  const colorscale = () => [[0, cssVar('--heat-neg')], [0.5, cssVar('--heat-mid')], [1, cssVar('--heat-pos')]];
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
    const abbrev = { Momentum: 'Mom.', Reversal: 'Rev.', Volatility: 'Vol.', Liquidity: 'Liq.', 'Mkt corr.': 'Corr.' };
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

  // Theme names at the line ends, spread to at least one label height apart with a short
  // connector back to each line.
  function endLabels(ends, range, plotPx) {
    const gap = (15 * (range[1] - range[0])) / plotPx;
    const sorted = ends.slice().sort((a, b) => b.y - a.y);
    sorted.forEach((e, k) => { e.at = k ? Math.min(e.y, sorted[k - 1].at - gap) : e.y; });
    const shortfall = range[0] + gap / 2 - sorted[sorted.length - 1].at;
    if (shortfall > 0) sorted.forEach((e) => { e.at += shortfall; });
    return sorted.map((e) => ({
      x: e.x, y: e.y, ax: 14, ay: ((e.y - e.at) * plotPx) / (range[1] - range[0]), xanchor: 'left',
      text: e.text, font: { size: 12, color: e.color },
      showarrow: true, arrowhead: 0, arrowwidth: 1, arrowcolor: e.color, standoff: 2,
    }));
  }

  function icChart() {
    const [from, to] = PERIODS[state.period];
    const rows = data.theme_ic.dates
      .map((date, t) => ({ date, values: data.theme_ic.values[t] }))
      .filter((r) => { const y = Number(r.date.slice(0, 4)); return y >= from && y <= to; });
    const x = rows.map((r) => r.date);
    const ends = [];
    const traces = data.themes.map((theme, t) => {
      let sum = 0;
      const y = rows.map((r) => { sum += r.values[t] / data.scale; return sum; });
      ends.push({ x: x[x.length - 1], y: sum, text: theme.short, color: themeColor(t) });
      return {
        type: 'scatter', mode: 'lines', name: theme.short, x, y, line: { color: themeColor(t), width: 2 },
        hovertemplate: `${theme.short} %{y:.1f} · mean IC ${(sum / rows.length).toFixed(3)}<extra></extra>`,
      };
    });
    const values = traces.flatMap((tr) => tr.y).concat(0);
    const pad = 0.05 * (Math.max(...values) - Math.min(...values));
    const range = [Math.min(...values) - pad, Math.max(...values) + pad];
    const height = 320;
    const margin = { l: 36, r: 82, t: 6, b: 28 };
    const grid = cssVar('--rule');
    const layout = Object.assign(baseLayout(height), {
      margin,
      showlegend: false,
      hovermode: 'x unified',
      xaxis: { range: [x[0], x[x.length - 1]], showgrid: false, linecolor: grid, ticks: '' },
      yaxis: { range, gridcolor: grid, zerolinecolor: cssVar('--muted-ink') },
      annotations: endLabels(ends, range, height - margin.t - margin.b),
    });
    return { traces, layout };
  }

  function render() {
    const [from, to] = PERIODS[state.period];
    const period = `${from}–${to}`;
    root.querySelectorAll('[data-period]').forEach((b) => b.setAttribute('aria-checked', String(Number(b.dataset.period) === state.period)));
    root.querySelectorAll('[data-level]').forEach((b) => b.setAttribute('aria-checked', String(b.dataset.level === state.level)));
    const config = { responsive: true, displayModeBar: false };
    const heat = state.level === 'theme' ? themeHeatmap() : predictorHeatmap();
    heatHeading.textContent = state.level === 'theme'
      ? `Correlation between theme composites, ${period}`
      : `Correlation between the 80 predictors, ${period}`;
    window.Plotly.react(heatEl, heat.traces, heat.layout, config);
    icHeading.textContent = `Cumulative daily IC by theme, ${period}`;
    const ic = icChart();
    window.Plotly.react(icEl, ic.traces, ic.layout, config);
  }

  function start() {
    const periods = root.querySelector('.pse-periods');
    PERIODS.forEach(([a, b], i) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.setAttribute('role', 'radio');
      button.dataset.period = String(i);
      button.textContent = i ? `${a}–${String(b).slice(2)}` : 'All years';
      button.addEventListener('click', () => { state.period = i; render(); });
      periods.appendChild(button);
    });
    root.querySelectorAll('[data-level]').forEach((b) => b.addEventListener('click', () => { state.level = b.dataset.level; render(); }));
    root.querySelector('.pse-status').hidden = true;
    render();
    new MutationObserver(render).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  }

  // Shared with the article's other Plotly figures, so the library loads once.
  function loadPlotly(src) {
    if (!window.__plotlyPromise) {
      window.__plotlyPromise = window.Plotly ? Promise.resolve() : new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
      });
    }
    return window.__plotlyPromise;
  }

  function load() {
    Promise.all([loadPlotly(root.dataset.plotly), fetch(root.dataset.source).then((r) => r.json())])
      .then(([, json]) => { data = json; start(); })
      .catch(() => { root.querySelector('.pse-status').textContent = 'The interactive figure could not load.'; });
  }

  const observer = new IntersectionObserver((entries) => {
    if (entries.some((e) => e.isIntersecting)) { observer.disconnect(); load(); }
  }, { rootMargin: '600px' });
  observer.observe(root);
}());
