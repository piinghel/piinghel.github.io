---
layout: post
interactive_charts: true
title: "Shrinking Stock Correlations Toward a Factor Model"
description: "I kept the Ridge stock forecasts fixed and changed how the long/short portfolio measures risk. I compared risk forecasts on the same holdings, hedges on the same stocks, and long/short returns at similar realized risk."
date: 2026-11-20
last_modified_at: 2026-11-20
categories: ["Portfolio construction"]
article_label: Portfolio construction · Factor risk
permalink: /quants/factor-risk-sizing.html
---

Imagine I’m $100 long NVIDIA and $100 short Workday. The dollars cancel in the technology sector, but a delay in data-center orders could hurt NVIDIA and barely touch Workday’s software sales. Vertiv sells power and cooling equipment for those data centers. It belongs to a different sector and could be the more useful hedge. [Vertiv’s October 2024 announcement](https://www.vertiv.com/en-emea/about/news-and-events/news-releases/vertiv-codevelops-with-nvidia-complete-power-and-cooling-blueprint-for--nvidia-gb200-nvl72-platform/)
{: .mathjax-ignore}

The example gives me a reason to look at how stocks move together after accounting for sectors and styles. The [January 2025 case]({% link _posts/2026-11-20-residual-risk.md %}#would-the-model-have-grouped-nvidia-and-vertiv) shows the limits too. The December groups put all three stocks in different clusters, and the simulated Ridge portfolios held none of them on the day of the selloff.

In [From Volatility Scaling to Joint Sizing]({% link _posts/2026-08-29-joint-sizing.md %}), I used historical stock correlations shrunk halfway toward zero. Here I keep the Ridge forecasts fixed. Does a different risk estimate forecast the risk of the same holdings more accurately, pick better hedges from the same stocks, and improve the portfolio after trading fees?

## What goes into a position

At each rebalance I use the Russell 1000 membership recorded by that close. Ridge ranks expected return per unit of risk within sectors. The joint optimizers start with the 75 highest scores as long candidates and the 75 lowest as short candidates. They can retain existing positions from the union of the top and bottom 175. Each uses the same sizing score, the Ridge prediction times trailing 21-session daily volatility, and a 2.5 bp penalty on changes from filled holdings.

The joint portfolios share a 7% annual forecast risk budget, a 4% cap per stock and the same gross, net, beta and sector limits. The simpler volatility-scaling benchmark starts with equal weights on each side and scales each name by its own volatility.

- **Stock shrinkage** uses 21-session stock volatilities, keeps half of each correlation estimated over 756 sessions and applies a 1.18 multiplier to forecast volatility.
- **Sector and style factors** explain daily returns with the market, broad sectors and seven styles. A stock’s residual is its return minus the fitted return. The model forecasts common factor risk and each stock’s own residual variance, with zero correlation between residuals.
- **Factor target** keeps the stock volatilities, the 1.18 multiplier and the half-weight on historical stock correlations. It replaces zero as the other half of the correlation estimate with the total stock correlation implied by named factors and shrunk residuals.

The factor regressions lag the measured exposures by one close. The historical runs use a single August 2026 sector and industry classification snapshot. Membership is dated, while the classifications can reflect information that arrived later. That matters for the factor fits and for comparisons that match stocks by industry.

## The average residual hides groups

Across 1,429 weekly observations, the same pairs averaged **29.71%** correlation on stock returns and **−0.06%** on residuals. The factor fit removes much of the common movement. Within some groups, the residuals still move together.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/matrix" mobile="/assets/residual-risk/matrix_mobile" version="2" alt="For the same 850 stocks, mean correlation is 24.68% on 2021 stock returns and near zero after removing factors. Positive residual blocks remain visible across the same stock groups in the following year." %}
  <p class="figure-caption">All three panels use the same 850 stocks with complete observations in both windows. The outlines and stock order come from the December 2021 residual groups and stay fixed. Each tile averages distinct pairs and uses the same color scale. Colors saturate at ±40%.</p>
</div>

In this cohort, which showed the strongest persistence of the 27, the average fell from **24.68% to −0.02%** when I removed the factors. The outlined groups were still **8.45 percentage points** more correlated internally than between groups. The next 252 sessions, with the groups unchanged, delivered a **5.05-point** gap. Across all 27 cohorts the forward gap was **2.06 points**, versus **0.35 points** when I shuffled the labels within industries. The [companion article]({% link _posts/2026-11-20-residual-risk.md %}#groups-identified-in-one-year-still-move-together-in-the-next) shows all 27 comparisons and tests which residual relationships are worth carrying forward.

## How the risk estimate changes the portfolio

I simulated the same Ridge forecasts on three staggered schedules, each rebalancing every three weeks against $5 million. Orders start from filled holdings, can execute at the following close and face the same 10% limit on prior 21-session average daily dollar volume. The optimizer penalty affects the orders. The simulation separately charges 7.5 bp on long trades and 10 bp on short trades through 2010, then 5 and 7.5 bp. The net figures include those fees and exclude borrow, financing and additional market impact. The simulation priced stopped-quote exits at the last available mark, covering 0.49% of traded dollars across the tested books.

The portfolio comparisons use 5,773 common sessions from 26 January 1999 through 31 December 2021 and 1,103 from 3 January 2022 through 27 May 2026. The later period includes history I had already seen in related research.

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
  {% include blog-chart.html chart="performance" source="/assets/factor-risk-sizing/performance.json?v=1" base="/assets/factor-risk-sizing/performance" mobile="/assets/factor-risk-sizing/performance_mobile" version="1" label="Net growth and drawdown of the long/short Ridge portfolios from January 1999 to May 2026." %}
</div>
<p class="figure-caption">The chart compounds the mean daily net return across schedules. The table averages the three schedules’ statistics, so its drawdowns can differ from the chart.</p>

The factor target improved on the original factor model in the later period. It also ran at **7.27%** realized volatility compared with **9.65%** for stock shrinkage. The two optimizers had the same 7% forecast budget, yet they took different amounts of risk. That makes the return comparison hard to interpret without pricing the same holdings and then replaying the portfolios at comparable risk.

<details markdown="1">
<summary>Sensitivity to the entry pool</summary>

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

The factor target also ran at lower volatility with 100 and 150 candidates per side. The wider pool with the same retention rule increased its later turnover and left the return ranking unchanged. [Download all 24 portfolio comparisons (CSV)](/assets/factor-risk-sizing/entry-breadth.csv).
</details>

## The same holdings reveal a gap in risk forecasts

I kept the incumbent stock-shrinkage portfolio’s filled shares and compared forecasts of their daily risk through the next rebalance. Across the same **227 completed later cycles**, stock shrinkage forecast **7.00%** and the factor target forecast **9.95%**, against **9.64%** annualized gross risk. On the original factor portfolio the target forecast 10.57% against 8.28% realized, so the closer forecast on the incumbent depended on which book I priced.

I then calibrated each model on the same holdings using the last 52 completed cycles. I multiplied forecast variance by the average ratio of realized to forecast variance in those cycles. On the incumbent’s later positions the forecasts converged to **9.73% and 9.72%**. Calibrated stock shrinkage scored better across those cycles. The factor target’s average variance-forecast loss (QLIKE) was **0.014 higher**, with a paired 95% interval of **0.005 to 0.025**. The score penalizes both underpredicting large moves and systematically quoting too much risk. [Paleologo, *The Elements of Quantitative Investing*, §5.1](https://www.wiley.com/en-us/shop/general-finance-investments/the-elements-of-quantitative-investing-p-9781394265466) · [Patton on comparing volatility forecasts](https://public.econ.duke.edu/~ap172/Patton_vol_proxies_JoE_2011.pdf)

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/fixed-book" mobile="/assets/factor-risk-sizing/fixed-book_mobile" version="1" alt="Same stock-shrinkage holdings. Over the later cycles, the stock model's forecast moves from 7.00% to 9.73% after calibration and the factor target moves from 9.95% to 9.72%. Realized gross volatility was 9.64%." %}
</div>
<p class="figure-caption">The open circles show uncalibrated forecasts. The diamonds use the last 52 completed cycles. Both models price the same filled shares, whose subsequent risk is the dashed line. The development comparison starts in 2000 once calibration history is available. <a href="/assets/factor-risk-sizing/fixed-book-forecasts.csv">Download forecasts for all three portfolios (CSV).</a></p>

## Comparing the hedges on the same stocks

I let each risk model choose weights for the same stocks. The optimizer targeted the same Ridge score exposure, 50% long and 50% short, with each name between one-quarter and three times its side’s equal weight. Multiplying every covariance by the same number leaves the minimum-variance weights unchanged. In the full portfolio, the same multiplier can change how much exposure fits inside the 7% budget. [Paleologo, §5.2.1](https://www.wiley.com/en-us/shop/general-finance-investments/the-elements-of-quantitative-investing-p-9781394265466) · [Engle and Colacito on matched-return minimum-variance portfolios](https://www.stern.nyu.edu/rengle/EngleColacito.pdf)

I drew 32 groups of stocks per weekly decision and compared gross returns for the session after the next close. The extra stock draws test whether the result depends on the names selected, with the same 1,426 weekly dates throughout. Later 150-stock spreads fell from **3.69% to 3.53%** annualized volatility when I added shrunk residual correlations to the factor model.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/stock-draws" mobile="/assets/factor-risk-sizing/stock-draws_mobile" version="1" alt="32 stock selections at each decision. Shrinking residual correlations reduces annualized spread volatility relative to stock shrinkage and to the factor model with zero residual correlations, at 75, 100 and 150 stocks in both periods." %}
</div>
<p class="figure-caption">Negative differences mean the spreads with shrunk residual correlations were quieter. The right panel changes only residual correlations. The 95% intervals account for six comparisons per period and resample stock paths and common 13-week blocks. <a href="/assets/factor-risk-sizing/stock-draws.csv">Download levels and paired differences (CSV).</a></p>

<details markdown="1">
<summary>Results for the original three stock draws</summary>

<table class="research-table comparison-table compact-table">
  <caption>Annualized realized volatility for the first three stock selections at each decision. Breadth counts the stocks across both sides together. Each row uses the same stocks and dates for all four models.</caption>
  <thead><tr><th>Stocks in spread</th><th>Stock shrinkage</th><th>Original factors</th><th>Shrunk residuals</th><th>Factor target</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="5">1999 – 2021</th></tr>
    <tr><th scope="row">75</th><td>4.33%</td><td>4.01%</td><td>3.97%</td><td>4.01%</td></tr>
    <tr><th scope="row">100</th><td>3.86%</td><td>3.57%</td><td>3.54%</td><td>3.56%</td></tr>
    <tr><th scope="row">150</th><td>3.27%</td><td>3.12%</td><td>3.07%</td><td>3.04%</td></tr>
    <tr class="period-heading"><th colspan="5">2022 – May 2026</th></tr>
    <tr><th scope="row">75</th><td>4.90%</td><td>4.62%</td><td>4.52%</td><td>4.68%</td></tr>
    <tr><th scope="row">100</th><td>4.42%</td><td>4.19%</td><td>4.04%</td><td>4.21%</td></tr>
    <tr><th scope="row">150</th><td>3.84%</td><td>3.68%</td><td>3.48%</td><td>3.55%</td></tr>
  </tbody>
</table>


</details>

I also compared one session with the three-week holding period used in the portfolio replay. For the same eight stock paths and 227 later starting dates, the test assumes full fills where the next close has a quote and leaves other allocations in cash. The returns are gross. At 150 stocks, adding shrunk residuals reduced annualized 15-session volatility from **3.35% to 3.22%**, a **0.13-point** reduction with a simultaneous 95% interval of **0.04 to 0.21 points**. Against stock shrinkage the estimate also favored shrunk residuals, but all three stock counts had intervals that crossed zero at 15 sessions. [Matched one- and 15-session results and intervals (CSV)]({{ '/assets/factor-risk-sizing/hedge-holding-horizons.csv' | relative_url }})

<details markdown="1">
<summary>Volatility reductions by stock count and horizon</summary>

<table class="research-table comparison-table compact-table">
  <caption>Annualized volatility saved by estimating residual correlations, 2022–May 2026. Values are percentage points relative to the same factor model with zero residual correlations. A larger positive number means a quieter spread.</caption>
  <thead><tr><th>Total stocks</th><th>1 session</th><th>15 sessions</th></tr></thead>
  <tbody>
    <tr><th>75</th><td>0.12</td><td>0.08</td></tr>
    <tr><th>100</th><td>0.15</td><td>0.07</td></tr>
    <tr><th>150</th><td>0.16</td><td>0.13</td></tr>
  </tbody>
</table>


</details>

For me, the narrower conclusion is the one these tests answer well. The factor model with shrunk residual correlations found a quieter way to hold the same Ridge score exposure. Whether I earn more from those hedges also depends on how the positions perform over the holding period and what I pay to change them.

## Why the same risk budget produced different volatility

The uncalibrated factor target had shallower drawdowns and lost **1.02%** on its worst 5% of later days, versus **1.35%** for stock shrinkage. It also held about **$1.24** of gross exposure per dollar of capital, against **$1.56** for stock shrinkage. To see how much the smaller book explained, I changed the level of the volatility forecast without changing the relative risks within each covariance estimate.

<details markdown="1">
<summary>Market exposure and tail losses</summary>

<table class="research-table comparison-table compact-table">
  <caption>Market exposure and daily losses of the traded Ridge portfolios. Down-market beta uses only sessions when the index fell. Tail loss is the average loss in the worst 5% of the portfolio’s own days. Each entry averages the three schedules.</caption>
  <thead><tr><th>Sizing rule</th><th>Market beta</th><th>Market corr.</th><th>Down-market beta</th><th>Daily tail loss</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="5">January 1999 – December 2021</th></tr>
    <tr><th scope="row">Volatility scaling</th><td>0.105</td><td>0.256</td><td>0.139</td><td>1.15%</td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>0.082</td><td>0.186</td><td>0.106</td><td>1.19%</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>0.020</td><td>0.047</td><td>0.038</td><td>1.12%</td></tr>
    <tr><th scope="row">Factor target</th><td>0.080</td><td>0.210</td><td>0.099</td><td>1.00%</td></tr>
    <tr class="period-heading"><th colspan="5">January 2022 – May 2026</th></tr>
    <tr><th scope="row">Volatility scaling</th><td>0.071</td><td>0.124</td><td>0.147</td><td>1.42%</td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>−0.001</td><td>−0.001</td><td>0.057</td><td>1.35%</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>−0.003</td><td>−0.006</td><td>0.045</td><td>1.22%</td></tr>
    <tr><th scope="row">Factor target</th><td>0.037</td><td>0.091</td><td>0.079</td><td>1.02%</td></tr>
  </tbody>
</table>


</details>

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

In the later period, switching to the factor target’s risk level reduced realized volatility by **2.39 percentage points** on average across both sets of stock relationships, with a paired 95% interval of **2.26 to 2.51 points**. Changing the relationships at a common risk level moved volatility by **0.01 points** (−0.20 to +0.24). The level explains most of the volatility gap. At either level the factor target earned less in the later sample, with considerable uncertainty around the return difference.

## Trading with a calibrated risk budget

A 7% forecast can deliver quite different realized risk, and the size of that gap changes over time.

<div class="research-figure responsive-figure">
  {% include blog-chart.html chart="realized-risk" source="/assets/factor-risk-sizing/realized-risk.json?v=2" base="/assets/factor-risk-sizing/realized-risk" mobile="/assets/factor-risk-sizing/realized-risk_mobile" version="1" label="Annualized net volatility of the preceding 252 trading sessions, measured at monthly endpoints, with the 7% optimizer forecast budget as a reference." %}
</div>
<p class="figure-caption">Trailing 252-session net volatility, calculated separately for each schedule and averaged at month-end. The line at 7% is the optimizer’s forecast budget.</p>

I replayed each optimizer after adjusting its forecast with the last 52 completed cycles from its own uncalibrated reference book. The staggered schedules supply roughly one completed cycle per week, with overlapping holding periods. The adjustment goes into the optimizer at each rebalance, so the calibrated books choose and pay for their own simulated trades.

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

Stock shrinkage and the factor target both held about **$1.19 gross** per dollar of capital later. At **7.13% and 7.00%** realized volatility, they earned **6.10% and 4.48%** after trading fees. Fees were 0.85% and 0.97% of capital per year. The factor target’s net Sharpe was lower by **0.21**, with a paired 95% interval from **0.55 lower to 0.20 higher**. [Calendar-year outcomes for both sets of portfolios (CSV)]({{ '/assets/factor-risk-sizing/yearly-outcomes.csv' | relative_url }})

The later short sleeve contributed **1.52 percentage points less** a year in the factor-target book before fees. Roughly **0.90 points** came from when it carried more or less short exposure, even though both books averaged about 47 cents short per dollar of capital. This is an attribution of the observed return gap.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/short-funding" mobile="/assets/factor-risk-sizing/short-funding_mobile" version="1" alt="Short-sleeve return attribution. The factor target lost 0.90 percentage points per year from the timing of short exposure in 2022 through May 2026 and 0.53 points in 1999 through 2021. Average funding explains little." %}
</div>
<p class="figure-caption">Contributions to the factor target’s annual arithmetic return relative to stock shrinkage. The three components add to the short-sleeve gap. Lines show paired 95% intervals using 63-session blocks.</p>

A flat 1% annual borrow charge on the saved short holdings cost both later books about **0.48 percentage points** a year. Even assigning security-level rates between zero and 1% entirely in the factor target’s favor narrowed the annual arithmetic gap by at most **0.13 points**. This prices the same fills. Security-level loan fees can exceed that range and availability can change which trades fill.

## Stock shrinkage remains the reference

None of the 27 alternatives in the recorded set showed a reliable net Sharpe gain over stock shrinkage after accounting for the search. I also applied the same random sign to all portfolio return differences in each 63-session block, then picked the best rule. In the later history the average gain under those random signs rose from **1.69 to 2.46 annual arithmetic return points** as the menu went from four rules to 28. More choices made it easier to find a winner even with randomized returns. [Daniel and Paleologo, *Backtesting*, slides 31–35](https://www.linkedin.com/posts/gappy_backtesting-lecture-ugcPost-7528535551839305728-Xbow/)

I would keep stock shrinkage as the Ridge reference. Shrunk residuals made the test spreads quieter than the same factor model with diagonal residuals. The risk-level adjustment did most of the work in bringing the simulated portfolios close to 7% volatility, and the factor target showed no after-fee advantage there. Before switching, I would freeze both calibrated rules and compare them on unseen dates with contemporaneous classifications and security-level borrow and execution costs.
