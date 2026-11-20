---
layout: post
interactive_charts: true
title: "Shrinking Stock Correlations Toward a Factor Model"
description: "I kept the Ridge stock forecasts fixed and changed how the long/short portfolio measures risk. The factor model found common shocks, but the choice of shrinkage target mattered more for sizing."
date: 2026-11-20
last_modified_at: 2026-11-20
categories: ["Portfolio construction"]
article_label: Portfolio construction · Factor risk
permalink: /quants/factor-risk-sizing.html
---

Suppose a cloud provider delays its next round of AI data-center construction. Which positions in my portfolio would feel it? Say I own $100 of a chip designer and I’m short $100 of a payroll software company. My sector report shows zero net dollars in technology. But the chip designer sells into the investment cycle that just slowed, while the payroll company earns subscription fees tied to employment. If the chip stock falls 10% and the payroll stock is flat, I lose $10 on the pair. Equal dollars on the two sides never told me what they were hedging.

Now add a manufacturer that supplies cooling equipment for those data centers. It sits in Industrials, so buying it spreads my dollars across two sectors. It also gives me a second business exposed to the same construction decision. The sign matters just as much as the sector label. Consider a war that interrupts oil supplies. If higher crude prices lift an oil producer and squeeze an airline, being long the producer and short the airline can make money on both legs. Reverse the shock and both legs can lose.

This is what I want to learn from a factor risk model. Once I account for the market, sectors and styles, which stocks still move together? I form groups using a year of residual returns, freeze them, and measure the same pairs over the following year. That lets me test whether the remaining co-movement lasts long enough to matter to my next portfolio. The AI trade is an illustration. Calling a historical cluster an AI trade would require separate evidence about what those businesses depended on at the time.

In [From Volatility Scaling to Joint Sizing]({% link _posts/2026-08-29-joint-sizing.md %}), I estimated stock correlations directly and shrank them halfway toward zero. Here I keep the stock forecasts fixed and give the optimizer another way to understand the positions it holds. Stocks can move together because of the market, their sector or their exposure to styles such as momentum. I wanted to see how much of that structure survives in returns *after* the named factors come out, and whether incorporating it gives me a better long/short portfolio after fees.

## What goes into a position

Ridge is trained to predict how a stock’s forward return per unit of risk ranks within its sector. At a rebalance I rank the eligible stocks by that prediction and start with the 75 highest scores as possible longs and the 75 lowest as possible shorts. These are **75 candidates per side**. The simple benchmark starts with equal weights on each side and scales each stock by 20% divided by its own annualized volatility over 60 sessions, with a 5% floor on that volatility. A more volatile stock gets a smaller weight. This rule can allocate up to a dollar per side for each dollar of capital.

The joint optimizer needs a reason to prefer one position over another. I take the raw Ridge score for a stock and multiply it by that stock’s trailing 21-session daily volatility. All the joint optimizers use this same return-like sizing score. A change in the factor risk estimate changes how much risk a position consumes while leaving its score in the objective alone. Once a portfolio exists, moving one dollar away from the holdings already filled also incurs a 2.5-basis-point penalty in the optimizer. The backtest separately charges the applicable historical fee on each filled trade.

The joint optimizer sees all the positions together. It can retain existing holdings while their ranks remain within the top or bottom 175. A 7% annual portfolio risk budget, a 4% cap per name, a gross exposure limit of twice capital, net exposure within ±25% and estimated market beta within ±0.05 constrain the weights. Each sector has a net limit of ±20% of capital and may account for up to 30% of either sleeve. A 7% *forecast* at the decision close can still lead to 9% *realized* volatility over subsequent sessions. The first number is a model input to sizing. The second comes from the daily returns of the positions that actually filled.

I use two starting estimates for joint sizing. **Stock shrinkage** measures volatility over 21 sessions and correlation over 756. It keeps half of each measured pairwise correlation and multiplies the resulting portfolio volatility forecast by 1.18. Halving a positive correlation reduces estimated risk for two longs and increases it for an offsetting pair. The multiplier adjusts the overall level separately.

**Sector and style factors** explain each day’s stock returns with the market, broad sectors and seven styles. The styles are momentum, short-term return, beta, residual volatility, size, liquidity and short interest. I use exposures available at the preceding close, weight the squared regression errors by the square root of prior market capitalization, and estimate factor covariance and specific variance with a 63-session half-life.

There are two regressions here. First, I look back along each stock’s own history to estimate how it responds to the market. I use up to 252 sessions, requiring at least 126 stock and market return pairs. Then I look *across* stocks on a single day. A group of stocks with high momentum scores might gain more than otherwise similar stocks that day. The cross-sectional regression estimates that day’s momentum factor return while accounting for their other exposures. Subtract each stock’s fitted return from its observed return and I have one residual per stock. Repeating that calculation gives me the history on which I can look for a hidden theme.

For momentum I average two standardized descriptors. The first is the past year’s return skipping the most recent month. The second is the fraction of sessions over the past year when the stock closed above or at its 200-session moving average. Short-term return gets its own exposure using the last 21 sessions. The first regression supplies two more descriptors, the stock’s beta shrunk toward one and the log root-mean-square size of its market-regression residuals. That last number lets the daily cross-section distinguish stocks that historically moved more on their own. The *specific variance* in the risk forecast below comes from the second regression, after accounting for all seven styles and the sectors. A stock can score high on the residual-volatility style and still share a shock with its peers.

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

At each of 27 year-ends I grouped stocks using their trailing residual correlations, froze the eleven groups, and measured the next 252 sessions. Within-group correlation exceeded between-group correlation by **4.74 percentage points** when forming the groups and **2.06 points** the following year, giving each year equal weight. I then shuffled group labels within each industry and sector. Those groups kept exactly the same industry composition and showed a forward difference of just **0.35 points** on average. That leaves **1.71 points** associated with the original grouping. Consider what that permits me to say about the chip designer and the cooling supplier. Historical co-movement can survive a sector-and-style adjustment, and industry membership explains some of it. To identify an AI exposure in a specific group, I would still need independent evidence, such as both firms’ dependence on data-center orders, known when the positions were chosen.

I tried three ways of letting residuals move together. The first principal component keeps one shared direction and assigns the remaining variance to each stock. Ledoit–Wolf shrinkage keeps a fraction of **all** estimated residual correlations, with the fraction estimated from the trailing sample. The combination keeps the first component, shrinks the remaining covariance toward its diagonal, and adds the component back once. [Ledoit and Wolf](https://www.ledoit.net/Well-conditioned2004.pdf)

## How the risk estimate changes the portfolio

I replayed the same Ridge forecasts on three schedules. Each trades every three weeks, offset by one week from the next. Each simulation starts with $5 million. Trades are sized from shares actually held, can fill at the following close and are subject to a liquidity limit. Both optimizers use the same 2.5 basis point trade penalty. Fees on filled long and short trades were 7.5 and 10 basis points through 2010, then 5 and 7.5. Returns exclude borrow, financing and additional market impact.

Prices begin in 1995. After allowing for estimation history and common portfolio availability, the development comparison covers 5,773 trading days from 26 January 1999 through 31 December 2021. The later comparison covers 1,103 days from 3 January 2022 through 27 May 2026. I had already seen some of the later history in related research, so it is a historical check on the choices made here.

The fourth sizing rule, **factor target**, changes one input to stock shrinkage. I keep the 21-session stock volatilities, the 1.18 multiplier and half the historical stock correlation. For the other half I use the *total stock correlation* implied by the sectors, styles and shrunk residuals. A pair of stocks can now retain a common exposure even if its direct sample correlation is imprecise.

<table class="research-table comparison-table compact-table">
  <caption>Net long/short portfolio outcomes. Each row averages statistics calculated separately for the three schedules. Return is compounded annually, volatility is annualized, drawdown is the largest peak-to-trough loss, and turnover counts purchases and sales in multiples of capital per year.</caption>
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
<p class="figure-caption">The chart compounds the mean daily net return across schedules. The table measures each schedule’s own experience, so its worst drawdown can differ from the chart. Select the later period to see how the paths diverged after 2021.</p>

The later return gap between the original factor model and stock shrinkage was **4.70 percentage points per year**. Turnover of 18.28× means that for every 100 dollars of capital, the factor portfolio traded 1,828 dollars of stock in an average year, adding purchases and sales. Stock shrinkage traded 1,876 dollars. Fees were almost identical at 1.12% and 1.15% of capital a year. The short positions explain more. Before fees, the factor shorts lost 4.01% of capital a year and the stock-shrinkage shorts lost 0.87%. About two-thirds of the gross arithmetic P&L gap came from that side of the book.

One way to reduce turnover is to act more slowly on changes in the stock forecast. I gave today’s Ridge score 75% weight and its previous score on the same rebalance schedule 25%. Over the full history this reduced the factor portfolio’s turnover by 24%. In development, annual fees fell from 1.98% to 1.51%, yet annual net return also fell from 7.95% to 7.81%. Some trades I avoided would have paid for themselves. In the later period, fees fell from 1.12% to 0.83% and net return rose from 2.72% to 3.29%. Saving fees was repeatable here. Improving returns was more dependent on the period.

Changing just the residual model moved later annual net return from 2.72% to **3.05%** with one principal component, **3.97%** with residual shrinkage, and **3.81%** with both. Across the entire history, preserving the first component on top of shrinkage changed net Sharpe by just **+0.002**. The paired 95% block interval ran from −0.017 to +0.021. The clustering result gave me a reason to model residual covariance. I follow those groups through the next year and test one and five components in [Residual Risk After Sectors and Styles]({% link _posts/2026-11-20-residual-risk.md %}).

## A wider entry pool changed both holdings and turnover

I repeated the full Ridge backtest with 100 and 150 entry candidates per side. At 150 the optimizer can buy from the highest 150 scores and short from the lowest 150. It can still retain an existing position through rank 175 on its side. Moving from 75 to 150 gives it more stocks to choose from, including weaker-ranked ones, and reduces the distance between the entry and exit ranks from 100 places to 25. Volatility scaling has no such retention rule.

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

The wider pool led to different trades. In the later period, moving from 75 to 150 raised factor-target turnover from **16.66× to 25.11× capital** per year and fees from **1.01% to 1.52%**. Under volatility scaling, annual turnover fell from **24.36× to 19.96×** as capital spread across more names. All four rules earned less net at 150 than at 75 in that period.

The number of candidates also overstates the diversification the optimizers used. At 150 per side the later stock-shrinkage book held **175 distinct stocks** on average and the factor target held **123**. I divided each stock’s absolute dollars by total gross and took the reciprocal of the sum of those squared shares. On that basis their concentrations were equivalent to **107 and 71 equally sized positions**, respectively. Volatility scaling held about 300 names with an effective count of 243.

One result was consistent across sizes. At 75, 100 and 150 per side, later factor-target volatility was **2.38, 2.42 and 2.36 percentage points lower** than stock shrinkage. All three paired 95% intervals excluded zero in both periods after accounting for the three breadths. At 150 per side the later interval was 2.05 to 2.68 points lower. The factor target also carried less gross, 1.53 times capital against 1.80. Its later net Sharpe was 0.18 lower at that breadth, with an interval from 0.57 lower to 0.21 higher. I see evidence for lower delivered risk across these choices. The differences in Sharpe are much less precisely measured. [All 24 comparisons, including turnover, fees, drawdown, beta and market correlation](/assets/factor-risk-sizing/entry-breadth.csv)

## Comparing the hedges on the same stocks

Before choosing a sizing rule, I wanted to know whether the factor models could actually identify better hedges. The Ridge P&L comparison alone cannot tell me. A model can recognize that two stocks offset one another and still give less weight to a short position that subsequently earns money. Chapter 6 of Giuseppe Paleologo’s *The Elements of Quantitative Investing* distinguishes testing a covariance forecast on a given portfolio from testing the portfolios it helps construct. [Paleologo, chapter 6](https://www.wiley.com/en-us/The%2BElements%2Bof%2BQuantitative%2BInvesting-p-9781394265466)

I first gave each optimizer the same stocks and the same required exposure to the Ridge score. At each weekly decision I drew three sets of 150 eligible stocks and used nested samples of 75 and 100 from each. The spread held 50% long and 50% short. Every selected stock received between one-quarter and three times its equal-weight allocation on its side, subject to the position cap. I chose weights at the decision close, allowed fills at the next close and measured the following session’s gross return. The figure compares the volatility of those one-session outcomes across **1,196 development decisions and 230 later decisions**.

Bloomberg’s Jose Menchero and Anthony Lazanas make a useful point about this exercise. If two portfolios carry the same exposure to a return forecast, I can judge which risk model found the quieter way to hold that exposure. I do not need to wait for the forecast itself to earn a high enough return to distinguish the portfolios. A minimum-variance test makes that comparison particularly direct. Its ability to distinguish models still depends on the positions the constraints allow them to take. A rule that forces identical weights gives every model identical realized volatility. [Menchero and Lazanas, *Evaluating and Comparing Risk Model Performance*](https://doi.org/10.3905/jpm.2023.1.565)

Paleologo’s minimum-variance example helped me see why I also need a calibration test. Suppose the only constraint is one unit of exposure to a vector $$b$$. Setting every entry of $$b$$ to one gives a fully invested portfolio. Minimizing forecast variance gives

$$
w = \frac{\widehat{\Sigma}^{-1} b}{b^\top \widehat{\Sigma}^{-1} b}.
$$

Double every entry of the covariance estimate and the weights stay exactly the same. The common scale cancels between numerator and denominator. A risk model could therefore pick excellent hedges and still forecast the wrong level of volatility for every one of them. In the traded Ridge portfolio a 7% risk limit changes the answer. Multiplying the forecast volatility by 1.2 can make the optimizer buy and short fewer shares. The hedge test assesses relative risks. The risk-budget replay also assesses their absolute level. [Paleologo, *The Elements of Quantitative Investing*, chapter 6](https://www.wiley.com/en-us/The%2BElements%2Bof%2BQuantitative%2BInvesting-p-9781394265466)

<table class="research-table comparison-table compact-table">
  <caption>Annualized realized volatility of the matched long/short spreads. Breadth counts the stocks across both sides together. Each row uses the same stocks and dates for all four models.</caption>
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

Read down the first numeric column. In the later period, doubling the stock count from 75 to 150 reduced stock shrinkage’s volatility from 4.90% to 3.84%. Now read *across* the 150-stock row. Letting the factor model shrink residual correlations reduced the same spread to 3.48%. Those are different gains. The first gave the optimizer more stocks to choose weights across. The second changed how it weighted exactly the same stocks. At 100 stocks the same comparison was 4.42% against 4.04%. The figure shows how precisely the differences were estimated.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/hedges" mobile="/assets/factor-risk-sizing/hedges_mobile" version="1" alt="Changes in long/short hedge volatility at 75, 100 and 150 stocks. The factor target reduced realized volatility at each size in both periods. Residual shrinkage reduced later volatility by about 0.36 to 0.39 percentage points." %}
</div>
<p class="figure-caption">Each point compares a model with stock shrinkage. A value of −0.3 means annualized volatility was 0.3 percentage points lower. The bars are 95% intervals from resampling 13-week blocks, accounting for the three sizes within each model comparison. Zero means the observed volatilities were equal.</p>

The residual-shrinkage advantage over stock shrinkage was distinguishable from zero at all three later sizes. For the original factor model, the intervals included zero at all three. These spreads had one dollar of gross exposure per dollar of capital. The Ridge trading portfolios above could use up to two. With residual shrinkage the 150 positions had the concentration of about 79 equal weights. That distinction also mattered for a long-only minimum-variance test. When all 150 stocks were represented, original factors reduced later volatility from 13.50% to 12.83%. When the optimizer could leave stocks out, effective breadth fell to 13–17 names and the difference was too uncertain to choose a model.

I also tried the reverse experiment. I kept stock shrinkage’s **actual filled positions** and asked each model to forecast their daily risk through the next rebalance. Over 227 complete later cycles, stock shrinkage forecast **7.00%**, the factor target forecast **9.95%**, and the positions realized **9.64%** annualized gross daily risk. On the original factor portfolio the target instead forecast 10.57% against 8.28% realized.

Stock shrinkage already uses a 1.18 multiplier. Could a backward-looking calibration on the portfolio itself close the remaining gap? Each week I took the ratio of realized to predicted variance from each of the last 52 completed cycles and averaged those ratios. I multiplied the current variance by that number, separately for each risk model and each portfolio. On the same incumbent positions the forecasts became **9.73% for stock shrinkage and 9.72% for the factor target**, against **9.64% realized**. Scoring each dated variance forecast with QLIKE, which rewards getting both the level and timing right, slightly favored calibrated stock shrinkage. The factor target’s large advantage on this particular book came mainly from its risk level. The hedge test still gives a reason to keep its information about relative stock movements.

## Smaller losses came with a return cost

How much market exposure did the sizing rules actually leave me with? I measured beta as the slope of daily net portfolio returns on Russell 1000 returns. A beta of 0.08 means that a 1% market move was associated with about a 0.08% portfolio move. Correlation measures how closely the two return series moved together, stripping out their different volatilities. On the same return series, beta equals correlation times portfolio volatility divided by market volatility. Both numbers can be small even when a portfolio has substantial exposure to a particular industry or theme.

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

The original factor book had close to zero later market correlation, yet its worst drawdown was 10.54%. What else was it exposed to? I took the same sector-and-style model and used it to describe both sets of actual positions. On average, momentum accounted for about 36% of forecast variance on the stock-shrinkage book and 15% on the original factor book. Short interest accounted for about 18% and 12%. These are shares of forecast variance, including each exposure’s covariance with the rest of the book. They explain how a portfolio can carry quite different bets at near-zero market beta. The returns those bets subsequently earned are a separate measurement.

Using the factor model as a shrinkage target recovered about **40% of the later return gap**. It also changed the experience of holding the portfolio. In the worst 5% of later trading days it lost an average of **1.02%** per day, against **1.35%** for stock shrinkage. Its maximum drawdown was shallower, although its longest spell below a previous peak lasted **190 sessions**, against **140**. A shallower drawdown can still take longer to recover if the gains that follow it are smaller.

Some of that protection came from taking less risk. I also reran stock shrinkage with the earlier article’s 1.55 multiplier. It delivered **7.47%** later volatility, close to the factor target’s **7.27%**, and earned **6.19%** net annually versus **4.59%**. But a fixed multiplier asks me to choose the scale upfront. I wanted to know what would happen if every optimizer could learn its own scale from earlier forecast errors.

## Trading with a calibrated risk budget

The 7% budget applies to the risk forecast when I choose the weights. To see the risk a holder actually experienced, I measured the standard deviation of the preceding 252 daily net returns on each schedule, annualized it, and averaged the three readings. Across 317 monthly observations the median for stock shrinkage was **8.58%**. Its highest reading was **14.81%** in the year ending February 2021. For the factor target the corresponding values were **7.21%** and **11.81%**. A risk level measured over that particular year answers a different question from the 8.74% stock-shrinkage volatility over the full development period.

<div class="research-figure responsive-figure">
  {% include blog-chart.html chart="realized-risk" source="/assets/factor-risk-sizing/realized-risk.json?v=2" base="/assets/factor-risk-sizing/realized-risk" mobile="/assets/factor-risk-sizing/realized-risk_mobile" version="1" label="Annualized net volatility of the preceding 252 trading sessions, measured at monthly endpoints, with the 7% optimizer forecast budget as a reference." %}
</div>
<p class="figure-caption">Each point uses a full trading year of daily returns. The series end on the last available session of each month. The horizontal line shows the forecast budget of the joint optimizers.</p>

I kept a reference portfolio for each of the three covariance models. At every decision I looked at its last 52 completed rebalance cycles. For each cycle I divided the mean squared daily gross return by the variance forecast for its filled positions. The square root of the average ratio is a volatility multiplier. If realized variance was consistently about 1.44 times the forecast, for instance, I would multiply the next volatility forecast by 1.20. These 52 observations arrive roughly weekly because the three trading schedules are staggered. Their three-week holding periods overlap.

I then replayed each optimizer with its own multiplier inside the 7% risk constraint. The stock model kept its original 1.18 adjustment underneath this additional scale. The reference portfolios continued under their original rules, giving me past errors to learn from even as the new simulations began taking different positions. Each simulation still paid fees on its own fills and measured its next trade from its own holdings.

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

Stock shrinkage and the factor target ended up taking almost the same later risk. Both carried about 1.19 dollars of gross positions per dollar of capital. Stock shrinkage earned 6.10% net against 4.48% for the factor target, and paid 0.85% a year in fees against 0.97%. The additional fee burden explains only a small part of the gap. The point estimate favors stock shrinkage, although the paired 95% interval for the factor target’s Sharpe difference spans −0.55 to +0.20. For me the clearest benefit of calibration was getting all three portfolios close to the intended risk. They did that by putting less capital to work, and all three earned lower net returns in both periods.

I would keep stock shrinkage as the reference for this Ridge portfolio and retain the factor target as a candidate. Its full-history Sharpe gain over the original factor model was 0.28, with a one-sided 95% lower bound of 0.03 after accounting for thirteen recorded comparisons and resampling common 63-session blocks. For the later period alone that lower bound was −0.25. The factor model helped find quieter hedges at every breadth I tested. At comparable risk and gross exposure, the stock-shrinkage optimizer still made better use of the Ridge scores in the later sample. I would want a change to the factor model to improve that last comparison before switching how I size the portfolio.
