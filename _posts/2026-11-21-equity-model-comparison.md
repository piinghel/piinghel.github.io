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

Suppose I’m looking at two stocks. One has stronger momentum, the other
is cheaper. For earlier dates I can see how stocks with similar
characteristics did over the following month. For the two stocks in front
of me, that outcome is still blank. NVIDIA Kumo Tabular is a pretrained
machine learning model that uses rows with known outcomes to make
predictions for the rows where those outcomes are missing.

I wanted to try it on the 80 predictors from the linear model study.
The panel can have millions of stock-date rows and still cover relatively
few independent return periods. Stocks move together, and adjacent
20-session outcome windows overlap. A model that has already learned to
read other tables might pick up a relationship that Ridge or LightGBM
misses when it learns from the equity data alone. An unfamiliar
relationship is useful only if it helps me rank stocks, or gives me a
different set of positions that earns its place after costs.
[Combining Multiple Predictors]({% link _posts/2025-02-09-combining-predictors.md %})

## A pretrained model for tables

Think of a table with two characteristics and an outcome. In one
simulated table, the outcome might increase when both characteristics
are high. In another, the relationship might reverse once the first
characteristic crosses a threshold. During pretraining, Kumo sees
millions of artificial tables with different relationships. It learns
to infer the missing outcomes in each table from the examples it can see.

In this study, each row is a stock on a date. Its outcome is the stock’s
forward 20-session Sharpe ratio, ranked against its sector peers. At each
refit I supply historical rows whose outcomes have already materialized.
These examples are the context. Kumo uses them to score the next
cross-section with its pretrained weights held fixed. That is what
in-context learning means here.

Some of the work that got me interested came from Europe. TabPFN grew
out of research in Freiburg, and TabICL came from researchers at Inria
in France. The first TabPFN was designed for small classification
problems. NVIDIA now reports that Kumo can handle tables of up to
150 million cells on modern GPUs and that its Large checkpoint leads
its TabArena and BeyondArena comparisons. [NVIDIA’s Kumo Tabular report](https://arxiv.org/abs/2611.23001v1)

Christoph Molnar sets out two ways this could matter. A pretrained model
may beat the usual tree model out of the box, or it may make a useful
second forecast because it makes different errors. Those are the two
questions I bring to the equity panel. Can Kumo improve on LightGBM’s
stock rankings? How differently do the scores and portfolios behave?
I use Ridge, which combines the predictors with shrunk linear weights,
and LightGBM, which learns rules from a sequence of decision trees.
[Christoph Molnar, The rise of tabular foundation models](https://mindfulmodeler.substack.com/p/tabular-ml-is-about-to-get-weird)

## Ranking the whole cross-section

The main comparison covers 1999–2021. I score every eligible stock on
the combined signal dates from three staggered portfolio schedules.
Each schedule rebalances roughly every three weeks, giving about one
signal date a week across the three. For Kumo Small, each of the 12
training contexts expands from January 1995. I take
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
Kumo trails both baselines in 2017–2021.

## Return and risk by score decile

I sort the eligible stocks into ten equal-weight deciles on each rebalance
date and trade at the next close. I keep decile membership until the next
rebalance and average the daily returns across the three schedules before
compounding.

<figure id="figure-1" class="research-figure responsive-figure">
  <div id="figure-2">
    {% include theme-svg-figure.html base="/assets/equity-model-comparison/scheduled-decile-profile" mobile="/assets/equity-model-comparison/scheduled-decile-profile_mobile" version="2" alt="LightGBM has the highest top-decile return and Sharpe. Kumo Small and Ridge have similar top-decile returns." %}
  </div>
  <figcaption class="figure-caption"><span class="caption-number">Figure 1.</span> <span class="caption-title">Return, volatility and Sharpe by score decile, 1999–2021.</span> Decile 10 holds the highest scores. All deciles are equal-weighted and shown before costs.</figcaption>
</figure>

Kumo Small and Ridge look similar in the top decile. The LightGBM curve
separates at both ends, with a higher return at the top and a lower
return at the bottom. The top-minus-bottom spread compounds the
difference between those two deciles' daily returns.

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
statistic separately on the three schedules and average them.

<div id="table-5">
<div id="table-6" class="research-table-scroll" tabindex="0" role="region" aria-label="Gross decile spreads and portfolios after execution fees">
<table id="table-2" class="research-table comparison-table equity-comparison-table">
  <caption><span class="caption-number">Table 2.</span> <span class="caption-title">Gross decile spreads and net constructed portfolios.</span> All models use the same signal dates. Return, volatility and Sharpe are annualized.</caption>
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

## How similarly the models trade

Two scores can rank most stocks in the same order and still hold different
names at the ends. I compare the rankings on each signal date, then
compare the daily portfolio returns after fees. For the scores I average
the cross-sectional Spearman correlations. For the portfolios I compute
the Pearson correlation separately on each schedule and average the
three estimates.

<div class="research-table-scroll" tabindex="0" role="region" aria-label="Correlations between model scores and portfolio returns">
<table id="table-3" class="research-table comparison-table ic-summary-table">
  <caption><span class="caption-number">Table 3.</span> <span class="caption-title">Correlations between models, 1999–2021.</span> The estimates use 1,200 signal dates for rankings and 5,773 sessions for net returns.</caption>
  <thead><tr><th scope="col">Models</th><th scope="col">Rankings</th><th scope="col">Net returns</th></tr></thead>
  <tbody>
    <tr><th scope="row">Ridge and LightGBM</th><td>0.74</td><td>0.65</td></tr>
    <tr><th scope="row">Ridge and Kumo Small</th><td>0.53</td><td>0.55</td></tr>
    <tr><th scope="row">LightGBM and Kumo Small</th><td>0.55</td><td>0.54</td></tr>
  </tbody>
</table>
</div>

Kumo Small differs more from either baseline than the baselines differ
from each other. Those differences show up in the books as well as the
rankings. That is a reason to look at what the portfolio earns on each
side before drawing a conclusion about combining the models.

I split each day's net result into the long contribution, the signed
short contribution and execution fees. Annualizing the average daily
contributions makes the components add up. On that basis, LightGBM
earned 7.1 percentage points more per year than Kumo Small. The long
side contributed 3.2 points of the gap, the short side 2.7, and lower
execution fees 1.2. Against Ridge, higher trading fees explained about
two thirds of Kumo Small’s 1.8-point gap.

## Running Kumo on a Mac

I used a 16 GB M2 Pro Mac with a separate Python 3.12 environment. This
is the CPU setup I used, with the library and PyTorch versions pinned.

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install structured-data-models==0.3.0 torch==2.11.0
```

The first model load downloads the checkpoint. I cached the released
weights and reused them across runs. The support for Apple’s GPU
depended on the PyTorch and macOS versions. In my test with the older
GPU-compatible build, repeated runs gave different scores, so I ran the
comparison on CPU in 32-bit precision.

The first Small run hit the 10 GiB process limit with just 35,738
training examples. Limiting the temporary batches used to build the
row embeddings and compute attention brought that fold within budget.
Preparing the historical context was still the limiting step.
With one training date a week and the same target tails, the final fold
would have about 760,000 examples. Small’s main buffers alone would
need about 35 GiB in standard 32-bit precision. I sample training dates
further apart, prepare the context once per fold and reuse it across
prediction batches. Scoring on the portfolio schedules cuts the number
of predictions to about a fifth of daily scoring and keeps every eligible
stock on each scheduled date.

## What changed with more training rows

To see what changes with a denser context, I first scored every trading
day from January 1999 to September 2000. Taking every 15th training session
and keeping the two target tails gave Kumo Small 35,738 labeled rows.
The latest selected training date was August 5, 1998, and the first score
was in January 1999.

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
