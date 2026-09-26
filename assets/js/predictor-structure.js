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

  function baseLayout(title, height) {
    const ink = cssVar('--ink');
    return {
      title: { text: title, x: 0, xanchor: 'left', font: { size: 14, color: ink } },
      height,
      margin: { l: 10, r: 10, t: 40, b: 40 },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: { family: getComputedStyle(root).fontFamily, size: 12, color: cssVar('--muted-ink') },
      hoverlabel: { bgcolor: cssVar('--page-surface'), bordercolor: cssVar('--rule'), font: { color: ink } },
    };
  }

  const colorscale = () => [[0, cssVar('--heat-neg')], [0.5, cssVar('--heat-mid')], [1, cssVar('--heat-pos')]];
  const colorbar = {
    orientation: 'h', thickness: 8, len: 0.45, x: 1, xanchor: 'right', y: -0.02, yanchor: 'top',
    tickvals: [-1, 0, 1], outlinewidth: 0,
  };

  function predictorHeatmap(period) {
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
    const layout = Object.assign(baseLayout(`Correlation between the 80 predictors, ${period}`, wide ? 600 : 420), {
      xaxis: { domain: [wide ? 0.2 : 0.17, 1], visible: false },
      xaxis2: { domain: [0, wide ? 0.16 : 0.13], autorange: 'reversed', visible: false },
      xaxis3: { domain: [wide ? 0.17 : 0.14, wide ? 0.195 : 0.165], visible: false },
      yaxis: { range: [10 * n, 0], visible: false },
    });
    return { traces, layout };
  }

  function themeHeatmap(period) {
    const n = data.themes.length;
    const matrix = square(periodMean(data.theme_pairs), n);
    const names = data.themes.map((t) => t.short);
    const trace = {
      type: 'heatmap', x: names, y: names, z: matrix, zmin: -1, zmax: 1, colorscale: colorscale(), colorbar,
      texttemplate: '%{z:.2f}', xgap: 2, ygap: 2,
      customdata: data.themes.map((a) => data.themes.map((b) => `${a.name} · ${b.name}`)),
      hovertemplate: '<b>ρ = %{z:.2f}</b><br>%{customdata}<extra></extra>',
    };
    const layout = Object.assign(baseLayout(`Correlation between theme composites, ${period}`, heatEl.clientWidth > 560 ? 460 : 380), {
      margin: { l: 76, r: 10, t: 40, b: 60 },
      yaxis: { autorange: 'reversed', ticks: '', color: cssVar('--ink') },
      xaxis: { ticks: '', tickangle: 0, color: cssVar('--ink') },
    });
    return { traces: [trace], layout };
  }

  function icChart(period) {
    const [from, to] = PERIODS[state.period];
    const rows = data.theme_ic.dates
      .map((date, t) => ({ date, values: data.theme_ic.values[t] }))
      .filter((r) => { const y = Number(r.date.slice(0, 4)); return y >= from && y <= to; });
    const traces = data.themes.map((theme, t) => {
      let sum = 0;
      const y = rows.map((r) => { sum += r.values[t] / data.scale; return sum; });
      return {
        type: 'scatter', mode: 'lines', name: `${theme.name} · IC ${(sum / rows.length).toFixed(3)}`,
        x: rows.map((r) => r.date), y, line: { color: themeColor(t), width: 2 },
        hovertemplate: `${theme.short} %{y:.2f}<extra></extra>`,
      };
    });
    const grid = cssVar('--rule');
    const layout = Object.assign(baseLayout(`Each theme's daily IC with the target, added up, ${period}`, 400), {
      margin: { l: 44, r: 10, t: 40, b: 10 },
      hovermode: 'x unified',
      legend: { orientation: 'h', y: -0.12, yanchor: 'top', x: 0, font: { size: 12, color: cssVar('--ink') } },
      xaxis: { showgrid: false, linecolor: grid, ticks: '' },
      yaxis: { gridcolor: grid, zerolinecolor: cssVar('--muted-ink'), title: { text: 'Sum of daily IC', standoff: 6 } },
    });
    return { traces, layout };
  }

  function render() {
    const [from, to] = PERIODS[state.period];
    const period = `${from}–${to}`;
    root.querySelectorAll('[data-period]').forEach((b) => b.setAttribute('aria-checked', String(Number(b.dataset.period) === state.period)));
    root.querySelectorAll('[data-level]').forEach((b) => b.setAttribute('aria-checked', String(b.dataset.level === state.level)));
    const config = { responsive: true, displayModeBar: false };
    const heat = state.level === 'theme' ? themeHeatmap(period) : predictorHeatmap(period);
    window.Plotly.react(heatEl, heat.traces, heat.layout, config);
    const ic = icChart(period);
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
