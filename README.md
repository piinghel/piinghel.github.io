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
low-volatility sizing → regression → portfolio construction and risk concentration
→ P&L attribution 1–3 → resources. The tranching, hybrid risk-model and
tree-model articles are unpublished (`published: false`) and out of the sequence
until they are rebuilt; their assets stay in place.
The homepage lists posts newest first, with the publication date and topic on
every entry; posts published on the same day list the latest part first (Part 3,
2, 1). Resources (`navigation: false`) stays in the header rather than the list.
Previous/Next links follow the sequence from
its beginning. Place new articles beside their prerequisites and follow-ups;
keep numbered series consecutive, in part order. Publication dates and RSS
remain chronological. Draft URLs reserve a future place without publishing them.
Posts missing from the sequence appear first in Previous/Next order;
assign their editorial position before publishing. Both layouts use the shared
`_includes/ordered-posts.html` ordering logic. The attribution parts stay together
in `_data/reading_order.yml`; `series_id` and `series_order` identify the series
without changing publication dates.

## Checks and drafts

The unpublished workflow draft is retained in `_drafts/research-workflow.md`.
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

For changes to the attribution explorers, run the browser regression with Node.js
and Playwright installed: `node --test tests/test_article_interactions.cjs`.
It uses Playwright's Chromium, or an existing Chrome executable supplied through
`CHROME_PATH`, and loads only local aggregate inputs.

Jekyll remains deliberate: the site needs static articles, equations, SVGs,
stable permalinks, and RSS. The local build already serves those requirements;
a framework migration would not strengthen the research.

## Figure sources

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
| Risk concentration | 1 | `assets/js/risk-concentration.js`; data from `scripts/export_risk_concentration.py --geometry` |
| | 2 and 3 | `portfolio_optimization.concentration_figure` and `.concentration_migration_figure` (private portfolio-optimization project, `outputs/review/risk_concentration/article_snapshot_20260905`) |
| Attribution Part 1 | 1 | `scripts/render_attribution_pnl.py` |
| | 2 and 5 | `scripts/render_attribution_series.py` |
| | 3 | `scripts/render_attribution_components.py` |
| | 4 (explorer) | `assets/js/attribution-dynamics.js`; data from `scripts/export_attribution_dynamics.py` |
| Attribution Part 2 | 1 | `scripts/render_attribution_pnl.py` |
| | 2 | `scripts/render_attribution_components.py` |
| | 3 | `scripts/render_attribution_holdings.py` |
| | 4 (explorer) | `assets/js/attribution-explorers.js` over `scripts/render_attribution_recoveries.py` |
| Attribution Part 3 | 1 | `scripts/render_attribution_series.py` |
| Rebalancing luck | 1–3 | `rebalance_tranching.grid_figures` and `.performance` in [rebalance-tranching](https://github.com/piinghel/rebalance-tranching) |
| Hybrid risk model | 1 | `scripts/render_hybrid_risk.py` |
| Tree models | 1 | `scripts/render_tree_comparison.py` |

The regression evidence and its provenance are described in
[`assets/multiple-linear-regression/evidence`](assets/multiple-linear-regression/evidence/README.md).
The attribution aggregates come from the private `performance_attribution`
project (`outputs/full_history` and the registered series and beta diagnostics):
`render_attribution_pnl.py --outputs` and `render_attribution_components.py
--outputs` read `outputs/full_history`; `export_attribution_series.py
--diagnostics PATH --beta-history PATH` refreshes `beta-history.json` and keeps only
recovery paths in `explorer-paths.json`; `export_attribution_dynamics.py` rebuilds
`dynamics.json` from the frozen snapshot; Part 3's `rally-evaluation.json` is
the aggregate output of that project's rally evaluation. `recoveries.json` and
`rebound-holdings.json` are frozen aggregates of the private recovery and holdings
diagnostics, with their source hashes recorded inside; the explorer paths come from
`python -m performance_attribution.explorer_export`. The public files contain
portfolio aggregates only; stock examples stay in the private evidence.

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

The optimizer's retained supporting CSVs are copies of
`article_period_comparison.csv` and `article_parameter_sensitivity.csv` from
the active research worktree at `5ed6a51`. Table 2 uses B2 and B3 from the first
file, the zero trade-coefficient row for buffer only, and holding cutoff 75 for
penalty only from the second. All four rows use development through 2021.

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
