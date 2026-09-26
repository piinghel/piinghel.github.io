/* Predictor-structure explorer for the regression article.
   One period filter scopes both panels: the correlation heatmap (theme composites or
   all 80 predictors) and each theme's IC with the target. Data: predictor-structure.json. */
(function () {
  'use strict';

  const root = document.getElementById('predictor-structure-explorer');
  if (!root) return;

  const PRESETS = [[1998, 2021], [1998, 2003], [2004, 2008], [2009, 2013], [2014, 2018], [2019, 2021]];
  const SVG = 'http://www.w3.org/2000/svg';
  const $ = (selector) => root.querySelector(selector);
  const state = { from: 1998, to: 2021, level: 'predictor', ic: 'cumulative', focus: null };
  let data = null;

  const el = (name, attrs, parent) => {
    const node = document.createElementNS(SVG, name);
    for (const [key, value] of Object.entries(attrs || {})) node.setAttribute(key, value);
    if (parent) parent.appendChild(node);
    return node;
  };
  const html = (name, text, parent, className) => {
    const node = document.createElement(name);
    if (text != null) node.textContent = text;
    if (className) node.className = className;
    if (parent) parent.appendChild(node);
    return node;
  };
  const fmt = (value, digits = 2) => (value < 0 ? '−' : '') + Math.abs(value).toFixed(digits);
  const css = (name) => getComputedStyle(root).getPropertyValue(name).trim();
  const seriesColor = (theme) => `var(--pse-s${theme + 1})`;

  /* --- data for the selected period ------------------------------------ */

  function yearWeights() {
    return data.years.map((year, i) => (year >= state.from && year <= state.to ? data.dates_per_year[i] : 0));
  }

  // Date-weighted mean of yearly upper-triangle vectors, as correlations.
  function periodMean(yearly) {
    const weights = yearWeights();
    const total = weights.reduce((a, b) => a + b, 0);
    const out = new Float64Array(yearly[0].length);
    yearly.forEach((row, y) => {
      if (!weights[y]) return;
      for (let k = 0; k < row.length; k += 1) out[k] += row[k] * weights[y];
    });
    for (let k = 0; k < out.length; k += 1) out[k] /= total * data.scale;
    return out;
  }

  const upperIndex = (i, j, n) => (i < j ? i * n - (i * (i + 1)) / 2 + (j - i - 1) : upperIndex(j, i, n));
  const cell = (values, i, j, n) => (i === j ? 1 : values[upperIndex(i, j, n)]);

  function periodIc() {
    const rows = [];
    data.theme_ic.dates.forEach((date, t) => {
      const year = Number(date.slice(0, 4));
      if (year >= state.from && year <= state.to) rows.push({ date, year, values: data.theme_ic.values[t] });
    });
    return rows;
  }

  function icSeries(rows) {
    const k = data.themes.length;
    if (state.ic === 'cumulative') {
      const sums = new Array(k).fill(0);
      return rows.map((row) => ({
        x: row.date,
        label: row.date,
        values: row.values.map((v, t) => (sums[t] += v / data.scale)),
      }));
    }
    const byYear = new Map();
    rows.forEach((row) => {
      const entry = byYear.get(row.year) || { n: 0, sums: new Array(k).fill(0) };
      entry.n += 1;
      row.values.forEach((v, t) => { entry.sums[t] += v / data.scale; });
      byYear.set(row.year, entry);
    });
    return [...byYear.entries()].map(([year, entry]) => ({
      x: `${year}-07-01`,
      label: String(year),
      values: entry.sums.map((s) => s / entry.n),
    }));
  }

  /* --- colour ------------------------------------------------------------- */

  const hex = (value) => [1, 3, 5].map((i) => parseInt(value.slice(i, i + 2), 16));
  function diverging() {
    const neg = hex(css('--pse-neg'));
    const mid = hex(css('--pse-mid'));
    const pos = hex(css('--pse-pos'));
    return (value) => {
      const t = Math.min(1, Math.abs(value));
      const pole = value < 0 ? neg : pos;
      const rgb = mid.map((m, c) => Math.round(m + (pole[c] - m) * t));
      return `rgb(${rgb.join(',')})`;
    };
  }

  /* --- tooltip ------------------------------------------------------------ */

  const tooltip = $('.pse-tooltip');
  function showTooltip(event, build) {
    tooltip.replaceChildren();
    build(tooltip);
    tooltip.hidden = false;
    const box = root.getBoundingClientRect();
    const tip = tooltip.getBoundingClientRect();
    let left = event.clientX - box.left + 14;
    if (left + tip.width > box.width) left = event.clientX - box.left - tip.width - 14;
    tooltip.style.left = `${Math.max(0, left)}px`;
    tooltip.style.top = `${event.clientY - box.top + 14}px`;
  }
  const hideTooltip = () => { tooltip.hidden = true; };

  /* --- heatmap ------------------------------------------------------------ */

  function heatmap() {
    const svg = $('.pse-heat');
    svg.replaceChildren();
    const width = svg.clientWidth || 720;
    const narrow = width < 520;
    const themeLevel = state.level === 'theme';
    const names = themeLevel ? data.themes.map((t) => (narrow ? t.short : t.name)) : null;
    const n = themeLevel ? data.themes.length : data.predictors.length;
    const values = periodMean(themeLevel ? data.theme_pairs : data.predictor_pairs);
    const color = diverging();
    const left = narrow ? 70 : 138;
    const bottom = themeLevel ? (narrow ? 58 : 30) : 8;
    const size = Math.min((width - left) / n, themeLevel ? 72 : 9);
    const side = size * n;
    svg.setAttribute('viewBox', `0 0 ${left + side} ${side + bottom}`);
    const gap = themeLevel ? 2 : 0;

    const cells = el('g', { transform: `translate(${left},0)` }, svg);
    for (let i = 0; i < n; i += 1) {
      for (let j = 0; j < n; j += 1) {
        const v = cell(values, i, j, n);
        el('rect', {
          x: j * size + gap / 2, y: i * size + gap / 2,
          width: size - gap, height: size - gap, rx: themeLevel ? 3 : 0,
          fill: color(v),
        }, cells);
        if (themeLevel && size > 34) {
          const text = el('text', {
            x: j * size + size / 2, y: i * size + size / 2 + 4, 'text-anchor': 'middle',
            class: Math.abs(v) > 0.55 ? '' : 'pse-ink',
          }, cells);
          if (Math.abs(v) > 0.55) text.setAttribute('fill', css('--pse-surface') || '#fff');
          text.textContent = fmt(v);
        }
      }
    }

    if (themeLevel) {
      names.forEach((name, i) => {
        const label = el('text', { x: left - 8, y: i * size + size / 2 + 4, 'text-anchor': 'end', class: 'pse-ink' }, svg);
        label.textContent = name;
        const bottomLabel = el('text', {
          x: left + i * size + size / 2, y: side + 16, 'text-anchor': narrow ? 'end' : 'middle',
          transform: narrow ? `rotate(-40 ${left + i * size + size / 2} ${side + 12})` : '',
        }, svg);
        bottomLabel.textContent = data.themes[i].short;
      });
    } else {
      const blocks = [];
      data.predictors.forEach((p, i) => {
        if (!i || p.theme !== data.predictors[i - 1].theme) blocks.push({ theme: p.theme, start: i, end: i + 1 });
        else blocks[blocks.length - 1].end = i + 1;
      });
      const surface = css('--pse-surface') || '#fff';
      blocks.forEach((block, b) => {
        if (b) {
          el('line', { x1: left, x2: left + side, y1: block.start * size, y2: block.start * size, stroke: surface, 'stroke-width': 1.5 }, svg);
          el('line', { x1: left + block.start * size, x2: left + block.start * size, y1: 0, y2: side, stroke: surface, 'stroke-width': 1.5 }, svg);
        }
        const label = el('text', { x: left - 8, y: ((block.start + block.end) / 2) * size + 4, 'text-anchor': 'end', class: 'pse-ink' }, svg);
        label.textContent = narrow ? data.themes[block.theme].short : data.themes[block.theme].name;
      });
    }

    if (state.focus != null) {
      const span = themeLevel
        ? { start: state.focus, end: state.focus + 1 }
        : (() => {
          const idx = data.predictors.map((p, i) => (p.theme === state.focus ? i : -1)).filter((i) => i >= 0);
          return { start: idx[0], end: idx[idx.length - 1] + 1 };
        })();
      const ink = css('--pse-ink');
      el('rect', { x: left, y: span.start * size, width: side, height: (span.end - span.start) * size, fill: 'none', stroke: ink, 'stroke-width': 1.5 }, svg);
      el('rect', { x: left + span.start * size, y: 0, width: (span.end - span.start) * size, height: side, fill: 'none', stroke: ink, 'stroke-width': 1.5 }, svg);
    }

    const hover = el('rect', { fill: 'none', stroke: css('--pse-ink'), 'stroke-width': 1.5, visibility: 'hidden' }, svg);
    const locate = (event) => {
      const point = svg.createSVGPoint();
      point.x = event.clientX; point.y = event.clientY;
      const local = point.matrixTransform(svg.getScreenCTM().inverse());
      const j = Math.floor((local.x - left) / size);
      const i = Math.floor(local.y / size);
      return i >= 0 && j >= 0 && i < n && j < n ? { i, j } : null;
    };
    svg.onpointermove = (event) => {
      const hit = locate(event);
      if (!hit) { hover.setAttribute('visibility', 'hidden'); hideTooltip(); return; }
      hover.setAttribute('x', left + hit.j * size);
      hover.setAttribute('y', hit.i * size);
      hover.setAttribute('width', size);
      hover.setAttribute('height', size);
      hover.setAttribute('visibility', 'visible');
      const v = cell(values, hit.i, hit.j, n);
      showTooltip(event, (tip) => {
        html('strong', `ρ = ${fmt(v)}`, tip);
        if (themeLevel) {
          html('div', `${data.themes[hit.i].name} · ${data.themes[hit.j].name}`, tip);
        } else {
          [hit.i, hit.j].forEach((k) => {
            const p = data.predictors[k];
            const row = html('div', null, tip);
            html('span', `${p.sign < 0 ? '− ' : ''}${p.description}`, row);
            html('span', ` · ${data.themes[p.theme].name}`, row, 'pse-tip-muted');
          });
        }
        html('div', `${state.from}–${state.to}, IC-signed`, tip, 'pse-tip-muted');
      });
    };
    svg.onpointerleave = () => { hover.setAttribute('visibility', 'hidden'); hideTooltip(); };
  }

  /* --- theme IC chart ------------------------------------------------------ */

  function icChart() {
    const svg = $('.pse-ic');
    svg.replaceChildren();
    const series = icSeries(periodIc());
    const width = svg.clientWidth || 720;
    const height = width < 520 ? 230 : 260;
    const pad = { left: 44, right: 12, top: 10, bottom: 26 };
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    if (!series.length) return;
    const k = data.themes.length;
    const all = series.flatMap((s) => s.values).concat([0]);
    let lo = Math.min(...all); let hi = Math.max(...all);
    const margin = (hi - lo) * 0.06 || 0.01; lo -= margin; hi += margin;
    const times = series.map((s) => Date.parse(s.x));
    const t0 = state.ic === 'yearly' ? Date.parse(`${state.from}-01-01`) : times[0];
    const t1 = state.ic === 'yearly' ? Date.parse(`${state.to}-12-31`) : times[times.length - 1];
    const x = (t) => pad.left + ((t - t0) / Math.max(1, t1 - t0)) * (width - pad.left - pad.right);
    const y = (v) => pad.top + (1 - (v - lo) / (hi - lo)) * (height - pad.top - pad.bottom);

    const grid = css('--pse-grid');
    const ticks = niceTicks(lo, hi, 4);
    ticks.forEach((tick) => {
      el('line', { x1: pad.left, x2: width - pad.right, y1: y(tick), y2: y(tick), stroke: tick === 0 ? css('--pse-muted') : grid, 'stroke-width': tick === 0 ? 1 : 0.8 }, svg);
      el('text', { x: pad.left - 6, y: y(tick) + 4, 'text-anchor': 'end' }, svg).textContent = fmt(tick, Math.abs(hi - lo) < 0.2 ? 2 : 1);
    });
    const span = state.to - state.from;
    const step = span > 12 ? 5 : span > 5 ? 2 : 1;
    for (let year = state.from; year <= state.to + 1; year += 1) {
      if ((year - state.from) % step) continue;
      const t = Date.parse(`${year}-01-01`);
      const slack = 10 * 864e5; // the first sampled session can fall a few days into January
      if (t < t0 - slack || t > t1 + slack) continue;
      el('text', { x: x(t), y: height - 6, 'text-anchor': 'middle' }, svg).textContent = String(year);
    }
    el('text', { x: pad.left + 4, y: pad.top + 10, 'text-anchor': 'start' }, svg)
      .textContent = state.ic === 'cumulative' ? 'Sum of daily IC' : 'Mean daily IC';

    for (let t = 0; t < k; t += 1) {
      const d = series.map((s, i) => `${i ? 'L' : 'M'}${x(times[i]).toFixed(1)},${y(s.values[t]).toFixed(1)}`).join('');
      const faded = state.focus != null && state.focus !== t;
      el('path', {
        d, fill: 'none', stroke: seriesColor(t), 'stroke-width': state.focus === t ? 2.5 : 2,
        'stroke-linejoin': 'round', 'stroke-linecap': 'round', opacity: faded ? 0.18 : 1,
      }, svg);
      if (state.ic === 'yearly') {
        series.forEach((s, i) => el('circle', { cx: x(times[i]), cy: y(s.values[t]), r: 2.5, fill: seriesColor(t), opacity: faded ? 0.18 : 1 }, svg));
      }
    }

    const cross = el('line', { y1: pad.top, y2: height - pad.bottom, stroke: css('--pse-muted'), 'stroke-width': 1, visibility: 'hidden' }, svg);
    svg.onpointermove = (event) => {
      const point = svg.createSVGPoint();
      point.x = event.clientX; point.y = event.clientY;
      const local = point.matrixTransform(svg.getScreenCTM().inverse());
      if (local.x < pad.left || local.x > width - pad.right) { cross.setAttribute('visibility', 'hidden'); hideTooltip(); return; }
      let best = 0;
      times.forEach((t, i) => { if (Math.abs(x(t) - local.x) < Math.abs(x(times[best]) - local.x)) best = i; });
      cross.setAttribute('x1', x(times[best])); cross.setAttribute('x2', x(times[best]));
      cross.setAttribute('visibility', 'visible');
      showTooltip(event, (tip) => {
        html('div', series[best].label, tip, 'pse-tip-muted');
        data.themes.forEach((theme, t) => {
          const row = html('div', null, tip, 'pse-tip-row');
          const key = html('span', null, row, 'pse-key'); key.style.background = seriesColor(t);
          html('span', theme.name, row);
          html('b', fmt(series[best].values[t], state.ic === 'cumulative' ? 2 : 3), row);
        });
      });
    };
    svg.onpointerleave = () => { cross.setAttribute('visibility', 'hidden'); hideTooltip(); };
  }

  function niceTicks(lo, hi, count) {
    const raw = (hi - lo) / count;
    const power = 10 ** Math.floor(Math.log10(raw));
    const step = [1, 2, 2.5, 5, 10].map((m) => m * power).find((s) => s >= raw);
    const ticks = [];
    for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-12; v += step) ticks.push(Math.abs(v) < 1e-12 ? 0 : v);
    return ticks;
  }

  /* --- legend and table ---------------------------------------------------- */

  function legend() {
    const list = $('.pse-legend');
    list.replaceChildren();
    const rows = periodIc();
    data.themes.forEach((theme, t) => {
      const mean = rows.reduce((s, r) => s + r.values[t], 0) / (rows.length * data.scale);
      const item = html('li', null, list);
      const button = html('button', null, item);
      button.type = 'button';
      button.setAttribute('aria-pressed', String(state.focus === t));
      const key = html('span', null, button, 'pse-key'); key.style.background = seriesColor(t);
      html('span', theme.name, button);
      html('span', `IC ${fmt(mean, 3)}`, button, 'pse-value');
      button.addEventListener('click', () => { state.focus = state.focus === t ? null : t; render(); });
    });
  }

  function table() {
    const body = $('.pse-table-body');
    body.replaceChildren();
    const values = periodMean(data.theme_pairs);
    const rows = periodIc();
    const n = data.themes.length;
    const tableEl = html('table', null, body);
    html('caption', `Theme composites, ${state.from}–${state.to}: mean daily IC with the target and average correlation with each other theme (IC-signed).`, tableEl);
    const head = html('tr', null, html('thead', null, tableEl));
    html('th', 'Theme', head);
    html('th', 'Mean IC', head);
    data.themes.forEach((t) => html('th', t.short, head));
    const tbody = html('tbody', null, tableEl);
    data.themes.forEach((theme, i) => {
      const tr = html('tr', null, tbody);
      html('th', theme.name, tr).scope = 'row';
      html('td', fmt(rows.reduce((s, r) => s + r.values[i], 0) / (rows.length * data.scale), 3), tr);
      for (let j = 0; j < n; j += 1) html('td', i === j ? '—' : fmt(cell(values, i, j, n)), tr);
    });
  }

  /* --- controls ------------------------------------------------------------ */

  function syncControls() {
    root.querySelectorAll('.pse-periods button').forEach((button) => {
      const [a, b] = button.dataset.period.split('-').map(Number);
      button.setAttribute('aria-checked', String(a === state.from && b === state.to));
    });
    root.querySelectorAll('[data-level]').forEach((b) => b.setAttribute('aria-checked', String(b.dataset.level === state.level)));
    root.querySelectorAll('[data-ic]').forEach((b) => b.setAttribute('aria-checked', String(b.dataset.ic === state.ic)));
    $('.pse-from').value = String(state.from);
    $('.pse-to').value = String(state.to);
    const period = `${state.from}–${state.to}`;
    $('.pse-heat-title').textContent = state.level === 'theme'
      ? `Correlation between theme composites, ${period}`
      : `Correlation between the 80 predictors, ${period}`;
    $('.pse-ic-title').textContent = state.ic === 'cumulative'
      ? `Each theme's IC with the target, added up over ${period}`
      : `Each theme's mean daily IC with the target by year, ${period}`;
  }

  function buildControls() {
    const periods = $('.pse-periods');
    PRESETS.forEach(([a, b], i) => {
      const button = html('button', i ? `${a}–${String(b).slice(2)}` : 'All', periods);
      button.type = 'button';
      button.setAttribute('role', 'radio');
      button.dataset.period = `${a}-${b}`;
      if (!i) button.setAttribute('aria-label', `All years, ${a}–${b}`);
      button.addEventListener('click', () => { state.from = a; state.to = b; render(); });
    });
    ['.pse-from', '.pse-to'].forEach((selector) => {
      const select = $(selector);
      data.years.forEach((year) => { const option = html('option', String(year), select); option.value = String(year); });
      select.addEventListener('change', () => {
        const from = Number($('.pse-from').value); const to = Number($('.pse-to').value);
        state.from = Math.min(from, to); state.to = Math.max(from, to);
        render();
      });
    });
    root.querySelectorAll('[data-level]').forEach((b) => b.addEventListener('click', () => { state.level = b.dataset.level; render(); }));
    root.querySelectorAll('[data-ic]').forEach((b) => b.addEventListener('click', () => { state.ic = b.dataset.ic; render(); }));
  }

  function render() {
    syncControls();
    heatmap();
    icChart();
    legend();
    table();
  }

  fetch(root.dataset.source)
    .then((response) => { if (!response.ok) throw new Error(response.statusText); return response.json(); })
    .then((json) => {
      data = json;
      buildControls();
      $('.pse-status').hidden = true;
      $('.pse-body').hidden = false;
      render();
      let pending = null;
      let lastWidth = $('.pse-body').clientWidth;
      new ResizeObserver(() => {
        const width = $('.pse-body').clientWidth;
        if (width === lastWidth) return;
        lastWidth = width;
        cancelAnimationFrame(pending);
        pending = requestAnimationFrame(render);
      }).observe($('.pse-body'));
      new MutationObserver(render).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    })
    .catch(() => { $('.pse-status').textContent = 'The explorer could not load its data. Figure 2 shows how the themes overlap by year.'; });
}());
