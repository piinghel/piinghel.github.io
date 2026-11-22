---
layout: post
interactive_charts: true
title: "Can Tabular Foundation Models Rank Stocks?"
description: "Ridge, LightGBM and NVIDIA Kumo Tabular on the same stock universe, from rank IC to net portfolio returns."
date: 2026-11-21
last_modified_at: 2026-11-22
categories: ["Signals"]
article_label: Signals · Tabular models
permalink: /quants/equity-model-comparison.html
---

NVIDIA pretrained Kumo Tabular entirely on synthetic tables. I wanted
to see whether that training could carry over to ranking real stocks,
where the signal is weak and adjacent return windows overlap.
[NVIDIA’s Kumo Tabular report](https://arxiv.org/abs/2611.23001v1)

I compared Kumo with Ridge and LightGBM using the same 80 stock
predictors. The test starts with the rankings and follows them through
portfolio construction and trading costs.
[How I combine the stock predictors]({% link _posts/2025-02-09-combining-predictors.md %})

## A pretrained model for tables

Each row in the study is a stock on a date. The outcome is its Sharpe
ratio over the next 20 trading sessions, ranked against other stocks in
its sector. The sketch uses momentum as the only predictor. On session
55, I know stock C’s momentum. Its sector rank is still a question mark.

LightGBM’s `fit` learns tree splits and leaf values from the labeled
rows A and B. When C arrives, its momentum goes through those fitted
trees. Kumo’s `fit` prepares A and B for reuse with the pretrained
weights fixed. At prediction time, Kumo uses C’s momentum and the
labeled examples together. Change the examples and C’s score can change
with the same weights. That’s in-context learning.

During pretraining, Kumo repeatedly predicted hidden outcomes from
labeled rows in artificial tables. A predictor that mattered in one
table might carry little signal in the next. Kumo had to infer what
mattered from each table’s examples. In the backtest those examples are
real stock-date rows with known outcomes.
[Molnar’s chapter on pretraining](https://tabularfoundationmodels.com/pretraining)

<figure id="figure-1" class="research-figure responsive-figure stock-scoring-figure">
  <picture>
    <source media="(max-width: 600px)" srcset="{{ '/assets/equity-model-comparison/in-context-sketch-mobile.webp' | relative_url }}" width="1024" height="1536">
    <img src="{{ '/assets/equity-model-comparison/in-context-sketch.webp' | relative_url }}" width="1536" height="1024" loading="lazy" decoding="async" alt="LightGBM fits trees on labeled stocks A and B, then scores C from its momentum. Kumo scores C with A and B as context. The label cutoff is session 50, the context refresh is 51, the forecast is 55, and the simulated trade is 56.">
  </picture>
  <figcaption class="figure-caption"><span class="caption-number">Figure 1.</span> <span class="caption-title">How LightGBM and Kumo score a stock.</span> The sketch draws on Christoph Molnar’s explanation of prediction inputs in <a href="https://tabularfoundationmodels.com/prediction#fig-input-output"><em>Tabular Foundation Models</em>, Figure 4.2</a>.</figcaption>
</figure>

Stock B’s outcome is known at session 50, in time for the context
refresh at 51. The forecast at 55 reuses that context, and the
simulated trade takes place at the next close.

## Subsampling the historical context

At each of the 12 context refreshes, Kumo can use historical rows whose
full 20-session outcomes are known before the first forecast. The
expanding samples start in January 1995. I cut the context to fit in
memory in two steps.

First I choose historical dates from a fixed grid of trading sessions.
One Small run takes every 20th session, the other every 30th. In the
figure, the two grids share sessions 0 and 60. The four-week grid also
uses 20 and 40, while the six-week grid uses 30. A denser grid changes
which dates Kumo sees as well as how many.

On each selected date I sort the eligible stocks by their realized
target and keep roughly the bottom and top 30%. With ten stocks and
distinct outcomes, that means keeping three at each end and leaving
four in the middle. I wanted the examples to emphasize the strong and
weak outcomes that matter for long and short selection.

<figure id="figure-2" class="research-figure responsive-figure">
  <div class="context-sampling" role="img" aria-label="The 20-session grid selects historical sessions 0, 20, 40 and 60. The 30-session grid selects 0, 30 and 60. On each selected date, ten stocks are sorted by realized outcome. The lowest three and highest three are kept, and the middle four are skipped.">
    <div aria-hidden="true">
      <div class="context-sampling-heading">Historical dates</div>
      <div class="context-sampling-dates">
        <span>Session</span>
        {% for tick in (0..6) %}
          <span>{{ tick | times: 10 }}</span>
        {% endfor %}
        {% for step in (2..3) %}
          <span>Every {{ step | times: 10 }}</span>
          {% for tick in (0..6) %}
            {% assign remainder = tick | modulo: step %}
            <span class="context-sampling-mark{% if remainder == 0 %} kept{% endif %}"></span>
          {% endfor %}
        {% endfor %}
      </div>
    </div>
    <div aria-hidden="true">
      <div class="context-sampling-heading">Stocks on one selected date</div>
      <div class="context-sampling-stocks">
        <div>
          <span>Lowest 30%</span>
          <div class="context-sampling-marks">
            {% for stock in (1..3) %}<span class="context-sampling-mark kept"></span>{% endfor %}
          </div>
        </div>
        <div>
          <span>Middle 40%</span>
          <div class="context-sampling-marks">
            {% for stock in (1..4) %}<span class="context-sampling-mark"></span>{% endfor %}
          </div>
        </div>
        <div>
          <span>Highest 30%</span>
          <div class="context-sampling-marks">
            {% for stock in (1..3) %}<span class="context-sampling-mark kept"></span>{% endfor %}
          </div>
        </div>
      </div>
    </div>
  </div>
  <figcaption class="figure-caption"><span class="caption-number">Figure 2.</span> <span class="caption-title">Which historical rows enter Kumo’s context.</span> Filled marks show the dates and stocks selected in this example.</figcaption>
</figure>

## Ranking the whole cross-section

Every Kumo run scores the same 1,162,773 stock-date rows over 1999–2021,
covering all eligible stocks on each signal date. Three staggered
portfolios each rebalance roughly every three weeks, giving about one
signal date a week across the three.

In the final fold, four-week Small used 190,064 labeled rows and
six-week Small used 126,892. Their full runs took 2 hours 37 minutes and
1 hour 39 minutes, respectively. Medium needed eight-week spacing to
fit in memory and ran in 2 hours 52 minutes.

I also ran Small with weekly historical dates in a shorter window. It
starts at two years and grows to three, then drops older dates as it
rolls forward. That run took just under two hours.

On each signal date I compare the model's ranking with the realized
ranking using Spearman correlation. Rank IC is the average correlation.
ICIR divides that average by how much the correlation varies across
dates, measured by its sample standard deviation. I leave ICIR
unannualized.

<div id="table-4" class="research-table-scroll" tabindex="0" role="region" aria-label="Rank statistics on matched signal dates">
<table id="table-1" class="research-table comparison-table ic-summary-table">
  <caption><span class="caption-number">Table 1.</span> <span class="caption-title">Rank metrics by period.</span> The full comparison covers 1,191 shared signal dates with realized targets.</caption>
  <thead><tr><th scope="col">Model</th><th scope="col">IC</th><th scope="col">IC SD</th><th scope="col">ICIR</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="rowgroup">1999–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0489</td><td>0.090</td><td>0.545</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0557</td><td>0.077</td><td>0.720</td></tr>
    <tr><th scope="row">Small, 4 weeks</th><td>0.0410</td><td>0.062</td><td>0.660</td></tr>
    <tr><th scope="row">Small, 6 weeks</th><td>0.0430</td><td>0.064</td><td>0.671</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>0.0458</td><td>0.073</td><td>0.625</td></tr>
    <tr><th scope="row">Small, rolling</th><td>0.0153</td><td>0.070</td><td>0.220</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="rowgroup">1999–2011</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0434</td><td>0.073</td><td>0.592</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0570</td><td>0.063</td><td>0.904</td></tr>
    <tr><th scope="row">Small, 4 weeks</th><td>0.0493</td><td>0.059</td><td>0.842</td></tr>
    <tr><th scope="row">Small, 6 weeks</th><td>0.0470</td><td>0.059</td><td>0.795</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>0.0444</td><td>0.060</td><td>0.735</td></tr>
    <tr><th scope="row">Small, rolling</th><td>0.0258</td><td>0.067</td><td>0.384</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="rowgroup">2012–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0560</td><td>0.107</td><td>0.523</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0541</td><td>0.093</td><td>0.582</td></tr>
    <tr><th scope="row">Small, 4 weeks</th><td>0.0301</td><td>0.065</td><td>0.465</td></tr>
    <tr><th scope="row">Small, 6 weeks</th><td>0.0377</td><td>0.070</td><td>0.542</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>0.0476</td><td>0.087</td><td>0.546</td></tr>
    <tr><th scope="row">Small, rolling</th><td>0.0016</td><td>0.071</td><td>0.023</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="4" scope="rowgroup">2017–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>0.0585</td><td>0.129</td><td>0.455</td></tr>
    <tr><th scope="row">LightGBM</th><td>0.0529</td><td>0.114</td><td>0.463</td></tr>
    <tr><th scope="row">Small, 4 weeks</th><td>0.0284</td><td>0.078</td><td>0.366</td></tr>
    <tr><th scope="row">Small, 6 weeks</th><td>0.0347</td><td>0.083</td><td>0.421</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>0.0480</td><td>0.107</td><td>0.449</td></tr>
    <tr><th scope="row">Small, rolling</th><td>-0.0046</td><td>0.078</td><td>-0.059</td></tr>
  </tbody>
</table>
</div>

All three expanding Kumo runs had positive rank IC in every period shown.
That’s what surprised me about a model pretrained on artificial tables.
LightGBM's full-period lead in mean IC comes from 1999–2011. Ridge has
the higher mean in the recent windows. Its IC varies more across dates,
so LightGBM still has the higher ICIR. Across the full matched sample,
both expanding Small runs have a higher full-period ICIR than Ridge
because their IC varies less. Medium has a higher mean IC than either
expanding Small run and more variation from date to date, giving it a
lower full-period ICIR. Rolling Small had the
weakest rank IC in each period, and its mean IC was slightly negative
from 2017–2021.

## Return and risk by score decile

Rank IC describes the whole cross-section. For a long-short portfolio
I'm especially interested in what happens at the ends. I sort each day's
scores into ten equal-weight groups, trade at the next close, and hold
until the next rebalance. I average daily returns across the three
schedules before compounding and use a zero cash return for Sharpe.

<figure id="figure-3" class="research-figure decile-profile-figure responsive-figure">
  {% include blog-chart.html chart="profiles" source="/assets/equity-model-comparison/deciles.json?v=2" base="/assets/equity-model-comparison/scheduled-decile-profile" mobile="/assets/equity-model-comparison/scheduled-decile-profile_mobile" version="7" label="Return, volatility and Sharpe by stock score decile, with selectable periods and models." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 3.</span> <span class="caption-title">Return, volatility and Sharpe by score decile.</span> Decile 10 holds the highest scores. All deciles are equal-weighted and shown before costs.</figcaption>
</figure>

LightGBM separates at both ends, with a higher return at the top and
a lower return at the bottom. The rolling variant is particularly weak
on the short side. Stocks in its lowest score decile earn nearly 10%
a year. The top-minus-bottom spread compounds the difference between
those two deciles' daily returns.

## Returns after portfolio construction

To see what I'd get after sizing and paying for trades, I build
long-short portfolios from the 75 highest and 75 lowest scores. Each
schedule uses $5 million of simulated capital, a 7% annual volatility
target, and limits on gross exposure and market beta. Where I can
measure liquidity, I cap trades at 10% of the previous 21 sessions'
average daily dollar volume.

I use LightGBM's construction settings for the Kumo books, including a
5 basis point turnover penalty. Ridge uses its original 2.5 basis point
penalty. In the trading simulation, long and short trades cost 7.5 and
10 basis points through 2010, then 5 and 7.5. The net results in Table 2
average the statistic from each of the three schedules.

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
    <tr><th scope="row">Small, 4 weeks</th><td>10.0%</td><td>15.2%</td><td>0.70</td><td class="comparison-divider">9.0%</td><td>7.1%</td><td>1.26</td></tr>
    <tr><th scope="row">Small, 6 weeks</th><td>9.4%</td><td>14.9%</td><td>0.68</td><td class="comparison-divider">8.9%</td><td>7.1%</td><td>1.24</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>8.7%</td><td>14.0%</td><td>0.66</td><td class="comparison-divider">11.0%</td><td>7.4%</td><td>1.44</td></tr>
    <tr><th scope="row">Small, rolling</th><td>3.7%</td><td>13.6%</td><td>0.34</td><td class="comparison-divider">2.7%</td><td>7.6%</td><td>0.39</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="7" scope="rowgroup">1999–2011</th></tr>
    <tr><th scope="row">Ridge</th><td>7.9%</td><td>20.9%</td><td>0.47</td><td class="comparison-divider">9.9%</td><td>8.0%</td><td>1.22</td></tr>
    <tr><th scope="row">LightGBM</th><td>20.2%</td><td>16.4%</td><td>1.20</td><td class="comparison-divider">17.7%</td><td>7.1%</td><td>2.35</td></tr>
    <tr><th scope="row">Small, 4 weeks</th><td>15.4%</td><td>15.9%</td><td>0.98</td><td class="comparison-divider">12.5%</td><td>6.7%</td><td>1.78</td></tr>
    <tr><th scope="row">Small, 6 weeks</th><td>11.8%</td><td>15.7%</td><td>0.79</td><td class="comparison-divider">9.9%</td><td>6.8%</td><td>1.42</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>8.0%</td><td>14.2%</td><td>0.62</td><td class="comparison-divider">9.8%</td><td>6.9%</td><td>1.38</td></tr>
    <tr><th scope="row">Small, rolling</th><td>3.7%</td><td>16.1%</td><td>0.30</td><td class="comparison-divider">4.0%</td><td>7.6%</td><td>0.55</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="7" scope="rowgroup">2012–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>6.3%</td><td>17.8%</td><td>0.43</td><td class="comparison-divider">11.9%</td><td>9.7%</td><td>1.22</td></tr>
    <tr><th scope="row">LightGBM</th><td>12.6%</td><td>12.9%</td><td>0.99</td><td class="comparison-divider">15.9%</td><td>8.0%</td><td>1.88</td></tr>
    <tr><th scope="row">Small, 4 weeks</th><td>3.4%</td><td>14.2%</td><td>0.31</td><td class="comparison-divider">4.6%</td><td>7.5%</td><td>0.64</td></tr>
    <tr><th scope="row">Small, 6 weeks</th><td>6.5%</td><td>13.7%</td><td>0.52</td><td class="comparison-divider">7.8%</td><td>7.5%</td><td>1.04</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>9.6%</td><td>13.8%</td><td>0.73</td><td class="comparison-divider">12.5%</td><td>8.1%</td><td>1.50</td></tr>
    <tr><th scope="row">Small, rolling</th><td>3.8%</td><td>9.5%</td><td>0.44</td><td class="comparison-divider">1.1%</td><td>7.5%</td><td>0.18</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="7" scope="rowgroup">2017–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>4.4%</td><td>20.9%</td><td>0.31</td><td class="comparison-divider">12.6%</td><td>10.5%</td><td>1.18</td></tr>
    <tr><th scope="row">LightGBM</th><td>9.9%</td><td>14.5%</td><td>0.72</td><td class="comparison-divider">14.9%</td><td>8.9%</td><td>1.60</td></tr>
    <tr><th scope="row">Small, 4 weeks</th><td>1.9%</td><td>17.7%</td><td>0.20</td><td class="comparison-divider">4.3%</td><td>8.1%</td><td>0.56</td></tr>
    <tr><th scope="row">Small, 6 weeks</th><td>3.9%</td><td>16.3%</td><td>0.32</td><td class="comparison-divider">7.0%</td><td>8.1%</td><td>0.88</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>7.5%</td><td>17.0%</td><td>0.51</td><td class="comparison-divider">13.0%</td><td>9.0%</td><td>1.40</td></tr>
    <tr><th scope="row">Small, rolling</th><td>2.9%</td><td>11.3%</td><td>0.30</td><td class="comparison-divider">−0.6%</td><td>7.8%</td><td>-0.04</td></tr>
  </tbody>
</table>
</div>
</div>

LightGBM's lead in the equal-weight spread carries through construction
and fees. Both expanding Small runs had higher gross spread Sharpe than
Medium. Medium came out ahead of both after positions were sized and traded.
Medium's net Sharpe trailed LightGBM's by 0.69. Resampling the two
portfolios together in 21-session blocks gives an interval of −0.99 to
−0.40 for the difference.

## How similarly the models trade

I also wanted to know whether Kumo was finding different trades. Two
models can agree on most of the ranking and still choose different
stocks at the ends. The left matrix averages rank correlations across
signal dates. The right one shows how the net daily returns move
together, averaging the Pearson correlations from the three schedules.

<div role="group" aria-labelledby="table-3">
  <p id="table-3" class="table-caption"><span class="caption-number">Table 3.</span> <span class="caption-title">Correlations between models, 1999–2021.</span> Rankings use 1,200 signal dates. Net returns use 5,773 trading sessions.</p>
  {% include equity-correlation-matrices.html %}
</div>

Expanding Small’s rankings differ more from either baseline than the
baselines differ from each other. Medium’s rankings look closer to
LightGBM’s, and its portfolio returns move more closely with LightGBM’s
too. Rolling Small is different again. The correlation of its daily net
returns with four-week Small is about 0.02.

I split each day's net result into the long contribution, the signed
short contribution and execution fees. Annualizing the average daily
contributions makes the components add up. On that basis, LightGBM
earned 7.1 percentage points more per year than four-week Small. The long
side contributed 3.3 points of the gap, the short side 2.4, and lower
execution fees 1.4. Medium earned about 1.8 points more than four-week Small.
The long side added 1.5 points and lower fees added 0.9, with the short
side giving back 0.6.

## Running Kumo on a Mac

I ran Kumo on the 10-core Apple M2 Pro CPU of my 14-inch MacBook Pro
(2023), with 16 GB of unified memory. I started with Large because it
had the best results in NVIDIA’s paper. Large and Small both hit my
10 GiB memory limit in the first fold, even with 35,738 context rows
for Small. Smaller batches during context preparation got both through.

With weekly historical dates, the final expanding fold would have
about 760,000 rows after the tail selection. Small’s main 32-bit
buffers alone would take about 35 GiB. I spaced the historical dates
farther apart and reused the prepared context across forecasts within
each fold. Large ran only in the first-fold comparison.

Scoring on the signal calendar cut the number of predictions to about
a fifth of the daily total. Each signal date still included the whole
eligible cross-section.

## What changed with more training rows

On the 91 matched signal dates in the first fold, Kumo Small's ICIR was
1.08 at three-week training spacing, 0.91 at four weeks, and 0.62 at six.
With the same six-week training dates, Medium reached 0.72 and Large
reached 0.79. Changing Small’s sampling grid moved ICIR more in that
fold than changing model size at six-week spacing.

By the final fold, four-week Small took 24 minutes and six-week Small
took 12½. The denser run's ICIR was 0.11 versus 0.21 for six weeks on
61 dates with realized targets.

Over all 12 folds, moving from six-week to four-week spacing took about
59% longer. The paired 21-session intervals for four weeks minus six
were −0.06 to 0.04 for ICIR and −0.21 to 0.23 for net Sharpe. The
full-period results were close. Four-week Small earned a higher net
Sharpe through 2011 and a lower one after 2011.

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
earned 0.7 points less, and lower fees recovered 0.4 points.

## How the P&L built up

I was surprised by how close Medium stayed to Ridge over the full
test. LightGBM pulled ahead early and kept adding to its lead.
At their original volatility, Ridge and Medium had each earned about
$244 per $100 of fixed capital by the end of 2021, and LightGBM had
earned about $365.

The chart opens with each portfolio rescaled to 7% annualized
volatility over the selected window. Clear the checkbox to see the
original P&L and drawdowns. Open **Window statistics** to compare
annual net P&L, volatility, Sharpe and drawdowns at either scale.

<figure id="figure-4" class="research-figure portfolio-path-figure responsive-figure">
  {% include blog-chart.html chart="pnl" source="/assets/equity-model-comparison/net-pnl.json?v=4" base="/assets/equity-model-comparison/net-pnl" mobile="/assets/equity-model-comparison/net-pnl_mobile" version="3" label="Cumulative net P&L and drawdown for Ridge, LightGBM and Kumo Medium, rescaled to 7% annualized volatility by default." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 4.</span> <span class="caption-title">Cumulative P&amp;L and drawdown after fees.</span> I sum the mean daily P&amp;L of the three schedules per $100 of fixed capital. Drawdown is the loss from the previous P&amp;L peak within the chosen window.</figcaption>
</figure>

At the same realized volatility over the full period, Medium earned
more than Ridge and had a smaller worst drawdown. LightGBM still earned
the most and had the smallest peak-to-trough loss of the three.

The result I’d most like to revisit is the effect of model size.
In the first fold, ranking improved from Small to Medium to Large
when I used the same training dates. Across the full test, the memory
limit forced me to use fewer dates for Medium, so I’m still curious
what a larger model would do with the same history.
