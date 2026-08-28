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

The regression article figures are refreshed with:

```bash
python3 scripts/render_multiple_linear_regression_figures.py \
  --research-root ../projects/factor_combination
```
