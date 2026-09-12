---
layout: post
title: "Can Two Return Horizons Share a Tree?"
description: "Comparing multi-output XGBoost, ordinary XGBoost, LightGBM and Ridge across two return horizons and their 50:50 blends."
permalink: /quants/xgboost-vector-leaves.html
toc: false
show_date: false
date: 2026-09-09
categories: ["Machine learning"]
---

So far, I've used [Ridge](/quants/2025/02/09/multiple-linear-regression.html) as my starting point for forecasting stock returns. The [attribution articles](/quants/portfolio-attribution.html) looked at the portfolio it produces; here I return to the forecasts themselves. I came across XGBoost's [post about vector leaves](https://xgboost.ai/2026/08/25/introducing-the-xgboost-vector-leaf-model) on X, and the idea caught my attention: one tree can share its splits across several outputs, with a separate prediction for each output in every leaf. I wanted to see whether that helped with two related return horizons.

## Sharing splits across horizons

For a stock, the two outputs are forecasts over 20 and 60 trading days. Ordinary XGBoost builds separate trees for each horizon. Multi-output XGBoost uses the same splits for both, with two predictions in each leaf. Sharing could help if the same feature thresholds are useful at both horizons; separate trees give each horizon more freedom. Related targets make this worth trying, but the useful splits still have to align.

I kept Ridge as the linear baseline and added LightGBM as another tree model. Each predicts forward Sharpe—the ratio of future mean daily return to volatility—ranked within date and sector. All four use the same 144 predictors, training windows and eligible stocks, with forecasts evaluated after their training windows.[^setup]

For each model, I take a **50:50 average of the two forecasts** before stock selection and portfolio optimization. Comparing ordinary and shared XGBoost blends asks whether learning the horizons together helps. I also evaluate the individual 20-day and 60-day forecasts from ordinary XGBoost, LightGBM and Ridge, bringing the comparison to ten portfolios. These ask a separate question: does averaging horizons improve on using either one alone?

## Does sharing improve the portfolio?

Table 1 compares the portfolios over the full history and its final five years. All use the same [portfolio construction](/quants/2026/08/29/portfolio-optimization.html), with a charge of 5 basis points on traded notional. As in the [tranching article](/quants/2025/05/10/rebalancing-luck.html), three sleeves each receive one-third of the capital. Each sleeve rebalances every three weeks, with one sleeve rebalancing each week.

<p class="table-caption"><strong>Table 1: Models, individual horizons and 50:50 blends.</strong> Net annual arithmetic return on fixed notional, annualized volatility and Sharpe. Metrics are calculated for each sleeve and then averaged; they describe the average rebalance calendar. The combined three-sleeve return series would have its own volatility and Sharpe. XGB abbreviates XGBoost.</p>
<table class="research-table comparison-table horizon-comparison">
<thead><tr><th>Forecast</th><th>Return<br>(%/yr)</th><th>Vol.<br>(%)</th><th>Sharpe</th></tr></thead>
<tbody>
<tr class="period-heading"><th colspan="4">Full history · November 1998–December 2021</th></tr>
<tr><th scope="row">XGB 50:50</th><td>15.6</td><td>7.9</td><td>1.98</td></tr>
<tr><th scope="row">Shared XGB 50:50</th><td>15.4</td><td>7.8</td><td>1.98</td></tr>
<tr><th scope="row">LightGBM 50:50</th><td>15.8</td><td>7.8</td><td>2.02</td></tr>
<tr><th scope="row">Ridge 50:50</th><td>11.5</td><td>8.1</td><td>1.43</td></tr>
<tr class="forecast-group-start"><th scope="row">XGB 20d</th><td>16.4</td><td>8.0</td><td>2.04</td></tr>
<tr><th scope="row">XGB 60d</th><td>14.0</td><td>7.7</td><td>1.82</td></tr>
<tr class="forecast-group-start"><th scope="row">LightGBM 20d</th><td>16.9</td><td>8.0</td><td>2.11</td></tr>
<tr><th scope="row">LightGBM 60d</th><td>13.9</td><td>7.7</td><td>1.81</td></tr>
<tr class="forecast-group-start"><th scope="row">Ridge 20d</th><td>11.5</td><td>8.3</td><td>1.39</td></tr>
<tr><th scope="row">Ridge 60d</th><td>11.0</td><td>7.9</td><td>1.40</td></tr>
<tr class="period-heading"><th colspan="4">2017–2021</th></tr>
<tr><th scope="row">XGB 50:50</th><td>13.5</td><td>9.2</td><td>1.47</td></tr>
<tr><th scope="row">Shared XGB 50:50</th><td>13.6</td><td>9.2</td><td>1.48</td></tr>
<tr><th scope="row">LightGBM 50:50</th><td>13.5</td><td>9.2</td><td>1.47</td></tr>
<tr><th scope="row">Ridge 50:50</th><td>12.6</td><td>9.6</td><td>1.31</td></tr>
<tr class="forecast-group-start"><th scope="row">XGB 20d</th><td>13.0</td><td>9.4</td><td>1.38</td></tr>
<tr><th scope="row">XGB 60d</th><td>12.9</td><td>8.9</td><td>1.44</td></tr>
<tr class="forecast-group-start"><th scope="row">LightGBM 20d</th><td>13.3</td><td>9.3</td><td>1.43</td></tr>
<tr><th scope="row">LightGBM 60d</th><td>12.9</td><td>9.0</td><td>1.44</td></tr>
<tr class="forecast-group-start"><th scope="row">Ridge 20d</th><td>12.1</td><td>9.8</td><td>1.23</td></tr>
<tr><th scope="row">Ridge 60d</th><td>11.7</td><td>9.3</td><td>1.25</td></tr>
</tbody>
</table>

Sharing the tree structure changes little in this comparison. Ordinary and shared XGBoost blends both round to Sharpe 1.98 over the full history, with annual returns of 15.6% and 15.4%. LightGBM is close at 2.02. In 2017–2021, all three blends are again close, at 1.47–1.48. I see no consistent portfolio gain from sharing splits under these settings.

The larger historical difference is between trees and the fixed Ridge baseline. The tree blends earn around 15.4–15.8% a year versus Ridge's 11.5%, at slightly lower volatility. That produces a full-history Sharpe of roughly 2.0 versus 1.43. The final-five-year gap is smaller, but this is the more promising difference to investigate.

## Does averaging the horizons help?

The individual-horizon rows in Table 1 give a less uniform answer. Over the full history, the 20-day forecast leads for both ordinary tree models: LightGBM reaches Sharpe 2.11, versus 2.02 for its blend and 1.81 for its 60-day forecast. For Ridge, the blend has a small edge over both horizons.

In 2017–2021, the blend beats both individual horizons for each of these three models. For LightGBM, that is 1.47 versus 1.43 and 1.44. Averaging is useful in that window, but it gives up some of the shorter horizon's full-history performance. I would keep the simple blend as a comparator; the results don't establish one horizon choice that wins throughout.

## A closer look at the weaker final period

Looking through the results, I also wanted to understand the weaker final period. For the LightGBM blend, Table 1 shows both lower return and higher volatility in 2017–2021 than over the full history. Ridge's return rises, but its volatility rises proportionally more. Is the ranking itself becoming less useful, or is something changing in how it translates into portfolio returns?

I start with **IC**, the daily cross-sectional Spearman correlation between forecasts and their targets. Its mean measures average ranking quality; its standard deviation measures how much that quality varies across dates. **ICIR** divides the mean by that sample standard deviation, left unannualized. Figure 1 separates these quantities over four five-year periods for the blends, evaluated against the mean of the two ranked targets on common dates.[^periods]

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/tree-model-comparison/forecast-quality" mobile="/assets/tree-model-comparison/forecast-quality_mobile" version="4" alt="Mean IC, SD of daily IC and ICIR across 2002–2006, 2007–2011, 2012–2016 and 2017–2021. The three tree blends follow similar paths. In the final period, all four models have slightly lower mean IC and substantially higher IC variability than in 2012–2016." %}
</div>
<p class="figure-caption"><strong>Figure 1: The signal becomes less consistent in 2017–2021.</strong> Daily Spearman IC for the four 50:50 blends. Each metric has its own scale; lines connect period summaries. The three tree models nearly overlap. *Final forecast date: 6 October 2021, allowing the 60-day targets to be observed within the data.</p>

For LightGBM, mean IC falls from 0.067 in 2012–2016 to 0.062 in 2017–2021, while the standard deviation of daily IC rises from 0.066 to 0.111. ICIR falls from 1.01 to 0.56. Average ranking quality weakens a little; the larger change is how much it varies across dates. All four blends show higher IC variability. The small mean decline is less certain.[^uncertainty]

That wider spread includes more dates when the ranking goes the wrong way: LightGBM's share of negative IC rises from 17% to 25%. Here a negative IC means higher-ranked stocks tend to have worse forward targets on that forecast date. How much the portfolio loses depends on which stocks it actually holds and their returns.

### From ranking quality to returns

Do these changes show up in the portfolio? Figure 2 compares ICIR with portfolio Sharpe, and daily IC variability with mean daily net return. Each point is one five-year period, using the same dates for both measures. I show LightGBM and Ridge because the three tree blends are so close; the final period ends on 6 October 2021 to match the available IC dates.[^endpoints]

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/tree-model-comparison/forecast-outcomes" mobile="/assets/tree-model-comparison/forecast-outcomes_mobile" version="1" alt="Four five-year period summaries for LightGBM and Ridge. ICIR is plotted against portfolio Sharpe, and SD of daily IC against mean daily net return. LightGBM's final period combines lower ICIR and Sharpe with higher IC variability and lower return. Ridge's lowest return occurs in 2007–2011, when IC variability is lower than in either later period." %}
</div>
<p class="figure-caption"><strong>Figure 2: How forecast consistency relates to portfolio performance.</strong> LightGBM and Ridge 50:50 blends, four periods each. Forecast statistics are on the vertical axes, portfolio outcomes on the horizontal axes. Mean daily net return is in basis points; 1 bp is 0.01%. Portfolio metrics average the three rebalance calendars separately. *Final date: 6 October 2021.</p>

For LightGBM, the final period moves down and left in the ICIR–Sharpe plot, and up and left in the IC-variability–return plot. Compared with 2012–2016, its annual net return falls from 16.0% to 11.5%, while portfolio volatility rises from 7.5% to 9.0%. Sharpe falls from 2.14 to 1.27. So the deterioration appears in both the forecasts and the portfolio: less consistent rankings, lower returns and more portfolio risk.

But the earlier points keep me from reading this as a simple conversion from ICIR to Sharpe. Between 2002–2006 and 2007–2011, LightGBM's ICIR falls from 1.16 to 0.94 while Sharpe stays near 2.1. Ridge gives another useful check: its worst return occurs in 2007–2011, even though daily IC varies less than in either later period. Its mean IC is also much lower then. Variability alone misses that loss of average ranking quality.

The common weakness across models makes a changing market environment worth investigating. Still, higher market volatility by itself needn't change a rank correlation: multiplying every stock's target by the same positive number preserves its rank. What matters is how the ordering of stock outcomes changes relative to the forecasts, and how portfolio weights turn those outcomes into P&amp;L. The models share predictors, targets and portfolio construction, so their common decline gives us several places to look. These four periods leave the cause open.

## What I take from the comparison

I tried shared trees because learning two related horizons together seemed worth exploring. Under these settings, they produce much the same portfolio performance as ordinary trees. The larger historical gain is from the tree models over the fixed Ridge baseline, while averaging horizons helps more in some periods than others. For now, I'm keeping production unchanged; a switch to shared trees would need a clearer benefit in a comparison with settings fixed before evaluation.

The declining performance is something I'd like to investigate further. I'd start by checking whether the weaker rankings and portfolio losses are concentrated in the same sectors or on the same side of the book, then compare their exposures and realized payoffs across periods. That would help separate a change in what the signals predict from a change in the risks the portfolio takes. It also gives the next model comparison a more useful question: does the new forecast improve the part of the strategy that has actually weakened?

[^setup]: The input covers 1995–2021; the first portfolio starts on 3 November 1998. Walk-forward training starts with 900 sessions, advances in 600-session blocks and keeps a 61-session gap. Predictions average three date-phase models, and both horizons use common 60-day eligibility. Trees use 350 rounds, depth 5, learning rate 0.05, feature subsampling 0.25 and 255 bins; LightGBM allows 32 leaves. Matching these settings gives different tree structures different amounts of flexibility. This is a comparison at fixed settings, with one fixed Ridge baseline and previously inspected history.

[^periods]: Figure 1 uses 2002–2006, 2007–2011, 2012–2016 and 2017–2021, omitting the initial partial block. The groups share no forecast dates. Removing the final 60 forecast dates from each earlier block also keeps their forward target windows within the block; the increase in recent IC variability remains. Table 1 retains full-calendar portfolio returns through December 2021.

[^uncertainty]: The increase in IC standard deviation survives 60- and 120-session moving-block bootstrap checks and the boundary adjustment. The change in mean IC is less certain: its intervals include zero. Nearby IC observations share forward returns, and all four models use the same market history. These checks describe the inspected sample.

[^endpoints]: Figure 2 matches IC and portfolio dates within each period. Including the rest of 2021 raises LightGBM's final-period Sharpe from 1.27 to about 1.5, as in Table 1. The table averages the original rounded calendar exports; the figure calculates metrics from daily returns. The lower tree returns and higher portfolio volatility survive the endpoint change. The plotted points pair period summaries of forecasts and returns; individual forecasts have overlapping forward target windows.
