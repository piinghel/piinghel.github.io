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

### Drafts in progress

This local branch prepares two posts. Neither is approved for publication.
Both live in `_drafts/` with `published: false` and are excluded from normal builds.

- `_drafts/research-workflow.md`: how the document library, experiment registry
  and blog connect sources, tests and decisions.
- `_drafts/portfolio-attribution.md`: the combined attribution article and
  dashboard walkthrough. It develops the accounting, additive/linked conventions,
  covariance risk, factor interpretation and prediction explanations in one place,
  as a personal study grounded in Paleologo's two books and real portfolio data.
  The former short dashboard introduction has been merged into this article.

Preview them with the site's existing layout and themes:

```bash
bundle exec jekyll serve --config _config.yml,_config.preview.yml --drafts --unpublished --host 127.0.0.1 --port 4001
```

Open `/drafts/research-workflow/` or `/quants/portfolio-attribution.html`.

The article's controlling question is: understand what the whole strategy is
doing over time, which exposures and positions drive its returns and risks,
and what changes deserve investigation. The route is strategy history →
sectors/industries/factors → stocks within each contribution → position and
prediction histories → a relevant research decision. The short drawdown is
one worked example, not the thesis of the article.

Write for a portfolio manager, quant researcher or allocator. Keep source-copy
metadata, unfinished-work notes and revision history here, out of the article.
Only retain explanations that help interpret a display or answer a practical
question; collapse useful derivations, and delete unrelated material.
The draft now uses verified saved-ledger aggregates for full strategy history,
annual long/short contributions, changing covered style exposures, matched
factor payoffs, sector/industry stock groupings and within-factor stock drivers.
The five figures pair history with period P&L, exposures through time, the book
bridge, factor P&L with realized covariance risk, and the existing Rocket score
comparison. The article keeps attribution coverage and model dependence visible.
No refits, trading-rule changes or counterfactual portfolios were run.

Next research steps are deliberately separate: resolve material uncovered P&L,
then compare stock selection and risk-weighted sizing on matched support. An
exposure-limit test needs its own controlled design and feasible costed replay.
These are questions raised by the article, not completed strategy improvements.
Publication still requires explicit user approval; keep this branch local.

The workflow post can stay short; add one concrete source-to-decision example
when refining it.

For attribution evidence, start in the existing `performance_attribution`
registry project. The book totals reference revision 1 of
`performance-attribution:stock-heatmap:finding:short-drawdown`, its verified run,
and `performance-attribution:stock-heatmap:artifact:observations` (lines 360–367).
The older linked-drawdown and whole-period risk tables were removed from the
article because they distract from this episode and their original export has
not been located. They remain recoverable from local commit `9ecc65f`; match
their evidence before reusing them. They are not newly verified results.

The original bridge and prediction figures use revision 1 of the verified
stock-heatmap observations artifact: book totals at lines 360–367, Rocket's
prediction at lines 17–75, and position observations at lines 2–16.

New evidence belongs to `performance_attribution` experiment
`performance-attribution:exp:article-strategy-evolution`. Use its verified run
and `performance-attribution:article-evolution:artifact:aggregates`, revision 1.
The artifact holds source hashes, definitions and complete aggregate inputs;
current interpretations belong in the registry. Reproduction code is the
adjacent private `article-evidence/analyze.py`, taking explicit `--source` and
`--output` paths. It validates daily factor reconciliation, signed book totals,
classification totals, fitted exposure × factor return, stock-driver totals,
and covariance-risk reconciliation. It does not alter saved observations.

Render the new exhibits from that registered aggregate (kept outside the site):

```bash
python3 scripts/render_attribution_history.py \
  --source /path/to/verified/aggregates.json \
  --source-sha256 bb75c2069952b34a00a55b76a980c28d92d9dec73bd0b70501c1f85d4b1572cb \
  --output-dir _draft_assets/portfolio-attribution
```

Reproduce the figures from the registry artifact's local file:

```bash
python3 scripts/render_attribution_figures.py \
  --source /path/to/verified/explore_stock_histories.json \
  --source-sha256 9589895774cd7a5f75c8cba4af80a0c3cd2ba6dea070a14d949201e3bc956950 \
  --output-dir _draft_assets/portfolio-attribution
python3 scripts/check_site.py --update-dimensions
```

The source artifact stays outside this repository. Normal builds exclude
`_draft_assets`; the local preview configuration includes it. Keep these outside
the theme's `assets` directory because Jekyll's theme asset reader bypasses
normal source exclusions.
Check that both the article and its real-data figures are absent from a normal
build before any later publication decision.

### Attribution reading plan

Read one section, derive its identity, then connect it to one real-data display.
The book sections guide the derivations; the equal-risk sizing comparison remains unrun.

| Reading | Physical PDF pages (printed pages) | Practical question and next display |
| --- | --- | --- |
| *Advanced Portfolio Management*, 2021, §8.1.1 | 136–138 (124–126) | From the book-level bridge to a reconciled factor breakdown. |
| *Elements*, 9 September 2024 draft, §14.1 | 453–454 (427–428) | Which holdings apply to each return, and what does trading P&L contain? |
| *Elements*, §14.2 | 455–458 (429–432) | How can factor/residual estimation errors cancel while total P&L reconciles? |
| *Advanced Portfolio Management*, §8.2.1 | 140–145 (128–133) | Define actual versus equal-sized positions, the included holdings, and feasibility limits. |
| *Elements*, §14.4 | 469–475 (443–449) | Derive selection, risk-weighted sizing and effective diversification; then specify a real-data comparison. |
| Later: *Elements*, §14.3; *Advanced Portfolio Management*, timing discussion in §8.2.1 | Locate and read the complete relevant subsections before drafting | Correlated-factor interpretation, then allocation through time. |

Exact library editions: `paleologo_2021_advanced_portfolio_management.pdf`
(document `da1e85e5a83a0af7`) and
`paleologo_elements_of_quantitative_investing_draft_2024-09-09.pdf`
(document `1be2bc901895cf0b`). The latter is a private author draft, not the
published 2025 edition; do not redistribute the PDF or its page images.
The article's algebra is explanatory, and its figures are our own renderings
of the saved research observations. Factor/sizing counterfactuals need a
separately agreed diagnostic design before computation.

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

Drafts are excluded from the normal build. Use both `--drafts` and `--unpublished`
to preview these explicitly unpublished articles. The attribution draft is an
explanatory study of saved observations, with no causal or out-of-sample claim.

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
