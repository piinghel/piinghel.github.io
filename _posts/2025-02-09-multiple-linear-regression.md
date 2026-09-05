---
layout: post
title: "Ridge Stabilizes Coefficients, Barely Changes the Portfolio"
description: "Why a third less coefficient movement leaves rankings and portfolio performance almost unchanged."
date: 2025-02-09
last_modified_at: 2026-09-05
categories: ["Regression"]
article_label: Factor combination · Multiple linear and Ridge regression
permalink: /quants/2025/02/09/multiple-linear-regression.html
series_next: /quants/2026/08/29/portfolio-optimization.html
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/systematic-equity-research
---

<p class="article-summary">Ridge reduces coefficient size and movement by about a third here, yet barely changes the stock ranking or portfolio performance. Compared with my fixed factor score, both OLS and Ridge deliver similar net returns with lower volatility—and roughly twice the trading. I use Ridge for steadier estimation, but it does little to reduce that trading burden.</p>

Three versions of momentum can give the same idea three votes in a stock score.
Regression can learn how to combine them, but closely related predictors can
exchange coefficients without changing the score much. I wanted to know whether
stabilizing those coefficients would change the portfolio I actually hold.

The [low-volatility study](/quant/2024/12/15/low-volatility-factor.html) used one
signal and inverse-volatility sizing. Here the score becomes broader, while
the portfolio holds the top and bottom 75 stocks with inverse-volatility
weights and caps.

## A simple factor benchmark

Before fitting a model, I want a score whose weights I can inspect and whose
behaviour is easy to follow. I use five factors: defensive, momentum, short
positioning, size, and return consistency. They combine the low-risk idea from
the previous post with trend, positioning, and company-size information.

I convert the underlying inputs to percentile ranks, with higher values more
attractive, then average the five factor scores with a 20% weight each. The defensive score itself
averages low volatility and avoidance of unusually large up days, giving each
of those two inputs 10% of the final score. The weights stay the same at every
rebalance. This provides a simple, transparent alternative to estimating them.

The five factors have modest average rank correlations, from −0.08 to 0.28
during development (Figure A2). Their standalone returns differ substantially
(Table A2), so equal weighting is a useful starting rule whose strengths and
weaknesses I can compare with a fitted model. These choices came from earlier
research using the available history.

The size direction deserves scrutiny. Here it favours larger companies within
the Russell 1000, as a defensive tilt. The conventional
[small-minus-big factor](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html)
has the opposite direction. The larger-company preference earns only 0.65%
annualized gross return on its own in development. Its contribution to the
combined score needs a separate test; the appendix checks how much removing
or reversing it changes the ranking.

I compare three rankings:

- **Factor score:** the five-factor average above, labelled *Fixed weights* in
  the performance chart.
- **OLS:** ordinary least squares learns the signs and weights of 144 predictors.
- **Ridge:** the same regression with a penalty on coefficient size.

OLS versus the factor score measures the change to a broader fitted model:
144 predictors, estimated weights, and different data coverage. Ridge versus
OLS is the controlled regularization comparison: the inputs and eligible
stocks are the same, and only the coefficient penalty changes.

Models are fitted on expanding history to rank the next 20-day return relative
to its volatility, within each date and sector. A 21-day buffer separates
training outcomes from the next prediction block. All portfolios use
point-in-time Russell 1000 membership, rebalancing every three weeks,
and a five-basis-point charge per dollar traded.

Development ends in December 2021. January 2022–May 2026 is later evidence that
has already informed research choices elsewhere in this series. Tables average
statistics calculated separately for three starting-week schedules. The appendix
gives the fitting and return conventions.

## Portfolio results

Table 1 shows the development result. OLS earns about the same return after
costs as the fixed score, with lower volatility and a shallower drawdown.

<table class="research-table comparison-table period-metrics-table portfolio-card-table">
  <thead>
    <tr><th>Development metric</th><th>Fixed</th><th>OLS</th><th>Ridge <i>c</i> = 0.01</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Annualized return, gross</th><td>7.61%</td><td>8.49%</td><td>8.82%</td></tr>
    <tr><th scope="row">Annualized return, net</th><td>6.92%</td><td>7.03%</td><td>7.38%</td></tr>
    <tr><th scope="row">Annualized volatility</th><td>9.73%</td><td>7.15%</td><td>7.36%</td></tr>
    <tr><th scope="row">Sharpe ratio</th><td>0.71</td><td>0.98</td><td>1.00</td></tr>
    <tr><th scope="row">Maximum drawdown</th><td>−31.55%</td><td>−18.77%</td><td>−19.03%</td></tr>
    <tr><th scope="row">Market beta</th><td>0.093</td><td>0.084</td><td>0.091</td></tr>
    <tr><th scope="row">Two-way turnover per rebalance</th><td>78.78%</td><td>167.67%</td><td>165.72%</td></tr>
    <tr><th scope="row">Annual trading cost</th><td>0.69 pp</td><td>1.46 pp</td><td>1.44 pp</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Development-period portfolio results, September 1998–December 2021, averaged across three schedules. Returns are annualized arithmetic means. Gross return precedes the 5 bp trading charge; volatility, Sharpe, and drawdown use net returns.</p>

The extra gross return is 0.88 percentage points a year; extra trading consumes
0.77 points. Almost the entire return gain is spent before it reaches the
portfolio. Lower volatility accounts for most of the higher Sharpe.

Figure 1 shows the paths behind that comparison. The learned portfolios have
shallower drawdowns during development, while OLS and Ridge remain close
throughout. The vertical rule separates the later period.

<div class="research-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/performance-and-drawdowns" alt="Net growth on a logarithmic scale and drawdowns for fixed weights, OLS, and selected Ridge with development and later periods separated" version="15" %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Net growth of <span class="mathjax-ignore">$1</span> (top, log scale) and drawdown (bottom), after 5 bp per dollar traded. The 2022 boundary marks later, reused history.</p>

The model target rewards quieter future gains, and inverse-volatility sizing
also favours quieter stocks. Both can contribute to the lower portfolio risk.
Separating their contributions would require matched allocation tests.

## Coefficients and stock rankings

Ridge adds one term to the mean squared prediction error:

$$
\min_{\beta_0,\boldsymbol\beta}
\frac{1}{n}\sum_{k=1}^{n}
\left(y_k-\beta_0-\mathbf X_k^\top\boldsymbol\beta\right)^2
+c\lVert\boldsymbol\beta\rVert_2^2.
$$

There are $n$ stock-date observations in the training window. For row $k$, $y_k$ is the
target rank, and $\mathbf X_k$ contains the predictor ranks. The intercept
$\beta_0$ is unpenalized. Setting $c=0$ gives OLS; a larger $c$ makes large
coefficients more expensive. The fitted value becomes the stock score.

Figure 2 compares the change in selected stocks with the change in coefficients.
At $c=0.01$, coefficient size and movement between refits fall by roughly one
third. About 14 of 150 selected names differ from OLS, and the full ranking
has a 0.991 correlation with it.

<div class="research-figure alpha-sensitivity-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/alpha-sensitivity" alt="Average portfolio-membership changes and coefficient shrinkage relative to OLS across the Ridge penalty grid" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Development-period membership changes relative to OLS (left) and reductions in coefficient norm and movement between refits (right).</p>

A model can put less weight on one momentum horizon and more on its neighbour
while giving nearly the same stocks high scores. Selection then discards most
score differences that leave a stock on the same side of the rank cutoff.
These two steps explain how large coefficient changes can lead to a small
portfolio change. Identifying which predictors substitute for one another
would require a closer comparison of the fitted coefficients.

Table 2 makes the performance consequence visible. The penalties change return
and volatility together, leaving Sharpe tightly grouped.

<table class="research-table comparison-table alpha-selection-table portfolio-card-table">
  <thead>
    <tr><th>Estimator</th><th>Gross return</th><th>Net return</th><th>Net volatility</th><th>Net Sharpe</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">OLS, <i>c</i> = 0</th><td>8.49%</td><td>7.03%</td><td>7.15%</td><td>0.983</td></tr>
    <tr><th scope="row">Ridge, <i>c</i> = 0.001</th><td>8.51%</td><td>7.05%</td><td>7.19%</td><td>0.981</td></tr>
    <tr><th scope="row"><strong>Ridge, <i>c</i> = 0.01</strong></th><td><strong>8.82%</strong></td><td><strong>7.38%</strong></td><td><strong>7.36%</strong></td><td><strong>1.003</strong></td></tr>
    <tr><th scope="row">Ridge, <i>c</i> = 0.1</th><td>9.26%</td><td>7.83%</td><td>7.92%</td><td>0.989</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Development-period results across the matched OLS–Ridge penalty grid. Volatility and Sharpe use net returns.</p>

I chose the smallest tested penalty that reduced coefficient size and refit
movement while keeping the portfolio close to OLS. That was a qualitative
development choice, without a predeclared numerical acceptance threshold.
I keep $c=0.01$ for that reason; the grid gives little reason to choose it for
higher expected return.

## Results after 2021

Table 3 repeats the comparison after 2021. Both learned portfolios remain less
volatile than the fixed score. Ridge slightly trails OLS in net return and
Sharpe. There is little here to justify Ridge on performance alone.

<table class="research-table comparison-table period-metrics-table portfolio-card-table">
  <thead>
    <tr><th>Later-period metric</th><th>Fixed</th><th>OLS</th><th>Ridge <i>c</i> = 0.01</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Annualized return, gross</th><td>7.85%</td><td>8.84%</td><td>8.68%</td></tr>
    <tr><th scope="row">Annualized return, net</th><td>7.24%</td><td>7.50%</td><td>7.37%</td></tr>
    <tr><th scope="row">Annualized volatility</th><td>11.33%</td><td>8.64%</td><td>8.95%</td></tr>
    <tr><th scope="row">Sharpe ratio</th><td>0.64</td><td>0.87</td><td>0.82</td></tr>
    <tr><th scope="row">Maximum drawdown</th><td>−10.98%</td><td>−7.59%</td><td>−8.05%</td></tr>
    <tr><th scope="row">Market beta</th><td>0.036</td><td>0.075</td><td>0.078</td></tr>
    <tr><th scope="row">Two-way turnover per rebalance</th><td>69.70%</td><td>152.75%</td><td>149.61%</td></tr>
    <tr><th scope="row">Annual trading cost</th><td>0.61 pp</td><td>1.34 pp</td><td>1.31 pp</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 3:</strong> January 2022–May 2026 results, averaged across three schedules. Returns are annualized arithmetic means; risk statistics use net returns. This later history was revisited during research.</p>

The prediction diagnostics tell a similar story. Mean daily rank IC is about
0.047 for both learned models in development and about 0.042 later
(Table A4). IC measures ordering across the whole eligible cross-section;
portfolio returns also depend on the selected tails, weights, execution, and
costs. I therefore check the implemented portfolio alongside IC.

## Trading costs

Ridge barely reduces the learned portfolio's trading burden. Relative to OLS,
annual cost falls by only 0.02 percentage points in development and 0.03 later
(Tables 1 and 3). The cost of maintaining the holdings remains almost unchanged.

The allocation also changes the exposures behind the ranking. Average net
stock exposure for Ridge rises from 30% in development to 47% later, largely
through changes in the short book. Its largest predictor tilts are defensive
and trend-related (Figure A4). P&L attribution would be needed to connect those
holdings to the sources of return.

I use the gentle Ridge penalty because it steadies estimation without changing
the portfolio much. The [optimizer
study](/quants/2026/08/29/portfolio-optimization.html) uses the same predictions
and asks when a new position is worth replacing one already held.

For the next model comparison, I would first test the four-factor score with
size removed. I would then fit OLS and Ridge to exactly the same underlying
inputs and eligible rows. That would give the learned weights a clearer
benchmark. Value or profitability would broaden the economic rationale, but
would also require point-in-time fundamental data beyond this study's inputs.

## Appendix

### Research conventions

<table class="research-table settings-table">
  <thead>
    <tr><th>Component</th><th>Shared setting</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Universe</th><td>Point-in-time Russell 1000 membership and daily U.S. equity data, 3 January 1995–27 May 2026</td></tr>
    <tr><th scope="row">Eligibility</th><td>Price of at least five dollars; announced merger targets and duplicate share classes excluded</td></tr>
    <tr><th scope="row">Walk-forward fit</th><td>900 initial training dates; 21-day buffer; 600-date prediction blocks; 12 expanding refits</td></tr>
    <tr><th scope="row">Target</th><td>Within-date, within-sector rank of forward 20-day return divided by forward 20-day volatility</td></tr>
    <tr><th scope="row">Portfolio rule</th><td>Top and bottom 75 stocks; inverse-volatility sizing with stock and book caps</td></tr>
    <tr><th scope="row">Execution and cost</th><td>Three-week rebalancing; 5 bp per dollar traded</td></tr>
    <tr><th scope="row">Evaluation</th><td>Development through 2021; later period from January 2022</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A1:</strong> Research conventions. Walk-forward fitting applies to OLS and Ridge; the target evaluates all three rankings. The fixed score and learned models have different predictor-coverage requirements.</p>

The 900-date initial window expands across 12 refits. Within each window,
three date-thinned training samples produce three fitted models whose
predictions are averaged. Figure A1 shows the timing: the buffer keeps forward
training outcomes outside the next prediction block. Overlapping targets and
common market shocks still make stock-date rows dependent.

<div class="research-figure walk-forward-figure">
  {%- include walk-forward-figure.html -%}
</div>

<p class="figure-caption"><strong>Figure A1:</strong> Schematic of expanding training history, a 21-day buffer, and 600-date prediction blocks.</p>

### Predictor and target ranks

The raw predictors use different units. For raw value
$$\widetilde X_{i,j,t}$$, let $$R_t(\widetilde X_{i,j,t})$$ be its dense
rank—a rank in which ties share a value—and let $$K_{j,t}$$ be the largest rank
on date $$t$$. I map predictor $$j$$ to

$$
X_{i,j,t}
=2\frac{R_t(\widetilde X_{i,j,t})}{K_{j,t}}-1.
$$

Every input now lies between $$-1+2/K_{j,t}$$ and 1; its mean and variance depend
on that date's rank distribution. Ranking limits the influence of raw
outliers and prevents dollars from appearing more important than percentages
because their numerical scale is larger. The model learns relative order
while discarding the distance between raw signal values.

The 144 inputs cover trend, distance from moving averages and earlier highs,
volatility, size, market sensitivity, trading activity, liquidity, and lagged
short positioning. Missing values use the latest known observation or that
date's sector average before the common eligibility screens apply.

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

The target ranks individual stocks by a forward Sharpe-like outcome. An
equally large but quieter gain receives a better raw outcome than a noisier
one. That preference helps explain why the learned ranking could be defensive.

### The fixed factors and their overlap

The defensive factor combines low volatility and upper-tail avoidance: it
penalizes stocks with unusually large up days.
Momentum skips the latest month. Return consistency favours fewer down days.
The remaining factors favour lower short positioning and larger companies.
Each measure becomes a same-date attractive-side percentile rank before
combination.

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

Figure A2 orders the ten factor pairs by their average rank correlation during
development. Defensive and return consistency overlap most, at 0.28; defensive
and short positioning have a slightly negative correlation. Individual periods
can show stronger overlap than these averages.

<div class="research-figure factor-correlation-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/factor-correlation" alt="Ten factor pairs ordered by mean Spearman correlation, from defensive and return consistency at 0.28 to defensive and short positioning at minus 0.08" version="3" %}
</div>

<p class="figure-caption"><strong>Figure A2:</strong> Mean same-date Spearman rank correlations between the five final factors, 21 May 1997–31 December 2021. Each pair is shown once. <a href="/assets/multiple-linear-regression/factor-correlations.csv">Data</a>.</p>

Table A2 tests each factor alone under the shared portfolio rule. Defensive
has the highest gross return and size the lowest. Measuring the incremental
contribution of each factor would require adding or removing it from the combination.

<table class="research-table comparison-table portfolio-card-table standalone-factor-table">
  <thead>
    <tr><th>Factor</th><th>Gross return</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Defensive</th><td>7.14%</td></tr>
    <tr><th scope="row">Momentum</th><td>3.44%</td></tr>
    <tr><th scope="row">Short positioning</th><td>1.95%</td></tr>
    <tr><th scope="row">Larger-company preference</th><td>0.65%</td></tr>
    <tr><th scope="row">Return consistency</th><td>5.64%</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A2:</strong> Development-period annualized arithmetic gross return for each standalone factor portfolio, averaged across the three schedules.</p>

### Sensitivity to the size choice

Using the same daily factor inputs, I recomputed the score with size removed
and with its direction reversed. Removing size gives each remaining factor
25%; reversing it keeps all five weights at 20%. Table A3 compares the resulting
rankings and the top/bottom 75 candidates on each date.

<table class="research-table comparison-table">
  <thead><tr><th>Size choice</th><th>Rank correlation with original</th><th>Candidates replaced, out of 150</th></tr></thead>
  <tbody>
    <tr><th scope="row">Remove size</th><td>0.960</td><td>32.8</td></tr>
    <tr><th scope="row">Prefer smaller companies</th><td>0.817</td><td>73.3</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A3:</strong> Means across 5,858 development dates, 22 September 1998–31 December 2021, using the common factor-score rows. Candidates are the highest and lowest 75 scores, before position sizing; ties use a stable security identifier. <a href="/assets/multiple-linear-regression/benchmark-size-sensitivity.csv">Data</a> · <a href="https://github.com/piinghel/piinghel.github.io/blob/main/scripts/check_benchmark_size.py">Calculation</a>.</p>

The size choice has a large effect on selection. Reversing it changes almost
half the candidates. Choosing between these alternatives on performance would
require replaying their positions and costs. For that comparison, I favour
starting with size removed: it makes the role of the remaining defensive,
trend, and positioning signals easier to assess.

### Coefficients across refits

Figure A3 follows the ten largest mean absolute Ridge coefficients. Positive
values reward a high predictor rank. Price relative to its moving average
stays positive; short-horizon MACD and illiquidity stay negative. Several other
coefficients weaken or change sign. Each is conditional on the other inputs,
including close substitutes. Penalty selection uses the refits through 2021.

<div class="research-figure coefficient-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/top-coefficients" alt="Heatmap of the ten largest average absolute coefficients for the selected Ridge model across walk-forward refits" version="11" %}
</div>

<p class="figure-caption"><strong>Figure A3:</strong> Signed coefficients for the selected Ridge model across refits; the ten predictors are selected by mean absolute weight.</p>

### Holdings tilts

Figure A4 plots the ten largest average absolute predictor tilts,
$T_{j,t}=\sum_i w_{i,t}X_{i,j,t}$, where $w$ is the signed portfolio weight
and $X$ the predictor rank. This sum combines selection and book size. With
unequal long and short gross exposure, the sum also reflects the difference
in book sizes. Comparing the average stock on each side would require
normalizing each book separately.

<div class="research-figure exposure-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/portfolio-feature-tilts" alt="Quarterly portfolio-weighted predictor-rank tilts for the selected Ridge portfolio on independent zero-inclusive panel scales" version="12" %}
</div>

<p class="figure-caption"><strong>Figure A4:</strong> Quarterly weighted predictor ranks. Panels have independent zero-inclusive scales; labelled means support comparisons of magnitude.</p>

The largest tilts favour low volatility and persistent trends. Several inputs
measure variants of the same characteristic; counting them separately would
overstate the breadth of the portfolio. Attribution and matched allocation
comparisons would be needed to distinguish the ranking's contribution from
the tilt introduced by inverse-volatility sizing.

### Rank IC

Table A4 reports same-date Spearman correlation between the score and target.
The IC information ratio is mean daily IC divided by its standard deviation.
Ridge barely changes either the mean or variability of IC relative to OLS.

<table class="research-table comparison-table ic-summary-table portfolio-card-table">
  <thead>
    <tr><th>Period and ranking</th><th>Mean daily IC</th><th>IC SD</th><th>IC IR</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Development · Fixed score</th><td>0.0399</td><td>0.1217</td><td>0.328</td></tr>
    <tr><th scope="row">Development · OLS</th><td>0.0461</td><td>0.0864</td><td>0.534</td></tr>
    <tr><th scope="row">Development · Ridge $c=0.01$</th><td>0.0469</td><td>0.0885</td><td>0.530</td></tr>
    <tr class="period-break"><th scope="row">2022–2026 · Fixed score</th><td>0.0502</td><td>0.1392</td><td>0.361</td></tr>
    <tr><th scope="row">2022–2026 · OLS</th><td>0.0417</td><td>0.1068</td><td>0.390</td></tr>
    <tr><th scope="row">2022–2026 · Ridge $c=0.01$</th><td>0.0415</td><td>0.1113</td><td>0.373</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A4:</strong> Mean and standard deviation of daily rank IC, with their unannualized ratio. Adjacent observations share overlapping forward outcomes.</p>

Figure A5 accumulates daily IC from September 1998 to the last complete
forward outcome on 28 April 2026. The near-overlapping OLS and Ridge paths show
that their similar averages are accompanied by similar timing.

<div class="research-figure ic-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/cumulative-ic" alt="Cumulative daily cross-sectional rank information coefficient for fixed weights, OLS, and selected Ridge with the 2022 boundary marked" version="13" %}
</div>

<p class="figure-caption"><strong>Figure A5:</strong> Running sum of daily rank IC. The vertical rule marks January 2022.</p>

### Source availability

The standalone factor results and correlations can be reproduced. Reproducing the OLS–Ridge comparison
requires the original return and coefficient files, which are missing.
Its tables and figures remain as originally reported.
