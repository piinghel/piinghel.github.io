# Pieter-Jan Inghelbrecht

Source for [piinghel.github.io](https://piinghel.github.io/), a Jekyll site for
research notes on systematic strategies, machine learning, and portfolio
construction.

## Local preview

```bash
bundle install
bundle exec jekyll serve
```

Research figures use one shared layout at every viewport width, with light and
dark SVG variants. Their generating code lives in `scripts/` or the
corresponding project under `projects/`.

## Checks and drafts

```bash
bundle exec jekyll build
python3 scripts/check_site.py _site
python3 -m pip install -r requirements-figures.txt
python3 -m unittest discover -s tests -v
```

The checker validates local links and fragments, SVG XML references, matching
theme dimensions, image descriptions, and exclusion of private development
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

The regression article figures are refreshed with:

```bash
python3 scripts/render_multiple_linear_regression_figures.py \
  --research-root ../projects/factor_combination
```

The factor correlation comparison can be regenerated from the included matrix:

```bash
python3 scripts/render_multiple_linear_regression_figures.py \
  --factor-correlation-only
```

The full figure command requires the compact MLR figure-source files expected by
`render_multiple_linear_regression_figures.py`. They are not present in the
current local factor-combination folder or its recoverable raw-run archive, so
the published MLR SVGs remain the retained assets until that source bundle is
restored. The figure code can still be reviewed, but a clean full regeneration
cannot currently be claimed.

The size-choice diagnostic uses the retained daily factor scores:

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

The main timing figure is reproduced from the included portfolio-level daily
net returns in `assets/tranching/schedule_returns.csv`, using Matplotlib and
NumPy from `requirements-figures.txt`:

```bash
python3 scripts/render_timing_performance.py
```

It shows the three starting weeks and their equal-notional mixture, compounded
separately within development and later history. The mixture column is checked
against the mean of the three schedule returns before export. These 6,963 matched
dates come from `outputs/review/timing/timing_daily.parquet` in the systematic
equity research project. Its source manifest records the schedule-return inputs.
The older combination-dispersion figure remains reproducible with
`python3 scripts/render_timing_figure.py` and the included aggregate metrics.
No licensed security-level data are published by this site.

The low-volatility article was fully reproduced in September 2026 with retained
daily outputs in its research project. The optimizer figures were regenerated
from the active main-worktree evidence. Older experimental branches and their
reports are historical, not interchangeable with the current article's runs.

The optimizer's downloadable CSVs are copies of
`article_period_comparison.csv` and `article_parameter_sensitivity.csv` from
the active research worktree at `5ed6a51`. Table 2 uses B2 and B3 from the first
file, the zero trade-coefficient row for buffer only, and holding cutoff 75 for
penalty only from the second. All four rows use development through 2021.

## Research repositories

| Material | Location | Reproduction scope |
| --- | --- | --- |
| Blog, timing chart, correlation chart, size diagnostic | This public repository | Charts from included aggregate CSVs; size diagnostic requires local daily scores |
| Low-volatility backtest | [low-vol-to-portfolio](https://github.com/piinghel/low-vol-to-portfolio) | Licensed input export and shared P&L package required |
| Optimizer figures, timing returns, Ridge estimator | [systematic-equity-research](https://github.com/piinghel/systematic-equity-research) | Included portfolio-level evidence; independently runnable |
| Full portfolio and timing backtests | Private `portfolio-optimization` repository | Shared research packages and licensed inputs required |
| Factor construction | Private `factor-combination` repository | Standalone factors retained; matched OLS–Ridge bundle missing |

Source recovery for the matched OLS–Ridge comparison covered project folders,
worktrees, research caches, local Git history, and available GitHub project
trees in September 2026. Optimizer returns use the selected Ridge strategy and
cannot substitute for the missing paired OLS results.

## Site maintenance

`_sass/site.scss` owns layout, typography, tables, and theme tokens;
`_sass/_figures.scss` owns figure sizing. Dense figures and tables scroll within
the article on narrow screens. Keep one shared composition for both themes.
The retired Minima overrides, unused social icons, signal-flow diagram, and
duplicate turnover chart have been removed with their callers.
