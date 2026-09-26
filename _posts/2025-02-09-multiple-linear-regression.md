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

The target is each stock's forward 20-session Sharpe ratio: mean daily return
divided by daily return volatility over the next 20 sessions, roughly a
trading month and close to the three-week rebalance interval. Lower future
volatility amplifies both positive and negative average returns, so the
target mixes return and risk. I rank it within each date and sector and map
the ranks into $[-1,1]$; a high label marks a stock that subsequently did well
relative to its sector peers.

Each predictor is ranked across the whole universe on each date and mapped
into $[-1,1]$ in the same way. Ranking puts different units on one bounded
scale and limits the influence of outliers, at the cost of discarding
magnitudes ([details](#ranking-details)). Throughout, the information
coefficient (IC) is the cross-sectional Spearman rank correlation between a
predictor, or a score, and the target on one date.

## The predictors
{: #the-predictors }

The regressions use 80 predictors, mostly built from prices and trading
activity. I group them into seven themes (Table 1).

<table class="research-table settings-table predictor-themes">
  <caption><strong>Table 1: The predictors by theme.</strong> Horizons are trading sessions.</caption>
  <thead>
    <tr><th>Theme</th><th>What it captures</th><th>Predictors</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Momentum &amp; trend</th><td>Returns and risk-adjusted returns over 3–12 months, price relative to moving averages and to recent highs and lows, how persistently the price stayed above its 200-day average, and the share of losing days</td><td>33</td></tr>
    <tr><th scope="row">Short-term reversal</th><td>Returns over the last 1–21 sessions, which tend to partly reverse</td><td>4</td></tr>
    <tr><th scope="row">Volatility</th><td>Close-to-close, downside and upside volatility and average true range, over 5–252 sessions</td><td>12</td></tr>
    <tr><th scope="row">Size</th><td>Log market capitalization, its change, and its variability: the standard deviation of log market cap over a window, or how much the company's value has moved around</td><td>10</td></tr>
    <tr><th scope="row">Liquidity &amp; volume</th><td>Share turnover, Amihud illiquidity (absolute return per dollar traded), variability of trading volume, and the correlation between price and volume changes</td><td>10</td></tr>
    <tr><th scope="row">Market correlation</th><td>Correlation of the stock's daily returns with the market over one and two years</td><td>2</td></tr>
    <tr><th scope="row">Short positioning</th><td>Short interest relative to daily volume: its level, variability and change</td><td>9</td></tr>
  </tbody>
</table>

An earlier version of this article used 144 predictors. Many were near
copies: the same measurement at a neighbouring window, or volatility measured
two slightly different ways. I kept a core and a few distinct variants per
family, dropped predictors that correlated above 0.9 with one I kept, and
added 21-day loss frequency as a short-term candidate. I chose the set on
data through 2021, from its stability across five-year blocks in a separate
tree-model comparison, not from the regressions below.

## How the predictors overlap
{: #correlation-structure }

On every fifth session from 1995 through 2021, I compute the rank
correlation between every pair of predictors and between each predictor and
the target, then average across dates. First I flip the sign of each
predictor whose average IC is negative. Lower volatility predicts a higher
target, for example, so I use negative volatility. After the flip, a positive
correlation means two predictors favour the same stocks.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/predictor-correlation" mobile="/assets/multiple-linear-regression/predictor-correlation_mobile" alt="Heatmap of average rank correlations between the 80 predictors, grouped into seven theme blocks. Volatility forms a strongly correlated block that also correlates with size; momentum and trend contains both positive and negative pairs." version="1" %}
</div>

<p class="figure-caption"><strong>Figure 1: Average rank correlation between the 80 predictors, 1995–2021.</strong> Predictors are grouped by theme and, within a theme, ordered by similarity. Each predictor is signed so that its average IC is positive; blue pairs favour the same stocks.</p>

Volatility is the most coherent theme: its predictors correlate 0.72 on
average. Momentum &amp; trend is the least coherent. It spans horizons from
days to two years, and 45% of its signed pairs are negatively correlated: a
stock trading well above its 10-day average is a short-term bet against the
stock, while a strong 12-month return is a bet for it. Across themes, the
largest block links volatility with size. Although there are 80 columns,
about ten independent combinations carry most of their variation.

To follow the themes through time, I combine each theme into one composite:
the equal-weight sum of its signed, standardized predictor ranks. Figure 2
shows how strongly each pair of composites moves together in each year.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/theme-overlap-by-year" mobile="/assets/multiple-linear-regression/theme-overlap-by-year_mobile" alt="Heatmap of correlations between the seven theme composites, one row per pair of themes and one column per year from 1995 to 2021. Volatility and size are strongly correlated in every year; most pairs involving short-term reversal are close to zero." version="1" %}
</div>

<p class="figure-caption"><strong>Figure 2: Overlap between themes by year, 1995–2021.</strong> Mean daily rank correlation between two theme composites in each calendar year. Rows are sorted by their average correlation.</p>

Volatility and size overlap in every year, with correlations between 0.55 and
0.83. Small companies tend to be volatile, and the size theme also measures
how much a company's market value has moved. Momentum &amp; trend and size
average 0.51. Other relationships change sign: the correlation between market
correlation and volatility ranges from −0.51 to 0.37 across years.

Figure 3 shows how well each composite ranked the target in each year.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/theme-ic-by-year" mobile="/assets/multiple-linear-regression/theme-ic-by-year_mobile" alt="Heatmap of each theme composite's mean daily rank IC by year from 1995 to 2021. Volatility and size are strongest after 2009; momentum and trend drops below zero in 2009; short-term reversal fades after the early 2000s." version="1" %}
</div>

<p class="figure-caption"><strong>Figure 3: Theme IC by year, 1995–2021.</strong> Mean daily rank IC of each theme composite with the forward 20-session sector-relative Sharpe target. Signs use the full period, so every theme's average IC is positive by construction.</p>

Every theme predicts the target on average, but not every year. Momentum
&amp; trend keeps a similar IC before and after 2009, 0.048 and 0.042, apart
from a sharp loss in the 2009 rebound (−0.053). Short-term reversal fades
from 0.029 in 1995–2008 to 0.006 in 2009–2021. Volatility and size
strengthen, from about 0.03 to above 0.05. Market correlation has a negative
IC in 8 of the 14 years through 2008 and in only one year after.

So the themes overlap, and their usefulness shifts. Overlap does not make a
theme redundant: volatility and size correlate 0.71 on average, and each can
still carry information the other lacks. But equal weights across all seven
themes would lean heavily on that shared bet, and weights that suit one decade
may not suit the next. Combining them needs some care.

## A three-theme benchmark
{: #a-fixed-weight-comparison }

The simplest response to that overlap is to choose a few themes that differ
and weight them equally. Momentum &amp; trend, volatility and short
positioning are among the least correlated pairs in Figure 2 (0.34, 0.08 and
0.05 on average). Size overlaps most with volatility, so I leave it out to keep
the rule small, not because it lacks information. My benchmark gives each
of these three themes one third of the score and splits that weight equally
among its predictors (Table 2). It favours medium-term strength, lower
volatility and lighter short positioning. I label it “Fixed” because I choose
its weights in advance.

<table class="research-table settings-table benchmark-ingredients">
  <caption><strong>Table 2: The fixed score.</strong> Each theme receives one third of the weight, divided equally among its predictors. Horizons are trading sessions.</caption>
  <thead>
    <tr><th>Theme</th><th>What the score favors</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Momentum</th><td>Higher returns over 63, 126 and 252 sessions; higher price relative to its 126- and 252-session moving averages</td></tr>
    <tr><th scope="row">Defensive</th><td>Lower volatility over 21, 63 and 126 sessions; lower downside volatility over 63 and 126 sessions</td></tr>
    <tr><th scope="row">Short positioning</th><td>Lower short interest relative to daily volume, smoothed over 21 and 63 sessions</td></tr>
  </tbody>
</table>

Equal theme weights are easy to understand, but they do not say how much
each overlapping horizon adds. The regressions learn the weights instead,
on all 80 predictors. Against the fixed rule they change both the inputs and
the weights; OLS against Ridge keeps the inputs the same and isolates
regularization. I also refit both on the benchmark's twelve inputs, to
separate learning the weights from adding predictors.

## OLS versus Ridge
{: #learning-the-combination }

Fitting the weights jointly makes each one conditional. The coefficient on
six-month momentum measures its relationship with the target holding the
other inputs fixed, including the neighbouring momentum horizons, and its
sign can differ from six-month momentum's own IC.

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

where $\mathbf z_{i,t}$ holds stock $i$'s 80 predictor ranks on date $t$ and
the intercept $a$ is unpenalized; $c=0$ gives OLS. The penalty shrinks the
least-variable combinations of predictors most, accepting some bias for less
sensitivity to noise ([appendix](#what-ridge-changes)). I fixed $c=0.01$ in
advance rather than tuning it: on these rank-scaled inputs it halves the
weight on combinations whose variance is below 0.01 and barely touches the
combinations that carry most of the variation. The predictor set, target,
penalty and training scheme were all fixed using data through 2021.

## Fitting through time
{: #from-predictions-to-portfolios }

I use an expanding window starting in January 1995. The first training
window contains 900 trading dates, and a 21-date gap lets the forward
20-session outcomes finish before predictions begin. I then refit every 600
dates, keeping the January 1995 start, so each refit adds history (Figure 4).
OLS and Ridge share the same twelve windows, with predictions from September
1998. Within each window, I fit three models on interleaved dates and average
their predictions ([appendix](#sampling-the-training-dates)).

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/expanding-walk-forward" mobile="/assets/multiple-linear-regression/expanding-walk-forward_mobile" alt="Three expanding walk-forward fits share a January 1995 start. Training grows from 900 to 1500 to 2100 dates. Each training window is followed by a gap and a subsequent prediction block." version="2" %}
</div>

<p class="figure-caption"><strong>Figure 4: Expanding walk-forward.</strong> Each refit retains the earlier history and adds 600 training dates. The 21-date gap precedes each 600-date prediction block. Widths are schematic; the final prediction block can be shorter.</p>

I report results through December 2021 and for January 2022–May 2026
separately.

<aside class="research-note" markdown="1" id="portfolio-construction">
**How I evaluate the scores.** Every score goes through the same plain
portfolio rule. I buy the top 75 stocks and short the bottom 75, scale
positions inversely to their past 60-session volatility (20% annual
reference, 5% floor), cap each stock at 4% and each side at 100% of capital,
rebalance every three weeks at the next close and charge 5 bp per dollar
traded. I run three rebalance schedules starting one week apart and average
their statistics. Portfolio construction itself is the subject of the
[optimization article](/quants/2026/08/29/portfolio-optimization.html). Because
this rule lets each score take its own level of risk, I compare scores on
Sharpe rather than return. Gross exposure is long plus short positions
relative to capital; traded notional is annual two-way trading divided by
capital. Returns use arithmetic annualization, and Sharpe assumes a zero cash
rate.
</aside>

## Results
{: #prediction-quality-and-portfolio-results }

I start with ranking quality, then look at portfolios, then at the
same-input refit.

<table class="research-table comparison-table ic-summary-table portfolio-card-table">
  <caption><strong>Table 3: Cross-sectional ranking quality.</strong> Mean daily rank IC, its standard deviation and their unannualized ratio. Adjacent observations share overlapping 20-session outcomes; later IC ends on 28 April 2026, the last complete target date.</caption>
  <thead>
    <tr><th>Ranking</th><th>Mean daily IC</th><th>IC SD</th><th>IC IR</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="4">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Fixed</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">OLS</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Ridge</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr class="period-heading"><th colspan="4">Later · January 2022–April 2026</th></tr>
    <tr><th scope="row">Fixed</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">OLS</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Ridge</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
  </tbody>
</table>

[TBD: two or three sentences on Table 3 — whether the regressions rank better
than the fixed score in each period, and how OLS and Ridge compare.]

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 4: Net performance and trading.</strong> Mean statistics across three rebalance schedules, after 5 bp per dollar traded, with min–max Sharpe in parentheses. Return and volatility are annualized; beta is measured against the Russell 1000.</caption>
  <thead>
    <tr><th>Score</th><th>Net return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Market beta</th><th>Gross exposure</th><th>Traded notional / year</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="8">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Fixed</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">OLS</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Ridge</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr class="period-heading"><th colspan="8">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Fixed</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">OLS</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Ridge</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
  </tbody>
</table>

[TBD: Table 4 in three short paragraphs — where the Sharpe difference comes
from (return or volatility), whether the regressions' advantage holds on each
schedule and in both periods, and how much extra trading it costs. Compare
Ridge with OLS last. The cost estimate excludes borrow, financing and market
impact.]

<div class="research-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/performance-and-drawdowns" mobile="/assets/multiple-linear-regression/performance-and-drawdowns_mobile" alt="Net growth on a logarithmic scale with a shared drawdown panel below for fixed weights, OLS, and Ridge" version="19" %}
</div>

<p class="figure-caption"><strong>Figure 5: Portfolio paths from the three scores.</strong> [TBD: rerender from the 80-predictor rerun.] The mean daily net P&amp;L of the three schedules, on common active dates, compounded into an index starting at <span class="mathjax-ignore">$1</span> (log scale), with drawdowns below. Each portfolio keeps its own risk level; Table 4 gives the risk-adjusted comparison.</p>

### Learning weights on the same inputs

How much of the difference comes from learning the weights? I refit OLS and
Ridge on exactly the fixed rule's twelve predictors, keeping the target,
training windows, penalty and portfolio rules the same.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 5: The same twelve inputs, different weights.</strong> Mean statistics across the three rebalance schedules, with min–max Sharpe in parentheses; conventions match Table 4.</caption>
  <thead>
    <tr><th>Score</th><th>Net return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Market beta</th><th>Gross exposure</th><th>Traded notional / year</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="8">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Fixed</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">OLS · 12</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Ridge · 12</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr class="period-heading"><th colspan="8">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Fixed</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">OLS · 12</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
    <tr><th scope="row">Ridge · 12</th><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td><td>[TBD]</td></tr>
  </tbody>
</table>

[TBD: compare Table 5 with Table 4 — how much of the Sharpe gain appears with
the same twelve inputs, and how much only with the 80 predictors; whether the
extra volatility reduction and trading come with the broader set.]

## What the model learned
{: #reading-the-predictors }

Figure 6 shows the ten largest average absolute Ridge weights. A positive
weight raises a stock's score as its rank on that predictor rises, holding
the other ranks fixed.

<div class="research-figure coefficient-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/top-coefficients" alt="Signed coefficients for the ten largest mean absolute Ridge weights across walk-forward refits" version="12" %}
</div>

<p class="figure-caption"><strong>Figure 6: The ten largest mean absolute Ridge coefficients, averaged across the three training subsamples at each refit.</strong> [TBD: rerender from the 80-predictor fits, with a mobile variant.] Rows are selected using the full coefficient history.</p>

Because each weight is conditional, it can disagree with the predictor's own
IC in Figure 3. In the earlier 144-predictor fit, the 10/21-day MACD had a
positive standalone IC but a negative weight, sitting among positive weights
on longer-horizon momentum: the model favoured long-term strength without
chasing the latest move. That is the contrast visible inside the
Momentum &amp; trend block of Figure 1, where short and long horizons point in
opposite directions. [TBD: confirm which contrasts the 80-predictor fit
learns, and whether their signs persist across the twelve refits.]

Those short-horizon contrasts are also a likely source of the extra trading.
Reversal and short-horizon trend predictors change rank quickly, so a score
that leans on them reshuffles its top and bottom 75 more often than the fixed
rule, which has no predictor shorter than 21 sessions. [TBD: support with the
rank persistence of each theme and the traded notional in Table 4.]

These are ten terms among 80, and several describe similar characteristics,
so a large coefficient can partly offset another. To establish which themes
improve the portfolio, I would need to remove them and refit.

## Where this leaves me

A simple theme-based score is hard to beat. [TBD: confirm with Tables 4–5.]
Learning the weights adds little on its own. Most of the modest gain comes
from the broader predictor set, mainly through lower volatility, at the cost
of more trading. The overlap in the predictors helps explain why: the two
strongest themes, volatility and size, share much of their bet, so a learned
model spends much of its freedom reweighting that shared bet and adding
short-horizon contrasts that trade a lot.

I still prefer a small Ridge penalty when predictors overlap this much. It
moderates the uncertain contrasts between them, although
[TBD: whether it changes stock selection enough to matter].

These results also depend on how I size the selected stocks. In the
[optimization article](/quants/2026/08/29/portfolio-optimization.html) I take
more control over portfolio risk and exposures, starting from the earlier
144-predictor Ridge ranking.

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

The smaller the variance, the stronger the shrinkage; at $c=0.01$ a direction
with $\lambda_j=0.01$ is halved. [Hastie's Ridge
review](https://arxiv.org/html/2006.00371v2) (2024, Sections 2–3) develops
this interpretation. [TBD: across the twelve training windows and three date
subsamples, how many of the 80 eigenvalues lie below 0.1 and below 0.01, and
the share of predictor variance in those directions.]

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
the next gets 2, 5, 8, …; and the third gets 3, 6, 9, … (Figure 7). Each
receives complete cross-sections from its dates, and I average their
predictions. This spreads out each model's observations while using all
dates collectively, although their forward targets still overlap.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/date-sampling" mobile="/assets/multiple-linear-regression/date-sampling_mobile" alt="Three models within one training window: model 1 uses dates 1, 4, 7; model 2 uses 2, 5, 8; model 3 uses 3, 6, 9. Their prediction scores are averaged." version="2" %}
</div>

<p class="figure-caption"><strong>Figure 7: Interleaved training dates.</strong> The first nine training dates illustrate the three offsets. Each selected date contributes a full cross-section.</p>

I give each training row equal weight, so dates with more usable stocks
contribute more to the loss. The row count overstates the independent
information: adjacent targets share 19 of their 20 daily returns, predictors
persist, and stocks share market and sector shocks.

### Ranking details
{: #ranking-details }

For a non-flat group of $N$ distinct observations, the rank transformation is

$$
z_i=2\frac{\operatorname{rank}(x_i)}{N}-1.
$$

A stock's momentum can rise from −2% to +10% while its rank stays unchanged.
The cross-sectional distributions stay approximately uniform over time, which
keeps scales comparable when pooling history[^rank-convention] and limits the
influence of extreme predictor and target values. Ranking fixes the scale,
not the relationships: correlations and predictive relationships can still
change, as Figures 2 and 3 show.

The cost is losing absolute levels and distances. Adjacent stocks receive the
same rank gap whether their momentum differs by one or twenty percentage
points, and those discarded magnitudes may contain predictive information.
Predictors are ranked across the universe while targets are ranked within
sectors, so a high momentum rank can pair with middling performance among
sector peers, and a portfolio that selects across sectors can still take
sector exposures.

[^rank-convention]: Gu, Kelly and Xiu also rank stock characteristics in [*Empirical Asset Pricing via Machine Learning*](https://dachxiu.chicagobooth.edu/download/ML_BKP.pdf), September 2019 manuscript, PDF page 24.
