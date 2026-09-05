---
layout: post
title: "Combining Stock Predictors with Linear Regression"
description: "Learning a joint stock ranking from overlapping predictors, and what Ridge regularization adds."
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

<p class="article-summary">Linear regression turns many overlapping stock predictors into one learned ranking. Here OLS and Ridge produce similar net returns to a small fixed-weight benchmark with lower volatility, but roughly twice the trading. Ridge reduces coefficient size and movement by about a third while leaving the ranking almost unchanged; it does not clearly improve on OLS after 2021.</p>

Several versions of momentum, volatility, liquidity and size can each look
reasonable on their own. Combining them is less straightforward. How much
weight should I give to each, especially when several describe much the same
thing?

Linear regression appeals to me here because I can let the data choose the
weights and still inspect the combination. That doesn't make the overlap go
away: the model can give large, opposing weights to very similar predictors.
I compare ordinary least squares with Ridge, which penalizes large
coefficients, and follow both through to the stocks they select and the
portfolios they produce outside their training windows.

## Predictors and the ranking target

OLS and Ridge use the same 144 predictors. They cover return and trend,
volatility, price location, size and market sensitivity, trading activity,
liquidity, and lagged short positioning. Examples include price
relative to a moving average, upside and downside volatility, and
short-interest-to-volume. Several appear at different horizons, so 144 inputs
represent far fewer independent economic ideas.

I rank each predictor across the current stock universe and put the ranks on
a common scale near −1 to 1. This limits the influence of raw outliers and
makes inputs measured in different units comparable. It also discards the
distance between raw values: the model learns from relative positions in the
cross-section.

The target ranks each stock's average daily return over the next 20 sessions
divided by its volatility over those sessions. For positive forward returns,
a quieter gain receives a better outcome than an equally large volatile gain.
I am asking the model to prefer those quieter gains, so the risk preference
starts in the training target, before I size a single position.

I rank that outcome within each date and sector, asking which stocks do better
than their sector peers. Predictor ranks retain cross-sector information.
Selection is global, so the resulting portfolio can still have sector
exposures. How well that stock-level preference translates into portfolio
Sharpe is something I check in the backtest.

As a reference, I use a fixed score with five equally weighted themes:
defensive, momentum, low short positioning, larger company size, and return
consistency. The defensive theme averages low volatility and avoidance of
unusually large up days. This gives me a small, readable rule to compare with
the learned scores. Regression also uses more predictors and different data
coverage, so any difference can come from those inputs as well as their
weights. OLS and Ridge use exactly the same inputs and eligible stocks.

## Learning the combination

The model assigns each stock a score from its predictor ranks:

$$\widehat y_{i,t}=\beta_0+\mathbf X_{i,t}^{\top}\boldsymbol\beta.$$

OLS chooses the coefficients to minimize squared error against the target
ranks. A positive coefficient rewards a high predictor rank, conditional on
the other inputs; a negative coefficient reverses that preference.

The awkward part is that related predictors can substitute for one another.
Take two versions of a trend signal. A score contribution of
$2x_1-1.8x_2$ can be written as $0.2x_1+1.8(x_1-x_2)$. If the two inputs were
identical, the difference term would vanish and only their combined weight
would matter. When they are merely similar, the model puts a small weight on
what they share and a large weight on the gap between them.

That gap might contain useful information about the shape of a price trend.
It might also be mostly measurement noise. This is why I wouldn't diagnose
overfitting just by spotting opposite signs in a coefficient table: I need to
look at what the predictors are doing together.

Ridge discourages large coefficients by adding a penalty:

$$
\min_{\beta_0,\boldsymbol\beta}
\frac{1}{n}\sum_{k=1}^{n}
\left(y_k-\beta_0-\mathbf X_k^\top\boldsymbol\beta\right)^2
+c\lVert\boldsymbol\beta\rVert_2^2.
$$

Here $n$ counts training stock-date observations. The intercept is unpenalized;
$c=0$ gives OLS. With positive $c$, a large coefficient has to earn its place
by reducing prediction error enough to offset the penalty. Ridge shrinks the
slopes; lasso's L1 penalty can also set them to zero.

I use expanding walk-forward fits, with a 21-session buffer between training
outcomes and the next prediction block. Predictions begin in September 1998.
Development ends in December 2021. January 2022–May 2026 has also informed
research choices, so it is later, reused evidence rather than an untouched
holdout.

I selected $c=0.01$ during development because it reduced coefficient size and
movement while keeping the portfolio close to OLS. I made that trade-off by
judgment, without setting a numerical acceptance threshold in advance. The
tested penalties gave me little reason to expect a reliable performance gain.

All three scores enter the same portfolio rule: the top and bottom 75 stocks,
inverse-volatility sizing with stock and book caps, three-week rebalancing,
next-close execution, and 5 bp per dollar traded. Reported portfolio statistics
are averaged across three starting-week schedules. Returns use arithmetic
annualization and a zero cash rate for Sharpe. Two-way turnover counts all
long- and short-side trades relative to strategy capital.

## What the model learns

Figure 1 follows the ten largest mean absolute Ridge coefficients across
refits. Price relative to its moving average remains positive; short-horizon
MACD and illiquidity remain negative. Other coefficients weaken or change sign.
To read these weights, I need to keep the other predictors in mind: the model
can spread a similar signal across several of them.

The first two rows illustrate how that combination works. Holding the other
predictor ranks fixed, the positive price-to-126-day-average weight rewards a
stock above its longer trend, while the negative 10/21-day MACD weight penalizes
a large normalized upward gap between its faster and slower price averages.

<div class="research-figure coefficient-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/top-coefficients" alt="Signed coefficients for the ten largest mean absolute Ridge weights across walk-forward refits" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Signed coefficients across refits for the selected Ridge model. The ten displayed predictors are selected by mean absolute weight; coefficient magnitude describes conditional model weight.</p>

At the selected penalty, coefficient size and absolute movement between refits
fall by roughly one third. Yet the full ranking has a 0.991 correlation with
OLS, and only about 14 of 150 selected names differ. Ridge has changed the
coefficients quite a bit while leaving me with much the same stocks.

The two-predictor example helps make sense of this. Related inputs give the
model room to change their individual weights while keeping much the same
score. Selection adds another filter: if a stock stays on the same side of the
cutoff, a change in its score need not change whether I hold it. The portfolio
can therefore be much less sensitive to regularization than the coefficient
table suggests.

I still want to be careful about calling those coefficients more stable.
Starting with smaller weights can itself produce smaller absolute changes at
the next refit. I would test modest changes to the inputs or training history
before trusting individual predictor effects more. The heatmap shows how the
model combines them; it doesn't measure their separate contributions to return.

## Ranking and portfolio results

Table 1 evaluates the ordering itself. Daily IC is the cross-sectional
Spearman correlation between the score and the subsequently observed target.
OLS and Ridge have almost identical mean IC in both periods. The small
development gain from Ridge disappears in the later period.

<table class="research-table comparison-table ic-summary-table portfolio-card-table">
  <caption><strong>Table 1: Cross-sectional ranking quality.</strong> Mean daily rank IC, its standard deviation and their unannualized ratio. Adjacent observations share overlapping 20-session outcomes; later IC ends on 28 April 2026, the last complete target date.</caption>
  <thead>
    <tr><th>Ranking</th><th>Mean daily IC</th><th>IC SD</th><th>IC IR</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="4">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Fixed</th><td>0.0399</td><td>0.1217</td><td>0.328</td></tr>
    <tr><th scope="row">OLS</th><td>0.0461</td><td>0.0864</td><td>0.534</td></tr>
    <tr><th scope="row">Ridge</th><td>0.0469</td><td>0.0885</td><td>0.530</td></tr>
    <tr class="period-heading"><th colspan="4">Later · January 2022–April 2026</th></tr>
    <tr><th scope="row">Fixed</th><td>0.0502</td><td>0.1392</td><td>0.361</td></tr>
    <tr><th scope="row">OLS</th><td>0.0417</td><td>0.1068</td><td>0.390</td></tr>
    <tr><th scope="row">Ridge</th><td>0.0415</td><td>0.1113</td><td>0.373</td></tr>
  </tbody>
</table>

The fixed score has the highest later-period mean IC, with more variable daily
IC. On this measure, the small fixed rule is still a useful competitor.
But I do not trade the entire ranking. The portfolio holds its tails, sizes
those positions and pays to change them, so I also need to follow the scores
through to returns.

Table 2 shows the result. During development, OLS has similar net return to the
fixed score, lower volatility and a shallower maximum drawdown. Extra trading
consumes 0.77 percentage points
of its 0.88-point gross-return advantage. Most of the higher Sharpe comes from
lower volatility.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 2: Net performance and trading.</strong> Net returns use arithmetic annualization, after 5 bp per dollar traded; volatility is annualized. Two-way turnover is measured per rebalance.</caption>
  <thead>
    <tr><th>Score</th><th>Net return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Turnover / rebalance</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="6">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Fixed</th><td>6.92%</td><td>9.73%</td><td>0.71</td><td>−31.55%</td><td>78.8%</td></tr>
    <tr><th scope="row">OLS</th><td>7.03%</td><td>7.15%</td><td>0.98</td><td>−18.77%</td><td>167.7%</td></tr>
    <tr><th scope="row">Ridge</th><td>7.38%</td><td>7.36%</td><td>1.00</td><td>−19.03%</td><td>165.7%</td></tr>
    <tr class="period-heading"><th colspan="6">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Fixed</th><td>7.24%</td><td>11.33%</td><td>0.64</td><td>−10.98%</td><td>69.7%</td></tr>
    <tr><th scope="row">OLS</th><td>7.50%</td><td>8.64%</td><td>0.87</td><td>−7.59%</td><td>152.8%</td></tr>
    <tr><th scope="row">Ridge</th><td>7.37%</td><td>8.95%</td><td>0.82</td><td>−8.05%</td><td>149.6%</td></tr>
  </tbody>
</table>

The portfolio results give me little reason to make much of the OLS–Ridge
difference. Development Sharpe is 1.00 versus 0.98
for OLS. After 2021 it is 0.82 versus 0.87, with slightly lower return and
higher volatility. Annual trading cost falls by only 0.02 percentage points
in development and 0.03 later. If I want to reduce the learned score's trading
bill, changing the regression penalty is doing very little for me.

Figure 2 shows the paths behind the period averages. OLS and Ridge remain
close, while both have shallower development drawdowns than the fixed score.
The risk-adjusted target and inverse-volatility sizing can both contribute to
the defensive portfolio behaviour; this comparison does not separate them.

<div class="research-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/performance-and-drawdowns" alt="Net growth on a logarithmic scale and drawdowns for fixed weights, OLS, and Ridge, with the later period marked" version="15" %}
</div>

<p class="figure-caption"><strong>Figure 2: Portfolio paths from the three rankings.</strong> Net growth of <span class="mathjax-ignore">$1</span> (log scale) and drawdown, after 5 bp per dollar traded. The portfolios have different volatilities; Table 2 supplies the risk-adjusted comparison. The 2022 boundary marks later, reused history.</p>

## What the learned combination delivers

Linear regression provides a workable way to combine this broad predictor set
into a stock ranking. Its portfolio has lower risk than the small fixed score,
with similar net return and substantially more trading. To find out how much
of that comes from learning the weights, I would next give the fixed and
learned rules the same inputs.

Ridge regularizes the combination, but its smaller coefficients bring little
change to the investment decision. I prefer it as a simple baseline because
I am less comfortable relying on large weights that nearly cancel each other.
The later results give me no clear performance reason to prefer it to OLS.
For this portfolio, the extra trading introduced by the learned ranking matters
far more than the choice between the two regressions.

Most predictors still come from prices, so expanding this set does not give
me 144 independent sources of information. The flat trading charge also omits
borrow, financing and market impact.

## Research notes

Boosted trees, random forests and neural networks can capture nonlinearities
and interactions. Recent research also explores
[transformer-based asset-pricing models](https://www.nber.org/papers/w33351)
that share information across stocks (Kelly et al., 2025; revised 2026).
Whether that flexibility improves this ranking after costs remains a question
for a later study.

The universe uses point-in-time Russell 1000 membership, excluding stocks below
five dollars, announced merger targets and duplicate share classes. The first
fit uses 900 dates; subsequent 600-date prediction blocks follow expanding
refits. Within a refit, predictions average three date-thinned training
samples. Overlapping targets and common date-level shocks still make
observations dependent.

Short-interest inputs use a deliberate 21-session delay to allow for
publication and avoid information leakage.

Each selected position starts from an equal share of its book, scaled by
20% divided by trailing 60-session volatility, with a 5% volatility floor and
4% position cap. A book exceeding 100% gross scales down; a smaller book keeps
its lower exposure.

The original matched return and coefficient files are unavailable. The
OLS–Ridge tables and figures retain the previously reported results and have
not been independently reproduced in this revision.
