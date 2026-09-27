---
layout: post
title: "Combining Multiple Predictors: The Linear Case"
description: "How 80 overlapping stock predictors relate, and whether learning their weights with OLS or Ridge beats equal weights."
date: 2025-02-09
last_modified_at: 2026-09-27
categories: ["Signals"]
article_label: Signals · Linear and Ridge regression
permalink: /quants/2025/02/09/multiple-linear-regression.html
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/systematic-equity-research
---

<link rel="stylesheet" href="/assets/css/regression-article.css?v=9">

In the [low-volatility article](/quant/2024/12/15/low-volatility-factor.html),
I selected stocks using one characteristic and examined how position sizing
changed the portfolio. Here I want to bring more information into that
selection. Alongside volatility, I can describe a stock by its momentum,
liquidity, size and short positioning.

With one characteristic, the ranking is the selection rule. With several, I
need weights, and the predictors overlap. A stock with strong momentum often
also has low volatility, and several momentum horizons repeat much of the same
information. How much weight should each predictor receive, given what the
others already tell me?

Before fitting anything, I want to understand the predictors: what they
measure, how much they overlap and whether their usefulness is stable. Then I
compare equal weights with weights learned by ordinary least squares (OLS) and
Ridge.

## Setup
{: #what-i-ask-the-model-to-predict }

The universe is point-in-time Russell 1000 membership, excluding stocks below
five dollars, announced merger targets and duplicate share classes.

The target is each stock's forward 20-session Sharpe ratio: mean daily return
divided by daily return volatility over the next 20 sessions, roughly a
trading month. Other targets would be reasonable too, such as the raw forward
return, a longer horizon or a return net of market and sector moves. I use a
risk-adjusted target because the portfolio sizes positions by inverse
volatility, so return per unit of risk is what it earns. Twenty sessions is
short enough for predictors built from prices and trading activity, many of
which change within weeks, and close to the portfolio's three-week rebalance.
I rank the target within each date and sector, so that the weights are fitted
to picking stocks among sector peers rather than to sector swings, and map the
ranks into $(-1,1]$. The portfolio still selects across sectors, so it can
take sector tilts the target never rewarded.

The choice has a consequence worth keeping in mind. Future volatility is far
easier to forecast than future return, and lower volatility alone raises a
Sharpe ratio, so a model trained on this target will lean toward calmer
stocks. The decile portfolios in the results show how strongly.

Each predictor is ranked across the whole universe on each date and mapped in
the same way. Ranking puts different units on one bounded scale and limits the
influence of outliers, at the cost of discarding magnitudes. Throughout, the
information coefficient (IC) is the cross-sectional Spearman rank correlation
between a predictor, or a score, and the target on one date.

## The predictors
{: #the-predictors }

I use a pool of 80 well-known predictors, mostly built from prices and trading
activity, in seven themes. Each theme comes with an economic story for why it
might rank the target;[^theme-references] where the data here disagree with
the story, I say so.

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
    <p>Low-volatility stocks have earned about as much as volatile ones with far less risk. Investors who cannot or will not use leverage bid up high-beta stocks, and some pay for lottery-like payoffs.</p>
  </section>
  <section class="theme-card" style="--theme-color: var(--theme-4)">
    <h3>Size <span>10 predictors</span></h3>
    <p class="theme-measures">Log market capitalization, its variability (the standard deviation of log market cap over a window), and its change and position relative to recent highs and lows.</p>
    <p>The small-cap premium is a return effect among much smaller firms, and it has been weak since the 1980s unless one also controls for quality. Every stock here is in the Russell 1000, so the level means large versus mega cap. On forward returns the larger names earned slightly less, but they rank higher on the Sharpe target because they are much calmer. Here size is mostly a low-risk measure, so it belongs in the pool for the same reason as volatility; its variability measures behave like volatility and its change measures like momentum.</p>
  </section>
  <section class="theme-card" style="--theme-color: var(--theme-5)">
    <h3>Liquidity &amp; volume <span>10 predictors</span></h3>
    <p class="theme-measures">Share turnover, Amihud illiquidity (absolute return per dollar traded), variability of trading volume, volume relative to its recent maximum, and the correlation between price and volume changes.</p>
    <p>Heavily traded stocks have tended to earn less than lightly traded ones. Illiquid stocks should compensate their holders, but here Amihud illiquidity points the other way: within the Russell 1000 it mostly marks the smaller names, which rank lower on the target.</p>
  </section>
  <section class="theme-card" style="--theme-color: var(--theme-6)">
    <h3>Market correlation <span>2 predictors</span></h3>
    <p class="theme-measures">Correlation of the stock's daily returns with the market over one and two years.</p>
    <p>Beta is correlation times relative volatility. Leverage-constrained investors bid up high-beta stocks for either reason, so high-correlation stocks should earn less even at the same volatility. That matches the data here before 2009. After 2009 the sign reverses: highly correlated stocks were calmer and earned more. I have no convincing explanation for the reversal, which makes this the least well-founded theme.</p>
  </section>
  <section class="theme-card" style="--theme-color: var(--theme-7)">
    <h3>Short positioning <span>9 predictors</span></h3>
    <p class="theme-measures">Short interest relative to daily volume, its variability, and changes in short interest.</p>
    <p>Short sellers are often well informed, and heavily shorted stocks have tended to underperform. Short interest relative to volume, often called days to cover, also measures crowding: how long the shorts would need to buy back.</p>
  </section>
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

<p class="figure-caption"><strong>Figure 1: How the predictors relate to each other and to the target.</strong> Average rank correlation over the selected period, every fifth session, with each predictor signed so that its 1998–2021 average IC is positive; blue pairs favour the same stocks. These full-period signs are for description only; the models learn signs from their training windows. The dendrogram (average linkage on 1 − |ρ|, since a mirrored predictor carries the same information) is fitted once on 1998–2021 so that periods stay comparable. The lower panel adds up each theme composite's IC with the forward 20-session sector-relative Sharpe target; hovering gives each theme's mean IC over the period.</p>

Over the full period, volatility is the most coherent theme: its predictors
correlate 0.71 on average. Momentum &amp; trend and Size are the least
coherent, at 0.15. Momentum &amp; trend spans horizons from days to three
years, and 43% of its signed pairs are negatively correlated: after the flip,
trading well above the 10-day average counts against a stock, while a strong
12-month return counts for it. The dendrogram agrees: cut into seven clusters,
it matches the themes for about three quarters of the predictors, and the
exceptions are informative. The 5–21-day price-position measures join
short-term reversal, market-cap variability joins volatility, and the
market-cap change measures join the longer momentum horizons. Although there
are 80 predictors, ten principal components carry nearly three quarters of
their variance.

Between themes, the composites overlap more than their individual predictors
do, because averaging removes each predictor's own noise. Volatility and size
correlate 0.72 on average, and between 0.56 and 0.83 in every calendar year.
Much of that is built in, as the dendrogram shows. Momentum &amp; trend and
size average 0.55. Other relationships change sign: market correlation and
volatility range from −0.51 to 0.37 across years.

Every theme ranks the target on average, but not in every period. Momentum
&amp; trend has an IC of 0.037 in 1998–2008 and 0.040 in 2009–2021, despite a
year of −0.060 in 2009. Short-term reversal fades from 0.021 to 0.004 across
the same split. Volatility and size strengthen, from about 0.02 to about 0.05,
which makes them the two strongest themes after 2009. Market correlation has a
negative IC in 7 of the 11 years through 2008 and in only one year after.

Overlap does not make a theme redundant. A correlation of 0.72 still leaves
about half of each composite's variance unexplained by the other, and that
part can carry its own information. The question for a learned combination is
whether weights fitted on one decade still suit the next.

## Three ways to combine them
{: #combining-them }

The simplest, most naive combination gives every predictor the same weight,
1/80. The only thing this *equal-weight* score learns from data is a
direction: each predictor enters with the sign of its correlation with the
target in the training window, so lower volatility counts in a stock's favour
because it did so in the past, not because I assumed it. Momentum &amp; trend
then carries 33 of the 80 weights simply because it has the most predictors. A
regression is free to reweight them.

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
gives OLS. The penalty acts on combinations of predictors: along a direction
whose variance across stock-dates is $\lambda$, Ridge multiplies the OLS
coefficient by $\lambda/(\lambda+c)$. Directions in which the predictors
barely vary, such as the difference between two nearly identical momentum
horizons, are shrunk the most ([Hastie](https://arxiv.org/abs/2006.00371)
explains this view well). As $c$ grows, the coefficients become proportional
to each predictor's own covariance with the target, so a heavily penalized
Ridge becomes a weighted version of the equal-weight score.

## Fitting through time
{: #from-predictions-to-portfolios }

I use an expanding window starting in January 1995. A rolling window would
adapt faster when predictors change, as Figure 1 shows they do, but each fit
would see less data and the weights would move more between refits; an
expanding window favours stable weights. The first training window contains
900 trading dates, and a 21-date gap lets the forward 20-session outcomes
finish before predictions begin. I then refit every 600 dates, keeping the
January 1995 start, so each refit adds history (Figure 2). Within each window
I fit three models on interleaved dates (1, 4, 7, …; 2, 5, 8, …; 3, 6, 9, …)
and average their predictions, which thins the overlap between neighbouring
targets within each fit. Until a long-window predictor has enough history, it
takes its date-and-sector mean.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/expanding-walk-forward" mobile="/assets/multiple-linear-regression/expanding-walk-forward_mobile" alt="Three expanding walk-forward fits share a January 1995 start. Training grows from 900 to 1500 to 2100 dates. Each training window is followed by a gap and a subsequent prediction block." version="3" %}
</div>

<p class="figure-caption"><strong>Figure 2: Expanding walk-forward.</strong> Each refit retains the earlier history and adds 600 training dates. The 21-date gap precedes each 600-date prediction block. Widths are schematic; the final prediction block can be shorter.</p>

Every prediction is made by a model that has not seen that date, so the
walk-forward keeps the weights out of sample. My own choices are a different
matter. I picked the predictors, the target, the portfolio rule and the Ridge
penalty by looking at results through December 2021, so I treat September
1998–December 2021 as the development period, the validation set for those
choices, and report January 2022–May 2026 separately as the test period,
labelled *Later* in the tables. The later period is short, about 54
non-overlapping 20-session windows, so small differences there are noise.

Every score goes through the same plain portfolio rule (Table 1). Because
volatility scaling lets each score take its own level of risk, I compare
scores on Sharpe rather than return. Portfolio construction itself is the
subject of the [optimization
article](/quants/2026/08/29/portfolio-optimization.html).

<table class="research-table settings-table" id="portfolio-construction">
  <caption><strong>Table 1: The portfolio rule.</strong> Identical for every score. Traded notional is annual two-way trading divided by capital.</caption>
  <tbody>
    <tr><th scope="row">Holdings</th><td>Long the top 75 stocks, short the bottom 75</td></tr>
    <tr><th scope="row">Position size</th><td>20% divided by the stock's past 60-session volatility (floored at 5%); at most 4% per stock and 100% of capital per side</td></tr>
    <tr><th scope="row">Rebalancing</th><td>Every three weeks at the next close; three schedules start one week apart and their statistics are averaged</td></tr>
    <tr><th scope="row">Costs</th><td>5 bp per dollar traded</td></tr>
  </tbody>
</table>

## Choosing the penalty
{: #choosing-the-penalty }

The penalty hardly matters until it is large enough to wash out the
regression's differences between predictors. Up to $c=0.1$, development IC and
Sharpe barely move (Table 2), even though the coefficients shrink to less than
half their OLS size. The portfolio only uses the ranking of the scores, so
shrinking every weight by the same factor would change nothing; what matters
is how the penalty changes the weights relative to each other. From $c=1$,
Ridge drifts toward the equal-weight score: its volatility rises toward the
equal-weight score's 9% and its Sharpe falls. At $c=100$ its IC, 0.046, is
essentially the equal-weight score's 0.047.

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
of how well a score ranks the target; $c$ of 0 to 0.01 has a marginally higher
Sharpe, 0.99 against 0.98, well inside the spread across schedules. Choosing
$c$ at each refit from the earlier prediction blocks alone lands in the same
range: 0.01 through 2010 (OLS once, and a default at the first refit, which
has no earlier blocks) and 0.1 at five of the six refits from 2012, including
every refit that predicts after 2021. At $c=0.1$, 44–48 of the 80 directions
have a variance below 0.1 and are shrunk by more than half, but together they
hold only 7–9% of the predictors' variance. OLS and Ridge scores still have a
daily rank correlation of 0.94.

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
0.44. After 2021 the gap in mean IC widens a little, 0.042 against 0.038.

Before looking at portfolios, I want to know how the Ridge and equal-weight
scores order returns. Figure 3 sorts the universe into ten equal-weighted
decile portfolios by score, re-formed on the same three-week schedules and
before costs.

<div class="pse-segments decile-periods" role="radiogroup" aria-label="Period">
  <button type="button" role="radio" aria-checked="true" data-decile-period="development">1998–2021</button>
  <button type="button" role="radio" aria-checked="false" data-decile-period="later">2022–2026</button>
</div>
<div class="mlr-plot" id="mlr-deciles" role="img" aria-label="Annual return of ten equal-weighted decile portfolios for the Ridge and equal-weight scores" data-source="/assets/multiple-linear-regression/regression-results.json?v=5" data-plotly="https://cdn.jsdelivr.net/npm/plotly.js-cartesian-dist-min@3.1.0/plotly-cartesian.min.js"></div>
<div class="research-table-scroll"><table class="research-table comparison-table decile-table" id="mlr-decile-table"></table></div>
<noscript><p>This chart needs JavaScript; the text below describes it.</p></noscript>

<p class="figure-caption"><strong>Figure 3: Decile portfolios of the scores.</strong> Compounded annual return of equal-weighted portfolios of the stocks in each score decile, with each decile's annualized volatility and Sharpe ratio below. Portfolios trade at the next close and are held until the next rebalance, averaged over the three schedules; before costs. Decile 10 holds the highest scores.</p>

Through 2021 Ridge's deciles climb from about 3% a year to 16%, and the top
decile earns a Sharpe ratio of 0.90 against 0.26 at the bottom. Equal weights
reach almost the same top-decile Sharpe, 0.89, by a different route: 13.5% a
year at 15.7% volatility, against Ridge's 15.9% at 18.2%. What stands out most
is volatility. For both scores it falls steadily from around 30% in decile 1
to 16–18% in decile 10, and more steeply for equal weights. As the target
suggested, much of what these scores learn is a volatility sort. After 2021
the return ordering almost disappears above decile 3: Ridge's deciles 3–10 all
earn 6–10%, the equal-weight top decile only 6.1%, and most of the spread
comes from the bottom decile. The volatility sort remains.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 4: Net performance and trading.</strong> Mean statistics across three rebalance schedules, after 5 bp per dollar traded, with min–max Sharpe in parentheses. Return and volatility are annualized; beta is measured against the Russell 1000.</caption>
  <thead>
    <tr><th>Score</th><th>Net return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Market beta</th><th>Gross exposure</th><th>Traded notional / year</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="8">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Equal-weight</th><td>7.52%</td><td>9.20%</td><td>0.82<br><small>(0.74–0.93)</small></td><td>−24.9%</td><td>0.11</td><td>134%</td><td>25.9×</td></tr>
    <tr><th scope="row">OLS</th><td>7.31%</td><td>7.37%</td><td>0.99<br><small>(0.90–1.05)</small></td><td>−18.7%</td><td>0.09</td><td>139%</td><td>29.0×</td></tr>
    <tr><th scope="row">Ridge</th><td>7.90%</td><td>8.05%</td><td>0.98<br><small>(0.89–1.16)</small></td><td>−19.8%</td><td>0.10</td><td>138%</td><td>28.4×</td></tr>
    <tr class="period-heading"><th colspan="8">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Equal-weight</th><td>6.00%</td><td>11.44%</td><td>0.52<br><small>(0.45–0.61)</small></td><td>−10.7%</td><td>0.07</td><td>131%</td><td>21.4×</td></tr>
    <tr><th scope="row">OLS</th><td>6.37%</td><td>9.18%</td><td>0.69<br><small>(0.67–0.73)</small></td><td>−8.5%</td><td>0.06</td><td>134%</td><td>25.9×</td></tr>
    <tr><th scope="row">Ridge</th><td>7.39%</td><td>10.16%</td><td>0.73<br><small>(0.67–0.83)</small></td><td>−9.4%</td><td>0.07</td><td>132%</td><td>24.4×</td></tr>
  </tbody>
</table>

Through 2021 learning the weights pays (Table 4): Ridge's Sharpe is 0.98
against 0.82 for equal weights, with a higher return, lower volatility and a
shallower drawdown, and OLS does about as well. The schedule ranges overlap,
though: Ridge's worst, 0.89, is below the best equal-weight schedule, 0.93.
The learned scores trade a little more, 28× a year against 26×, and the edge
survives costs up to about 28 bp per dollar traded, more than five times the 5
bp charged here. Costs exclude borrow, financing and market impact. Both books
are net long in dollars, by 35–50% of capital through 2021, because volatility
scaling gives the calmer long side larger positions; market beta stays near
0.1.

After 2021 both Sharpe ratios fall, but the gap holds: Ridge's Sharpe is 0.73
against 0.52, with a higher return and lower volatility, and its worst
schedule, 0.67, is above the best equal-weight schedule, 0.61. The edge
survives costs up to about 43 bp. How much of this is luck? A block bootstrap
of the combined daily returns puts Ridge's Sharpe advantage at about 0.2 in
both periods, with 95% intervals from roughly zero to 0.4: suggestive rather
than conclusive. Figure 4 shows the two paths.

Both scores lean toward larger stocks. Ridge's long candidates sit on average
at the 62nd market-cap percentile of the universe through 2021 and its short
candidates at the 31st, widening to the 70th and 23rd after 2021; equal
weights lean even further, to the 68th and 31st, then the 77th and 22nd. That
is the target at work: within the Russell 1000, larger mostly means calmer. So
the tilt is part of what both scores earn rather than Ridge's edge, and
whether to keep it is a portfolio construction question rather than a
modelling one.

<div class="mlr-plot" id="mlr-growth" role="img" aria-label="Growth of one dollar on a log scale and drawdowns for the equal-weight and Ridge scores, 1998–2026" data-source="/assets/multiple-linear-regression/regression-results.json?v=5" data-plotly="https://cdn.jsdelivr.net/npm/plotly.js-cartesian-dist-min@3.1.0/plotly-cartesian.min.js"></div>
<noscript><p>This chart needs JavaScript; Table 4 gives the same comparison.</p></noscript>

<p class="figure-caption"><strong>Figure 4: Portfolio paths of the equal-weight and Ridge scores.</strong> Mean daily net P&amp;L of the three schedules on common dates, compounded from <span class="mathjax-ignore">$1</span> (log scale), with drawdowns below; the dotted line marks the start of the test period. Each portfolio keeps its own risk level; Table 4 gives the risk-adjusted comparison.</p>

## What Ridge learned
{: #reading-the-predictors }

Figure 5 shows the ten largest average absolute Ridge weights at each refit. A
positive weight raises a stock's score as its rank on that predictor rises,
holding the other ranks fixed.

<div class="mlr-plot" id="mlr-coefficients" role="img" aria-label="Heatmap of the ten largest Ridge coefficients at each of the twelve refits" data-source="/assets/multiple-linear-regression/regression-results.json?v=5" data-plotly="https://cdn.jsdelivr.net/npm/plotly.js-cartesian-dist-min@3.1.0/plotly-cartesian.min.js"></div>
<noscript><p>This chart needs JavaScript; the text below describes it.</p></noscript>
<script src="/assets/js/regression-results.js?v=10" defer></script>

<p class="figure-caption"><strong>Figure 5: The ten largest Ridge coefficients by refit.</strong> Each refit averages the three interleaved training fits; the year is the start of its prediction block. Rows are ranked by mean absolute coefficient over all refits; hover for each predictor's full definition.</p>

The largest weight is negative, on the 10/21-day MACD, a short-horizon trend
measure whose own IC is close to zero, and the 90-day high relative to the
start of the window also counts against a stock. Positive weights on the
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
for equal weights, which is why it trades more. Short windows don't explain
that, since predictors of 21 sessions or less hold about 31% of the weight
under both scores; the contrasts between horizons are the more likely source.

## What learning the weights buys

I started by asking how much weight each predictor should get, given what the
others already tell me. Letting a regression answer that is better than not
answering it, by about 0.2 of Sharpe in both periods, though that gap is not
far from noise. Against equal weights on every predictor, Ridge lifts the
Sharpe ratio from 0.82 to 0.98 through 2021 and from 0.52 to 0.73 after,
trades only a little more, and keeps its edge at costs of 28–43 bp per dollar
traded, well above the 5 bp I charge. The gain doesn't come from a clever
penalty: OLS does as well, and a heavy enough penalty pushes Ridge back toward
the equal-weight score. It comes from fitting the weights jointly, which lets
the regression discount overlapping and weak predictors instead of counting
each at 1/80.

What the regression learns is less exciting than a Sharpe of 0.98 suggests.
The decile portfolios show that both scores are largely a volatility sort and
lean toward larger, calmer stocks, equal weights even more so; Ridge's edge
over them comes more from return. The volatility sort is what the Sharpe
target asks for, and a volatility-scaled portfolio can use it, but it ties the
result to the low-volatility effect. After 2021 Ridge's daily returns move
more closely with the volatility-scaled portfolio from the [low-volatility
article](/quant/2024/12/15/low-volatility-factor.html), with a correlation of
0.78 against 0.62 before, and that portfolio earned only about 1.5% a year
over those years, against 6.5% before. Ridge's own return held up; its
volatility rose, and that is what lowered its Sharpe. In the April 2025–May
2026 rally that the low-volatility article looks at, its long and short stocks
rose almost equally, and it made roughly nothing.

So I would keep Ridge with a light penalty as the ranking, and treat its lean
toward calm, large stocks as an exposure to manage rather than as skill. Two
questions stay open. The expanding window weights 1995–2008 as heavily as the
recent decade, and Figure 1 shows the themes changed between them, so a
rolling window might adapt better. And a target that separates return from
risk would show how much of the edge survives once the volatility forecast is
taken out. The
[optimization article](/quants/2026/08/29/portfolio-optimization.html)
takes up the portfolio side, controlling portfolio risk and market exposure
directly.

[^theme-references]: Momentum: Jegadeesh and Titman, *Returns to Buying Winners and Selling Losers*, Journal of Finance, 1993; Da, Gurun and Warachka, *Frog in the Pan*, Review of Financial Studies, 2014. Reversal: Jegadeesh, *Evidence of Predictable Behavior of Security Returns*, Journal of Finance, 1990; Lehmann, *Fads, Martingales, and Market Efficiency*, Quarterly Journal of Economics, 1990. Volatility: Ang, Hodrick, Xing and Zhang, *The Cross-Section of Volatility and Expected Returns*, Journal of Finance, 2006; Baker, Bradley and Wurgler, *Benchmarks as Limits to Arbitrage*, Financial Analysts Journal, 2011; Bali, Cakici and Whitelaw, *Maxing Out*, Journal of Financial Economics, 2011. Trading volume: Lee and Swaminathan, *Price Momentum and Trading Volume*, Journal of Finance, 2000. Illiquidity: Amihud, *Illiquidity and Stock Returns*, Journal of Financial Markets, 2002. Size: Banz, *The Relationship Between Return and Market Value of Common Stocks*, Journal of Financial Economics, 1981; Asness, Frazzini, Israel, Moskowitz and Pedersen, *Size Matters, If You Control Your Junk*, Journal of Financial Economics, 2018. Market correlation: Frazzini and Pedersen, *Betting Against Beta*, Journal of Financial Economics, 2014; Asness, Frazzini, Gormsen and Pedersen, *Betting Against Correlation*, Journal of Financial Economics, 2020. Short positioning: Boehmer, Jones and Zhang, *Which Shorts Are Informed?*, Journal of Finance, 2008; Hong, Li, Ni, Scheinkman and Yan, *Days to Cover and Stock Returns*, NBER working paper, 2015.
