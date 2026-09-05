# Pieter-Jan Inghelbrecht

Source for [piinghel.github.io](https://piinghel.github.io/), a Jekyll site for
research notes on systematic strategies, machine learning, and portfolio
construction.

## Local preview

```bash
bundle install
bundle exec jekyll serve
```

Research figures use matching light/dark SVG variants. Ordinary line charts
have phone-specific layouts where needed; dense figures remain scrollable.
Their generating code lives in `scripts/` or the corresponding study repository
linked below.

## Checks and drafts

```bash
bundle exec jekyll build
python3 scripts/check_site.py _site
python3 -m pip install -r requirements-figures.txt
python3 -m unittest discover -s tests -v
```

The checker validates local links and fragments, SVG XML references, matching
theme dimensions, image descriptions, and exclusion of development
files. After regenerating figures, run
`python3 scripts/check_site.py --update-dimensions` to refresh their intrinsic
sizes before rebuilding the site.

Drafts are excluded from the normal build. Preview the portfolio-attribution
draft explicitly with `bundle exec jekyll serve --drafts`. It reconciles saved
book-level P&L and realized risk but is not a finished sector/style study.

Jekyll remains deliberate: the site needs static articles, equations, SVGs,
stable permalinks, and RSS. The local build already serves those requirements;
a framework migration would not strengthen the research.

## Figure sources

The regression article figures are regenerated from the included aggregate evidence:

```bash
python3 scripts/render_multiple_linear_regression_figures.py \
  --review-dir assets/multiple-linear-regression/evidence
```

The factor correlation comparison can be regenerated from the included matrix:

```bash
python3 scripts/render_multiple_linear_regression_figures.py \
  --factor-correlation-only
```

The primary renderer produces the coefficient heatmap and performance /
drawdown figure. It requires two compact source files in the review directory:
`multiple_linear_selected_coefficient_heatmap_source_c0p01.csv.gz` and
`multiple_linear_selected_return_drawdown_figure_source.csv.gz`. It does not
require IC, penalty-sweep, holdings-tilt or factor-correlation inputs.
The [evidence directory](assets/multiple-linear-regression/evidence) also
contains the ranking and portfolio summaries behind the article tables, plus
the coefficient-persistence diagnostics. These are the three-theme benchmark,
OLS and Ridge results on matched stock-date rows. The figures and reporting
can be reproduced from these aggregate files; full model fitting requires the
original research inputs and dependencies.

To review another validated compact bundle before changing article assets:

```bash
python3 scripts/render_multiple_linear_regression_figures.py \
  --review-dir /path/to/validated-matched-review \
  --output-dir /path/to/new-figure-review
```

This produces light/dark heatmaps and desktop/phone performance figures. The
heatmap uses a common signed scale without cell annotations; exact coefficients
remain in the source bundle. Performance preserves the source series and checks that
drawdowns include the initial index of 1 before adding its starting reference.
Missing, inconsistent or non-positive log-growth evidence is rejected before
any chart is written. Fixture tests check rendering behavior. The published
matched export is also reconciled against the daily returns of all three
starting-week schedules, including costs and initial-index drawdowns.

The historical five-theme size-choice diagnostic uses the retained daily factor scores:

```bash
python3 scripts/check_benchmark_size.py \
  --scores ../projects/factor_combination/outputs/review/five_factor_scores.parquet \
  --output assets/multiple-linear-regression/benchmark-size-sensitivity.csv
```

It compares same-date Spearman rankings and membership of the top/bottom 75
candidate sets. Removing size reweights four factors to 25%; reversing size
retains five 20% weights. Selection ties follow the stable security identifier.
The public CSV contains aggregate diagnostics; the local input contains
security-level scores. Portfolio returns require a separate execution replay.

The timing calculations, figure generators and their portfolio-level inputs live
in [rebalance-tranching](https://github.com/piinghel/rebalance-tranching).
From that repository:

```bash
uv sync --locked
uv run python -m rebalance_tranching.performance
```

The command rebuilds the three schedules and their mixture from January 2022
onward, in both themes and desktop/phone layouts. The same repository owns the
supporting dispersion figure and tests that reconcile the chart-ready returns
with the daily evidence. Only the reviewed SVG copies belong in this site's
`assets/tranching/`; do not maintain another copy of the calculation or renderer.

The low-volatility article was fully reproduced in September 2026 with retained
daily outputs in its research project. The latest run uses commit `0f8acbe`,
which values exits and retained positions from the execution-date price panel
when calculating turnover. Gross returns and non-cost diagnostics reconcile
with the previous run; Table 1, terminal wealth and the net performance figure
use the corrected costs. The optimizer figures were regenerated
from the active main-worktree evidence. Older experimental branches and their
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
`_sass/_figures.scss` owns figure sizing. Dense figures and tables scroll within
the article on narrow screens. Keep one shared composition for both themes.
The retired Minima overrides, unused social icons, signal-flow diagram, and
duplicate turnover chart have been removed with their callers.
