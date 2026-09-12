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

XGBoost’s [vector-leaf model](https://xgboost.ai/2026/08/25/introducing-the-xgboost-vector-leaf-model) made me curious: would sharing tree splits help predict two related return horizons? I compared it with ordinary XGBoost, LightGBM and Ridge in my existing backtester. The larger differences came from using trees at all and choosing the return horizon.

Each model predicts ranked forward Sharpe targets over 20 or 60 trading days. Ordinary XGBoost, LightGBM and Ridge fit the horizons separately; shared XGBoost learns both together. **50:50 averages the two forecasts before stock selection and portfolio optimization.** Features, normalization and portfolio rules stay fixed.

## Portfolio results

Figure 1 compares net portfolio Sharpe over the full history and its final five years. The input covers 1995–2021; the first portfolio begins on 3 November 1998. Results include 5 basis points of realized costs on traded notional and average the metrics of three staggered rebalance calendars.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/tree-model-comparison/portfolio-sharpe" mobile="/assets/tree-model-comparison/portfolio-sharpe_mobile" version="1" alt="Portfolio Sharpe for ten model and horizon combinations. Tree blends are near 2 over the full history versus Ridge at 1.43; all are lower during 2017–2021." %}
</div>
<p class="figure-caption"><strong>Figure 1: Tree choice matters less than the linear baseline and the horizon.</strong> Circles show full-history Sharpe; diamonds show 2017–2021. Lines connect the two estimates within each forecast; the samples overlap. XGB abbreviates XGBoost.</p>

The three tree blends are close: Sharpe ranges from 1.98 to 2.02, against Ridge’s 1.43. Their annual arithmetic net returns are about 15.4–15.8%, versus 11.5% for Ridge, at similar volatility. Sharing splits gives me little extra here.

Both ordinary tree models prefer the 20-day forecast over the full history; LightGBM reaches a Sharpe of 2.11. Over 2017–2021, however, each model’s blend beats its individual horizons on Sharpe. I’d keep the longer forecast in the comparison. The gap over Ridge also narrows: the tree blends have five-year Sharpe ratios of 1.47–1.48, against 1.31.

## Forecast quality

Figure 2 asks whether the forecasts themselves rank stocks better. **IC** is the daily cross-sectional Spearman correlation between forecast and target. Its information ratio, **ICIR**, is mean daily IC divided by its sample standard deviation, unannualized. It measures the consistency of the ranking signal.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/tree-model-comparison/forecast-quality" mobile="/assets/tree-model-comparison/forecast-quality_mobile" version="1" alt="Full-history mean IC and full-history versus 2017–2021 ICIR. Tree blends have similar ranking quality and exceed Ridge; individual horizons are evaluated against their respective targets." %}
</div>
<p class="figure-caption"><strong>Figure 2: Ranking strength and consistency.</strong> Mean IC uses the full history; ICIR compares full history with 2017–2021. Blends are evaluated against the mean of the two ranked targets; individual forecasts against their own horizon. Finite target coverage differs by horizon, so compare models within the same forecast.</p>

The tree blends are close here too, with full-history ICIR around 0.79 against Ridge’s 0.64. Shared trees sit slightly below ordinary XGBoost. The 60-day forecasts can have steadier IC while their portfolios earn less, which is why I wanted both prediction metrics and complete portfolio results.

For this comparison, LightGBM remains a reasonable choice: it matches the other tree blends and took about 24 minutes for training and prediction, versus roughly 50–54 minutes for XGBoost. Ridge took about a minute per horizon. These are observed timings at the tested settings. The same historical sample has already been inspected, so I’m keeping production unchanged; this study gives me little reason to pursue shared trees further.

<details markdown="1" class="research-details">
<summary>Exact figures and comparison setup</summary>

<div markdown="1">
<p class="table-caption"><strong>Table 1: Full-history portfolio performance.</strong> Annual arithmetic return and volatility in percent; maximum drawdown shown as a positive loss percentage.</p>

<table class="research-table comparison-table horizon-comparison">
<thead><tr><th>Model / forecast</th><th>Return (%)</th><th>Sharpe</th><th>Vol. (%)</th><th>Max DD (%)</th></tr></thead>
<tbody>
<tr><th scope="row">XGBoost 50:50</th><td>15.55</td><td>1.98</td><td>7.85</td><td>14.19</td></tr>
<tr><th scope="row">Shared XGBoost 50:50</th><td>15.42</td><td>1.98</td><td>7.79</td><td>15.08</td></tr>
<tr><th scope="row">LightGBM 50:50</th><td>15.77</td><td>2.02</td><td>7.82</td><td>13.98</td></tr>
<tr><th scope="row">Ridge 50:50</th><td>11.53</td><td>1.43</td><td>8.09</td><td>17.67</td></tr>
<tr class="period-break"><th scope="row">XGBoost 20 days</th><td>16.38</td><td>2.04</td><td>8.02</td><td>14.71</td></tr>
<tr><th scope="row">XGBoost 60 days</th><td>14.01</td><td>1.82</td><td>7.69</td><td>14.97</td></tr>
<tr class="forecast-group-start"><th scope="row">LightGBM 20 days</th><td>16.87</td><td>2.11</td><td>8.00</td><td>12.67</td></tr>
<tr><th scope="row">LightGBM 60 days</th><td>13.93</td><td>1.81</td><td>7.68</td><td>15.52</td></tr>
<tr class="forecast-group-start"><th scope="row">Ridge 20 days</th><td>11.48</td><td>1.39</td><td>8.25</td><td>18.19</td></tr>
<tr><th scope="row">Ridge 60 days</th><td>11.05</td><td>1.40</td><td>7.90</td><td>17.97</td></tr>
</tbody>
</table>
</div>

<div markdown="1">
<p class="table-caption"><strong>Table 2: Recent-window performance.</strong> Net annual arithmetic return in percent and Sharpe. The ten-year window begins on 3 January 2012; the five-year window begins on 3 January 2017. Both end on 31 December 2021.</p>
<table class="research-table comparison-table horizon-comparison">
<thead><tr><th>Model / forecast</th><th>10y return (%)</th><th>10y Sharpe</th><th>5y return (%)</th><th>5y Sharpe</th></tr></thead>
<tbody>
<tr><th scope="row">XGBoost 50:50</th><td>14.76</td><td>1.76</td><td>13.50</td><td>1.47</td></tr>
<tr><th scope="row">Shared XGBoost 50:50</th><td>14.87</td><td>1.78</td><td>13.63</td><td>1.48</td></tr>
<tr><th scope="row">LightGBM 50:50</th><td>14.76</td><td>1.77</td><td>13.52</td><td>1.47</td></tr>
<tr><th scope="row">Ridge 50:50</th><td>12.29</td><td>1.42</td><td>12.59</td><td>1.31</td></tr>
<tr class="period-break"><th scope="row">XGBoost 20 days</th><td>15.01</td><td>1.76</td><td>13.03</td><td>1.38</td></tr>
<tr><th scope="row">XGBoost 60 days</th><td>13.71</td><td>1.68</td><td>12.88</td><td>1.44</td></tr>
<tr class="forecast-group-start"><th scope="row">LightGBM 20 days</th><td>15.02</td><td>1.77</td><td>13.30</td><td>1.43</td></tr>
<tr><th scope="row">LightGBM 60 days</th><td>13.56</td><td>1.65</td><td>12.91</td><td>1.44</td></tr>
<tr class="forecast-group-start"><th scope="row">Ridge 20 days</th><td>12.58</td><td>1.41</td><td>12.14</td><td>1.23</td></tr>
<tr><th scope="row">Ridge 60 days</th><td>11.71</td><td>1.41</td><td>11.65</td><td>1.25</td></tr>
</tbody>
</table>
</div>

<div markdown="1">
<p class="table-caption"><strong>Table 3: Forecast ranking quality.</strong> Mean IC over the full active history and unannualized ICIR over the three reporting windows. Horizon changes alter the target being evaluated.</p>
<table class="research-table comparison-table horizon-comparison">
<thead><tr><th>Model / forecast</th><th>Mean IC</th><th>Full ICIR</th><th>10y ICIR</th><th>5y ICIR</th></tr></thead>
<tbody>
<tr><th scope="row">XGBoost 50:50</th><td>0.0593</td><td>0.788</td><td>0.707</td><td>0.555</td></tr>
<tr><th scope="row">Shared XGBoost 50:50</th><td>0.0587</td><td>0.783</td><td>0.698</td><td>0.540</td></tr>
<tr><th scope="row">LightGBM 50:50</th><td>0.0598</td><td>0.798</td><td>0.709</td><td>0.556</td></tr>
<tr><th scope="row">Ridge 50:50</th><td>0.0512</td><td>0.644</td><td>0.640</td><td>0.515</td></tr>
<tr class="period-break"><th scope="row">XGBoost 20 days</th><td>0.0541</td><td>0.712</td><td>0.589</td><td>0.491</td></tr>
<tr><th scope="row">XGBoost 60 days</th><td>0.0538</td><td>0.717</td><td>0.678</td><td>0.493</td></tr>
<tr class="forecast-group-start"><th scope="row">LightGBM 20 days</th><td>0.0544</td><td>0.718</td><td>0.596</td><td>0.502</td></tr>
<tr><th scope="row">LightGBM 60 days</th><td>0.0543</td><td>0.728</td><td>0.679</td><td>0.491</td></tr>
<tr class="forecast-group-start"><th scope="row">Ridge 20 days</th><td>0.0458</td><td>0.562</td><td>0.529</td><td>0.464</td></tr>
<tr><th scope="row">Ridge 60 days</th><td>0.0482</td><td>0.621</td><td>0.632</td><td>0.474</td></tr>
</tbody>
</table>
</div>

All models use 144 predictors. Targets are the annualized ratio of future mean daily return to future daily volatility, with a zero hurdle, ranked within date and sector onto [−1, 1]. The walk-forward design starts with 900 training sessions, advances in 600-session blocks and retains a 61-session gap. Predictions average three date-phase models. Each horizon keeps the common training sample and prediction rows, including the 60-day eligibility convention.

The tree settings are 350 rounds, depth 5, learning rate 0.05, feature subsampling 0.25 and 255 bins; LightGBM allows 32 leaves. These provide comparable settings while the algorithms differ in growth and regularization. Individual tree portfolios reuse the original saved estimators; Ridge’s blend averages its saved horizon forecasts.

Financial figures average calendar metrics. Each calendar uses fixed notional; drawdown comes from its compounded daily return index. The [portfolio construction](https://piinghel.github.io/quants/2026/08/29/portfolio-optimization.html) is common to all models. IC includes only finite forecast–target pairs with defined daily correlation.

</details>
