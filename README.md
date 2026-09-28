# Pieter-Jan Inghelbrecht

Source for [piinghel.github.io](https://piinghel.github.io/), a Jekyll site for
research notes on systematic strategies, machine learning, and portfolio
construction.

Layouts, includes and styles are maintained directly in this repository.
The Gemfile declares Jekyll and the feed/SEO plugins; no theme gem is needed.

## Local preview

```bash
bundle install
bundle exec jekyll serve
```

## Article reading order

`_data/reading_order.yml` defines the research sequence used by Previous/Next links:
low-volatility sizing → regression → portfolio construction → P&L attribution 1–2
→ resources. The tranching article is unpublished (`published: false`) and out of
the sequence until it is rebuilt; its assets stay in place.
The homepage lists posts newest first, with the publication date and topic on
every entry; posts published on the same day list the latest part first (Part 2,
then 1). Resources (`navigation: false`) stays in the header rather than the list.
Previous/Next links follow the sequence from
its beginning. Place new articles beside their prerequisites and follow-ups;
keep numbered series consecutive, in part order. Publication dates and RSS
remain chronological. Draft URLs reserve a future place without publishing them.
Posts missing from the sequence appear first in Previous/Next order;
assign their editorial position before publishing. The post layout uses
`_includes/ordered-posts.html`; the homepage sorts by publication date. The attribution parts stay together
in `_data/reading_order.yml`; `series_id` and `series_order` identify the series
without changing publication dates.

## Checks and drafts

The normal build excludes drafts. Use `--drafts --unpublished` for a local preview.

```bash
bundle exec jekyll build
python3 scripts/check_site.py _site
python3 -m pytest -q tests
git diff --check
```

The checker validates local links and fragments, SVG XML references, matching
theme dimensions, image descriptions, and exclusion of development
files. After regenerating figures, run
`python3 scripts/check_site.py --update-dimensions` to refresh their intrinsic
sizes before rebuilding the site.

Jekyll remains deliberate: the site needs static articles, equations, SVGs,
stable permalinks, and RSS. The local build already serves those requirements;
a framework migration would not strengthen the research.

## Figure sources

### Interactive chart standard

Use the shared `scripts/blog_charts.py` exporter, `assets/js/blog-charts.js`
renderer and `blog-chart.html` include for new finalized figures. The first
reference is the low-volatility article; other articles migrate after review.
Keep article prose, results and conclusions unchanged during chart conversions.
Do not convert evidence still being rerun. Export only allowlisted, neutrally
named portfolio aggregates, never raw inputs or their metadata.

Add `interactive_charts: true` to the post front matter. A minimal export:

```python
from pathlib import Path
from scripts.blog_charts import series, write_chart

write_chart(Path("assets/example/performance.json"),
    ["2025-01-02", "2025-01-03", "2025-01-06"],
    [series("strategy", "Strategy", "strategy", [0.0, 0.01, -0.005])],
    {"performance": {"kind": "performance", "series": ["strategy"],
                     "drawdown": True, "note": "After costs; zero-cash Sharpe."}})
```

Embed with a retained static fallback:

```liquid
{% raw %}{% include blog-chart.html chart="performance"
   source="/assets/example/performance.json"
   base="/assets/example/performance" label="Strategy growth and drawdown" %}{% endraw %}
```

Use `role` for shared colours; `episodes` are `[label, start, end]` triples.
An `index` role supplies market context (`benchmark: true` defaults it on).
Keep only the central comparison visible; put optional series, dates and presets
under Explore. Do not add miniature slider previews. Show subtotals with nested
components rather than additive peers. Extend the helper for new chart families.

Performance paths rebase to 100 at the selected close; statistics use subsequent
daily returns. Prepend a zero-return capital anchor to retain the original first
return in Full. Bar windows include both endpoints. Return compounds; sample
volatility and arithmetic zero-cash Sharpe use 252 sessions/year. Linked book
contributions are not standalone returns. Preserve each article's conventions.
Long displays sample weekly endpoints and extremes, but statistics retain every
daily observation. The pinned Plotly bundle loads once; SVGs are fallbacks.

Regenerate the reference with:

```bash
python3 scripts/export_low_vol_charts.py --baseline /path/to/completed/run --hedge /path/to/completed/hedge
python3 -m unittest discover -s tests
node --test tests/blog_charts.test.cjs
```

Before committing, reconcile full-window values, inspect desktop/phone and both
themes, test ranges and legends, and run the site checks. Scan the diff, exports
and built site for confidential source identifiers. Keep checks, mismatches and
page-weight comparisons in the private review, not in article prose.

Every figure has light/dark SVG variants, with phone layouts where needed, drawn
from one composition per viewport. Renderers in `scripts/` read only the aggregate
JSON or CSV beside the figures; an `--outputs`, `--sweep` or `--geometry` option
first refreshes that aggregate from the research project's saved results. Install
`requirements-figures.txt` (Matplotlib 3.10.8 reproduces the committed SVGs byte
for byte), run the renderer from this directory, then
`python3 scripts/check_site.py --update-dimensions`.

| Article | Figures | Source |
| --- | --- | --- |
| Low volatility | 1 and 3 | `python -m low_volatility_factor.hedge_figures` in [low-vol-to-portfolio](https://github.com/piinghel/low-vol-to-portfolio) |
| | 2 and 4 | `python -m low_volatility_factor.article_figures` in the same repository |
| Regression | 1 (explorer), 3–5 | `assets/js/predictor-structure.js`, `assets/js/regression-results.js`; data from `scripts/export_mlr_data.py` |
| | 1 (no-JavaScript fallback) | `scripts/render_multiple_linear_regression_figures.py` |
| | 2 | `scripts/render_mlr_training_design.py` |
| Joint sizing | all | private portfolio-optimization project (see below) |
| Attribution Part 1 | 1 | `scripts/render_attribution_pnl.py` |
| | 2–4 | `scripts/render_attribution_themes.py` |
| Attribution Part 2 | 1–2 | `scripts/render_attribution_themes.py` |
| Rebalancing luck | 1–3 | `rebalance_tranching.grid_figures` and `.performance` in [rebalance-tranching](https://github.com/piinghel/rebalance-tranching) |

The regression evidence and its provenance are described in
[`assets/multiple-linear-regression/evidence`](assets/multiple-linear-regression/evidence/README.md).
The attribution aggregates come from the private `performance_attribution`
project, on the 80-predictor Ridge optimizer book:
`render_attribution_pnl.py --outputs` reads the whole-history ledger
(`outputs/full-history-ridge80-b3k155-*`), and `render_attribution_themes.py
--outputs` reads the composite theme attribution (`outputs/factors-composite-calendar-20260928`,
study `studies/2026-09-theme-attribution-over-time`). The public files contain
portfolio aggregates only.

The tranching calculations and renderers live only in rebalance-tranching; copy
the reviewed SVGs into `assets/tranching/` rather than maintaining a second
renderer. From that repository:

```bash
uv sync --locked
uv run python -m rebalance_tranching.grid_figures --input output/calendar --output output
uv run python -m rebalance_tranching.performance
```

The low-volatility figures are rendered from the retained September 2026 run
(`output/turnover-review-2026-09-05` and `output/point-in-time-beta-2026-09-14`
in that project); its README lists the commands.

The optimizer figures were regenerated from the active main-worktree evidence
of the private portfolio-optimization project. Older experimental branches and their
reports are historical, not interchangeable with the current article's runs.

## Research repositories

| Material | Location | Reproduction scope |
| --- | --- | --- |
| Site and regression figure sources | This repository | Matched Ridge figures and result tables from included aggregate evidence; correlation chart from its included matrix |
| Low-volatility sizing | [low-vol-to-portfolio](https://github.com/piinghel/low-vol-to-portfolio) | Independent sizing example; full runner needs its configured inputs and dependencies |
| Optimizer methods and evidence | [portfolio-optimization-study](https://github.com/piinghel/portfolio-optimization-study) | One-rebalance control example and figures from included portfolio results |
| Rebalance tranching | [rebalance-tranching](https://github.com/piinghel/rebalance-tranching) | Mixture calculations, examples and figures from included daily portfolios |
| Ridge estimator and research index | [systematic-equity-research](https://github.com/piinghel/systematic-equity-research) | Sample-scaled estimator and a runnable example |

Each study records its own evidence and reproduction scope. Returns from a
different portfolio specification cannot substitute for a matched model
comparison.

## Site maintenance

The reusable [Quant Blog Style skill](.agents/skills/quant-blog-style/SKILL.md)
records the house conventions for prose, figures, captions, tables and mobile
presentation. Invoke it as `$quant-blog-style` when preparing future posts.

`_sass/site.scss` owns layout, typography, tables, and theme tokens;
`_sass/_figures.scss` owns figure sizing. `.compact-table` is the narrow-table
style shared across articles. Dense figures and tables scroll within the
article on narrow screens. Keep one shared composition for both themes.
