---
layout: post
title: "Combining Multiple Predictors: The Linear Case"
description: "How 80 overlapping stock predictors relate, and whether learning their weights with OLS or Ridge beats a simple theme score."
date: 2025-02-09
last_modified_at: 2026-09-26
categories: ["Signals"]
article_label: Signals · Linear and Ridge regression
permalink: /quants/2025/02/09/multiple-linear-regression.html
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/systematic-equity-research
---

<link rel="stylesheet" href="/assets/css/predictor-structure.css?v=2">

In the [low-volatility article](/quant/2024/12/15/low-volatility-factor.html),
I selected stocks using one characteristic and examined how position sizing
changed the portfolio. Here I want to bring more information into that
selection. Alongside volatility, I can describe a stock by its momentum,
liquidity, size and short positioning.

With one characteristic, the ranking is the selection rule. With several, I
need weights, and the predictors overlap. A stock with strong momentum often
also has low volatility, and several momentum horizons repeat much of the
same information. How much weight should each predictor receive, given what
the others already tell me?

Before fitting anything, I want to understand the predictors: what they
measure, how much they overlap and whether their usefulness is stable. Then I
compare three ways of combining them: a fixed three-theme score, ordinary
least squares (OLS) and Ridge.

## Setup
{: #what-i-ask-the-model-to-predict }

The universe is point-in-time Russell 1000 membership, excluding stocks below
five dollars, announced merger targets and duplicate share classes.

The target is each stock's forward 20-session Sharpe ratio, roughly a trading
month: mean daily return divided by daily return volatility over the next 20
sessions. Lower future volatility amplifies both positive and negative
average returns, so the target mixes return and risk. I rank it within each
date and BICS sector and map the ranks into $(-1,1]$; a high label marks a
stock that subsequently did well relative to its sector peers.

Each predictor is ranked across the whole universe on each date and mapped in
the same way. Ranking puts different units on one bounded scale and limits
the influence of outliers, at the cost of discarding magnitudes
([details](#ranking-details)). Throughout, the information coefficient (IC)
is the cross-sectional Spearman rank correlation between a predictor, or a
score, and the target on one date.

## The predictors
{: #the-predictors }

I use 80 predictors, mostly built from prices and trading activity, in seven
themes.[^predictor-set] Each theme comes with an economic story for why it
might rank the target; where the data here disagree with the story, I say so.

<div class="theme-cards" markdown="0">
  <section class="theme-card" style="--theme-color: var(--theme-1)">
    <h3>Momentum &amp; trend <span>33 predictors</span></h3>
    <p class="theme-measures">Returns and risk-adjusted returns over 3–12 months, price relative to moving averages and to highs and lows, how persistently the price stayed above its 200-day average, and the share of losing days over up to three years.</p>
    <p>Stocks that did well over the past year have tended to keep doing well for a while, which is usually read as investors underreacting to news. Momentum built from many small moves has persisted longer than momentum from a few jumps. The theme also holds short-horizon position measures, such as price relative to its 5-day low, which work the other way.</p>
  </section>
  <section class="theme-card" style="--theme-color: var(--theme-2)">
    <h3>Short-term reversal <span>4 predictors</span></h3>
    <p class="theme-measures">Returns over the last 1–21 sessions.</p>
    <p>Over days to a month, prices partly reverse. A common reading is compensation for providing liquidity: an investor who has to sell quickly pushes the price below fair value, and the buyer earns the recovery.</p>
  </section>
  <section class="theme-card" style="--theme-color: var(--theme-3)">
    <h3>Volatility <span>12 predictors</span></h3>
    <p class="theme-measures">Close-to-close, downside and upside volatility and average true range, over 5–252 sessions.</p>
    <p>Low-volatility stocks have earned about as much as volatile ones with far less risk. Investors who cannot or will not use leverage bid up high-beta stocks, and some pay for lottery-like payoffs. The target adds a tilt when returns are positive: lower future volatility raises the Sharpe ratio of a positive mean, and volatility persists.</p>
  </section>
  <section class="theme-card" style="--theme-color: var(--theme-4)">
    <h3>Size <span>10 predictors</span></h3>
    <p class="theme-measures">Log market capitalization, its change, its position relative to recent highs and lows, and its variability: the standard deviation of log market cap over a window.</p>
    <p>Every stock here is in the Russell 1000, so size means large versus mega cap. Larger, steadier companies tend to have lower future volatility, and the change in market cap overlaps with momentum.</p>
  </section>
  <section class="theme-card" style="--theme-color: var(--theme-5)">
    <h3>Liquidity &amp; volume <span>10 predictors</span></h3>
    <p class="theme-measures">Share turnover, Amihud illiquidity (absolute return per dollar traded), variability of trading volume, and the correlation between price and volume changes.</p>
    <p>Heavily traded stocks have tended to earn less than lightly traded ones. Illiquid stocks should compensate their holders, but here Amihud illiquidity points the other way: within the Russell 1000 it mostly marks the smaller names, which rank lower on the target.</p>
  </section>
  <section class="theme-card" style="--theme-color: var(--theme-6)">
    <h3>Market correlation <span>2 predictors</span></h3>
    <p class="theme-measures">Correlation of the stock's daily returns with the market over one and two years.</p>
    <p>Beta is correlation times relative volatility; this theme isolates the correlation. The betting-against-beta argument says market-sensitive stocks are overpriced. Here higher correlation ranked slightly better on average, but the sign flips with the market's direction: such stocks look good on a 20-session Sharpe target when the market rises.</p>
  </section>
  <section class="theme-card" style="--theme-color: var(--theme-7)">
    <h3>Short positioning <span>9 predictors</span></h3>
    <p class="theme-measures">Short interest relative to daily volume, its variability, and changes in short interest.</p>
    <p>Short sellers are often well informed, and heavily shorted stocks have tended to underperform. Short interest relative to volume, often called days to cover, also measures crowding: how long the shorts would need to buy back.</p>
  </section>
</div>

The literature behind these stories is in the footnote.[^theme-references]

## How the predictors overlap
{: #correlation-structure }

On every fifth session from 1998 through 2021, once every predictor has
enough history, I compute the rank correlation between every pair of
predictors and between each predictor and the target. First I flip the sign
of each predictor whose average IC is negative. Lower volatility predicts a
higher target, for example, so I use negative volatility. After the flip, a
positive correlation means two predictors favour the same stocks.

To follow whole themes, I also combine each theme into one composite: the
equal-weight sum of its signed, standardized predictor ranks. Figure 1 lets
you pick a period and switch between all 80 predictors and the seven theme
composites. The predictors are ordered by a dendrogram, which joins the most
similar predictors first, and the colour strip shows each one's theme. The
lower panel adds up each composite's daily IC with the target, so a steadily
rising line is a theme that kept ranking stocks well.

{% include predictor-structure-explorer.html %}

<noscript markdown="0">
  <div class="research-figure responsive-figure">
    {% include theme-svg-figure.html base="/assets/multiple-linear-regression/predictor-correlation" mobile="/assets/multiple-linear-regression/predictor-correlation_mobile" alt="Heatmap of average rank correlations between the 80 predictors, grouped into seven theme blocks." version="3" %}
  </div>
  <div class="research-figure responsive-figure">
    {% include theme-svg-figure.html base="/assets/multiple-linear-regression/theme-ic-by-year" mobile="/assets/multiple-linear-regression/theme-ic-by-year_mobile" alt="Heatmap of each theme composite's mean IC by year from 1998 to 2021." version="3" %}
  </div>
</noscript>

<p class="figure-caption"><strong>Figure 1: How the predictors relate to each other and to the target.</strong> Average rank correlation over the selected period, every fifth session, with each predictor signed so that its 1998–2021 average IC is positive; blue pairs favour the same stocks. The dendrogram (average linkage on 1 − |ρ|) is fitted once on 1998–2021 so that periods stay comparable. The lower panel adds up each theme composite's IC with the forward 20-session sector-relative Sharpe target; the legend gives each theme's mean IC over the period.</p>

Over the full period, volatility is the most coherent theme: its predictors
correlate 0.71 on average. Momentum &amp; trend is the least coherent. It
spans horizons from days to three years, and 43% of its signed pairs are
negatively correlated: a stock trading well above its 10-day average is a
short-term bet against the stock, while a strong 12-month return is a bet for
it. The dendrogram agrees: cut into seven clusters, it matches the themes for
about three quarters of the predictors, and the exceptions are informative.
The 5–21-day price-position measures join short-term reversal, market-cap
variability joins volatility, and the market-cap change measures join the
longer momentum horizons.

Although there are 80 predictors, the average correlation matrix behaves like
about ten uncorrelated directions: its ten largest eigenvalues account for
roughly three quarters of the variance.

Between themes, the composites overlap more than their individual predictors
do, because averaging removes each predictor's own noise. Volatility and size
correlate 0.72 on average, and between 0.56 and 0.83 in every calendar year.
Momentum &amp; trend and size average 0.55. Other relationships change sign:
market correlation and volatility range from −0.51 to 0.37 across years.

Every theme ranks the target on average, but not in every period. Momentum
&amp; trend has an IC of 0.037 in 1998–2008 and 0.040 in 2009–2021, despite a
year of −0.060 in 2009. Short-term reversal fades from 0.021 to 0.004 across
the same split. Volatility and size strengthen, from about 0.02 to about
0.05, which makes them the two strongest themes after 2009. Market correlation
has a negative IC in 7 of the 11 years through 2008 and in only one year
after.

Overlap does not make a theme redundant. A correlation of 0.72 still leaves
about half of each composite's variance unexplained by the other, and that
part can carry its own information. So the question for a simple score is
which themes to include, and for a learned one, whether weights fitted on one
decade still suit the next.

## The fixed score
{: #a-fixed-weight-comparison }

My simple score uses three themes. Momentum and volatility are the strongest
over the full period and share some of their bet (0.36). Short positioning
brings a different one: it correlates 0.09 with momentum and 0.07 with
volatility. Size is also strong, but it correlates 0.72 with volatility and
0.55 with momentum, so a score that already holds those two carries much of
its bet; I leave it out to keep the rule to three themes. Equal weights also
cannot chase a decade, which matters given how much the strongest themes
changed in Figure 1.

Each theme receives one third of the score, split equally among its
predictors (Table 1). I call it the fixed score because its weights are set
by hand rather than fitted.

<table class="research-table settings-table benchmark-ingredients">
  <caption><strong>Table 1: The fixed score.</strong> Each theme receives one third of the weight, divided equally among its predictors. Horizons are trading sessions. Momentum and Defensive are narrower versions of the Momentum &amp; trend and Volatility themes; five of the twelve inputs are among the 80 predictors.</caption>
  <thead>
    <tr><th>Theme</th><th>What the score favors</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Momentum</th><td>Higher returns over 63, 126 and 252 sessions; higher price relative to its 126- and 252-session moving averages</td></tr>
    <tr><th scope="row">Defensive</th><td>Lower volatility over 21, 63 and 126 sessions; lower downside volatility over 63 and 126 sessions</td></tr>
    <tr><th scope="row">Short positioning</th><td>Lower short interest relative to daily volume, smoothed over 21 and 63 sessions</td></tr>
  </tbody>
</table>

The regressions learn the weights instead, on all 80 predictors. Against the
fixed score they change both the predictor set and the weights; OLS against
Ridge keeps the inputs the same and isolates regularization. I also refit
both on the fixed score's twelve inputs, to separate learning the weights
from changing the predictor set.

## OLS versus Ridge
{: #learning-the-combination }

Fitting the weights jointly makes each one conditional. The coefficient on
the 12-month return measures its relationship with the target holding the
other inputs fixed, including the neighbouring momentum horizons, and its sign
can differ from the 12-month return's own IC.

That is useful when two predictors differ in a meaningful way. For example,
$2x_1-1.8x_2=0.2x_1+1.8(x_1-x_2)$ combines a small common exposure with a
large weight on the difference between two signals. With related momentum
horizons, that difference may describe the shape of the trend. But if the two
horizons move closely together, the sample contains little variation in
their difference, and OLS can assign large, opposing coefficients that mostly
fit noise.

Ridge adds a penalty on the size of the coefficients:

$$
\min_{a,\,\boldsymbol\beta}\;\frac1n\sum_{i,t}\bigl(y_{i,t}-a-\mathbf z_{i,t}^\top\boldsymbol\beta\bigr)^2+c\lVert\boldsymbol\beta\rVert_2^2 ,
$$

where $\mathbf z_{i,t}$ holds stock $i$'s 80 predictor ranks on date $t$, $n$
is the number of stock-date rows and the intercept $a$ is unpenalized; $c=0$
gives OLS. The penalty shrinks the least-variable combinations of predictors
most ([appendix](#what-ridge-changes)). I fixed $c=0.01$ in advance rather
than tuning it: it at least halves the weight on any combination with a
variance of 0.01 or less, about 3% of one rank predictor's variance, and
barely touches the combinations that carry most of the variation. The fixed
score, predictor set, target, penalty and training scheme were all fixed
using data through 2021.

## Fitting through time
{: #from-predictions-to-portfolios }

I use an expanding window starting in January 1995. The first training
window contains 900 trading dates, and a 21-date gap lets the forward
20-session outcomes finish before predictions begin. I then refit every 600
dates, keeping the January 1995 start, so each refit adds history (Figure 2).
Until a long-window predictor has enough history, it takes its date-and-sector
mean. OLS and Ridge share the same twelve windows, with predictions from
September 1998. Within each window, I fit three models on interleaved dates
and average their predictions ([appendix](#sampling-the-training-dates)).

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/expanding-walk-forward" mobile="/assets/multiple-linear-regression/expanding-walk-forward_mobile" alt="Three expanding walk-forward fits share a January 1995 start. Training grows from 900 to 1500 to 2100 dates. Each training window is followed by a gap and a subsequent prediction block." version="2" %}
</div>

<p class="figure-caption"><strong>Figure 2: Expanding walk-forward.</strong> Each refit retains the earlier history and adds 600 training dates. The 21-date gap precedes each 600-date prediction block. Widths are schematic; the final prediction block can be shorter.</p>

I report results through December 2021 and for January 2022–May 2026
separately.

<aside class="research-note" markdown="1" id="portfolio-construction">
**How I evaluate the scores.** Every score goes through the same plain
portfolio rule. I buy the top 75 stocks and short the bottom 75, weight each
position by 20% divided by its past 60-session volatility (floored at 5%),
cap each stock at 4% and each side at 100% of capital, rebalance every three
weeks at the next close and charge 5 bp per dollar traded. I run three
rebalance schedules starting one week apart and average their statistics.
Because this rule lets each score take its own level of risk, I compare
scores on Sharpe rather than return, and report gross exposure, long plus
short positions relative to capital: a score that selects calmer stocks gets
larger positions. Traded notional is annual two-way trading divided by
capital. Portfolio construction itself is the subject of the
[optimization article](/quants/2026/08/29/portfolio-optimization.html).
</aside>

## Results
{: #prediction-quality-and-portfolio-results }

<table class="research-table comparison-table ic-summary-table portfolio-card-table">
  <caption><strong>Table 2: Cross-sectional ranking quality.</strong> Mean daily rank IC, its standard deviation and their unannualized ratio. Adjacent observations share overlapping 20-session outcomes; later IC ends on 28 April 2026, the last complete target date.</caption>
  <thead>
    <tr><th>Ranking</th><th>Mean daily IC</th><th>IC SD</th><th>IC IR</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="4">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Fixed score</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">OLS</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Ridge</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr class="period-heading"><th colspan="4">Later · January 2022–April 2026</th></tr>
    <tr><th scope="row">Fixed score</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">OLS</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Ridge</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
  </tbody>
</table>

[TBD: two or three sentences on Table 2 — whether the regressions rank better
than the fixed score in each period, and how OLS and Ridge compare.]

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 3: Net performance and trading.</strong> Mean statistics across three rebalance schedules, after 5 bp per dollar traded, with min–max Sharpe in parentheses. Return and volatility are annualized; beta is measured against the Russell 1000.</caption>
  <thead>
    <tr><th>Score</th><th>Net return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Market beta</th><th>Gross exposure</th><th>Traded notional / year</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="8">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Fixed score</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">OLS</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Ridge</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr class="period-heading"><th colspan="8">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Fixed score</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">OLS</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Ridge</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
  </tbody>
</table>

[TBD: Table 3 in two short paragraphs — where any Sharpe difference comes
from (return or volatility), whether it holds on each schedule and in both
periods, what it costs in trading, and Ridge against OLS. The cost estimate
excludes borrow, financing and market impact.]

<div class="research-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/performance-and-drawdowns" mobile="/assets/multiple-linear-regression/performance-and-drawdowns_mobile" alt="Net growth on a logarithmic scale with a shared drawdown panel below for the fixed score, OLS and Ridge" version="19" %}
</div>

<p class="figure-caption"><strong>Figure 3: Portfolio paths from the three scores.</strong> [TBD: rebuild as an interactive chart from the 80-predictor rerun.] The mean daily net P&amp;L of the three schedules, compounded into an index starting at <span class="mathjax-ignore">$1</span> (log scale), with drawdowns below.</p>

### Learning weights on the same inputs

How much of any difference comes from learning the weights? I refit OLS and
Ridge on exactly the fixed score's twelve predictors, keeping the target,
training windows, penalty and portfolio rules the same.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 4: The same twelve inputs, different weights.</strong> Mean statistics across the three rebalance schedules, with min–max Sharpe in parentheses; conventions match Table 3.</caption>
  <thead>
    <tr><th>Score</th><th>Net return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Market beta</th><th>Gross exposure</th><th>Traded notional / year</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="8">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Fixed score</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">OLS · 12</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Ridge · 12</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr class="period-heading"><th colspan="8">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Fixed score</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">OLS · 12</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Ridge · 12</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
  </tbody>
</table>

[TBD: compare Table 4 with Table 3 — how much of the difference appears with
the same twelve inputs and how much only with the 80 predictors.]

## What the model learned
{: #reading-the-predictors }

Figure 4 shows the ten largest average absolute Ridge weights. A positive
weight raises a stock's score as its rank on that predictor rises, holding
the other ranks fixed.

<div class="research-figure coefficient-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/top-coefficients" alt="Signed coefficients for the ten largest mean absolute Ridge weights across walk-forward refits" version="12" %}
</div>

<p class="figure-caption"><strong>Figure 4: The ten largest mean absolute Ridge coefficients, averaged across the three training subsamples at each refit.</strong> [TBD: rebuild from the 80-predictor fits.] Rows are selected using the full coefficient history.</p>

Because each weight is conditional, it can disagree with the predictor's own
IC. Figure 1 shows where to expect that: inside Momentum &amp; trend, short
and long horizons point in opposite directions, so a linear model can learn a
contrast between them rather than one sign for the whole theme.
[TBD: which contrasts the 80-predictor fit learns, whether their signs
persist across the twelve refits, and whether the short-horizon terms explain
any extra trading.]

These are ten terms among 80, and several describe similar characteristics,
so a large coefficient can partly offset another. To establish which themes
improve the portfolio, I would need to remove them and refit.

## Where this leaves me

The predictors tell a clear story before any model is fitted: seven themes
that all rank the target on average, with volatility and size overlapping
heavily and the strongest themes changing between decades.
[TBD: the takeaway from Tables 2–4 — whether a simple theme-based score is
hard to beat, how much learning the weights adds on its own, how much comes
from the broader predictor set, and at what cost in trading.]

In the [optimization article](/quants/2026/08/29/portfolio-optimization.html)
I take more control over portfolio risk and exposures, starting from the
earlier 144-predictor Ridge ranking.

## Appendix

### What Ridge changes
{: #what-ridge-changes }

[TBD: rerun on the 80-predictor fits — how much Ridge reduces coefficient
size and movement between refits, the daily ranking correlation between OLS
and Ridge, and how many of the 150 daily candidates differ.]

To see where Ridge acts, consider combinations of the predictors that vary
together. Let $X_c$ denote the training inputs centered on their column
means. The eigenvectors $$\mathbf v_j$$ of $$G=X_c^\top X_c/n$$ identify those
combinations, and each eigenvalue $$\lambda_j$$ measures its variance. For one
fitted model, Ridge scales the OLS coefficient in each direction by

$$
\widehat\theta_{j,c}
=\frac{\lambda_j}{\lambda_j+c}\widehat\theta_{j,0},
\qquad \widehat\theta_{j,c}=\mathbf v_j^\top\widehat{\boldsymbol\beta}_c,
\quad \lambda_j>0.
$$

The smaller the variance, the stronger the shrinkage; a direction with
$\lambda_j=c$ is halved. Hastie develops this interpretation in his Ridge
review.[^hastie] [TBD: across the twelve training windows and three date
subsamples, how many of the 80 eigenvalues lie below 0.1 and below 0.01, and
their share of predictor variance.]

A coefficient change matters for scores in proportion to the variance of the
combination it moves along. With $$\Delta\boldsymbol\beta$$ the Ridge minus
OLS coefficients,

$$
\frac{\lVert X_c\Delta\boldsymbol\beta\rVert_2^2}{n}
=\sum_j\lambda_j(\mathbf v_j^\top\Delta\boldsymbol\beta)^2 .
$$

[TBD: the share of the squared coefficient difference in the least-variable
directions and their share of predictor variance, averaged across refits.]

### Sampling the training dates
{: #sampling-the-training-dates }

Within each training window, I fit three models: one gets dates 1, 4, 7, …;
the next gets 2, 5, 8, …; and the third gets 3, 6, 9, … (Figure 5). Each
receives complete cross-sections from its dates, and I average their
predictions. This spreads out each model's observations while using all
dates collectively, although their forward targets still overlap.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/date-sampling" mobile="/assets/multiple-linear-regression/date-sampling_mobile" alt="Three models within one training window: model 1 uses dates 1, 4, 7; model 2 uses 2, 5, 8; model 3 uses 3, 6, 9. Their prediction scores are averaged." version="2" %}
</div>

<p class="figure-caption"><strong>Figure 5: Interleaved training dates.</strong> The first nine training dates illustrate the three offsets. Each selected date contributes a full cross-section.</p>

I give each training row equal weight, so dates with more usable stocks
contribute more to the loss. The row count overstates the independent
information: adjacent targets share 19 of their 20 daily returns, predictors
persist, and stocks share market and sector shocks.

### Ranking details
{: #ranking-details }

For a group of $N$ distinct observations on one date, the rank
transformation is

$$
z_i=2\frac{\operatorname{rank}(x_i)}{N}-1 \in (-1,1].
$$

A stock's momentum can rise from −2% to +10% while its rank stays unchanged.
The cross-sectional distributions stay approximately uniform over time, which
keeps scales comparable when pooling history[^rank-convention] and limits the
influence of extreme predictor and target values. Correlations between
predictors, and their relationship with the target, can still change, as
Figure 1 shows.

The cost is losing absolute levels and distances. Adjacent stocks receive the
same rank gap whether their momentum differs by one or twenty percentage
points, and those discarded magnitudes may contain predictive information.
Predictors are ranked across the universe while targets are ranked within
sectors, so a high momentum rank can pair with middling performance among
sector peers, and a portfolio that selects across sectors can still take
sector exposures.

[^predictor-set]: I started from a library of 144 predictors and use a core-plus-standard set of 79, chosen on data through 2021 for its stability across five-year blocks in a separate tree-model comparison, plus 21-day loss frequency as a short-term candidate. The set leaves out near copies, weak predictors and some distinct variants.
[^theme-references]: Momentum: Jegadeesh and Titman, *Returns to Buying Winners and Selling Losers*, Journal of Finance, 1993; Da, Gurun and Warachka, *Frog in the Pan*, Review of Financial Studies, 2014. Reversal: Jegadeesh, *Evidence of Predictable Behavior of Security Returns*, Journal of Finance, 1990; Lehmann, *Fads, Martingales, and Market Efficiency*, Quarterly Journal of Economics, 1990. Volatility: Ang, Hodrick, Xing and Zhang, *The Cross-Section of Volatility and Expected Returns*, Journal of Finance, 2006; Baker, Bradley and Wurgler, *Benchmarks as Limits to Arbitrage*, Financial Analysts Journal, 2011; Bali, Cakici and Whitelaw, *Maxing Out*, Journal of Financial Economics, 2011. Trading volume: Lee and Swaminathan, *Price Momentum and Trading Volume*, Journal of Finance, 2000. Illiquidity: Amihud, *Illiquidity and Stock Returns*, Journal of Financial Markets, 2002. Market correlation: Frazzini and Pedersen, *Betting Against Beta*, Journal of Financial Economics, 2014. Short positioning: Boehmer, Jones and Zhang, *Which Shorts Are Informed?*, Journal of Finance, 2008; Hong, Li, Ni, Scheinkman and Yan, *Days to Cover and Stock Returns*, NBER working paper, 2015.
[^hastie]: Hastie, [*Ridge Regularization: An Essential Concept in Data Science*](https://arxiv.org/abs/2006.00371), Technometrics, 2020, Sections 2–3.
[^rank-convention]: Gu, Kelly and Xiu also rank stock characteristics in [*Empirical Asset Pricing via Machine Learning*](https://dachxiu.chicagobooth.edu/download/ML_BKP.pdf), Review of Financial Studies, 2020.
