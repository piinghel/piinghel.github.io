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
use the same stocks.

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

Lower future volatility amplifies both positive and negative average returns
in this target, so the model learns about return and risk together.

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
uniform over time, although ties and changing group sizes affect the exact
grid.[^rank-convention] This keeps scales comparable when pooling history and
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

[^rank-convention]: Without ties, the range is $[-1+2/N,1]$. Ties share a dense rank, divided by the largest rank in the group; flat groups and missing predictor ranks receive zero. Gu, Kelly and Xiu, [*Empirical Asset Pricing via Machine Learning*](https://dachxiu.chicagobooth.edu/download/ML_BKP.pdf), manuscript of 13 September 2019, physical PDF pages 9 and 24, describe pooling across stocks and time and ranking characteristics into $[-1,1]$. Here the target is also ranked, within each date and sector.

### The feature matrix
{: #building-the-training-matrix }

Indexed by date and asset ID, the feature matrix $X$ has $n$ stock-date rows
and 144 ranked predictor columns; I give each training row equal weight,
so dates with more usable stocks contribute more to the loss.

### Breadth and dependence

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
controls how much of that estimation risk the model accepts. [Hastie’s Ridge
review](https://arxiv.org/html/2006.00371v2) (2024, Sections 2–3) develops this
spectral interpretation and the bias–variance trade-off.

I use $c=0.01$ in the mean-squared-error objective. Equivalently, the penalty
on a sum-of-squares objective is $\alpha=nc$, preserving its scale as the
training sample expands. Because coefficient size depends on predictor units,
the common rank scaling also determines how this penalty treats the inputs.

Across the twelve training windows and three date subsamples, **86–91 of
144 eigenvalues lie below $0.1$**. At $c=0.01$, those directions shrink by
more than 9%; **15–17 lie below $0.01$** and shrink by more than half.
The penalty reaches most directions, but those below $0.1$ account for only
6.3–7.9% of total predictor variance. That distinction matters when judging
how much the penalty changes predictions. These counts describe the chosen
penalty; a sensitivity test would be needed to choose it empirically.[^diagnostics]

[^diagnostics]: The [aggregate evidence](https://github.com/piinghel/piinghel.github.io/tree/main/assets/multiple-linear-regression/evidence) includes spectra, coefficient projections, beta estimates and schedule-level results. Training covariances use the retained normalized inputs and recorded windows, dropping missing targets. Original training-input hashes were not captured, so these diagnostics reconstruct the retained design rather than independently reproducing the original fits.

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
three windows.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/expanding-walk-forward" mobile="/assets/multiple-linear-regression/expanding-walk-forward_mobile" alt="Three expanding walk-forward fits share a January 1995 start. Training grows from 900 to 1500 to 2100 dates. Each training window is followed by a gap and a subsequent prediction block." version="2" %}
</div>

<p class="figure-caption"><strong>Figure 1: Expanding walk-forward.</strong> Each refit retains the earlier history and adds 600 training dates. The 21-date gap precedes each 600-date prediction block. Recent dates enter training once their forward outcomes are available. Widths are schematic; the final prediction block can be shorter.</p>

Keeping the older history adds observations but retains older relationships;
a rolling window would drop the earliest dates. OLS and Ridge share the
same twelve expanding windows, with predictions beginning in September 1998.

I report results through December 2021 and for January 2022–May 2026 separately.

### Sampling the training dates

Within each training window, I use **three offsets**: one model gets dates
1, 4, 7, …; the next gets 2, 5, 8, …; and the third gets 3, 6, 9, … (Figure 2).
Each receives complete cross-sections from its dates, and I average their
predictions for each stock and forecast date. This spreads out each model's
observations while using all dates collectively. Dependence remains:
20-session targets three dates apart still share 17 returns. The expanding
walk-forward boundaries stay the same.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/date-sampling" mobile="/assets/multiple-linear-regression/date-sampling_mobile" alt="Three models within one training window: model 1 uses dates 1, 4, 7; model 2 uses 2, 5, 8; model 3 uses 3, 6, 9. Their prediction scores are averaged." version="2" %}
</div>

<p class="figure-caption"><strong>Figure 2: Interleaved training dates.</strong> The first nine training dates illustrate the three offsets used in the study. Each selected date contributes a full cross-section. The same construction is applied within each training window.</p>

## Prediction quality
{: #prediction-quality-and-portfolio-results }

OLS and Ridge have almost identical ranking quality: both beat the fixed
score during development, but the fixed score has the highest mean information
coefficient (IC) after 2021. The regressions' daily IC is less variable in both periods
(Table 2). I measure IC as the cross-sectional Spearman correlation between
the score and the forward sector-relative Sharpe target.

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

Splitting capital across staggered schedules is called tranching. I examine
its effect on timing risk in the
[rebalance-schedules article](/quants/2025/05/10/rebalancing-luck.html).[^schedule-summary]

[^schedule-summary]: Table 3 averages statistics calculated separately for the three schedules. Figure 3 compounds their mean daily net P&L on common dates. Averaging schedule-level Sharpes differs from calculating the Sharpe of that averaged return series.

## Portfolio results

The regressions' main gain is lower volatility, despite slightly higher
market beta (Table 3). During development, OLS earns only slightly more net
return than the fixed score: extra trading consumes 0.74 percentage points
of its 1.08-point gross-return advantage.

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
for Ridge; the gap also remains later. This does not separate stock selection
from sizing, changing beta or other factor exposures.

After 2021, the fixed rule earns more net return than either regression,
with more volatility and a lower Sharpe. The learned models improve
risk-adjusted performance, but have no consistent net-return advantage.

The OLS–Ridge difference is much smaller. Ridge's 0.25-point development return
gain comes with higher volatility, leaving both Sharpes close to 1.00. That
small Sharpe difference changes sign across the three starting-week schedules;
after 2021, Ridge's mean Sharpe is 0.79 versus 0.83 for OLS. It saves less than
0.03 percentage points in annual trading costs in either period. Regularizing
the coefficients has done little to reduce the trading bill. The flat charge
also omits borrow, financing and market impact.

OLS and Ridge follow close portfolio paths, while both have shallower
development drawdowns than the fixed score (Figure 3).

<div class="research-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/performance-and-drawdowns" mobile="/assets/multiple-linear-regression/performance-and-drawdowns_mobile" alt="Net growth on a logarithmic scale with a shared drawdown panel below for fixed weights, OLS, and Ridge" version="19" %}
</div>

<p class="figure-caption"><strong>Figure 3: Portfolio paths from the three scores.</strong> The mean daily net P&amp;L of the three schedules, on common active dates, compounded into an index starting at <span class="mathjax-ignore">$1</span> (log scale), with drawdowns below. Each portfolio retains its own risk level; Table 3 supplies the risk-adjusted comparison for development through 2021 and the later period from January 2022.</p>

## What Ridge changes
{: #what-ridge-changes }

Ridge reduces coefficient size and absolute movement between refits by
roughly one third, while the rankings barely change. After normalizing each
coefficient vector to unit length, the vectors move by similar amounts for
OLS and Ridge. Much of the apparent stability comes from rescaling: a smaller
vector can move less in absolute terms even when its change in direction
stays the same.

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
for only **4.0% of predictor variance**. Ridge changes
the weights mainly along contrasts that vary little in the training data.
That helps explain how coefficients can change substantially while scores
remain close. The observed ranking correlation checks what happens on the
following prediction blocks; relationships can change beyond the training
window.

The ten largest mean absolute Ridge coefficients keep the same sign across
all twelve refits (Figure 4). Price relative to its 126-day moving
average stays positive, while 10/21-day MACD stays negative; both remain among
the ten largest weights at every refit. Holding the other predictor ranks
fixed, they favor relative longer-term strength with weaker recent momentum.

<div class="research-figure coefficient-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/top-coefficients" alt="Signed coefficients for the ten largest mean absolute Ridge weights across walk-forward refits" version="12" %}
</div>

<p class="figure-caption"><strong>Figure 4:</strong> The ten largest mean absolute Ridge coefficients, averaged across the three training subsamples at each refit. Signs persist while most magnitudes decline; the rows are selected using the full coefficient history.</p>

## Where this leaves me

The three-theme rule is competitive: twelve inputs and roughly half the
trading get close to the learned models. OLS and Ridge improve Sharpe and
drawdowns, but their small development-period net-return advantage reverses
later. Given the extra complexity, I don't find it impressive.

I prefer a small Ridge penalty when predictors overlap this much. Here it
shrinks most predictor directions by more than 9% and 15–17 by more than
half, yet OLS and Ridge rankings correlate at 0.991. The projection explains
why: 99.1% of their squared coefficient difference lies in directions
carrying only 4.0% of predictor variance. That supports regularizing the
weights, while the portfolio results give me little reason to prefer
Ridge over OLS at this penalty.

The lower volatility survives removing a constant market component, but this
comparison still combines stock selection with the exposures produced by
sizing. The sizing rule leaves net and market exposure to emerge from the
positions. In the [optimization article](/quants/2026/08/29/portfolio-optimization.html),
I treat portfolio risk and exposure limits as explicit choices.

To isolate what learning adds, I would next fit OLS and Ridge on the
benchmark's same twelve inputs. A ranked-return target would test the value
of the volatility adjustment, and repricing the trades at 10 bp would test
how much of the small net-return edge survives higher costs.
