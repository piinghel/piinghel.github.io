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
in advance. Each ingredient enters as a rank among eligible stocks on that
date, on the common scale described below.

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

Equal theme weights are easy to understand, but they do not tell me how much
each overlapping horizon adds. I can instead learn the weights jointly from
historical outcomes. Here I compare the twelve-input rule with ordinary
least squares (OLS) and Ridge on a broader set of 144 predictors. That tests
the learned approach as a whole, changing both inputs and weights; comparing
OLS with Ridge keeps the inputs fixed and isolates regularization. All three
use the same eligible stocks.

## Supervised learning

The target, normalization and sampling choices determine what the regression
learns from the historical stock-date observations.

### Choosing the target
{: #what-i-ask-the-model-to-predict }

The first choice is what a successful stock selection should deliver. I use
each stock's forward 20-session Sharpe ratio: mean daily return divided by
daily return volatility over those sessions. This continues the interest in
risk-adjusted performance from the low-volatility article, while allowing
several predictors to inform the selection. Past volatility is an input;
future return relative to future volatility is the outcome to be learned.

This target makes both parts of that ratio matter. For the same positive
average return, a stock with lower realized volatility has a higher target
value. For a negative average return, dividing by lower volatility makes the
ratio more negative. The learning problem therefore concerns the joint
behaviour of return and risk.

Twenty sessions covers roughly a trading month, close to the portfolio's
three-week rebalance interval. The target measures a fixed forward window;
portfolio results will also depend on selection, sizing and trading costs.

I then rank these forward Sharpe ratios within each date and sector and
map them into $[-1,1]$. A high label identifies a stock that subsequently
performs well relative to its sector peers. The fitted score estimates that
relative standing; expected returns in percentage points would require a
separate mapping.

### Representing the predictors

To predict that outcome, both regressions use 144 predictors, mostly based
on prices and trading activity: momentum and trend, volatility, liquidity,
size and short positioning. Several horizons capture recent and longer-term
behaviour, while introducing substantial overlap between the inputs.

The universe uses point-in-time Russell 1000 membership, excluding stocks below
five dollars, announced merger targets and duplicate share classes. On each
date, I rank eligible stocks on each predictor across this whole universe and
map the ranks into $[-1,1]$.[^rank-scaling]

### What ranking changes

Ranking puts those different units on a bounded, comparable scale. For a
non-flat group of $N$ distinct observations, the transformation used here is

$$
z_i=2\frac{\operatorname{rank}(x_i)}{N}-1.
$$

The smallest value becomes $-1+2/N$ and the largest becomes $1$. With many
distinct observations, the values form an approximately uniform grid over
$[-1,1]$. Ties, imputation and changing group sizes affect the exact
distribution.[^rank-convention]

For example, a stock's momentum can rise from −2% to +10% while its rank
stays unchanged if it keeps the same relative position. This is the stability
I want when pooling history: changes in market-wide levels or dispersion
leave the input scale comparable, and extreme raw values have bounded
influence through that predictor. Ranking the target likewise prevents a
few extreme realized Sharpe ratios from dominating the loss through their
raw magnitude.

The cost is that the model loses those absolute levels and distances.
Adjacent stocks receive the same rank gap whether their momentum differs
by one or twenty percentage points. For the target, a narrow win over sector
peers and a large one can receive the same label. Those discarded magnitudes
may contain predictive information.

This gives a useful, limited form of stationarity: the **marginal
cross-sectional distributions** are approximately stable by construction.
A stock's ranks can still be persistent, correlations between predictors can
change, and their relationship with future outcomes can shift.

The normalization groups also matter. A stock can rank highly on market-wide
momentum while having only middling subsequent performance within its sector.
The model learns from that pairing. Since predictor ranks and portfolio
selection span sectors, sector exposures can remain in the portfolio.

[^rank-scaling]: Gu, Kelly and Xiu, [*Empirical Asset Pricing via Machine Learning*](https://dachxiu.chicagobooth.edu/download/ML_BKP.pdf#page=24), author manuscript of 13 September 2019, physical PDF page 24, footnote 29, also rank stock characteristics period by period and map them into $[-1,1]$. Here I additionally rank the forward Sharpe target within each date and sector.

[^rank-convention]: Tied values share a dense rank; the divisor is the largest rank in the group. Flat groups map to zero. Without ties, the largest rank equals $N$, giving the formula above. Missing predictor ranks receive a neutral zero fallback.

### The feature matrix
{: #building-the-training-matrix }

Indexed by date and asset ID, the feature matrix $X$ has $n$ stock-date rows
and 144 ranked predictor columns; I give each training row equal weight,
so dates with more usable stocks contribute more to the loss.

### Breadth and dependence

The row count overstates the independent information in this sample.
Consecutive 126-session momentum signals share almost all of their return
window, and consecutive forward 20-session targets share 19 daily returns.
Daily observations give repeated views of a limited history of market
conditions.

For independent daily returns, $T$ overlapping 20-session means carry roughly
$T/20$ independent-observation equivalents for estimating their mean: about
45 for 900 dates.[^overlap] Our ranked Sharpe labels, persistent predictors
and shared stock shocks require their own dependence calculation.

Cross-sectional breadth adds variation: stocks on the same date differ in
characteristics and subsequent outcomes. Pooling lets the model learn from
those differences as well as changes through time, assuming the predictive
relationship is sufficiently shared across stocks and dates.[^panel-pooling]

Stocks also share market and sector shocks, and firms with similar
characteristics can move together. Ranking within sectors leaves dependence
between their outcomes, so breadth adds less information than the same
number of independent stocks would.

[^overlap]: In the independent, equal-variance daily-return example, overlapping 20-session means have lag correlation $\rho_k=1-k/20$ for $1\leq k<20$ and zero thereafter. The large-$T$ effective sample size for their sample mean is $T/(1+2\sum_{k=1}^{19}\rho_k)=T/20$. This illustrative calculation concerns a time-series mean, not the ranked Sharpe regression.

[^panel-pooling]: Gu, Kelly and Xiu, [*Empirical Asset Pricing via Machine Learning*](https://dachxiu.chicagobooth.edu/download/ML_BKP.pdf#page=9), author manuscript of 13 September 2019, physical PDF page 9, describe learning a common predictive function across stocks and time. Here that pooling principle is applied to a ranked risk-adjusted target.

## Learning the weights
{: #learning-the-combination }

I fit the weights jointly to the historical predictor–target pairs. With
$z_{i,j,t}$ denoting stock $i$'s rank on predictor $j$ at date $t$, each
regression produces a score[^score-range]:

$$
\widehat y_{i,t}
=\widehat a+\sum_{j=1}^{144}\widehat\beta_j z_{i,j,t}.
$$

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

Let $X_c$ denote $X$ centred using its training column means. Ridge's effect
is clearest in the eigenvectors $$\mathbf v_j$$ of the predictor covariance
$$G=X_c^\top X_c/n$$, with eigenvalues $$\lambda_j$$. Writing
$$\widehat\theta_{j,c}=\mathbf v_j^\top\widehat{\boldsymbol\beta}_c$$ gives:

$$
\widehat\theta_{j,c}
=\frac{\lambda_j}{\lambda_j+c}\widehat\theta_{j,0},
\qquad \lambda_j>0.
$$

The smaller the variation in a direction, the stronger the shrinkage.
This moderates the uncertain contrasts between overlapping predictors,
at the cost of biasing their estimated contributions toward zero. A
low-variance direction may still be useful for prediction; the penalty
controls how much of that estimation risk the model accepts.[^ridge-theory]

I use $c=0.01$ in the mean-squared-error objective. Equivalently, the penalty
on a sum-of-squares objective is $\alpha=nc$, preserving its scale as the
training sample expands. Because coefficient size depends on predictor units,
the common rank scaling also determines how this penalty treats the inputs.

To put that choice in context, I reconstruct $G$ for each of the twelve
training windows and its three date subsamples. Of the 144 eigenvalues,
86–91 lie below $0.1$, accounting for 6.3–7.9% of total predictor variance;
15–17 lie below $0.01$. At $c=0.01$, a direction with
$\lambda=0.1$ retains about 91% of its OLS coefficient; one with
$\lambda=0.01$ retains 50%. The penalty therefore materially shrinks some
directions, even though the final stock rankings remain close. These counts
describe the strength of the chosen penalty; they do not establish that it
is the best choice.[^spectrum-diagnostic]

[^spectrum-diagnostic]: [Eigenvalue counts by fit](/assets/multiple-linear-regression/evidence/spectrum_by_fit.csv) and [variance shares](/assets/multiple-linear-regression/evidence/low_spectrum_variance_by_member.csv), reconstructed from the retained normalized inputs and recorded training windows, after dropping missing targets and selecting each date subsample. The covariance is centred separately within each fit. Original training-input hashes were not captured, so this checks the retained design rather than independently reproducing the original fits.

[^score-range]: The inputs and observed target lie within $[-1,1]$, but fitted linear scores can extend beyond that interval.

[^ridge-theory]: Trevor Hastie, [*Ridge Regularization: an Essential Concept in Data Science*](https://arxiv.org/html/2006.00371v2), arXiv version 2 (2024), Sections 2–3, gives the spectral and bias–variance formulations. Here the objective is divided by $n$, so its sum-of-squares penalty corresponds to $nc$. The technical note at the end gives the covariance expressions.

## Fitting through time

The regression formula defines one fit. To evaluate a sequence of forecasts,
I also need to decide which dates enter each fit and when to update it.

### Expanding walk-forward
{: #from-predictions-to-portfolios }

Walk-forward sets the chronological training and prediction windows. At each
refit, I use the history available at that point, then hold the fitted
coefficients fixed while predicting the following block. Those boundaries
are a separate choice from the date sampling inside each training window.

I use an **expanding window**, beginning in January 1995. The first training
window contains 900 trading dates. A 21-date gap allows the forward
20-session training outcomes to finish before predictions begin. I then
predict the next 600 dates and refit, keeping the January 1995 start and
extending the training endpoint by 600 dates. Figure 1 shows the first
three windows.[^chronological-training]

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/expanding-walk-forward" mobile="/assets/multiple-linear-regression/expanding-walk-forward_mobile" alt="Three expanding walk-forward fits share a January 1995 start. Training grows from 900 to 1500 to 2100 dates. Each training window is followed by a gap and a subsequent prediction block." version="2" %}
</div>

<p class="figure-caption"><strong>Figure 1: Expanding walk-forward.</strong> Each refit retains the earlier history and adds 600 training dates. The 21-date gap precedes each 600-date prediction block. Recent dates enter training once their forward outcomes are available. Widths are schematic; the final prediction block can be shorter.</p>

Keeping the older history adds observations but retains older relationships;
a rolling window would drop the earliest dates. OLS and Ridge share the
same expanding windows and refit schedule, with predictions beginning in
September 1998.[^training]

I report results through December 2021 and for January 2022–May 2026 separately.

[^chronological-training]: Hyndman and Athanasopoulos, [*Forecasting: Principles and Practice*, third edition, Section 5.10](https://otexts.com/fpp3/tscv.html), illustrate evaluation with a rolling forecasting origin and an expanding training set. Here the gap also accommodates the forward outcome window.

### Sampling the training dates

Within each of these training windows, I can fit every eligible date or
select more widely spaced cross-sections. This changes the rows used by
each model while keeping the walk-forward boundaries fixed.

Keeping every fifth trading date gives roughly a weekly sample and one
fifth of the rows. Some omitted observations are redundant; others capture
changes the sparse sample misses. Fitting all five offsets separately and
averaging their predictions uses every date collectively, while spacing out
each model's observations. The models remain dependent: even five sessions
apart, 20-session targets share 15 returns.

The reported study uses **three offsets**, sampling every third trading
date, as Figure 2 shows. Each model receives complete cross-sections from
its assigned dates, and I average their predictions for the same stock and
forecast date.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/date-sampling" mobile="/assets/multiple-linear-regression/date-sampling_mobile" alt="Three models within one training window: model 1 uses dates 1, 4, 7; model 2 uses 2, 5, 8; model 3 uses 3, 6, 9. Their prediction scores are averaged." version="1" %}
</div>

<p class="figure-caption"><strong>Figure 2: Interleaved training dates.</strong> The first nine eligible dates illustrate the three offsets used in the study. Each selected date contributes a full cross-section. The same construction is applied within each training window.</p>

## Prediction quality
{: #prediction-quality-and-portfolio-results }

OLS and Ridge have almost identical mean daily information coefficients
(IC) in both periods (Table 2).
IC is the cross-sectional Spearman correlation between the score and the
forward sector-relative Sharpe target. A positive value means higher scores
tend to identify better subsequent outcomes. The small development gain
from Ridge disappears later.

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

Both regressions have higher mean IC than the fixed score during development,
with less variation in daily IC. After 2021, the fixed score has the highest
mean IC, while the regressions still have less variable daily IC. The broader
learned combination therefore improves average ordering in the first period,
but that advantage does not persist in the later one.

IC measures ordering across the whole cross-section. To see what these
scores deliver after costs, I next turn them into portfolios using the same
selection, sizing and trading rules.

## From scores to portfolios
{: #portfolio-construction }

On each forecast date, I rank the available predictors and compute three
sets of stock scores: the benchmark's fixed combination, the averaged OLS
predictions and the averaged Ridge predictions. Each ranking feeds the same
portfolio rule: buy the top 75 stocks, short the bottom 75, and size inversely
to volatility with stock and book caps. I rebalance every three weeks with
next-close execution and charge 5 bp per dollar traded.

Holding selection and sizing rules fixed lets me compare what the scores
add. Returns use arithmetic annualization, and Sharpe assumes a zero cash
rate. Two-way turnover counts purchases and sales relative to strategy
capital, annualized.

For each score, I run three rebalance schedules, starting one week apart:
weeks 1, 4, 7, …; weeks 2, 5, 8, …; and weeks 3, 6, 9, …. These schedules
determine when to act on each score and show how the comparison depends on
the starting week.

Table 3 averages the statistics calculated separately for the three
schedules. Figure 3 averages their daily net P&L and compounds that series
into an index. The mean of schedule-level Sharpes and the Sharpe of an
averaged return series are different calculations.

Splitting capital across staggered schedules is called tranching. I examine
its effect on timing risk in the
[rebalance-schedules article](/quants/2025/05/10/rebalancing-luck.html).

## Portfolio results

During development, OLS earns slightly more net return than the fixed score,
with lower volatility and a shallower maximum drawdown (Table 3). Extra trading
consumes 0.74 percentage points of its 1.08-point gross-return advantage. That
leaves most of the Sharpe improvement coming from lower volatility.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 3: Net performance, market beta and trading.</strong> Mean of three schedule-level statistics, after 5 bp per dollar traded. Arithmetic return and volatility are annualized; traded notional is annual two-way trading divided by strategy capital. Market beta is the slope from regressing daily net strategy returns on the Russell 1000 benchmark returns, with an intercept, within each period.</caption>
  <thead>
    <tr><th>Score</th><th>Net return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Market beta</th><th>Traded notional / year</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="7">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Fixed</th><td>6.81%</td><td>9.11%</td><td>0.75</td><td>−26.32%</td><td>0.07</td><td>14.4×</td></tr>
    <tr><th scope="row">OLS</th><td>7.14%</td><td>7.14%</td><td>1.00</td><td>−18.31%</td><td>0.08</td><td>29.3×</td></tr>
    <tr><th scope="row">Ridge</th><td>7.40%</td><td>7.36%</td><td>1.01</td><td>−18.46%</td><td>0.09</td><td>29.0×</td></tr>
    <tr class="period-heading"><th colspan="7">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Fixed</th><td>7.76%</td><td>11.92%</td><td>0.65</td><td>−10.03%</td><td>−0.02</td><td>13.1×</td></tr>
    <tr><th scope="row">OLS</th><td>7.17%</td><td>8.67%</td><td>0.83</td><td>−7.91%</td><td>0.07</td><td>26.8×</td></tr>
    <tr><th scope="row">Ridge</th><td>7.08%</td><td>8.98%</td><td>0.79</td><td>−8.28%</td><td>0.07</td><td>26.3×</td></tr>
  </tbody>
</table>

Market beta is small for all three and slightly higher for the regressions
in both periods. Their lower volatility therefore does not come from lower
constant market exposure. Removing the fitted market component leaves
development volatility at 9.01% for the fixed rule, 6.96% for OLS and 7.16%
for Ridge; the gap also remains later. This check still leaves the effects
of stock selection, sizing, changing beta and other factor exposures
unseparated.[^beta-diagnostic]

[^beta-diagnostic]: [Beta summaries](/assets/multiple-linear-regression/evidence/beta_schedule_means.csv) and [individual schedules](/assets/multiple-linear-regression/evidence/beta_by_schedule.csv) use the saved daily net strategy and market returns. Residual volatility is the annualized standard deviation after subtracting the fitted intercept and market component. Each estimate uses one constant beta per schedule and reporting period; summaries average the three schedules equally.

After 2021, the fixed rule earns more net return than either regression, with
more volatility and a lower Sharpe. Ridge's volatility is about 19% below the
fixed rule during development and 25% below it later, but its annual net-return
advantage moves from +0.59 percentage points to −0.68 points. The improvement
is therefore in risk-adjusted performance, with no consistent net-return
advantage over the three-factor benchmark.

The OLS–Ridge difference is much smaller. Ridge's 0.25-point development return
gain comes with higher volatility, leaving both Sharpes close to 1.00. That
small Sharpe difference changes sign across the three starting-week schedules;
after 2021, Ridge's mean Sharpe is 0.79 versus 0.83 for OLS. It saves less than
0.03 percentage points in annual trading costs in either period. Regularizing
the coefficients has done little to reduce the trading bill. The flat charge
also omits borrow, financing and market impact.

OLS and Ridge also follow close portfolio paths, while both have shallower
development drawdowns than the fixed score (Figure 3). Their lower risk may
reflect the target, the stocks selected and the resulting exposures; this
comparison does not separate those contributions.

<div class="research-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/performance-and-drawdowns" mobile="/assets/multiple-linear-regression/performance-and-drawdowns_mobile" alt="Net growth on a logarithmic scale with a shared drawdown panel below for fixed weights, OLS, and Ridge" version="19" %}
</div>

<p class="figure-caption"><strong>Figure 3: Portfolio paths from the three scores.</strong> The mean daily net P&amp;L of the three schedules, on common active dates, compounded into an index starting at <span class="mathjax-ignore">$1</span> (log scale), with drawdowns below. Each portfolio retains its own risk level; Table 3 supplies the risk-adjusted comparison for development through 2021 and the later period from January 2022.</p>

## What Ridge changes
{: #what-ridge-changes }

The close OLS–Ridge results raise a useful question about the combination:
how much has regularization changed the fitted relationship? Ridge reduces
coefficient size and absolute movement between refits by roughly one third.
Yet after normalizing each coefficient vector to unit length, the vectors
move by similar amounts for OLS and Ridge. Much of the apparent coefficient
stability comes from the smaller scale. Shrinking a vector also reduces its
absolute movement even when its change in direction stays the same.

For stock selection, a positive rescaling of all coefficients leaves the
ordering unchanged. The relevant empirical check is how much regularization
changes the rankings: their daily correlation is 0.991, and only about 14–15
of the 150 daily candidates differ between OLS and Ridge. The coefficient
changes translate into limited changes in the portfolio's candidate set.
These are daily candidate comparisons; the rebalance schedule determines
when a changed selection leads to a trade.

To locate the difference, I subtract the OLS coefficient vector from the
Ridge vector at each refit, using the saved ensemble-average weights, and
project $$\Delta\boldsymbol\beta$$ onto the eigenvectors of the pooled
training covariance $G$. The resulting change in centred training scores is
$$X_c\Delta\boldsymbol\beta$$, with mean squared difference:

$$
\begin{aligned}
\frac{\lVert X_c\Delta\boldsymbol\beta\rVert_2^2}{n}
&=\Delta\boldsymbol\beta^\top G\Delta\boldsymbol\beta\\
&=\sum_j\lambda_j(\mathbf v_j^\top\Delta\boldsymbol\beta)^2.
\end{aligned}
$$

The lowest 72 eigenvalue directions contain **99.1% of the squared
coefficient difference**, averaged across the twelve refits, while accounting
for only **4.0% of predictor variance**.[^coefficient-projection] Ridge changes
the weights mainly along contrasts that vary little in the training data.
That helps explain how coefficients can change substantially while scores
remain close. The observed ranking correlation checks what happens on the
following prediction blocks; relationships can change beyond the training
window.

[^coefficient-projection]: [Projection by refit](/assets/multiple-linear-regression/evidence/projection_by_refit.csv). The bottom half contains the 72 smallest eigenvalues of each refit's pooled valid-target training covariance. Its coefficient share is $\sum_{j=1}^{72}(\mathbf v_j^\top\Delta\boldsymbol\beta)^2/\lVert\Delta\boldsymbol\beta\rVert_2^2$, ranging from 98.6% to 99.4%. The reported 99.1% is the equal mean across refits; 4.0% averages the corresponding predictor-variance shares. This uses the stored ensemble coefficients and the retained-input reconstruction described above.

The ten largest mean absolute Ridge coefficients keep the same sign across
all twelve refits (Figure 4). Price relative to its 126-day moving
average stays positive, while 10/21-day MACD stays negative; both remain among
the ten largest weights at every refit. Holding the other predictor ranks
fixed, they favor relative longer-term strength with weaker recent momentum.

<div class="research-figure coefficient-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/top-coefficients" alt="Signed coefficients for the ten largest mean absolute Ridge weights across walk-forward refits" version="12" %}
</div>

<p class="figure-caption"><strong>Figure 4:</strong> The ten largest mean absolute Ridge coefficients, averaged across the three training subsamples at each refit. Signs persist while most magnitudes decline; the rows are selected using the full coefficient history.</p>

These signs describe conditional relationships with the target. A large
coefficient can reflect a contrast between correlated predictors, so its
magnitude alone is a poor measure of a signal's standalone importance.
That is the distinction between assigning weights to familiar factor themes
and estimating a joint predictive relationship: the fitted combination can
use differences within a theme as well as exposure to the theme itself.

## Where this leaves me

The three-factor model is quite competitive. A fixed combination of momentum,
defensive signals and short positioning gets close to the learned models with
far fewer inputs and roughly half the trading. OLS and Ridge improve Sharpe
and reduce drawdowns, but their net-return advantage is small during
development and reverses later. I see that as a modest improvement overall;
given the additional complexity, I don't find it particularly impressive.

Within the linear models, I naturally prefer a small Ridge penalty. Many of
these predictors overlap by construction, so allowing some shrinkage is a
sensible modelling choice. The case for it is the estimation problem itself:
the portfolio results give me little reason to prefer Ridge over OLS, but
also show little cost to that preference at the penalty used here.

The most useful next comparison is to fit OLS and Ridge on the
three-factor benchmark's same twelve inputs. That would separate the value of
learning the weights from the value of expanding the predictor set. Comparing
ranked forward returns with ranked forward Sharpe would isolate the target's
volatility adjustment. Repricing the same trades at 10 bp would show how
sensitive the learned models' small development-period net-return advantage
is to higher costs.

<details markdown="1">
<summary>Technical note: Ridge estimation and coefficient movement</summary>

**Dependence in the panel.** For the centred target vector $\mathbf y_c$,
write the working model as
$$\mathbf y_c=X_c\boldsymbol\beta^\star+\boldsymbol\varepsilon$$,
$$\Omega=\operatorname{Var}(\boldsymbol\varepsilon\mid X_c)$$ captures
cross-sectional dependence and overlapping outcomes after centring.
For $c>0$, the coefficient covariance is:

$$
\begin{gathered}
\operatorname{Var}(\widehat{\boldsymbol\beta}_c\mid X_c)\\
=(G+cI)^{-1}\frac{X_c^\top\Omega X_c}{n^2}(G+cI)^{-1}.
\end{gathered}
$$

The term $$X_c^\top\Omega X_c$$ makes coefficient uncertainty depend on
how residual dependence aligns with the predictors. A single effective row
count cannot describe uncertainty in every coefficient direction.

**Magnitude and direction.** Write the coefficient vector at refit $k$ as
$$\boldsymbol\beta_k=a_k\mathbf u_k$$, where
$$a_k=\lVert\boldsymbol\beta_k\rVert_2>0$$ and
$$\lVert\mathbf u_k\rVert_2=1$$. Then:

$$
\begin{aligned}
\lVert\boldsymbol\beta_{k+1}-\boldsymbol\beta_k\rVert_2^2
&=(a_{k+1}-a_k)^2\\
&\quad+a_{k+1}a_k\lVert\mathbf u_{k+1}-\mathbf u_k\rVert_2^2.
\end{aligned}
$$

The first term measures changes in magnitude; the second measures changes in
direction, weighted by the two magnitudes. Shrinking both vectors reduces
absolute movement even if their angular change stays the same.

</details>


[^training]: The first fit uses 900 trading dates, followed by a 21-date gap.
    I refit every 600 dates, expanding the training history, for twelve refits.
    The last prediction block ends with the available sample.
