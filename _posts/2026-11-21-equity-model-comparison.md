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

Random forests and boosted trees like LightGBM have long been strong
choices for tabular data.[^tree-benchmark] That’s starting to change.
Tabular foundation models such as TabPFN and TabICL are beating tuned
tree ensembles on some broad benchmarks.[^new-benchmarks]

What caught my attention was how they use the data. LightGBM fits
trees for the table in front of it. A tabular foundation model comes
pretrained across many tables and reads examples from yours when it
makes a prediction. When those pretraining tables are all synthetic,
the stock history the model sees is the history I supply in the
backtest.

As these models started handling larger tables, I wanted to see how
well that approach could rank stocks.[^larger-tables] I compare one
with Ridge and LightGBM, first on the rankings and then on what those
rankings deliver after trading costs.

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
*posterior predictive distribution*. For a prior-data fitted network,
the table generator sets the prior by choosing which relationships
to show the network and how often. Pretraining teaches the network
to approximate this kind of prediction directly from the examples.
[Molnar’s chapter on prior-data fitted networks](https://tabularfoundationmodels.com/prior-data-fitted-networks)
develops the idea from [Müller et al.](https://openreview.net/forum?id=KSugKcbNf9).

## Testing a tabular foundation model on stocks

### What the model could know on each date

When I backtest a model, I need to know what it could have seen on
each forecast date. Say I give a language model an old announcement
of a proposed merger. It may already have read news about how the
deal ended. If it did, that later information can influence its
answer even when I give it just the announcement. One way to guard
against this is to start the backtest after the last date covered
by the training data, if I can verify that date. Glasserman and Lin
explore the issue for
[*GPT-based news sentiment*](https://arxiv.org/abs/2309.17322).

I chose NVIDIA’s Kumo Tabular for the stock test. Its generated
tables teach it how to use examples, and the historical rows I
give it supply the evidence about stocks
([Qu et al., *NVIDIA Kumo Tabular*, §3](https://arxiv.org/html/2611.23001v1#S3)).
I keep its weights fixed throughout the backtest. At each forecast
I use predictors available on that date. A historical row can enter
the context at a refresh only if its 20-session outcome is already known.

### Research setup

Ridge, LightGBM and the Kumo runs all use the same target and 80
predictors. For the target, I take each stock’s Sharpe ratio over
the next 20 sessions and rank it against its sector peers. I rank the
predictors across the whole stock universe on each date.
I describe how I build the target and predictors in
[*Combining Multiple Predictors: The Linear Case*]({% link _posts/2025-02-09-combining-predictors.md %}#what-i-ask-the-model-to-predict).

Ridge and LightGBM fit on past data and score the dates that follow.
I refresh Kumo’s context on the LightGBM refit dates. For Kumo,
I test Small and Medium with expanding histories, where the pool
of examples grows from the same January 1995 start. I also test
Rolling Small, which keeps only recent history. The test runs from
1999 through May 27, 2026. I show 2022 onward separately to see
whether the same patterns turn up in the more recent years.

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
Kumo can process A and B before it sees C, so it caches their
representations for reuse on later forecasts. For C, it predicts
quantiles from the low end of the outcome distribution to the high
end. I average those quantiles to get one score per stock.

## Subsampling the historical context

A long history makes prediction expensive because Kumo has to
prepare, store and use the context. Near the end of the 1999–2021
run, sampling one historical date a week would have left Kumo Small
with about 760,000 labeled rows, even after the tails cut below.
I estimated that the main buffers alone would take about 35 GiB
to prepare that context. My Mac has 16 GB of memory. NVIDIA recommends
a GPU for large contexts in its
[*GPU Sizing Guide*](https://docs.nvidia.com/sdgm/structured-data-models/gpu-sizing).
I wanted to run the test on the CPU, so I reduced the context in
two ways.

**First, space out the historical dates.** Two targets one session
apart share 19 of their 20 return days. Keeping every date would give
Kumo many examples built from nearly the same returns. I sample every
30 trading sessions (roughly six weeks) for expanding Small and every
40 (roughly eight weeks) for Medium, whose context is more expensive
to process. With six-week sampling, that late Small context came
down to about 127,000 rows and fit on the Mac.

**Then, keep the tails on each sampled date.** I sort eligible
stocks on that date by their **realized target**, the rank of each
stock’s 20-session Sharpe ratio within its sector. I keep roughly
the lowest and highest 30% across the date. That saves about 40%
of the rows while keeping examples of the unusually strong and weak
outcomes I care about for a long–short portfolio. The middle may
contain useful examples too. I’d need to give the same model all
the stocks on those dates to see what dropping the middle does to
ranking accuracy.

In [*Training Trees on Tails with Applications to Portfolio
Choice*](https://doi.org/10.1007/s10479-020-03539-2), Coqueret and
Guida (2020) tested this idea with boosted trees.
Keeping the lowest and highest 20% of their training outcomes cut
backtest time by roughly 60% and gave a similar return spread
between the highest- and lowest-ranked portfolios.

Figure 2 uses two illustrative grids. Sampling every 20 sessions
keeps four dates, and sampling every 30 keeps three. The tails filter
keeps six of the ten stocks on each selected date, leaving 24 or 18
labeled rows.

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

At each context refresh, as in Figure 1, I apply these cuts to the
history with known outcomes. The portfolios have three staggered
signal calendars, each with a rebalance roughly every three weeks.
Even with six weeks between historical examples, Kumo can score
every eligible stock on those signal dates using the latest context.

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

Scoring on the three portfolios’ shared set of signal dates takes
about a fifth as many scoring days as running daily forecasts.

## Ranking the whole cross-section

Once I have the forecasts, the first thing I check is how well
each model orders the stocks. On each signal date, I rank the model
scores and the realized outcomes for the same stocks, then correlate
the two ranks. That Spearman
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
  <figcaption class="figure-caption"><span class="caption-number">Figure 3.</span> <span class="caption-title">Rank metrics by period.</span> The full-period rank metrics use 1,421 signal dates with realized outcomes. Each metric keeps the same scale across periods.</figcaption>
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

The decile spread weights all names in each tail equally. Sizing
positions changes which stocks drive returns, and trading costs can
change the ordering again. I give the optimizer the 75 highest- and
75 lowest-scoring stocks as new candidates. Stocks already held
can stay eligible within a wider rank buffer. Each schedule uses
$5 million of simulated capital, a 7% annual volatility target,
and limits on gross exposure and market beta. Where I can measure
liquidity, I cap trades at 10%
of the previous 21 sessions’ average daily dollar volume. The
sizing method is in
[*From Volatility Scaling to Joint Sizing*]({% link _posts/2026-08-29-joint-sizing.md %}#sizing-under-a-volatility-budget).

The optimizer uses a turnover penalty of 5 basis points for
LightGBM and Kumo and 2.5 for Ridge. This affects how much it
trades. The simulated execution fees are 7.5 basis points on
long trades and 10 on shorts through 2010, then 5 and 7.5.
I use the same holdings for the before- and after-fee figures.
I compute return, volatility, Sharpe and turnover for each
schedule, then average across the three. Two-way turnover adds
all dollars bought and sold across both sides, divides by fixed
capital, and annualizes the average over trading sessions.

I also tried 100 and 150 new candidates per side. This lets me
see how much the results depend on how far into the ranking the
optimizer can look for new positions. Table 1 shows all three
choices with the same forecasts, sizing rules and fees.

<div id="table-5" class="equity-breadth">
<fieldset class="equity-breadth-controls">
  <legend>New candidates per side</legend>
  {% for breadth in site.data.equity_portfolio_breadth %}
  <input type="radio" name="equity-breadth" id="equity-breadth-{{ breadth.count }}" value="{{ breadth.count }}"{% if forloop.first %} checked{% endif %} aria-controls="table-1">
  <label for="equity-breadth-{{ breadth.count }}">{{ breadth.count }}</label>
  {% endfor %}
</fieldset>
<div id="table-6" class="research-table-scroll" tabindex="0" role="region" aria-label="Portfolio results before and after execution fees, with turnover">
<table id="table-1" class="research-table comparison-table equity-comparison-table">
  <caption><span class="caption-number">Table 1.</span> <span class="caption-title">Portfolio performance before and after fees.</span> Returns are compounded. Turnover is two-way traded notional per year, in multiples of fixed capital. All figures are annualized.</caption>
  <colgroup span="1"></colgroup><colgroup span="2"></colgroup><colgroup span="3"></colgroup><colgroup span="1"></colgroup>
  <thead>
    <tr><th scope="col" rowspan="2">Model</th><th scope="colgroup" colspan="2">Before fees</th><th scope="colgroup" colspan="3" class="comparison-divider">After fees</th><th scope="col" rowspan="2">Turnover</th></tr>
    <tr><th scope="col">Return</th><th scope="col">Sharpe</th><th scope="col" class="comparison-divider">Return</th><th scope="col">Vol.</th><th scope="col">Sharpe</th></tr>
  </thead>
  {% for breadth in site.data.equity_portfolio_breadth %}
    {% for period in breadth.periods %}
    <tbody data-candidates="{{ breadth.count }}">
      <tr class="period-heading"><th colspan="7" scope="rowgroup">{{ period.label | escape }}</th></tr>
      {% for row in period.rows %}
      <tr>
        <th scope="row">{{ row.model | escape }}</th>
        {% for metric in row.metrics %}
        <td{% if forloop.index == 3 %} class="comparison-divider"{% endif %}>{{ metric | escape }}</td>
        {% endfor %}
      </tr>
      {% endfor %}
    </tbody>
    {% endfor %}
  {% endfor %}
</table>
</div>
</div>

In the 1999–2021 decile spread, six-week Small had the higher
Sharpe of the two expanding Kumo runs. Once I sized the portfolios
with 75 new candidates per side, Medium edged ahead before fees,
1.76 versus 1.68. Small also traded
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

From 2022 to May 2026, LightGBM still led on rank IC. With
75 candidates per side, Medium had the highest net Sharpe,
at 1.20 versus 1.04 for LightGBM and 0.79 for Ridge. The paired
95% interval for Medium’s Sharpe minus LightGBM’s ran from −0.38
to 0.71 using 21-session blocks.

Medium’s higher average net P&L came from the long side. Relative
to LightGBM, its long book contributed 5.5 percentage points more annualized
arithmetic P&L and its short book gave up 3.2 points. It traded
29.2 times capital per year versus 20.1 for LightGBM, and the
extra fees cost another 0.6 points.

At 100 candidates per side, Medium and LightGBM were closer, with
after-fee Sharpes of 1.18 and 1.14. At 150, LightGBM moved ahead,
at 1.24 versus 1.12 for Medium. Both models traded more
as I gave the optimizer more names. The paired intervals for
the later Sharpe gap include zero at all three widths. Over
the full history, LightGBM led on net Sharpe at every width.

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
2022 to May 2026 the rolling book lost money before fees at
every width. Its annual net return was −2.8% with 75 candidates
per side and −3.9% with 150.

## How the P&L built up

Table 1 compounds returns. Figure 5 adds up daily net P&L as a
share of fixed capital, so you can see when the gaps opened and
how deep the drawdowns were. The chart starts with each path
visually rescaled to 7% annualized volatility in the selected
window. Clear the checkbox to see the original paths. Open
**Explore** to add Rolling Small.

<figure id="figure-5" class="research-figure portfolio-path-figure responsive-figure">
  {% include blog-chart.html chart="pnl" source="/assets/equity-model-comparison/net-pnl.json?v=7" base="/assets/equity-model-comparison/net-pnl" mobile="/assets/equity-model-comparison/net-pnl_mobile" version="6" label="Cumulative net P&L and drawdown through May 2026, rescaled to 7% annualized volatility by default." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 5.</span> <span class="caption-title">Cumulative P&amp;L and drawdown after fees.</span> These portfolios use 75 new candidates per side. I average daily P&amp;L across the three schedules and add it up. Both panels show percentages of fixed capital.</figcaption>
</figure>

LightGBM finished with the highest cumulative P&L over the full
history. At matched volatility, Medium finished ahead of Ridge
and its worst drawdown was smaller. The gap between Medium and Ridge
narrowed at their original volatilities. Select 2022–May 2026 to see
the period in which Medium finished ahead of LightGBM in both views.

## What I found and what I’d test next

What surprised me was that a model pretrained on artificial tables
could take these historical examples and rank stocks at all.
Medium beat Ridge on net Sharpe at each candidate width over the
full history and from 2022 onward. LightGBM had the highest
full-period net Sharpe at all three widths. In the later period,
the ordering of Medium and LightGBM changed with the number
of candidates. Rolling Small struggled, particularly on the short side.

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
