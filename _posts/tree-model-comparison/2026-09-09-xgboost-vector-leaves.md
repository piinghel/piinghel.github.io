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

Here $T$ counts dates with a defined correlation, using stocks with finite forecast–target pairs. I leave ICIR unannualized. Figure 1 separates its mean and sample standard deviation for the four blends, which share the same target and dates.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/tree-model-comparison/forecast-quality" mobile="/assets/tree-model-comparison/forecast-quality_mobile" version="3" alt="Mean IC, sample standard deviation of daily IC and ICIR for four 50:50 blends. Mean IC is slightly higher in 2017–2021, but standard deviation rises much more and ICIR falls for every model." %}
</div>
<p class="figure-caption"><strong>Figure 1: Average ranking holds up; its variability rises.</strong> All forecasts are 50:50 blends, evaluated against the mean of the two ranked targets. Circles show full history; diamonds show 2017–2021. The samples overlap. Each metric has its own scale. XGB abbreviates XGBoost.</p>

The tree blends have full-history ICIR around 0.79, against Ridge's 0.64, with little difference between the three tree models. Their lower ICIR in 2017–2021 initially looks like a weaker signal. But the mean IC is slightly higher for every blend; its standard deviation rises by roughly 42–48%.

For LightGBM, mean IC moves from 0.060 to 0.062 while its standard deviation rises from 0.075 to 0.111. ICIR falls from 0.80 to 0.56: the average ranking holds up, but varies more from day to day. The individual 20- and 60-day forecasts show the same direction. These overlapping-period summaries describe that change; they leave its economic cause open.

## What reaches the portfolio

Table 1 puts return and volatility beside Sharpe. All models use the same [portfolio construction](/quants/2026/08/29/portfolio-optimization.html), with 5 basis points of realized costs on traded notional. As in the [tranching article](/quants/2025/05/10/rebalancing-luck.html), each of three portfolios receives one-third of the capital. Each portfolio rebalances every three weeks, with one rebalancing each week.

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

IC variability and portfolio volatility describe different parts of the process. The former measures how much ranking quality changes across dates; the latter measures how much the portfolio's daily return changes. Their increase helps describe the deterioration, but connecting the two requires looking at which stocks the forecasts selected and how they were sized.

Both ordinary tree models prefer the 20-day forecast over the full history; LightGBM reaches Sharpe 2.11. In 2017–2021, each model's blend beats its individual horizons on Sharpe. That gives me a reason to keep both horizons in the comparison. The bigger historical difference is between trees and Ridge; sharing splits adds little here.

I'm keeping production unchanged. This history has already been inspected, and shared trees haven't given me a clear improvement. The more useful follow-up is to understand how a similar average ranking signal translates into lower tree-portfolio returns and higher risk.

[^setup]: The input covers 1995–2021 with 144 common predictors; the first portfolio starts on 3 November 1998. Walk-forward training starts with 900 sessions, advances in 600-session blocks and keeps a 61-session gap. Predictions average three date-phase models, and both horizons use the common 60-day eligibility convention. Trees use 350 rounds, depth 5, learning rate 0.05, feature subsampling 0.25 and 255 bins; LightGBM allows 32 leaves. Individual-horizon IC uses its own target and available pairs, so model comparisons should hold the forecast horizon fixed.
