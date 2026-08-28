---
layout: post
title: "From Volatility Scaling to State-Aware Portfolio Optimization"
last_modified_at: 2026-08-26
categories: ["Portfolio construction"]
article_label: Portfolio construction · Ridge allocation
permalink: /quants/portfolio-optimization-preview.html
---

<p class="article-summary">I compare three ways of turning the same Ridge forecasts into a long–short portfolio: a volatility-scaled portfolio, a standard optimizer that adds correlations and exposure constraints, and a state-aware optimizer that starts from existing holdings and discourages unnecessary turnover. Across the full history, the state-aware and standard optimizers produce almost the same gross return (13.17% versus 13.13%), but the state-aware optimizer cuts annualized turnover from 42.1 to 27.6. Its net return and Sharpe therefore rise to 11.62% and 1.33, from 10.77% and 1.24. This is a clear improvement, although rebalance timing, risk calibration, and realized beta control remain important risks.</p>

## Why volatility scaling is not enough

All three portfolios use the same Ridge forecasts. The existing
**volatility-scaled portfolio** selects the 75 strongest forecasts for its long
side and the 75 weakest forecasts for its short side. It gives more weight to
stronger signals and reduces the weight of more volatile stocks.

This is a useful starting point. It allocates according to both forecast
strength and individual-stock risk, and it adapts as volatility changes. But it
has three limitations:

- It does not account for correlations between stocks.
- It does not directly control net exposure, market beta, sectors, or total
  portfolio risk.
- It chooses a new portfolio without considering current holdings or the cost
  of replacing them.

I test two changes. The **standard optimizer** adds correlations, a portfolio
risk budget, and exposure constraints. The **state-aware optimizer** uses the
same framework but starts from the portfolio already held and discourages
unnecessary turnover.

## Data, forecasts, and validation

The Ridge model uses 144 ranked predictors, mostly derived from prices and
returns. They include momentum, volatility, moving-average position, RSI, ATR,
market correlation, turnover, and illiquidity. Ridge combines them to predict a
ranked forward Sharpe-like outcome.

I use exactly the same saved forecasts, universe, execution assumptions, and
transaction costs for all three portfolios. The comparison therefore tests
portfolio construction, not a change in the prediction model or trading setup.

Forecasts are generated with expanding walk-forward estimation. Results through
2021 are development evidence. January 2022 through May 2026 is a later
pseudo-holdout. Each portfolio is tested across three staggered rebalance
schedules and pays 5 basis points per dollar traded. The earlier
[Ridge article](/quants/2025/02/09/multiple-linear-regression.html) describes the
prediction methodology in full.

## Adding correlations and exposure constraints

The first change replaces name-by-name volatility scaling with portfolio-level
optimization. Traditional mean–variance optimization chooses weights by
balancing expected return against the variance of the complete portfolio. Let
$w$ denote portfolio weights, $\mu$ expected returns, and $\Sigma$ the
covariance matrix:

$$
\max_w \quad \mu^\top w-\frac{\gamma}{2}w^\top\Sigma w
$$

The first term rewards stocks with higher expected returns. The second
penalizes combinations of stocks that create more portfolio risk. Unlike
volatility scaling, this formulation accounts for correlations between
holdings.

Giuseppe Paleologo gives the same two views of the problem in Chapter 9 of
[*The Elements of Quantitative
Investing*](https://www.wiley.com/en-us/The+Elements+of+Quantitative+Investing-p-9781394265473).
One can choose the return–risk trade-off through $\gamma$, or maximize return
for a chosen level of risk. In the basic problem, the two formulations trace the
same efficient portfolios. With real constraints, the correspondence is not
always exact, but the economic choice is the same.

### Building the covariance matrix

The covariance matrix combines two quantities: each stock's volatility and the
correlation between every pair of stocks. I estimate them separately because
volatility can change quickly, while correlation is slower and noisier. The
calculation has three steps.

First, I divide each daily return by that stock's recent volatility. Let
$r_{i,\tau}$ be stock $i$'s daily return and $\widehat\sigma_{i,\tau}$ its
rolling volatility estimate:

$$
\widetilde r_{i,\tau}
=\frac{r_{i,\tau}}{\widehat\sigma_{i,\tau}}
$$

This removes the changing volatility scale. A large move in a normally quiet
stock is then comparable with a large move in a normally volatile stock.

Second, I use these standardized returns to estimate which stocks move together.
The correlation estimate uses a longer rolling history than the volatility
estimate. I then shrink the estimated correlation matrix toward the identity:

$$
\widehat C_t=\operatorname{Corr}(\widetilde r_\tau),
\qquad
C_t^{(\rho)}=(1-\rho)\widehat C_t+\rho I
$$

When $\rho=0$, the optimizer uses the estimated correlations as they are. When
$\rho=1$, it ignores cross-stock correlations. An intermediate value keeps
some dependence information while reducing the influence of estimation noise.

Third, I estimate each stock's current volatility separately and place those
estimates on the diagonal of $D_t$. I combine current volatilities with the
shrunk correlation matrix to obtain the covariance matrix:

$$
\Sigma_t=D_tC_t^{(\rho)}D_t
$$

Each entry in $\Sigma_t$ is therefore the volatility of stock $i$, multiplied by
its correlation with stock $j$, multiplied by the volatility of stock $j$. The
diagonal entries are the stocks' variances. The off-diagonal entries are their
covariances. This is the matrix the optimizer uses to calculate total portfolio
risk.

This split has a practical advantage. The short volatility window reacts to a
change in risk, while the longer correlation history uses more observations for
a quantity that is harder to estimate. Standardizing returns also prevents a
high-volatility period from dominating the correlation estimate. Adrian
Letchford explains the broader case in [*A Quant's Guide to Covariance Matrix
Estimation*](https://osquant.com/papers/a-quants-guide-to-covariance-matrix-estimation/).

The trade-off is that the two estimates move at different speeds. The volatility
estimate can be noisy, while the correlation estimate can lag a new market
regime. Shrinkage improves stability by pulling correlations toward zero, but it
also discards some real dependence.

### The optimization used here

The Ridge model produces a Sharpe-like score rather than an expected return. I
multiply that score by the stock's volatility forecast to put the objective on
a return scale. The standard optimizer then maximizes forecast return inside a
fixed portfolio-risk budget:

$$
\max_w \quad \mu^\top w
\qquad
\text{subject to}
\qquad
w^\top\Sigma w\leq \sigma_*^2
$$

The optimizer chooses the portfolio with the highest forecast return that
remains inside the ex-ante volatility budget. Sign and position limits keep
longs and shorts in their intended sleeves. Gross, net, beta, and sector limits
control the overall shape of the book. The implementation note records the
chosen risk budget and constraint values.

The move from volatility scaling to the standard optimizer changes more than
the covariance estimate. Ridge scores become return scores, and the optimizer
also adds a risk budget and exposure constraints. The comparison therefore
supports the complete allocation method, not the covariance model alone. The
[implementation note](/quants/portfolio-optimization-technical-note.html)
records the exact parameter values, return clipping, missing-value rules, matrix
repairs, and full constraint algebra.

## Accounting for current holdings and turnover

The standard optimizer calculates its preferred portfolio without considering
what the strategy already owns. A small improvement in forecast return can
therefore trigger a large and expensive trade.

The state-aware optimizer starts from the current portfolio and subtracts a
penalty for proposed trading:

$$
\max_w \quad
\mu^\top w-\lambda\lVert w-w^{-}\rVert_1
$$

Here $w^{-}$ is the portfolio before rebalancing. The second term penalizes
the amount traded. A position changes only when the forecast benefit is large
enough to justify the turnover penalty.

Fresh positions must still enter through the top or bottom 75 Ridge ranks, but
an existing holding may remain eligible until it falls beyond rank 175. This
allows acceptable positions to stay in the portfolio. The coefficient
$\lambda$ is a hyperparameter that controls how strongly the optimizer prefers
the current holdings. It is not an estimate of transaction costs and has no
basis-point interpretation. The backtest separately charges the realized cost
of 5 basis points per dollar traded.

## Results before and after 2022

Constrained optimization improves on volatility scaling during development.
Through 2021, the standard optimizer raises annualized net return from 8.92% to
11.60% and net Sharpe from 1.12 to 1.35. The state-aware optimizer improves
them further, to 12.32% and 1.43.

The later period separates the two optimizers. From January 2022 through May
2026, the standard optimizer falls behind the volatility-scaled portfolio. The
state-aware optimizer remains ahead, with a 7.99% net return and 0.87 net
Sharpe. The three state-aware schedules differ widely, however: their net-return
spread is 4.49 percentage points and their Sharpe spread is 0.43.

Both optimized portfolios also have lower realized market beta. During
development, their average beta is 0.08, compared with 0.09 for the
volatility-scaled portfolio. The difference is larger after 2022: beta falls
from 0.08 for volatility scaling to 0.02 for the standard optimizer and 0.01
for the state-aware optimizer. The exposure constraints therefore improve
average beta control, even though the recent drift discussed below remains a
risk.

<div class="research-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/performance-and-drawdowns" mobile_suffix="-mobile" alt="Net growth of one dollar on a logarithmic scale and drawdowns for the volatility-scaled portfolio, standard optimizer, and state-aware optimizer, with the later period beginning in 2022" version="4" %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Net cumulative wealth and drawdown for an equal-weight blend of the three rebalance schedules after charging 5 basis points per dollar traded, 22 September 1998–27 May 2026. The vertical rule marks January 2022, the start of the later pseudo-holdout.</p>

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Portfolio</th><th>Gross return</th><th>Net return</th><th>Net volatility</th><th>Net Sharpe</th><th>Beta</th><th>Max drawdown</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Volatility-scaled portfolio</th><td data-label="Gross return">10.58%</td><td data-label="Net return">8.92%</td><td data-label="Net volatility"><strong>7.92%</strong></td><td data-label="Net Sharpe">1.12</td><td data-label="Beta">0.09</td><td data-label="Max drawdown">19.63%</td></tr>
    <tr><th scope="row">Standard optimizer</th><td data-label="Gross return"><strong>14.00%</strong></td><td data-label="Net return">11.60%</td><td data-label="Net volatility">8.41%</td><td data-label="Net Sharpe">1.35</td><td data-label="Beta">0.08</td><td data-label="Max drawdown">19.77%</td></tr>
    <tr><th scope="row"><strong>State-aware optimizer</strong></th><td data-label="Gross return">13.91%</td><td data-label="Net return"><strong>12.32%</strong></td><td data-label="Net volatility">8.40%</td><td data-label="Net Sharpe"><strong>1.43</strong></td><td data-label="Beta"><strong>0.08</strong></td><td data-label="Max drawdown"><strong>18.06%</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1A:</strong> Development-period mean across the three rebalance schedules, from each schedule's September 1998 start through 31 December 2021. Net-return/Sharpe spreads are 1.72 percentage points/0.18 for the volatility-scaled portfolio, 0.41/0.09 for the standard optimizer, and 0.54/0.05 for the state-aware optimizer.</p>

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Portfolio</th><th>Gross return</th><th>Net return</th><th>Net volatility</th><th>Net Sharpe</th><th>Beta</th><th>Max drawdown</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Volatility-scaled portfolio</th><td data-label="Gross return">8.92%</td><td data-label="Net return">7.38%</td><td data-label="Net volatility">9.73%</td><td data-label="Net Sharpe">0.78</td><td data-label="Beta">0.08</td><td data-label="Max drawdown"><strong>8.65%</strong></td></tr>
    <tr><th scope="row">Standard optimizer</th><td data-label="Gross return">8.63%</td><td data-label="Net return">6.47%</td><td data-label="Net volatility">9.39%</td><td data-label="Net Sharpe">0.71</td><td data-label="Beta">0.02</td><td data-label="Max drawdown">9.41%</td></tr>
    <tr><th scope="row"><strong>State-aware optimizer</strong></th><td data-label="Gross return"><strong>9.33%</strong></td><td data-label="Net return"><strong>7.99%</strong></td><td data-label="Net volatility"><strong>9.32%</strong></td><td data-label="Net Sharpe"><strong>0.87</strong></td><td data-label="Beta"><strong>0.01</strong></td><td data-label="Max drawdown">9.05%</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1B:</strong> Later pseudo-holdout mean across the three rebalance schedules, 3 January 2022–27 May 2026. Net-return/Sharpe spreads are 1.48 percentage points/0.14 for the volatility-scaled portfolio, 1.14/0.10 for the standard optimizer, and 4.49/0.43 for the state-aware optimizer.</p>

## Why turnover falls

Across the full history, the state-aware optimizer is a clear improvement over
the standard optimizer. Their gross returns are almost identical: 13.17% for
the state-aware optimizer and 13.13% for the standard optimizer. Annualized
turnover falls from 42.1 to 27.6. Net return therefore rises from 10.77% to
11.62%, and net Sharpe rises from 1.24 to 1.33.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Portfolio</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Annualized turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Volatility-scaled portfolio</th><td data-label="Gross return">10.31%</td><td data-label="Net return">8.67%</td><td data-label="Net Sharpe">1.05</td><td data-label="Annualized turnover">29.9</td></tr>
    <tr><th scope="row">Standard optimizer</th><td data-label="Gross return">13.13%</td><td data-label="Net return">10.77%</td><td data-label="Net Sharpe">1.24</td><td data-label="Annualized turnover">42.1</td></tr>
    <tr><th scope="row"><strong>State-aware optimizer</strong></th><td data-label="Gross return"><strong>13.17%</strong></td><td data-label="Net return"><strong>11.62%</strong></td><td data-label="Net Sharpe"><strong>1.33</strong></td><td data-label="Annualized turnover"><strong>27.6</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Full-history mean across the three rebalance schedules. Annualized turnover is the sum of absolute long and short trades; net returns charge 5 basis points per dollar traded.</p>

The state-aware optimizer achieves essentially the same underlying performance
with substantially less trading. Its gross-to-net return gap is 1.55 percentage
points, compared with 2.36 points for the standard optimizer. Lower trading
costs explain most of the full-history net advantage.

State awareness also changes which stocks may remain in the portfolio. Over the
last five years, the state-aware optimizer earns 1.53 percentage points more
gross return than the standard optimizer. The result is therefore not only a
cost effect: carryover can change the portfolio as well as reduce trading.

The trading penalty and carryover rule work better together than separately.
Carryover alone reduces turnover modestly. The penalty alone reduces it further.
Combining them produces the lowest turnover and the best net result.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Configuration</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Annualized turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">No penalty, no carryover</th><td data-label="Gross return">13.13%</td><td data-label="Net return">10.77%</td><td data-label="Net Sharpe">1.24</td><td data-label="Annualized turnover">42.1</td></tr>
    <tr><th scope="row">Carryover only</th><td data-label="Gross return">13.16%</td><td data-label="Net return">10.96%</td><td data-label="Net Sharpe">1.25</td><td data-label="Annualized turnover">39.0</td></tr>
    <tr><th scope="row">Trading penalty only</th><td data-label="Gross return">13.02%</td><td data-label="Net return">11.07%</td><td data-label="Net Sharpe">1.27</td><td data-label="Annualized turnover">34.8</td></tr>
    <tr><th scope="row"><strong>Penalty and carryover</strong></th><td data-label="Gross return"><strong>13.17%</strong></td><td data-label="Net return"><strong>11.62%</strong></td><td data-label="Net Sharpe"><strong>1.33</strong></td><td data-label="Annualized turnover"><strong>27.6</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 3:</strong> Full-history comparison of the two state-aware components. “Carryover” allows existing holdings to remain eligible through rank 175; without it, every holding must remain in the fresh top or bottom 75.</p>

The average interaction adds 0.36 percentage points of net return beyond the
sum of the two changes tested separately. The economic explanation is direct:
a trading penalty is more useful when the optimizer has an acceptable existing
position that it is allowed to keep.

Forced exits prevent turnover from falling even further. Holdings that move
beyond rank 175 must leave the portfolio. These exits account for 36% of the
state-aware optimizer's modeled turnover, so they are included in the reported
27.6 figure.

## Remaining risks

The state-aware optimizer is the best historical implementation, but four
problems still matter before live use.

First, the later-period result is sensitive to rebalance timing. The three
schedules produce a 4.49-percentage-point spread in net return and a 0.43 spread
in Sharpe after 2022. A result that depends this much on the day of the rebalance
needs more evidence.

Second, the period after 2022 is a pseudo-holdout, not a completely untouched
test. It was separate from the original development period, but later research
decisions were made with some knowledge of these results.

Third, predicted risk does not stay close to the risk realized over the next
holding period. Figure 2 shows every rebalance forecast and subsequent outcome.
The standard and state-aware forecasts remain near 7% annualized volatility,
while realized volatility moves much more and reaches about 35% during the 2020
shock. Across all rebalances, their root-mean-square realized volatility is
8.6%, compared with a 7.0% forecast.

<div class="research-figure risk-forecast-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/risk-forecast-through-time" mobile_suffix="-mobile" alt="Predicted and subsequently realized annualized volatility at every rebalance for the volatility-scaled portfolio, standard optimizer, and state-aware optimizer" version="2" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Predicted and subsequently realized annualized volatility at every rebalance. Each panel contains all three staggered schedules; realized volatility covers the following execution-to-execution holding period. The shared vertical scale focuses on 0–20%. Triangles mark the 10, 12, and 11 observations above 20% for volatility scaling, the standard optimizer, and the state-aware optimizer; their maxima are 48.9%, 34.7%, and 34.3%.</p>

Fourth, target beta control does not guarantee realized beta control. Target
beta is constrained to ±0.05 at each optimization, yet realized beta reached
about +0.22 during the final five months. Execution delay and subsequent price
movement separate the target portfolio from the holdings that generate returns
(Figure 3).

<div class="research-figure realised-beta-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/realised-beta" mobile_suffix="-mobile" alt="Rolling 252-day realized beta for the volatility-scaled portfolio, standard optimizer, and state-aware optimizer" version="1" %}
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Rolling 252-day realized beta, sampled monthly and averaged across the three staggered schedules. The gray band marks the ±0.05 optimization target for the standard and state-aware portfolios.</p>

The next version should measure and control risk and beta drift directly.

These limitations affect readiness for live implementation. They do not
overturn the historical comparison between the two optimizers.

## Conclusion

The state-aware optimizer is the version I would carry forward. It preserves
gross performance while trading substantially less, leading to higher net
return and Sharpe. The next work is to improve realized beta control and test
whether the advantage persists on new data.
