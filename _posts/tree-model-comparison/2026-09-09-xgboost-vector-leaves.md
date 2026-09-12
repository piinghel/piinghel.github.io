---
layout: post
title: "Can Two Return Horizons Share a Tree?"
description: "A post about XGBoost vector leaves led me to compare shared trees, ordinary XGBoost and LightGBM with Ridge—and to look at why their later-period performance weakens."
permalink: /quants/xgboost-vector-leaves.html
toc: false
show_date: false
date: 2026-09-09
categories: ["Machine learning"]
---

So far, I've used [Ridge](/quants/2025/02/09/multiple-linear-regression.html) as my starting point for forecasting stock returns. The [attribution articles](/quants/portfolio-attribution.html) looked at the portfolio it produces; here I return to the forecasts themselves. I came across XGBoost's [post about vector leaves](https://xgboost.ai/2026/08/25/introducing-the-xgboost-vector-leaf-model) on X, and the idea caught my attention: one tree can share its splits across several outputs, with a separate prediction for each output in every leaf. I wanted to see whether that helped with two related return horizons.

I kept Ridge as the linear baseline and added ordinary XGBoost and LightGBM, so I could distinguish the benefit of trees from the benefit of sharing their structure. Each model predicts forward Sharpe—the ratio of future mean daily return to volatility—ranked within date and sector, over 20 or 60 trading days. Ordinary XGBoost, LightGBM and Ridge fit the horizons separately; shared XGBoost learns both together.

I also combine the two horizons with a simple **50:50 average of their forecasts**, before stock selection and portfolio optimization. That gives the shorter and longer horizons equal weight without fitting another model to combine them. The individual forecasts remain in the comparison so I can see whether combining them helps.[^setup]

## Forecast quality

I start with **IC**: the daily cross-sectional Spearman correlation between forecasts and their targets. Its information ratio, **ICIR**, compares average ranking quality with its variability across dates:

$$\begin{gathered}
\mathrm{ICIR}=\frac{\overline{IC}}{s_{IC}},\\[6pt]
s_{IC}=\sqrt{\frac{\sum_{t=1}^{T}(IC_t-\overline{IC})^2}{T-1}}.
\end{gathered}$$

Here $T$ counts dates with a defined correlation, using stocks with finite forecast–target pairs. I leave ICIR unannualized. To see when the signal changed, Figure 1 compares four separate five-year periods. The four blends share the same target and dates; the last period ends on 6 October 2021 so the 60-day targets can be observed within the data.[^periods]

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/tree-model-comparison/forecast-quality" mobile="/assets/tree-model-comparison/forecast-quality_mobile" version="4" alt="Mean IC, SD of daily IC and ICIR across 2002–2006, 2007–2011, 2012–2016 and 2017–2021. The three tree blends follow similar paths. In the final period, all four models have slightly lower mean IC and substantially higher IC variability than in 2012–2016." %}
</div>
<p class="figure-caption"><strong>Figure 1: The signal becomes less consistent in 2017–2021.</strong> Daily Spearman IC against the mean of the two ranked targets, for the four 50:50 blends. Each metric has its own scale. Lines connect period summaries; the near-overlap of the tree models is part of the result. XGB abbreviates XGBoost. *Final forecast date: 6 October 2021.</p>

For LightGBM, mean IC falls from 0.067 in 2012–2016 to 0.062 in 2017–2021, while its standard deviation rises from 0.066 to 0.111. ICIR falls from 1.01 to 0.56. Average ranking quality weakens a little; the much larger change is its variability. Across all four models, IC standard deviation rises by roughly 51–69%.[^uncertainty]

That wider spread includes more occasions when the ranking goes the wrong way: LightGBM's share of dates with negative IC rises from 17% to 25%. These are forecast dates evaluated against forward targets, so they cannot be read as the portfolio's share of losing days.

## What reaches the portfolio

Table 1 puts return and volatility beside Sharpe. All models use the same [portfolio construction](/quants/2026/08/29/portfolio-optimization.html), with a charge of 5 basis points on traded notional. As in the [tranching article](/quants/2025/05/10/rebalancing-luck.html), each of three portfolios receives one-third of the capital. Each portfolio rebalances every three weeks, with one rebalancing each week.

<p class="table-caption"><strong>Table 1: Net portfolio return, volatility and Sharpe.</strong> Return is annual arithmetic P&amp;L on fixed notional; volatility is the annualized standard deviation of daily returns. Each column averages the metric calculated separately for the three portfolios, so Sharpe can differ from the ratio of the displayed averages.</p>
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

For the LightGBM blend, annual return falls from 15.8% over the full history to 13.5% in 2017–2021, while volatility rises from 7.8% to 9.2%. Both contribute to the lower Sharpe, from 2.02 to 1.47. The other tree portfolios show the same combination. Ridge is different: its blend's return rises from 11.5% to 12.6%, but volatility rises more proportionally, from 8.1% to 9.6%, and Sharpe slips from 1.43 to 1.31.

Both ordinary tree models prefer the 20-day forecast over the full history; LightGBM reaches Sharpe 2.11. In 2017–2021, each model's blend beats its individual horizons on Sharpe. That gives me a reason to keep both horizons in the comparison. The bigger historical difference is between trees and Ridge; sharing splits adds little here.

## What changed over time?

Figure 2 connects the forecast statistics to portfolio outcomes over the same four periods. I show LightGBM and Ridge here because the three tree blends behave so similarly. Both axes use matching dates, ending on 6 October in the final period. That gives LightGBM a recent Sharpe of 1.27; including the final quarter, as Table 1 does, raises it to about 1.5.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/tree-model-comparison/forecast-outcomes" mobile="/assets/tree-model-comparison/forecast-outcomes_mobile" version="1" alt="Four period comparisons for LightGBM and Ridge. Left panels show ICIR against portfolio Sharpe; right panels show SD of daily IC against mean daily net return. LightGBM's latest period has lower ICIR and Sharpe and higher IC variability. Ridge's lowest return occurs in 2007–2011, despite lower IC variability than in the later periods." %}
</div>
<p class="figure-caption"><strong>Figure 2: Forecast consistency and portfolio performance move together, imperfectly.</strong> Each point represents one five-year period. Right panels use arithmetic mean daily net return in basis points; 1 bp is 0.01%. Portfolio statistics average the three rebalance calendars separately. *Both axes end on 6 October 2021 in the final period. These are historical point estimates.</p>

The change between periods is much larger than the difference between tree implementations. Their Sharpes cluster around 2.14–2.18 in 2012–2016, then 1.24–1.27 on the matching dates in 2017–2021. LightGBM's annualized return falls from 16.0% to 11.5%, while portfolio volatility rises from 7.5% to 9.0%. The direction survives including the final quarter. Switching tree libraries hasn't avoided the shared deterioration.

Still, ICIR isn't a direct conversion into Sharpe. LightGBM's ICIR falls from 1.16 in 2002–2006 to 0.94 in 2007–2011, while Sharpe stays near 2.1. Ridge gives another useful counterexample: its IC variability is lower in 2007–2011 than in 2012–2016, yet its return is much worse. Its mean IC is also lower. Which stocks receive weight, their correlations and the size of their gains and losses matter alongside ranking quality.

A changing market environment is one possible explanation. But simply scaling every stock's target by the same positive amount preserves ranks and leaves rank IC unchanged. We would need to understand changes in which stocks outperform and how those changes interact with our signals. The shared inputs and portfolio construction are other places to look.

I started by comparing tree implementations. What I take from this is how similarly they struggle in the same period: the average signal remains positive, but it becomes less reliable while portfolio risk rises. I'm keeping production unchanged; this inspected history gives me no clear reason to adopt shared trees.

[^setup]: The input covers 1995–2021 with 144 common predictors; the first portfolio starts on 3 November 1998. Walk-forward training starts with 900 sessions, advances in 600-session blocks and keeps a 61-session gap. Predictions average three date-phase models, and both horizons use the common 60-day eligibility convention. Trees use 350 rounds, depth 5, learning rate 0.05, feature subsampling 0.25 and 255 bins; LightGBM allows 32 leaves. Individual-horizon IC uses its own target and available pairs, so model comparisons should hold the forecast horizon fixed.

[^periods]: The figures use 2002–2006, 2007–2011, 2012–2016 and 2017–2021, omitting the initial partial block. The groups share no forecast dates. Removing the final 60 forecast dates from each earlier block also keeps their forward target windows within the block; the increase in recent IC variability remains. Table 1 retains full-calendar portfolio returns.

[^uncertainty]: The increase in IC standard deviation survives 60- and 120-session moving-block bootstrap checks and the boundary adjustment. The change in mean IC is less certain: its intervals include zero. Nearby IC observations share forward returns, and all four models use the same market history. These checks describe the inspected sample.
