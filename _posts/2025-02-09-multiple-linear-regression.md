---
layout: post
title: "Combining Multiple Predictors: The Linear Case"
description: "Combining overlapping stock predictors with linear regression, and why smaller Ridge coefficients need not produce a different portfolio."
date: 2025-02-09
last_modified_at: 2026-09-14
categories: ["Regression"]
article_label: Factor combination · Multiple linear and Ridge regression
permalink: /quants/2025/02/09/multiple-linear-regression.html
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/systematic-equity-research
---

<p class="article-summary">Learning from a broad set of stock predictors produces lower-volatility portfolios than a small fixed-weight benchmark, with comparable net returns and roughly twice the trading. Regularizing the regression changes the coefficients much more than it changes the stocks selected.</p>

Here I use multiple linear regression to model stocks' relative risk-adjusted
performance from momentum, volatility, liquidity, size and short-positioning
predictors. I'm interested in how correlated inputs affect the fitted model,
and what regularization changes in its coefficients and predictions.

I start with ordinary least squares (OLS), then compare it with Ridge
regression. OLS estimates the relationship with each predictor conditional
on the others, but multicollinearity can produce large, opposing coefficients.
Ridge penalizes coefficient size. That gives me a way to examine whether
shrinking the coefficients also makes the forecasts more stable and useful.

The portfolio comparison follows from that modelling question. I compare
the stock rankings and returns after costs, using the same allocation rules
for both models and a smaller fixed-weight benchmark. This builds on the
[low-volatility article](/quant/2024/12/15/low-volatility-factor.html): the
focus now is the model that selects stocks, before deciding how to size them.

## Target and predictors
{: #what-i-ask-the-model-to-predict }

The prediction target is each stock's forward 20-session Sharpe ratio: mean
daily return divided by daily return volatility over those sessions, ranked
within date and sector. This builds a preference for risk-adjusted performance
into stock selection. The forecasts are relative ranking scores; ranking
discards the original return magnitudes.

Both regressions use 144 predictors, mostly based on prices and trading
activity: momentum and trend, volatility, liquidity, size and short positioning.
Many measure the same idea at different horizons. On each date, I rank stocks
on each predictor across the whole eligible universe and rescale the ranks to
roughly −1 to 1. This makes different units comparable and limits the influence
of raw outliers. The regression coefficients then describe the effect of a
stock's relative standing on each predictor.

The universe uses point-in-time Russell 1000 membership, excluding stocks below
five dollars, announced merger targets and duplicate share classes. Predictor
ranks and portfolio selection span sectors, even though the target compares
sector peers. Sector exposures can therefore remain in the portfolio.

## A fixed-weight comparison

My benchmark combines momentum, defensive signals and short positioning with
fixed weights. It favors medium-term strength, lower volatility and lighter
short positioning. Table 1 gives the twelve inputs, grouped into three themes
so that a theme's weight doesn't depend on how many variants it contains.

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

The fixed rule uses twelve predictors, while OLS and Ridge use 144.
Comparing them tests the broader learned approach as a whole, changing both the
inputs and their weights. OLS versus Ridge keeps the predictors fixed and
isolates regularization. All three use the same eligible stocks.

## Learning the combination

For stock $$i$$ on date $$t$$, the regression predicts the target from the
vector of predictor ranks $$\mathbf X_{i,t}$$:

$$\widehat y_{i,t}=\beta_0+\mathbf X_{i,t}^{\top}\boldsymbol\beta.$$

The coefficients $$\boldsymbol\beta$$ determine how the inputs combine, and
$$\beta_0$$ is an intercept. OLS minimizes squared error between these
predictions and the observed target ranks. A positive coefficient rewards a
high predictor rank, conditional on the other inputs; a negative coefficient
reverses that preference.

Correlated predictors can substitute for one another, making their individual
coefficients hard to estimate reliably. This is the multicollinearity problem.
Take two versions of a trend signal. A score contribution of
$2x_1-1.8x_2$ can be written as $0.2x_1+1.8(x_1-x_2)$. If the two inputs were
identical, the difference term would vanish and only their combined weight
would matter. When they are merely similar, this combination puts a small
weight on what they share and a large weight on the gap between them.

That gap might contain useful information about the shape of a price trend.
It might also be mostly noise. The large weight on the gap makes the score
sensitive to changes in how the two signals move together. I want to allow
useful differences without relying too heavily on a relationship estimated
from a particular sample.

Ridge discourages large coefficients by adding a penalty:

$$
\min_{\beta_0,\boldsymbol\beta}
\frac{1}{n}\sum_{k=1}^{n}
\left(y_k-\beta_0-\mathbf X_k^\top\boldsymbol\beta\right)^2
+c\lVert\boldsymbol\beta\rVert_2^2.
$$

Here $n$ counts training stock-date observations and $y_k$ is the observed
target rank. The intercept is unpenalized; $c=0$ gives OLS. With positive $c$,
a large coefficient has to reduce prediction error enough to offset its
penalty. Ridge accepts a worse fit to the training sample in exchange for
shrinking the coefficients, with the aim of making predictions less sensitive
to estimation noise. Both positive and negative coefficients remain possible.

I use $c=0.01$: a compromise that reduces coefficient size and movement while
keeping the portfolio close to OLS. I'm looking for a less fragile combination,
so I'll check both the coefficients and the portfolios it produces.

## From predictions to portfolios

I fit the models on an expanding history beginning in January 1995, then
predict the next block of dates. A gap between training and prediction lets
the last training outcomes finish before the forecasts begin. Predictions
start in September 1998.[^training]

I report results through December 2021 and for January 2022–May 2026 separately.

All three scores enter the same portfolio rule: buy the top 75 stocks and
short the bottom 75, size inversely to volatility with stock and book caps,
and rebalance every three weeks with next-close execution. I charge 5 bp per
dollar traded. Three starting-week schedules show sensitivity to the
rebalancing calendar; reported statistics are their averages. Returns use
arithmetic annualization, and Sharpe assumes a zero cash rate. Two-way turnover
counts all purchases and sales relative to strategy capital, annualized.

## Prediction quality and portfolio results

Table 2 compares ranking quality using the daily information
coefficient (IC), the cross-sectional Spearman correlation between each score
and the target observed over the following 20 sessions.
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
IC. It's still a useful competitor. IC evaluates the ordering across the
cross-section, while the portfolio holds only the extremes, sizes them and pays
to change them. A gain in IC need not translate into a gain in net returns.

During development, OLS earns slightly more net return than the fixed score,
with lower volatility and a shallower maximum drawdown (Table 3). Extra trading
consumes 0.74 percentage points of its 1.08-point gross-return advantage. That
leaves most of the Sharpe improvement coming from lower volatility.

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
more volatility and a lower Sharpe. Ridge's volatility is about 19% below the
fixed rule during development and 25% below it later, but its annual net-return
advantage moves from +0.59 percentage points to −0.68 points. I find the lower
risk useful; the return comparison is less convincing for a model using twelve
times as many predictors and roughly twice the trading.

The OLS–Ridge difference is much smaller. Ridge's 0.25-point development return
gain comes with higher volatility, leaving both Sharpes close to 1.00. That
small Sharpe difference changes sign across the three starting-week schedules;
after 2021, Ridge's mean Sharpe is 0.79 versus 0.83 for OLS. It saves less than
0.03 percentage points in annual trading costs in either period. Regularizing
the coefficients has done little to reduce the trading bill. The flat charge
also omits borrow, financing and market impact.

Figure 1 shows the paths behind the period averages. OLS and Ridge remain
close, while both have shallower development drawdowns than the fixed score.
The lower risk is consistent with the preference built into the training
target. Its separate contribution would require a comparison with a model
trained on an unadjusted return target.

<div class="research-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/performance-and-drawdowns" mobile="/assets/multiple-linear-regression/performance-and-drawdowns_mobile" alt="Net growth on a logarithmic scale with a shared drawdown panel below for fixed weights, OLS, and Ridge" version="19" %}
</div>

<p class="figure-caption"><strong>Figure 1: Portfolio paths from the three scores.</strong> The mean daily net P&amp;L of the three schedules, on common active dates, compounded into an index starting at <span class="mathjax-ignore">$1</span> (log scale), with drawdowns below. Each portfolio retains its own risk level; Table 3 supplies the risk-adjusted comparison for development through 2021 and the later period from January 2022.</p>

## What Ridge changes

The coefficient diagnostics help explain the similar portfolios. Ridge reduces
coefficient size and absolute movement between refits by roughly one third.
But once I normalize the coefficient vectors to the same length, their
directions change by similar amounts. Much of the apparent stability comes
from shrinking the weights.

Scale also matters when interpreting the predictions. Multiplying all
coefficients by the same positive constant would leave the stock ordering
unchanged. Ridge can change their relative sizes too, but related inputs give
it room to redistribute weights while keeping much the same score. A score
change then affects selection only when it moves a stock across the portfolio
cutoff. Here the daily rankings have a 0.991 correlation, and only about 14–15
of the 150 daily candidates differ between OLS and Ridge.

Figure 2 follows the ten largest mean absolute Ridge coefficients across the
twelve refits. All ten keep the same sign. Price relative to its 126-day moving
average stays positive, while 10/21-day MACD stays negative; both remain among
the ten largest weights at every refit. Holding the other predictor ranks
fixed, they favor relative longer-term strength with weaker recent momentum.

<div class="research-figure coefficient-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/top-coefficients" alt="Signed coefficients for the ten largest mean absolute Ridge weights across walk-forward refits" version="12" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> The ten largest mean absolute Ridge coefficients, averaged across the three training subsamples at each refit. Signs persist while most magnitudes decline; the rows are selected using the full coefficient history.</p>

I read this as persistent directions with changing emphasis. The model keeps
favoring similar patterns, but most weights become smaller. Each coefficient
describes an effect alongside the other predictors, so I wouldn't read a large
weight as a standalone signal's importance.

## Where this leaves me

Linear regression gives me an inspectable way to turn many related predictors
into forecasts. I prefer Ridge as a linear baseline because I'm less
comfortable relying on large weights that nearly cancel each other. At my
chosen penalty, I get smaller coefficients with little change in prediction
quality or portfolio performance relative to OLS.

The larger trade-off is between either learned model and the fixed rule.
Lower portfolio volatility is useful, but the extra trading absorbs much of
the development return advantage. Before adding more predictors, I would next
fit OLS and Ridge on the benchmark's same twelve inputs, keeping the portfolio
rules fixed. That would tell me more directly what learning the weights adds.

[^training]: The first fit uses 900 trading dates, followed by a 21-date gap.
    I refit every 600 dates, expanding the training history, for twelve refits.
    At each refit, three regressions use interleaved subsets of training dates;
    I average their predictions before ranking stocks. The coefficient charts
    show the corresponding average weights.
