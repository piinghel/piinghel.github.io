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

The signal in stock returns is weak. I wanted to see whether a model
pretrained on synthetic tables could use real stock history to rank
stocks. I tested NVIDIA’s Kumo Tabular alongside Ridge and LightGBM.
All three use the 80 stock predictors I describe in [*Combining Multiple Predictors:
The Linear Case*]({% link _posts/2025-02-09-combining-predictors.md %}#the-predictors).
I first compare the rankings themselves. Then I use the sizing method
from [*From Volatility Scaling to Joint
Sizing*]({% link _posts/2026-08-29-joint-sizing.md %}#sizing-under-a-volatility-budget)
to see how each ranking fares after trading costs.

## A pretrained model for tables

### What the historical examples do at prediction time

Each row is a stock on a particular date. Its predictors are what I
know on that date, such as momentum. To get the outcome, I divide the
stock’s average daily return over the next 20 trading sessions by
its daily return volatility over the same period and rank that ratio
within its sector. In Figure 1, the outcomes for A and B are already
known. The task is to score C using the momentum observed on session 55.

LightGBM and Kumo both expose `fit()` and `predict()`. With LightGBM,
`fit()` builds trees from A and B. To score C, `predict()` passes C’s
momentum through the fitted trees and adds their contributions. Ridge
fits a set of coefficients and uses those coefficients to score new rows.

With Kumo, `fit()` prepares A and B and caches information from them.
At `predict()`, the network uses that cached information alongside C’s
momentum. As more outcomes become available, I can refresh the examples
while keeping the pretrained network weights fixed. Using labeled
examples this way is called *in-context learning*. [Christoph Molnar’s
first example](https://tabularfoundationmodels.com/first-look) shows how
the familiar calls conceal this change in what the model uses at prediction time.

<figure id="figure-1" class="research-figure responsive-figure stock-scoring-figure">
  <picture>
    <source media="(max-width: 600px)" srcset="{{ '/assets/equity-model-comparison/in-context-sketch-mobile.webp' | relative_url }}" width="1024" height="1536">
    <img src="{{ '/assets/equity-model-comparison/in-context-sketch.webp' | relative_url }}" width="1536" height="1024" loading="lazy" decoding="async" alt="LightGBM fits trees on labeled stocks A and B, then scores C from its momentum. Kumo scores C with A and B as context. The label cutoff is session 50, the context refresh is 51, the forecast is 55, and the simulated trade is 56.">
  </picture>
  <figcaption class="figure-caption"><span class="caption-number">Figure 1.</span> <span class="caption-title">How LightGBM and Kumo score a stock.</span> The sketch draws on Christoph Molnar’s explanation of prediction inputs in <a href="https://tabularfoundationmodels.com/prediction#fig-input-output"><em>Tabular Foundation Models</em>, Figure 4.2</a>.</figcaption>
</figure>

B is sampled at session 30, so its 20-session outcome is known at
session 50. I refresh the context on 51 and reuse it for a block of
forecasts, including the one for C on 55. The simulated trade takes
place at the next close. At the start of each block I rebuild the
context using the outcomes available by then.

### What Kumo learns during pretraining

NVIDIA generated tables with different relationships between predictors
and outcomes. On each table, Kumo saw some outcomes and had to predict
the rest. Its prediction errors drove updates to the same network
across many such tables. By the time I use Kumo, that training is
complete. The stock history supplies examples of how predictors and
outcomes relate in this particular dataset.
[Molnar’s chapter on pretraining](https://tabularfoundationmodels.com/pretraining)
explains why varying the relationships across tables matters.

### The Bayesian intuition

Suppose an outcome is usually high when momentum is high under one
rule, and usually high only when both momentum and value are high under
another. Say each rule gives its usual outcome nine times out of ten,
with independent errors across rows, and I give both rules a 50%
probability to start.

Now I see a row with high momentum, low value and a low outcome. That
outcome is nine times as likely under the second rule, so I raise its
probability to 90%. For a new row with the same predictors, the chance
of a low outcome is 0.9 × 0.9 + 0.1 × 0.1, or 82%.

The probabilities assigned to the rules before seeing the example
are the *prior*. The updated probabilities are the *posterior*.
Averaging each rule’s forecast using those probabilities gives the
*posterior predictive distribution*. For a prior-data fitted network,
the generator of the synthetic tables defines the prior. Pretraining
teaches the network to approximate this kind of prediction from
examples, across a much wider range of relationships.
[Molnar’s chapter on prior-data fitted networks](https://tabularfoundationmodels.com/prior-data-fitted-networks)
develops the idea from [Müller et al.](https://openreview.net/forum?id=KSugKcbNf9).

### How Kumo turns the examples into a score

Kumo builds a numerical representation of each row from its predictors
and any known outcome. Attention lets the model use these representations
to decide how much information to draw from each historical example.
Successive layers refine the representation of the new row before
predicting its outcome
([Qu et al., *NVIDIA Kumo Tabular*, §§2 and 5](https://arxiv.org/html/2611.23001v1#S2)).
Kumo produces quantiles of the predicted outcome, and I average them
to get one score for each stock.

## Subsampling the historical context

In the expanding runs, the available history starts in January 1995.
By the later blocks, there are many more examples to choose from.
Processing those examples takes more compute and memory as the
context grows. Table sizes have been moving up quickly. In 2025,
the [TabPFN-2.5 paper](https://arxiv.org/abs/2511.08667) reported a
fivefold increase in the number of rows it could handle, from 10,000
to 50,000. NVIDIA recommends a GPU for large contexts in its
[*GPU Sizing Guide*](https://docs.nvidia.com/sdgm/structured-data-models/gpu-sizing).
I wanted to run the comparison on my Mac’s CPU, so I needed to pass
Kumo fewer examples. I cut down the context in two steps.

**First, space out the historical dates.** Adjacent 20-session targets
share 19 return days. I sample every 30 trading sessions (roughly
six weeks) for expanding Small, and every 40 for Medium. Spacing
out the dates keeps examples from across the history while dropping
many overlapping ones.

**Then, keep the tails on each sampled date.** Stocks on the same
date share market moves. To cut the number of rows further, I sort
that date’s stocks by their **realized target**, the 20-session
Sharpe rank within each stock’s sector. I keep roughly the lowest
30% and the highest 30%. The hope is that examples of strong and
weak outcomes are especially useful for a portfolio that buys and
shorts at the ends of the ranking. The middle can still contain
useful examples. Both cuts apply to historical rows with outcomes
already known. On each forecast date Kumo still scores every
eligible stock, and both runs trade on the same schedule.

In [*Training Trees on Tails with Applications to Portfolio
Choice*](https://doi.org/10.1007/s10479-020-03539-2), Coqueret and
Guida (2020) tested this idea with boosted trees.
Keeping the lowest and highest 20% of their training outcomes cut
backtest time by roughly 60% and gave a similar return spread
between the highest- and lowest-ranked portfolios. That result
motivated keeping the tails when I needed to shrink Kumo’s context.

Figure 2 puts the two steps together. The 20-session grid keeps
four dates and the 30-session grid keeps three. With six stocks
per date, that leaves 24 and 18 examples, respectively.

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

When the available history was longest, weekly sampling with the
tails filter would still leave about 760,000 labeled rows. I
estimated 35 GiB just to prepare that context with Kumo Small, on
a Mac with 16 GB. That’s why I used wider spacing. At six weeks,
the context dropped to about 127,000 rows and fit on the Mac.

## Running Kumo on a Mac

I ran Kumo on the 10-core Apple M2 Pro CPU of my 14-inch MacBook Pro
(2023), with 16 GB of unified memory. I started with Kumo Large because it
had the best results in NVIDIA’s paper. Large and Small both hit my
10 GiB memory limit in the first block, even with 35,738 context rows
for Small. Smaller batches during context preparation got both through.

In the [TabICL example in Molnar’s classification
chapter](https://tabularfoundationmodels.com/classification#fit-is-faster-than-predict),
`predict` takes longer than `fit`.
Kumo can do part of the prediction work up front by preparing a
context once and reusing it. In the last block of the 1999–2021 test,
Medium’s setup took about 13 minutes and scoring took about eight.

Over the full 1999–2021 comparison, expanding Small took 1 hour 39
minutes and Medium took 2 hours 52 minutes.
I ran Large only in the first block. I also ran Small with weekly dates
in a shorter window that grew from two to three years, then rolled
forward. That run took just under two hours.

Each portfolio needs a new ranking only on its signal dates. Scoring
on those dates cuts the number of predictions to about a fifth of
what daily scoring would require.

## Ranking the whole cross-section

The full-period runs all score the same 1,162,773 stock-date rows
across 1,200 signal dates over 1999–2021. Three staggered
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
  {% include blog-chart.html chart="rank" source="/assets/equity-model-comparison/rank-metrics.json?v=3" base="/assets/equity-model-comparison/rank-metrics" mobile="/assets/equity-model-comparison/rank-metrics_mobile" version="4" label="Rank IC, standard deviation of IC, and ICIR by model, with four selectable periods." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 3.</span> <span class="caption-title">Rank metrics by period.</span> Kumo runs are in blue. Each metric uses the same scale across periods. The full period covers 1,191 shared signal dates with known targets.</figcaption>
</figure>

Both expanding Kumo runs had positive rank IC in every period
shown. That’s what surprised me about a model pretrained on artificial
tables. LightGBM’s lead in mean IC over the full period comes from
1999–2011. Ridge had the higher mean IC in the recent windows.
LightGBM’s IC was steadier, keeping it ahead on ICIR.

Among the Kumo runs, Medium had the highest mean IC over the full
period. Expanding Small had steadier ICs and a higher ICIR
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
  {% include blog-chart.html chart="profiles" source="/assets/equity-model-comparison/deciles.json?v=3" base="/assets/equity-model-comparison/scheduled-decile-profile" mobile="/assets/equity-model-comparison/scheduled-decile-profile_mobile" version="8" label="Return, volatility and Sharpe by stock score decile, with selectable periods and models." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 4.</span> <span class="caption-title">Return, volatility and Sharpe by score decile.</span> Decile 10 holds the highest scores. All deciles are equal-weighted and shown before costs.</figcaption>
</figure>

Over the full period, LightGBM’s top decile earns about 19% a year
and its bottom decile is roughly flat. Rolling Small struggles on
the short side. Even the stocks it ranks lowest earn nearly 10% a year.

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
through 2010, then 5 and 7.5. Table 1 shows the same holdings before
and after those fees. I compute return, volatility, Sharpe and
turnover for each schedule and then average the three. Two-way
turnover adds all dollars bought and sold across both sides, divides
by fixed capital, and annualizes the average over trading sessions.

<div id="table-5">
<div id="table-6" class="research-table-scroll" tabindex="0" role="region" aria-label="Portfolio results before and after execution fees, with turnover">
<table id="table-1" class="research-table comparison-table equity-comparison-table">
  <caption><span class="caption-number">Table 1.</span> <span class="caption-title">Portfolio performance before and after fees.</span> Returns are compounded. Turnover is two-way traded notional per year, in multiples of fixed capital. All figures are annualized.</caption>
  <colgroup span="1"></colgroup><colgroup span="2"></colgroup><colgroup span="3"></colgroup><colgroup span="1"></colgroup>
  <thead>
    <tr><th scope="col" rowspan="2">Model</th><th scope="colgroup" colspan="2">Before fees</th><th scope="colgroup" colspan="3" class="comparison-divider">After fees</th><th scope="col" rowspan="2">Turnover</th></tr>
    <tr><th scope="col">Return</th><th scope="col">Sharpe</th><th scope="col" class="comparison-divider">Return</th><th scope="col">Vol.</th><th scope="col">Sharpe</th></tr>
  </thead>
  <tbody>
    <tr class="period-heading"><th colspan="7" scope="rowgroup">1999–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>12.9%</td><td>1.43</td><td class="comparison-divider">10.8%</td><td>8.7%</td><td>1.21</td><td>25.6×</td></tr>
    <tr><th scope="row">LightGBM</th><td>19.2%</td><td>2.37</td><td class="comparison-divider">16.9%</td><td>7.5%</td><td>2.12</td><td>25.4×</td></tr>
    <tr><th scope="row">Small, 6 weeks</th><td>12.4%</td><td>1.68</td><td class="comparison-divider">8.9%</td><td>7.1%</td><td>1.24</td><td>42.3×</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>13.7%</td><td>1.76</td><td class="comparison-divider">11.0%</td><td>7.4%</td><td>1.44</td><td>31.8×</td></tr>
    <tr><th scope="row">Small, rolling</th><td>5.7%</td><td>0.77</td><td class="comparison-divider">2.7%</td><td>7.6%</td><td>0.39</td><td>38.2×</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="7" scope="rowgroup">1999–2011</th></tr>
    <tr><th scope="row">Ridge</th><td>12.4%</td><td>1.52</td><td class="comparison-divider">9.9%</td><td>8.0%</td><td>1.22</td><td>27.5×</td></tr>
    <tr><th scope="row">LightGBM</th><td>20.4%</td><td>2.66</td><td class="comparison-divider">17.7%</td><td>7.1%</td><td>2.35</td><td>26.3×</td></tr>
    <tr><th scope="row">Small, 6 weeks</th><td>13.5%</td><td>1.91</td><td class="comparison-divider">9.9%</td><td>6.8%</td><td>1.42</td><td>38.6×</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>12.9%</td><td>1.80</td><td class="comparison-divider">9.8%</td><td>6.9%</td><td>1.38</td><td>33.1×</td></tr>
    <tr><th scope="row">Small, rolling</th><td>7.3%</td><td>0.97</td><td class="comparison-divider">4.0%</td><td>7.6%</td><td>0.55</td><td>37.2×</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="7" scope="rowgroup">2012–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>13.5%</td><td>1.36</td><td class="comparison-divider">11.9%</td><td>9.7%</td><td>1.22</td><td>23.2×</td></tr>
    <tr><th scope="row">LightGBM</th><td>17.6%</td><td>2.05</td><td class="comparison-divider">15.9%</td><td>8.0%</td><td>1.88</td><td>24.1×</td></tr>
    <tr><th scope="row">Small, 6 weeks</th><td>10.9%</td><td>1.43</td><td class="comparison-divider">7.8%</td><td>7.5%</td><td>1.04</td><td>47.2×</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>14.6%</td><td>1.73</td><td class="comparison-divider">12.5%</td><td>8.1%</td><td>1.50</td><td>30.1×</td></tr>
    <tr><th scope="row">Small, rolling</th><td>3.6%</td><td>0.50</td><td class="comparison-divider">1.1%</td><td>7.5%</td><td>0.18</td><td>39.4×</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="7" scope="rowgroup">2017–2021</th></tr>
    <tr><th scope="row">Ridge</th><td>14.1%</td><td>1.30</td><td class="comparison-divider">12.6%</td><td>10.5%</td><td>1.18</td><td>22.0×</td></tr>
    <tr><th scope="row">LightGBM</th><td>16.4%</td><td>1.76</td><td class="comparison-divider">14.9%</td><td>8.9%</td><td>1.60</td><td>22.3×</td></tr>
    <tr><th scope="row">Small, 6 weeks</th><td>10.2%</td><td>1.24</td><td class="comparison-divider">7.0%</td><td>8.1%</td><td>0.88</td><td>47.1×</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>15.0%</td><td>1.59</td><td class="comparison-divider">13.0%</td><td>9.0%</td><td>1.40</td><td>28.5×</td></tr>
    <tr><th scope="row">Small, rolling</th><td>1.8%</td><td>0.27</td><td class="comparison-divider">−0.6%</td><td>7.8%</td><td>−0.04</td><td>39.0×</td></tr>
  </tbody>
</table>
</div>
</div>

Expanding Small had the higher equal-weight decile-spread Sharpe
of the two expanding Kumo runs. Once I sized the portfolios,
Medium edged ahead before fees, 1.76 versus 1.68. Small traded
42.3 times capital per year versus 31.8 for Medium. Fees widened
Medium’s lead to 1.44 versus 1.24.

Medium also beat Ridge on net Sharpe over 1999–2021, 1.44 versus
1.21, with lower realized volatility. LightGBM led in the decile
spread and in the sized portfolios, reaching a net Sharpe of 2.12.
Resampling the same 21-session stretches of returns for Medium and
LightGBM gives a 95% interval of −0.99 to −0.40 for Medium’s net
Sharpe minus LightGBM’s.

I split the difference in average daily P&L into longs, shorts and
fees, then annualize so the pieces add up. LightGBM earned 7.1
percentage points more per year than expanding Small on this
measure. Longs contributed 3.2 points, shorts 2.7 and lower fees
1.2. Medium earned 1.9 points more than expanding Small, with 1.5
points from longs and 0.7 from lower fees, offset by a 0.3-point
shortfall on the short side.

## How similarly the models trade

Medium beat Ridge on net Sharpe. Did it rank stocks similarly or
make money on the same days?
The left side of Table 2 averages score rank correlations across all
signal dates, including dates whose outcomes fall beyond the test
period. The right side averages net daily return correlations across
the three schedules.

<div role="group" aria-labelledby="table-2">
  <p id="table-2" class="table-caption"><span class="caption-number">Table 2.</span> <span class="caption-title">Correlations between models, 1999–2021.</span> Rankings use 1,200 signal dates. Net returns use 5,773 trading sessions.</p>
  {% include equity-correlation-matrices.html %}
</div>

The two baselines agree more on rankings than either agrees with the
expanding Small. Medium is closer to LightGBM than to Ridge
on both rankings and daily returns. Rolling Small’s daily net returns
have a correlation of about 0.03 with expanding Small.

## Comparing model sizes on the same context

The full run compares the configurations that fit on my Mac.
For the first block of forecasts, all three model sizes fit with
the same six-week context. On 91 matched signal dates, ICIR was
0.62 for Small, 0.72 for Medium and 0.79 for Large. That early
comparison isolates model size. For the full run I needed wider
spacing for Medium, which also changes the examples it sees.

## Rolling Small was weaker in every period

If the relationships between predictors and outcomes change, recent
examples might help more than old ones. I tried a rolling version of
Small that sampled weekly and dropped older observations as it moved
forward. It changed both the spacing of the dates and how far back the
model could look.

Rolling Small’s rankings were less correlated with Ridge and
LightGBM. Relative to expanding Small, its ICIR was lower
by 0.45 and its after-fee Sharpe by 0.85.
Even in 2012–2021, when the rolling equal-weight decile spread was
less volatile, its Sharpe was lower than expanding Small’s. After
sizing and fees, Rolling Small had the lowest Sharpe of any model
in every period shown. Its net Sharpe was
0.39 for the full period and −0.04 in 2017–2021.

The short book explains most of the difference. The rolling variant
gave up 5.9 percentage points of annualized arithmetic net P&L versus
expanding Small. The short side cost 5.4 points more, the long side
earned 0.7 points less, and lower fees recovered 0.2 points.

## How the P&L built up

Figure 5 shows when the portfolios diverged. It opens with each
portfolio rescaled to 7% annualized volatility over the selected
window. The chart includes six-week Small. Open **Explore** to
add rolling Small.

<figure id="figure-5" class="research-figure portfolio-path-figure responsive-figure">
  {% include blog-chart.html chart="pnl" source="/assets/equity-model-comparison/net-pnl.json?v=6" base="/assets/equity-model-comparison/net-pnl" mobile="/assets/equity-model-comparison/net-pnl_mobile" version="5" label="Cumulative net P&L and drawdown for Ridge, LightGBM, Kumo Small and Kumo Medium, rescaled to 7% annualized volatility by default." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 5.</span> <span class="caption-title">Cumulative P&amp;L and drawdown after fees.</span> I average daily P&amp;L across the three schedules and add it up. The chart shows P&amp;L and drawdown as percentages of fixed capital.</figcaption>
</figure>

At matched volatility, LightGBM pulled ahead early and finished with
the highest cumulative P&L. Medium finished ahead of Ridge and had
a smaller worst drawdown. Clear the checkbox to see the original
paths. At their original volatilities, Medium and Ridge finished with
almost the same cumulative P&L.

## What I found and what I’d test next

What surprised me was that a model pretrained on artificial tables
could rank stocks at all. Both expanding Kumo runs had positive
rank IC in every period shown. Medium beat Ridge on net Sharpe,
1.44 versus 1.21, while LightGBM led at 2.12. Rolling Small was the
weakest result after fees.

I’d like to test Kumo Large over the full period, giving it the same
historical rows as Small and Medium. Large ranked better on the
first block of forecasts by ICIR when all three sizes saw the same examples.
The full-period comparison would tell me whether that early advantage
holds up.

I’d also like to give a fixed model more data. With more memory, I
could sample dates more often and test all eligible stocks against
keeping just the tails. Changing one of those at a time would show
which extra examples improve the ranking and what they cost to
process. As newer tabular foundation models come out, I’d run them
through the same comparison to see whether they can use more history
at a manageable cost and whether that shows up after trading fees.

## References

- Coqueret, Guillaume, and Tony Guida (2020). [*Training Trees on Tails with Applications to Portfolio Choice*](https://doi.org/10.1007/s10479-020-03539-2). *Annals of Operations Research*, 288(1), 181–221.
- Grinsztajn, Léo, et al. (2025). [*TabPFN-2.5: Advancing the State of the Art in Tabular Foundation Models*](https://arxiv.org/abs/2511.08667). Technical report, arXiv:2511.08667.
- Molnar, Christoph. [*Tabular Foundation Models: A Short and Opinionated Guide*](https://tabularfoundationmodels.com/). Online book.
- Müller, Samuel, Noah Hollmann, Sebastian Pineda Arango, Josif Grabocka, and Frank Hutter (2022). [*Transformers Can Do Bayesian Inference*](https://openreview.net/forum?id=KSugKcbNf9). ICLR.
- NVIDIA. [*GPU Sizing Guide*](https://docs.nvidia.com/sdgm/structured-data-models/gpu-sizing). *NVIDIA Kumo Documentation*.
- Qu, Jingang, et al. (2026). [*NVIDIA Kumo Tabular: Pushing the Accuracy–Efficiency Frontier for Tabular Prediction*](https://arxiv.org/abs/2611.23001v1). arXiv:2611.23001, version 1.
