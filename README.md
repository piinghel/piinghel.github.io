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

The five-factor correlation map can be regenerated independently from the
retained development matrix:

```bash
python3 scripts/render_multiple_linear_regression_figures.py \
  --research-root ../projects/factor_combination \
  --factor-correlation-only
```

The full figure command requires the compact MLR figure-source files expected by
`render_multiple_linear_regression_figures.py`. They are not present in the
current local factor-combination folder or its recoverable raw-run archive, so
the published MLR SVGs remain the retained assets until that source bundle is
restored. The figure code can still be reviewed, but a clean full regeneration
cannot currently be claimed.

The timing article now uses the frozen constrained Ridge portfolio, not the
unreproducible archived LightGBM example. Its two figures and downloadable
aggregate metrics come from `portfolio_optimization.rebalance_timing` in the
[portfolio-optimization project](https://github.com/piinghel/portfolio-optimization).
The source manifest contains the hashes of the three schedule-return inputs.
No licensed security-level data are published by this site.

The low-volatility article was fully reproduced in September 2026 with retained
daily outputs in its research project. The optimizer figures were regenerated
from the active main-worktree evidence. Older experimental branches and their
reports are historical, not interchangeable with the current article's runs.
