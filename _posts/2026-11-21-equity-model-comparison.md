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

For years, boosted trees like LightGBM have been a standard choice for
prediction on tabular data. The setup is familiar. Fit the trees on
rows with known outcomes, then use the fitted trees to score a new row
from its predictors.

Tabular foundation models change what the model sees when it makes a
prediction. During pretraining, they learn to predict hidden outcomes
from labeled examples across many different tables. Give one a new
table and it uses the rows with known outcomes to score the others.

Tabular foundation models have gained attention over the past two
years as they’ve become faster and more practical on larger tables.
In 2025, for example, TabPFN went from being designed for 10,000 rows
to 50,000. That progress made me want to see whether a
model like this could rank stocks, where the signal is weak.
[TabPFN-2.5 technical report](https://arxiv.org/abs/2511.08667)

For the comparison, I chose NVIDIA’s Kumo Tabular, a model pretrained
entirely on synthetic tables. All three models get the same 80 stock
predictors so I can focus on how they rank the same stocks. I then
use the existing portfolio construction to see how those differences
carry through to returns after fees.
[The stock predictors]({% link _posts/2025-02-09-combining-predictors.md %}#the-predictors) ·
[How rankings become positions]({% link _posts/2026-08-29-joint-sizing.md %}#sizing-under-a-volatility-budget)

## A pretrained model for tables

Imagine two artificial tables with the same two predictors. In one,
the outcome is high whenever the first predictor is high. In the
other, both predictors have to be high. Now give the model a row with
a high first value and a low second value. The first table suggests a
high outcome. The second suggests a low one. The labeled rows are the
context that tells the model which relationship applies.

During pretraining, each table is a separate prediction problem.
The model sees some outcomes and tries to fill in the hidden ones.
Its errors across many tables update its weights. It learns how to
use examples to make a prediction in a table it has just been given.
[Molnar’s chapter on pretraining](https://tabularfoundationmodels.com/pretraining)

When a new table arrives, the pretrained weights stay fixed. The
model encodes the table entries into numerical representations. As it
scores a new row, attention lets it draw more information from some
labeled examples than others. Changing those examples can change the
score with the same model weights. That’s in-context learning.
[Molnar’s chapter on in-context learning](https://tabularfoundationmodels.com/prediction)

Each row in the study is a stock on a date. To get its realized outcome,
I take the stock’s average daily return over the next 20 trading sessions,
divide by daily return volatility, and rank that Sharpe ratio among its
sector peers. Figure 1 follows a prediction for stock C. I know its
momentum on session 55. Its eventual rank is still a question mark.

LightGBM learns its tree splits and leaf values from the labeled rows
A and B, then runs C’s momentum through those fitted trees. Kumo
scores C using its momentum and the labeled examples together.

<figure id="figure-1" class="research-figure responsive-figure stock-scoring-figure">
  <picture>
    <source media="(max-width: 600px)" srcset="{{ '/assets/equity-model-comparison/in-context-sketch-mobile.webp' | relative_url }}" width="1024" height="1536">
    <img src="{{ '/assets/equity-model-comparison/in-context-sketch.webp' | relative_url }}" width="1536" height="1024" loading="lazy" decoding="async" alt="LightGBM fits trees on labeled stocks A and B, then scores C from its momentum. Kumo scores C with A and B as context. The label cutoff is session 50, the context refresh is 51, the forecast is 55, and the simulated trade is 56.">
  </picture>
  <figcaption class="figure-caption"><span class="caption-number">Figure 1.</span> <span class="caption-title">How LightGBM and Kumo score a stock.</span> The sketch draws on Christoph Molnar’s explanation of prediction inputs in <a href="https://tabularfoundationmodels.com/prediction#fig-input-output"><em>Tabular Foundation Models</em>, Figure 4.2</a>.</figcaption>
</figure>

Stock B’s outcome is known at session 50. At the refresh on 51,
Kumo’s `fit` call saves a representation of the labeled rows for
reuse. The forecast at 55 uses that context, and the simulated
trade takes place at the next close.

I reuse one context for a block of forecasts, then rebuild it with
the outcomes known when the next block begins. In the expanding runs,
each context draws on history back to January 1995. Later blocks have
more history available to sample.

## Subsampling the historical context

When Ridge or LightGBM scores a row, it uses fitted coefficients or
trees. Kumo also has to process the historical examples it will use
to make the prediction. That work takes more compute and memory as
the table grows. NVIDIA recommends a GPU for large contexts.
I wanted to run the comparison on my Mac’s CPU, so I needed to pass
Kumo fewer examples. I cut down the context in two steps.
[NVIDIA’s GPU sizing guide](https://docs.nvidia.com/sdgm/structured-data-models/gpu-sizing)

**First, space out the historical dates.** Adjacent 20-session targets
share 19 return days. Taking every 20th or 30th trading session keeps
examples from across the history while dropping many overlapping
ones. This changes which dates supply examples. Both runs still
forecast and trade on the same schedule.

**Then, keep the tails on each sampled date.** Stocks on the same
date share market moves. To cut the number of rows further, I sort
that date’s stocks by their **realized target**, the 20-session
Sharpe rank within each stock’s sector. I keep roughly the lowest
30% and the highest 30%. The hope is that examples of strong and
weak outcomes are especially useful for a portfolio that buys and
shorts at the ends of the ranking. The middle can still contain
useful examples.

Coqueret and Guida (2020) tested this idea with boosted trees.
Keeping the lowest and highest 20% of their training outcomes cut
backtest time by roughly 60% and gave a similar return spread
between the highest- and lowest-ranked portfolios. That result
motivated keeping the tails when I needed to shrink Kumo’s context.
[Training trees on tails with applications to portfolio choice](https://link.springer.com/article/10.1007/s10479-020-03539-2)

Figure 2 puts the two steps together. Follow the 20-session row to
see which four dates are kept. On each of those dates, keeping the
three stocks at either end leaves six examples, or 24 rows in total.

<figure id="figure-2" class="research-figure responsive-figure">
  <div class="context-sampling" role="img" aria-label="The 20-session grid selects historical sessions 0, 20, 40 and 60. The 30-session grid selects 0, 30 and 60. On each selected date, ten stocks are sorted by the realized prediction target. The lowest three and highest three are kept, and the middle four are skipped.">
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
      <div class="context-sampling-heading">Stocks sorted by realized target</div>
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

By the end of the backtest, a weekly sample would still leave about
760,000 labeled rows after keeping only the tails. I estimated 35 GiB
just to prepare that context with Kumo Small, on a Mac with 16 GB.
Spacing the dates four or six weeks apart brought that down to about
190,000 or 127,000 labeled rows, respectively. Both runs fit on the Mac.

## Running Kumo on a Mac

I ran Kumo on the 10-core Apple M2 Pro CPU of my 14-inch MacBook Pro
(2023), with 16 GB of unified memory. I started with Kumo Large because it
had the best results in NVIDIA’s paper. Large and Small both hit my
10 GiB memory limit in the first block, even with 35,738 context rows
for Small. Smaller batches during context preparation got both through.

In Molnar’s TabICL example, `predict` takes longer than `fit`.
Kumo can do part of the prediction work up front by preparing a
context once and reusing it. For Small at four-week spacing, setup
for the last block took about 16 minutes and scoring took about eight.
[Molnar’s TabICL timing example](https://tabularfoundationmodels.com/classification#fit-is-faster-than-predict)

For the longer runs, I spaced the historical dates farther apart and
kept the context fixed until the next refresh. The four- and six-week
Small runs took 2 hours 37 minutes and 1 hour 39 minutes.
Medium needed eight-week spacing to fit and ran in 2 hours 52 minutes.
I ran Large only in the first block. I also ran Small with weekly dates
in a shorter window that grew from two to three years, then rolled
forward. That run took just under two hours.

Each portfolio needs a new ranking only on its signal dates. Scoring
on those dates cuts the number of predictions to about a fifth of
what daily scoring would require.

## Ranking the whole cross-section

Every Kumo run scores the same 1,162,773 stock-date rows over 1999–2021,
covering all eligible stocks on each signal date. Three staggered
portfolios each rebalance roughly every three weeks, giving about one
signal date a week across the three.

A useful ranking puts stocks with higher scores near the top of the
realized ranking. On each signal date $t$, I measure that agreement
by correlating the ranks of scores $s_{i,t}$ and realized targets
$y_{i,t}$. I use the same stocks for every model, with a score from
each and a known target. The result is the information coefficient
(IC), or Spearman rank correlation for that date.

$$
\mathrm{IC}_t
= \operatorname{Corr}_i\!\bigl(
  \operatorname{rank}_i(s_{i,t}),\,\operatorname{rank}_i(y_{i,t})
\bigr).
$$

Rank IC in Figure 3 is the average of the $T$ signal-date ICs. I also
want to know how steady that agreement is. The information coefficient
ratio (ICIR) divides the average by the sample standard deviation of
the signal-date ICs, $s_{\mathrm{IC}}$.

$$
\overline{\mathrm{IC}}=\frac{1}{T}\sum_{t=1}^{T}\mathrm{IC}_t,
\qquad
\mathrm{ICIR}=\frac{\overline{\mathrm{IC}}}{s_{\mathrm{IC}}}.
$$

Read across LightGBM’s full-period row in Figure 3. Its average IC
of 0.0557 divided by its IC standard deviation of about 0.077 gives
an ICIR of about 0.72. The ratio is unannualized.

<figure id="figure-3" class="research-figure responsive-figure">
  {% include blog-chart.html chart="rank" source="/assets/equity-model-comparison/rank-metrics.json?v=2" base="/assets/equity-model-comparison/rank-metrics" mobile="/assets/equity-model-comparison/rank-metrics_mobile" version="2" label="Rank IC, standard deviation of IC, and ICIR by model, with four selectable periods." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 3.</span> <span class="caption-title">Rank metrics by period.</span> IC SD measures how much IC varies across signal dates. The full period covers 1,191 shared signal dates with known targets.</figcaption>
</figure>

All three expanding Kumo runs had positive rank IC in every period
shown. That’s what surprised me about a model pretrained on artificial
tables. LightGBM’s lead in mean IC over the full period comes from
1999–2011. Ridge had the higher mean IC in the recent windows.
LightGBM’s IC was steadier, keeping it ahead on ICIR.

Among the Kumo runs, Medium had the highest mean IC over the full
period. The two expanding Small runs had steadier ICs and higher ICIRs
than Medium and Ridge. Rolling Small had the lowest mean IC in each
period, and its mean fell slightly below zero in 2017–2021.

## Return and risk by score decile

Rank IC looks across the whole ranking. A long-short portfolio depends
on the stocks at the ends. To see how those stocks performed, I sort
each signal date’s scores into ten roughly equal-sized groups, from
lowest to highest score. I simulate the trade at the next close. The
new groups start earning returns the following session and keep the
same members until the next trade.

Each day I give the stocks in a decile equal weights within their
schedule, then give the three schedules equal weight. Let $D_{d,k,t}$
be the members of decile $d$ on schedule $k$ with an available return
on date $t$, and $r_{i,t}$ be stock $i$’s close-to-close total return.

$$
R_{d,t}
=\frac{1}{3}\sum_{k=1}^{3}
  \frac{1}{|D_{d,k,t}|}\sum_{i\in D_{d,k,t}}r_{i,t}.
$$

If a decile has three stocks returning 2%, 1% and −1% on one schedule,
its return for that day and schedule is about 0.67%. I average the
schedule returns on days when all three are available. The spread is
the top decile’s return minus the bottom decile’s each day.

For either a decile or the spread, let $R_t$ be its daily return,
$\bar R$ its mean and $s_R$ its sample standard deviation over $T$
trading sessions. With 252 sessions per year and zero cash return,
the annualized statistics are

$$
\begin{aligned}
R_{\mathrm{ann}}&=\left[\prod_{t=1}^{T}(1+R_t)\right]^{252/T}-1,\\
\sigma_{\mathrm{ann}}&=\sqrt{252}\,s_R,\\
\mathrm{Sharpe}_{\mathrm{ann}}&=\sqrt{252}\,\frac{\bar R}{s_R}.
\end{aligned}
$$

Figure 4 shows whether the stocks at the two ends of each ranking
earned different returns. In the return panel, look at deciles 1
and 10 to see where the long-short spread comes from.

<figure id="figure-4" class="research-figure decile-profile-figure responsive-figure">
  {% include blog-chart.html chart="profiles" source="/assets/equity-model-comparison/deciles.json?v=2" base="/assets/equity-model-comparison/scheduled-decile-profile" mobile="/assets/equity-model-comparison/scheduled-decile-profile_mobile" version="7" label="Return, volatility and Sharpe by stock score decile, with selectable periods and models." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 4.</span> <span class="caption-title">Return, volatility and Sharpe by score decile.</span> Decile 10 holds the highest scores. All deciles are equal-weighted and shown before costs.</figcaption>
</figure>

LightGBM separates at both ends, with a higher return at the top and
a lower return at the bottom. The rolling variant is particularly weak
on the short side. Stocks in its lowest score decile earn nearly 10%
a year.

## Returns after portfolio construction

To see how the decile results carry through sizing and fees, I build
long-short portfolios from the 75 highest and 75 lowest scores. The
optimizer uses forecast risk to size those positions together. Each
schedule uses $5 million of simulated capital, a 7% annual volatility
target, and limits on gross exposure and market beta. Where I can
measure liquidity, I cap trades at 10% of the previous 21 sessions'
average daily dollar volume.

I use LightGBM's construction settings for the Kumo books, including a
5 basis point turnover penalty. Ridge uses its original 2.5 basis point
penalty. The penalty shapes how much the optimizer trades. The
execution fees are 7.5 basis points on long trades and 10 on shorts
through 2010, then 5 and 7.5. I compute each net statistic separately
by schedule, then average the three. Table 1 puts the equal-weight
spread from the decile analysis on the left and the sized portfolio
after fees on the right. It shows whether the models keep the same
ordering once their scores become trades.

<div id="table-5">
<div id="table-6" class="research-table-scroll" tabindex="0" role="region" aria-label="Gross decile spreads and portfolios after execution fees">
<table id="table-1" class="research-table comparison-table equity-comparison-table">
  <caption><span class="caption-number">Table 1.</span> <span class="caption-title">Gross decile spreads and net constructed portfolios.</span> All models use the same signal dates. Return, volatility and Sharpe are annualized.</caption>
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

Over 1999–2021, LightGBM leads on Sharpe for both the equal-weight
spread and the net portfolios. Medium ranks below both expanding Small
runs on gross spread Sharpe and above both on net Sharpe. Medium’s net
Sharpe trails LightGBM’s by 0.69. I resample 21-session stretches of
returns to keep nearby observations together, using the same stretches
for both portfolios. The 95% interval for the difference is −0.99 to
−0.40.

## How similarly the models trade

Medium came close to Ridge on net Sharpe. That still leaves open
whether they ranked stocks similarly or made money on the same days.
The left side of Table 2 averages score rank correlations across all
signal dates, including dates whose outcomes fall beyond the test
period. The right side averages net daily return correlations across
the three schedules.

<div role="group" aria-labelledby="table-2">
  <p id="table-2" class="table-caption"><span class="caption-number">Table 2.</span> <span class="caption-title">Correlations between models, 1999–2021.</span> Rankings use 1,200 signal dates. Net returns use 5,773 trading sessions.</p>
  {% include equity-correlation-matrices.html %}
</div>

The two baselines agree more on rankings than either agrees with the
expanding Small variants. Medium is closer to LightGBM than to Ridge
on both rankings and daily returns. Rolling Small’s daily net returns
have a correlation of about 0.02 with four-week Small.

To see where the P&L differences come from, I split each day’s result
into contributions from longs, shorts and fees. Annualizing the average
daily contributions keeps them additive. LightGBM earned 7.1 percentage
points more per year than four-week Small on this measure. Longs accounted
for 3.3 points, shorts for 2.4 and lower fees for 1.4. Medium earned 1.8 points
more than four-week Small. Longs added 1.5 points and lower fees added
0.9, with the short side giving back 0.6.

## The cost of sampling more dates

Finer date spacing gives Kumo more examples at a higher compute cost.
To see whether it improves the rankings, I compare versions of
Small at different spacings with the same tail filter. For the first
block, I could also compare model sizes on exactly the same dates.

On the 91 matched signal dates in that block, Kumo Small’s ICIR was
1.08 at three-week training spacing, 0.91 at four weeks, and 0.62 at six.
With the same six-week training dates, Medium reached 0.72 and Large
reached 0.79. Changing Small’s date spacing moved ICIR more in that
early comparison than changing model size at six-week spacing.

For the last block, four-week Small took 24 minutes and six-week Small
took 12½. The denser run's ICIR was 0.11 versus 0.21 for six weeks on
61 dates with realized targets.

Across the full run, moving from six-week to four-week spacing took about
59% longer. The paired 21-session intervals for four weeks minus six
were −0.06 to 0.04 for ICIR and −0.21 to 0.23 for net Sharpe. The
full-period results were close. Four-week Small earned a higher net
Sharpe through 2011 and a lower one after 2011. The accuracy cost of
dropping the middle 40% is unknown here since both runs use the tail
filter.

## The shorter history changed what Kumo picked

Spacing determines how often I sample dates. A rolling window also
changes how far back I look. I tried this because relationships in
equities can change. The rolling run samples recent history weekly
and drops older observations as the window moves forward.

Rolling Small’s rankings were less correlated with Ridge and
LightGBM. Relative to four-week expanding Small, its ICIR was lower
by 0.44 and its after-fee Sharpe by 0.87. The paired intervals are
−0.58 to −0.30 for ICIR and −1.39 to −0.36 for net Sharpe.
In 2012–2021, the rolling gross spread was less volatile and had a
higher Sharpe. The net rolling portfolio’s Sharpe was lower in every
period shown.

The short book explains most of the difference. The rolling variant
gave up 5.9 percentage points of annualized arithmetic net P&L versus
four-week Small. The short side cost 5.6 points more, the long side
earned 0.7 points less, and lower fees recovered 0.4 points.

## How the P&L built up

Figure 5 puts Medium, Ridge and LightGBM on the same timeline
to show when their results diverged. Medium stayed close to Ridge
over the full test. At their original volatility, both earned about
$244 per $100 of fixed capital by the end of 2021. LightGBM pulled
ahead early and ended at about $365.

The chart opens with each portfolio rescaled to 7% annualized
volatility over the selected window so the paths are comparable at
the same risk level. Clear the checkbox to see the
original P&L and drawdowns. Open **Window statistics** to compare
annual net P&L, volatility, Sharpe and drawdowns at either scale.

<figure id="figure-5" class="research-figure portfolio-path-figure responsive-figure">
  {% include blog-chart.html chart="pnl" source="/assets/equity-model-comparison/net-pnl.json?v=4" base="/assets/equity-model-comparison/net-pnl" mobile="/assets/equity-model-comparison/net-pnl_mobile" version="3" label="Cumulative net P&L and drawdown for Ridge, LightGBM and Kumo Medium, rescaled to 7% annualized volatility by default." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 5.</span> <span class="caption-title">Cumulative P&amp;L and drawdown after fees.</span> I sum the mean daily P&amp;L of the three schedules per $100 of fixed capital. Drawdown is the loss from the previous P&amp;L peak within the chosen window.</figcaption>
</figure>

At the same realized volatility over the full period, Medium earned
more than Ridge and had a smaller worst drawdown. LightGBM still earned
the most and had the smallest peak-to-trough loss of the three.

## What I found and what I’d test next

What surprised me was how much Kumo could do with a model pretrained
on artificial tables and a sample of labeled stock history. Medium
came close to Ridge after fees. LightGBM had the highest net Sharpe
over 1999–2021. Sampling made the test feasible on my Mac. For Small,
sampling dates more densely cost more time and left full-period
ICIR and net Sharpe broadly similar.

With more memory, I’d run the same Kumo model on the same dates with
all eligible stocks and with just the tails. That would show how much
memory and time the filter saves and what it costs in ranking quality.
I’d also give Small, Medium and Large the same context across the full
backtest. The comparison on the first block favored the larger models.
Across the full run, models of different sizes used different amounts
of history.

## References

- Coqueret, Guillaume, and Tony Guida (2020). *Training trees on tails with applications to portfolio choice*. *Annals of Operations Research*, 288, 181–221. [Published article](https://doi.org/10.1007/s10479-020-03539-2)
- Grinsztajn, Léo, et al. (2025). *TabPFN-2.5: Advancing the State of the Art in Tabular Foundation Models*. [Technical report](https://arxiv.org/abs/2511.08667)
- Molnar, Christoph. *Tabular Foundation Models*. [Online book](https://tabularfoundationmodels.com/) · [In-context learning, Figure 4.2](https://tabularfoundationmodels.com/prediction#fig-input-output) · [Pretraining](https://tabularfoundationmodels.com/pretraining) · [Classification](https://tabularfoundationmodels.com/classification)
- Qu, Jingang, et al. (2026). *NVIDIA Kumo Tabular: Pushing the Accuracy–Efficiency Frontier for Tabular Prediction*. arXiv:2611.23001, v1. [Preprint](https://arxiv.org/abs/2611.23001v1)
