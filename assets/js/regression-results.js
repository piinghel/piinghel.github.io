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
    font: { family: getComputedStyle(document.body).fontFamily, size: 12, color: cssVar('--muted-ink') },
    hoverlabel: { bgcolor: cssVar('--page-surface'), bordercolor: cssVar('--rule'), font: { color: cssVar('--ink') } },
  });
  const config = { responsive: true, displayModeBar: false };

  // Line-end labels, pushed apart vertically when two series finish close together.
  function endLabels(names, last) {
    const ends = names
      .map((name) => ({ name, y: Math.log10(data.growth[name].growth[data.growth[name].growth.length - 1]) }))
      .sort((a, b) => b.y - a.y);
    const gap = 0.045; // log10 units, about one label height at this chart size
    ends.forEach((end, k) => { if (k) end.y = Math.min(end.y, ends[k - 1].y - gap); });
    return ends.map((end) => ({
      x: last, y: end.y, yref: 'y', xanchor: 'left', xshift: 6,
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
    const last = data.dates[data.dates.length - 1];
    const grid = cssVar('--rule');
    const layout = Object.assign(base(growthEl.clientWidth > 560 ? 460 : 400), {
      margin: { l: 48, r: 70, t: 10, b: 30 },
      showlegend: false,
      hovermode: 'x unified',
      xaxis: { showgrid: false, linecolor: grid, ticks: '' },
      yaxis: { type: 'log', domain: [0.34, 1], gridcolor: grid, title: { text: 'Growth of $1', standoff: 4 } },
      yaxis2: { domain: [0, 0.26], gridcolor: grid, zerolinecolor: grid, title: { text: 'Drawdown %', standoff: 4 } },
      annotations: endLabels(names, last),
    });
    window.Plotly.react(growthEl, traces, layout, config);
  }

  const wrap = (text, width) => text.replace(new RegExp(`(.{1,${width}})(\\s+|$)`, 'g'), '$1<br>').replace(/<br>$/, '');

  function coefficientChart() {
    const c = data.coefficients;
    const narrow = coefEl.clientWidth < 560;
    const labels = c.predictors.map((p) => wrap(p.description, narrow ? 26 : 44));
    const limit = Math.max(...c.values.flat().map(Math.abs));
    const trace = {
      type: 'heatmap', x: c.refit_years.map(String), y: labels, z: c.values, zmin: -limit, zmax: limit,
      colorscale: [[0, cssVar('--heat-neg')], [0.5, cssVar('--heat-mid')], [1, cssVar('--heat-pos')]],
      xgap: 2, ygap: 2,
      customdata: c.predictors.map((p) => c.refit_years.map(() => `${p.description} · ${p.theme}`)),
      hovertemplate: '<b>%{z:.3f}</b><br>%{customdata}<br>Refit %{x}<extra></extra>',
      colorbar: { orientation: 'h', thickness: 8, len: 0.5, x: 1, xanchor: 'right', y: -0.12, yanchor: 'top', outlinewidth: 0 },
    };
    const layout = Object.assign(base(narrow ? 520 : 440), {
      margin: { l: 10, r: 10, t: 10, b: 60 },
      xaxis: { ticks: '', type: 'category', tickangle: narrow ? -45 : 0 },
      yaxis: { autorange: 'reversed', ticks: '', automargin: true, color: cssVar('--ink') },
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
