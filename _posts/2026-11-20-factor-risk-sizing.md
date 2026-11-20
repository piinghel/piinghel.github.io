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

Imagine I am $100 long NVIDIA and $100 short Workday. My sector report shows zero net dollars in technology. Now suppose a cloud provider postpones its next AI data center. NVIDIA could sell fewer chips. That same delay might barely affect subscriptions to Workday’s human-resources software. If NVIDIA falls 10% and Workday stays flat, I lose $10. What looked like a hedge in my sector report still leaves me exposed to data-center spending.
{: .mathjax-ignore}

Which other stock might share that exposure? In October 2024, Vertiv and NVIDIA published a design for powering and cooling data centers that use NVIDIA’s chips. Vertiv sits in Industrials. If I hold both stocks, my sector report shows two different sectors. Both positions could still lose if customers postpone building AI data centers. Workday had a business link too. In 2022 it described how NVIDIA used its HR software to manage recruiting. What matters for the trade is *how* the companies are connected and which cash flows a particular shock could change. [Vertiv’s announcement](https://www.vertiv.com/en-emea/about/news-and-events/news-releases/vertiv-codevelops-with-nvidia-complete-power-and-cooling-blueprint-for--nvidia-gb200-nvl72-platform/) · [Workday’s NVIDIA customer study](https://forms.workday.com/content/dam/web/en-us/documents/ebooks/power-of-skills-insights-customer-success-story-global-enus.pdf)

A common shock can also push companies in opposite directions. Take a war that interrupts oil supplies. Higher crude prices could lift an oil producer and squeeze an airline. A portfolio long the producer and short the airline could gain on both legs. If oil prices fell back, both positions could lose. To understand the risk I need to know what each company depends on and which side of the trade I hold.

I can look for those missing exposures in **residual returns**, the part of each stock’s return left after accounting for the market, sectors and styles. I group stocks using a year of residuals, freeze the groups, and see whether the same stocks still move together the following year. A group can tell me which stocks moved together. It takes business evidence to say that AI spending linked them. And if a risk is new, a year of returns may have little to say about it. I can still ask what a pause in data-center orders or a jump in fuel prices would do to my actual longs and shorts.

In [From Volatility Scaling to Joint Sizing]({% link _posts/2026-08-29-joint-sizing.md %}), I sized positions using historical stock correlations shrunk halfway toward zero. Here I keep the Ridge stock forecasts fixed. Does a risk model that knows about sectors, styles and residual co-movement choose better hedges, and what do those choices earn after fees?

## What goes into a position

I start with the historical Russell 1000 membership. On each date I use the most recent constituent list recorded by that close. Ridge is trained to predict how a stock’s forward return per unit of risk ranks within its sector. At a rebalance I rank the eligible stocks by that prediction and start with the 75 highest scores as possible longs and the 75 lowest as possible shorts. These are **75 candidates per side**. The simple benchmark starts with equal weights on each side and scales each stock by 20% divided by its own annualized volatility over 60 sessions, with a 5% floor on that volatility. A more volatile stock gets a smaller weight. This rule can allocate up to a dollar per side for each dollar of capital.

The joint optimizer needs a reason to prefer one position over another. I take the raw Ridge score for a stock and multiply it by that stock’s trailing 21-session daily volatility. All the joint optimizers use this same return-like sizing score. A change in the factor risk estimate changes how much risk a position consumes while leaving its score in the objective alone. Once a portfolio exists, moving one dollar away from the holdings already filled also incurs a 2.5-basis-point penalty in the optimizer. The backtest separately charges the applicable historical fee on each filled trade.

The joint optimizer sees all the positions together. It can retain existing holdings while their ranks remain within the top or bottom 175. A 7% annual portfolio risk budget, a 4% cap per name, a gross exposure limit of twice capital, net exposure within ±25% and estimated market beta within ±0.05 constrain the weights. Each sector has a net limit of ±20% of capital and may account for up to 30% of either sleeve. A 7% *forecast* at the decision close can still lead to 9% *realized* volatility over subsequent sessions. The first number is a model input to sizing. The second comes from the daily returns of the positions that actually filled.

I use two starting estimates for joint sizing. **Stock shrinkage** measures volatility over 21 sessions and correlation over 756. It keeps half of each measured pairwise correlation and multiplies the resulting portfolio volatility forecast by 1.18. Halving a positive correlation reduces estimated risk for two longs and increases it for an offsetting pair. The multiplier adjusts the overall level separately.

**Sector and style factors** explain each day’s stock returns with the market, broad sectors and seven styles. The styles are momentum, short-term return, beta, residual volatility, size, liquidity and short interest. I use exposures available at the preceding close, weight the squared regression errors by the square root of prior market capitalization, and estimate factor covariance and specific variance with a 63-session half-life.

There are two regressions here. First, I look back along each stock’s own history to estimate how it responds to the market. I use up to 252 sessions, requiring at least 126 stock and market return pairs. Then I look *across* stocks on a single day. A group of stocks with high momentum scores might gain more than otherwise similar stocks that day. The cross-sectional regression estimates that day’s momentum factor return while accounting for their other exposures. Subtract each stock’s fitted return from its observed return and I have one residual per stock. Repeating that calculation gives me the history on which I can look for a hidden theme.

For momentum I average two standardized descriptors. The first is the past year’s return skipping the most recent month. The second is the fraction of sessions over the past year when the stock closed above or at its 200-session moving average. A return and a fraction of days have different units. At each close I clip extreme readings, center each descriptor on its market-cap-weighted mean and divide by its cross-sectional standard deviation, giving each stock equal weight in that last calculation. I average the two scores and standardize the blend again. This gives each ingredient an equal say in the momentum exposure.

Short-term return gets its own exposure using the last 21 sessions. The first regression supplies two more descriptors, the stock’s beta shrunk toward one and the log root-mean-square size of its market-regression residuals. That last number lets the daily cross-section distinguish stocks that historically moved more on their own. The *specific variance* in the risk forecast below comes from the second regression, after accounting for all seven styles and the sectors. A stock can score high on the residual-volatility style and still share a shock with its peers.

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

At each of 27 year-ends I grouped stocks using their trailing residual correlations, froze the eleven groups, and measured the next 252 sessions. Within-group correlation exceeded between-group correlation by **4.74 percentage points** when forming the groups and **2.06 points** the following year, giving each year equal weight. I then shuffled group labels within each industry and sector. Those groups kept exactly the same industry composition and showed a forward difference of just **0.35 points** on average. That leaves **1.71 points** associated with the original grouping. Consider what that permits me to say about the chip designer and the cooling supplier. When I compared only pairs from different sectors and matched their industry mix, sharing a cluster still raised next-year residual correlation by 0.67 percentage points in development. Within a sector the corresponding gap was much larger, 7.78 points. To identify an AI exposure in a specific group, I would still need independent evidence, such as both firms’ dependence on data-center orders, known when the positions were chosen.

I tried three ways of letting residuals move together. The first principal component keeps one shared direction and assigns the remaining variance to each stock. Ledoit–Wolf shrinkage keeps a fraction of **all** estimated residual correlations, with the fraction estimated from the trailing sample. The combination keeps the first component, shrinks the remaining covariance toward its diagonal, and adds the component back once. [Ledoit and Wolf](https://www.ledoit.net/Well-conditioned2004.pdf)

## How the risk estimate changes the portfolio

I replayed the same Ridge forecasts on three schedules. Each trades every three weeks, offset by one week from the next. Each simulation sizes trades against a fixed $5 million. I divide each day’s filled-position P&L after fees by that amount. Compounding those daily returns gives the growth index shown below. Trades are sized from shares actually held, can fill at the following close and are subject to a liquidity limit. Both optimizers use the same 2.5 basis point trade penalty. Fees on filled long and short trades were 7.5 and 10 basis points through 2010, then 5 and 7.5. Returns exclude borrow, financing and additional market impact. When a stock stopped quoting, the simulation could close it at its last recorded price. These exits accounted for 0.49% of traded dollars across the tested books. Their actual sale or buyback prices are unknown.

Prices begin in 1995. After allowing for estimation history and common portfolio availability, the development comparison covers 5,773 trading days from 26 January 1999 through 31 December 2021. The later comparison covers 1,103 days from 3 January 2022 through 27 May 2026. I had already seen some of the later history in related research, so it is a historical check on the choices made here.

The fourth sizing rule, **factor target**, changes one input to stock shrinkage. I keep the 21-session stock volatilities, the 1.18 multiplier and half the historical stock correlation. For the other half I use the *total stock correlation* implied by the sectors, styles and shrunk residuals. A pair of stocks can now retain a common exposure even if its direct sample correlation is imprecise.

These are long/short portfolios with room for a long bias. In the later period stock shrinkage held about **91 cents long and 65 cents short per dollar of capital** on an average day. The factor target held about **74 cents long and 50 cents short**. The optimizer limits net investment at the decision close. Subsequent stock moves can carry the marked holdings away from that limit before the next trade.

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
<p class="figure-caption">The chart compounds the mean daily net return across schedules. The table measures each schedule’s own experience, so its worst drawdown can differ from the chart. Select the later period to see how the paths diverged after 2021.</p>

The later return gap between the original factor model and stock shrinkage was **4.70 percentage points per year**. Turnover of 18.28× means that for every 100 dollars of capital, the factor portfolio traded 1,828 dollars of stock in an average year, adding purchases and sales. Stock shrinkage traded 1,876 dollars. Fees were almost identical at 1.12% and 1.15% of capital a year. The short positions explain more. Before fees, the factor shorts lost 4.01% of capital a year and the stock-shrinkage shorts lost 0.87%. About two-thirds of the gross arithmetic P&L gap came from that side of the book.

One way to reduce turnover is to act more slowly on changes in the stock forecast. I gave today’s Ridge score 75% weight and its previous score on the same rebalance schedule 25%. Over the full history this reduced the factor portfolio’s turnover by 24%. In development, annual fees fell from 1.98% to 1.51%, yet annual net return also fell from 7.95% to 7.81%. Some trades I avoided would have paid for themselves. In the later period, fees fell from 1.12% to 0.83% and net return rose from 2.72% to 3.29%. Saving fees was repeatable here. Improving returns was more dependent on the period.

Changing just the residual model moved later annual net return from 2.72% to **3.05%** with one principal component, **3.97%** with residual shrinkage, and **3.81%** with both. Across the entire history, preserving the first component on top of shrinkage changed net Sharpe by just **+0.002**. The paired 95% block interval ran from −0.017 to +0.021. The clustering result gave me a reason to model residual covariance. I follow those groups through the next year and test one and five components in [Residual Risk After Sectors and Styles]({% link _posts/2026-11-20-residual-risk.md %}).

How often did a bad day take the model by surprise? I defined a bad day as a gross return below a threshold the model expected to breach once in twenty sessions. After each fill, I took its volatility forecast on the actual shares and multiplied it by the fifth percentile of the last three years of returns per unit of forecast risk. In the later period on the stock-shrinkage holdings, the factor target put the average threshold at a loss of **0.97%**, compared with **1.00%** under stock shrinkage. Actual losses crossed those thresholds on **5.71% and 5.28%** of observations. A score that counts both the frequency and the size of misses favored stock shrinkage there. It had favored the factor target in development. On the factor target’s own later holdings, both forecasts were breached on 5.07% of observations. The portfolio matters even when the question is as simple as the chance of a bad day.

## A wider entry pool changed both holdings and turnover

I repeated the full Ridge backtest with 100 and 150 entry candidates per side. At 150 the optimizer can buy from the highest 150 scores and short from the lowest 150. For existing holdings the optimizer uses a wider pool, the union of the top 175 and bottom 175 scores. A stock in that pool can carry over on its held side, even if its score has crossed to the other end of the ranking. Moving from 75 to 150 gives it more stocks to choose from, including weaker-ranked ones, and reduces the distance between the entry and exit ranks from 100 places to 25. Volatility scaling has no such retention rule.

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

I could separate the effect of the narrower holding band from the effect of admitting more stocks. I kept the 150 entry candidates per side and let an existing position stay eligible through rank 250. In 2022–May 2026, stock shrinkage traded **20.80 times capital a year**, down from 25.31. The factor target traded **21.95 times**, down from 25.11. Allowing a stock that slipped a few places to stay saved 0.26 and 0.18 percentage points of capital in annual fees, respectively. Trading fell in 1999–2021 as well.

Did those savings improve returns? Later net compounded return rose from 6.69% to 7.60% for stock shrinkage and from 3.75% to 4.23% for the factor target. Realized volatility stayed near 9.8% and 7.5%, respectively. The paired return intervals included zero in both periods. I would widen the band to cut trading. I would still use the original 75-entry portfolio as the reference for comparing risk models.

The number of candidates also overstates the diversification the optimizers used. At 150 per side the later stock-shrinkage book held **175 distinct stocks** on average and the factor target held **123**. I divided each stock’s absolute dollars by total gross and took the reciprocal of the sum of those squared shares. On that basis their concentrations were equivalent to **107 and 71 equally sized positions**, respectively. Volatility scaling held about 300 names with an effective count of 243.

One result was consistent across sizes. At 75, 100 and 150 per side, later factor-target volatility was **2.38, 2.42 and 2.36 percentage points lower** than stock shrinkage. All three paired 95% intervals excluded zero in both periods after accounting for the three breadths. At 150 per side the later interval was 2.05 to 2.68 points lower. The factor target also carried less gross, 1.53 times capital against 1.80. Its later net Sharpe was 0.18 lower at that breadth, with an interval from 0.57 lower to 0.21 higher. I see evidence for lower delivered risk across these choices. The differences in Sharpe are much less precisely measured. [All 24 comparisons, including turnover, fees, drawdown, beta and market correlation](/assets/factor-risk-sizing/entry-breadth.csv)

## Comparing the hedges on the same stocks

Before choosing a sizing rule, I wanted to know whether the factor models could actually identify better hedges. The Ridge P&L comparison alone cannot tell me. A model can recognize that two stocks offset one another and still give less weight to a short position that subsequently earns money. In the published edition of *The Elements of Quantitative Investing*, Giuseppe Paleologo’s chapter 5, “Evaluating Risk,” distinguishes testing a covariance forecast on a given portfolio from testing the portfolios it helps construct. [Paleologo, chapter 5](https://www.wiley.com/en-us/shop/general-finance-investments/the-elements-of-quantitative-investing-p-9781394265466)

I first gave each optimizer the same stocks and the same required exposure to the Ridge score. At each weekly decision I drew three sets of 150 eligible stocks and used nested samples of 75 and 100 from each. The spread held 50% long and 50% short. Every selected stock received between one-quarter and three times its equal-weight allocation on its side, subject to the position cap. I chose weights at the decision close, allowed fills at the next close and measured the following session’s gross return. I compare the volatility of those one-session outcomes across **1,196 development decisions and 230 later decisions**.

Bloomberg’s Jose Menchero and Anthony Lazanas make a useful point about this exercise. If two portfolios carry the same exposure to a return forecast, I can judge which risk model found the quieter way to hold that exposure. I do not need to wait for the forecast itself to earn a high enough return to distinguish the portfolios. A minimum-variance test makes that comparison particularly direct. Its ability to distinguish models still depends on the positions the constraints allow them to take. A rule that forces identical weights gives every model identical realized volatility. [Menchero and Lazanas, *Evaluating and Comparing Risk Model Performance*](https://doi.org/10.3905/jpm.2023.1.565)

Paleologo’s minimum-variance example helped me see why I also need a calibration test. Suppose the only constraint is one unit of exposure to a vector $$b$$. Setting every entry of $$b$$ to one gives a fully invested portfolio. Minimizing forecast variance gives

$$
w = \frac{\widehat{\Sigma}^{-1} b}{b^\top \widehat{\Sigma}^{-1} b}.
$$

Double every entry of the covariance estimate and the weights stay exactly the same. The common scale cancels between numerator and denominator. A risk model could therefore pick excellent hedges and still forecast the wrong level of volatility for every one of them. In the traded Ridge portfolio a 7% risk limit changes the answer. Multiplying the forecast volatility by 1.2 can make the optimizer buy and short fewer shares. The hedge test assesses relative risks. The risk-budget replay also assesses their absolute level. [Paleologo, *The Elements of Quantitative Investing*, chapter 5](https://www.wiley.com/en-us/shop/general-finance-investments/the-elements-of-quantitative-investing-p-9781394265466)

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

Read down the stock-shrinkage column. In the later period, increasing the stock count from 75 to 150 lowered volatility from 4.90% to 3.84%. Now read *across* the 150-stock row, where every model sees exactly the same stocks. The factor model gave **3.68% with diagonal residuals and 3.48% with shrunk residual correlations**. That 0.20-point difference isolates what estimating the residual correlations added. The 3.84% stock-shrinkage result also differs in how it estimates the rest of the covariance matrix.

Did those three selections happen to contain unusually good hedges? I repeated the test with **32 fresh stock selections at each weekly decision**. Each model saw the same names. I kept the original 1,426 dates, so the extra draws tell me how much the result depends on the names I picked. They give me no extra recessions or market rallies. [Intervals for the original three selections](/assets/factor-risk-sizing/hedges.svg)

In the later period, allowing residual correlations reduced annualized volatility by **0.11, 0.13 and 0.16 percentage points** at 75, 100 and 150 stocks, respectively, compared with the otherwise identical factor model. At 150 stocks the average went from **3.69% to 3.53%**. Every one of the 32 stock paths gave the same direction, although the original three had suggested a larger gain of 0.20 points. In development the reductions were smaller at 0.03, 0.05 and 0.07 points. Comparing with stock shrinkage gives a larger difference because that comparison also changes the named-factor part of the estimate.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/stock-draws" mobile="/assets/factor-risk-sizing/stock-draws_mobile" version="1" alt="32 fresh stock selections at each decision. Shrinking residual correlations reduces annualized spread volatility relative to stock shrinkage and to the factor model with zero residual correlations, at 75, 100 and 150 stocks in both periods." %}
</div>
<p class="figure-caption">A point to the left of zero means the spread with shrunk residual correlations was quieter. The right panel isolates the contribution of the residuals. The bars are 95% intervals that account for all six comparisons within a period, resampling both stock paths and common 13-week blocks. At 150 names the estimated later reduction relative to zero residual correlations ranges from 0.07 to 0.25 percentage points. <a href="/assets/factor-risk-sizing/stock-draws.csv">Download levels, differences and intervals.</a></p>

Did the quieter spread simply take a smaller market position? In the later 150-stock test, average realized beta was **−0.053 with diagonal residuals and −0.052 with shrunk residual correlations**. For each stock selection I split the spread’s variance into the part explained by its fitted Russell 1000 beta and the part left over. The change in the market component accounted for about **2.5% of the reduction in variance**. Most of the gain survived this adjustment. A single beta estimated over the period leaves room for exposures that changed week to week.

These test spreads started with one dollar of gross exposure per dollar of capital. The traded Ridge portfolios could use up to two. The weight limits also mattered. In the initial 150-stock test, the residual-shrinkage spread had the concentration of about 79 equal weights. In a fully invested long-only test, requiring every one of the 150 names to receive a weight let the original factor model reduce later volatility from 13.50% to 12.83% relative to stock shrinkage. When the optimizer could leave stocks out, concentration rose to the equivalent of just 13–17 equal weights and the difference was too uncertain to choose a model.

A Ridge holding can stay in the book for three weeks. Would a hedge that looked good for one session still help if I left the shares alone? I took the first eight of the same 32 stock selections at each date, assumed a full fill wherever the next close had a valid quote, and held those shares for 15 exchange sessions. Unfilled allocations stayed in cash. For a missing terminal quote I used its last available close. I compared the first day and the full holding period on exactly the same 1,193 earlier and 227 later weekly decisions. For the 15-session result, I measured how much the total gain or loss varied across starting dates, then annualized that standard deviation by multiplying by $$\sqrt{252/15}$$. These are gross hedge returns.

<table class="research-table comparison-table compact-table">
  <caption>Annualized volatility saved by estimating residual correlations, 2022–May 2026. Values are percentage points relative to the same factor model with zero residual correlations. A larger positive number means a quieter spread.</caption>
  <thead><tr><th>Total stocks</th><th>1 session</th><th>15 sessions</th></tr></thead>
  <tbody>
    <tr><th>75</th><td>0.12</td><td>0.08</td></tr>
    <tr><th>100</th><td>0.15</td><td>0.07</td></tr>
    <tr><th>150</th><td>0.16</td><td>0.13</td></tr>
  </tbody>
</table>

In the later 150-stock spreads, allowing residual correlations reduced 15-session annualized volatility from **3.35% to 3.22%**. The estimated reduction was **0.13 percentage points**, with a simultaneous 95% interval from **0.04 to 0.21 points**. At 75 and 100 stocks the average reduction was positive and the intervals included zero. All three reductions were distinguishable from zero in development. The wider later uncertainty also mattered against the incumbent stock-shrinkage model. The residual model’s 15-session spreads were quieter on average at every size, but all three intervals against the incumbent included zero. The weekly starting dates share holding days, so I resampled common blocks of 13 weeks as well as the eight stock paths. [Download both periods, both reference models and the paired intervals (CSV)]({{ '/assets/factor-risk-sizing/hedge-holding-horizons.csv' | relative_url }})

For me, the narrower conclusion is the one these tests answer well. The factor model with shrunk residual correlations found a quieter way to hold the same Ridge score exposure. Whether I earn more from those hedges also depends on how the positions perform over the holding period and what I pay to change them.

I also tried the reverse experiment. I kept stock shrinkage’s **actual filled positions** and asked each model to forecast their daily risk through the next rebalance. Over 227 complete later cycles, stock shrinkage forecast **7.00%**, the factor target forecast **9.95%**, and the positions realized **9.64%** annualized gross daily risk. On the original factor portfolio the target instead forecast 10.57% against 8.28% realized.

Stock shrinkage already uses a 1.18 multiplier. Could a backward-looking calibration on the portfolio itself close the remaining gap? Each week I took the ratio of realized to predicted variance from each of the last 52 completed cycles and averaged those ratios. I multiplied the current variance by that number, separately for each risk model and each portfolio. On the same incumbent positions the forecasts became **9.73% for stock shrinkage and 9.72% for the factor target**, against **9.64% realized**. Two models can both average close to 9.64% and disagree about which weeks are risky. I score each forecast variance $$v$$ against the subsequent mean squared daily return $$u$$ with $$\log v + u/v$$, then average across matched cycles. The logarithm penalizes a model for always quoting a huge variance. The ratio penalizes it for quoting a small one before large moves. A lower average loss, called QLIKE, slightly favored calibrated stock shrinkage. The factor target’s large advantage on this particular book came mainly from its risk level. The hedge test still gives a reason to keep its information about relative stock movements.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/fixed-book" mobile="/assets/factor-risk-sizing/fixed-book_mobile" version="1" alt="Same stock-shrinkage holdings. Over the later cycles, the stock model's forecast moves from 7.00% to 9.73% after calibration and the factor target moves from 9.95% to 9.72%. Realized gross volatility was 9.64%." %}
</div>
<p class="figure-caption">Both rows price the actual stock-shrinkage holdings. The dashed line is what those shares subsequently realized. Moving from the open circle to the diamond changes the forecast using the last 52 completed cycles. The shares and their P&amp;L stay fixed. The earlier comparison begins in 2000, after the calibration history becomes available. <a href="/assets/factor-risk-sizing/fixed-book-forecasts.csv">Download both forecasts for all three portfolios.</a></p>

How quickly should the named factors forget an old shock? With a 63-session half-life, a factor return 63 trading days ago gets half the weight of the most recent one. I tried 21 and 126 sessions on the original factor book’s unchanged holdings, holding specific risk and stock exposures fixed. The 21-session estimate had a lower average variance loss than 63 over 1999–2021, though the paired interval included zero. It had a higher loss over the 227 completed later cycles. The 126-session estimate gave the reverse ordering. Choosing a memory from whichever period I had just looked at would have led me to opposite decisions. I kept 63 sessions for sizing.

Those forecasts describe the daily swings along the way. What if I only care where the book finishes at the next rebalance? Two daily moves of +1% and −1% on fixed capital cancel in the final P&L, even though both counted toward daily risk. On the later stock-shrinkage holdings, the typical size of the whole-cycle move was 0.99 times what the sum of daily squared moves implied. The 95% interval ran from 0.86 to 1.11. On the factor-target holdings the ratio was 1.01 (0.90 to 1.11). Across these three-week holdings the daily approximation was close on average.

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

How could stock shrinkage have a realized beta of 0.082 when I capped beta at 0.05? Every target portfolio met the cap using the stock betas known at the decision close. Once the orders filled, market prices had moved. In the later period, 51 of 230 stock-shrinkage entries landed outside the band. Among those 51, the median overshoot was just 0.005 in beta units.

The larger difference in development came from how the stocks actually moved. Per 1% move in the index, the portfolio’s fitted response was about **8.2 basis points**. The intended market exposure accounted for 0.7 bp, and fills and subsequent weight changes together accounted for 0.8 bp. The remaining 6.7 bp came from co-movement that the stock beta estimates did not anticipate. That term tells me how much the estimate missed. It cannot tell me which theme caused the miss.

The original factor book had close to zero later market correlation, yet its worst drawdown was 10.54%. What else was it exposed to? I took the same sector-and-style model and used it to describe both sets of actual positions. On average, momentum accounted for about 36% of forecast variance on the stock-shrinkage book and 15% on the original factor book. Short interest accounted for about 18% and 12%. These are shares of forecast variance, including each exposure’s covariance with the rest of the book. They explain how a portfolio can carry quite different bets at near-zero market beta. The returns those bets subsequently earned are a separate measurement.

Using the factor model as a shrinkage target recovered about **40% of the later return gap**. It also changed the experience of holding the portfolio. In the worst 5% of later trading days it lost an average of **1.02%** per day, against **1.35%** for stock shrinkage. Its maximum drawdown was shallower, although its longest spell below a previous peak averaged **190 sessions** across the three schedules, against **140** for stock shrinkage. A shallower drawdown can still take longer to recover if the gains that follow it are smaller.

Some of that protection came from taking less risk. I also reran stock shrinkage with the earlier article’s 1.55 multiplier. It delivered **7.47%** later volatility, close to the factor target’s **7.27%**, and earned **6.19%** net annually versus **4.59%**. That comparison suggested that the amount of risk assigned to the whole book deserved a test of its own.

## Why the same risk budget produced different volatility

Why did two optimizers with a 7% budget deliver 9.65% and 7.27% volatility? I could change how expensive risk looked to the optimizer while preserving every one of its estimated correlations. At each decision close, I asked both models to forecast variance on the stock-shrinkage portfolio’s actual holdings. If the factor target assigned twice the variance to those shares, for example, I multiplied every entry in the stock covariance matrix by two. Doubling variance multiplies forecast volatility by the square root of two. With the same positions scaled uniformly, about 71 cents of the old exposure would now use the old risk budget. I also ran the reverse experiment, dividing the factor-target matrix by two. That makes the two forecasts agree on the reference shares at that close. Each optimizer then chose its own trades from its own filled holdings.

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

Read down the last column in pairs. At the stock-shrinkage risk level, both portfolios realized about **9.7% volatility**. At the factor-target level, both realized about **7.3%**. Changing the risk level cut later volatility by **2.39 percentage points** on average across the two sets of stock relationships, with a paired 95% interval of **2.26 to 2.51 points**. Gross exposure fell by 35 cents per dollar of capital. At a common level, changing the relationships shifted later volatility by just **0.01 points** (interval **−0.20 to +0.24**). It still changed the trades. Using factor-target relationships added 2.47 times capital in annual turnover and earned 1.40 points less per year on average, with the return interval spanning **4.18 points less to 1.30 more**. For this portfolio I can explain the volatility gap much more confidently than I can rank the two models by return.

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

How consistent was the ranking through time? The calibrated factor target earned 2.02 percentage points more than calibrated stock shrinkage in 2023 and 5.91 points less in 2024. The year-by-year file gives all six portfolios’ net returns, drawdowns, market betas, correlations, gross exposures, fees and traded dollars. Returns and trading cover the observed sessions of each year, including the partial years at either end. Each year’s drawdown starts from fresh capital. [Download the calendar-year results, 1999–May 2026 (CSV)]({{ '/assets/factor-risk-sizing/yearly-outcomes.csv' | relative_url }})

The dates of the losses made the risks easier to understand. I took an equal daily mix of the two calibrated portfolios and found its deepest later drawdown. From the close on **December 28, 2022 to February 2, 2023**, stock shrinkage lost **7.64%** and the factor target lost **7.71%**. The Russell 1000 **rose 11.15%**. Their longs made money, but rising prices on their short positions cost **11.17 and 12.97 percentage points** of capital respectively before fees, adding daily P&L over the episode. Reverse the question and the dates change. During the Russell’s deepest later drawdown, January 3 to October 12, 2022, it fell **25.99%** while these portfolios gained **2.13% and 1.57%**. I chose both windows by the same peak-to-trough rule. A report focused only on falling equity markets would have missed the worst shared loss of the two books.

Where did the remaining difference come from? I compared the filled positions stock by stock on each trading day. In the later period, the factor target’s longs contributed **0.08 percentage points more** per year, its shorts contributed **1.52 points less**, and it paid **0.12 points more** in fees. Those add to a 1.56-point shortfall in annualized arithmetic return. Compounding the two portfolios separately gives the 1.62-point gap in the table. The two books both averaged about 47 cents short per dollar of capital. Yet on an average day their short exposures differed by three cents in absolute value. Giving the two short books the same stock return per dollar, the timing of that funding difference cost the factor target **0.90 points a year**. The difference in average funding cost just **0.02 points**. The remaining **roughly 0.6 points** came from which stocks were short and their relative weights. The interval for the arithmetic gap runs from 3.92 points worse to 1.00 better, so I treat the short side as an explanation of this sample.

The shorts also raise a cost question. The backtest includes dated trading fees, and the dataset has no stock-loan fee history. Keeping the calibrated fills fixed, I charged an illustrative **1% annual rate** on the prior close’s short market value, accruing calendar days over 360. That cost **0.48 percentage points of capital per year** in each later book. Suppose instead that each security could cost anywhere from zero to 1% on any date, with both portfolios paying the same rate to borrow the same stock. Even allocating every rate in the factor target’s favor would improve its later arithmetic return relative to stock shrinkage by only **0.13 points**. The observed gap was **1.56 points**. A real loan can cost more than 1%, its fee depends on the security and the collateral, and a stock can be unavailable to borrow. The calculation shows which assumptions would matter for these holdings. [How stock-loan costs are charged](https://investors.interactivebrokers.com/en/pricing/short-sale-cost.php)

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/short-funding" mobile="/assets/factor-risk-sizing/short-funding_mobile" version="1" alt="Short-sleeve return attribution. The factor target lost 0.90 percentage points per year from the timing of short exposure in 2022 through May 2026 and 0.53 points in 1999 through 2021. Average funding explains little." %}
</div>
<p class="figure-caption">Contribution to the factor target’s annual arithmetic return relative to stock shrinkage, using the two calibrated portfolios. Each date uses the average of their signed returns per short dollar to value the funding difference. The three components add to the short-sleeve return gap. Lines show 95% intervals from paired 63-session blocks.</p>

I used that observation to try one change. What if I used factor correlations only between stocks with above-median Ridge scores? I kept the same stock volatilities, historical correlations and risk budget. Only the target for pairs involving lower-scoring names changed, reverting to zero off the diagonal. On the **same filled positions** of the original factor target, the later annualized risk forecast rose from **7.00% to 10.16%**, against **7.28% realized**. Removing part of the positive correlation between a long and a short removes part of their estimated hedge. Giving the new model its own portfolio, it used 91 cents of gross exposure per dollar of capital, down from $1.24. Annual turnover fell from 16.66× to 10.53×, yet net return also fell from 4.59% to 4.21%. I would keep the correlations across the two score groups. The later portfolio returns had already informed this experiment, so the result helps explain the mechanism and needs fresh history for confirmation.

I tested 28 portfolio rules, which gives me 27 opportunities to find a favorable comparison against either reference. Over the full history the factor target’s net Sharpe exceeded the original factor model’s by 0.28. Resampling common 63-session blocks and accounting for those comparisons gave a one-sided 95% lower bound of +0.02. With 20,000 resamples the full-history lower bound stayed between +0.02 and +0.03 for blocks of 21, 63, 126 and 252 sessions. In the later period alone the 63-session bound was −0.27. Against stock shrinkage, none of the 27 alternatives cleared zero at any of the four block lengths.

How much room did those choices give me to fit noise? Following Daniel and Paleologo, I randomly flipped the sign of a block of 63 days for every portfolio together, then asked how much the best choice gained over stock shrinkage. Across repetitions, the original four choices averaged **1.69 percentage points** of annual arithmetic gain on those randomized later returns. With 28 choices that rose to **2.46 points**. On the actual later returns the best of the 28 beat stock shrinkage by **0.18 points** on the same arithmetic basis. The sign experiment measures flexibility conditional on this history. It gives me a reason to ask for fresh evidence before adopting a more complicated portfolio rule. [Daniel and Paleologo, backtesting lecture, slides 31–35](https://www.linkedin.com/posts/gappy_backtesting-lecture-ugcPost-7528535551839305728-Xbow/)

I would keep stock shrinkage as the reference for this Ridge portfolio. The factor model earned its place in the risk report and the hedge tests. It showed me which positions shared risk and helped construct quieter spreads. Giving its estimate of overall risk to stock shrinkage also brought realized volatility close to 7%. Once both traded portfolios took comparable risk, stock shrinkage earned more from the same Ridge scores in the later sample. The return difference is still uncertain enough to keep the factor target as a candidate.
