---
layout: post
interactive_charts: true
title: "Combining Multiple Predictors: The Linear Case"
description: "How 80 overlapping stock predictors relate, and whether learning their weights with OLS or Ridge beats equal weights."
date: 2025-02-09
last_modified_at: 2026-09-28
categories: ["Signals"]
article_label: Signals · Linear and Ridge regression
permalink: /quants/2025/02/09/multiple-linear-regression.html
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/systematic-equity-research
---

<link rel="stylesheet" href="/assets/css/regression-article.css?v=10">

In the [low-volatility article](/quant/2024/12/15/low-volatility-factor.html),
I selected stocks using one characteristic and examined how position sizing
changed the portfolio. Here I want to bring more information into that
selection. Alongside volatility, I can describe a stock by its momentum,
liquidity, size and short positioning, among other characteristics.

With one characteristic, the ranking is the selection rule. With several, I
need weights, and the predictors overlap. A stock with strong momentum often
also has low volatility, and several momentum horizons repeat much of the same
information. Each predictor's weight has to reflect what the others already
say.

Before fitting anything, I want to understand the predictors: what they
measure, how much they overlap and whether their usefulness is stable. Then I
compare equal weights with weights learned by ordinary least squares (OLS) and
Ridge, judged by the Sharpe ratio of the same long–short portfolio.

## Setup
{: #what-i-ask-the-model-to-predict }

The universe is point-in-time Russell 1000 membership, excluding stocks below
five dollars, announced merger targets and duplicate share classes.

The target is each stock's forward 20-session Sharpe ratio: mean daily return
divided by daily return volatility over the next 20 sessions, roughly a
trading month. I use a
risk-adjusted target because the portfolio sizes positions by inverse
volatility, so return per unit of risk is what it earns. Twenty sessions is
short enough for predictors built from prices and trading activity, many of
which change within weeks, and close to the portfolio's three-week rebalance.
I rank the target within each date and sector, so that the weights are fitted
to picking stocks among sector peers rather than to sector swings, and map the
ranks into $(-1,1]$. The portfolio still selects across sectors, so it can
take sector tilts the target never rewarded.

The choice matters for what the model learns. For a given positive return,
lower volatility raises the target. The fitted scores strongly favour
lower-volatility stocks, as the decile portfolios below show.

Each predictor is ranked across the whole universe on each date and mapped in
the same way. Ranking puts different units on one bounded scale and limits the
influence of outliers, at the cost of discarding magnitudes. Throughout, the
information coefficient (IC) is the cross-sectional Spearman rank correlation
between a predictor, or a score, and the target on one date.

## The predictors
{: #the-predictors }

I use a pool of 80 well-known predictors, mostly built from prices and trading
activity, in seven themes. Each theme comes with an economic story for why it
might rank the target (references at the end); where the data here disagree
with the story, I say so.

<div class="theme-cards" markdown="0">
  <details class="theme-card">
    <summary>Momentum &amp; trend <span>33 predictors</span></summary>
    <p class="theme-measures">Returns and risk-adjusted returns over 3–12 months, price relative to moving averages and to highs and lows, how persistently the price stayed above its 200-day average, and the share of losing days over up to three years.</p>
    <p>Stocks that did well over the past year have tended to keep doing well for a while, which is usually read as investors underreacting to news. Momentum built from many small moves has persisted longer than momentum from a few jumps. The theme also holds short-horizon position measures, such as price relative to its 5-day low, which work the other way.</p>
      <details class="predictor-list" data-theme="0"><summary>Predictors</summary><ul></ul></details>
  </details>
  <details class="theme-card">
    <summary>Short-term reversal <span>4 predictors</span></summary>
    <p class="theme-measures">Returns over the last 1–21 sessions.</p>
    <p>Over days to a month, prices partly reverse. A common reading is compensation for providing liquidity: an investor who has to sell quickly pushes the price below fair value, and the buyer earns the recovery.</p>
      <details class="predictor-list" data-theme="1"><summary>Predictors</summary><ul></ul></details>
  </details>
  <details class="theme-card">
    <summary>Volatility <span>12 predictors</span></summary>
    <p class="theme-measures">Close-to-close, downside and upside volatility and average true range, over 5–252 sessions.</p>
    <p>Low-volatility stocks have earned about as much as volatile ones with far less risk. Investors who cannot or will not use leverage bid up high-beta stocks, and some pay for lottery-like payoffs.</p>
      <details class="predictor-list" data-theme="2"><summary>Predictors</summary><ul></ul></details>
  </details>
  <details class="theme-card">
    <summary>Size <span>10 predictors</span></summary>
    <p class="theme-measures">Log market capitalization, its variability (the standard deviation of log market cap over a window), and its change and position relative to recent highs and lows.</p>
    <p>The small-cap premium lives among much smaller firms and has been weak since the 1980s unless one controls for quality. Within the Russell 1000, size means large versus mega cap, and larger names rank higher on the Sharpe target because their volatility is lower. Here size is mostly a low-risk measure; its variability measures behave like volatility and its change measures like momentum.</p>
      <details class="predictor-list" data-theme="3"><summary>Predictors</summary><ul></ul></details>
  </details>
  <details class="theme-card">
    <summary>Liquidity &amp; volume <span>10 predictors</span></summary>
    <p class="theme-measures">Share turnover, Amihud illiquidity (absolute return per dollar traded), variability of trading volume, volume relative to its recent maximum, and the correlation between price and volume changes.</p>
    <p>Heavily traded stocks have tended to earn less than lightly traded ones. Illiquid stocks should compensate their holders, but here Amihud illiquidity points the other way: within the Russell 1000 it mostly marks the smaller names, which rank lower on the target.</p>
      <details class="predictor-list" data-theme="4"><summary>Predictors</summary><ul></ul></details>
  </details>
  <details class="theme-card">
    <summary>Market correlation <span>2 predictors</span></summary>
    <p class="theme-measures">Correlation of the stock's daily returns with the market over one and two years.</p>
    <p>Beta is correlation times relative volatility. Leverage-constrained investors bid up high-beta stocks for either reason, so high-correlation stocks should earn less even at the same volatility. The data here match this story only before 2009, and I have no convincing explanation for the reversal, which makes this the least well-founded theme.</p>
      <details class="predictor-list" data-theme="5"><summary>Predictors</summary><ul></ul></details>
  </details>
  <details class="theme-card">
    <summary>Short positioning <span>9 predictors</span></summary>
    <p class="theme-measures">Short interest relative to daily volume, its variability, and changes in short interest.</p>
    <p>Short sellers are often well informed, and heavily shorted stocks have tended to underperform. Short interest relative to volume, often called days to cover, also measures crowding: how long the shorts would need to buy back.</p>
      <details class="predictor-list" data-theme="6"><summary>Predictors</summary><ul></ul></details>
  </details>
</div>

## How the predictors overlap
{: #correlation-structure }

On every fifth session from 1998 through 2021, once every predictor has enough
history, I compute the rank correlation between every pair of predictors and
between each predictor and the target. First I flip the sign of each predictor
whose average IC is negative. Lower volatility predicts a higher target, for
example, so I use negative volatility. After the flip, a positive correlation
means two predictors favour the same stocks.

To follow whole themes, I also combine each theme into one composite: the
equal-weight sum of its signed, standardized predictor ranks. Figure 1 lets
you pick a period and switch between all 80 predictors and the seven theme
composites. The predictors are ordered by a dendrogram, which joins the most
similar predictors first, and the colour strip shows each one's theme. The
lower panel adds up each composite's IC with the target, sampled every fifth
session, so a steadily rising line is a theme that kept ranking stocks well.

{% include predictor-structure-explorer.html %}

<noscript markdown="0">
  <div class="research-figure responsive-figure">
    {% include theme-svg-figure.html base="/assets/multiple-linear-regression/predictor-correlation" mobile="/assets/multiple-linear-regression/predictor-correlation_mobile" alt="Heatmap of average rank correlations between the 80 predictors, grouped into seven theme blocks." version="3" %}
  </div>
  <div class="research-figure responsive-figure">
    {% include theme-svg-figure.html base="/assets/multiple-linear-regression/theme-ic-by-year" mobile="/assets/multiple-linear-regression/theme-ic-by-year_mobile" alt="Heatmap of each theme composite's mean IC by year from 1998 to 2021." version="3" %}
  </div>
</noscript>

<p class="figure-caption"><strong>Figure 1: How the predictors relate to each other and to the target.</strong> Average rank correlation over the selected period, with each predictor signed so that its 1998–2021 average IC is positive; blue pairs favour the same stocks. The dendrogram (average linkage on 1 − |ρ|) is fitted once on 1998–2021 so that periods stay comparable. The lower panel is each theme composite's cumulative IC; hover for its mean over the period. Zooming the lower panel recalculates its cumulative IC and mean; the year controls set the correlation window.</p>

Over the full period, volatility is the most coherent theme: its predictors
correlate 0.71 on average. Momentum &amp; trend and size are the least
coherent, at 0.15. Momentum &amp; trend spans horizons from days to three
years, and 43% of its signed pairs are negatively correlated: after the flip,
trading well above the 10-day average counts against a stock, while a strong
12-month return counts for it. Although there
are 80 predictors, ten principal components carry nearly three quarters of
their variance.

Between themes, the composites overlap more than their individual predictors
do, because averaging removes each predictor's idiosyncratic part. Volatility
and size correlate 0.72 on average, and between 0.56 and 0.83 in every calendar
year, partly because the size theme's variability measures are volatility
measures. Momentum &amp; trend and
size average 0.55. Other relationships change sign: market correlation and
volatility range from −0.51 to 0.37 across years.

Every theme ranks the target on average, but not in every period. Momentum
&amp; trend has an IC of 0.037 in 1998–2008 and 0.040 in 2009–2021, despite a
year of −0.060 in 2009. Short-term reversal fades from 0.021 to 0.004 across
the same split. Volatility and size strengthen, from about 0.02 to about 0.05,
which makes them the two strongest themes after 2009. Market correlation has a
negative IC in 7 of the 11 years through 2008 and in only one year after.

A learned combination therefore has to carry weights fitted in one decade into
the next.

## Three ways to combine them
{: #combining-them }

The simplest combination gives every predictor the same weight, 1/80. The only thing this *equal-weight* score learns from data is a
direction: each predictor enters with the sign of its correlation with the
target in the training window, so lower volatility counts in a stock's favour
because it did so in the past. Momentum &amp; trend then carries 33 of the 80
weights simply because it has the most predictors.

The regressions learn the weights instead. Fitting them jointly makes each one
conditional: the coefficient on the 12-month return measures its relationship
with the target holding the other inputs fixed, including the neighbouring
momentum horizons, and its sign can differ from the 12-month return's own IC.
That is useful when two predictors differ in a meaningful way. For example,
$2x_1-1.8x_2=0.2x_1+1.8(x_1-x_2)$ combines a small common exposure with a
large weight on the difference between two signals. But if the two move
closely together, the sample contains little variation in their difference,
and OLS can assign large, opposing coefficients that mostly fit noise.

Ridge adds a penalty on the size of the coefficients:

$$
\min_{a,\,\boldsymbol\beta}\;\frac1n\sum_{i,t}\bigl(y_{i,t}-a-\mathbf z_{i,t}^\top\boldsymbol\beta\bigr)^2+c\lVert\boldsymbol\beta\rVert_2^2 ,
$$

where $\mathbf z_{i,t}$ holds stock $i$'s 80 predictor ranks on date $t$, $n$
is the number of stock-date rows and the intercept $a$ is unpenalized; $c=0$
gives OLS. Ridge shrinks most along directions in which the predictors barely
vary, such as the difference between two nearly identical momentum horizons
([Hastie](https://arxiv.org/abs/2006.00371) explains this view well). As $c$ grows, each coefficient becomes proportional
to its predictor's own covariance with the target, so a heavily penalized Ridge
weights each predictor by its own correlation with the target, close to the
equal-weight score.

## Fitting through time
{: #from-predictions-to-portfolios }

I refit the weights on an expanding window that starts in January 1995, so
each refit adds history (Figure 2). A rolling window would adapt faster to the
shifts in Figure 1, but with less data per fit its weights would move more
between refits; I prefer stable weights.[^fitting]

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/expanding-walk-forward" mobile="/assets/multiple-linear-regression/expanding-walk-forward_mobile" alt="Twelve refits on a 1995–2026 time axis. Every training window starts in January 1995 and grows with each refit; each prediction block runs until the next refit. Predictions from 2022 onward fall in the shaded later period." version="7" %}
</div>

<p class="figure-caption"><strong>Figure 2: Expanding walk-forward.</strong> Each row is one refit. Training always starts in January 1995 and grows with each refit; each prediction block runs until the next refit. The shaded area is the later period; the month-long gap between training and predictions is too short to see at this scale.</p>

Every prediction is made by a model that has not seen that date. I report two
periods: development, September 1998–December 2021, and later, January
2022–May 2026. The later period is short, about 54 non-overlapping 20-session
windows.

Every score goes through the same volatility-scaled rule (Table 1), the low-volatility article's inverse-volatility sizing with 75 names per side. Because
volatility scaling lets each score take its own level of risk, I compare
scores on Sharpe rather than return. Portfolio construction itself is the
subject of the [optimizer
article](/quants/2026/08/29/portfolio-optimization.html), where the same Ridge
scores reach a Sharpe of 1.32 through 2021 and 0.87 after.

<table class="research-table settings-table" id="portfolio-construction">
  <caption><strong>Table 1: The portfolio rule.</strong> Identical for every score.</caption>
  <tbody>
    <tr><th scope="row">Holdings</th><td>Long the top 75 stocks, short the bottom 75</td></tr>
    <tr><th scope="row">Position size</th><td>20% divided by the stock's past 60-session volatility (floored at 5%); at most 4% per stock and 100% of capital per side</td></tr>
    <tr><th scope="row">Rebalancing</th><td>Every three weeks at the next close, on three schedules that start one week apart. Tables report the mean of each schedule's statistics; the bootstrap holds the three schedules together at equal notional.</td></tr>
    <tr><th scope="row">Costs</th><td>5 bp per dollar traded</td></tr>
  </tbody>
</table>

## Choosing the penalty
{: #choosing-the-penalty }

Up to $c=0.1$, development IC and Sharpe barely move (Table 2), even though
the coefficients shrink to less than half their OLS size; from $c=1$, Ridge
drifts toward the equal-weight score, its volatility rising toward 9% and its
Sharpe falling.

<table class="research-table comparison-table">
  <caption><strong>Table 2: Ridge penalty on development data.</strong> September 1998–December 2021, mean of three schedules, after costs. $c=0$ is OLS. IC IR is the mean daily IC divided by its standard deviation, unannualized. Coefficient size is the average length of the coefficient vector across refits, relative to OLS.</caption>
  <thead>
    <tr><th>Penalty $c$</th><th>Coefficient size</th><th>Mean daily IC</th><th>IC IR</th><th>Volatility</th><th>Sharpe</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">0</th><td>100%</td><td>0.0466</td><td>0.558</td><td>7.37%</td><td>0.99</td></tr>
    <tr><th scope="row">0.01</th><td>82%</td><td>0.0472</td><td>0.557</td><td>7.50%</td><td>0.99</td></tr>
    <tr class="selected-rule"><th scope="row">0.1</th><td>43%</td><td>0.0481</td><td>0.534</td><td>8.05%</td><td>0.98</td></tr>
    <tr><th scope="row">1</th><td>16%</td><td>0.0473</td><td>0.483</td><td>8.78%</td><td>0.91</td></tr>
    <tr><th scope="row">10</th><td>4%</td><td>0.0466</td><td>0.455</td><td>9.23%</td><td>0.82</td></tr>
    <tr><th scope="row">100</th><td>0.5%</td><td>0.0465</td><td>0.448</td><td>9.37%</td><td>0.78</td></tr>
  </tbody>
</table>

I use $c=0.1$, which has the highest development IC, the most direct measure
of how well a score ranks the target; its Sharpe is within 0.01 of the best.

## Results
{: #prediction-quality-and-portfolio-results }

<table class="research-table comparison-table ic-summary-table portfolio-card-table">
  <caption><strong>Table 3: Cross-sectional ranking quality.</strong> Mean daily rank IC, its standard deviation and their unannualized ratio. Adjacent observations share overlapping 20-session outcomes; later IC ends on 28 April 2026, the last complete target date.</caption>
  <thead>
    <tr><th>Score</th><th>Mean daily IC</th><th>IC SD</th><th>IC IR</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="4">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Equal-weight</th><td>0.0467</td><td>0.1049</td><td>0.445</td></tr>
    <tr><th scope="row">OLS</th><td>0.0466</td><td>0.0834</td><td>0.558</td></tr>
    <tr><th scope="row">Ridge</th><td>0.0481</td><td>0.0900</td><td>0.534</td></tr>
    <tr class="period-heading"><th colspan="4">Later · January 2022–April 2026</th></tr>
    <tr><th scope="row">Equal-weight</th><td>0.0384</td><td>0.1337</td><td>0.287</td></tr>
    <tr><th scope="row">OLS</th><td>0.0412</td><td>0.1087</td><td>0.379</td></tr>
    <tr><th scope="row">Ridge</th><td>0.0422</td><td>0.1218</td><td>0.346</td></tr>
  </tbody>
</table>

The regressions rank stocks more steadily than equal weights (Table 3).
Through 2021 Ridge's mean IC, 0.048, is close to the equal-weight score's
0.047, but its day-to-day variation is smaller, so the IC IR is 0.53 against
0.45. After 2021 the gap in mean IC widens a little, 0.042 against 0.038.

Figure 3 first shows how the Ridge and equal-weight scores order return and
volatility, using equal-weighted decile portfolios before costs.

{% include blog-chart.html chart="deciles" source="/assets/multiple-linear-regression/deciles.json" label="Return, volatility and Sharpe across score deciles" %}

<p class="figure-caption"><strong>Figure 3: Decile portfolios of the scores.</strong> Compounded annual return of equal-weighted portfolios of the stocks in each score decile, with each decile's annualized volatility and Sharpe ratio in the expandable statistics. Portfolios trade at the next close and are held until the next rebalance, averaged over the three schedules; before costs. Decile 10 holds the highest scores.</p>

Through 2021 Ridge's deciles climb from about 3% a year to 16%, and the top
decile's Sharpe ratio is 0.90 against 0.26 at the bottom. Equal weights reach
almost the same top-decile Sharpe, 0.89, with less return and less volatility.
For both scores volatility falls steadily from around 30% in decile 1 to 16–18%
in decile 10: as the target suggested, much of what these scores learn is a
volatility sort. After 2021 the return ordering almost disappears above decile
3, and most of the spread comes from the bottom decile. The volatility sort
remains. Ridge's daily returns correlate 0.62 with the volatility-scaled
portfolio from the [low-volatility article](/quant/2024/12/15/low-volatility-factor.html)
through 2021 and 0.78 after.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 4: Net performance and trading.</strong> Mean statistics across three rebalance schedules, after 5 bp per dollar traded, with min–max Sharpe in parentheses. Returns are compounded annual returns and volatility is annualized; Sharpe uses a zero cash rate, beta is measured against the Russell 1000, and two-way turnover is mean daily traded notional divided by capital, multiplied by 252.</caption>
  <thead>
    <tr><th>Score</th><th>Net return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Market beta</th><th>Gross exposure</th><th>Two-way turnover / year</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="8">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Equal-weight</th><td>7.35%</td><td>9.20%</td><td>0.82<br><small>(0.74–0.93)</small></td><td>−24.9%</td><td>0.11</td><td>134%</td><td>25.9×</td></tr>
    <tr><th scope="row">OLS</th><td>7.29%</td><td>7.37%</td><td>0.99<br><small>(0.90–1.05)</small></td><td>−18.7%</td><td>0.09</td><td>139%</td><td>29.0×</td></tr>
    <tr><th scope="row">Ridge</th><td>7.88%</td><td>8.05%</td><td>0.98<br><small>(0.89–1.16)</small></td><td>−19.8%</td><td>0.10</td><td>138%</td><td>28.4×</td></tr>
    <tr class="period-heading"><th colspan="8">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Equal-weight</th><td>5.50%</td><td>11.44%</td><td>0.52<br><small>(0.45–0.61)</small></td><td>−10.7%</td><td>0.07</td><td>131%</td><td>21.4×</td></tr>
    <tr><th scope="row">OLS</th><td>6.13%</td><td>9.18%</td><td>0.69<br><small>(0.67–0.73)</small></td><td>−8.5%</td><td>0.06</td><td>134%</td><td>25.9×</td></tr>
    <tr><th scope="row">Ridge</th><td>7.12%</td><td>10.16%</td><td>0.73<br><small>(0.67–0.83)</small></td><td>−9.4%</td><td>0.07</td><td>132%</td><td>24.4×</td></tr>
  </tbody>
</table>

Through 2021 learning the weights pays (Table 4): Ridge's Sharpe is 0.98
against 0.82 for equal weights, with a higher return, lower volatility and a
shallower drawdown, and OLS does about as well. The learned scores trade a
little more, 28× a year against 26×, and Ridge stays ahead of equal weights up
to costs of about 28 bp per dollar traded (43 bp after 2021), against the 5 bp
charged here; borrow, financing and market impact are excluded. Both portfolios
are net long in dollars, by 35–50% of capital through 2021, because volatility
scaling gives the lower-volatility long side larger positions; market beta
stays near 0.1.

After 2021 both Sharpe ratios fall, but the gap holds: Ridge's Sharpe is 0.73
against 0.52, with a higher return and lower volatility. Ridge's return falls
from 7.9% to 7.1% a year; its volatility rises from 8% to 10%. A block bootstrap of daily
returns, averaged across the three schedules, puts Ridge's Sharpe advantage at
about 0.2 in both periods, with 95% intervals from roughly zero to 0.4. Figure
4 shows the two paths.

{% include blog-chart.html chart="performance" source="/assets/multiple-linear-regression/performance.json" label="Ridge and equal-weight growth and drawdowns" %}

<p class="figure-caption"><strong>Figure 4: Portfolio paths of the equal-weight and Ridge scores.</strong> Mean daily net P&amp;L of the three schedules on common dates, compounded (log scale), with drawdowns below; the dotted line marks the start of the later period. Each portfolio keeps its own risk level; Table 4 gives the risk-adjusted comparison.</p>

Both scores lean toward larger stocks, because within the Russell 1000 larger
mostly means lower volatility. Through 2021 the stocks Ridge selects for the
long side sit on average at the 62nd market-cap percentile and its shorts at
the 31st; equal weights lean further, to the 68th and 31st, and both tilts
widen after 2021. The tilt is common to both scores, so it isn't Ridge's edge,
and whether to keep it is a portfolio-construction question.

## What Ridge learned
{: #reading-the-predictors }

Figure 5 initially shows the Ridge weights at each refit for the ten predictors with the
largest mean absolute weight; Explore lets you choose from all 80. A
positive weight raises a stock's score as its rank on that predictor rises,
holding the other ranks fixed.

{% include blog-chart.html chart="coefficients" source="/assets/multiple-linear-regression/coefficients.json" label="Ridge coefficients by refit, with selectable predictors" %}

<p class="figure-caption"><strong>Figure 5: Ridge coefficients by refit.</strong> The ten largest by mean absolute coefficient are shown by default. Each refit averages the three interleaved training fits; the year is the start of its prediction block. Rows keep their magnitude ranking; hover for each predictor's full definition.</p>

The largest weight is negative, on the 10/21-day MACD, a short-horizon trend
measure whose own IC is close to zero. Positive weights on the
126-day Sharpe ratio and the 12-month return favour long, steady trends, so
together these weights lean against the latest spurt, the same contrast
between short and long horizons that Figure 1 shows inside Momentum &amp;
trend. Days to cover, Amihud illiquidity and 5-day average true range get
negative weights, as their own ICs suggest. Share turnover and two-year
market-cap variability get positive weights although their own ICs are
negative: holding correlated neighbours fixed, their conditional effect
differs from their effect alone.

All ten keep their sign at every refit, but most shrink as the training
history grows: the 12-month return's weight falls from 0.015 at the first
refit to 0.003 at the last, and Amihud illiquidity's from −0.022 to −0.008.
Momentum &amp; trend takes about 45% of the absolute weight, a little more
than its 41% under equal weights. Ridge's score also changes faster: its rank
correlation with itself 15 sessions later is 0.67 through 2021, against 0.76
for equal weights, which is why it trades more.

## What learning the weights buys

Fitting the weights jointly beats giving every predictor 1/80. Ridge's Sharpe
is 0.16 higher than the equal-weight score's through 2021 and 0.21 higher
after, for a little more trading. The gain comes from the joint fit, not the
penalty: OLS does as well, and a heavy penalty pushes Ridge back toward equal
weights.

Much of what both scores learn is the low-volatility effect. The Sharpe target
asks for it, the deciles sort volatility more cleanly than return, and both
scores lean toward larger stocks.

OLS and lightly penalized Ridge perform similarly here. I keep the light
penalty to shrink unstable coefficient combinations, without a demonstrated
Sharpe advantage over OLS. I treat the ranking's lean toward large,
low-volatility stocks as an exposure to manage rather than as skill.

## References

- **Momentum:** Jegadeesh and Titman (1993), *Returns to Buying Winners and Selling Losers*; Da, Gurun and Warachka (2014), *Frog in the Pan*.
- **Reversal:** Jegadeesh (1990), *Evidence of Predictable Behavior of Security Returns*; Lehmann (1990), *Fads, Martingales, and Market Efficiency*.
- **Volatility:** Ang, Hodrick, Xing and Zhang (2006), *The Cross-Section of Volatility and Expected Returns*; Baker, Bradley and Wurgler (2011), *Benchmarks as Limits to Arbitrage*; Bali, Cakici and Whitelaw (2011), *Maxing Out*.
- **Size:** Banz (1981), *The Relationship Between Return and Market Value of Common Stocks*; Asness et al. (2018), *Size Matters, If You Control Your Junk*.
- **Liquidity and volume:** Amihud (2002), *Illiquidity and Stock Returns*; Lee and Swaminathan (2000), *Price Momentum and Trading Volume*.
- **Market correlation:** Frazzini and Pedersen (2014), *Betting Against Beta*; Asness et al. (2020), *Betting Against Correlation*.
- **Short positioning:** Boehmer, Jones and Zhang (2008), *Which Shorts Are Informed?*; Hong et al. (2015), *Days to Cover and Stock Returns*.

[^fitting]: I refit about every two and a half years, starting from three and a half years of history, with a one-month gap before each prediction block. Each fit averages three models trained on interleaved dates, and a missing predictor value takes its date-and-sector mean.
