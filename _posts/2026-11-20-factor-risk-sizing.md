---
layout: post
toc: false
title: "Factor Risk, Part 1: Shrinking Stock Correlations"
description: "I kept the Ridge stock forecasts fixed and changed how the long/short portfolio measures risk. I compared risk forecasts on the same holdings, hedges on the same stocks, and long/short returns at similar realized risk."
date: 2026-11-20
last_modified_at: 2026-11-21
categories: ["Portfolio construction"]
article_label: Factor risk · Part 1 of 2
series_id: factor-risk
series_order: 1
permalink: /quants/factor-risk-sizing.html
---

When I add a short, I want to know which risk it takes out of the book. My baseline uses historical stock correlations shrunk toward zero. That gives the optimizer a way to size positions together. In the Russell 1000 it still starts from nearly half a million pairwise relationships.

A factor risk model estimates those relationships through a smaller set of shared returns, such as the market, sectors and styles. The same exposures tell me what a trade does to the whole book. A short can cancel some market exposure and add to momentum exposure at the same time. The model can still miss shared moves among stocks, and its estimate of total volatility can be off.

I keep the Ridge forecasts fixed. I first compare risk forecasts on the same holdings, then compare hedges on the same stocks, and finally look at the portfolios after trading fees.

## From stock exposures to portfolio risk

Consider three stocks and two factors. Each row of $$B$$ holds a stock’s exposures. All three stocks have a loading of one on the common market term, as they do for the market intercept in the study. A and B have opposite momentum exposures. The two factors in this example are uncorrelated and have daily variances of 4 and 1 in squared percentage points.

{% assign example = site.data.factor_risk_example %}
<div class="matrix-calculation" role="group" aria-label="Stock exposures multiplied by factor covariance">
  <div class="matrix-product">
    {% include worked-matrix.html matrix=example.exposures symbol="B" label="Stock exposures" %}
    <span class="matrix-operator" aria-hidden="true">×</span>
    {% include worked-matrix.html matrix=example.factor_covariance symbol="F" label="Factor covariance" %}
  </div>
</div>

Multiplying by this diagonal $$F$$ scales the market column by 4 and the momentum column by 1. A’s row goes from $$(1,1)$$ to $$(4,1)$$. To get the factor covariance between A and B, take the dot product of A’s row in $$BF$$ and B’s column in $$B^\top$$. The highlighted cells give $$4(1)+1(-1)=3$$.

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

Now put 50% of capital long A and 50% short B. The signed weights are $$w=(0.5,-0.5,0)^\top$$. In $$B^\top w$$, the market intercept exposure is $$0.5(1)-0.5(1)=0$$. Momentum exposure is $$0.5(1)-0.5(-1)=1$$. The long and short cancel the common intercept. Their momentum exposures add. The index-beta limit later in the article uses estimated stock betas.

The model treats factor returns and residuals as uncorrelated, so total stock covariance is $$\Sigma=BFB^\top+\operatorname{Cov}(\epsilon)$$. Let A, B and C have specific volatilities of 2%, 2% and 1%, with zero residual correlations. That adds 4, 4 and 1 to the diagonal of $$BFB^\top$$.

<div class="matrix-calculation" role="group" aria-label="Total stock covariance with a diagonal residual model">
  {% include worked-matrix.html matrix=example.total_stock_covariance symbol="Σ" label="Total stock covariance" mark_row="A" mark_column="B" %}
</div>

The spread’s variance comes from the two individual variances and the cross term. With a short in B, its weight enters with a minus sign.

$$
w^\top\Sigma w=\frac{9+9-2(3)}{4}=3.
$$

The three units of daily variance are one from momentum and two from the individual residuals. That calculation changes if the residuals move together.
{: #the-average-residual-hides-groups}

## What goes into a position

At each rebalance I use the Russell 1000 membership recorded by that close. Ridge ranks expected return per unit of risk within sectors. The joint optimizers start with the 75 highest scores as long candidates and the 75 lowest as short candidates. They can retain existing positions from the union of the top and bottom 175. They use the same sizing score, the Ridge prediction times trailing 21-session daily volatility, and the same turnover penalty.

- **Volatility scaling** is the simple benchmark. It starts with equal weights on each side and multiplies each by 20% divided by its trailing 60-session annualized volatility, with a 5% volatility floor. A 40%-volatility stock starts at half its equal weight. Each sleeve can use up to one dollar per dollar of capital. This benchmark sizes stocks one at a time.
- **Stock shrinkage** is the main benchmark for the covariance comparison. It shrinks the 756-session stock correlation matrix halfway toward the identity. The stock volatilities use 21 sessions and a 1.18 multiplier.
- **Sector and style factors** estimate stock covariance from a market intercept, broad sectors and seven styles, including momentum, size and liquidity. The model adds each stock’s specific variance and starts with zero pairwise residual correlations.
- **Factor target** keeps the stock-shrinkage volatilities and averages the historical correlation matrix with the total correlation implied by the factor model, including shrunk residual correlations. For a pair with 0.40 historical correlation and 0.20 factor-implied correlation, stock shrinkage uses 0.20 and the factor target uses 0.30.

At each close I fit $$r_t=B_{t-1}f_t+\epsilon_t$$ across stocks. I know the exposures $$B_{t-1}$$ from the previous close and observe today’s stock returns $$r_t$$. The regression estimates today’s factor returns $$f_t$$ and leaves one residual per stock, $$\epsilon_t$$. The fitted return histories give me the factor covariance and each stock’s specific variance.

For the factor target, I first divide each model-implied stock covariance by the two model-implied stock volatilities to get a correlation. I average that matrix with the historical stock correlation matrix. Finally, I turn the result back into covariance using the same stock volatilities as the stock-shrinkage benchmark. That keeps the two models’ standalone stock risks equal while changing how they estimate co-movement.

### The limits apply to target weights

The joint optimizers use the same limits. Gross exposure can reach twice capital, net exposure stays within ±25%, and a single name can use up to 4%. Each sector is limited to ±20% net and 30% of either sleeve. The estimated index beta stays within ±0.05 at the decision close.

The risk budget is separate. If $$w$$ is the vector of signed capital weights and $$\Sigma$$ is the daily stock covariance, the optimizer requires annualized forecast volatility $$\sqrt{252\,w^\top\Sigma w}$$ to stay at or below 7%. Style exposures enter through that covariance, without separate style caps. A 3%-long and 3%-short position in the same sector adds zero sector net. If their estimated index betas are 1.4 and 0.8, the pair still adds $$0.03(1.4-0.8)=0.018$$ to portfolio beta.

The stock membership is dated. The sector and industry labels come from a single August 2026 snapshot, so historical labels may reflect later reclassifications.

I replayed the same Ridge forecasts in the Russell 1000 on three staggered schedules, each rebalancing every three weeks against $5 million. All four rules trade from filled holdings, with next-close execution and a 10% cap on participation in average daily dollar volume for ordinary fills. From 2011 I charge 5 bp on long trades and 7.5 bp on short trades, with higher rates earlier.

The portfolio comparisons use 5,773 common sessions from 26 January 1999 through 31 December 2021 and 1,103 from 3 January 2022 through 27 May 2026. The later period includes history I had already seen in related research.

## The same holdings reveal a gap in risk forecasts

I kept each portfolio’s filled shares and compared forecasts of their daily risk through the next rebalance. Across **227 completed later cycles** on the stock-shrinkage book, stock shrinkage forecast **7%** and the factor target forecast **about 10%**, against **9.6%** annualized gross risk. On the original factor book, the target overshot realized volatility by more than two points. The result depended on which book I priced.

I then calibrated each model on the same holdings. I multiplied forecast variance by the average realized-to-forecast variance ratio over the last 52 completed cycles. Both forecasts came out near **9.7%** on the stock-shrinkage holdings. To compare accuracy across cycles, I scored forecast variance $$v$$ against mean squared daily return $$u$$ using $$\log v+u/v$$. Lower is better. Stock shrinkage scored better on its own holdings. On the other two reference books the paired intervals included zero, so this gives limited grounds for preferring either risk forecast across books.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/fixed-book" mobile="/assets/factor-risk-sizing/fixed-book_mobile" version="1" alt="On the same stock-shrinkage holdings, the two models forecast 7% and about 10% in the later period. Calibration brings both forecasts close to the 9.6% realized gross volatility." %}
</div>
<p class="figure-caption">Compare each marker’s horizontal distance from the dashed line, the subsequent volatility of the same filled stock-shrinkage book. Open circles are the original forecasts. Diamonds are forecasts recalibrated with the last 52 completed holding periods. The top panel starts in 2000 once calibration history is available.</p>

## Comparing the hedges on the same stocks

I let each risk model choose weights for the same stocks. For Ridge scores $$s$$, I minimize $$w^\top\Sigma w$$ while holding $$w^\top s$$ at the equal-weight spread’s score. The gross long and short weights are each 50%, and each name stays between one-quarter and three times its side’s equal weight. Multiplying every covariance by the same number leaves the minimum-variance weights unchanged. In the full portfolio, the same multiplier can change how much exposure fits inside the 7% budget.

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

At three weeks, 150 names gave the clearest reduction in risk relative to diagonal residuals. The smaller spreads gave inconclusive results, and the comparison with stock shrinkage remains open at all three sizes. These tests tell me about the hedge weights on a fixed set of stocks. The portfolio replay also has to account for which stocks the optimizer takes, how much it puts into them and what trades it needs to get there.

## The portfolio comparison after fees
{: #how-the-risk-estimate-changes-the-portfolio}

<table class="research-table comparison-table compact-table">
  <caption>Net long/short portfolio outcomes. Each row averages statistics calculated separately for the three schedules. Net return is the annualized compound growth rate. Sharpe uses the arithmetic mean of daily net returns, a zero cash rate and 252 sessions per year. Drawdown is the largest peak-to-trough loss. Turnover counts purchases and sales in multiples of capital per year.</caption>
  <thead><tr><th>Sizing rule</th><th>Net return</th><th>Vol.</th><th>Sharpe</th><th>Drawdown</th><th>Turnover</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="6">January 1999 – December 2021</th></tr>
    <tr><th scope="row">Volatility scaling</th><td>7.12%</td><td>8.07%</td><td>0.89</td><td>20.07%</td><td>28.49×</td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>10.77%</td><td>8.74%</td><td>1.21</td><td>18.52%</td><td>25.65×</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>7.95%</td><td>8.13%</td><td>0.98</td><td>19.10%</td><td>26.49×</td></tr>
    <tr><th scope="row">Factor target</th><td>9.50%</td><td>7.47%</td><td>1.25</td><td>15.79%</td><td>25.17×</td></tr>
    <tr class="period-heading"><th colspan="6">January 2022 – May 2026</th></tr>
    <tr><th scope="row">Volatility scaling</th><td>6.96%</td><td>10.16%</td><td>0.71</td><td>9.41%</td><td>24.36×</td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>7.42%</td><td>9.65%</td><td>0.79</td><td>9.84%</td><td>18.76×</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>2.72%</td><td>8.29%</td><td>0.37</td><td>10.54%</td><td>18.28×</td></tr>
    <tr><th scope="row">Factor target</th><td>4.59%</td><td>7.27%</td><td>0.65</td><td>7.64%</td><td>16.66×</td></tr>
  </tbody>
</table>

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/performance" mobile="/assets/factor-risk-sizing/performance_mobile" version="3" alt="Net growth of the three long/short Ridge portfolios above their drawdowns on the same timeline. Stock shrinkage finished ahead of the factor target and sector and style factors." %}
</div>
<p class="figure-caption">The top panel shows how $1 grew after fees on a log scale. Each path compounds the mean daily return across schedules. Below, drawdown is the percentage loss from each path’s previous peak. The table calculates drawdown separately for each schedule before averaging.</p>

Of the three joint optimizers, the factor target came closest to its 7% volatility budget in both periods. From 2022 to May 2026, realized volatility was **7.3%** for the factor target, **8.3%** for sector and style factors and **9.7%** for stock shrinkage. Stock shrinkage also earned the most after fees. To compare what the optimizers did with similar amounts of risk, I looked at how each one interpreted the budget.

## Why the same risk budget produced different volatility

The original factor target held about **$1.24** of gross exposure per dollar of capital in the later period, against **$1.56** for stock shrinkage. It also had smaller drawdowns. To see how much the smaller book explained, I changed the level of the volatility forecast while keeping the relative risks within each covariance estimate fixed.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/realized-risk" mobile="/assets/factor-risk-sizing/realized-risk_mobile" version="1" alt="Trailing annualized volatility of the original sizing rules before the rolling calibration." %}
</div>
<p class="figure-caption">Each monthly point shows trailing 252-session net volatility averaged across schedules. The 7% line is the limit on each optimizer’s own forecast at rebalance. Stock shrinkage ran above the factor target throughout the chart. It traded places with the sector-and-style book before 2022, then stayed above it at every later point shown.</p>

At each decision close, I priced the stock-shrinkage portfolio’s filled holdings with both models. To give stock shrinkage the factor target’s risk level, I rescaled its covariance until the two forecasts agreed on those reference holdings. I also ran the reverse. Each optimizer then selected its own positions and simulated trades from its own prior fills.

<table class="research-table comparison-table compact-table">
  <caption>Each cell shows annualized net compounded return / realized volatility. Within each pair of rows the models agree on the risk of the reference holdings. The later history runs through May 2026.</caption>
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

In the later period, switching to the factor target’s risk level reduced realized volatility by **about 2.4 percentage points** across both sets of stock relationships. At a common risk level the volatility difference was negligible, with an interval spanning roughly a fifth of a point either way. The level explains most of the volatility gap. At either level the factor target earned less in the later sample, with considerable uncertainty around the return difference.

## Trading with a calibrated risk budget

The scale swap is a way to diagnose the result. For a sizing rule I can carry forward, I need a way to adjust risk using information available at the rebalance. I replayed each optimizer with a multiplier estimated from the last 52 completed cycles of its original book. Each new replay starts trades from its own holdings.

<table class="research-table comparison-table compact-table">
  <caption>Outcomes with the rolling calibration applied inside each optimizer. Gross is long plus absolute short market value per dollar of capital. Returns and volatility are annual, after fees.</caption>
  <thead><tr><th>Sizing rule</th><th>Net return</th><th>Volatility</th><th>Sharpe</th><th>Gross</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="5">January 1999 – December 2021</th></tr>
    <tr><th scope="row">Stock shrinkage</th><td>9.80%</td><td>7.41%</td><td>1.30</td><td>1.65</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>7.56%</td><td>7.25%</td><td>1.04</td><td>1.44</td></tr>
    <tr><th scope="row">Factor target</th><td>9.38%</td><td>7.12%</td><td>1.29</td><td>1.62</td></tr>
    <tr class="period-heading"><th colspan="5">January 2022 – May 2026</th></tr>
    <tr><th scope="row">Stock shrinkage</th><td>6.10%</td><td>7.13%</td><td>0.87</td><td>1.19</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>2.44%</td><td>6.92%</td><td>0.38</td><td>0.96</td></tr>
    <tr><th scope="row">Factor target</th><td>4.48%</td><td>7.00%</td><td>0.66</td><td>1.19</td></tr>
  </tbody>
</table>

All three portfolios realized about **7% volatility** in the later period. Stock shrinkage and the factor target also held almost identical gross exposure. Stock shrinkage earned **6.1%** a year after fees, the factor target **4.5%**, and sector and style factors **2.4%**. Most of the gap between stock shrinkage and the factor target came from the short sleeve before fees. The factor target’s net Sharpe was about **0.2 lower**, with a paired interval that included zero.

## A wider candidate list changes both holdings and turnover

I also replayed all four sizing rules with **100 and 150 new candidates per side**. These are entry limits. At 150 per side the later stock-shrinkage and factor-target books held about **175 and 123 stocks**, respectively. At that width, volatility scaling earned **5.51%** after fees at **8.88%** volatility, between stock shrinkage and the factor target on both measures. Across all three widths the factor target stayed roughly 2.4 volatility points below stock shrinkage, with no clear Sharpe advantage. The comparable-risk replay covers the 75-per-side case.

<table class="research-table comparison-table compact-table">
  <caption>Compounded annual net return as the number of eligible new positions changes. Column labels count entry candidates per side. Each cell averages three separately traded schedules.</caption>
  <thead><tr><th>Sizing rule</th><th>75 per side</th><th>100 per side</th><th>150 per side</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="4">1999–2021</th></tr>
    <tr><th scope="row">Volatility scaling</th><td>7.12%</td><td>6.43%</td><td>5.75%</td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>10.77%</td><td>10.41%</td><td>10.44%</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>7.95%</td><td>7.71%</td><td>8.12%</td></tr>
    <tr><th scope="row">Factor target</th><td>9.50%</td><td>9.06%</td><td>9.32%</td></tr>
    <tr class="period-heading"><th colspan="4">2022–May 2026</th></tr>
    <tr><th scope="row">Volatility scaling</th><td>6.96%</td><td>6.76%</td><td>5.51%</td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>7.42%</td><td>7.20%</td><td>6.69%</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>2.72%</td><td>2.51%</td><td>2.17%</td></tr>
    <tr><th scope="row">Factor target</th><td>4.59%</td><td>4.37%</td><td>3.75%</td></tr>
  </tbody>
</table>

The wider list also left fewer ranks between entry and exit. At 150 entries, extending retention from rank 175 to 250 cut two-way turnover by **4.5× capital** per year for stock shrinkage and **3.2×** for the factor target. The return differences between the two retention rules were uncertain.

At 150 per side, leaving out 2024 put the two models close to even on later Sharpe. That width check shows how much the ranking depends on a particular part of the sample.

Exposure changed with breadth too. At 150 per side both models met the ±0.05 estimated beta band at the decision close. The later filled factor-target book had a realized index beta of about **0.06**, versus **0.02** for stock shrinkage. A common beta band still allowed different market exposures after execution.

## Stock shrinkage remains the reference

I would keep stock shrinkage for this Ridge portfolio. The factor model gives me a useful way to see what the book is exposed to. Estimating residual correlations also helped the factor model choose hedge weights across the stocks I gave it. In the portfolio replay, calibrating the risk budget brought both covariance models close to 7% realized volatility, and there was no clear gain from switching to the factor target.

The comparison I’d want next is a wider book with a common beta target and comparable realized risk on new dates. That would put less weight on what happened in 2024 and make it easier to see whether the covariance choice improved the trades themselves.

## References

- Volatility scaling. [Paleologo, *Advanced Portfolio Management*, §6.3](https://www.wiley.com/en-us/advanced-portfolio-management-a-quant%27s-guide-for-fundamental-investors-p-9781119789802)
- Correlation shrinkage. [Pedersen, Babu and Levine, *Enhanced Portfolio Optimization*](https://doi.org/10.1080/0015198X.2020.1854543)
