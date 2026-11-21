---
layout: post
title: "Equity Model Comparison"
description: "Ridge, LightGBM and NVIDIA Kumo Tabular on the same stock universe, from rank IC to net portfolio returns."
date: 2026-11-21
last_modified_at: 2026-11-22
categories: ["Signals"]
article_label: Signals · Equity model comparison
permalink: /quants/equity-model-comparison.html
---

I wanted to see whether a model pretrained on synthetic tables could rank
stocks using the same 80 predictors as Ridge and LightGBM. An equity panel
can have millions of rows while still giving you relatively few independent
return periods. Stocks move together, and adjacent 20-session targets
overlap. LightGBM learns its thresholds and interactions from that equity
history. Kumo arrives with a prior from pretraining and uses labeled rows
from the panel to make predictions at inference. I wanted to see how
well that prior transfers to a noisy equity target.
[Kumo Tabular technical report](https://arxiv.org/abs/2611.23001v1)

I start with the ranking across the whole stock universe, then look at the
two ends through equal-weight deciles and finally at returns after risk
constraints and trading costs. The predictors come from the
[linear comparison]({% link _posts/2025-02-09-combining-predictors.md %}).
The shared target is the forward 20-session Sharpe ratio, ranked within
sector on each date.

## Ranking the whole cross-section

The main comparison covers 1999–2021. I score every eligible stock on
the combined signal dates from the three weekly portfolio schedules. For Kumo
Small, each of the 12 training contexts expands from January 1995. I take
one date every 30 trading sessions and keep the top and bottom 30% of
targets whose return windows have ended. The context grows from 18,148
to 126,892 rows. Scoring 1,162,773 stock observations took 99 minutes on
a laptop CPU.

On each signal date I compute the Spearman correlation between the scores
and realized targets. Rank IC is the mean of those correlations and ICIR
divides it by their sample standard deviation. I report ICIR unannualized.

<div id="table-4" class="research-table-scroll" tabindex="0" role="region" aria-label="Rank statistics on matched signal dates">
<table id="table-1" class="research-table comparison-table ic-summary-table">
  <caption><span class="caption-number">Table 1.</span> <span class="caption-title">Rank metrics by period.</span> The full comparison covers 1,191 shared signal dates with realized targets.</caption>
  <thead><tr><th scope="col">Model</th><th scope="col">IC</th><th scope="col">IC SD</th><th scope="col">ICIR</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="colgroup">1999–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0489</td><td>0.090</td><td>0.545</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0557</td><td>0.077</td><td>0.720</td></tr>
    <tr><th scope="row">Kumo Small</th><td>0.0430</td><td>0.064</td><td>0.671</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="colgroup">1999–2011</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0434</td><td>0.073</td><td>0.592</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0570</td><td>0.063</td><td>0.904</td></tr>
    <tr><th scope="row">Kumo Small</th><td>0.0470</td><td>0.059</td><td>0.795</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="colgroup">2012–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0560</td><td>0.107</td><td>0.523</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0541</td><td>0.093</td><td>0.582</td></tr>
    <tr><th scope="row">Kumo Small</th><td>0.0377</td><td>0.070</td><td>0.542</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="colgroup">2017–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0585</td><td>0.129</td><td>0.455</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0529</td><td>0.114</td><td>0.463</td></tr>
    <tr><th scope="row">Kumo Small</th><td>0.0347</td><td>0.083</td><td>0.421</td></tr>
  </tbody>
</table>
</div>

LightGBM's full-period lead in mean IC comes from 1999–2011. Ridge has
the higher mean in the recent windows. Its IC varies more across dates,
so LightGBM still has the higher ICIR. Across the full matched sample,
Kumo Small's lower IC variability puts its ICIR above Ridge's, though
Kumo trails both baselines in 2017–2021. Using every daily date for Ridge
and LightGBM gives similar full-period ICIRs of 0.54 and 0.72.

## Return and risk by score decile

I sort the eligible stocks into ten equal-weight deciles on each rebalance
date and trade at the next close. I keep decile membership until the next
rebalance and average the daily returns across the three schedules before
compounding. The figure starts with the matched weekly schedules. The
15-session view shows the original Ridge and LightGBM deciles.

<figure id="figure-1" class="research-figure responsive-figure decile-schedule-figure">
  <fieldset id="figure-2" class="decile-schedule">
    <legend>Rebalance schedule</legend>
    <input type="radio" name="decile-schedule" id="deciles-weekly" checked>
    <label for="deciles-weekly">Weekly schedules</label>
    <input type="radio" name="decile-schedule" id="deciles-fifteen">
    <label for="deciles-fifteen">15-session schedules</label>
    <div class="decile-schedule-panel decile-schedule-weekly">
      {% include theme-svg-figure.html base="/assets/equity-model-comparison/scheduled-decile-profile" mobile="/assets/equity-model-comparison/scheduled-decile-profile_mobile" version="2" alt="On the weekly schedules, LightGBM has the highest top-decile return and Sharpe. Kumo Small and Ridge have similar top-decile returns." %}
    </div>
    <div class="decile-schedule-panel decile-schedule-fifteen">
      {% include theme-svg-figure.html base="/assets/equity-model-comparison/decile-profile" mobile="/assets/equity-model-comparison/decile-profile_mobile" version="2" alt="On 15-session schedules, LightGBM's top decile earns more at higher volatility than Ridge. Their top-decile Sharpes are nearly equal." %}
    </div>
  </fieldset>
  <figcaption class="figure-caption"><span class="caption-number">Figure 1.</span> <span class="caption-title">Return, volatility and Sharpe by score decile, 1999–2021.</span> Decile 10 holds the highest scores. Both views use equal-weight deciles before costs.</figcaption>
</figure>

On the 15-session schedules, LightGBM's top decile earns more at higher
volatility, leaving its Sharpe close to Ridge's. Their bottom deciles
separate more clearly. The broader advantage also shows up in the
weekly top-minus-bottom spread, which compounds the difference between
the two deciles' daily returns.

## Returns after portfolio construction

The optimized books start from the 75 highest and 75 lowest scores.
Each schedule uses $5 million of simulated capital, a 7% annual volatility
target, and gross and beta limits. Measurable orders are capped at 10% of
prior 21-session average daily dollar volume. Positions with stopped quotes
close at their last observed price.

The optimizer prices trades against settled holdings, with a turnover
penalty of 2.5 basis points for Ridge and 5 for LightGBM and Kumo. The Kumo
books use the LightGBM construction recipe. Simulated long and short
trades pay 7.5 and 10 basis points per executed dollar through 2010,
then 5 and 7.5 basis points. For the constructed books I compute each
statistic separately on the three weekly schedules and average them.

<div id="table-5">
<div id="table-6" class="research-table-scroll" tabindex="0" role="region" aria-label="Gross decile spreads and portfolios after execution fees">
<table id="table-2" class="research-table comparison-table equity-comparison-table">
  <caption><span class="caption-number">Table 2.</span> <span class="caption-title">Gross decile spreads and net constructed portfolios.</span> The main comparison uses the matched weekly schedules. Return, volatility and Sharpe are annualized.</caption>
  <colgroup span="1"></colgroup><colgroup span="3"></colgroup><colgroup span="3"></colgroup>
  <thead>
    <tr><th scope="col" rowspan="2">Model</th><th scope="colgroup" colspan="3">Gross decile spread</th><th scope="colgroup" colspan="3" class="comparison-divider">Net constructed book</th></tr>
    <tr><th scope="col">Return</th><th scope="col">Vol.</th><th scope="col">Sharpe</th><th scope="col" class="comparison-divider">Return</th><th scope="col">Vol.</th><th scope="col">Sharpe</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="7" scope="colgroup">1999–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>7.2%</td><td>19.6%</td><td>0.45</td><td class="comparison-divider">10.8%</td><td>8.7%</td><td>1.21</td></tr>
    <tr><th scope="row">LightGBM</th><td>16.8%</td><td>15.0%</td><td>1.11</td><td class="comparison-divider">16.9%</td><td>7.5%</td><td>2.12</td></tr>
    <tr><th scope="row">Kumo Small</th><td>9.4%</td><td>14.9%</td><td>0.68</td><td class="comparison-divider">8.9%</td><td>7.1%</td><td>1.24</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="7" scope="colgroup">1999–2011</th></tr>
    <tr><th scope="row">Ridge</th><td>7.9%</td><td>20.9%</td><td>0.47</td><td class="comparison-divider">9.9%</td><td>8.0%</td><td>1.22</td></tr>
    <tr><th scope="row">LightGBM</th><td>20.2%</td><td>16.4%</td><td>1.20</td><td class="comparison-divider">17.7%</td><td>7.1%</td><td>2.35</td></tr>
    <tr><th scope="row">Kumo Small</th><td>11.8%</td><td>15.7%</td><td>0.79</td><td class="comparison-divider">9.9%</td><td>6.8%</td><td>1.42</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="7" scope="colgroup">2012–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>6.3%</td><td>17.8%</td><td>0.43</td><td class="comparison-divider">11.9%</td><td>9.7%</td><td>1.22</td></tr>
    <tr><th scope="row">LightGBM</th><td>12.6%</td><td>12.9%</td><td>0.99</td><td class="comparison-divider">15.9%</td><td>8.0%</td><td>1.88</td></tr>
    <tr><th scope="row">Kumo Small</th><td>6.5%</td><td>13.7%</td><td>0.52</td><td class="comparison-divider">7.8%</td><td>7.5%</td><td>1.04</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="7" scope="colgroup">2017–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>4.4%</td><td>20.9%</td><td>0.31</td><td class="comparison-divider">12.6%</td><td>10.5%</td><td>1.18</td></tr>
    <tr><th scope="row">LightGBM</th><td>9.9%</td><td>14.5%</td><td>0.72</td><td class="comparison-divider">14.9%</td><td>8.9%</td><td>1.60</td></tr>
    <tr><th scope="row">Kumo Small</th><td>3.9%</td><td>16.3%</td><td>0.32</td><td class="comparison-divider">7.0%</td><td>8.1%</td><td>0.88</td></tr>
  </tbody>
</table>
</div>
</div>

LightGBM's lead in the equal-weight spread carries through construction
and fees. Kumo Small earned a lower net return than Ridge at lower
volatility. Their net Sharpe difference of 0.02 had a paired 21-session
block-bootstrap interval from −0.30 to 0.32. From 2017–2021, Kumo trailed
both baselines after fees.

## Kumo’s training context

To see what changes with a denser context, I first scored every trading
day from January 1999 to September 2000. Taking every 15th training session
and keeping the two target tails gave Kumo Small 35,738 labeled rows.
The latest selected training date was August 5, 1998, and the first score
was in January 1999.

<div id="table-3"></div>

Over these first 421 dates, ICIR was 1.03 for Kumo Small and 1.01 for
LightGBM. The rank IC difference was 0.0012,
with a paired 21-session block-bootstrap interval from −0.0044 to 0.0070.
The gap changed sign when I evaluated the same scores against the forward
Sharpe ratio before sector ranking. With that target, ICIR was 0.75 for
Kumo Small and 0.84 for LightGBM.

On the 91 matched signal dates in that first fold, Kumo Small's ICIR was
1.08 at three-week training spacing, 0.91 at four weeks, and 0.62 at six.
At six-week spacing, Medium reached 0.724 in 6 minutes 25 seconds and
Large reached 0.785 in 8 minutes 42 seconds. Their gross spread Sharpes
were 1.91 and 1.87, versus 2.66 for LightGBM on the same schedule. Moving
Small from six weeks to four gave a larger ICIR gain in that fold and
took 3 minutes 8 seconds.

In the final fold, from October 2020 through December 2021, four-week
spacing gave Small 190,064 context rows and took 24 minutes. Six-week
spacing used 126,892 rows and took 12½ minutes. On 61 dates with realized
targets, ICIR was 0.11 at four weeks and 0.21 at six. The paired 21-session
block-bootstrap interval for the difference was −0.23 to 0.06. Training
spacing changes which dates enter the context as well as how many.

These comparisons use the same archived development panel. The walk-forward
cutoff governs when each return outcome can enter a fit. Reproducing the
information available on each historical date would require dated input
vintages.
