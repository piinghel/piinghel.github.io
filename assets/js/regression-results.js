/* Regression article, Figures 3 and 4 (Plotly): growth and drawdown of the three scores,
   and the ten largest Ridge coefficients by refit. Data: regression-results.json. */
(function () {
  'use strict';

  const growthEl = document.getElementById('mlr-growth');
  const coefEl = document.getElementById('mlr-coefficients');
  if (!growthEl && !coefEl) return;
  const source = (growthEl || coefEl).dataset.source;
  const MODELS = { 'Fixed score': '--model-fixed', OLS: '--model-ols', Ridge: '--model-ridge' };
  let data = null;

  const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const base = (height) => ({
    height,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: cssVar('--font-sans'), size: 12, color: cssVar('--muted-ink') },
    hoverlabel: { bgcolor: cssVar('--page-surface'), bordercolor: cssVar('--rule'), font: { color: cssVar('--ink') } },
  });
  const config = { responsive: true, displayModeBar: false };

  // Short horizontal heading above a panel, aligned with the tick labels.
  const heading = (text, y, left) => ({
    text, x: 0, xref: 'paper', xanchor: 'left', xshift: -left, y, yref: 'paper', yanchor: 'bottom',
    showarrow: false, font: { size: 13, color: cssVar('--ink') },
  });

  // Line-end labels, pushed apart by one label height when two series finish close together.
  function endLabels(names, last, range, panelPx) {
    const gap = (15 * (range[1] - range[0])) / panelPx; // 15 px in log10 units
    const ends = names
      .map((name) => ({ name, y: Math.log10(data.growth[name].growth[data.growth[name].growth.length - 1]) }))
      .sort((a, b) => b.y - a.y);
    ends.forEach((end, k) => { if (k) end.y = Math.min(end.y, ends[k - 1].y - gap); });
    return ends.map((end) => ({
      x: last, y: end.y, yref: 'y', xanchor: 'left', xshift: 5,
      text: end.name, showarrow: false, font: { color: cssVar(MODELS[end.name]), size: 12 },
    }));
  }

  function growthChart() {
    const names = Object.keys(data.growth);
    const traces = names.flatMap((name) => {
      const color = cssVar(MODELS[name]);
      const s = data.growth[name];
      return [
        { type: 'scatter', mode: 'lines', name, x: data.dates, y: s.growth, line: { color, width: 1.8 },
          hovertemplate: `${name} %{y:.2f}<extra></extra>` },
        { type: 'scatter', mode: 'lines', name, x: data.dates, y: s.drawdown, yaxis: 'y2', showlegend: false,
          line: { color, width: 1.2 }, hovertemplate: `${name} %{y:.1f}%<extra></extra>` },
      ];
    });
    const values = names.flatMap((name) => data.growth[name].growth);
    const range = [Math.log10(Math.min(...values) * 0.92), Math.log10(Math.max(...values) * 1.08)];
    const narrow = growthEl.clientWidth < 560;
    const height = narrow ? 420 : 460;
    const margin = { l: 40, r: narrow ? 72 : 80, t: 24, b: 28 };
    const growthDomain = [0.42, 1];
    const drawdownDomain = [0, 0.27];
    const panelPx = (height - margin.t - margin.b) * (growthDomain[1] - growthDomain[0]);
    const grid = cssVar('--rule');
    const last = data.dates[data.dates.length - 1];
    const layout = Object.assign(base(height), {
      margin,
      showlegend: false,
      hovermode: 'x unified',
      xaxis: { anchor: 'y2', range: [data.dates[0], last], showgrid: false, linecolor: grid, ticks: '' },
      yaxis: { type: 'log', range, domain: growthDomain, gridcolor: grid, tickformat: '~g' },
      yaxis2: { domain: drawdownDomain, gridcolor: grid, zerolinecolor: grid, nticks: 4 },
      annotations: [
        heading('Growth of $1 (log scale)', 1.0, margin.l - 4),
        heading('Drawdown (%)', drawdownDomain[1] + 0.03, margin.l - 4),
        ...endLabels(names, last, range, panelPx),
      ],
    });
    window.Plotly.react(growthEl, traces, layout, config);
  }

  function coefficientChart() {
    const c = data.coefficients;
    const narrow = coefEl.clientWidth < 560;
    const years = c.refit_years.map(String);
    const limit = Math.max(...c.values.flat().map(Math.abs));
    const tick = Math.floor(limit * 100) / 100;
    const trace = {
      type: 'heatmap', x: years, y: c.predictors.map((p) => p.label), z: c.values, zmin: -limit, zmax: limit,
      colorscale: [[0, cssVar('--heat-neg')], [0.5, cssVar('--heat-mid')], [1, cssVar('--heat-pos')]],
      xgap: 2, ygap: 2,
      customdata: c.predictors.map((p) => c.refit_years.map(() => `${p.description} · ${p.theme}`)),
      hovertemplate: '<b>%{z:.3f}</b><br>%{customdata}<br>Refit %{x}<extra></extra>',
      colorbar: {
        orientation: 'h', thickness: 8, len: narrow ? 0.7 : 0.4, x: 1, xanchor: 'right', y: -0.1, yanchor: 'top',
        outlinewidth: 0, tickvals: narrow ? [-tick, 0, tick] : undefined, nticks: 5, tickangle: 0, title: { text: 'Coefficient', side: 'top', font: { size: 12 } },
      },
    };
    const layout = Object.assign(base(narrow ? 400 : 420), {
      margin: { l: 10, r: 10, t: 10, b: 70 },
      // On phones every second refit year keeps the labels horizontal.
      xaxis: { ticks: '', showgrid: false, zeroline: false, type: 'category', tickangle: 0, tickvals: narrow ? years.filter((_, k) => k % 2 === 0) : years },
      yaxis: { autorange: 'reversed', ticks: '', showgrid: false, zeroline: false, automargin: true, color: cssVar('--ink') },
    });
    window.Plotly.react(coefEl, [trace], layout, config);
  }

  function render() {
    if (growthEl) growthChart();
    if (coefEl) coefficientChart();
  }

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
    Promise.all([loadPlotly((growthEl || coefEl).dataset.plotly), fetch(source).then((r) => r.json())])
      .then(([, json]) => {
        data = json;
        render();
        new MutationObserver(render).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
      })
      .catch(() => { [growthEl, coefEl].forEach((el) => { if (el) el.textContent = 'The interactive chart could not load.'; }); });
  }

  const observer = new IntersectionObserver((entries) => {
    if (entries.some((e) => e.isIntersecting)) { observer.disconnect(); load(); }
  }, { rootMargin: '600px' });
  [growthEl, coefEl].forEach((el) => { if (el) observer.observe(el); });
}());
