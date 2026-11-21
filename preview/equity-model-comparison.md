---
layout: post
title: "Equity Model Comparison"
description: "A comparison of Ridge and LightGBM on the same stock universe, from rank IC to score deciles and after-cost returns."
date: 2026-11-21
navigation: false
article_label: "Signals · Preview"
permalink: /preview/equity-model-comparison.html
---

When I compare two stock scores, I start by asking how well each one orders
the whole cross-section. A long–short portfolio pays particular attention
to the two ends of that ordering. It also changes the weights once risk,
turnover and trading constraints enter. I wanted to see how much of the
difference between a linear model and a boosted tree model survives each
of those steps.

Both models use the 80 predictors from the
[linear comparison]({% link _posts/2025-02-09-combining-predictors.md %}).
The target is the forward 20-session Sharpe ratio, ranked within sector on
each date. Ridge learns a regularized linear combination of the predictors.
LightGBM fits trees that can use thresholds and interactions. I compare their
walk-forward scores on the same stock-days over 1999–2021.

## Ranking the whole cross-section

I compute the Spearman correlation between the scores and realized targets
on each date. The mean of those daily correlations is the rank IC. Dividing
it by their daily sample standard deviation gives the ICIR. I leave the
ratio unannualized because consecutive 20-session outcomes overlap.

<div class="research-table-scroll" tabindex="0" role="region" aria-label="Rank IC, IC standard deviation and ICIR by period">
<table id="table-1" class="research-table comparison-table ic-summary-table">
  <caption><span class="caption-number">Table 1.</span> <span class="caption-title">Daily rank IC, standard deviation and ICIR by period.</span> The full comparison has 5,748 dates.</caption>
  <thead>
    <tr><th scope="col">Period</th><th scope="colgroup" colspan="3">Ridge</th><th scope="colgroup" colspan="3">LightGBM</th></tr>
    <tr><th></th><th scope="col">IC</th><th scope="col">SD</th><th scope="col">ICIR</th><th scope="col">IC</th><th scope="col">SD</th><th scope="col">ICIR</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">1999–2021</th><td>0.0480</td><td>0.090</td><td>0.54</td><td>0.0551</td><td>0.077</td><td>0.72</td></tr>
    <tr><th scope="row">1999–2011</th><td>0.0420</td><td>0.073</td><td>0.58</td><td>0.0555</td><td>0.061</td><td>0.91</td></tr>
    <tr><th scope="row">2012–2021</th><td>0.0559</td><td>0.108</td><td>0.52</td><td>0.0545</td><td>0.093</td><td>0.58</td></tr>
    <tr><th scope="row">2017–2021</th><td>0.0607</td><td>0.128</td><td>0.47</td><td>0.0554</td><td>0.114</td><td>0.49</td></tr>
  </tbody>
</table>
</div>

LightGBM's lead in mean IC comes from 1999–2011. Ridge has the higher mean
in both recent windows. The daily IC is steadier for LightGBM in all four
rows, enough to give it a slightly higher ICIR in 2017–2021.

## Return and risk by score decile

To see where the scores differ, I sort the eligible stocks into ten
equal-weight deciles on each rebalance date and trade at the next close.
Each of three schedules rebalances every 15 sessions. I average their
daily returns before compounding, and use zero cash return for the Sharpe
ratio. This gives the same gross portfolio diagnostic for both scores.

<figure id="figure-1" class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/equity-model-comparison/decile-profile" mobile="/assets/equity-model-comparison/decile-profile_mobile" version="1" alt="In 1999–2021, LightGBM's top score decile earns higher annual return and has higher volatility than Ridge. Their top decile Sharpes are nearly equal." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 1.</span> <span class="caption-title">Return, volatility and Sharpe by score decile.</span> Decile 10 holds the highest scores. The series show 1999–2021 before costs.</figcaption>
</figure>

The top LightGBM decile earned 18.3% a year at 22.1% volatility, compared with
15.3% at 18.1% for Ridge. Top-decile Sharpe was nearly the same at 0.87 and
0.88. There is more separation at the other end. The lowest LightGBM decile
earned 0.6% a year, versus 2.4% for Ridge. The top-minus-bottom spread also
had lower realized volatility under LightGBM.

<div class="research-table-scroll" tabindex="0" role="region" aria-label="Top-minus-bottom spread metrics">
<table id="table-2" class="research-table comparison-table risk-performance-table">
  <caption><span class="caption-number">Table 2.</span> <span class="caption-title">Top-minus-bottom decile spread before costs.</span> Returns and volatility are annualized.</caption>
  <thead><tr><th scope="col">Model</th><th scope="col">Return</th><th scope="col">Volatility</th><th scope="col">Sharpe</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="colgroup">1999–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>7.6%</td><td>19.5%</td><td>0.47</td></tr>
    <tr><th scope="row">LightGBM</th><td>15.4%</td><td>14.8%</td><td>1.04</td></tr>
    <tr class="period-heading"><th colspan="4" scope="colgroup">2017–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>4.1%</td><td>21.0%</td><td>0.30</td></tr>
    <tr><th scope="row">LightGBM</th><td>8.8%</td><td>14.7%</td><td>0.65</td></tr>
  </tbody>
</table>
</div>

I form the spread from the two deciles' daily returns and then compound it.
That puts the higher recent Ridge IC in context. LightGBM had the stronger
spread over 2017–2021 even when Ridge's scores had the higher mean correlation
across all names.

## Returns after portfolio construction

The optimized books start from the 75 highest and 75 lowest scores. A common
risk target, gross and beta constraints, and an order limit of 10% of prior
21-session average daily dollar volume govern the weights and fills. I use
the turnover penalties chosen with each model, 2.5 basis points for Ridge and
5 basis points for LightGBM. The simulated fees are shared, at 7.5 and 10 basis
points per executed dollar on the long and short sides through 2010, then 5
and 7.5 basis points.

<div class="research-table-scroll" tabindex="0" role="region" aria-label="Constructed portfolio metrics">
<table id="table-3" class="research-table comparison-table risk-performance-table">
  <caption><span class="caption-number">Table 3.</span> <span class="caption-title">Long–short performance after execution fees.</span> I calculate compounded annual return, volatility and zero-cash Sharpe for each schedule, then average the three statistics over matching dates.</caption>
  <thead><tr><th scope="col">Model</th><th scope="col">Net return</th><th scope="col">Volatility</th><th scope="col">Net Sharpe</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="colgroup">1999–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>10.7%</td><td>8.7%</td><td>1.21</td></tr>
    <tr><th scope="row">LightGBM</th><td>16.9%</td><td>7.5%</td><td>2.12</td></tr>
    <tr class="period-heading"><th colspan="4" scope="colgroup">1999–2011</th></tr>
    <tr><th scope="row">Ridge</th><td>9.9%</td><td>7.9%</td><td>1.22</td></tr>
    <tr><th scope="row">LightGBM</th><td>17.7%</td><td>7.1%</td><td>2.34</td></tr>
    <tr class="period-heading"><th colspan="4" scope="colgroup">2012–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>11.8%</td><td>9.7%</td><td>1.20</td></tr>
    <tr><th scope="row">LightGBM</th><td>15.9%</td><td>8.1%</td><td>1.87</td></tr>
    <tr class="period-heading"><th colspan="4" scope="colgroup">2017–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>12.3%</td><td>10.6%</td><td>1.15</td></tr>
    <tr><th scope="row">LightGBM</th><td>14.8%</td><td>8.9%</td><td>1.60</td></tr>
  </tbody>
</table>
</div>

## Extending the comparison to Kumo

Kumo Tabular Small and Large approach the same prediction problem through
in-context learning. They receive historical labeled rows as context at
inference. I would take that context from an expanding history, using only
labels available at each refit. Thinning the dates and keeping the upper and
lower 30% of mature targets on those dates reduces the size of the context.
It also changes the target distribution the model sees, so that choice belongs
in the interpretation of a Kumo result. This preview covers the two baselines
while the Kumo evaluation is pending. [Kumo Tabular technical report](https://arxiv.org/abs/2611.23001v1)

The Ridge and LightGBM results show why I want all three views of a score.
The daily IC compares the whole ordering, the deciles show what happens at
the tails, and the constructed book incorporates the weights and fees paid
to trade them. Here the difference was already visible in the equal-weight
spread. The optimized comparison then shows how much of it survived in two
specified portfolio recipes. These are historical comparisons on the
development period.
