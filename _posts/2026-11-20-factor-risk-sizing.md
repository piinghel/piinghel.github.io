---
layout: post
interactive_charts: true
title: "Shrinking Stock Correlations Toward a Factor Model"
description: "I kept the Ridge stock forecasts fixed and changed how the long/short portfolio measures risk. The factor model found common shocks, but the choice of shrinkage target mattered more for sizing."
date: 2026-11-20
categories: ["Portfolio construction"]
article_label: Portfolio construction · Factor risk
permalink: /quants/factor-risk-sizing.html
---

Suppose the Ridge model wants to buy two banks. Their prices have moved together, so buying both gives me less diversification than their individual volatilities suggest. Now change the second order to a short. The very same correlation makes the pair a better hedge. A risk model has to get both decisions reasonably right.

In [From Volatility Scaling to Joint Sizing]({% link _posts/2026-08-29-joint-sizing.md %}), I estimated stock correlations directly and shrank them halfway toward zero. Here I keep the stock forecasts fixed and give the optimizer another way to understand the positions it holds. Stocks can move together because of the market, their sector or their exposure to styles such as momentum. I wanted to see how much of that structure survives in returns *after* the named factors come out, and whether incorporating it gives me a better long/short portfolio after fees.

## What goes into a position

The simple benchmark starts with the top and bottom 75 eligible Ridge scores and sizes each stock inversely to its own volatility. The joint optimizer sizes the two sides together under a 7% annual risk budget. It can retain existing positions while their ranks remain within the top or bottom 175. Each position is capped at 4% of capital. At each decision it can allocate up to twice its capital in gross exposure, with net exposure within ±25% and estimated market beta within ±0.05.

I use two starting estimates for joint sizing. **Stock shrinkage** measures volatility over 21 sessions and correlation over 756. It keeps half of each measured pairwise correlation and multiplies the resulting portfolio volatility forecast by 1.18. Halving a positive correlation reduces estimated risk for two longs and increases it for an offsetting pair. The multiplier adjusts the overall level separately.

**Sector and style factors** explain each day’s stock returns with the market, broad sectors and seven styles. The styles are momentum, short-term return, beta, residual volatility, size, liquidity and short interest. I use exposures available at the preceding close, weight the squared regression errors by the square root of prior market capitalization, and estimate factor covariance and specific variance with a 63-session half-life.

For a portfolio with signed stock weights $$w$$, the factor estimate is

$$
\widehat{\mathrm{Var}}(r_p)=(B^\top w)^\top F(B^\top w)+(Dw)^\top R_\varepsilon(Dw).
$$

The first term collects the portfolio’s exposures to the named factors, $$B^\top w$$, and uses their return covariance $$F$$. In the second, $$D$$ contains each stock’s residual volatility. I start with $$R_\varepsilon=I$$, so a stock contributes its own unexplained variance and gives no residual hedge against another stock. This assumes zero pairwise residual covariance in the forecast. It also assumes zero covariance between the factor shocks and the residual shocks. Neither assumption requires statistical independence.

## The average residual hides groups

Across 1,429 weekly observations, the mean trailing one-year stock correlation was **29.71%**. For the same stock pairs, the mean residual correlation was **−0.06%**. The regression itself helps produce that second number. With a market term in the fit, the weighted residuals balance across stocks each day. Positive correlations in one group can coexist with offsetting correlations elsewhere.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/residuals" mobile="/assets/factor-risk-sizing/residuals_mobile" version="1" alt="Stock correlation rises in stressed markets while average residual correlation stays near zero. In each of 27 forward years, residual correlation within previously identified groups exceeds the sector-matched shuffle threshold." %}
</div>
<p class="figure-caption">Above, each point uses 252 sessions. Below, each dot measures how much more correlated pairs in the same group were during the following year, in percentage points. The short marks show the 95th percentile after shuffling group labels within sectors.</p>

At each of 27 year-ends I grouped stocks using their trailing residual correlations, froze the eleven groups, and measured the next 252 sessions. Within-group correlation exceeded between-group correlation by **4.74 percentage points** when forming the groups and **2.06 points** the following year, giving each year equal weight. The groups retained some information about future co-movement. How much that information is worth depends on the signs and sizes of the positions.

I tried three ways of letting residuals move together. The first principal component keeps one shared direction and assigns the remaining variance to each stock. Ledoit–Wolf shrinkage keeps a fraction of **all** estimated residual correlations, with the fraction estimated from the trailing sample. The combination keeps the first component, shrinks the remaining covariance toward its diagonal, and adds the component back once. [Ledoit and Wolf](https://www.ledoit.net/Well-conditioned2004.pdf)

## How the risk estimate changes the portfolio

I replayed the same Ridge forecasts on three schedules. Each trades every three weeks, offset by one week from the next. Each simulation starts with $5 million. Trades are sized from shares actually held, can fill at the following close and are subject to a liquidity limit. Both optimizers use the same 2.5 basis point trade penalty. Fees on filled long and short trades were 7.5 and 10 basis points through 2010, then 5 and 7.5. Returns exclude borrow, financing and additional market impact.

Prices begin in 1995. After allowing for estimation history and common portfolio availability, the development comparison covers 5,773 trading days from 26 January 1999 through 31 December 2021. The later comparison covers 1,103 days from 3 January 2022 through 27 May 2026. I had already seen some of the later history in related research, so it is a historical check on the choices made here.

The fourth sizing rule, **factor target**, changes one input to stock shrinkage. I keep the 21-session stock volatilities, the 1.18 multiplier and half the historical stock correlation. For the other half I use the *total stock correlation* implied by the sectors, styles and shrunk residuals. A pair of stocks can now retain a common exposure even if its direct sample correlation is imprecise.

<table class="research-table comparison-table compact-table">
  <caption>Net long/short portfolio outcomes. Each row averages statistics calculated separately for the three schedules. Return is compounded annually, volatility is annualized, drawdown is the largest peak-to-trough loss, and turnover counts purchases and sales in multiples of capital per year.</caption>
  <thead><tr><th>Sizing rule</th><th>Net return</th><th>Vol.</th><th>Sharpe</th><th>Drawdown</th><th>Turnover</th></tr></thead>
  <tbody>
    <tr><th colspan="6">January 1999 – December 2021</th></tr>
    <tr><td>Volatility scaling</td><td>7.12%</td><td>8.08%</td><td>0.89</td><td>20.07%</td><td>28.49×</td></tr>
    <tr><td>Stock shrinkage</td><td>10.77%</td><td>8.74%</td><td>1.21</td><td>18.52%</td><td>25.65×</td></tr>
    <tr><td>Sector and style factors</td><td>7.95%</td><td>8.13%</td><td>0.98</td><td>19.10%</td><td>26.49×</td></tr>
    <tr><td>Factor target</td><td>9.50%</td><td>7.47%</td><td>1.25</td><td>15.79%</td><td>25.17×</td></tr>
    <tr><th colspan="6">January 2022 – May 2026</th></tr>
    <tr><td>Volatility scaling</td><td>6.96%</td><td>10.16%</td><td>0.71</td><td>9.41%</td><td>24.36×</td></tr>
    <tr><td>Stock shrinkage</td><td>7.42%</td><td>9.65%</td><td>0.79</td><td>9.84%</td><td>18.76×</td></tr>
    <tr><td>Sector and style factors</td><td>2.72%</td><td>8.29%</td><td>0.37</td><td>10.54%</td><td>18.28×</td></tr>
    <tr><td>Factor target</td><td>4.59%</td><td>7.27%</td><td>0.65</td><td>7.64%</td><td>16.66×</td></tr>
  </tbody>
</table>

<div class="research-figure responsive-figure">
  {% include blog-chart.html chart="performance" source="/assets/factor-risk-sizing/performance.json?v=1" base="/assets/factor-risk-sizing/performance" mobile="/assets/factor-risk-sizing/performance_mobile" version="1" label="Net growth and drawdown of the long/short Ridge portfolios from January 1999 to May 2026." %}
</div>
<p class="figure-caption">The chart compounds the mean daily net return across schedules. The table measures each schedule’s own experience, so its worst drawdown can differ from the chart. Select the later period to see how the paths diverged after 2021.</p>

The later return gap between the original factor model and stock shrinkage was **4.70 percentage points per year**. Fees were almost identical at 1.12% and 1.15% of capital a year. The short positions explain more. Before fees, the factor shorts lost 4.01% of capital a year and the stock-shrinkage shorts lost 0.87%. About two-thirds of the gross arithmetic P&L gap came from that side of the book.

Changing just the residual model moved later annual net return from 2.72% to **3.05%** with one principal component, **3.97%** with residual shrinkage, and **3.81%** with both. Across the entire history, preserving the first component on top of shrinkage changed net Sharpe by just **+0.002**. The paired 95% block interval ran from −0.017 to +0.021. The clustering result gave me a reason to model residual covariance. It gave me little reason to give that first component special treatment.

## The improvement I would keep

Using the factor model as a shrinkage target recovered about **40% of the later return gap**. It also changed the experience of holding the portfolio. In the worst 5% of later trading days it lost an average of **1.02%** per day, against **1.35%** for stock shrinkage. Its maximum drawdown was shallower, although its longest spell below a previous peak lasted **190 sessions**, against **140**. Its realized beta to the Russell 1000 was **+0.037**, against **−0.001** for stock shrinkage. The improvement in loss severity came with a little more market sensitivity and a longer wait for recovery.

Some of that protection came from taking less risk. I also reran stock shrinkage with the earlier article’s 1.55 multiplier. It delivered **7.47%** later volatility, close to the factor target’s **7.27%**, and still earned **6.19%** net annually versus **4.59%**. That comparison is why I would keep stock shrinkage as the reference for this Ridge portfolio.

I would retain the factor target as a candidate. Its full-history Sharpe gain over the original factor model was 0.28, with a one-sided 95% lower bound of 0.04 after accounting for ten recorded comparisons and resampling common 63-session blocks. For the later period alone that lower bound was −0.24. The part I find most persuasive is the combination of two observations. Residual groups persisted into the next year, and using that structure alongside measured stock correlations produced a portfolio with smaller losses in both periods. That is a narrower and more useful conclusion than choosing a risk model by how much variation it explains in yesterday’s returns.
