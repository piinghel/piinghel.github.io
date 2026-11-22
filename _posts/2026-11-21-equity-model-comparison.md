---
layout: post
interactive_charts: true
title: "Can Tabular Foundation Models Rank Stocks?"
description: "How tabular foundation models learn from examples, and how one compares with Ridge and LightGBM for stock ranking."
date: 2026-11-21
last_modified_at: 2026-11-22
categories: ["Signals"]
article_label: Signals · Tabular models
permalink: /quants/equity-model-comparison.html
---

For years, boosted trees like LightGBM and XGBoost were the
benchmark I looked for when a new model seemed promising on
tabular data.[^tree-benchmark] Now models like TabPFN and TabICL
are beating strong tree ensembles on a growing range of
benchmarks.[^new-benchmarks]

What got me curious was how they make those predictions. With
LightGBM, I fit trees on the examples for the problem in front of
me. The fitted trees then score the new rows. A tabular foundation
model comes with a network trained across many tables. When I
ask it for a prediction, I give it rows from my own table with
known outcomes. The network uses those examples and its weights
stay fixed.

As these models got better at handling larger tables, I wanted to
try one on stocks.[^larger-tables] With a model pretrained on
synthetic tables, the stock-specific evidence comes from the
history I give it. I can walk through the backtest one forecast
date at a time, giving it the stock information available then.
I compare its rankings with Ridge and LightGBM and see how those
rankings hold up after trading costs.

## A pretrained model for tables

### What the historical examples do at prediction time

Imagine adding a row to a table with two predictors. The predictors
are filled in and the outcome is blank. In LightGBM, `fit()` builds
a series of trees from the labeled rows. Each tree adds a correction
to the earlier predictions. One tree might split the rows on the
first predictor and learn a different correction on either side.
In `predict()`, the new row follows the branches in the fitted
trees and I add up the corrections. With Ridge, the fitted
coefficients play the same role as the trees.

A tabular foundation model sees the new row’s predictors alongside
the examples and their known outcomes. Those examples are its
*context*. I can keep the same new row and the same network weights,
swap the examples, and get a different answer. That’s *in-context
learning*.

Both workflows can look like `fit()` followed by `predict()` in
code. For LightGBM, `fit()` is where the trees are built. For a
pretrained model such as TabPFN or TabICL, it prepares the examples
that the network will use to predict. Christoph Molnar illustrates
what goes into each prediction in
[*Tabular Foundation Models*, Chapter 4](https://tabularfoundationmodels.com/prediction#tfms-do-in-context-learning).

### Pretraining across many tables

During pretraining, the network sees one prediction problem after
another. In each table, it gets the outcomes for some rows and has
to predict the outcomes for the others. Its errors on those hidden
outcomes are used to update the network weights.

In one synthetic table, the first column might explain most of
the outcome. In another, two columns might matter together. If
every table followed the same rule, the network could use that
rule everywhere. When the rules vary, the labeled rows help it
work out which relationships make sense for the table at hand.
Molnar shows how those tables are generated in
[*Tabular Foundation Models*, Chapter 5](https://tabularfoundationmodels.com/pretraining).

### The Bayesian intuition

Return to the table with two predictors and imagine two possible rules.
Under the first, a high value in the first column usually gives a high
outcome. Under the second, both predictors usually need to be high.
Start with a 50% probability for each rule. Suppose the usual outcome
occurs nine times out of ten under either rule, with independent errors
across rows.

Now I see a row where the first predictor is high, the second is
low, and the outcome is low. That outcome is nine times as likely
under the second rule. The rules started with equal odds, so I
now give the second rule a 90% probability. For a new row with
the same predictors, either rule could still give a low outcome.
Weight the two forecasts by their updated probabilities and you
get 0.9 × 0.9 + 0.1 × 0.1, or 82%.

The probabilities assigned to the rules before seeing the example
are the *prior*. The updated probabilities are the *posterior*.
Averaging each rule’s forecast using those probabilities gives the
*posterior predictive distribution*. In a prior-data fitted network,
the way we generate the synthetic tables plays the role of those
starting probabilities. It determines which relationships the
network sees and how often it sees them. Pretraining teaches the
network to make this kind of prediction across many such relationships.
[Molnar’s chapter on prior-data fitted networks](https://tabularfoundationmodels.com/prior-data-fitted-networks)
develops the idea from [Müller et al.](https://openreview.net/forum?id=KSugKcbNf9).

## Testing a tabular foundation model on stocks

### What the model could know on each date

When I backtest a model, I need to know what it could have seen on
each forecast date. Say I give a language model an old announcement
of a proposed merger. It may already have read news about how the
deal ended. If it did, that later information can influence its
answer even when I give it just the announcement. For a language model, one
way to guard against this is to start the backtest after a training
cutoff I can verify. Glasserman and Lin explore the issue for
[*GPT-based news sentiment*](https://arxiv.org/abs/2309.17322).

This is where synthetic pretraining makes the stock test appealing.
NVIDIA trained Kumo Tabular on generated tables. The stock predictors
and outcomes it sees here come from the tables I give it
([Qu et al., *NVIDIA Kumo Tabular*, §3](https://arxiv.org/html/2611.23001v1#S3)).
I can step through history with one fixed network and check the
inputs on each date. I use predictors available on that date and
add a historical row to the context only after its 20-session
outcome is known.

### Research setup

I give all three models the same target and 80 predictors. For
the target, I take each stock’s Sharpe ratio over the next 20
sessions and rank it against its sector peers. I rank the
predictors across the whole stock universe on each date.
I describe how I build the target and predictors in
[*Combining Multiple Predictors: The Linear Case*]({% link _posts/2025-02-09-combining-predictors.md %}#what-i-ask-the-model-to-predict).

Ridge and LightGBM fit on past data and score the dates that follow.
I refresh Kumo’s context on the LightGBM refit dates. The expanding
Kumo runs draw on history back to January 1995. The test runs from
1999 to May 2026, with the results from 2022 onward also shown on
their own.

For **Ridge**, I use a penalty of $c=0.1$. Several predictors overlap,
such as momentum measured over nearby horizons, and the penalty
keeps the coefficients from growing too large as a result. I go
into the penalty choice in
[*Combining Multiple Predictors*]({% link _posts/2025-02-09-combining-predictors.md %}#choosing-the-penalty).

For **LightGBM**, I use 350 trees per fit, a maximum depth of five,
and a learning rate of 0.05. The shallow trees can still pick up
interactions. Each tree sees a random quarter of the predictors,
giving different trees a chance to split on different inputs.

### A stock forecast with historical context

Figure 1 uses momentum alone to show how both models score stock C on
session 55. LightGBM fits trees on historical rows A and B and scores C
by following its momentum through those trees. With Kumo, `fit()`
prepares and caches information from A and B, and `predict()` uses
that context alongside C’s momentum. C’s outcome is still unknown.

<figure id="figure-1" class="research-figure responsive-figure stock-scoring-figure">
  <picture>
    <source media="(max-width: 600px)" srcset="{{ '/assets/equity-model-comparison/in-context-sketch-mobile.webp' | relative_url }}" width="1024" height="1536">
    <img src="{{ '/assets/equity-model-comparison/in-context-sketch.webp' | relative_url }}" width="1536" height="1024" loading="lazy" decoding="async" alt="LightGBM fits trees on labeled stocks A and B, then scores C from its momentum. Kumo scores C with A and B as context. The label cutoff is session 50, the context refresh is 51, the forecast is 55, and the simulated trade is 56.">
  </picture>
  <figcaption class="figure-caption"><span class="caption-number">Figure 1.</span> <span class="caption-title">How LightGBM and Kumo score a stock.</span> The sketch draws on Christoph Molnar’s explanation of prediction inputs in <a href="https://tabularfoundationmodels.com/prediction#fig-input-output"><em>Tabular Foundation Models</em>, Figure 4.2</a>.</figcaption>
</figure>

B is sampled at session 30, so its outcome is known at session 50.
It can enter the context refreshed on 51 and help score C on 55.
The simulated trade takes place at the next close.

### How Kumo turns the examples into a score

Kumo turns the rows into vectors that represent their predictors
and, for the historical rows, their known outcomes. In an attention
layer, it compares C’s vector with those of A and B. That comparison
determines how much information from each example goes into an
updated vector for C. The next layer can use the updated vector
to look at the examples again. The network learns how to make
those comparisons during pretraining
([Qu et al., *NVIDIA Kumo Tabular*, §§2 and 5](https://arxiv.org/html/2611.23001v1#S2)).
Kumo predicts a range of quantiles for the outcome. I average them
to get the single score used to rank each stock.

## Subsampling the historical context

The part that took work on my Mac was giving Kumo enough history.
Ridge and LightGBM can score a row from their fitted coefficients or
trees. Kumo also has to process the historical examples it keeps
around for prediction. The more rows I give it, the more work that
takes. NVIDIA recommends a GPU for large contexts in its
[*GPU Sizing Guide*](https://docs.nvidia.com/sdgm/structured-data-models/gpu-sizing).
I wanted to run the test on the CPU, so I looked for rows I could
leave out.

**First, space out the historical dates.** Adjacent 20-session targets
share 19 days of returns. Keeping every date would give Kumo
many outcomes built from almost the same return days. I sample
every 30 trading sessions (roughly six weeks) for expanding Small and
every 40 (roughly eight weeks) for Medium. Both still get examples
from across the history.

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

Figure 2 puts the two steps together in a small example. Here the
20-session grid keeps four dates and the 30-session grid keeps
three. With six stocks per date, that leaves 24 and 18 examples.

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

By the end of the original 1999–2021 comparison, weekly sampling
with the tails filter would still leave about 760,000 labeled rows. I
estimated 35 GiB just to prepare that context with Kumo Small, on
a Mac with 16 GB. That’s why I used wider spacing. At six weeks,
the context dropped to about 127,000 rows and fit on the Mac.

## Running Kumo on a Mac

I ran Kumo on the 10-core Apple M2 Pro CPU of my 14-inch MacBook Pro
(2023), with 16 GB of unified memory. I started with Kumo Large because it
had the best results in NVIDIA’s paper. Large and Small both hit my
10 GiB memory limit on the first group of forecast dates, even with
35,738 context rows for Small. Smaller batches during context
preparation got both through.

In the [TabICL example in Molnar’s classification
chapter](https://tabularfoundationmodels.com/classification#fit-is-faster-than-predict),
`predict` takes longer than `fit`.
Kumo does some of that prediction work up front by preparing a
context once and reusing it. For the largest Medium context in the
1999–2021 test, that preparation took about 13 minutes and scoring
took another eight.

In the original 1999–2021 run, expanding Small took 1 hour 39
minutes and Medium took 2 hours 52 minutes.
I ran Large only on the first group of forecast dates. For Rolling
Small, I sampled the history weekly in a window that grew from
two to three years, then rolled forward. That run took just under
two hours.

Each portfolio needs a new ranking only on its signal dates. Scoring
on those dates cuts the number of predictions to about a fifth of
what daily scoring would require.

## Ranking the whole cross-section

Once I have the forecasts, the first thing I check is how well
each model orders the stocks. All five configurations score the
same 1,387,790 stock-date rows. That’s 1,429 signal dates across
three staggered portfolios, each rebalanced roughly every three weeks.

On each signal date, I rank the model scores and the realized outcomes
for the same stocks, then correlate the two ranks. That Spearman
correlation is the information coefficient, or $\mathrm{IC}_t$.
Figure 3 shows its mean, sample standard deviation and their ratio
across signal dates. The ratio is left unannualized.

$$
\mathrm{ICIR} = \frac{\operatorname{mean}_t(\mathrm{IC}_t)}
                      {\operatorname{sd}_t(\mathrm{IC}_t)}
$$

The windows ending in 2021 use outcomes known by that year-end.
The full history includes five more 2021 signals whose outcomes
became known in 2022.

<figure id="figure-3" class="research-figure responsive-figure">
  {% include blog-chart.html chart="rank" source="/assets/equity-model-comparison/rank-metrics.json?v=5" base="/assets/equity-model-comparison/rank-metrics" mobile="/assets/equity-model-comparison/rank-metrics_mobile" version="6" label="Bar plots for rank IC, standard deviation of IC and ICIR by model through May 2026, with selectable periods." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 3.</span> <span class="caption-title">Rank metrics by period.</span> The full sample has 1,421 shared signal dates with known targets. Each metric keeps the same scale across periods.</figcaption>
</figure>

Both expanding Kumo runs had positive mean IC over 1999–2021 and
again from 2022 to May 2026. In the later window, Medium’s mean IC
was 0.040, below Ridge’s 0.044 and LightGBM’s 0.046. Medium’s IC
varied less from one date to the next than Ridge’s, so its ICIR was
higher, 0.38 versus 0.34. LightGBM led on both measures. Six-week
Small’s mean IC was 0.025, and Rolling Small’s was −0.010.

## Return and risk by score decile

Rank IC looks across the whole ranking. For the portfolios, I care
especially about the stocks at either end. I sort each model’s
scores into deciles on the signal date and trade at the next close.
If a decile has $n$ stocks with a return that day, its daily
return is $\sum_i r_i / n$. I average these returns across
the three schedules on days when all three are available. The spread
is the top decile’s daily return minus the bottom decile’s. I compound
returns, annualize using 252 sessions and use zero cash return for Sharpe.
I use the same decile comparison for Ridge in
[*Combining Multiple Predictors*]({% link _posts/2025-02-09-combining-predictors.md %}#figure-3).

<figure id="figure-4" class="research-figure decile-profile-figure responsive-figure">
  {% include blog-chart.html chart="profiles" source="/assets/equity-model-comparison/deciles.json?v=4" base="/assets/equity-model-comparison/scheduled-decile-profile" mobile="/assets/equity-model-comparison/scheduled-decile-profile_mobile" version="9" label="Return, volatility and Sharpe by stock score decile from 1999 through May 2026, with selectable periods and models." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 4.</span> <span class="caption-title">Return, volatility and Sharpe by score decile.</span> Decile 10 holds the highest scores. All deciles are equal-weighted and shown before costs.</figcaption>
</figure>

Over the full history, LightGBM’s top decile earned about 18% a year
and its bottom decile was roughly flat. For Rolling Small, even the
lowest-scoring stocks earned about 9% a year. That left much less
room for a long–short spread before sizing or trading fees.

## Returns after portfolio construction

The decile spread gives me a first look at the two sides of the
ranking. Now I want to know what happens when I size positions
and pay for trading. I give the optimizer the 75 highest- and
75 lowest-scoring stocks as new candidates. Stocks already held
can stay eligible within a wider rank buffer. Each schedule uses
$5 million of simulated capital, a 7% annual volatility target,
and limits on gross exposure and market beta. Where I can measure
liquidity, I cap trades at 10%
of the previous 21 sessions’ average daily dollar volume. The
sizing method is in
[*From Volatility Scaling to Joint Sizing*]({% link _posts/2026-08-29-joint-sizing.md %}#sizing-under-a-volatility-budget).

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
    <tr class="period-heading"><th colspan="7" scope="rowgroup">1999–May 2026</th></tr>
    <tr><th scope="row">Ridge</th><td>12.2%</td><td>1.34</td><td class="comparison-divider">10.2%</td><td>8.9%</td><td>1.14</td><td>24.5×</td></tr>
    <tr><th scope="row">LightGBM</th><td>17.6%</td><td>2.17</td><td class="comparison-divider">15.5%</td><td>7.6%</td><td>1.94</td><td>24.5×</td></tr>
    <tr><th scope="row">Small, 6 weeks</th><td>11.1%</td><td>1.47</td><td class="comparison-divider">7.7%</td><td>7.3%</td><td>1.05</td><td>43.3×</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>13.4%</td><td>1.70</td><td class="comparison-divider">10.8%</td><td>7.6%</td><td>1.39</td><td>31.4×</td></tr>
    <tr><th scope="row">Small, rolling</th><td>4.7%</td><td>0.61</td><td class="comparison-divider">1.8%</td><td>8.0%</td><td>0.26</td><td>38.0×</td></tr>
  </tbody>
  <tbody>
    <tr class="period-heading"><th colspan="7" scope="rowgroup">2022–May 2026</th></tr>
    <tr><th scope="row">Ridge</th><td>8.7%</td><td>0.91</td><td class="comparison-divider">7.4%</td><td>9.7%</td><td>0.79</td><td>18.8×</td></tr>
    <tr><th scope="row">LightGBM</th><td>9.5%</td><td>1.19</td><td class="comparison-divider">8.2%</td><td>7.9%</td><td>1.04</td><td>20.1×</td></tr>
    <tr><th scope="row">Small, 6 weeks</th><td>4.6%</td><td>0.58</td><td class="comparison-divider">1.6%</td><td>8.4%</td><td>0.23</td><td>48.2×</td></tr>
    <tr><th scope="row">Kumo Medium</th><td>12.0%</td><td>1.43</td><td class="comparison-divider">10.0%</td><td>8.2%</td><td>1.20</td><td>29.2×</td></tr>
    <tr><th scope="row">Small, rolling</th><td>−0.5%</td><td>−0.01</td><td class="comparison-divider">−2.8%</td><td>9.7%</td><td>−0.24</td><td>36.9×</td></tr>
  </tbody>
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

In the 1999–2021 decile spread, six-week Small had the higher
Sharpe of the two expanding Kumo runs. Once I sized the portfolios,
Medium edged ahead before fees, 1.76 versus 1.68. Small also traded
more, at 42.3 times capital per year versus 31.8 for Medium.
After fees, Medium’s lead widened to 1.44 versus 1.24.

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

From 2022 to May 2026, LightGBM still led on rank IC. Medium
had the highest observed net Sharpe, at 1.20 versus 1.04 for
LightGBM and 0.79 for Ridge. Medium’s 0.17 lead over LightGBM
had a paired 95% interval of −0.38 to 0.71 using 21-session blocks.

Medium’s lead came from the long side. Relative to LightGBM, its
long book contributed 5.5 percentage points more annualized
arithmetic P&L and its short book gave up 3.2 points. It traded
29.2 times capital per year versus 20.1 for LightGBM, and the
extra fees cost another 0.6 points.

## How similarly the models trade

Two models can have similar results overall while ranking stocks
differently. Table 2 shows how closely the rankings agreed and
whether the portfolios made or lost money on the same days.
The left side averages score
rank correlations across all signal dates, including dates whose
outcomes fall beyond the test period. The right side averages net
daily return correlations across the three schedules.

<div role="group" aria-labelledby="table-2">
  <p id="table-2" class="table-caption"><span class="caption-number">Table 2.</span> <span class="caption-title">Correlations between models, 1999–May 2026.</span> Rankings use 1,429 signal dates. Net returns use 6,876 trading sessions.</p>
  {% include equity-correlation-matrices.html %}
</div>

Ridge and LightGBM agree more on rankings than either agrees with
expanding Small. Medium is closer to LightGBM than to Ridge
on both rankings and daily returns. Rolling Small’s net daily
returns had a correlation of −0.06 with expanding Small.

## Comparing model sizes on the same context

I could give all three Kumo sizes the same six-week context for
the earliest forecasts. On those 91 signal dates, ICIR rose from
0.62 for Small to 0.72 for Medium and 0.79 for Large. That’s the one
comparison where I could change model size and keep the examples
the same. Over the full history, Medium needed wider spacing, so
the comparison also changes which examples it sees.

## A shorter context with Rolling Small

If the relationships between predictors and outcomes change, recent
examples might help more than old ones. I tried a rolling version of
Small that sampled weekly and dropped older observations as it moved
forward. It changed both the spacing of the dates and how far back the
model could look.

Over 1999–2021, Rolling Small’s ICIR was 0.45 below expanding
Small’s and its net Sharpe was 0.85 lower.
Even in 2012–2021, when the rolling equal-weight decile spread was
less volatile, its Sharpe was lower than expanding Small’s. After
sizing and fees, Rolling Small’s net Sharpe was 0.39 over 1999–2021
and −0.04 in 2017–2021.

The short book explains most of the original gap. The rolling variant
gave up 5.9 percentage points of annualized arithmetic net P&L versus
expanding Small. The short side cost 5.4 points more, the long side
earned 0.7 points less, and lower fees recovered 0.2 points. From
2022 to May 2026 the rolling book lost money even before fees.
Its net return was −2.8% a year.

## How the P&L built up

Table 1 compares annualized results. Figure 5 shows when the gaps
opened and how deep the drawdowns were. The chart starts with each
path visually rescaled to 7% annualized volatility in the selected
window. Clear the checkbox to see the original paths. Open
**Explore** to add Rolling Small.

<figure id="figure-5" class="research-figure portfolio-path-figure responsive-figure">
  {% include blog-chart.html chart="pnl" source="/assets/equity-model-comparison/net-pnl.json?v=7" base="/assets/equity-model-comparison/net-pnl" mobile="/assets/equity-model-comparison/net-pnl_mobile" version="6" label="Cumulative net P&L and drawdown through May 2026, rescaled to 7% annualized volatility by default." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 5.</span> <span class="caption-title">Cumulative P&amp;L and drawdown after fees.</span> I average daily P&amp;L across the three schedules and add it up. The chart shows P&amp;L and drawdown as percentages of fixed capital.</figcaption>
</figure>

LightGBM finished with the highest cumulative P&L over the full
history. At matched volatility, Medium finished ahead of Ridge
and its worst drawdown was smaller. The gap between Medium and Ridge
narrowed at their original volatilities. Select 2022–May 2026 to see
the period in which Medium finished ahead of LightGBM in both views.

## What I found and what I’d test next

What surprised me was that a model pretrained on artificial tables
could take these historical examples and rank stocks at all.
Medium beat Ridge on net Sharpe in both the original and later
periods. LightGBM led over the full history, at 1.94 versus 1.39 for
Medium. Medium pulled ahead from 2022 to May 2026, though the
estimated gap was imprecise.

I’d like to test Kumo Large over the full period, giving it the same
historical rows as Small and Medium. Large ranked better on the
earliest forecasts by ICIR when all three sizes saw the same examples.
The full-period comparison would tell me whether that early advantage
holds up.

I’d also like to give a fixed model more data. With more memory, I
could sample dates more often and test all eligible stocks against
keeping just the tails. Changing one of those at a time would show
whether the extra examples improve the ranking and what they cost
to process. As newer tabular foundation models come out, I’d run them
through the same comparison to see whether they can use more history
at a manageable cost and whether that shows up after trading fees.

## References

- Coqueret, Guillaume, and Tony Guida (2020). [*Training Trees on Tails with Applications to Portfolio Choice*](https://doi.org/10.1007/s10479-020-03539-2). *Annals of Operations Research*, 288(1), 181–221.
- Glasserman, Paul, and Caden Lin (2023). [*Assessing Look-Ahead Bias in Stock Return Predictions Generated By GPT Sentiment Analysis*](https://arxiv.org/abs/2309.17322). arXiv:2309.17322.
- Grinsztajn, Léo, Edouard Oyallon, and Gaël Varoquaux (2022). [*Why Do Tree-Based Models Still Outperform Deep Learning on Typical Tabular Data?*](https://proceedings.neurips.cc/paper_files/paper/2022/hash/0378c7692da36807bdec87ab043cdadc-Abstract-Datasets_and_Benchmarks.html). *NeurIPS*, Datasets and Benchmarks Track.
- Grinsztajn, Léo, et al. (2025). [*TabPFN-2.5: Advancing the State of the Art in Tabular Foundation Models*](https://arxiv.org/abs/2511.08667). Technical report, arXiv:2511.08667.
- Molnar, Christoph. [*Tabular Foundation Models: A Short and Opinionated Guide*](https://tabularfoundationmodels.com/). Online book.
- Müller, Samuel, Noah Hollmann, Sebastian Pineda Arango, Josif Grabocka, and Frank Hutter (2022). [*Transformers Can Do Bayesian Inference*](https://openreview.net/forum?id=KSugKcbNf9). ICLR.
- NVIDIA. [*GPU Sizing Guide*](https://docs.nvidia.com/sdgm/structured-data-models/gpu-sizing). *NVIDIA Kumo Documentation*.
- Qu, Jingang, et al. (2026). [*NVIDIA Kumo Tabular: Pushing the Accuracy–Efficiency Frontier for Tabular Prediction*](https://arxiv.org/abs/2611.23001v1). arXiv:2611.23001, version 1.
- Qu, Jingang, David Holzmüller, Gaël Varoquaux, and Marine Le Morvan (2026). [*TabICLv2: A Better, Faster, Scalable, and Open Tabular Foundation Model*](https://proceedings.mlr.press/v306/qu26a.html). *ICML*, PMLR 306, 102477–102555.

[^tree-benchmark]: [Grinsztajn, Oyallon and Varoquaux (2022)](https://proceedings.neurips.cc/paper_files/paper/2022/hash/0378c7692da36807bdec87ab043cdadc-Abstract-Datasets_and_Benchmarks.html) compared models across 45 datasets and examined how tree ensembles handle irrelevant predictors and irregular relationships.

[^new-benchmarks]: See the comparisons with tuned tree models in the [TabPFN-2.5 report](https://arxiv.org/abs/2511.08667) and the [TabICLv2 paper](https://proceedings.mlr.press/v306/qu26a.html).

[^larger-tables]: [TabPFN-2.5](https://arxiv.org/abs/2511.08667) extended the supported table size from 10,000 to 50,000 rows.
