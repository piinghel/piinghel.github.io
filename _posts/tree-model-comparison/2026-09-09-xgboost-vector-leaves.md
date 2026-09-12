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

XGBoost’s [vector-leaf model](https://xgboost.ai/2026/08/25/introducing-the-xgboost-vector-leaf-model) made me curious: would sharing tree splits help predict two related return horizons? A shared tree uses the same splits for both targets and stores two predictions in each leaf. That could be useful if the two horizons benefit from similar partitions of the feature space.

I wanted to know whether that translated into a better portfolio. I compared ordinary XGBoost, shared XGBoost and LightGBM in my existing ML backtester, keeping the features, normalization and portfolio rules fixed. I included Ridge as a linear baseline: before choosing between tree implementations, I want to know what they add over a simple regularized regression. I also checked the individual horizons, because the choice of target can matter more than the choice of tree implementation.

Each target is the annualized ratio of future mean daily return to future daily volatility, measured over 20 or 60 trading days, then ranked within each date and sector onto [−1, 1]. The return hurdle is zero. Ordinary XGBoost, LightGBM and Ridge fit one model per horizon; shared XGBoost learns both targets together. **50:50 means averaging the two forecasts before stock selection and portfolio optimization.**

## Portfolio performance

The backtest input covers 1995–2021. After the original training warmup, the first portfolio starts on 3 November 1998; all results end on 31 December 2021. Table 1 uses the backtester’s net long–short financial metrics, with realized trading costs of 5 basis points on traded notional.

<div markdown="1">
<p class="table-caption"><strong>Table 1: Full-history portfolio performance.</strong> Annual arithmetic return and volatility in percent; maximum drawdown shown as a positive loss percentage.</p>

<table class="research-table comparison-table">
<thead><tr><th>Model / forecast</th><th>Return</th><th>Sharpe</th><th>Vol.</th><th>Max DD</th></tr></thead>
<tbody>
<tr><th scope="row">XGBoost 50:50</th><td>15.55</td><td>1.98</td><td>7.85</td><td>14.19</td></tr>
<tr><th scope="row">Shared XGBoost 50:50</th><td>15.42</td><td>1.98</td><td>7.79</td><td>15.08</td></tr>
<tr><th scope="row">LightGBM 50:50</th><td>15.77</td><td>2.02</td><td>7.82</td><td>13.98</td></tr>
<tr><th scope="row">Ridge 50:50</th><td>11.53</td><td>1.43</td><td>8.09</td><td>17.67</td></tr>
<tr class="period-break"><th scope="row">XGBoost 20 days</th><td>16.38</td><td>2.04</td><td>8.02</td><td>14.71</td></tr>
<tr><th scope="row">XGBoost 60 days</th><td>14.01</td><td>1.82</td><td>7.69</td><td>14.97</td></tr>
<tr><th scope="row">LightGBM 20 days</th><td>16.87</td><td>2.11</td><td>8.00</td><td>12.67</td></tr>
<tr><th scope="row">LightGBM 60 days</th><td>13.93</td><td>1.81</td><td>7.68</td><td>15.52</td></tr>
<tr><th scope="row">Ridge 20 days</th><td>11.48</td><td>1.39</td><td>8.25</td><td>18.19</td></tr>
<tr><th scope="row">Ridge 60 days</th><td>11.05</td><td>1.40</td><td>7.90</td><td>17.97</td></tr>
</tbody>
</table>
</div>

The reported numbers average the metrics of three staggered rebalance calendars, following the existing package convention. Each calendar uses fixed notional; drawdown is calculated from its compounded daily return index. The [portfolio construction](https://piinghel.github.io/quants/2026/08/29/portfolio-optimization.html) and its risk, exposure and trading rules are common to every model.

The three tree-model blends are close: annual returns span 15.42–15.77%, Sharpe ratios 1.98–2.02, and volatility stays around 7.8%. Shared trees give me no visible portfolio upgrade here. LightGBM has a small full-history advantage at these settings, which is consistent with keeping the simpler existing choice.

The larger gap is between the trees and Ridge. Ridge's blend earns 11.53% a year with a Sharpe of 1.43 and a maximum drawdown of 17.67%. Its volatility is similar to the tree blends, so their higher returns also translate into higher Sharpe ratios. The trees add value over this linear baseline in the historical sample, although this comparison alone does not tell me which nonlinear relationships account for it.

The individual horizons make a larger difference than the choice between tree implementations. Both ordinary tree models earn more with the 20-day forecast over the full history. LightGBM’s 20-day portfolio has a full-history Sharpe of 2.11. But the preference for the shorter horizon does not hold uniformly in the recent windows.

<div markdown="1">
<p class="table-caption"><strong>Table 2: Recent-window performance.</strong> Net annual arithmetic return in percent and Sharpe. The ten-year window begins on 3 January 2012; the five-year window begins on 3 January 2017. Both end on 31 December 2021.</p>
<table class="research-table comparison-table">
<thead><tr><th>Model / forecast</th><th>10y return</th><th>10y Sharpe</th><th>5y return</th><th>5y Sharpe</th></tr></thead>
<tbody>
<tr><th scope="row">XGBoost 50:50</th><td>14.76</td><td>1.76</td><td>13.50</td><td>1.47</td></tr>
<tr><th scope="row">Shared XGBoost 50:50</th><td>14.87</td><td>1.78</td><td>13.63</td><td>1.48</td></tr>
<tr><th scope="row">LightGBM 50:50</th><td>14.76</td><td>1.77</td><td>13.52</td><td>1.47</td></tr>
<tr><th scope="row">Ridge 50:50</th><td>12.29</td><td>1.42</td><td>12.59</td><td>1.31</td></tr>
<tr class="period-break"><th scope="row">XGBoost 20 days</th><td>15.01</td><td>1.76</td><td>13.03</td><td>1.38</td></tr>
<tr><th scope="row">XGBoost 60 days</th><td>13.71</td><td>1.68</td><td>12.88</td><td>1.44</td></tr>
<tr><th scope="row">LightGBM 20 days</th><td>15.02</td><td>1.77</td><td>13.30</td><td>1.43</td></tr>
<tr><th scope="row">LightGBM 60 days</th><td>13.56</td><td>1.65</td><td>12.91</td><td>1.44</td></tr>
<tr><th scope="row">Ridge 20 days</th><td>12.58</td><td>1.41</td><td>12.14</td><td>1.23</td></tr>
<tr><th scope="row">Ridge 60 days</th><td>11.71</td><td>1.41</td><td>11.65</td><td>1.25</td></tr>
</tbody>
</table>
</div>

In Table 2, the tree-model blends again sit close together. Over the last five years, the XGBoost and LightGBM blends each have a higher Sharpe than either of their individual horizons. The full-history preference for 20 days therefore gives me no reason to discard the longer forecast. Portfolio optimization also makes the blend a distinct strategy: averaging forecasts can change which stocks are selected and how they are weighted.

Ridge's blend also has a higher five-year Sharpe than either individual horizon. The tree blends still lead, but the gap has narrowed: their five-year Sharpe ratios are 1.47–1.48 against Ridge's 1.31, compared with 1.98–2.02 against 1.43 over the full history.

## Ranking quality

Table 3 checks the forecasts directly. IC is the daily cross-sectional Spearman correlation between forecast and target. ICIR is its mean divided by its sample standard deviation, unannualized. A blend is evaluated against the equal-weight mean of the two ranked targets; an individual forecast is evaluated against its own horizon. Only finite forecast–target pairs and defined daily correlations enter the calculation. Changing the horizon changes both the target and the available pairs; the shorter target also has more evaluation dates.

<div markdown="1">
<p class="table-caption"><strong>Table 3: Forecast ranking quality.</strong> Mean IC over the full active history and unannualized ICIR over the three reporting windows. Horizon changes alter the target being evaluated.</p>
<table class="research-table comparison-table">
<thead><tr><th>Model / forecast</th><th>Mean IC</th><th>Full ICIR</th><th>10y ICIR</th><th>5y ICIR</th></tr></thead>
<tbody>
<tr><th scope="row">XGBoost 50:50</th><td>0.0593</td><td>0.788</td><td>0.707</td><td>0.555</td></tr>
<tr><th scope="row">Shared XGBoost 50:50</th><td>0.0587</td><td>0.783</td><td>0.698</td><td>0.540</td></tr>
<tr><th scope="row">LightGBM 50:50</th><td>0.0598</td><td>0.798</td><td>0.709</td><td>0.556</td></tr>
<tr><th scope="row">Ridge 50:50</th><td>0.0512</td><td>0.644</td><td>0.640</td><td>0.515</td></tr>
<tr class="period-break"><th scope="row">XGBoost 20 days</th><td>0.0541</td><td>0.712</td><td>0.589</td><td>0.491</td></tr>
<tr><th scope="row">XGBoost 60 days</th><td>0.0538</td><td>0.717</td><td>0.678</td><td>0.493</td></tr>
<tr><th scope="row">LightGBM 20 days</th><td>0.0544</td><td>0.718</td><td>0.596</td><td>0.502</td></tr>
<tr><th scope="row">LightGBM 60 days</th><td>0.0543</td><td>0.728</td><td>0.679</td><td>0.491</td></tr>
<tr><th scope="row">Ridge 20 days</th><td>0.0458</td><td>0.562</td><td>0.529</td><td>0.464</td></tr>
<tr><th scope="row">Ridge 60 days</th><td>0.0482</td><td>0.621</td><td>0.632</td><td>0.474</td></tr>
</tbody>
</table>
</div>

The tree-model blends are close here too, with shared trees slightly below ordinary XGBoost on ICIR in each window. Ridge has a lower blend ICIR in all three windows, consistent with its weaker portfolio results. The horizon comparison answers a different question: the 60-day target can have a steadier IC while its portfolio earns less. That is why I wanted the complete portfolio backtest alongside the prediction metrics.

## What was held fixed

All models use the same 144 predictors. The tree models use 350 boosting rounds, maximum depth 5, learning rate 0.05, feature subsampling of 0.25 and maximum bin count of 255. LightGBM allows 32 leaves. These are comparable settings; the algorithms still differ in how they grow trees and regularize them. Two separate models also have more independently chosen splits than one shared model at the same number of rounds.

The expanding walk-forward design starts with 900 training sessions, advances in 600-session blocks and retains a 61-session gap. Each prediction averages three models fitted on different date phases. Every individual-horizon comparison keeps the same common training sample and eligible prediction rows as its blend. The 20-day models therefore retain the 60-day training-eligibility and gap convention. The individual tree-horizon portfolios reuse estimators saved by the original blend runs; Ridge's blend averages its saved individual-horizon forecasts.

Training and prediction took about 54 minutes for ordinary XGBoost, 50 minutes for shared XGBoost and 24 minutes for LightGBM. Ridge took about a minute per horizon. These are observed pipeline timings from sequential, two-worker runs. The LightGBM comparator uses the matched research settings; production retains its existing configuration.

Ridge gives me a useful reference: the tree models improve on this linear baseline, while changing the tree implementation adds little. These windows share one historical sample and have already been inspected. The small differences between the tree-model blends give me no reason to change production or keep searching settings until shared trees look better. The remaining question is whether these advantages survive new data.
