---
layout: post
title: "How to Combine Stock Signals with Multiple Linear and Ridge Regression"
date: 2025-02-09
last_modified_at: 2026-09-02
categories: ["Regression"]
article_label: Factor combination · Multiple linear and Ridge regression
permalink: /quants/2025/02/09/multiple-linear-regression.html
---

<p class="article-summary"><strong>TL;DR:</strong> I compare a five-factor score with fixed weights against linear regression that learns weights and directions over 144 predictors. Moving to the learned model raises development-period Sharpe from 0.71 to 0.98, mainly because volatility falls from 9.7% to 7.2%, although the comparison also changes predictors and eligible rows. Ridge shrinks unstable coefficients by about a third but leaves the ranking almost unchanged: rank correlation with OLS is 0.991, and performance is similar before and after 2021. The learned ranking also roughly doubles turnover. The next test must separate learned weighting from the broader predictor set.</p>

This article follows the
[low-volatility study](/quant/2024/12/15/low-volatility-factor.html), which
sizes one signal with inverse-volatility weights. Here I combine many signals
into one ranking. The
[next article](/quants/2026/08/29/portfolio-optimization.html) holds the learned
ranking fixed, sizes the stocks jointly, and makes the allocation account for
its current holdings.

I start with a score built from five factors whose directions and weights are
chosen in advance. It makes every preference visible. I then give multiple
linear regression a broader set of 144 predictors and let it learn the weights
and directions from subsequent stock outcomes.

Once a stock model contains more than a handful of signals, finding another one
is no longer the main problem. The harder decision is how much influence each
signal should have in the combined ranking. Ordinary least squares (OLS) learns
that combination. Ridge uses the same model but shrinks its coefficients when
many predictors contain similar information. The practical question is whether
that restraint improves the ranking or merely steadies the coefficient vector.

Two comparisons answer different questions. Fixed weights versus OLS compares
the five-factor score with the whole broader model. OLS versus Ridge isolates
the penalty because the predictors, target, universe, eligible rows, and
portfolio rule stay the same.

All choices through 2021 belong to the development period. I call January 2022
through May 2026 the later period: a **pseudo-holdout**, because that history
influenced subsequent feature, target, portfolio, and presentation work rather
than remaining untouched. Portfolio results average three staggered
schedules,[^schedules] which run the same full-capital rule from different
starting weeks.

## What stays fixed

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Component</th><th>Shared setting</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Universe</th><td data-label="Shared setting">Point-in-time Russell 1000 membership and daily U.S. equity data, 3 January 1995–27 May 2026</td></tr>
    <tr><th scope="row">Eligibility</th><td data-label="Shared setting">Price of at least five dollars; announced merger targets and duplicate share classes excluded</td></tr>
    <tr><th scope="row">Walk-forward fit</th><td data-label="Shared setting">900 initial training dates; 21-day buffer; 600-date prediction blocks; 12 expanding refits</td></tr>
    <tr><th scope="row">Target</th><td data-label="Shared setting">Within-date, within-sector rank of forward 20-day return divided by forward 20-day volatility</td></tr>
    <tr><th scope="row">Portfolio rule</th><td data-label="Shared setting">Top and bottom 75 stocks; inverse-volatility sizing with stock and book caps</td></tr>
    <tr><th scope="row">Execution and cost</th><td data-label="Shared setting">Three-week rebalancing; 5 bp per dollar traded</td></tr>
    <tr><th scope="row">Evaluation</th><td data-label="Shared setting">Development through 2021; later period from January 2022</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Data, timing, target, portfolio construction, and costs shared by the compared ranking rules.</p>

The 21-day buffer keeps the forward 20-day outcomes used for training outside
the next prediction block. I split each training window into three date-thinned
samples, fit one model to each, and average their predictions. Figure 1 shows
the expanding sequence.

<div class="research-figure walk-forward-figure">
  {%- include walk-forward-figure.html -%}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Expanding walk-forward estimation, with a 21-day buffer before each 600-date prediction block.</p>

The design prevents the most direct leakage across prediction boundaries.

## A fixed score makes every preference visible

Fixed weights provide a useful baseline because every preference is visible. I
group familiar signals into five factors, give each factor the same influence,
and set each direction in advance. Those choices are easy to inspect, though
the factors, horizons, and signs still reflect my judgment.

The defensive factor favours low volatility and upper-tail avoidance—stocks
whose recent gains do not depend on a few sharp up days. Momentum looks for a
trend that remains after skipping the latest month. The other factors favour
lower short positioning, larger companies, and fewer negative-return days.

I turn each measure into a percentile rank among stocks available on the same
date, with higher ranks always meaning more attractive stocks. Low volatility
and upper-tail avoidance split the defensive factor; the five final factors
then receive equal weight. The exact averaging equations are in the appendix.

The factors need not be independent. Figure 2 shows their mean same-date
Spearman rank correlations during development. Each cell compares two final
factor scores on their common stock-date rows; the lower triangle shows each
pair once.

<div class="research-figure factor-correlation-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/factor-correlation" alt="Development-period correlation map for the five final fixed factors, with ten distinct pairwise mean Spearman rank correlations shown once in the lower triangle" version="1" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Mean same-date Spearman rank correlation among the five final fixed factors, 21 May 1997–31 December 2021. The defensive score combines low volatility and upper-tail avoidance.</p>

No factor is a close substitute for another. The largest displayed correlation
is 0.28, between defensive and return consistency; defensive and short
positioning are slightly negative at −0.08. Table A1 reports each factor's
standalone return, but that test does not measure its incremental contribution
to the combined score.

## The regression learns weights and directions

OLS and Ridge receive 144 predictors, but not 144 unrelated ideas. Price-based
measures describe trend, distance from a moving average or earlier high, and
the turbulence of the path. Other families cover company size, market
sensitivity, trading activity, liquidity, and lagged short positioning. Several
ideas appear at multiple horizons, so the model can choose among them while
individual coefficients remain hard to identify.

The raw predictors use different units. For raw value
$$\widetilde X_{i,j,t}$$, let $$R_t(\widetilde X_{i,j,t})$$ be its dense
rank—a rank in which ties share a value—and let $$K_{j,t}$$ be the largest rank
on date $$t$$. I map predictor $$j$$ to

$$
X_{i,j,t}
=2\frac{R_t(\widetilde X_{i,j,t})}{K_{j,t}}-1.
$$

Every input now lies in $$[-1,1]$$. Ranking limits the influence of raw
outliers and prevents dollars from appearing more important than percentages
because their numerical scale is larger. It also discards distance: the model
learns relative order, not a calibrated relationship between a raw signal and
future return.

Figure 3 separates the stages. Raw measures become comparable ranks, the fixed
score or regression combines them, and the shared portfolio rule turns the
resulting stock ranking into positions.

<div class="research-figure signal-flow-figure">
  {%- include signal-combination-flow.html -%}
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Fixed and learned signal-combination pipelines feeding the same stock-selection and portfolio rule.</p>

The target expresses the outcome the regression should prefer. I divide average
return over the next 20 trading days by volatility over the same period, then
rank that result within each date and sector. Writing those returns as
$$r_{i,t+s}$$ gives

$$
q_{i,t}
=\sqrt{252}\,
\frac{\frac1{20}\sum_{s=1}^{20}r_{i,t+s}}
{\operatorname{sd}(r_{i,t+1},\ldots,r_{i,t+20})},
\qquad
y_{i,t}
=2\frac{\operatorname{rank}_{t,\,\mathrm{sector}}(q_{i,t})}
{K_{t,\,\mathrm{sector}}}-1.
$$

The target is a forward Sharpe-like rank, not the portfolio's Sharpe ratio. An
equally large but quieter gain receives a better raw outcome than a noisier
one. That preference makes a defensive learned portfolio plausible; it does
not by itself prove what caused the realized volatility difference in Section
3.

Let $$\mathbf X_{i,t}\in[-1,1]^{144}$$ contain the normalized predictors.
For walk-forward fold $$f$$, the mean squared training loss is

$$
\mathcal L_f(\beta_0,\boldsymbol\beta)
=
\frac{1}{n_f}\sum_{(i,t)\in\mathcal T_f}
\left(y_{i,t}-\beta_0-\mathbf X_{i,t}^{\top}
\boldsymbol\beta\right)^2.
$$

OLS learns the intercept, directions, and weights by minimizing that loss:

$$
(\widehat\beta^{\mathrm{OLS}}_{0,f},
\widehat{\boldsymbol\beta}^{\mathrm{OLS}}_f)
=\arg\min_{\beta_0,\boldsymbol\beta}
\mathcal L_f(\beta_0,\boldsymbol\beta).
$$

The fitted value becomes the stock score. A positive coefficient rewards a high
predictor rank; a negative coefficient reverses the preference. Missing
predictors use the latest known value or that date's sector average before the
common eligibility screens apply.

Every score then enters the inverse-volatility rule from the
[low-volatility article](/quant/2024/12/15/low-volatility-factor.html): the top
and bottom 75 stocks form the long and short books, and quieter stocks receive
larger weights subject to name and book caps.

## The learned model takes less risk, not more return

Table 2 compares the fixed score with the two learned rankings during
development. Fixed versus OLS is the headline comparison; OLS versus Ridge is
the cleaner penalty comparison.

<table class="research-table comparison-table period-metrics-table portfolio-card-table">
  <thead>
    <tr><th>Development metric</th><th>Fixed</th><th>OLS</th><th>Ridge <i>c</i> = 0.01</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Annualized return, gross</th><td data-label="Fixed">7.61%</td><td data-label="OLS">8.49%</td><td data-label="Ridge c = 0.01">8.82%</td></tr>
    <tr><th scope="row">Annualized return, net</th><td data-label="Fixed">6.92%</td><td data-label="OLS">7.03%</td><td data-label="Ridge c = 0.01">7.38%</td></tr>
    <tr><th scope="row">Annualized volatility</th><td data-label="Fixed">9.73%</td><td data-label="OLS">7.15%</td><td data-label="Ridge c = 0.01">7.36%</td></tr>
    <tr><th scope="row">Sharpe ratio</th><td data-label="Fixed">0.71</td><td data-label="OLS">0.98</td><td data-label="Ridge c = 0.01">1.00</td></tr>
    <tr><th scope="row">Maximum drawdown</th><td data-label="Fixed">−31.55%</td><td data-label="OLS">−18.77%</td><td data-label="Ridge c = 0.01">−19.03%</td></tr>
    <tr><th scope="row">Market beta</th><td data-label="Fixed">0.093</td><td data-label="OLS">0.084</td><td data-label="Ridge c = 0.01">0.091</td></tr>
    <tr><th scope="row">Two-way turnover per rebalance</th><td data-label="Fixed">78.78%</td><td data-label="OLS">167.67%</td><td data-label="Ridge c = 0.01">165.72%</td></tr>
    <tr><th scope="row">Annual trading cost</th><td data-label="Fixed">0.69 pp</td><td data-label="OLS">1.46 pp</td><td data-label="Ridge c = 0.01">1.44 pp</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Development-period portfolio results. Gross return is before the stated trading cost; risk statistics use returns after 5 bp per dollar traded.</p>

Gross return rises by 0.88 percentage points, but the extra trading cost
consumes 0.77 points of that gap, leaving only 0.11 points after costs. The
Sharpe improvement comes mainly from volatility falling from 9.7% to 7.2%,
alongside a shallower maximum drawdown.

The comparison does not isolate learned weights. OLS also receives more
predictors and uses different eligible rows because the fixed score requires
complete histories for its five factors. A matched six-input OLS model on the
same rows would separate estimated weights from additional information.

I cannot add that row from the retained outputs. They contain the fixed
five-factor scores and the full 144-predictor rankings, but not predictions from
a six-input OLS model on the matched rows. That is the first test to run next.

Figure 4 shows when the difference accumulated. The upper panel plots net
growth on a logarithmic scale; the lower panel shows drawdowns. The two learned
models follow smoother paths than the fixed score during development, while
Ridge remains close to OLS throughout.

<div class="research-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/performance-and-drawdowns" alt="Net growth on a logarithmic scale and drawdowns for fixed weights, OLS, and selected Ridge with development and later periods separated" version="14" %}
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Net growth of <span class="mathjax-ignore">$1</span> on a logarithmic scale (top) and drawdown (bottom) for the three ranking rules after 5 bp per dollar traded. The vertical rule starts the later period.</p>

The path supports a lower-risk learned portfolio, not a dramatic return gain.
The Sharpe-like target and the defensive holdings described later are
consistent with that result. The missing matched-input test prevents a stronger
causal claim.

## Ridge stabilises coefficients, not rankings

Overlapping predictors make OLS coefficients hard to interpret. Ridge
penalizes their squared size:

$$
(\widehat\beta^{(c)}_{0,f},\widehat{\boldsymbol\beta}^{(c)}_f)
=\arg\min_{\beta_0,\boldsymbol\beta}
\left\{\mathcal L_f(\beta_0,\boldsymbol\beta)
+c\lVert\boldsymbol\beta\rVert_2^2\right\}.
$$

The intercept remains unpenalized. Setting $$c=0$$ gives matched OLS—the same
predictors, target, universe, dates, eligible rows, and portfolio rule without
the Ridge penalty. Positive values encourage correlated predictors to share
influence. Shrinkage is guaranteed by the objective; better predictions are
not.

I tested $$c\in\{0,0.001,0.01,0.1\}$$ on the development period. I did not
predeclare a numerical acceptance threshold. The rule was to carry forward the
smallest penalty that reduced coefficient size and refit movement—the
change in the coefficient vector between fits—while leaving portfolio results
close to OLS.

<table class="research-table comparison-table alpha-selection-table portfolio-card-table">
  <thead>
    <tr><th>Estimator</th><th>Gross return</th><th>Net return</th><th>Net volatility</th><th>Net Sharpe</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">OLS, <i>c</i> = 0</th><td data-label="Gross return">8.49%</td><td data-label="Net return">7.03%</td><td data-label="Net volatility">7.15%</td><td data-label="Net Sharpe">0.983</td></tr>
    <tr><th scope="row">Ridge, <i>c</i> = 0.001</th><td data-label="Gross return">8.51%</td><td data-label="Net return">7.05%</td><td data-label="Net volatility">7.19%</td><td data-label="Net Sharpe">0.981</td></tr>
    <tr><th scope="row"><strong>Ridge, <i>c</i> = 0.01</strong></th><td data-label="Gross return"><strong>8.82%</strong></td><td data-label="Net return"><strong>7.38%</strong></td><td data-label="Net volatility"><strong>7.36%</strong></td><td data-label="Net Sharpe"><strong>1.003</strong></td></tr>
    <tr><th scope="row">Ridge, <i>c</i> = 0.1</th><td data-label="Gross return">9.26%</td><td data-label="Net return">7.83%</td><td data-label="Net volatility">7.92%</td><td data-label="Net Sharpe">0.989</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 3:</strong> Development-period results across the matched OLS–Ridge penalty grid. Volatility and Sharpe use net returns.</p>

No penalty improves Sharpe enough to identify a winner. I carry $$c=0.01$$
forward as a gentle compromise, not as an estimate of a unique optimum.

Figure 5 separates parameter stability from portfolio change. The left panel
counts names entering or leaving the 150-stock portfolio relative to OLS. The
right panel compares coefficient size and movement between refits.

<div class="research-figure alpha-sensitivity-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/alpha-sensitivity" alt="Average portfolio-membership changes and coefficient shrinkage relative to OLS across the Ridge penalty grid" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Portfolio-membership changes and coefficient shrinkage relative to matched OLS during development.</p>

At $$c=0.01$$, coefficient size and movement fall by roughly one third, yet
only about 14 of 150 selected names change on a typical rebalance. The full
ranking retains a 0.991 correlation with OLS. Ridge changes how predictors
divide the weight much more than it changes which stocks are selected.

Correlated predictors can exchange coefficients while preserving their combined
score. That is why Ridge can steady the coefficient vector without moving the
ranking much. Figure 6 follows the ten largest Ridge coefficients across refits.
Positive cells reward a high rank and negative cells favour a low rank; the 2022
and 2024 columns are later refits and did not enter penalty selection.

<div id="coefficient-heatmap" class="research-figure coefficient-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/top-coefficients" alt="Heatmap of the ten largest average absolute coefficients for the selected Ridge model across walk-forward refits" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 6:</strong> Signed coefficients for the selected Ridge model's ten largest mean absolute weights across walk-forward refits.</p>

Price relative to its moving average stays positive, while short-horizon MACD
and illiquidity stay negative. Several other coefficients weaken or change
sign. The broad predictor themes are easier to trust than any single
coefficient.

## Ridge does not improve performance before or after 2021

Table 3 shows the development result: Ridge moves Sharpe from 0.98 to 1.00,
without a decisive improvement across the penalty grid. Table 4 repeats the
comparison in the later period using $$c=0.01$$.

<table class="research-table comparison-table period-metrics-table portfolio-card-table">
  <thead>
    <tr><th>Later-period metric</th><th>Fixed</th><th>OLS</th><th>Ridge <i>c</i> = 0.01</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Annualized return, gross</th><td data-label="Fixed">7.85%</td><td data-label="OLS">8.84%</td><td data-label="Ridge c = 0.01">8.68%</td></tr>
    <tr><th scope="row">Annualized return, net</th><td data-label="Fixed">7.24%</td><td data-label="OLS">7.50%</td><td data-label="Ridge c = 0.01">7.37%</td></tr>
    <tr><th scope="row">Annualized volatility</th><td data-label="Fixed">11.33%</td><td data-label="OLS">8.64%</td><td data-label="Ridge c = 0.01">8.95%</td></tr>
    <tr><th scope="row">Sharpe ratio</th><td data-label="Fixed">0.64</td><td data-label="OLS">0.87</td><td data-label="Ridge c = 0.01">0.82</td></tr>
    <tr><th scope="row">Maximum drawdown</th><td data-label="Fixed">−10.98%</td><td data-label="OLS">−7.59%</td><td data-label="Ridge c = 0.01">−8.05%</td></tr>
    <tr><th scope="row">Market beta</th><td data-label="Fixed">0.036</td><td data-label="OLS">0.075</td><td data-label="Ridge c = 0.01">0.078</td></tr>
    <tr><th scope="row">Two-way turnover per rebalance</th><td data-label="Fixed">69.70%</td><td data-label="OLS">152.75%</td><td data-label="Ridge c = 0.01">149.61%</td></tr>
    <tr><th scope="row">Annual trading cost</th><td data-label="Fixed">0.61 pp</td><td data-label="OLS">1.34 pp</td><td data-label="Ridge c = 0.01">1.31 pp</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 4:</strong> Later-period portfolio results using the penalty selected through 2021. Risk statistics use net returns.</p>

Ridge trails OLS after 2021: net return is 0.13 percentage points lower,
volatility is 0.31 points higher, and Sharpe is 0.82 rather than 0.87. Turnover
and costs are only slightly lower. The gap counts against Ridge and is not a
reason to retune it after seeing the later period.

Information coefficient (IC) checks the whole ranking: the daily Spearman
correlation between the predicted order and the subsequently realized,
sector-ranked target. IC information ratio (IC IR) is mean daily IC divided by
its standard deviation.

<table class="research-table comparison-table ic-summary-table portfolio-card-table">
  <thead>
    <tr><th>Period and ranking</th><th>Mean daily IC</th><th>IC SD</th><th>IC IR</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Development · Fixed score</th><td data-label="Mean daily IC">0.0399</td><td data-label="IC standard deviation">0.1217</td><td data-label="IC IR">0.328</td></tr>
    <tr><th scope="row">Development · OLS</th><td data-label="Mean daily IC">0.0461</td><td data-label="IC standard deviation">0.0864</td><td data-label="IC IR">0.534</td></tr>
    <tr><th scope="row">Development · Ridge $c=0.01$</th><td data-label="Mean daily IC">0.0469</td><td data-label="IC standard deviation">0.0885</td><td data-label="IC IR">0.530</td></tr>
    <tr class="period-break"><th scope="row">2022–2026 · Fixed score</th><td data-label="Mean daily IC">0.0502</td><td data-label="IC standard deviation">0.1392</td><td data-label="IC IR">0.361</td></tr>
    <tr><th scope="row">2022–2026 · OLS</th><td data-label="Mean daily IC">0.0417</td><td data-label="IC standard deviation">0.1068</td><td data-label="IC IR">0.390</td></tr>
    <tr><th scope="row">2022–2026 · Ridge $c=0.01$</th><td data-label="Mean daily IC">0.0415</td><td data-label="IC standard deviation">0.1113</td><td data-label="IC IR">0.373</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 5:</strong> Mean and standard deviation of daily rank IC, with IC IR shown for the development and later periods.</p>

Mean IC is about 0.047 for both learned models during development, with no
useful IC IR improvement from Ridge. The later period is equally close. The
fixed score's later mean IC is higher, but its IC is more variable and its IC IR
remains below OLS. IC evaluates the whole cross-section; portfolio return
depends on the selected tails, position sizing, execution, and costs.

The penalty therefore does one useful job and no more. It steadies coefficients
without changing the economic ranking or producing better portfolio results.
Figure A1 shows the same conclusion in cumulative IC.

## The learned ranking leaves trading and exposure work open

The learned rankings roughly double trading. Figure 7 compares two-way turnover
per rebalance in the upper panel with annual cost under the 5 bp assumption
below; the columns separate development and the later period.

<div class="research-figure turnover-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/turnover-and-costs" alt="Turnover per rebalance and annual trading cost for fixed weights, OLS, and selected Ridge in development and later periods" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 7:</strong> Average two-way turnover per rebalance and annual trading cost for the fixed, OLS, and Ridge rankings.</p>

The fixed score trades about half as much as either learned ranking. Ridge
barely changes that burden: it saves 0.02 percentage points of annual cost in
development and 0.03 later. Smaller coefficients do not create a more stable
book.

Inverse-volatility sizing also leaves portfolio exposures uncontrolled. In the
selected Ridge portfolio, average net exposure rises from +30.0% in development
to +46.9% later because the short book does most of the moving. The rule
controls neither net exposure nor market beta directly. The
[next article](/quants/2026/08/29/portfolio-optimization.html) replaces that
stock-by-stock rule with joint sizing and explicit constraints.

The finished portfolio reveals what the model and allocation own together. I
define a **realized tilt** as the portfolio-weighted average of a predictor's
signed ranks: positive values mean the long book owns higher ranks than the
short book. Figure 8 plots the ten largest average absolute tilts by quarter.
Each panel includes zero but uses its own vertical scale, so the labelled
full-sample means—not apparent amplitude—support comparisons across panels.

<div class="research-figure exposure-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/portfolio-feature-tilts" alt="Quarterly portfolio-weighted predictor-rank tilts for the selected Ridge portfolio on independent zero-inclusive panel scales" version="12" %}
</div>

<p class="figure-caption"><strong>Figure 8:</strong> Quarterly paths of the ten largest average absolute realized predictor tilts; panels use independent zero-inclusive scales.</p>

The portfolio is mainly defensive and trend-following. The long book owns
quieter stocks, spends more time above its long-run moving average, and remains
closer to an earlier high. Several panels are variations on those two predictor
families rather than independent exposures.

That pattern connects the target to the realized result. The Sharpe-like target
rewards quieter future paths, and the learned portfolio owns defensive
predictor ranks; Table 2 then records lower realized volatility. This remains an
interpretation rather than attribution because inverse-volatility sizing can
strengthen the same tilt and correlated predictors can select similar stocks.

About two thirds of the predictor deck comes from price history or
price–volume interactions. The appendix describes the family-level test that
would show whether the apparent breadth adds independent information.

## Conclusion

The larger result is the move from fixed preferences to learned weights and
directions. During development, the learned model raises Sharpe from 0.71 to
0.98 mainly by taking less realized risk. The matched six-input test is the
next step before I credit learned weights alone.

Ridge is a guardrail, not a second source of edge. At $$c=0.01$$ it reduces
coefficient size and refit movement by roughly one third while preserving a
0.991 rank correlation with OLS. Its performance remains close to OLS during
development and trails it in the later period. I carry the gentle penalty
forward for stability, not because it improves the ranking.

Overlapping targets, common shocks within each date, and repeated development
work reduce the sample's independent information. Equal-date weighting,
non-overlapping training dates, and a genuinely new period remain useful
robustness tests.

The first next test is OLS restricted to the benchmark's six primitive inputs
on the same eligible rows. The retained outputs do not contain that comparison.
The
[portfolio-optimization article](/quants/2026/08/29/portfolio-optimization.html)
then keeps the Ridge ranking unchanged and moves to joint sizing, explicit exposure
constraints, and a trading penalty based on current holdings.

## Appendix: selected supporting details

### Fixed-score equations

Write the same-date attractive-side ranks as $$L$$ for low volatility, $$U$$
for upper-tail avoidance, $$M$$ for momentum, $$S$$ for low short positioning,
$$Z$$ for company size, and $$C$$ for return consistency. The defensive factor
is

$$
D_{i,t}=\frac{L_{i,t}+U_{i,t}}{2}.
$$

The benchmark then gives equal weight to the five final factors:

$$
F_{i,t}=\frac{D_{i,t}+M_{i,t}+S_{i,t}+Z_{i,t}+C_{i,t}}{5}.
$$

### Standalone factor returns

<table class="research-table comparison-table portfolio-card-table standalone-factor-table">
  <thead>
    <tr><th>Factor</th><th>Gross return</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Defensive</th><td data-label="Gross return">7.14%</td></tr>
    <tr><th scope="row">Momentum</th><td data-label="Gross return">3.44%</td></tr>
    <tr><th scope="row">Short positioning</th><td data-label="Gross return">1.95%</td></tr>
    <tr><th scope="row">Size</th><td data-label="Gross return">0.65%</td></tr>
    <tr><th scope="row">Return consistency</th><td data-label="Gross return">5.64%</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A1:</strong> Development-period annualized arithmetic gross return for each standalone factor portfolio, averaged across the three schedules.</p>

All five standalone portfolios have positive gross return during development.
Defensive leads, followed by return consistency; size is weakest. These runs
answer how each factor performs alone, not how much it adds after controlling
for the other four.

### Cumulative IC

Figure A1 accumulates daily rank IC from the first predictions in September
1998 to the last complete forward outcome on 28 April 2026. A rising path means
the model ordered future outcomes correctly on balance; the vertical rule
starts the later period.

<div class="research-figure ic-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/cumulative-ic" alt="Cumulative daily cross-sectional rank information coefficient for fixed weights, OLS, and selected Ridge with the 2022 boundary marked" version="12" %}
</div>

<p class="figure-caption"><strong>Figure A1:</strong> Cumulative daily rank IC for the fixed score, OLS, and selected Ridge rankings.</p>

The OLS and Ridge paths overlap through both periods. Table 5 carries the exact
comparison, so the figure belongs here as a timing check rather than a main
result.

### Matched tests

The first test holds information fixed: fit OLS to the benchmark's six primitive
inputs on the same eligible rows. Comparing that row with the fixed score would
test learned weights and directions without adding predictors.

A second test removes one predictor family at a time, both before and after
portfolio construction. It would show whether each family changes the ranking
or whether broad tails and inverse-volatility sizing pull related predictor
sets toward the same holdings.

[^schedules]: A staggered schedule runs the same full-capital portfolio from a different starting week. The [tranching article](/quants/2025/05/10/rebalancing-luck.html) introduced this timing check.
