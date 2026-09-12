---
layout: post
title: "Can Two Return Horizons Share a Tree?"
description: "XGBoost and LightGBM beat a Ridge baseline in this historical comparison, while sharing tree splits brings little benefit. The return horizon matters more."
permalink: /quants/xgboost-vector-leaves.html
toc: false
show_date: false
date: 2026-09-09
categories: ["Machine learning"]
---

XGBoost’s [vector-leaf model](https://xgboost.ai/2026/08/25/introducing-the-xgboost-vector-leaf-model) made me curious: would sharing tree splits help predict two related return horizons? I compared ordinary XGBoost, shared XGBoost, LightGBM and Ridge, starting with forecast quality and then the portfolios those forecasts produce.

Each model predicts forward Sharpe—the ratio of future mean daily return to volatility—ranked within date and sector, over 20 or 60 trading days. Ordinary XGBoost, LightGBM and Ridge fit the horizons separately; shared XGBoost learns both together. **50:50 averages the two forecasts before stock selection and portfolio optimization.**

The input covers 1995–2021, with 144 common predictors. The walk-forward comparison starts with 900 training sessions, advances in 600-session blocks and keeps a 61-session gap. Predictions average three date-phase models; both horizons use the common 60-day eligibility convention.

## Forecast quality

**IC** is the daily cross-sectional Spearman correlation between forecasts and their targets, calculated over stocks with finite pairs. I compare its information ratio, **ICIR**:

$$\mathrm{ICIR}=\frac{\operatorname{mean}_t(IC_t)}{\operatorname{sd}_t(IC_t)}.$$

The denominator is the sample standard deviation across dates with a defined correlation. I leave the ratio unannualized. A higher value means stronger average ranking relative to its day-to-day variability.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/tree-model-comparison/forecast-quality" mobile="/assets/tree-model-comparison/forecast-quality_mobile" version="2" alt="ICIR for ten model and horizon combinations over the full history and 2017–2021. Tree blends are near 0.79 versus Ridge at 0.64 over the full history; all are lower in the later period." %}
</div>
<p class="figure-caption"><strong>Figure 1: Ranking quality relative to its variability.</strong> Circles show full history; diamonds show 2017–2021. Lines connect overlapping samples. Blends use the mean of the ranked targets; individual forecasts use their own horizon. Target coverage differs, so compare models within the same forecast. XGB abbreviates XGBoost.</p>

The tree blends are close, with full-history ICIR around 0.79 against Ridge’s 0.64. Shared trees sit slightly below ordinary XGBoost. ICIR drops for all models in 2017–2021, and the gap over Ridge narrows.

## Portfolio results

The first portfolio begins on 3 November 1998. Results include 5 basis points of realized costs on traded notional and average the metrics of three staggered rebalance calendars. All models use the same [portfolio construction](/quants/2026/08/29/portfolio-optimization.html).

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/tree-model-comparison/portfolio-sharpe" mobile="/assets/tree-model-comparison/portfolio-sharpe_mobile" version="1" alt="Portfolio Sharpe for ten model and horizon combinations. Tree blends are near 2 over the full history versus Ridge at 1.43; all are lower during 2017–2021." %}
</div>
<p class="figure-caption"><strong>Figure 2: Shared splits add little to portfolio Sharpe.</strong> The same models, row order and period encoding as Figure 1, now evaluated through their net portfolio returns.</p>

The three tree blends have Sharpe ratios of 1.98–2.02, against Ridge’s 1.43. Their annual arithmetic net returns are 15.4–15.8% at 7.8–7.9% volatility, versus Ridge’s 11.5% at 8.1%. Sharing splits gives me little extra here.

Both ordinary tree models prefer the 20-day forecast over the full history; LightGBM reaches Sharpe 2.11. Yet the 60-day forecasts can have higher ICIR while their portfolios earn less. Over 2017–2021, each model’s blend beats its individual horizons on Sharpe. The tree blends reach 1.47–1.48 against Ridge’s 1.31. That gives me a reason to retain both horizons.

## Computation time

<p class="table-caption"><strong>Table 1: Observed training and prediction time.</strong> Full walk-forward stages for both horizons, excluding feature preparation and portfolio optimization. These are observed runs, not a controlled timing benchmark.</p>
<table class="research-table comparison-table timing-table">
<thead><tr><th>Model</th><th>Minutes</th></tr></thead>
<tbody>
<tr><th scope="row">XGBoost</th><td>54.0</td></tr>
<tr><th scope="row">Shared XGBoost</th><td>50.3</td></tr>
<tr><th scope="row">LightGBM</th><td>23.7</td></tr>
<tr><th scope="row">Ridge</th><td>1.9</td></tr>
</tbody>
</table>

Ridge’s time sums its two separate horizon runs. The trees use 350 rounds, depth 5, learning rate 0.05, feature subsampling 0.25 and 255 bins; LightGBM allows 32 leaves. Timings depend on these settings and the run conditions.

LightGBM matches the other tree blends at less than half their observed training and prediction time. That makes it a reasonable choice here. The historical sample has already been inspected, so I’m keeping production unchanged; this comparison gives me little reason to pursue shared trees further.
