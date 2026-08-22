---
layout: post
title: "Multiple Linear Regression"
date: 2025-02-09
last_modified_at: 2026-08-22
categories: [Quants]
article_mark: /assets/brand/multiple-linear-regression-mark.svg
article_label: Factor combination · Multiple linear regression
permalink: /quants/2025/02/09/multiple-linear-regression.html
---

A stock-selection model rarely begins with one clean predictor. It begins with
many measures of momentum, risk, liquidity, size, and trading activity, often
calculated over several horizons. The practical question is how to combine them
into one ranking.

I compare three answers. The first is a transparent fixed-weight score. The
second uses ordinary multiple linear regression to learn a weight for each of
144 predictors. The third uses Ridge, the same regression with an L2 penalty.
The core idea is the learned linear combination; Ridge is one implementation
choice whose effect needs to be tested rather than assumed.

The main result is deliberately mixed. Over the full common-date record, OLS
and Ridge both produce stronger and less variable stock rankings than the
fixed-weight reference.
Increasing the Ridge penalty shrinks the coefficients, reduces their movement
between refits, and eventually changes the ranking. The penalty selected on
pre-2021 IC, however, does not beat OLS on risk-adjusted portfolio performance
from 2021 onward. Regularization changes the model, but this test does not show
that it improves the portfolio.

## 1. Why combine multiple predictors?

Many columns in the predictor library are related. A 21-session volatility rank
and a 63-session downside-volatility rank, for example, are different views of
the same defensive idea. Giving every column an equal weight would let themes
with more lookbacks dominate by construction. Choosing a single horizon would
discard potentially useful differences and make the result depend on an
arbitrary choice.

The research question is therefore:

> Can multiple linear regression combine many stock predictors into a more
> useful out-of-sample ranking than a simple fixed-weight factor score, and what
> does an L2 penalty change in a matched comparison with OLS?

The regression receives 144 separately ranked predictors from ten broad
families. It does not receive one pre-aggregated score per family.

| Predictor family | Count | Examples |
| --- | ---: | --- |
| Return history | 24 | Recent and lagged returns, momentum, historical Sharpe |
| Price risk | 19 | Total, range-based, downside, and upside volatility |
| Technical state | 18 | RSI, MACD, Bollinger position, moving-average state |
| Price path | 20 | Distance from recent highs and lows, prior-high comparisons |
| Return consistency | 7 | Frequency of negative-return sessions |
| Size | 14 | Market capitalization, changes, stability, and extrema |
| Market correlation | 4 | Correlation with the broad index over several horizons |
| Trading volume | 21 | Turnover, volume changes, variability, and extrema |
| Price and volume | 4 | Illiquidity and return-turnover correlation |
| Short interest | 13 | Publication-lagged changes, moments, and volume ratios |
| **Total** | **144** | |
{: .predictor-library-table }

The panel uses point-in-time Russell 1000 membership. The traded portfolio also
removes stocks below $5, announced merger targets, and duplicate share classes.
Short interest is delayed by 21 sessions before it enters a predictor. Across
the regression's prediction dates, 841 to 1,023 stocks have the required inputs
and pass the trading screens, with a median of 973.

The deck began with 191 candidates. I removed invalid or persistently redundant
variants, then used group-level sensitivity tests to decide several
volume-related changes. Those choices used the historical record. The
walk-forward predictions are out of sample conditional on a predictor library
that was itself developed in sample.

## 2. How the reference factors are built and perform alone

The reference score begins with six familiar components. Each is oriented so a
higher rank is more attractive, then ranked across current index members on the
same date. The two defensive components are averaged first. That defensive
theme and the other four themes receive 20% each, leaving each defensive
component with a 10% final weight.

| Component | Intuition and construction | Attractive direction | Final weight |
| --- | --- | --- | ---: |
| Low volatility | Risk tends to persist; mean annualized volatility over 21, 63, and 126 sessions | Lower | 10% |
| Upper-tail avoidance | Prefer a path that relies less on isolated gains; third-largest daily return over 21 sessions | Lower | 10% |
| Momentum | Trends may persist; sum of 3-, 6-, 9-, and 12-month returns, skipping the latest month | Higher | 20% |
| Low short interest | Less adverse positioning; delayed short interest relative to 63-session mean volume | Lower | 20% |
| Large capitalization | Tilt toward mature, investable firms; log market capitalization | Higher | 20% |
| Fewer loss days | Prefer a smoother long-run path; share of negative sessions over 756 sessions | Lower | 20% |
{: .benchmark-component-table }

For stock $i$ on date $t$, the fixed score is

$$
s^{\mathrm{fixed}}_{i,t}=\frac{1}{5}\sum_{k=1}^{5}z_{i,t,k},
$$

where $z_{i,t,k}$ is one of the five theme ranks. Its absolute scale does not
matter for selection; its ordering does. Once chosen, the signs and weights do
not change.

Before asking a model to combine these ideas, I reran each component on one
common sample. Only the score changes: every run selects 75 longs and 75 shorts,
uses the same volatility-scaled allocation, next-close execution, three offset
calendars, and 5 basis points per dollar traded. The shared signal sample runs
from May 1997 to May 2026.

All six standalone net returns are positive. They range from 1.66% a year for
large capitalization to 6.38% for low volatility; net Sharpe ranges from 0.23
to 0.62. The result is encouraging but economically uneven. The large-cap
portfolio has a 51.6% maximum drawdown. Upper-tail avoidance trades about 30
times equity per year and gives up 1.51 percentage points of annual return under
the stated cost assumption. Positive does not mean equally strong or equally
implementable.

## 3. Why the dependence structure matters

The two correlation panels in Figure 1 measure different things. Signal
correlation compares same-date cross-sectional ranks before stocks are selected.
Fourteen of the fifteen pairs have an absolute correlation no greater than
0.32; the exception is the two defensive components at 0.75. This says most of
the input rankings are differentiated.

Realized-return correlation compares the daily net returns of the standalone
portfolios. It is calculated separately for each executable calendar and then
averaged. The higher realized correlations are consistent with shared holdings
and risk exposures: the defensive pair reaches 0.85, low volatility versus
fewer loss days reaches 0.54, and the median pair is 0.30. Distinct rankings do
not guarantee equally distinct portfolios, but this diagnostic does not
attribute the overlap to one channel.

<div class="research-figure component-evidence-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/benchmark-component-evidence-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/benchmark-component-evidence-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/benchmark-component-evidence.svg">
    <img src="/assets/multiple-linear-regression/benchmark-component-evidence.png" alt="Positive standalone annualized net returns, same-date signal rank correlations, and realized net portfolio-return correlations for the six reference components" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Standalone annualized
arithmetic net return and two distinct dependence measures.</p>

Useful but imperfect individual factors provide a reason to combine them, not
independent validation. The set and its horizons were selected with knowledge
of the full history. Definitions overlap, availability differs before the
common start, and positive standalone performance does not show that a factor
adds value after controlling for the others. That stronger claim needs a
spanning, residualized, or leave-one-factor-out test.

The fixed score is also not neutral. Its theme definitions and equal weights
are subjective, and another reasonable reference could change the comparison.
It remains useful because the rule is simple, fixed, and inspectable.

## 4. Fixed weights versus unpenalized regression

The regression target is the stock's Sharpe ratio over the following 20 market
sessions,

$$
\mathrm{SR}^{(20)}_{i,t}
=\sqrt{252}\,
\frac{\overline r_{i,t+1:t+20}}
{\sigma\!\left(r_{i,t+1:t+20}\right)}.
$$

I use forward Sharpe rather than forward return because the desired ranking
should reward a return that is persistent over the month more than an equally
large return produced by a few volatile days. It is still only a ranking
target; it does not directly optimize the later portfolio Sharpe.

Predictors and targets are both mapped to $[-1,1]$, but over different groups.
Each predictor is ranked across all current index members on its date. This puts
unlike units on one scale, limits outliers, and retains cross-sector
differences. Missing inputs are first carried forward within a stock where
possible, then filled with that date's sector average.

The forward-Sharpe target is ranked within each date and sector. The model is
asked which stocks will do better than their sector peers, so sector-level
outcomes and their magnitude do not determine the label. This does not make the
portfolio sector neutral: selection remains global and there is no sector
constraint.

<div class="research-figure normalization-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/normalization-flow-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/normalization-flow-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/normalization-flow.svg">
    <img src="/assets/multiple-linear-regression/normalization-flow.png" alt="Predictors ranked across all stocks on each date and the forward Sharpe target ranked within each date and sector" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Predictor ranks retain
cross-sector information; target ranks define success relative to sector peers.</p>

With the ranked target and predictor matrix, the unpenalized model solves

$$
(\widehat\beta_{0,t},\widehat\beta_t)
=\arg\min_{\beta_0,\beta}
\sum_{(i,s)\in\mathcal T_t}
\left(y^{(20)}_{i,s}-\beta_0-x_{i,s}^{\top}\beta\right)^2.
$$

This is ordinary least squares: one intercept and one coefficient for each of
the 144 predictors. The predicted score is their weighted sum.

At each refit, the model uses only earlier observations, leaves out the forward
target horizon, and scores the next unseen block. The training history then
expands. I average three fits trained on complementary date subsamples because
adjacent 20-session targets overlap heavily. The exact initial window and block
length determine when coefficients update, but the core design is simply past
data, a leakage-preventing gap, and an unseen next block.

The research history begins in January 1995. The first years establish the
initial training sample, so out-of-sample predictions begin in 1998. All
penalty decisions use only predictions through 2020; the later evaluation begins
in January 2021.

<div class="research-figure walk-forward-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/walk-forward-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/walk-forward-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/walk-forward.svg">
    <img src="/assets/multiple-linear-regression/walk-forward.png" alt="Walk-forward regression trained on past observations, separated from the next unseen test block by the target horizon" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Each fit uses past data,
leaves out the target horizon, and predicts the next unseen block.</p>

The fixed score and OLS are not a pure estimator comparison. The fixed score
uses six components and has a median of 915 tradable scores per date; OLS uses
144 predictors and has a median of 973. The IC comparison below uses common
stock-dates, but each portfolio trades its own available cross-section. This
comparison asks whether the complete learned score is useful. Only the matched
OLS-versus-Ridge runs isolate the penalty.

## 5. What Ridge regularization changes

Ridge adds a squared-coefficient penalty to the same regression:

$$
(\widehat\beta_{0,t},\widehat\beta_t)
=\arg\min_{\beta_0,\beta}
\sum_{(i,s)\in\mathcal T_t}
\left(y^{(20)}_{i,s}-\beta_0-x_{i,s}^{\top}\beta\right)^2
+\alpha_t\lVert\beta\rVert_2^2.
$$

Setting $\alpha_t=0$ gives the exact unpenalized least-squares objective.
Positive values discourage large individual coefficients and can change how
correlated predictors share weight. Shrinkage is guaranteed; better predictions
or portfolios are not.

The implementation uses a summed squared-error loss. A fixed raw $\alpha$
therefore becomes weaker as the expanding sample grows. The training rows in
this study rise from about 293,000 to 2.46 million per ensemble member. With the
old raw $\alpha=1$, $\alpha/n$ falls from $3.4\times10^{-6}$ to
$4.1\times10^{-7}$, and its predictions are numerically indistinguishable from
OLS.

To keep the effective strength comparable through time, I set

$$
\alpha_t=c\,n_t.
$$

Dividing the objective by $n_t$ then gives
$\mathrm{MSE}_t+c\lVert\beta\rVert_2^2$. The grid is
$c\in\{0,0.001,0.01,0.1\}$, ranging from OLS through a penalty strong enough to
change the ranking. Every run holds the 144 predictors, target, rows,
walk-forward dates, portfolio rules, execution, and costs constant.

## 6. Alpha sensitivity, predictions, and coefficients

I use mean daily walk-forward rank IC through December 2020 to choose the
penalty. No candidate portfolio result is used in that choice. The mean IC rises
monotonically from 0.04453 for OLS to 0.04598 for $c=0.1$, so the rule selects
$c=0.1$. The absolute gain is 0.00145, about 3.3% of the OLS level: measurable,
but not a transformation of signal strength. Because the best value is at the
edge of the grid, this test selects among the four candidates; it does not show
that 0.1 is optimal.

The middle panel of Figure 4 asks whether shrinkage changes the actual ranking.
At $c=0.001$, predictions retain a 0.9996 rank correlation with OLS; the scores
are effectively the same. At $c=0.01$ the correlation is 0.991, and at the
selected $c=0.1$ it falls to 0.934. Only the stronger penalties materially
change which stocks rank above others.

The last panel asks what happens inside the fit. Relative to OLS, $c=0.1$ cuts
the average coefficient L2 norm from 0.1687 to 0.0522 and the mean absolute
change at a refit from 0.00337 to 0.00095. Adjacent coefficient-vector
correlation rises only slightly, from 0.941 to 0.952. Ridge clearly makes the
coefficients smaller and their absolute movements gentler, but high correlation
between adjacent OLS fits means instability was not catastrophic to begin with.

Signs and concentration move in the same direction, but modestly. Adjacent
sign agreement rises from 90.0% for OLS to 91.7% for $c=0.1$, and the share of
predictors keeping one sign through all 12 folds rises from 47.9% to 58.3%.
Meanwhile, the top 20 absolute coefficients' share of total absolute coefficient
mass falls from 41.3% to 36.6%. The stronger penalty therefore spreads weight a
little more evenly and makes directions somewhat more persistent; it does not
produce a perfectly stable or diffuse model.

<div class="research-figure alpha-sensitivity-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/alpha-sensitivity-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/alpha-sensitivity-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/alpha-sensitivity.svg">
    <img src="/assets/multiple-linear-regression/alpha-sensitivity.png" alt="Changes in development and later-period mean rank IC relative to OLS, prediction rank correlation with OLS, and coefficient shrinkage across four sample-scaled penalty strengths" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 4:</strong> The penalty strengthens
from left to right. Development IC chooses the penalty; later IC and the
full-record prediction and coefficient diagnostics are post-selection checks.</p>

These coefficients are conditional associations, not causal effects. Correlated
predictors can divide one underlying signal in different ways, so a smaller or
more persistent coefficient is not automatically more economically meaningful.
The coefficient vector is also different from the portfolio's market beta:
the former maps predictors to scores, while the latter measures the realized
portfolio's sensitivity to broad-market returns.

## 7. Locked later-period evaluation

After selecting $c=0.1$ on pre-2021 IC, I apply the locked rule from January
2021 through May 2026. Portfolio returns run through 27 May 2026; IC stops on 28
April because the full 20-session forward target must be observed. The period is
useful, but it is not a genuinely untouched holdout. The factor definitions,
predictor deck, target comparisons, portfolio rules, and earlier presentation
had already been influenced by post-2020 data. The alpha exercise is also a
post-selection reconstruction rather than a pre-registered experiment. I
therefore call this a pseudo-holdout or later-period check.

Among the four learned models, the selected penalty retains the highest
later-period IC: 0.05082 versus 0.04988 for OLS. The difference is only 0.00094.
The fixed score is slightly higher still at 0.05193 on common stock-dates, so
the later ranking evidence does not preserve the learned models' full-period
lead. More importantly, the Ridge-versus-OLS ranking gain does not become a
portfolio gain. OLS has a later-period Sharpe of 1.09,
while the selected Ridge model has 0.98, higher volatility, and a deeper
drawdown. Ridge adds only 0.10 percentage points of annual net return while
adding 1.10 points of annualized volatility; that is not an economically useful
trade in this period. The smallest positive penalty happens to have the highest later
Sharpe at 1.12, but it was not selected and should not be promoted after looking
at the later results.

<table class="research-table comparison-table alpha-grid-table">
  <thead>
    <tr>
      <th>2021–2026</th>
      <th>Fixed weights</th>
      <th>OLS</th>
      <th>Ridge c = 0.001</th>
      <th>Ridge c = 0.01</th>
      <th>Ridge c = 0.1</th>
    </tr>
  </thead>
  <tbody>
    <tr><th scope="row">Mean daily IC</th><td data-label="Fixed weights">0.0519</td><td data-label="OLS">0.0499</td><td data-label="Ridge c = 0.001">0.0500</td><td data-label="Ridge c = 0.01">0.0503</td><td data-label="Ridge c = 0.1">0.0508</td></tr>
    <tr><th scope="row">Net return</th><td data-label="Fixed weights">8.21%</td><td data-label="OLS">9.83%</td><td data-label="Ridge c = 0.001">10.09%</td><td data-label="Ridge c = 0.01">9.72%</td><td data-label="Ridge c = 0.1">9.92%</td></tr>
    <tr><th scope="row">Volatility</th><td data-label="Fixed weights">11.33%</td><td data-label="OLS">9.00%</td><td data-label="Ridge c = 0.001">9.05%</td><td data-label="Ridge c = 0.01">9.26%</td><td data-label="Ridge c = 0.1">10.09%</td></tr>
    <tr><th scope="row">Sharpe</th><td data-label="Fixed weights">0.72</td><td data-label="OLS">1.09</td><td data-label="Ridge c = 0.001">1.12</td><td data-label="Ridge c = 0.01">1.05</td><td data-label="Ridge c = 0.1">0.98</td></tr>
    <tr><th scope="row">Maximum drawdown</th><td data-label="Fixed weights">−10.78%</td><td data-label="OLS">−7.59%</td><td data-label="Ridge c = 0.001">−7.65%</td><td data-label="Ridge c = 0.01">−8.05%</td><td data-label="Ridge c = 0.1">−9.12%</td></tr>
    <tr><th scope="row">Market beta</th><td data-label="Fixed weights">0.07</td><td data-label="OLS">0.10</td><td data-label="Ridge c = 0.001">0.10</td><td data-label="Ridge c = 0.01">0.11</td><td data-label="Ridge c = 0.1">0.11</td></tr>
    <tr><th scope="row">Turnover per sleeve rebalance</th><td data-label="Fixed weights">71.5%</td><td data-label="OLS">152.4%</td><td data-label="Ridge c = 0.001">151.8%</td><td data-label="Ridge c = 0.01">149.4%</td><td data-label="Ridge c = 0.1">144.2%</td></tr>
    <tr><th scope="row">Annual cost drag</th><td data-label="Fixed weights">0.62 pp</td><td data-label="OLS">1.33 pp</td><td data-label="Ridge c = 0.001">1.33 pp</td><td data-label="Ridge c = 0.01">1.31 pp</td><td data-label="Ridge c = 0.1">1.26 pp</td></tr>
  </tbody>
</table>

<p class="figure-caption"><strong>Table 1:</strong> Annualized arithmetic
portfolio metrics after 5 bp costs through 27 May 2026; IC ends 28 April.</p>

Figure 5 puts the later check in context. Cumulative IC is shown on common
stock-dates, so it compares ranking quality rather than coverage. Both learned
scores lead the fixed score over the full record, but OLS and Ridge remain close
to each other. The vertical line records where the penalty was locked; it does
not turn the period to its right into an untouched experiment.

<div class="research-figure ic-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/cumulative-ic-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/cumulative-ic-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/cumulative-ic.svg">
    <img src="/assets/multiple-linear-regression/cumulative-ic.png" alt="Cumulative daily rank information coefficient for the fixed-weight score, OLS, and selected Ridge model, with the 2021 penalty-lock boundary marked" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Cumulative daily rank IC
on common out-of-sample stock-dates through 28 April 2026.</p>

Across that full common-date record, mean daily IC / daily IC standard deviation
are 0.04213 / 0.12488 for fixed weights, 0.04557 / 0.08511 for OLS, and
0.04692 / 0.09441 for selected Ridge. Both learned rankings are less variable
than the fixed reference, but OLS is steadier than selected Ridge on this
measure. Because adjacent targets overlap, this dispersion is descriptive; it
is not a standard error or evidence that one difference is statistically
significant.

## 8. Portfolio results, limitations, and next steps

Every portfolio selects the 75 highest- and 75 lowest-ranked eligible stocks.
The ranking chooses the names; a separate trailing-volatility estimate sets
their relative sizes. Each position begins at $1/75$, is scaled toward a 20%
reference volatility, and is capped at 4% of sleeve capital. Floors and leverage
caps limit extreme weights, and a side above 100% gross exposure is scaled down.

Three equal-capital sleeves rebalance on offset weekly schedules, with each
sleeve held for three weeks. Orders execute at the following close. Reported
net returns charge 5 basis points for every dollar traded, including initial
formation. Borrow fees, financing, market impact, and taxes are not included.

Over the full record, OLS earns 7.10% a year after costs with 7.41% volatility
and a 0.96 Sharpe. The selected Ridge model earns 7.73% with 8.26% volatility
and a 0.94 Sharpe. Its return is 0.63 percentage points higher, but the extra
volatility and slightly deeper drawdown mean risk-adjusted performance is not
better. Both learned portfolios have much lower volatility and drawdown than
the fixed reference, but that gap can reflect the broader predictor set,
coverage, stock selection, and sizing—not regularization alone.

<div class="research-figure performance-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/performance-and-drawdowns-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/performance-and-drawdowns-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/performance-and-drawdowns.svg">
    <img src="/assets/multiple-linear-regression/performance-and-drawdowns.png" alt="Cumulative net wealth and drawdowns for the fixed-weight score, OLS, and selected Ridge model, with the 2021 penalty-lock boundary marked" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 6:</strong> Net wealth and drawdown;
the lines combine the three offset sleeves with equal capital.</p>

<table class="research-table comparison-table">
  <thead>
    <tr>
      <th>Full period</th>
      <th>Fixed weights</th>
      <th>OLS</th>
      <th>Ridge c = 0.1</th>
    </tr>
  </thead>
  <tbody>
    <tr><th scope="row">Net return</th><td data-label="Fixed weights">6.96%</td><td data-label="OLS">7.10%</td><td data-label="Ridge c = 0.1">7.73%</td></tr>
    <tr><th scope="row">Volatility</th><td data-label="Fixed weights">9.97%</td><td data-label="OLS">7.41%</td><td data-label="Ridge c = 0.1">8.26%</td></tr>
    <tr><th scope="row">Sharpe</th><td data-label="Fixed weights">0.70</td><td data-label="OLS">0.96</td><td data-label="Ridge c = 0.1">0.94</td></tr>
    <tr><th scope="row">Maximum drawdown</th><td data-label="Fixed weights">−31.70%</td><td data-label="OLS">−18.77%</td><td data-label="Ridge c = 0.1">−19.69%</td></tr>
    <tr><th scope="row">Market beta</th><td data-label="Fixed weights">0.08</td><td data-label="OLS">0.08</td><td data-label="Ridge c = 0.1">0.10</td></tr>
    <tr><th scope="row">Turnover per sleeve rebalance</th><td data-label="Fixed weights">77.8%</td><td data-label="OLS">165.3%</td><td data-label="Ridge c = 0.1">160.9%</td></tr>
    <tr><th scope="row">Annual cost drag</th><td data-label="Fixed weights">0.68 pp</td><td data-label="OLS">1.44 pp</td><td data-label="Ridge c = 0.1">1.40 pp</td></tr>
  </tbody>
</table>

<p class="figure-caption"><strong>Table 2:</strong> Full-period arithmetic
return and risk after 5 bp costs, averaged across executable calendars.</p>

Turnover is the clearest implementation trade-off. The learned scores replace
roughly twice as much of each sleeve as the fixed score. Moving from OLS to the
selected penalty lowers turnover by only 4.4 percentage points per sleeve
rebalance and annual cost drag by about 0.04 points. That reduction is real but
small relative to the difference between fixed and learned scores.

### What this experiment does not establish

The evidence supports three narrow observations: the six reference components
were positive but uneven on a matched historical sample; the learned scores
ranked stocks more consistently than this fixed reference; and a strong Ridge
penalty materially shrank coefficients and changed predictions. It does not
show that regularization caused the learned strategy's advantage, or that the
selected penalty improves portfolio outcomes.

Several limitations qualify the result:

- Factor, feature, target, and portfolio decisions used historical knowledge,
  including the period after 2020. The later test is only a pseudo-holdout.
- The fixed score and learned score use different predictor sets and coverage.
  Their portfolio gap is not an estimator effect.
- The alpha grid is small, the selected value is its upper boundary, and the
  exercise was designed after earlier results existed. A wider nested search
  inside the development period is the proper next penalty test.
- Overlapping forward targets make daily IC observations serially dependent.
  IC means and dispersion are descriptive, not significance statistics.
- The portfolio uses individual volatility but not stock-to-stock covariance,
  and the constant-cost model omits borrow, financing, and market impact.

### The next research steps

The prediction side should first add economically distinct, less-correlated
predictors and test their incremental value, rather than adding more variants
of existing themes. A matched estimator study can then compare OLS, Ridge,
other linear penalties, and a nonlinear model such as LightGBM on the same
features and splits. A tree model may capture thresholds and interactions that
a linear score cannot, but it also brings more tuning and overfitting risk.

Portfolio construction is the other large opportunity. A covariance-aware
optimizer could manage total risk and concentration instead of scaling each
stock independently. Trading should begin from current drifted holdings and
compare the expected benefit of each change with realistic costs, allowing a
position to remain when the new target is not worth trading toward.

My practical conclusion is therefore not “use Ridge.” Multiple linear
regression is a useful, transparent way to combine many predictors, and OLS is
the essential baseline. Ridge makes the fitted coefficients smaller and can
change the ranking, but the penalty that won the development IC test did not
improve later risk-adjusted portfolio performance. The next decision is to
improve the validation and trading problem, not to treat regularization itself
as the result.
