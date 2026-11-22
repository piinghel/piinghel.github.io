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

LightGBM and XGBoost have long been regulars near the top of
Kaggle’s tabular competitions, and random forests have featured
in winning solutions too.[^tree-benchmark] That track record is
what made me pay attention when tabular foundation models like
TabPFN and TabICL started beating tuned tree ensembles on benchmark
datasets.[^new-benchmarks] As these models got better at handling
larger tables, I wanted to see how one would do at ranking
stocks.[^larger-tables]

An 8 km delivery is enough to see what each model needs to make
a prediction. From there, I give Ridge, LightGBM and a tabular
foundation model the same stock predictors and compare their
rankings. Then I see whether a better ranking leads to a better
portfolio after trading costs.

## A pretrained model for tables

I’m still getting to know these models. What helped me make sense
of them was Christoph Molnar’s excellent
[*Tabular Foundation Models*](https://tabularfoundationmodels.com/).

### What the model needs to make a prediction

Suppose I want to predict how long an 8 km delivery will take at
5 p.m. My table has past deliveries, with the distance, time of
day and actual delivery time for each one. For the new order,
I know the distance and time of day. The delivery time is blank.

With Ridge, `fit()` learns coefficients from the completed
deliveries. LightGBM fits trees from those examples. Either way,
`predict()` only needs the new order’s distance and time of day.
The coefficients or trees already carry what the model learned
from the earlier deliveries.

A useful comparison here is k-nearest neighbors. To predict the
delivery time, I go back to the table and look for past orders
with a similar distance and start time. If the two nearest took
25 and 35 minutes, I’d predict 30 minutes. I still need the old
orders to make that prediction.

A tabular foundation model also gets the past deliveries and
their known outcomes at prediction time. Those rows are its
*context*. With k-nearest neighbors, I choose what counts as
a similar trip. The network has already learned how to combine
information from the examples.

<figure id="figure-1" class="research-figure responsive-figure">
  {% include equity-delivery-context-sketch.html %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 1.</span> <span class="caption-title">Two ways to use the past deliveries.</span> The last row is the new order. The shaded rows are its two nearest neighbors.</figcaption>
</figure>

Inside the network, the new order and the historical examples
become vectors it can compare. Through *attention*, the
representation of the new order picks up information from the
examples. One comparison might bring in useful information about
similar distances. Another might help it pick up that rush hour
matters more for long trips. The network turns the resulting
representation into an estimate for the missing delivery time.

If I give the same network a different city’s deliveries, the
same order can get a different estimate. The network weights
stay fixed. That’s *in-context learning*.

Many tabular foundation models use `fit()` and `predict()` so
the interface feels familiar if you’ve used scikit-learn. Here,
`fit()` gets the examples ready for `predict()`.

### Pretraining across many tables

Many tabular foundation models are pretrained on synthetic data.
A generator makes tables with different relationships between
predictors and outcomes. In one table, a single predictor might
explain most of the outcome. In another, the effect of one
predictor might depend on a second.

Figure 2 shows two such practice tables. The inputs are the same,
but the generator has used a different rule to produce the outcomes
in each table. The network sees some outcomes and tries to predict
the missing ones. The training procedure knows the hidden outcomes
and uses the resulting errors to update the network’s weights.

<figure id="figure-2" class="research-figure responsive-figure">
  {% include equity-synthetic-pretraining-sketch.html %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 2.</span> <span class="caption-title">Two prediction tasks during pretraining.</span> Errors on the hidden outcomes update the same network.</figcaption>
</figure>

As the rules change from table to table, the useful skill is
working out what matters from the labeled examples. Once trained,
the network can use that skill on a new table with its weights fixed.
Molnar shows how those tables are generated in
[*Tabular Foundation Models*, Chapter 5](https://tabularfoundationmodels.com/pretraining).

### How an example changes the forecast

Go back to the deliveries and imagine two possible rules. Under
the first, long routes usually take a long time. Under the second,
they usually take a long time during rush hour and are quick at
other times. Start with both rules equally likely and suppose each
rule gives the right outcome nine times out of ten, independently
from one delivery to the next.

Now I see a long route outside rush hour that was delivered quickly.
That outcome is nine times as likely under the second rule, so I
update its probability to 90%. For another long route outside rush
hour, the probability of a quick delivery is 90% under the second
rule and 10% under the first. Weight those forecasts by the new
probabilities of the rules and I get 0.9 × 0.9 + 0.1 × 0.1, or 82%.

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

I picked NVIDIA’s Kumo Tabular for the stock test. NVIDIA
pretrained it entirely on synthetic data
([Qu et al., *NVIDIA Kumo Tabular*, §3](https://arxiv.org/html/2611.23001v1#S3)).
Each time I ask Kumo for a ranking, it sees the stock predictors
for that day alongside examples from the past. I only include
a past example once I know how the stock did over the following
20 trading sessions.

### Research setup

Ridge, LightGBM and Kumo all use the same 80 predictors. On each
date, I rank stocks across the full universe on each predictor
and put the ranks on a −1 to +1 scale. For example, the stocks
with the highest momentum end up near +1 for that predictor.

For the target, I take each stock’s Sharpe ratio over the following
20 trading sessions. I rank those outcomes on the same −1 to +1
scale within each sector on each date. A high target means the
stock did well against its sector peers. The models are trying to
identify which stocks are likely to do best within their sectors.
I describe the predictors and target in more detail in
[*Combining Multiple Predictors: The Linear Case*]({% link _posts/2025-02-09-combining-predictors.md %}#what-i-ask-the-model-to-predict).

Ridge and LightGBM fit on past data and score the dates that follow.
I put together a new set of examples for Kumo whenever I fit
LightGBM again. For Small and Medium, I let the history grow from
the same January 1995 start. I also test
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

Figure 3 illustrates the two workflows with raw momentum as its
only predictor.
LightGBM fits trees on historical rows A and B and scores C
by following its momentum through those trees. With Kumo, `fit()`
prepares and caches information from A and B, and `predict()` uses
that context alongside C’s momentum. C’s outcome is still unknown.

<figure id="figure-3" class="research-figure responsive-figure stock-scoring-figure">
  <picture>
    <source media="(max-width: 600px)" srcset="{{ '/assets/equity-model-comparison/in-context-sketch-mobile.webp' | relative_url }}?v=2" width="1024" height="1536">
    <img src="{{ '/assets/equity-model-comparison/in-context-sketch.webp' | relative_url }}?v=2" width="1536" height="1024" loading="lazy" decoding="async" alt="LightGBM fits trees on labeled stocks A and B, then scores C from its momentum. Kumo scores C with A and B as context. Outcomes must be known by session 50. The context is built on 51, the forecast is on 55, and the simulated trade is on 56.">
  </picture>
  <figcaption class="figure-caption"><span class="caption-number">Figure 3.</span> <span class="caption-title">How LightGBM and Kumo score a stock.</span> The sketch draws on Christoph Molnar’s explanation of prediction inputs in <a href="https://tabularfoundationmodels.com/prediction#fig-input-output"><em>Tabular Foundation Models</em>, Figure 4.2</a>.</figcaption>
</figure>

B is sampled at session 30, so its outcome is known at session 50.
I can include B when I put the examples together on session 51
and use those same examples to score C on 55.
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
I estimated it would take about 35 GiB of memory just to prepare
that context, well above what my Mac could provide. NVIDIA recommends
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

Figure 4 uses two illustrative grids. Sampling every 20 sessions
keeps four dates, and sampling every 30 keeps three. The tails filter
keeps six of the ten stocks on each selected date, leaving 24 or 18
labeled rows.

<figure id="figure-4" class="research-figure responsive-figure">
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
  <figcaption class="figure-caption"><span class="caption-number">Figure 4.</span> <span class="caption-title">Which historical rows enter Kumo’s context.</span> Filled marks show the dates and stocks selected in this example.</figcaption>
</figure>

When I put together a set of examples, I apply these cuts to the
history with known outcomes. The portfolios have three staggered
signal calendars, each with a rebalance roughly every three weeks.
Even with six weeks between historical examples, Kumo can score
every eligible stock on those signal dates using the latest context.

## Running Kumo on a Mac

I ran Kumo on the 10-core Apple M2 Pro CPU of my 14-inch MacBook Pro
(2023), with 16 GB of unified memory.

In the [TabICL example in Molnar’s classification
chapter](https://tabularfoundationmodels.com/classification#fit-is-faster-than-predict),
`predict` takes longer than `fit`.
Kumo does some of that prediction work up front by preparing a
context once and reusing it. For the largest Medium context in the
1999–2021 test, that preparation took about 13 minutes and scoring
took another eight.

## Ranking the whole cross-section

Once I have the forecasts, the first thing I check is how well
each model orders the stocks. For a signal date with known outcomes,
I rank the model scores and the realized outcomes for the same stocks,
then correlate the two ranks. That Spearman correlation is the
information coefficient, or $\mathrm{IC}_t$.
Figure 5 shows its mean, sample standard deviation and their ratio
across signal dates. The ratio is left unannualized.

$$
\mathrm{ICIR} = \frac{\operatorname{mean}_t(\mathrm{IC}_t)}
                      {\operatorname{sd}_t(\mathrm{IC}_t)}
$$

<figure id="figure-5" class="research-figure responsive-figure">
  {% include blog-chart.html chart="rank" source="/assets/equity-model-comparison/rank-metrics.json?v=5" base="/assets/equity-model-comparison/rank-metrics" mobile="/assets/equity-model-comparison/rank-metrics_mobile" version="6" label="Bar plots for rank IC, standard deviation of IC and ICIR by model through May 2026, with selectable periods." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 5.</span> <span class="caption-title">Rank metrics by period.</span> Each metric keeps the same scale across periods.</figcaption>
</figure>

Both expanding Kumo runs had positive mean IC over 1999–2021 and
again from 2022 to May 2026. In the later window, mean IC was 0.044
for Ridge, 0.046 for LightGBM and 0.040 for Medium. Medium’s IC
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

<figure id="figure-6" class="research-figure decile-profile-figure responsive-figure">
  {% include blog-chart.html chart="profiles" source="/assets/equity-model-comparison/deciles.json?v=4" base="/assets/equity-model-comparison/scheduled-decile-profile" mobile="/assets/equity-model-comparison/scheduled-decile-profile_mobile" version="9" label="Return, volatility and Sharpe by stock score decile from 1999 through May 2026, with selectable periods and models." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 6.</span> <span class="caption-title">Return, volatility and Sharpe by score decile.</span> Decile 10 holds the highest scores. All deciles are equal-weighted and shown before costs.</figcaption>
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

The optimizer uses a turnover penalty of 2.5 basis points for
Ridge and 5 for LightGBM and Kumo. This affects how much it
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

From 2022 to May 2026, LightGBM still led on rank IC. With
75 candidates per side, net Sharpe was 0.79 for Ridge, 1.04 for
LightGBM and 1.20 for Medium, the highest of the five runs. The paired
95% interval for Medium’s Sharpe minus LightGBM’s ran from −0.38
to 0.71 using 21-session blocks.

Medium’s higher average net P&L came from the long side.
I annualize the differences in average daily P&L so the long,
short and fee contributions add up. Compared with LightGBM,
Medium gained 5.5 percentage points on the long side, gave up
3.2 points on the short side and paid 0.6 points more in fees.

At 100 candidates per side, Medium and LightGBM were closer, with
after-fee Sharpes of 1.18 and 1.14. At 150, LightGBM moved ahead,
at 1.24 versus 1.12 for Medium. Both models traded more
as I gave the optimizer more names. The paired intervals for
the later Sharpe gap include zero at all three widths. Over
the full history, LightGBM led on net Sharpe at every width.

## How the P&L built up

Figure 7 shows when those gaps opened and how deep the drawdowns
were. The curves add up daily net P&L as a share of fixed capital.
Table 1 gives compounded returns. The chart opens with each path
rescaled to 7% annualized volatility in the selected window.
Clear the checkbox to see the original paths. Open **Explore** to
add Rolling Small.

<figure id="figure-7" class="research-figure portfolio-path-figure responsive-figure">
  {% include blog-chart.html chart="pnl" source="/assets/equity-model-comparison/net-pnl.json?v=7" base="/assets/equity-model-comparison/net-pnl" mobile="/assets/equity-model-comparison/net-pnl_mobile" version="6" label="Cumulative net P&L and drawdown through May 2026, rescaled to 7% annualized volatility by default." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 7.</span> <span class="caption-title">Cumulative P&amp;L and drawdown after fees.</span> These portfolios use 75 new candidates per side. I average daily P&amp;L across the three schedules and add it up. Both panels show percentages of fixed capital.</figcaption>
</figure>

LightGBM finished with the highest cumulative P&L over the full
history. At matched volatility, Medium finished ahead of Ridge
and its worst drawdown was smaller. The gap between Medium and Ridge
narrowed at their original volatilities. Select 2022–May 2026 to see
the period in which Medium finished ahead of LightGBM in both views.

## How similarly the models trade

Two portfolios can finish close together even if their models
rank stocks differently. The left side of Table 2 shows how
closely the rankings agree, averaging rank correlations across
signal dates. The right side shows how closely the portfolios
move together, averaging daily net return correlations across
the three schedules.

<div role="group" aria-labelledby="table-2">
  <p id="table-2" class="table-caption"><span class="caption-number">Table 2.</span> <span class="caption-title">Correlations between models, 1999–May 2026.</span></p>
  {% include equity-correlation-matrices.html %}
</div>

Medium is closer to LightGBM than to Ridge on both the stock
rankings and the daily portfolio returns.

## Comparing model sizes on the same context

Over the full test, Medium used more widely spaced historical
dates than Small. To compare the sizes on the same examples, I
gave Small, Medium and Large the same six-week context for the
earliest forecasts. On those 91 signal dates, ICIR was 0.62
for Small, 0.72 for Medium and 0.78 for Large.

## A shorter context with Rolling Small

If the relationships between predictors and outcomes change, recent
examples might help more than old ones. I tried a rolling version of
Small that sampled weekly, started with two years of history, and
began dropping older observations once the window reached three
years. That gave it more closely spaced examples from a shorter
history.

Over 1999–2021, Rolling Small ranked stocks worse than expanding
Small and had a net Sharpe of 0.39 versus 1.24. The short book
accounted for most of the gap in average net P&L. From 2022 to
May 2026, Rolling Small lost money before fees at every candidate
width.

## What I found and what I’d test next

What surprised me was that a model pretrained on artificial tables
could take these historical examples and rank stocks at all.
Medium beat Ridge on net Sharpe at each candidate width over the
full history and from 2022 onward. LightGBM had the highest
full-period net Sharpe at all three widths. In the later period,
the ordering of Medium and LightGBM changed with the number
of candidates. Rolling Small struggled, particularly on the short side.

I’d like to compare Kumo Small, Medium and Large over the full
period, giving all three the same historical examples.

I’d also like to give a fixed model more data. With more memory, I
could sample dates more often and test all eligible stocks against
keeping just the tails. Changing one of those at a time would show
whether the extra examples improve the ranking and what they cost
to process. As newer tabular foundation models come out, I’d run them
through the same comparison to see whether they can use more history
at a manageable cost and whether that shows up after trading fees.

## References

- Coqueret, Guillaume, and Tony Guida (2020). [*Training Trees on Tails with Applications to Portfolio Choice*](https://doi.org/10.1007/s10479-020-03539-2). *Annals of Operations Research*, 288(1), 181–221.
- Grinsztajn, Léo, Edouard Oyallon, and Gaël Varoquaux (2022). [*Why Do Tree-Based Models Still Outperform Deep Learning on Typical Tabular Data?*](https://proceedings.neurips.cc/paper_files/paper/2022/hash/0378c7692da36807bdec87ab043cdadc-Abstract-Datasets_and_Benchmarks.html). *NeurIPS*, Datasets and Benchmarks Track.
- Grinsztajn, Léo, et al. (2025). [*TabPFN-2.5: Advancing the State of the Art in Tabular Foundation Models*](https://arxiv.org/abs/2511.08667). Technical report, arXiv:2511.08667.
- Molnar, Christoph. [*Tabular Foundation Models: A Short and Opinionated Guide*](https://tabularfoundationmodels.com/). Online book.
- Müller, Samuel, Noah Hollmann, Sebastian Pineda Arango, Josif Grabocka, and Frank Hutter (2022). [*Transformers Can Do Bayesian Inference*](https://openreview.net/forum?id=KSugKcbNf9). ICLR.
- NVIDIA. [*GPU Sizing Guide*](https://docs.nvidia.com/sdgm/structured-data-models/gpu-sizing). *NVIDIA Kumo Documentation*.
- Qu, Jingang, et al. (2026). [*NVIDIA Kumo Tabular: Pushing the Accuracy–Efficiency Frontier for Tabular Prediction*](https://arxiv.org/abs/2611.23001v1). arXiv:2611.23001, version 1.
- Qu, Jingang, David Holzmüller, Gaël Varoquaux, and Marine Le Morvan (2026). [*TabICLv2: A Better, Faster, Scalable, and Open Tabular Foundation Model*](https://proceedings.mlr.press/v306/qu26a.html). *ICML*, PMLR 306, 102477–102555.

[^tree-benchmark]: [Chen and Guestrin (2016)](https://arxiv.org/abs/1603.02754) document XGBoost’s early Kaggle results, and [Ambrosm’s winning Kaggle write-up](https://www.kaggle.com/competitions/bench-tab-v2/writeups/ambrosm-1-solution) uses boosted trees and random forests. [Grinsztajn, Oyallon and Varoquaux (2022)](https://proceedings.neurips.cc/paper_files/paper/2022/hash/0378c7692da36807bdec87ab043cdadc-Abstract-Datasets_and_Benchmarks.html) compare tree ensembles and neural networks across 45 datasets.

[^new-benchmarks]: See the comparisons with tuned tree models in the [TabPFN-2.5 report](https://arxiv.org/abs/2511.08667) and the [TabICLv2 paper](https://proceedings.mlr.press/v306/qu26a.html).

[^larger-tables]: [TabPFN-2.5](https://arxiv.org/abs/2511.08667) extended the supported table size from 10,000 to 50,000 rows.
