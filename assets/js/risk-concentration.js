/* Risk-concentration article (Plotly): the largest principal component's share of
   forecast variance at each rebalance, with the component's rank on hover.
   Data: pc-share.json (scripts/export_risk_concentration.py). */
(function () {
  'use strict';

  const el = document.getElementById('rc-pc-share');
  if (!el) return;
  const LATER_START = '2022-01-01';
  const CAP = 10;
  let data = null;

  const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const config = { responsive: true, displayModeBar: false };

  function render() {
    const above = (s) => s > CAP;
    const trace = (keep, color, size) => {
      const idx = data.share_pct.map((s, i) => (keep(s) ? i : -1)).filter((i) => i >= 0);
      return {
        type: 'scatter', mode: 'markers', x: idx.map((i) => data.dates[i]), y: idx.map((i) => data.share_pct[i]),
        customdata: idx.map((i) => data.pc[i]), marker: { color, size, opacity: 0.85 },
        hovertemplate: '%{x|%-d %b %Y}<br>Largest share %{y:.1f}% · component %{customdata}<extra></extra>',
      };
    };
    const last = data.dates[data.dates.length - 1];
    const layout = {
      height: el.clientWidth < 500 ? 280 : 320,
      margin: { l: 44, r: 12, t: 30, b: 34 },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: { family: cssVar('--font-sans'), size: 12, color: cssVar('--muted-ink') },
      hoverlabel: { bgcolor: cssVar('--page-surface'), bordercolor: cssVar('--rule'), font: { color: cssVar('--ink') } },
      showlegend: false,
      xaxis: { type: 'date', showgrid: false, zeroline: false, fixedrange: true },
      yaxis: { ticksuffix: '%', gridcolor: cssVar('--rule'), zeroline: false, fixedrange: true, rangemode: 'tozero' },
      shapes: [
        { type: 'rect', xref: 'x', yref: 'paper', x0: LATER_START, x1: last, y0: 0, y1: 1,
          fillcolor: cssVar('--soft-accent'), line: { width: 0 }, layer: 'below' },
        { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: CAP, y1: CAP,
          line: { color: cssVar('--muted-ink'), width: 1, dash: 'dot' } },
      ],
      annotations: [
        { text: 'Largest component share of forecast variance', x: 0, xref: 'paper', xanchor: 'left',
          xshift: -44, y: 1, yref: 'paper', yanchor: 'bottom', yshift: 8, showarrow: false,
          font: { size: 13, color: cssVar('--ink') } },
      ],
    };
    window.Plotly.react(el, [trace((s) => !above(s), cssVar('--muted-ink'), 4), trace(above, cssVar('--accent'), 5)], layout, config);
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
    Promise.all([loadPlotly(el.dataset.plotly), fetch(el.dataset.source).then((r) => r.json())])
      .then(([, json]) => {
        data = json;
        render();
        new MutationObserver(render).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
      })
      .catch(() => { el.textContent = 'The interactive chart could not load.'; });
  }

  const observer = new IntersectionObserver((entries) => {
    if (entries.some((e) => e.isIntersecting)) { observer.disconnect(); load(); }
  }, { rootMargin: '300px' });
  observer.observe(el);
})();
