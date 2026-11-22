---
layout: post
title: "Ranking Stocks with Kumo Tabular"
description: "Ridge, LightGBM and NVIDIA Kumo Tabular on the same stock universe, from rank IC to net portfolio returns."
date: 2026-11-21
last_modified_at: 2026-11-22
categories: ["Signals"]
article_label: Signals · Kumo Tabular
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
signal date a week across the three. For the two expanding Kumo runs,
each of the 12 contexts starts from January 1995. On the selected dates
I keep the top and bottom 30% of targets whose return windows have ended.

I used one date every 20 trading sessions for Small, about four weeks.
Its contexts grew from 26,960 to 190,064 rows. Medium used eight-week
spacing and grew from 13,459 to 95,033 rows. The two runs scored the same
1,162,773 stock-date rows. They took 2 hours 37 minutes and 2 hours 52
minutes on the Mac.

I also ran Small with weekly training dates inside a rolling window.
It starts with two years of history and grows to three. After that,
older dates drop out as the window moves forward. That run used
59,252 to 92,190 context rows and took 1 hour 58 minutes. All three
runs use the same signal dates and scoring universe.

On each signal date I compute the Spearman correlation between the scores
and realized targets. Rank IC is the mean of those correlations and ICIR
divides it by their sample standard deviation. I report ICIR unannualized.

<div id="table-4" class="research-table-scroll" tabindex="0" role="region" aria-label="Rank statistics on matched signal dates">
<table id="table-1" class="research-table comparison-table ic-summary-table">
  <caption><span class="caption-number">Table 1.</span> <span class="caption-title">Rank metrics by period.</span> The full comparison covers 1,191 shared signal dates with realized targets.</caption>
  <thead><tr><th scope="col">Model</th><th scope="col">IC</th><th scope="col">IC SD</th><th scope="col">ICIR</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="rowgroup">1999–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0489</td><td>0.090</td><td>0.545</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0557</td><td>0.077</td><td>0.720</td></tr>
    <tr><th scope="row">Kumo Small</th><td>0.0410</td><td>0.062</td><td>0.660</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>0.0458</td><td>0.073</td><td>0.625</td></tr>
    <tr><th scope="row">Small, rolling</th><td>0.0153</td><td>0.070</td><td>0.220</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="rowgroup">1999–2011</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0434</td><td>0.073</td><td>0.592</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0570</td><td>0.063</td><td>0.904</td></tr>
    <tr><th scope="row">Kumo Small</th><td>0.0493</td><td>0.059</td><td>0.842</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>0.0444</td><td>0.060</td><td>0.735</td></tr>
    <tr><th scope="row">Small, rolling</th><td>0.0258</td><td>0.067</td><td>0.384</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="rowgroup">2012–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0560</td><td>0.107</td><td>0.523</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0541</td><td>0.093</td><td>0.582</td></tr>
    <tr><th scope="row">Kumo Small</th><td>0.0301</td><td>0.065</td><td>0.465</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>0.0476</td><td>0.087</td><td>0.546</td></tr>
    <tr><th scope="row">Small, rolling</th><td>0.0016</td><td>0.071</td><td>0.023</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="rowgroup">2017–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0585</td><td>0.129</td><td>0.455</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0529</td><td>0.114</td><td>0.463</td></tr>
    <tr><th scope="row">Kumo Small</th><td>0.0284</td><td>0.078</td><td>0.366</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>0.0480</td><td>0.107</td><td>0.449</td></tr>
    <tr><th scope="row">Small, rolling</th><td>-0.0046</td><td>0.078</td><td>-0.059</td></tr>
  </tbody>
</table>
</div>

LightGBM's full-period lead in mean IC comes from 1999–2011. Ridge has
the higher mean in the recent windows. Its IC varies more across dates,
so LightGBM still has the higher ICIR. Across the full matched sample,
Kumo Small's lower IC variability puts its full-period ICIR above
Ridge's. Medium has a slightly higher mean IC than Small and more
variation from date to date, giving it a lower ICIR over the full
period. The two expanding Kumo runs compare the checkpoint sizes and
training cadences that fit the same laptop. Rolling Small had the
weakest rank IC in each period, and its mean IC was slightly negative
from 2017–2021.

## Return and risk by score decile

I sort the eligible stocks into ten equal-weight deciles on each rebalance
date and trade at the next close. I keep decile membership until the next
rebalance and average the daily returns across the three schedules before
compounding. Sharpe uses a zero cash return.

<figure id="figure-1" class="research-figure responsive-figure">
  <div id="figure-2">
    {% include theme-svg-figure.html base="/assets/equity-model-comparison/scheduled-decile-profile" mobile="/assets/equity-model-comparison/scheduled-decile-profile_mobile" version="5" alt="LightGBM has the highest top-decile return. Rolling Small has a flatter return profile with substantially higher returns in its lowest score deciles." %}
  </div>
  <figcaption class="figure-caption"><span class="caption-number">Figure 1.</span> <span class="caption-title">Return, volatility and Sharpe by score decile, 1999–2021.</span> Decile 10 holds the highest scores. All deciles are equal-weighted and shown before costs.</figcaption>
</figure>

LightGBM separates at both ends, with a higher return at the top and
a lower return at the bottom. The rolling variant is particularly weak
on the short side. Stocks in its lowest score decile earn nearly 10%
a year. The top-minus-bottom spread compounds the difference between
those two deciles' daily returns.

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
    <tr class="period-heading"><th colspan="7" scope="rowgroup">1999–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>7.2%</td><td>19.6%</td><td>0.45</td><td class="comparison-divider">10.8%</td><td>8.7%</td><td>1.21</td></tr>
    <tr><th scope="row">LightGBM</th><td>16.8%</td><td>15.0%</td><td>1.11</td><td class="comparison-divider">16.9%</td><td>7.5%</td><td>2.12</td></tr>
    <tr><th scope="row">Kumo Small</th><td>10.0%</td><td>15.2%</td><td>0.70</td><td class="comparison-divider">9.0%</td><td>7.1%</td><td>1.26</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>8.7%</td><td>14.0%</td><td>0.66</td><td class="comparison-divider">11.0%</td><td>7.4%</td><td>1.44</td></tr>
    <tr><th scope="row">Small, rolling</th><td>3.7%</td><td>13.6%</td><td>0.34</td><td class="comparison-divider">2.7%</td><td>7.6%</td><td>0.39</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="7" scope="rowgroup">1999–2011</th></tr>
    <tr><th scope="row">Ridge</th><td>7.9%</td><td>20.9%</td><td>0.47</td><td class="comparison-divider">9.9%</td><td>8.0%</td><td>1.22</td></tr>
    <tr><th scope="row">LightGBM</th><td>20.2%</td><td>16.4%</td><td>1.20</td><td class="comparison-divider">17.7%</td><td>7.1%</td><td>2.35</td></tr>
    <tr><th scope="row">Kumo Small</th><td>15.4%</td><td>15.9%</td><td>0.98</td><td class="comparison-divider">12.5%</td><td>6.7%</td><td>1.78</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>8.0%</td><td>14.2%</td><td>0.62</td><td class="comparison-divider">9.8%</td><td>6.9%</td><td>1.38</td></tr>
    <tr><th scope="row">Small, rolling</th><td>3.7%</td><td>16.1%</td><td>0.30</td><td class="comparison-divider">4.0%</td><td>7.6%</td><td>0.55</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="7" scope="rowgroup">2012–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>6.3%</td><td>17.8%</td><td>0.43</td><td class="comparison-divider">11.9%</td><td>9.7%</td><td>1.22</td></tr>
    <tr><th scope="row">LightGBM</th><td>12.6%</td><td>12.9%</td><td>0.99</td><td class="comparison-divider">15.9%</td><td>8.0%</td><td>1.88</td></tr>
    <tr><th scope="row">Kumo Small</th><td>3.4%</td><td>14.2%</td><td>0.31</td><td class="comparison-divider">4.6%</td><td>7.5%</td><td>0.64</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>9.6%</td><td>13.8%</td><td>0.73</td><td class="comparison-divider">12.5%</td><td>8.1%</td><td>1.50</td></tr>
    <tr><th scope="row">Small, rolling</th><td>3.8%</td><td>9.5%</td><td>0.44</td><td class="comparison-divider">1.1%</td><td>7.5%</td><td>0.18</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="7" scope="rowgroup">2017–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>4.4%</td><td>20.9%</td><td>0.31</td><td class="comparison-divider">12.6%</td><td>10.5%</td><td>1.18</td></tr>
    <tr><th scope="row">LightGBM</th><td>9.9%</td><td>14.5%</td><td>0.72</td><td class="comparison-divider">14.9%</td><td>8.9%</td><td>1.60</td></tr>
    <tr><th scope="row">Kumo Small</th><td>1.9%</td><td>17.7%</td><td>0.20</td><td class="comparison-divider">4.3%</td><td>8.1%</td><td>0.56</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>7.5%</td><td>17.0%</td><td>0.51</td><td class="comparison-divider">13.0%</td><td>9.0%</td><td>1.40</td></tr>
    <tr><th scope="row">Small, rolling</th><td>2.9%</td><td>11.3%</td><td>0.30</td><td class="comparison-divider">−0.6%</td><td>7.8%</td><td>-0.04</td></tr>
  </tbody>
</table>
</div>
</div>

LightGBM's lead in the equal-weight spread carries through construction
and fees. Small had the stronger gross decile spread of the two Kumo
models. Medium came out ahead after positions were sized and traded.
Its net Sharpe was still 0.69 below LightGBM's, with a paired 21-session
block-bootstrap interval for the difference from −0.99 to −0.40.

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
    <tr><th scope="row">Ridge and Kumo Small</th><td>0.46</td><td>0.52</td></tr>
    <tr><th scope="row">Ridge and Kumo Medium</th><td>0.60</td><td>0.55</td></tr>
    <tr><th scope="row">Ridge and Small, rolling</th><td>0.33</td><td>0.08</td></tr>
    <tr><th scope="row">LightGBM and Kumo Small</th><td>0.50</td><td>0.51</td></tr>
    <tr><th scope="row">LightGBM and Kumo Medium</th><td>0.71</td><td>0.67</td></tr>
    <tr><th scope="row">LightGBM and Small, rolling</th><td>0.35</td><td>0.12</td></tr>
    <tr><th scope="row">Kumo Small and Kumo Medium</th><td>0.50</td><td>0.57</td></tr>
    <tr><th scope="row">Kumo Small and Small, rolling</th><td>0.21</td><td>0.02</td></tr>
    <tr><th scope="row">Kumo Medium and Small, rolling</th><td>0.26</td><td>0.01</td></tr>
  </tbody>
</table>
</div>

Expanding Small’s rankings differ more from either baseline than the
baselines differ from each other. Medium’s rankings look closer to
LightGBM’s, and its portfolio returns move more closely with LightGBM’s
too. Rolling Small is different again. The correlation of its daily net
returns with expanding Small is about 0.02.

I split each day's net result into the long contribution, the signed
short contribution and execution fees. Annualizing the average daily
contributions makes the components add up. On that basis, LightGBM
earned 7.1 percentage points more per year than Kumo Small. The long
side contributed 3.3 points of the gap, the short side 2.4, and lower
execution fees 1.4. Medium earned about 1.8 points more than Small.
The long side added 1.5 points and lower fees added 0.9, with the short
side giving back 0.6.

## Running Kumo on a Mac

I started with Large because it had the best results in NVIDIA’s paper.
Getting the weights to load was straightforward. The first equity fold
was where I got stuck. Large hit the 10 GiB memory limit I had set on my
16 GB Mac. Small did too, even with only 35,738 training rows. I was able
to get both through that fold by making the temporary batches smaller
while Kumo prepared the historical examples. The CPU setup that worked
used Python 3.12, `structured-data-models` 0.3.0 and PyTorch 2.11.

That solved the first fold. For the full walk-forward test, the last
fold was a better guide. At one training date a week, it would have
about 760,000 rows even after keeping only the target tails. In 32-bit
precision, Small’s main buffers alone would take about 35 GiB. Large
would exceed my memory budget in the last fold even with the six-week
spacing used for Small. I could include Large in the first-fold test.
Running it through 2021 would have required a different setup.

The biggest saving came from scoring only when one of the portfolios
needed a ranking. That cut predictions to about a fifth of the daily
total while keeping all eligible stocks on each signal date. I then
spread the training dates further apart and reused each prepared context
for every batch in its fold. That left enough room to run the expanding
comparison and ask whether giving Kumo more history actually helped.

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
block-bootstrap interval for the difference was −0.23 to 0.06.

Over all 12 folds, moving from six-week to four-week dates took Small
from about 99 minutes to 2 hours 37 minutes. ICIR moved from 0.67 to
0.66 and net Sharpe from 1.24 to 1.26. The paired intervals included zero
for both differences. The near tie covers two different periods. Net
Sharpe rose from 1.42 to 1.78 through 2011 and fell from 1.04 to 0.64
after 2011. Four-week Small’s scores were less correlated with
LightGBM’s, 0.50 versus 0.55.

## The shorter history changed what Kumo picked

I tried the rolling window because relationships in equities can
change. Weekly dates give Kumo more examples of the recent market.
Letting older observations fall out gives those recent examples more
weight in the context. Here the comparison changes both the age of
the examples and how often I sample them.

The rolling model’s rankings were less correlated with Ridge and
LightGBM. Its own ICIR fell by 0.44 versus four-week expanding Small,
with a paired 21-session interval from −0.58 to −0.30. The after-fee
Sharpe fell by 0.87, with an interval from −1.39 to −0.36. The gross
spread was quieter and had a higher gross Sharpe after 2012, while
the constructed rolling book earned less per unit of risk in every
reported period.

The short book explains most of the difference. The rolling variant
gave up 5.9 percentage points of annualized arithmetic net P&L versus
four-week Small. The short side cost 5.6 points more, the long side
earned 0.7 points less, and lower fees recovered 0.4 points. The
rolling context produced more distinct positions and a weaker
standalone portfolio.
