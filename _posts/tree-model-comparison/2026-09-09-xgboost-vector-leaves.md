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

I kept Ridge as the linear baseline and added LightGBM as another tree model. Each predicts forward Sharpe—the ratio of future mean daily return to volatility—ranked within date and sector. All four use the same 144 predictors, training windows and eligible stocks, with forecasts evaluated after their training windows.[^setup] I kept the model settings fixed, including one Ridge specification, and used history I'd already inspected. Matching settings also leaves different tree structures with different amounts of flexibility.

For each model, I take a **50:50 average of the two forecasts** before stock selection and portfolio optimization. Comparing ordinary and shared XGBoost blends asks whether learning the horizons together helps. I also evaluate the individual 20-day and 60-day forecasts from ordinary XGBoost, LightGBM and Ridge, bringing the comparison to ten portfolios. These ask a separate question: does averaging horizons improve on using either one alone?

## Does sharing improve the portfolio?

Table 1 compares the four blends over the full history. All use the same [portfolio construction](/quants/2026/08/29/portfolio-optimization.html), with a charge of 5 basis points on traded notional. As in the [tranching article](/quants/2025/05/10/rebalancing-luck.html), three sleeves each receive one-third of the capital. Each sleeve rebalances every three weeks, with one sleeve rebalancing each week. I calculate performance for each sleeve and then average the metrics, so the reported volatility and Sharpe describe the average rebalance calendar. Combining the sleeves would give its own volatility and Sharpe.

<p class="table-caption"><strong>Table 1: Comparing the four 50:50 blends.</strong> November 1998–December 2021. Net annual arithmetic return on fixed notional, annualized volatility and Sharpe; each metric averages three rebalance calendars. XGB abbreviates XGBoost.</p>
<table class="research-table comparison-table horizon-comparison">
<thead><tr><th>Forecast</th><th>Return<br>(%/yr)</th><th>Vol.<br>(%)</th><th>Sharpe</th></tr></thead>
<tbody>
<tr><th scope="row">XGB 50:50</th><td>15.6</td><td>7.9</td><td>1.98</td></tr>
<tr><th scope="row">Shared XGB 50:50</th><td>15.4</td><td>7.8</td><td>1.98</td></tr>
<tr><th scope="row">LightGBM 50:50</th><td>15.8</td><td>7.8</td><td>2.02</td></tr>
<tr><th scope="row">Ridge 50:50</th><td>11.5</td><td>8.1</td><td>1.43</td></tr>
</tbody>
</table>

Sharing the tree structure changes little in this comparison. Ordinary and shared XGBoost blends both round to Sharpe 1.98 over the full history, with annual returns of 15.6% and 15.4%. LightGBM is close at 2.02. In 2017–2021, all three blends are again close, at 1.47–1.48. I see no consistent portfolio gain from sharing splits under these settings.

The larger historical difference is between trees and the fixed Ridge baseline. The tree blends earn around 15.4–15.8% a year versus Ridge's 11.5%, at slightly lower volatility. The final-five-year Sharpe gap is smaller—1.47–1.48 versus 1.31—but the tree-versus-linear comparison is the more promising difference to investigate.

## Does averaging the horizons help?

Table 2 puts the horizon choices next to each other. Over the full history, the 20-day forecast leads for both ordinary tree models. For Ridge, the blend has a small edge over both horizons.

<p class="table-caption"><strong>Table 2: Does the blend improve Sharpe?</strong> Net annualized Sharpe, averaged across the same three rebalance calendars. The 50:50 column averages forecasts before portfolio construction.</p>
<table class="research-table comparison-table horizon-comparison">
<thead><tr><th>Model</th><th>20-day</th><th>50:50</th><th>60-day</th></tr></thead>
<tbody>
<tr class="period-heading"><th colspan="4">Full history · November 1998–December 2021</th></tr>
<tr><th scope="row">XGB</th><td>2.04</td><td>1.98</td><td>1.82</td></tr>
<tr><th scope="row">LightGBM</th><td>2.11</td><td>2.02</td><td>1.81</td></tr>
<tr><th scope="row">Ridge</th><td>1.39</td><td>1.43</td><td>1.40</td></tr>
<tr class="period-heading"><th colspan="4">2017–2021</th></tr>
<tr><th scope="row">XGB</th><td>1.38</td><td>1.47</td><td>1.44</td></tr>
<tr><th scope="row">LightGBM</th><td>1.43</td><td>1.47</td><td>1.44</td></tr>
<tr><th scope="row">Ridge</th><td>1.23</td><td>1.31</td><td>1.25</td></tr>
</tbody>
</table>

In 2017–2021, the blend beats both individual horizons for each of these three models. Averaging is useful in that window, but it gives up some of the shorter horizon's full-history performance. I would keep the simple blend as a comparator; the results don't establish one horizon choice that wins throughout.

## A closer look at the weaker final period

Looking through the results, I also wanted to understand the weaker final period. In 2017–2021, the LightGBM blend's annual return is 13.5% and volatility is 9.2%: lower return and higher risk than over the full history. Ridge's return rises to 12.6%, but its volatility rises proportionally more, to 9.6%. Is the ranking itself becoming less useful, or is something changing in how it translates into portfolio returns?

I start with **IC**, the daily cross-sectional Spearman correlation between forecasts and their targets. Its mean measures average ranking quality; its standard deviation measures how much that quality varies across dates. **ICIR** divides the mean by that sample standard deviation, left unannualized. Figure 1 separates these quantities over four five-year periods for the blends, evaluated against the mean of the two ranked targets on common dates. I start in 2002 to leave out the initial partial period.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/tree-model-comparison/forecast-quality" mobile="/assets/tree-model-comparison/forecast-quality_mobile" version="4" alt="Mean IC, SD of daily IC and ICIR across 2002–2006, 2007–2011, 2012–2016 and 2017–2021. The three tree blends follow similar paths. In the final period, all four models have slightly lower mean IC and substantially higher IC variability than in 2012–2016." %}
</div>
<p class="figure-caption"><strong>Figure 1: The signal becomes less consistent in 2017–2021.</strong> Daily Spearman IC for the four 50:50 blends. Each metric has its own scale; lines connect period summaries. The three tree models nearly overlap. *Final forecast date: 6 October 2021, allowing the 60-day targets to be observed within the data.</p>

For LightGBM, mean IC falls from 0.067 in 2012–2016 to 0.062 in 2017–2021, while the standard deviation of daily IC rises from 0.066 to 0.111. ICIR falls from 1.01 to 0.56. Average ranking quality weakens a little; the larger change is how much it varies across dates. All four blends show higher IC variability. That increase survives block-bootstrap checks that account for overlapping forward returns, and removing forecasts whose targets cross period boundaries. The intervals for the small mean change include zero, so I'm less confident about that decline.

That wider spread includes more dates when the ranking goes the wrong way: LightGBM's share of negative IC rises from 17% to 25%. Here a negative IC means higher-ranked stocks tend to have worse forward targets on that forecast date. How much the portfolio loses depends on which stocks it actually holds and their returns.

### From ranking quality to returns

Do these changes show up in the portfolio? Figure 2 compares ranking quality with portfolio performance for LightGBM and Ridge; the three tree blends are so close that one is enough here. Each labelled point represents one five-year period, using the same dates for the forecast and portfolio measures. Farther right means better portfolio performance. Higher ICIR means more consistent ranking quality, while a higher standard deviation of daily IC means that quality varies more. The filled triangles mark the final period.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/tree-model-comparison/forecast-outcomes" mobile="/assets/tree-model-comparison/forecast-outcomes_mobile" version="2" alt="Four labelled periods for each 50:50 blend, LightGBM and Ridge. ICIR is on the vertical axis against annualized portfolio Sharpe; standard deviation of daily IC is on the vertical axis against annual net arithmetic return in percent. Filled triangles highlight 2017–2021. LightGBM's final period has lower ICIR and Sharpe, greater IC variability and lower return than 2012–2016. Ridge's lowest return occurs in 2007–2011." %}
</div>
<p class="figure-caption"><strong>Figure 2: Do more consistent forecasts go with better portfolio performance?</strong> LightGBM and Ridge 50:50 blends. Annual net return is arithmetic: mean daily return × 252, expressed as a percentage of fixed notional. Portfolio metrics average the three rebalance calendars separately; ICIR remains unannualized. *The final period ends on 6 October 2021 so all 60-day targets are observed.</p>

For LightGBM, the final period moves down and left in the ICIR–Sharpe plot, and up and left in the IC-variability–return plot. Compared with 2012–2016, its annual net return falls from 16.0% to 11.5%, while portfolio volatility rises from 7.5% to 9.0%. Sharpe falls from 2.14 to 1.27. Including the rest of 2021 raises that last Sharpe to about 1.5, as in Table 2; the lower return and higher volatility remain. So the deterioration appears in both the forecasts and the portfolio: less consistent rankings, lower returns and more portfolio risk.

But the earlier points keep me from reading this as a simple conversion from ICIR to Sharpe. Between 2002–2006 and 2007–2011, LightGBM's ICIR falls from 1.16 to 0.94 while Sharpe stays near 2.1. Ridge gives another useful check: its worst return occurs in 2007–2011, even though daily IC varies less than in either later period. Its mean IC is also much lower then. Variability alone misses that loss of average ranking quality.

The common weakness across models makes a changing market environment worth investigating. Still, higher market volatility by itself needn't change a rank correlation: multiplying every stock's target by the same positive number preserves its rank. What matters is how the ordering of stock outcomes changes relative to the forecasts, and how portfolio weights turn those outcomes into P&amp;L. The models share predictors, targets and portfolio construction, so their common decline gives us several places to look. These four periods leave the cause open.

## What I take from the comparison

I tried shared trees because learning two related horizons together seemed worth exploring. Under these settings, they produce much the same portfolio performance as ordinary trees. The larger historical gain is from the tree models over the fixed Ridge baseline. For now, I'm keeping production unchanged; a switch to shared trees would need a clearer benefit in a comparison with settings fixed before evaluation.

I still like the simple 50:50 blend of the 20-day and 60-day forecasts. Part of that preference is methodological: I'd rather spread the choice across two horizons than rely entirely on one. Here, the full-history performance trade-off is modest, and the blend does better in the final period. If it lagged the 20-day forecast by a lot, I'd find that preference much harder to defend. My hunch is that combining horizons could also help as the economic environment changes. That depends on their mistakes differing enough to offset each other; they still share predictors, training history and overlapping targets. Greater robustness is something I'd like to test, rather than a benefit I can already claim.

The declining performance is something I'd like to investigate further. I'd start by checking whether the weaker rankings and portfolio losses are concentrated in the same sectors or on the same side of the book, then compare their exposures and realized payoffs across periods. That would help separate a change in what the signals predict from a change in the risks the portfolio takes. It also gives the next model comparison a more useful question: does the new forecast improve the part of the strategy that has actually weakened?

[^setup]: Walk-forward training uses a 900-session warmup, 600-session steps and a 61-session gap. Predictions average three date-phase models; both horizons require complete 60-day targets. Trees use 350 rounds, depth 5, learning rate 0.05, feature subsampling 0.25 and 255 bins; LightGBM allows 32 leaves.
