---
layout: post
title: "Equity Model Comparison"
description: "Ridge, LightGBM and NVIDIA Kumo Tabular Small on the same stock universe, from rank IC to net portfolio returns."
date: 2026-11-21
last_modified_at: 2026-11-21
categories: ["Signals"]
article_label: Signals · Equity model comparison
permalink: /quants/equity-model-comparison.html
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
Each of three schedules rebalances every 15 sessions. Between rebalances I
keep the decile membership and average its stocks' daily returns. I average
the three schedules' daily returns before compounding and use zero cash return
for Sharpe.

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

## The first Kumo Small window

Kumo Tabular Small and Large approach the same prediction problem through
in-context learning. They receive historical labeled rows as context at
inference. For the first Small fold I took every 15th trading session of
training history. Among targets whose return windows had ended, I kept
the upper and lower 30% on those dates. That gave Kumo 35,738 labeled rows.
The latest selected training date was August 5, 1998, and the first score
was in January 1999. I scored every eligible stock using its features for
that date. [Kumo Tabular technical report](https://arxiv.org/abs/2611.23001v1)

<div class="research-table-scroll" tabindex="0" role="region" aria-label="First Kumo Small window, ranking and gross spread">
<table id="table-3" class="research-table comparison-table risk-performance-table">
  <caption><span class="caption-number">Table 3.</span> <span class="caption-title">January 1999–September 2000.</span> Rank statistics use 421 dates with realized targets. The gross top-minus-bottom spread statistics are annualized.</caption>
  <thead><tr><th scope="col">Model</th><th scope="col">IC</th><th scope="col">IC SD</th><th scope="col">ICIR</th><th scope="col">Return</th><th scope="col">Volatility</th><th scope="col">Sharpe</th></tr></thead>
  <tbody>
    <tr><th scope="row">Ridge</th><td>0.0491</td><td>0.070</td><td>0.70</td><td>18.7%</td><td>15.6%</td><td>1.18</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0723</td><td>0.071</td><td>1.01</td><td>52.0%</td><td>18.1%</td><td>2.41</td></tr>
    <tr><th scope="row">Kumo Small</th><td>0.0735</td><td>0.071</td><td>1.03</td><td>61.0%</td><td>22.4%</td><td>2.24</td></tr>
  </tbody>
</table>
</div>

Kumo Small and LightGBM had similar rank IC in this window. The difference
was 0.0012, with a paired 21-session block-bootstrap interval of roughly
−0.0044 to 0.0070. Kumo's gross spread returned more and took more risk.
LightGBM had the higher observed spread Sharpe. The Kumo results here cover
one early fold.

I also evaluated those same scores against the forward Sharpe ratio without
ranking the target by sector. On corrected closing prices, rank IC was
0.0812 for Kumo and 0.0822 for LightGBM, with ICIR of 0.75 and 0.84.
The small rank IC gap changes direction with the outcome definition.

## The expanding-window run

The three portfolio schedules give me a second way to choose scoring dates.
I score every eligible stock on their shared set of signal dates and
recompute Ridge and LightGBM's statistics on that same schedule. I expand
Kumo's training context from January 1995 using one date every 30 trading
sessions, keeping the two target tails as before. Across 12 refits, the
context grew from 18,148 to 126,892 rows. Scoring 1,162,773 stock observations
took about 99 minutes on a laptop CPU.

<div class="research-table-scroll" tabindex="0" role="region" aria-label="Matched expanding-window rank metrics for Ridge, LightGBM and Kumo Small">
<table id="table-4" class="research-table comparison-table ic-summary-table">
  <caption><span class="caption-number">Table 4.</span> <span class="caption-title">Rank metrics on the portfolio signal dates.</span> The full comparison has 1,191 dates with realized targets.</caption>
  <thead><tr><th scope="col">Model</th><th scope="col">IC</th><th scope="col">IC SD</th><th scope="col">ICIR</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="colgroup">1999–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0489</td><td>0.090</td><td>0.545</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0557</td><td>0.077</td><td>0.720</td></tr>
    <tr><th scope="row">Kumo Small</th><td>0.0430</td><td>0.064</td><td>0.671</td></tr>
    <tr class="period-heading"><th colspan="4" scope="colgroup">1999–2011</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0434</td><td>0.073</td><td>0.592</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0570</td><td>0.063</td><td>0.904</td></tr>
    <tr><th scope="row">Kumo Small</th><td>0.0470</td><td>0.059</td><td>0.795</td></tr>
    <tr class="period-heading"><th colspan="4" scope="colgroup">2012–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0560</td><td>0.107</td><td>0.523</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0541</td><td>0.093</td><td>0.582</td></tr>
    <tr><th scope="row">Kumo Small</th><td>0.0377</td><td>0.070</td><td>0.542</td></tr>
    <tr class="period-heading"><th colspan="4" scope="colgroup">2017–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0585</td><td>0.129</td><td>0.455</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0529</td><td>0.114</td><td>0.463</td></tr>
    <tr><th scope="row">Kumo Small</th><td>0.0347</td><td>0.083</td><td>0.421</td></tr>
  </tbody>
</table>
</div>

Across 1999–2021, Ridge has a higher mean IC than Kumo Small. Kumo's
lower IC variability gives it the higher ICIR. In 2017–2021, the drop in
Kumo's mean IC is enough to put its ICIR below both baselines.

<figure id="figure-2" class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/equity-model-comparison/scheduled-decile-profile" mobile="/assets/equity-model-comparison/scheduled-decile-profile_mobile" version="1" alt="LightGBM has the highest top-decile return and Sharpe. Kumo Small and Ridge have similar top-decile returns." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 2.</span> <span class="caption-title">The three scores on the shared trading schedules.</span> The deciles are equal-weighted. Return, volatility and Sharpe are shown before costs.</figcaption>
</figure>

<div class="research-table-scroll" tabindex="0" role="region" aria-label="Matched expanding-window gross spread metrics">
<table id="table-5" class="research-table comparison-table risk-performance-table">
  <caption><span class="caption-number">Table 5.</span> <span class="caption-title">Gross top-minus-bottom spread on the shared schedules.</span> Return, volatility and Sharpe are annualized.</caption>
  <thead><tr><th scope="col">Model</th><th scope="col">Return</th><th scope="col">Volatility</th><th scope="col">Sharpe</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="colgroup">1999–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>7.2%</td><td>19.6%</td><td>0.45</td></tr>
    <tr><th scope="row">LightGBM</th><td>16.8%</td><td>15.0%</td><td>1.11</td></tr>
    <tr><th scope="row">Kumo Small</th><td>9.4%</td><td>14.9%</td><td>0.68</td></tr>
    <tr class="period-heading"><th colspan="4" scope="colgroup">2017–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>4.4%</td><td>20.9%</td><td>0.31</td></tr>
    <tr><th scope="row">LightGBM</th><td>9.9%</td><td>14.5%</td><td>0.72</td></tr>
    <tr><th scope="row">Kumo Small</th><td>3.9%</td><td>16.3%</td><td>0.32</td></tr>
  </tbody>
</table>
</div>

Kumo's gross spread earns a Sharpe of 0.68 over the full sample, between
Ridge and LightGBM. Its full-sample Sharpe gap versus LightGBM is −0.43,
with a paired 21-session block-bootstrap interval from −0.78 to −0.10.
Kumo's spread Sharpe finishes close to Ridge in 2017–2021.

I can hold the first fold's scoring dates fixed to compare the training
samples. On the same 91 dates, Kumo's ICIR was 1.08 with three-week spacing,
0.91 with four weeks, and 0.62 with six weeks. The four-week context took
3 minutes 8 seconds to fit and score the fold, compared with 2 minutes
42 seconds at six weeks. A larger context helped in this fold.

Kumo Medium reached an ICIR of 0.72 on the same dates using the six-week
context. It took 6 minutes 25 seconds. In this window, increasing Small's
context from six-week to four-week spacing gave a larger ICIR gain for
less computation.

The scoring schedule made the bigger difference to runtime. It used
about one fifth of the predictions needed to score every daily
cross-section. Increasing the prediction batch size from 1,000 to 1,500
improved throughput by about 4% in a timing test on the first context.

## Returns after portfolio construction

The optimized books start from the 75 highest and 75 lowest scores. Each
schedule uses $5 million of simulated capital, a 7% annual volatility
target, and gross and beta limits. Measurable orders are capped at 10% of
prior 21-session average daily dollar volume. The simulation closes
positions with stopped quotes at their last observed price.

The optimizer prices trades against settled holdings. Its turnover penalty
is 2.5 basis points for Ridge and 5 basis points for LightGBM and Kumo Small.
I use the LightGBM portfolio recipe with Kumo scores.

The books share the same execution fees. Simulated long and short trades
pay 7.5 and 10 basis points per executed dollar through 2010, then 5 and 7.5
basis points. I compute compounded annual return, volatility and zero-cash
Sharpe separately for each schedule on matching dates and average the
three statistics.

<div class="research-table-scroll" tabindex="0" role="region" aria-label="Current-cost portfolio metrics">
<table id="table-6" class="research-table comparison-table risk-performance-table">
  <caption><span class="caption-number">Table 6.</span> <span class="caption-title">Long–short performance after execution fees.</span> All three models use the same rebalance schedules.</caption>
  <thead><tr><th scope="col">Model</th><th scope="col">Net return</th><th scope="col">Volatility</th><th scope="col">Net Sharpe</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="colgroup">1999–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>10.8%</td><td>8.7%</td><td>1.21</td></tr>
    <tr><th scope="row">LightGBM</th><td>16.9%</td><td>7.5%</td><td>2.12</td></tr>
    <tr><th scope="row">Kumo Small</th><td>8.9%</td><td>7.1%</td><td>1.24</td></tr>
    <tr class="period-heading"><th colspan="4" scope="colgroup">1999–2011</th></tr>
    <tr><th scope="row">Ridge</th><td>9.9%</td><td>8.0%</td><td>1.22</td></tr>
    <tr><th scope="row">LightGBM</th><td>17.7%</td><td>7.1%</td><td>2.35</td></tr>
    <tr><th scope="row">Kumo Small</th><td>9.9%</td><td>6.8%</td><td>1.42</td></tr>
    <tr class="period-heading"><th colspan="4" scope="colgroup">2012–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>11.9%</td><td>9.7%</td><td>1.22</td></tr>
    <tr><th scope="row">LightGBM</th><td>15.9%</td><td>8.0%</td><td>1.88</td></tr>
    <tr><th scope="row">Kumo Small</th><td>7.8%</td><td>7.5%</td><td>1.04</td></tr>
    <tr class="period-heading"><th colspan="4" scope="colgroup">2017–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>12.6%</td><td>10.5%</td><td>1.18</td></tr>
    <tr><th scope="row">LightGBM</th><td>14.9%</td><td>8.9%</td><td>1.60</td></tr>
    <tr><th scope="row">Kumo Small</th><td>7.0%</td><td>8.1%</td><td>0.88</td></tr>
  </tbody>
</table>
</div>

LightGBM's lead in the equal-weight spread carries through construction and
fees. Kumo Small and Ridge have similar net Sharpe over 1999–2021. Kumo
earned a lower return at lower volatility. Their net Sharpe difference
was 0.02, with a paired 21-session block-bootstrap interval from −0.30 to
0.32. From 2017–2021, Kumo trailed both baselines after fees.

These comparisons use the same archived development panel. The walk-forward
cutoff governs when each return outcome can enter a fit. Reproducing the
information available on each historical date would require dated input
vintages.
