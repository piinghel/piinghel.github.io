---
layout: post
title: "Combining Multiple Predictors: The Linear Case"
description: "From a low-volatility signal to supervised stock selection: choosing a target, ranking predictors, and learning a linear combination."
date: 2025-02-09
last_modified_at: 2026-09-14
categories: ["Regression"]
article_label: Factor combination · Multiple linear and Ridge regression
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

With one characteristic, the ranking gives me a selection rule directly.
With several, I need to decide how to combine them. A stock might have strong
momentum but high volatility, and several momentum horizons may repeat much
of the same information. How much weight should each predictor receive,
given what the others already tell me?

## A three-theme benchmark
{: #a-fixed-weight-comparison }

I start with a simple rule. I group twelve predictors into momentum,
defensive signals and short positioning, giving each theme one third of the
score and splitting that weight equally among its ingredients (Table 1).
The rule favours medium-term strength, lower volatility and lighter short
positioning. I label it “Fixed” in the results because I choose its weights
in advance. Each ingredient enters as a rank among the stocks on that
date, on the common scale described below.

<table class="research-table settings-table benchmark-ingredients">
  <caption>Table 1: The fixed score. Each theme receives one third of the weight, divided equally among its ingredients. Horizons are trading sessions.</caption>
  <thead>
    <tr><th>Theme</th><th>What the score favors</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Momentum</th><td>Higher returns over 63, 126 and 252 sessions; higher price relative to its 126- and 252-session moving averages</td></tr>
    <tr><th scope="row">Defensive</th><td>Lower volatility over 21, 63 and 126 sessions; lower downside volatility over 63 and 126 sessions</td></tr>
    <tr><th scope="row">Short positioning</th><td>Lower short interest relative to daily volume, smoothed over 21 and 63 sessions</td></tr>
  </tbody>
</table>

Equal theme weights are easy to understand, but they do not tell me how much
each overlapping horizon adds. I can instead learn the weights jointly from
historical outcomes. Here I compare the twelve-input rule with ordinary
least squares (OLS) and Ridge on a broader set of 144 predictors. That tests
the learned approach as a whole, changing both inputs and weights; comparing
OLS with Ridge keeps the inputs fixed and isolates regularization. All three
use the same stocks. I also repeat the regressions on the benchmark's twelve
inputs, so I can separate learning the weights from adding predictors.

## Supervised learning

<span id="what-i-ask-the-model-to-predict"></span>

I want to keep the focus on risk-adjusted performance from the low-volatility
article. My target is each stock's forward 20-session Sharpe ratio: mean daily
return divided by daily return volatility over those sessions.

Lower future volatility amplifies both positive and negative average returns
in this target, so the model learns about return and risk together.

Twenty sessions covers roughly a trading month, close to the portfolio's
three-week rebalance interval.

I then rank these forward Sharpe ratios within each date and sector and
map them into $[-1,1]$. A high label identifies a stock that subsequently
performs well relative to its sector peers. This gives me a score for ranking
stocks, which is what I need for selection.

### Representing the predictors

For the main comparison, both regressions use 144 predictors, mostly based
on prices and trading activity: momentum and trend, volatility, liquidity,
size and short positioning. Several horizons capture recent and longer-term
behaviour, while introducing substantial overlap between the inputs.

The universe uses point-in-time Russell 1000 membership, excluding stocks below
five dollars, announced merger targets and duplicate share classes. On each
date, I rank the remaining stocks on each predictor across this whole universe and
map the ranks into $[-1,1]$.

### What ranking changes

Ranking puts those different units on a bounded, comparable scale. For a
non-flat group of $N$ distinct observations, the transformation used here is

$$
z_i=2\frac{\operatorname{rank}(x_i)}{N}-1.
$$

For example, a stock's momentum can rise from −2% to +10% while its rank
stays unchanged. The marginal cross-sectional distributions stay approximately
uniform over time. This keeps scales comparable when pooling history[^rank-convention] and
limits the influence of extreme predictor and target values. Correlations
and predictive relationships can still change.

The cost is losing absolute levels and distances: adjacent stocks receive
the same rank gap whether their momentum differs by one or twenty percentage
points. A narrow win over sector peers and a large one can receive the same
target label. Those discarded magnitudes may contain predictive information.

The groups also matter: predictors are ranked across the universe, while
targets are ranked within sectors. A high momentum rank can therefore pair
with middling subsequent performance among sector peers. Portfolio selection
still spans sectors and can create sector exposures.

[^rank-convention]: Gu, Kelly and Xiu also rank stock characteristics in [*Empirical Asset Pricing via Machine Learning*](https://dachxiu.chicagobooth.edu/download/ML_BKP.pdf), September 2019 manuscript, PDF page 24.

### Breadth and dependence
{: #building-the-training-matrix }

Indexed by date and asset ID, the feature matrix $X$ has $n$ stock-date rows
and 144 ranked predictor columns; I give each training row equal weight,
so dates with more usable stocks contribute more to the loss.

The row count overstates the independent information: adjacent targets share
19 of their 20 daily returns, predictors persist, and stocks share market
and sector shocks. Breadth gives the model differences across stocks to
learn from within a limited market history. Pooling assumes that the
predictive relationship is sufficiently shared across stocks and dates;
cross-sectional dependence limits how much information that breadth adds.

## Learning the weights
{: #learning-the-combination }

I fit the weights jointly to the historical predictor–target pairs. With
$z_{i,j,t}$ denoting stock $i$'s rank on predictor $j$ at date $t$, each
regression produces a score that can extend beyond $[-1,1]$:

$$
\widehat y_{i,t}
=\widehat a+\sum_{j=1}^{144}\widehat\beta_j z_{i,j,t}.
$$

The model is linear in the predictor ranks. A given change in a rank has
the same effect on the score wherever that stock starts; the ranking step
has already discarded the original units and distances.

Fitting the weights together matters when predictors overlap. The coefficient on
six-month momentum measures its relationship with the target conditional on
the other inputs, including shorter and longer momentum horizons. Its sign
can differ from the relationship obtained using six-month momentum alone.

For example, $2x_1-1.8x_2=0.2x_1+1.8(x_1-x_2)$ combines a small common
exposure with a large weight on the difference between two signals. With
related momentum horizons, that difference may contain information about the
shape of the trend. But if the horizons move closely together, the sample
contains much less variation from which to estimate the effect of their
difference. OLS can then assign large, opposing coefficients that are
sensitive to noise.

I minimize $\mathrm{MSE}+c\lVert\boldsymbol\beta\rVert_2^2$, leaving the
intercept unpenalized; $c=0$ gives OLS. Squared error fits target-rank levels
across the whole cross-section, while the portfolio uses only the tails.

Ridge moderates the large, opposing weights that overlapping predictors
can produce. It shrinks the least-variable combinations most strongly,
accepting some bias to reduce sensitivity to noise. Those combinations may
still contain useful information, so the amount of shrinkage matters.

I use $c=0.01$ in the mean-squared-error objective. Equivalently, the penalty
on a sum-of-squares objective is $\alpha=nc$, preserving its scale as the
training sample expands. Because coefficient size depends on predictor units,
the common rank scaling also determines how this penalty treats the inputs.

[^diagnostics]: The [aggregate evidence](https://github.com/piinghel/piinghel.github.io/tree/main/assets/multiple-linear-regression/evidence) includes spectra, coefficient projections, beta estimates and schedule-level results. Training covariances use the retained normalized inputs and recorded windows, dropping missing targets. Original training-input hashes were not captured, so these diagnostics reconstruct the retained design rather than independently reproducing the original fits.

## Fitting through time

<span id="from-predictions-to-portfolios"></span>

I use an expanding window, beginning in January 1995. The first training
window contains 900 trading dates. A 21-date gap allows the forward
20-session training outcomes to finish before predictions begin. I then
refit roughly every two and a half years, keeping the January 1995 start
and adding the available history. Between refits, the coefficients stay
fixed. Figure 1 shows the first three windows.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/expanding-walk-forward" mobile="/assets/multiple-linear-regression/expanding-walk-forward_mobile" alt="Three expanding walk-forward fits share a January 1995 start. Training grows from 900 to 1500 to 2100 dates. Each training window is followed by a gap and a subsequent prediction block." version="2" %}
</div>

<p class="figure-caption">Figure 1: Expanding walk-forward. Each refit retains the earlier history and adds 600 training dates. The 21-date gap precedes each 600-date prediction block. Recent dates enter training once their forward outcomes are available. Widths are schematic; the final prediction block can be shorter.</p>

Keeping the older history adds observations but retains older relationships;
a rolling window would drop the earliest dates. OLS and Ridge share the
same twelve expanding windows, with predictions beginning in September 1998.

I report results through December 2021 and for January 2022–May 2026 separately.

### Sampling the training dates

Within each training window, I fit three models: one gets dates
1, 4, 7, …; the next gets 2, 5, 8, …; and the third gets 3, 6, 9, … (Figure 2).
Each receives complete cross-sections from its dates, and I average their
predictions. This spreads out each model's observations while using all dates
collectively, although their forward targets still overlap.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/date-sampling" mobile="/assets/multiple-linear-regression/date-sampling_mobile" alt="Three models within one training window: model 1 uses dates 1, 4, 7; model 2 uses 2, 5, 8; model 3 uses 3, 6, 9. Their prediction scores are averaged." version="2" %}
</div>

<p class="figure-caption">Figure 2: Interleaved training dates. The first nine training dates illustrate the three offsets used in the study. Each selected date contributes a full cross-section. The same construction is applied within each training window.</p>

## Prediction quality
{: #prediction-quality-and-portfolio-results }

OLS and Ridge have almost identical ranking quality: both beat the fixed
score during development, but the fixed score has the highest mean information
coefficient (IC) after 2021. The regressions' daily IC is less variable in both periods
(Table 2). I measure IC as the cross-sectional Spearman correlation between
the score and the forward sector-relative Sharpe target.

<table class="research-table comparison-table ic-summary-table portfolio-card-table">
  <caption>Table 2: Cross-sectional ranking quality. Mean daily rank IC, its standard deviation and their unannualized ratio. Adjacent observations share overlapping 20-session outcomes; later IC ends on 28 April 2026, the last complete target date.</caption>
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

## From scores to portfolios
{: #portfolio-construction }

For each score, I buy the top 75 stocks and short the bottom 75. Starting
from equal weights within each side, I scale positions inversely to their
past 60-session volatility, using 20% annual volatility as the reference
and a 5% floor. Each stock is capped at 4% of strategy capital, and each
side at 100%; a side below that cap is left at its resulting size. I
rebalance every three weeks with next-close execution and charge 5 bp
per dollar traded.

Returns use arithmetic annualization, and Sharpe assumes a zero cash
rate. Two-way turnover counts purchases and sales relative to strategy
capital, annualized.

To reduce dependence on [rebalance luck](/quants/2025/05/10/rebalancing-luck.html),
I run each score on three schedules starting one week apart and report
results across all three.[^schedule-summary]

[^schedule-summary]: Table 3 averages statistics calculated separately for the three schedules. Figure 3 compounds their mean daily net P&L on common dates. Averaging schedule-level Sharpes differs from calculating the Sharpe of that averaged return series.

## Portfolio results

OLS and Ridge mainly improve the portfolio by lowering volatility (Table 3).
The gain in net return is much less convincing. During development, extra
trading eats up most of OLS's gross-return advantage over the fixed score.

<table class="research-table comparison-table portfolio-card-table">
  <caption>Table 3: Net performance and trading. Mean statistics across three rebalance schedules, after 5 bp per dollar traded, with min–max Sharpe in parentheses. Arithmetic return and volatility are annualized; traded notional is annual two-way trading divided by strategy capital. Beta is measured against the Russell 1000.</caption>
  <thead>
    <tr><th>Score</th><th>Net return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Market beta</th><th>Traded notional / year</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="7">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Fixed</th><td>6.81%</td><td>9.11%</td><td>0.75<br><small>(0.71–0.80)</small></td><td>−26.32%</td><td>0.07</td><td>14.4×</td></tr>
    <tr><th scope="row">OLS</th><td>7.14%</td><td>7.14%</td><td>1.00<br><small>(0.90–1.13)</small></td><td>−18.31%</td><td>0.08</td><td>29.3×</td></tr>
    <tr><th scope="row">Ridge</th><td>7.40%</td><td>7.36%</td><td>1.01<br><small>(0.91–1.09)</small></td><td>−18.46%</td><td>0.09</td><td>29.0×</td></tr>
    <tr class="period-heading"><th colspan="7">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Fixed</th><td>7.76%</td><td>11.92%</td><td>0.65<br><small>(0.56–0.73)</small></td><td>−10.03%</td><td>−0.02</td><td>13.1×</td></tr>
    <tr><th scope="row">OLS</th><td>7.17%</td><td>8.67%</td><td>0.83<br><small>(0.73–1.01)</small></td><td>−7.91%</td><td>0.07</td><td>26.8×</td></tr>
    <tr><th scope="row">Ridge</th><td>7.08%</td><td>8.98%</td><td>0.79<br><small>(0.72–0.92)</small></td><td>−8.28%</td><td>0.07</td><td>26.3×</td></tr>
  </tbody>
</table>

After 2021, the fixed rule earns more net return than either regression,
with more volatility and a lower Sharpe. The learned models improve
risk-adjusted performance, with higher Sharpe on each of the three schedules
in both periods, but have no consistent net-return advantage.

Ridge adds little over OLS here. Their portfolio paths are close, neither
has a consistent Sharpe advantage across periods and schedules, and Ridge
barely reduces trading. Both have shallower development drawdowns than the
fixed score (Figure 3). The cost estimate excludes borrow, financing and
market impact, so the extra trading remains a concern.

<div class="research-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/performance-and-drawdowns" mobile="/assets/multiple-linear-regression/performance-and-drawdowns_mobile" alt="Net growth on a logarithmic scale with a shared drawdown panel below for fixed weights, OLS, and Ridge" version="19" %}
</div>

<p class="figure-caption">Figure 3: Portfolio paths from the three scores. The mean daily net P&amp;L of the three schedules, on common active dates, compounded into an index starting at <span class="mathjax-ignore">$1</span> (log scale), with drawdowns below. Each portfolio retains its own risk level; Table 3 supplies the risk-adjusted comparison for development through 2021 and the later period from January 2022.</p>

### Learning weights on the same inputs

How much of that improvement comes from learning the weights? I repeat OLS
and Ridge using exactly the fixed rule's twelve predictors, keeping the
target, training windows and portfolio rules the same. Ridge keeps the
same $c=0.01$ penalty.

<table class="research-table comparison-table portfolio-card-table">
  <caption>Table 4: The same twelve inputs, different weights. Mean statistics across the three rebalance schedules, with min–max Sharpe in parentheses. Returns are net of 5 bp per dollar traded; annualization and trading conventions match Table 3.</caption>
  <thead>
    <tr><th>Score</th><th>Net return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Traded notional / year</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="6">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Fixed</th><td>6.81%</td><td>9.11%</td><td>0.75<br><small>(0.71–0.80)</small></td><td>−26.32%</td><td>14.4×</td></tr>
    <tr><th scope="row">OLS · 12</th><td>6.66%</td><td>8.27%</td><td>0.81<br><small>(0.78–0.82)</small></td><td>−26.63%</td><td>21.3×</td></tr>
    <tr><th scope="row">Ridge · 12</th><td>6.97%</td><td>8.41%</td><td>0.83<br><small>(0.79–0.86)</small></td><td>−26.74%</td><td>19.6×</td></tr>
    <tr class="period-heading"><th colspan="6">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Fixed</th><td>7.76%</td><td>11.92%</td><td>0.65<br><small>(0.56–0.73)</small></td><td>−10.03%</td><td>13.1×</td></tr>
    <tr><th scope="row">OLS · 12</th><td>7.28%</td><td>10.89%</td><td>0.67<br><small>(0.59–0.77)</small></td><td>−10.19%</td><td>17.4×</td></tr>
    <tr><th scope="row">Ridge · 12</th><td>7.72%</td><td>11.07%</td><td>0.70<br><small>(0.62–0.75)</small></td><td>−10.23%</td><td>16.0×</td></tr>
  </tbody>
</table>

Learning the weights alone gives a modest average Sharpe gain, with no
consistent net-return or drawdown advantage. It also raises trading. Ridge
does somewhat better than OLS on these inputs and trades less, but after
2021 each beats the fixed rule's Sharpe on only one of the three schedules.
The broader predictor set adds more of the volatility reduction seen in
Table 3, along with another increase in trading.

## What Ridge changes
{: #what-ridge-changes }

With the full 144-predictor set, Ridge reduces coefficient size and absolute
movement between refits by roughly one third, while the rankings barely
change. After normalizing each coefficient vector to unit length, the
vectors move by similar amounts for OLS and Ridge. Much of the apparent
stability comes from rescaling.

For stock selection, a positive rescaling of all coefficients leaves the
ordering unchanged. On the prediction blocks, OLS and Ridge have a daily
ranking correlation of 0.991, with about 14–15 of the 150 daily candidates
differing. The rebalance schedule determines when those differences lead
to trades.

To see why, consider combinations of the predictors that vary together.
Let $X_c$ denote the training inputs centred on their column means. The
eigenvectors $$\mathbf v_j$$ of $$G=X_c^\top X_c/n$$ identify those
combinations, and each eigenvalue $$\lambda_j$$ measures its variance.
For one fitted model, Ridge scales the OLS coefficient in each direction by

$$
\widehat\theta_{j,c}
=\frac{\lambda_j}{\lambda_j+c}\widehat\theta_{j,0},
\qquad \widehat\theta_{j,c}=\mathbf v_j^\top\widehat{\boldsymbol\beta}_c,
\quad \lambda_j>0.
$$

The smaller the variance, the stronger the shrinkage. [Hastie's Ridge
review](https://arxiv.org/html/2006.00371v2) (2024, Sections 2–3) develops
this interpretation. Across the twelve training windows and three date
subsamples, 86–91 of 144 eigenvalues lie below $0.1$ and shrink by
more than 9% at $c=0.01$; 15–17 lie below $0.01$ and shrink by more
than half. The directions below $0.1$ carry only 6.3–7.9% of total predictor
variance.[^diagnostics]

Where do the weights actually change? At each refit, I take Ridge minus OLS using
the coefficients averaged across the three training fits. I express this
difference, $$\Delta\boldsymbol\beta$$, along the eigenvectors of the pooled
training covariance $G$. Each represents a combination of predictors. The
equation gives a simple rule: a coefficient change affects scores more when
that combination varies more across the training observations ($\lambda_j$):

$$
\begin{aligned}
\frac{\lVert X_c\Delta\boldsymbol\beta\rVert_2^2}{n}
&=\Delta\boldsymbol\beta^\top G\Delta\boldsymbol\beta\\
&=\sum_j\lambda_j(\mathbf v_j^\top\Delta\boldsymbol\beta)^2.
\end{aligned}
$$

The 72 least-variable combinations contain 99.1% of the squared coefficient
difference, averaged across the twelve refits, but only 4.0% of predictor
variance. Ridge therefore makes most of its weight adjustments where they
have relatively little effect on scores.

## Reading the predictors

Figure 4 shows the ten largest average absolute Ridge weights.
A positive weight raises a stock's score as its rank on that predictor
rises; a negative weight lowers it, holding the other ranks fixed.

<div class="research-figure coefficient-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/top-coefficients" alt="Signed coefficients for the ten largest mean absolute Ridge weights across walk-forward refits" version="12" %}
</div>

<p class="figure-caption">Figure 4: The ten largest mean absolute Ridge coefficients, averaged across the three training subsamples at each refit. Signs persist while most magnitudes decline; the rows are selected using the full coefficient history.</p>

The clearest pattern is longer-term strength with a short-term reversal
component. Price relative to its six-month moving average, historical
six-month Sharpe and the past year's return all receive positive weights.
So does the fraction of days spent above the 200-day moving average over
the past two years. Together, these terms favour stronger, more persistent
trends. The negative 10/21-day MACD weight then favours weaker recent
momentum among otherwise similar stocks. I read this combination as looking
for longer-term strength without chasing the latest upward move.

The negative weight on the 90-day high relative to the window-start price
adds another distinction between price paths. This predictor measures how
far the price had run up within that earlier window, excluding the latest
ten days. For similar values of the other trend measures, a larger earlier
run-up lowers the score. The model is learning contrasts between horizons
and aspects of the price path, rather than giving every momentum measure
the same sign.

Liquidity matters too. The negative illiquidity weight favours stocks with
less absolute price movement per dollar traded. The market-cap variability
terms contrast different horizons: the two-year measure has a positive
weight, while the one-month measure has a negative weight. This pair favours
more variation over the longer history and a quieter recent month. These
features describe variation in log market capitalization over time.

One-year upside volatility has a positive weight.
Conditional on the other predictors, more variation in the positive part of
daily returns raises the score. This is a different treatment of risk from
the fixed rule's general preference for lower volatility.

All ten signs persist across the twelve refits, which makes this a fairly
consistent description of the fitted score. But these are ten terms in a
144-predictor model, and several describe similar characteristics. A large
coefficient can help offset another input. To establish which predictor
families improve performance, I would need to remove them and refit; the
heatmap alone cannot attribute the portfolio's returns to them.

## Where this leaves me

The three-theme rule is competitive. With 144 predictors, OLS and Ridge
improve Sharpe and drawdowns, but their small development-period net-return
advantage reverses later, while trading roughly doubles. Learning weights
on the same twelve inputs adds only a modest Sharpe gain. These are
improvements, but given the extra complexity, I don't find them especially
impressive.

I still prefer a small Ridge penalty when predictors overlap this much.
It moderates the uncertain contrasts between them, although with the full
predictor set that changes stock selection too little to give Ridge a
clear portfolio advantage over OLS.

These results also depend on how I size the selected stocks. Here, net and
market exposure emerge from the positions. In the
[optimization article](/quants/2026/08/29/portfolio-optimization.html), I take
more control over portfolio risk and exposures.

A ranked-return target would be a useful next comparison: how much does
adjusting the training outcome for future volatility actually add?
