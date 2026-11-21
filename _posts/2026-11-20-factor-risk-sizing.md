---
layout: post
toc: false
title: "Factor Risk Models, Part 1: An Introduction"
description: "How factor exposures become portfolio risk, and what changes in hedges and position sizing when the Ridge forecasts stay fixed."
date: 2026-11-20
last_modified_at: 2026-11-21
categories: ["Portfolio construction"]
article_label: Factor risk · Part 1 of 2
series_id: factor-risk
series_order: 1
permalink: /quants/factor-risk-sizing.html
---

Suppose I’m long a chipmaker and want to hedge it. I could short another chipmaker or a stock from a different sector. Both shorts could offset the same amount of market beta. The first can also offset a semiconductor selloff. If the long has strong momentum and the short has weak momentum, the spread can still lose when momentum reverses. The hedge depends on which move I want protection from.

A factor risk model estimates how much each stock responds to shared moves in the market, sectors and styles. I multiply those exposures by the signed position weights and add them up. That gives the portfolio’s exposure to each factor. To turn exposures into a volatility forecast, I need to know how large each factor’s moves tend to be and how the factors move together. I also need a forecast of the risk left over after accounting for those shared moves, such as the part of an earnings surprise specific to one company.

The same exposures tell me how a proposed trade changes the portfolio’s risk, what a sector or style shock would do to the book, and how much of an observed return the factor moves explain. There is also a statistical reason to use them. A universe of 1,000 stocks has 499,500 pairwise correlations. The factor model estimates much of that co-movement through a smaller covariance matrix. Whether that helps depends on what the factors capture and what co-movement remains in the residuals.

I use the Ridge forecasts as a worked example and keep them fixed. First I test which covariance estimates find quieter hedges on the same stocks. Then I compare risk forecasts on identical holdings. Finally I let each estimate change the positions under the same risk budget and check what happens to exposure, realized volatility and returns after fees.

## From stock exposures to portfolio risk

At each close I write the vector of stock returns as shared factor moves plus a residual for each stock.

$$
r_t = B_{t-1} f_t + \epsilon_t.
$$

Each row of $$B_{t-1}$$ gives one stock’s exposures as of the previous close. The market column is one for every stock. The other columns encode sectors and styles. The model adds the factor contributions linearly. An interaction, such as momentum having a different effect among small stocks, would need its own term.

I fit the factor returns $$f_t$$ across stocks by weighted least squares, using the square root of prior market cap as the weight. I center the sector returns under those weights to separate them from the common market term. What’s left after the fit is the vector of residual returns $$\epsilon_t$$.

To forecast risk I hold the latest exposures $$B$$ fixed. Let $$F$$ be the covariance of factor returns and $$\Omega$$ the covariance of residual returns. The model assumes the factor and residual returns are uncorrelated, so their covariance contributions add.

$$
\Sigma = BFB^\top + \Omega.
$$

The additivity of the return model still allows factor returns to move together, so I estimate a full covariance matrix $$F$$. The baseline takes $$\Omega$$ to be diagonal, treating different stocks’ residuals as uncorrelated. This leaves one specific variance per stock to estimate. A shared move the chosen factors miss can still raise each stock’s specific variance. The diagonal estimate omits the covariance between those stocks.

Which moves land in the residuals depends on the factors. A model with only a market and sectors can leave a common momentum effect behind. Adding a factor or estimating residual correlations can capture more of that co-movement, with more relationships to estimate. Part 2 checks how much of the residual co-movement survives into the following year.

For signed weights $$w$$, let $$b=B^\top w$$ be the portfolio’s factor exposures. A factor move $$f$$ contributes $$b^\top f$$ to portfolio return. Before seeing that move, the model forecasts daily variance as

$$
w^\top\Sigma w = b^\top F b + w^\top\Omega w.
$$

The first term depends on the net exposures and on how the factors move together. With diagonal $$\Omega$$, the second is the sum of each stock’s specific variance times its squared weight. Two positions can cancel a shared exposure while both still add specific risk.

### The factors in this study

The market intercept and sector indicators capture broad moves. The seven styles describe how stocks within and across sectors can still move together.

- **Momentum and short-term return** describe price behavior over different horizons. Momentum blends 12–1 return with a moving-average trend measure. Short-term return measures the last month.
- **Beta and residual volatility** separate sensitivity to the Russell 1000 from the volatility left after fitting that index alone. Residual volatility is a stock characteristic here. The specific variance in $$\Omega$$ comes from the full factor fit.
- **Size, liquidity and short interest** capture differences in market capitalization, trading volume relative to capitalization, and the share of stock sold short. They describe different ways stocks can react together when investors trade or unwind positions.

These are risk exposures. A characteristic can explain co-movement even when the return forecast omits it. Value and quality could be useful for that reason. I lacked enough historical data to include them over this sample.

### A three-stock example

Take three stocks with a common market exposure of one. A and B have opposite momentum exposures. For the example, give the factors zero correlation and daily variances of 4 and 1 in squared percentage points.

{% assign example = site.data.factor_risk_example %}
<div class="matrix-calculation" role="group" aria-label="Stock exposures multiplied by factor covariance">
  <div class="matrix-product">
    {% include worked-matrix.html matrix=example.exposures symbol="B" label="Stock exposures" %}
    <span class="matrix-operator" aria-hidden="true">×</span>
    {% include worked-matrix.html matrix=example.factor_covariance symbol="F" label="Factor covariance" %}
  </div>
</div>

This diagonal $$F$$ scales the market column by 4 and the momentum column by 1. A’s row becomes $$(4,1)$$. Its dot product with B’s column in $$B^\top$$ gives their factor covariance. The highlighted cells show $$4(1)+1(-1)=3$$.

<div class="matrix-calculation" role="group" aria-label="Scaled exposures times transposed exposures equals stock covariance from factors">
  <div class="matrix-product">
    {% include worked-matrix.html matrix=example.scaled_exposures symbol="BF" label="Scaled exposures" mark_row="A" %}
    <span class="matrix-operator" aria-hidden="true">×</span>
    {% include worked-matrix.html matrix=example.transposed_exposures symbol="Bᵀ" label="Transposed exposures" mark_column="B" %}
  </div>
  <div>
    <span class="matrix-operator" aria-hidden="true">=</span>
    {% include worked-matrix.html matrix=example.factor_stock_covariance symbol="BFBᵀ" label="Stock covariance from factors" mark_row="A" mark_column="B" %}
  </div>
</div>

Now put 50% of capital long A and 50% short B, so $$w=(0.5,-0.5,0)^\top$$. The common market exposure cancels, $$0.5(1)-0.5(1)=0$$. The momentum exposures add, $$0.5(1)-0.5(-1)=1$$. The portfolio’s index-beta limit uses betas estimated separately for each stock.

Let A, B and C have specific volatilities of 2%, 2% and 1%. With zero residual correlations, $$\Omega$$ adds their variances of 4, 4 and 1 to the diagonal of $$BFB^\top$$.

<div class="matrix-calculation" role="group" aria-label="Total stock covariance with a diagonal residual model">
  {% include worked-matrix.html matrix=example.total_stock_covariance symbol="Σ" label="Total stock covariance" mark_row="A" mark_column="B" %}
</div>

The spread’s variance comes from the two individual variances and the cross term. With a short in B, its weight enters with a minus sign.

$$
w^\top\Sigma w=\frac{9+9-2(3)}{4}=3.
$$

Momentum accounts for one unit of variance and the two specific risks account for the other two. To choose the weights, I need return forecasts and limits on what I can hold and trade.
{: #the-average-residual-hides-groups}

## What goes into a position

Ridge scores stocks within each sector on expected return per unit of risk. Each joint optimizer multiplies the same score by the stock’s trailing 21-session volatility to put it in return units.

At rebalance, new longs come from the top 75 scores in the dated Russell 1000 universe and new shorts from the bottom 75. Existing positions can stay eligible beyond the entry cutoff, so a small rank change needn’t trigger a round trip.

To see what modeling co-movement adds, I compare a stock-by-stock sizing rule with three joint rules that use different covariance estimates.

- **Volatility scaling** is the simple benchmark. It starts with equal weights on each side and multiplies each by 20% divided by its trailing 60-session annualized volatility, with a 5% volatility floor. A 40%-volatility stock starts at half its equal weight. Each sleeve can use up to one dollar per dollar of capital. This benchmark sizes stocks one at a time.
- **Stock shrinkage** shrinks the 756-session stock correlation matrix halfway toward the identity. This reduces the influence of noisy pairwise estimates. Stock volatilities use 21 sessions, with the fixed risk adjustment from the reference backtest.
- **Sector and style factors** estimate stock covariance from a market intercept, broad sectors and seven styles, including momentum, size and liquidity. The model adds each stock’s specific variance and starts with zero pairwise residual correlations.
- **Factor target** keeps the stock-shrinkage volatilities and averages the historical correlation matrix with the total correlation implied by the factor model, including shrunk residual correlations. For a pair with 0.40 historical correlation and 0.20 factor-implied correlation, stock shrinkage uses 0.20 and the factor target uses 0.30.

Stock shrinkage and the factor target use the same standalone stock risk. They differ in how much risk they assign to holding those stocks together. Shrinking a positive correlation toward zero lowers the estimated risk of two longs and gives less hedging credit to a long paired with a short. The effect on the whole book depends on its positions.

### The objective and constraints

At each rebalance the three joint optimizers maximize expected return after a turnover penalty. Each uses the same limits and prices portfolio risk with its own covariance estimate.

$$
\begin{aligned}
\max_w\quad & \mu^\top w - c\lVert w-w_{\rm prev}\rVert_1 \\
\text{subject to}\quad & A\,w^\top\Sigma w \le \sigma_{\rm target}^2 \\
& \lVert w\rVert_1 \le G_{\max},\quad |\mathbf{1}^\top w| \le N_{\max} \\
& |\beta^\top w| \le \beta_{\max} \\
& |w_i| \le w_{\max} \quad \text{for each stock }i \\
& |a_g^\top w| \le S_{\max} \quad \text{for each sector }g \\
& \lVert w_{g\cap\ell}\rVert_1 \le q_{\max}\lVert w_\ell\rVert_1
  \quad \text{for each sector }g\text{ and sleeve }\ell.
\end{aligned}
$$

Here $$w$$ gives the signed target weights and $$w_{\rm prev}$$ the weights held at rebalance. Eligible longs have nonnegative weights, eligible shorts have nonpositive weights, and other weights are zero. The vector $$\mu$$ contains the Ridge forecasts in return units. The rate $$c$$ is 2.5 basis points per unit of two-way turnover, the sum of absolute weight changes. Trading fees apply separately to fills.

| Symbol | Meaning | Setting |
| --- | --- | --- |
| $$A$$ | Sessions per year, used to annualize the daily variance from $$\Sigma$$ | 252 |
| $$\sigma_{\rm target}$$ | Annualized forecast-volatility target | 7% |
| $$G_{\max}$$ | Gross exposure, longs plus absolute shorts | 200% |
| $$N_{\max}$$ | Absolute net exposure, the magnitude of longs minus shorts | 25% |
| $$\beta_{\max}$$ | Absolute exposure to the Russell 1000, with stock betas in $$\beta$$ | 0.05 |
| $$w_{\max}$$ | Maximum absolute target weight of a single stock | 4% |
| $$S_{\max}$$ | Absolute net sector exposure, with $$a_g$$ selecting sector $$g$$ | 20% |
| $$q_{\max}$$ | Maximum share of either sleeve in a single sector | 30% |

These constraints address different risks. A 3% long with beta 1.4 and a 3% short with beta 0.8 add zero net exposure and 0.018 of market beta. The volatility constraint also captures how sector and style exposures combine. If two estimates price the same positions differently, the same volatility target can support different amounts of gross exposure.

For the replay, I stagger the starting week across three schedules to see how sensitive the results are to when the book trades. Each rebalances every three weeks against $5 million. All four rules trade from filled holdings, with next-close execution and a 10% cap on participation in average daily dollar volume for ordinary fills. From 2011 I charge 5 bp on long trades and 7.5 bp on short trades, with higher rates earlier.

The portfolio comparisons use 5,773 common sessions from 26 January 1999 through 31 December 2021 and 1,103 from 3 January 2022 through 27 May 2026. The later period includes history I had already seen in related research.

## Comparing the hedges on the same stocks

I give stock shrinkage, the sector-and-style model, and the same factor model with shrunk residual correlations the same sampled stocks. Each finds the minimum-variance spread at the same Ridge score. For scores $$s$$, each model minimizes $$w^\top\Sigma w$$ while holding $$w^\top s$$ at the equal-weight spread’s score. The gross long and short weights are each 50%, and each name stays between one-quarter and three times its side’s equal weight. Multiplying the whole covariance matrix by a constant leaves those minimum-variance weights unchanged.

I drew 32 groups per weekly decision at 75, 100 and 150 stocks **in total** and measured gross returns for the session after the next close. The stock draws vary the names on the same dates. Later 150-stock spreads fell from **3.69% to 3.53%** annualized volatility when I added shrunk residual correlations to the factor model.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/stock-draws" mobile="/assets/factor-risk-sizing/stock-draws_mobile" version="1" alt="32 stock selections at each decision. Point estimates of spread volatility favor shrunk residuals at all three stock counts. The left panel compares with stock shrinkage. The right compares with diagonal residuals." %}
</div>
<p class="figure-caption">Each point subtracts the reference spread’s realized volatility from that of the spread with shrunk residual correlations. Left of zero means a quieter spread. The left panel uses stock shrinkage as the reference. The right uses the same factor model with zero residual correlations. Each row fixes the names and score exposure, and the paired 95% intervals account for six comparisons per period.</p>

I also compared one session with the three-week holding period used in the portfolio replay. For the same eight stock paths and 227 later starting dates, the test assumes full fills where the next close has a quote and leaves other allocations in cash. The returns are gross. At 150 stocks, adding shrunk residuals reduced annualized 15-session volatility from **3.35% to 3.22%**, a **0.13-point** reduction with a simultaneous 95% interval of **0.04 to 0.21 points**. Against stock shrinkage the estimate also favored shrunk residuals, but all three stock counts had intervals that crossed zero at 15 sessions.

<table class="research-table comparison-table compact-table">
  <caption>Annualized volatility saved by estimating residual correlations, 2022–May 2026. Values are percentage points relative to the same factor model with zero residual correlations. A larger positive number means a quieter spread.</caption>
  <thead><tr><th>Total stocks</th><th>1 session</th><th>15 sessions</th></tr></thead>
  <tbody>
    <tr><th>75</th><td>0.12</td><td>0.08</td></tr>
    <tr><th>100</th><td>0.15</td><td>0.07</td></tr>
    <tr><th>150</th><td>0.16</td><td>0.13</td></tr>
  </tbody>
</table>

At three weeks, the smaller spreads gave inconclusive results. Sampling more stocks helps check how the result depends on which names I draw. All the draws share the same market dates.

To see how much the result depends on the kind of portfolio, I also ran long-only minimum variance on sampled stocks without using Ridge scores. In the later period, the sector-and-style model lowered next-session annualized volatility from **13.5% to 12.8%** at 150 names when both optimizers had to hold every stock. Once either model could drop names, the difference was uncertain. The benefit depends on which positions the optimizer is required to hold.

## The same holdings reveal a gap in risk forecasts

A model can find a good hedge and still misjudge how much risk the spread carries. That distinction matters under a hard risk limit. I give both models the same holdings and compare their forecasts with the same realized returns.

I score variance forecasts with **QLIKE**, the variance-forecast Q statistic. Let $$x=u/v$$ be the mean squared daily return divided by forecast daily variance. The normalized loss $$x-\log x-1$$ is zero at a match. A given proportional miss costs the same on quiet and volatile books. Forecasting half the realized variance costs more than forecasting twice the realized variance. On identical holdings, $$\log v+u/v$$ gives the same paired comparison.

For a check without Ridge scores, I assigned the longs and shorts at random and gave names equal weights on each side. On these identical holdings, the factor target’s raw forecasts had lower QLIKE than stock shrinkage at 75, 100 and 150 names in the later period. All three paired intervals favored it. At 150 names, stock shrinkage forecast **3.6%** volatility and the factor target **3.4%**, against **2.7%** realized. Both estimates ran high.

On the filled stock-shrinkage book, the same models forecast **7%** and **about 10%** across 227 later cycles, against **9.6%** annualized gross volatility. Absolute risk matters here because the lower forecast leaves room to take larger positions. I checked how much of the QLIKE gap came from forecast scale by rescaling each forecast with the mean ratio of realized to forecast variance over its last 52 completed cycles. Both forecasts then came out near **9.7%**. Stock shrinkage had a lower QLIKE on its own holdings, and the paired intervals on the other two filled books included zero.

Calibration can help when a model consistently under- or overestimates risk on the holdings it will size. A uniform adjustment leaves the correlations intact. Here the direction of the error depended on the holdings. Stock shrinkage forecast too much risk on the random spreads and too little on the optimized book.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/fixed-book" mobile="/assets/factor-risk-sizing/fixed-book_mobile" version="1" alt="On the same stock-shrinkage holdings, the two models forecast 7% and about 10% in the later period. Calibration brings both forecasts close to the 9.6% realized gross volatility." %}
</div>
<p class="figure-caption">The dashed line is the realized volatility of the same filled stock-shrinkage book. Circles are the original forecasts and diamonds are forecasts recalibrated with the last 52 completed holding periods. The distance from the line shows how far each forecast was from the volatility the book delivered.</p>

## The portfolio comparison after fees
{: #how-the-risk-estimate-changes-the-portfolio}

I now let each sizing rule choose its own positions and trade from its own fills. The cost of those trades enters the comparison.

<table class="research-table comparison-table compact-table">
  <caption>Long/short portfolio outcomes, averaged across three schedules. Return and Sharpe show net on top and gross before trading fees below. Returns are annualized compound growth. Sharpe uses daily returns, a zero cash rate and 252 sessions per year. Volatility and drawdown use net returns. Turnover counts purchases and sales in multiples of capital per year.</caption>
  <thead><tr><th>Sizing rule</th><th>Return</th><th>Vol.</th><th>Sharpe</th><th>Drawdown</th><th>Turnover</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="6">January 1999 – December 2021</th></tr>
    <tr><th scope="row">Volatility scaling</th><td>7.12%<span class="secondary-metric">9.34%</span></td><td>8.07%</td><td>0.89<span class="secondary-metric">1.15</span></td><td>20.07%</td><td>28.49×</td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>10.77%<span class="secondary-metric">12.91%</span></td><td>8.74%</td><td>1.21<span class="secondary-metric">1.43</span></td><td>18.52%</td><td>25.65×</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>7.95%<span class="secondary-metric">10.11%</span></td><td>8.13%</td><td>0.98<span class="secondary-metric">1.23</span></td><td>19.10%</td><td>26.49×</td></tr>
    <tr><th scope="row">Factor target</th><td>9.50%<span class="secondary-metric">11.56%</span></td><td>7.47%</td><td>1.25<span class="secondary-metric">1.50</span></td><td>15.79%</td><td>25.17×</td></tr>
    <tr class="period-heading"><th colspan="6">January 2022 – May 2026</th></tr>
    <tr><th scope="row">Volatility scaling</th><td>6.96%<span class="secondary-metric">8.47%</span></td><td>10.16%</td><td>0.71<span class="secondary-metric">0.85</span></td><td>9.41%</td><td>24.36×</td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>7.42%<span class="secondary-metric">8.66%</span></td><td>9.65%</td><td>0.79<span class="secondary-metric">0.91</span></td><td>9.84%</td><td>18.76×</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>2.72%<span class="secondary-metric">3.88%</span></td><td>8.29%</td><td>0.37<span class="secondary-metric">0.50</span></td><td>10.54%</td><td>18.28×</td></tr>
    <tr><th scope="row">Factor target</th><td>4.59%<span class="secondary-metric">5.64%</span></td><td>7.27%</td><td>0.65<span class="secondary-metric">0.79</span></td><td>7.64%</td><td>16.66×</td></tr>
  </tbody>
</table>

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/performance" mobile="/assets/factor-risk-sizing/performance_mobile" version="3" alt="Net growth of the three long/short Ridge portfolios above their drawdowns on the same timeline. Stock shrinkage finished ahead of the factor target and sector and style factors." %}
</div>
<p class="figure-caption">The top panel shows how $1 grew after fees on a log scale. Each path compounds the mean daily return across schedules. Below, drawdown is the percentage loss from each path’s previous peak. The table calculates drawdown separately for each schedule before averaging.</p>

The factor target came closest to its 7% budget in both periods. Stock shrinkage earned more after fees in the later period and carried more risk. To understand that trade-off, it helps to see how much exposure each book held.

## Why the same risk budget produced different volatility

The same 7% cap can produce a smaller book if one model forecasts more risk for a given set of positions. In the later period the factor target held **$1.24** of gross exposure per dollar of capital, against **$1.56** for stock shrinkage. It also had smaller drawdowns. The next comparison asks how much of the volatility gap follows the forecast level.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/realized-risk" mobile="/assets/factor-risk-sizing/realized-risk_mobile" version="1" alt="Trailing annualized volatility of the original sizing rules before the rolling calibration." %}
</div>
<p class="figure-caption">Each monthly point shows trailing 252-session net volatility averaged across schedules. The 7% line is the limit on each optimizer’s own forecast at rebalance. Stock shrinkage ran above the factor target throughout the chart. It traded places with the sector-and-style book before 2022, then stayed above it at every later point shown.</p>

All three books became more volatile in 2020–21. Stock shrinkage peaked near **15%**, several points above both factor books. The factor target spent more of the chart close to the **7%** budget.

At each decision close, I priced the filled stock-shrinkage holdings with both models. I rescaled one covariance matrix until the models forecast the same risk for those holdings, using each model as the scale reference in turn. Each optimizer then chose its own positions and traded from its own fills.

<table class="research-table comparison-table compact-table">
  <caption>Each cell shows annualized net compounded return / realized volatility. Compare rows within a block to see the effect of changing stock relationships at a common risk scale. Find the same model in both blocks to see the effect of changing its forecast scale.</caption>
  <thead><tr><th scope="col">Stock relationships</th><th scope="col">1999–2021</th><th scope="col">2022–26</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="3">Stock-shrinkage risk level</th></tr>
    <tr><th scope="row">Stock shrinkage</th><td>10.77% / 8.74%</td><td>7.42% / 9.65%</td></tr>
    <tr><th scope="row">Factor target</th><td>10.48% / 8.84%</td><td>6.00% / 9.70%</td></tr>
    <tr class="period-heading"><th colspan="3">Factor-target risk level</th></tr>
    <tr><th scope="row">Stock shrinkage</th><td>9.67% / 7.45%</td><td>5.96% / 7.30%</td></tr>
    <tr><th scope="row">Factor target</th><td>9.50% / 7.47%</td><td>4.59% / 7.27%</td></tr>
  </tbody>
</table>

In the later period, moving to the factor target’s forecast scale reduced realized volatility by **about 2.4 percentage points** for both covariance models. Swapping the stock relationships at the same scale barely moved volatility, with paired intervals spanning roughly 0.2 points either way. The factor target earned less at both scales in this sample, with considerable uncertainty around the return difference.

## Trading with a calibrated risk budget

The scale swap shows how much exposure moved with the risk estimate. I next let each model adjust its risk forecast as new outcomes became available. At each rebalance I rescale the covariance using the last 52 completed cycles of the corresponding reference book, then reoptimize from the calibrated replay’s own fills. A fixed adjustment estimated through 2021 also brought the stock-shrinkage book close to the budget later, at **7.5%** realized volatility. The rolling adjustment brought it to **7.1%**. Both replays point to the importance of the risk level, with less evidence for the value of updating the adjustment.

<table class="research-table comparison-table compact-table">
  <caption>Outcomes with rolling calibration. Return and Sharpe show net on top and gross before trading fees below. Volatility uses net returns. Gross exposure is the average market value of longs and shorts, both counted as positive, per dollar of capital.</caption>
  <thead><tr><th>Sizing rule</th><th>Return</th><th>Vol.</th><th>Sharpe</th><th>Gross exposure</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="5">January 1999 – December 2021</th></tr>
    <tr><th scope="row">Stock shrinkage</th><td>9.80%<span class="secondary-metric">11.73%</span></td><td>7.41%</td><td>1.30<span class="secondary-metric">1.54</span></td><td>1.65</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>7.56%<span class="secondary-metric">9.55%</span></td><td>7.25%</td><td>1.04<span class="secondary-metric">1.29</span></td><td>1.44</td></tr>
    <tr><th scope="row">Factor target</th><td>9.38%<span class="secondary-metric">11.38%</span></td><td>7.12%</td><td>1.29<span class="secondary-metric">1.55</span></td><td>1.62</td></tr>
    <tr class="period-heading"><th colspan="5">January 2022 – May 2026</th></tr>
    <tr><th scope="row">Stock shrinkage</th><td>6.10%<span class="secondary-metric">7.00%</span></td><td>7.13%</td><td>0.87<span class="secondary-metric">0.99</span></td><td>1.19</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>2.44%<span class="secondary-metric">3.41%</span></td><td>6.92%</td><td>0.38<span class="secondary-metric">0.52</span></td><td>0.96</td></tr>
    <tr><th scope="row">Factor target</th><td>4.48%<span class="secondary-metric">5.49%</span></td><td>7.00%</td><td>0.66<span class="secondary-metric">0.80</span></td><td>1.19</td></tr>
  </tbody>
</table>

All three portfolios realized about **7% volatility** in the later period. Stock shrinkage and the factor target also held almost identical gross exposure. Stock shrinkage earned **6.1%** a year after fees, the factor target **4.5%**, and sector and style factors **2.4%**. Most of the gap between stock shrinkage and the factor target came from the short sleeve before fees. The factor target’s net Sharpe was about **0.2 lower**, with a paired interval that included zero.

Similar overall volatility can come with different market exposure. The estimated beta limit applies at rebalance. Realized beta measures how the filled book moved with the Russell 1000. When measured over the same window, beta equals correlation with the index times the ratio of portfolio to index volatility, $$\beta_{p,m}=\rho_{p,m}\sigma_p/\sigma_m$$. At the same market correlation, a more volatile book has a larger beta in magnitude.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/market-exposure" mobile="/assets/factor-risk-sizing/market-exposure_mobile" version="2" alt="Rolling 63-session market beta and 252-session correlation with the Russell 1000 across the full backtest for the three calibrated portfolios." %}
</div>
<p class="figure-caption">Monthly readings across the full backtest, starting when the first 252-session window is complete. Correlation uses the prior 252 sessions and beta uses 63. Both use daily net returns against the Russell 1000, calculated separately for each schedule and then averaged.</p>

Stock shrinkage’s beta has some of the largest swings, especially in the mid-2010s. Around 2020 its market correlation rises alongside the factor target’s. The sector-and-style book spends more time near zero and turns sharply negative around 2009–10. Scaling the same positions down lowers their volatility and beta. Their market correlation stays the same. Changing the covariance can also change the positions themselves, even under the same estimated beta cap.

To understand what market exposure misses, I looked at the deepest drawdown of an equal mix of the calibrated stock-shrinkage and factor-target books. In that early-2023 window, each book lost about **8%** while the Russell 1000 rose **11%**. The losses came from the short side as its stocks rose.

## A wider candidate list changes both holdings and turnover

I used 75 entry candidates per side in the experiments above. I widened the list to **100 and 150 per side** to see how much the results depend on that choice. A wider list gives the optimizer more potential hedges, including stocks with weaker forecasts. I kept the reference retention rule, which lets the joint optimizers keep holdings in the top or bottom **175** ranks. With that rule fixed, going from 75 to 150 leaves only 25 ranks of room at the entry boundary, down from 100.

At 150 per side stock shrinkage held about **175 stocks** and the factor target **123** in the later period. Net Sharpe fell for all three joint optimizers as the entry list widened. Stock shrinkage and the factor target also had lower gross Sharpe at 150 than at 75, so trading fees explain only part of the decline.

<table class="research-table comparison-table compact-table">
  <caption>Each cell shows annualized net return on top and net Sharpe below, averaged across three schedules. Columns give the number of entry candidates per side.</caption>
  <thead><tr><th>Sizing rule</th><th>75 per side</th><th>100 per side</th><th>150 per side</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="4">1999–2021</th></tr>
    <tr><th scope="row">Volatility scaling</th><td>7.12%<span class="secondary-metric">0.89</span></td><td>6.43%<span class="secondary-metric">0.85</span></td><td>5.75%<span class="secondary-metric">0.84</span></td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>10.77%<span class="secondary-metric">1.21</span></td><td>10.41%<span class="secondary-metric">1.17</span></td><td>10.44%<span class="secondary-metric">1.17</span></td></tr>
    <tr><th scope="row">Sector and style factors</th><td>7.95%<span class="secondary-metric">0.98</span></td><td>7.71%<span class="secondary-metric">0.94</span></td><td>8.12%<span class="secondary-metric">0.97</span></td></tr>
    <tr><th scope="row">Factor target</th><td>9.50%<span class="secondary-metric">1.25</span></td><td>9.06%<span class="secondary-metric">1.19</span></td><td>9.32%<span class="secondary-metric">1.22</span></td></tr>
    <tr class="period-heading"><th colspan="4">2022–May 2026</th></tr>
    <tr><th scope="row">Volatility scaling</th><td>6.96%<span class="secondary-metric">0.71</span></td><td>6.76%<span class="secondary-metric">0.73</span></td><td>5.51%<span class="secondary-metric">0.65</span></td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>7.42%<span class="secondary-metric">0.79</span></td><td>7.20%<span class="secondary-metric">0.76</span></td><td>6.69%<span class="secondary-metric">0.71</span></td></tr>
    <tr><th scope="row">Sector and style factors</th><td>2.72%<span class="secondary-metric">0.37</span></td><td>2.51%<span class="secondary-metric">0.34</span></td><td>2.17%<span class="secondary-metric">0.29</span></td></tr>
    <tr><th scope="row">Factor target</th><td>4.59%<span class="secondary-metric">0.65</span></td><td>4.37%<span class="secondary-metric">0.62</span></td><td>3.75%<span class="secondary-metric">0.53</span></td></tr>
  </tbody>
</table>

To isolate the retention rule, I kept entry at 150 and let positions remain eligible through rank 250. Later annual turnover fell from roughly **25× capital** to **21×** for stock shrinkage and **22×** for the factor target. Most of the saving came from less trading on exits beyond the cutoff and on new entries. Net Sharpe rose from **0.71 to 0.79** and from **0.53 to 0.59**, respectively. Both paired Sharpe intervals included zero. The clearest effect of a wider retention band was less trading.

The later Sharpe comparison at 150 per side is sensitive to which years are included. Leaving out 2024 put stock shrinkage and the factor target close to even.

Exposure changed with breadth too. At 150 per side both models met the ±0.05 estimated beta band at the decision close. The later filled factor-target book had a realized index beta of about **0.06**, versus **0.02** for stock shrinkage. A common beta band still allowed different market exposures after execution.

## What changes when the risk model changes

The covariance estimate does two jobs. It tells the optimizer which positions offset one another, and it determines how much exposure fits inside the risk budget. A model can improve the first job for a broadly diversified spread while pushing the optimizer toward quite different positions once names can be dropped. In the Ridge replay, most of the gap in headline volatility came from how the models priced a dollar of exposure. Matching total volatility still left room for different market exposures and different stock weights.

## References

- Factor exposures, risk and attribution. [Paleologo, *Linear Models of Asset Returns*, Columbia Quantitative Investing, Lecture 3](https://www.dropbox.com/scl/fi/1nqzz8zfikjace6g5fa5j/FINC_B8420_3_simple.pdf?rlkey=pj6boer325ci9e3bys5rt5vdz&dl=0)
- The linear factor model applied to equity portfolios. [Zhang, *Modeling Equities Returns: The Linear Case*, Hudson River Trading](https://www.hudsonrivertrading.com/hrtbeat/modeling-equities-returns/)
- Practitioner examples. [MSCI Barra US Equity Model (USE4)](https://www.msci.com/documents/10199/242721/Barra_US_Equity_Model_USE4.pdf) · [Bloomberg Portfolio & Risk Analytics](https://professional.bloomberg.com/products/bloomberg-terminal/portfolio-analytics/)
- Volatility scaling. [Paleologo, *Advanced Portfolio Management*, §6.3](https://www.wiley.com/en-us/advanced-portfolio-management-a-quant%27s-guide-for-fundamental-investors-p-9781119789802)
- Correlation shrinkage. [Pedersen, Babu and Levine, *Enhanced Portfolio Optimization*](https://doi.org/10.1080/0015198X.2020.1854543)
