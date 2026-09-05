---
layout: post
title: "Combining Stock Predictors with Linear Regression"
description: "Learning a joint stock ranking from overlapping predictors, and what Ridge regularization adds."
date: 2025-02-09
last_modified_at: 2026-09-06
categories: ["Regression"]
article_label: Factor combination · Multiple linear and Ridge regression
permalink: /quants/2025/02/09/multiple-linear-regression.html
series_next: /quants/2026/08/29/portfolio-optimization.html
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/systematic-equity-research
---

<p class="article-summary">Ridge substantially shrinks the regression coefficients but barely changes the stock ranking or the resulting portfolio. Both learned scores deliver lower volatility than a small fixed-weight benchmark, with broadly similar net returns and roughly twice the trading. For this portfolio, trading costs matter much more than the choice between OLS and Ridge.</p>

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

The universe uses point-in-time Russell 1000 membership, excluding stocks below
five dollars, announced merger targets and duplicate share classes.

OLS and Ridge use the same set of 144 predictors, mostly built from
prices and trading activity. They cover momentum and trend, volatility,
liquidity, size and short positioning. Many measure the same idea at different
horizons, so the model has to combine many overlapping inputs.

On each date, I rank stocks cross-sectionally on each predictor and rescale
those ranks to roughly −1 to 1. Each stock is compared with the other stocks
available on that date. This limits the influence of raw outliers and
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

## A fixed-weight comparison

I compare the learned scores with a fixed combination of momentum, defensive
signals and short positioning. Momentum looks for continuing medium-term
strength; defensive signals favor quieter stocks; heavy short positioning
is treated as a possible bearish signal. Table 1 gives each theme a few
representative measures.

<table class="research-table settings-table benchmark-ingredients">
  <caption><strong>Table 1: The fixed score.</strong> Each theme receives one third of the weight, divided equally among its ingredients. Horizons are trading sessions.</caption>
  <thead>
    <tr><th>Theme</th><th>What the score favors</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Momentum</th><td>Higher returns over 63, 126 and 252 sessions; higher price relative to its 126- and 252-session moving averages</td></tr>
    <tr><th scope="row">Defensive</th><td>Lower volatility over 21, 63 and 126 sessions; lower downside volatility over 63 and 126 sessions</td></tr>
    <tr><th scope="row">Short positioning</th><td>Lower short interest relative to daily volume, smoothed over 21 and 63 sessions</td></tr>
  </tbody>
</table>

I orient the predictor ranks as shown, average within each theme, then average
the three themes. This covers several horizons without giving a theme more
weight just because it has more variants. The directions and equal weights
come from the investment ideas and were fixed before inspecting the revised
benchmark's results. Size stays out of this fixed rule.

The fixed rule uses twelve predictors, while OLS and Ridge use 144.
Their comparison asks what the broader learned approach delivers over a
sensible investment rule; it changes both the inputs and their weights.
All three use the same eligible stocks. OLS versus Ridge also keeps the
predictors fixed, isolating regularization.

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
It might also be mostly measurement noise. The large weight on the gap makes
the score sensitive to changes in how the two signals move together. Opposite
signs give me a reason to inspect that relationship; they do not, by themselves,
establish overfitting. A good portfolio backtest also leaves that question open.

Ridge discourages large coefficients by adding a penalty:

$$
\min_{\beta_0,\boldsymbol\beta}
\frac{1}{n}\sum_{k=1}^{n}
\left(y_k-\beta_0-\mathbf X_k^\top\boldsymbol\beta\right)^2
+c\lVert\boldsymbol\beta\rVert_2^2.
$$

Here $n$ counts training stock-date observations. The intercept is unpenalized;
$c=0$ gives OLS. With positive $c$, a large coefficient has to earn its place
by reducing prediction error enough to offset the penalty. This makes it harder
to rely on large offsetting weights, though Ridge does not force coefficients
to follow the signs I would choose for standalone factors.

The recorded fitting rule starts with 900 trading dates from January 1995,
leaves a 21-date gap, then predicts the next 600 trading dates. I refit from
scratch every 600 dates, expanding the training history and keeping the same
gap. Predictions begin in September 1998; there are twelve refits, with a
shorter final prediction block. The gap lets the last training date's full
20-session outcome finish before prediction begins. Targets require all 20
returns, and rows with missing targets are excluded from fitting.

At each refit, I fit three regressions: one on training dates 1, 4, 7, …,
one on dates 2, 5, 8, …, and one on dates 3, 6, 9, …. Each scores every stock
in the next prediction block. I average their three predicted scores equally,
then rank that average. For a linear model, this is equivalent to averaging
their intercepts and coefficient vectors; those averaged coefficients are
what the heatmap and movement diagnostics describe. The 20-session targets
still overlap within these samples, and stocks on the same date share market
and sector shocks. Three fits therefore do not provide three independent tests.

Keeping the older data gives the model more observations to estimate a common
combination, which can slow adaptation when relationships change. Development
ends in December 2021. January 2022–May 2026 has also informed research choices,
including the benchmark revision, so it is a later historical check.

I retain $c=0.01$, chosen during development to reduce coefficient size and
movement while keeping the portfolio close to OLS. I made that trade-off by
judgment, without setting a numerical acceptance threshold in advance. The
comparison below evaluates that choice with the revised fixed rule.

I keep portfolio construction fixed so the comparison follows differences in
the rankings. Inverse-volatility sizing gives less weight to volatile stocks;
three starting weeks show sensitivity to the rebalancing calendar.
All three scores enter the same rule: the top and bottom 75 stocks,
inverse-volatility sizing with stock and book caps, three-week rebalancing,
next-close execution, and 5 bp per dollar traded. Reported portfolio statistics
are averaged across three starting-week schedules. Returns use arithmetic
annualization and a zero cash rate for Sharpe. Annual traded notional counts
all long- and short-side trades relative to strategy capital.

## Ranking and portfolio results

Table 2 evaluates the ordering itself. Daily IC is the cross-sectional
Spearman correlation between the score and the subsequently observed target.
OLS and Ridge have almost identical mean IC in both periods. The small
development gain from Ridge disappears in the later period.

<table class="research-table comparison-table ic-summary-table portfolio-card-table">
  <caption><strong>Table 2: Cross-sectional ranking quality.</strong> Mean daily rank IC, its standard deviation and their unannualized ratio. Adjacent observations share overlapping 20-session outcomes; later IC ends on 28 April 2026, the last complete target date.</caption>
  <thead>
    <tr><th>Ranking</th><th>Mean daily IC</th><th>IC SD</th><th>IC IR</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="4">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Fixed</th><td>0.0367</td><td>0.1093</td><td>0.336</td></tr>
    <tr><th scope="row">OLS</th><td>0.0464</td><td>0.0814</td><td>0.570</td></tr>
    <tr><th scope="row">Ridge</th><td>0.0472</td><td>0.0835</td><td>0.566</td></tr>
    <tr class="period-heading"><th colspan="4">Later · January 2022–April 2026</th></tr>
    <tr><th scope="row">Fixed</th><td>0.0490</td><td>0.1243</td><td>0.394</td></tr>
    <tr><th scope="row">OLS</th><td>0.0435</td><td>0.1042</td><td>0.417</td></tr>
    <tr><th scope="row">Ridge</th><td>0.0435</td><td>0.1087</td><td>0.400</td></tr>
  </tbody>
</table>

The fixed score has the highest later-period mean IC, with more variable daily
IC. On this measure, the small fixed rule is still a useful competitor.
But I do not trade the entire ranking. The portfolio holds its tails, sizes
those positions and pays to change them, so I also need to follow the scores
through to returns.

Table 3 shows the result. During development, OLS has similar net return to the
fixed score, lower volatility and a shallower maximum drawdown. Extra trading
consumes 0.74 percentage points of its 1.08-point gross-return advantage.
Most of the higher Sharpe comes from lower volatility.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 3: Net performance and trading.</strong> Mean of three schedule-level statistics, after 5 bp per dollar traded. Arithmetic return and volatility are annualized; traded notional is annual two-way trading divided by strategy capital.</caption>
  <thead>
    <tr><th>Score</th><th>Net return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Traded notional / year</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="6">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Fixed</th><td>6.81%</td><td>9.11%</td><td>0.75</td><td>−26.32%</td><td>14.4×</td></tr>
    <tr><th scope="row">OLS</th><td>7.14%</td><td>7.14%</td><td>1.00</td><td>−18.31%</td><td>29.3×</td></tr>
    <tr><th scope="row">Ridge</th><td>7.40%</td><td>7.36%</td><td>1.01</td><td>−18.46%</td><td>29.0×</td></tr>
    <tr class="period-heading"><th colspan="6">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Fixed</th><td>7.76%</td><td>11.92%</td><td>0.65</td><td>−10.03%</td><td>13.1×</td></tr>
    <tr><th scope="row">OLS</th><td>7.17%</td><td>8.67%</td><td>0.83</td><td>−7.91%</td><td>26.8×</td></tr>
    <tr><th scope="row">Ridge</th><td>7.08%</td><td>8.98%</td><td>0.79</td><td>−8.28%</td><td>26.3×</td></tr>
  </tbody>
</table>

After 2021, the fixed rule earns more net return than either regression, with
more volatility and a lower Sharpe. The learned portfolios' main advantage
here is lower risk. Their extra trading remains substantial in both periods.

Ridge's Sharpe is 1.01 versus 0.75 for the fixed rule during development,
and 0.79 versus 0.65 later. Annual net return improves by
0.59 percentage points during development and is 0.68 points lower later.
Volatility falls by about 19% and 25%, respectively. The improvement is mainly
in risk-adjusted performance, and this comparison changes both the inputs and
how they are combined.

The OLS–Ridge difference is much smaller. Ridge's 0.25-point development return
gain comes with higher volatility, leaving both Sharpes close to 1.00. That
small Sharpe difference changes sign across the three starting-week schedules.
After 2021 its mean Sharpe is 0.79 versus 0.83 for OLS. Ridge saves less than
0.03 percentage points in annual trading costs in either period. Changing the
regression penalty does little to reduce the learned score's trading bill.
The flat trading charge also omits borrow, financing and market impact.

Figure 1 shows the paths behind the period averages. OLS and Ridge remain
close, while both have shallower development drawdowns than the fixed score.
The lower risk is consistent with the preference built into the training
target. Its separate contribution would require a comparison with a model
trained on an unadjusted return target.

<div class="research-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/performance-and-drawdowns" mobile="/assets/multiple-linear-regression/performance-and-drawdowns_mobile" alt="Net growth on a logarithmic scale with a shared drawdown panel below for fixed weights, OLS, and Ridge" version="19" %}
</div>

<p class="figure-caption"><strong>Figure 1: Portfolio paths from the three rankings.</strong> The mean daily net P&amp;L of the three schedules, on common active dates, compounded into an index starting at <span class="mathjax-ignore">$1</span> (log scale), with drawdowns below. Each portfolio retains its own risk level; Table 3 supplies the risk-adjusted comparison for development through 2021 and the later period from January 2022.</p>

## What Ridge changes

The similar portfolios leave a useful question: how much has Ridge changed
the fitted combination? At the selected penalty, coefficient size and absolute
movement between refits fall by roughly one third. After normalizing each
coefficient vector to unit length, though, OLS and Ridge show similar changes
in direction. Smaller vectors can move less in absolute terms without making
the predictor relationships more stable.

The full ranking has a 0.991 correlation with OLS, and about 14–15 of the 150
daily candidates differ. Related inputs give the model room to redistribute
their weights while keeping much the same score, as in the two-trend example
above. Selection adds another filter: a score change affects membership only
when it moves a stock across the portfolio cutoff. Ridge has changed the
coefficients quite a bit while leaving me with much the same stocks.

Figure 2 follows the ten largest mean absolute Ridge coefficients across the
twelve refits. All ten keep the same sign. Price relative to its 126-day moving
average stays positive, while 10/21-day MACD stays negative; both remain among
the ten largest weights at every refit. Holding the other predictor ranks
fixed, they favor relative longer-term strength with weaker recent momentum.

<div class="research-figure coefficient-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/top-coefficients" alt="Signed coefficients for the ten largest mean absolute Ridge weights across walk-forward refits" version="12" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> The ten largest mean absolute Ridge coefficients, averaged across the three training subsamples at each refit. Signs persist while most magnitudes decline; the rows are selected using the full coefficient history.</p>

The price-to-moving-average coefficient settles around 0.02–0.03 after its
larger first estimate, while short-horizon MACD roughly halves in magnitude,
from −0.032 to −0.016. I read this as persistent directions with changing
emphasis. These are conditional weights among overlapping predictors, and
the training windows themselves overlap. Selecting the largest weights over
the full history also makes their persistence a descriptive finding.

## What the learned combination delivers

Linear regression provides a workable way to combine this broad predictor set
into a stock ranking. Its portfolio has lower risk than the small fixed score,
with comparable net return and substantially more trading.

Ridge regularizes the combination, but its smaller coefficients bring little
change to the investment decision. I chose the penalty to shrink coefficients
while keeping the portfolio close to OLS, so the similar performance partly
reflects that choice. I prefer Ridge as a simple baseline because I am less
comfortable relying on large weights that nearly cancel each other: small
changes in the relationship between those inputs can then matter too much.
The later results give me no clear performance reason to prefer it to OLS.
For this portfolio, the extra trading introduced by the learned ranking matters
far more than the choice between the two regressions.

To isolate what learning the weights adds, I would next fit OLS and Ridge on
the benchmark's same twelve predictors, keeping the portfolio rules fixed.
