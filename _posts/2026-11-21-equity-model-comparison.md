---
layout: post
interactive_charts: true
title: "Can Tabular Foundation Models Rank Stocks?"
description: "How tabular foundation models learn from examples, and how one compares with Ridge and LightGBM for stock ranking."
date: 2026-11-21
last_modified_at: 2026-11-23
categories: ["Signals"]
article_label: Signals · Tabular models
permalink: /quants/equity-model-comparison.html
---

Tree-based models such as LightGBM, XGBoost, and random forests have
a long track record on tabular data. LightGBM and XGBoost in particular
have repeatedly featured in top Kaggle solutions.[^tree-benchmark]

Tabular foundation models such as TabPFN and TabICL caught my
attention when they started beating tuned tree ensembles on some
benchmarks.[^new-benchmarks] As these models got better at handling
larger tables,[^larger-tables] I wanted to see whether the same
approach could improve stock rankings. I give Kumo, Ridge, and
LightGBM the same stock predictors, then compare their rankings
and the portfolios they produce after trading costs.

## Tabular foundation models

I got a lot out of Christoph Molnar’s book *Tabular Foundation
Models*. His diagrams helped me picture what happens to a table
from the inputs all the way to the predictions. If you want to
dig into that, I’d start with his
[chapter on in-context learning](https://tabularfoundationmodels.com/prediction).

### What goes into a table

A table gives each observation a row and each variable a column.
In this test, an observation is a stock on a particular date.
Its row contains predictors such as momentum and volatility, plus
the outcome I want to predict once that outcome is known. The
rows I want to score today have the predictors available now and
an outcome that will only be available later. The prediction task
is to fill in that last piece using the historical rows.

What makes a general model for tables hard to build is how much
the columns can vary. Pixels in an image have a common meaning
and a spatial relationship to their neighbors. Words in a sentence
get part of their meaning from their order. In a table, the column
next to volatility might hold a sector code or a date. If I move
the volatility column and keep its identity, I still have the
same measurement. A different table can have different columns,
units, and relationships between predictors and outcomes.

### Fit and predict

The interface looks familiar. With a model that follows the
scikit-learn convention, I can write the same two calls for
Ridge, LightGBM, k-nearest neighbors, or a tabular foundation model.

```python
model.fit(X_history, y_history)
scores = model.predict(X_today)
```

For Ridge, `fit()` estimates a coefficient for each predictor by
balancing the squared errors on the historical rows against a
penalty on large coefficients. The fitted model carries those
coefficients and an intercept into `predict()`. I can take a new
stock’s predictors, multiply each by its coefficient, and add
the results and the intercept to get a score.

LightGBM fits a gradient-boosted ensemble of decision trees. It
adds trees one at a time to improve the predictions from the
trees already fitted. Each tree splits the predictor space into
regions. At prediction time, a stock follows a path through each
tree and receives a contribution from the leaf it lands in.
LightGBM adds those contributions to produce the score. Ridge
and LightGBM both carry a fitted rule into prediction, so the new
stock’s predictors are enough to compute its score.

K-nearest neighbors (kNN) is a useful bridge. Its `fit()` keeps the
labeled examples, sometimes building an index to make the search
faster. Each `predict()` finds the $k$ closest examples to the
new row in predictor space. A simple regression version averages
their outcomes. The choice of distance matters. If one predictor
has a much larger numerical scale, it can dominate the search
unless I rescale the inputs.

### Pretraining across tables

A foundation model is pretrained on a broad range of data so it can
be reused on new tasks. For the tabular models here, a single
pretraining task is a table with some outcomes visible and some
held back. The network gets the predictors for all those rows and
uses the visible outcomes as examples. Its job is to predict the
held-out outcomes. A training batch can include many tables, and
the prediction errors from those tasks update the same network.

Figure 1 shows why the variety of tables matters. The predictor
values are identical in the two tables. In Table A the outcome is
twice the first predictor. In Table B the second predictor adds
three when it is one. The last row therefore has an outcome of
8 in Table A and 11 in Table B. Its predictors are the same in
both cases. The labeled rows are the information the network can
use to work out which relationship applies.

<figure id="figure-1" class="research-figure responsive-figure">
  {% include equity-synthetic-pretraining-sketch.html %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 1.</span> <span class="caption-title">Two prediction tasks during pretraining.</span> The predictors are identical. The labeled rows give the model a clue about which relationship applies.</figcaption>
</figure>

NVIDIA pretrained Kumo on synthetic tables. The generator varies
the rules linking columns and also varies things such as noise
and missing observations. That choice matters because it determines
the kinds of relationships the model gets to practice on. The stock
test asks how well that way of using examples carries over to a
different problem.
[Qu et al., *NVIDIA Kumo Tabular*, §§3–4](https://arxiv.org/html/2611.23001v1#S3)

### Using the labeled rows at prediction time

Take the bottom row of Table A and run a two-nearest-neighbors
regressor using only the first predictor to measure distance.
From a value of 4, the two closest observed values are 3 and 2.
Their outcomes are 6 and 4, so uniform averaging gives a
prediction of $(6 + 4)/2 = 5$. Changing the distance rule or
the number of neighbors could change the answer. This makes
the idea of predicting from examples concrete.

Kumo also draws on labeled examples when it makes a prediction.
Their predictors and known outcomes form the *context*, much like
the examples in a prompt. The network learned during pretraining
how to represent the inputs and how to use those representations
to combine information from the context. I can give it a different
history and get a different forecast with the same network weights.
That is *in-context learning*. In my backtest, Kumo’s `fit()`
prepares the labeled history as context. The `predict()` call takes
the new predictors and scores them using that prepared context.

### From a table to a forecast

Figure 2 follows the data through Kumo. It starts by representing
groups of cells as vectors of numbers. The table encoder combines
information along columns and within rows. Looking down a column
helps represent a value relative to other values of the same
predictor. Looking across a row lets the encoder represent several
predictors together. It produces one vector, or *embedding*, for
each row.

<figure id="figure-2" class="research-figure responsive-figure">
  {% include tabular-inference-diagram.html %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 2.</span> <span class="caption-title">From a table to a prediction.</span> The labeled rows feed into the new row’s representation. The output shows three of the quantile levels Kumo predicts.</figcaption>
</figure>

The next stage uses *attention* to compare a new row’s embedding
with the labeled rows, whose representations also carry their known
outcomes. The comparisons give the model weights for gathering
information from different examples. As the row passes through
successive layers, it can update its vector and use the updated
representation to make the next set of comparisons. Kumo reads
out a set of target quantiles from the final vector. Those
quantiles describe a range of outcomes given the predictors
and the supplied history.
[Qu et al., *NVIDIA Kumo Tabular*, §2](https://arxiv.org/html/2611.23001v1#S2)

The labeled rows only attend to one another, so Kumo can cache
the information it needs from them. I reuse that cache to score
each new cross-section until the next refit. A longer history
gives the model more examples and a larger context to prepare
and keep in memory. That trade-off matters when the table grows
at each refit.

## The stock-ranking test

Ridge, LightGBM and Kumo all use the same 80 predictors. On each
date, I cross-sectionally rank each predictor across the full
stock universe and put the ranks on a −1 to +1 scale.

For the target, I take each stock’s Sharpe ratio over the following
20 trading days and rank it on the same scale within its sector
on that date. The models are trying to identify which stocks are
likely to do best against their sector peers. Kumo predicts a set
of quantiles for this target, which I average into one score per stock.
I describe the predictors and target in more detail in
[*Combining Multiple Predictors: The Linear Case*]({% link _posts/2025-02-09-combining-predictors.md %}#what-i-ask-the-model-to-predict).

The main test uses an expanding walk-forward window. The history
starts in January 1995 and grows at each refit as more 20-day
outcomes become known. I use each fit to score the dates that follow.
I refresh Kumo’s context when I refit LightGBM. Rolling Small
uses the same walk-forward setup with a rolling context. The
test runs from 1999 through May 27, 2026, with 2022 onward
shown separately.

For **Ridge**, I use a penalty of $c=0.1$. Several predictors overlap,
such as momentum measured over nearby horizons, and the penalty
keeps the coefficients from growing too large as a result. I go
into the penalty choice in
[*Combining Multiple Predictors*]({% link _posts/2025-02-09-combining-predictors.md %}#choosing-the-penalty).

For **LightGBM**, I use 350 trees per fit, a maximum depth of five,
a learning rate of 0.05 and a feature fraction of 0.25. The shallow
trees can still pick up interactions.

## Subsampling the historical context

Kumo has to prepare and keep the historical examples in memory
to make a prediction. Each example is one stock on one date, so
adding a date can add hundreds of rows. Over a long backtest that
table gets too big for my Mac. I ran the backtests on the CPU and
kept fewer dates and fewer stocks on those dates.

Take the same stock on two consecutive trading days. Its two
targets use 20 days of forward returns and share 19 of those
days. Keeping both rows gives Kumo examples based on almost the
same returns. For expanding Small, I kept one date every 30
trading days, or roughly six weeks. For Medium and Large, I
kept one date every 40 trading days, or roughly eight weeks.
Medium and Large used the same historical rows, 80 predictors
and one estimator to score the same 1.39 million stock-dates.

Even after spacing out the dates, there are still hundreds of
stocks on each one. I sort them by their realized target, the
20-day Sharpe rank within each stock’s sector, and keep the lowest
and highest 30% across the date. That cuts about 40% of the rows.
I kept the extremes because the portfolio picks long and short
candidates from the ends of the predicted ranking. The stocks in
the middle may also carry useful information.

In [*Training Trees on Tails with Applications to Portfolio
Choice*](https://doi.org/10.1007/s10479-020-03539-2), Coqueret and
Guida (2020) tested this idea with boosted trees.
Keeping the lowest and highest 20% of their training outcomes cut
backtest time by roughly 60% and gave a similar return spread
between the highest- and lowest-ranked portfolios.

With the same stock filter, weekly sampling would have left
Kumo Small about 760,000 rows to prepare late in the 1999–2021
test. I estimated just that preparation would need about 35 GiB
of memory. Spacing the dates six weeks apart brought it down to
about 127,000 rows, which fit on my Mac.

Figure 3 uses two illustrative grids. Sampling every 20 trading days
keeps four dates, and sampling every 30 keeps three. The tails filter
keeps six of the ten stocks on each selected date, leaving 24 or 18
labeled rows.

<figure id="figure-3" class="research-figure responsive-figure">
  <div class="context-sampling" role="img" aria-label="Sampling every 20 trading days selects days 0, 20, 40 and 60. Sampling every 30 trading days selects days 0, 30 and 60. On each selected date, ten stocks are sorted by the realized prediction target. The lowest three and highest three are kept, and the middle four are skipped.">
    <div aria-hidden="true">
      <div class="context-sampling-heading">Historical dates</div>
      <div class="context-sampling-dates">
        <span>Day</span>
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
  <figcaption class="figure-caption"><span class="caption-number">Figure 3.</span> <span class="caption-title">Which historical rows enter Kumo’s context.</span> Filled marks show the dates and stocks selected in this example.</figcaption>
</figure>

When I put together a set of examples, I apply these cuts to the
history with known outcomes. The portfolios have three staggered
signal calendars, each with a rebalance roughly every three weeks.
Even with six weeks between historical examples, Kumo can score
every eligible stock on those signal dates using the latest context.

## Running Kumo on a Mac

I ran the full Kumo Large backtest on my 2023 MacBook Pro, which has
a 10-core M2 Pro CPU and 16 GB of unified memory. All 15 folds ran
on the CPU. The last fold used 110,167 historical rows and scored
84,243 stock-dates through May 2026. Medium took 17.5 minutes to
prepare the context and 11.5 minutes to score the new rows. Large
took 29.0 minutes and 17.9 minutes on the same inputs. Large’s peak
resident memory across the full test was 9.3 GiB.

## Ranking the whole cross-section

Once I have the forecasts, the first thing I check is how well
each model orders the stocks. For a signal date with known outcomes,
I rank the model scores and the realized outcomes for the same stocks,
then correlate the two ranks. That Spearman correlation is the
information coefficient, or $\mathrm{IC}_t$.
Figure 4 shows its mean, sample standard deviation and their ratio
across signal dates. The ratio is left unannualized.

$$
\mathrm{ICIR} = \frac{\operatorname{mean}_t(\mathrm{IC}_t)}
                      {\operatorname{sd}_t(\mathrm{IC}_t)}
$$

<figure id="figure-4" class="research-figure responsive-figure">
  {% include blog-chart.html chart="rank" source="/assets/equity-model-comparison/rank-metrics.json?v=6" base="/assets/equity-model-comparison/rank-metrics" mobile="/assets/equity-model-comparison/rank-metrics_mobile" version="7" label="Bar plots for rank IC, standard deviation of IC and ICIR by model through May 2026, with selectable periods." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 4.</span> <span class="caption-title">Rank metrics by period.</span> Each metric keeps the same scale across periods.</figcaption>
</figure>

From 2022 to May 2026, mean IC was 0.044
for Ridge, 0.046 for LightGBM and 0.040 for Medium. Medium’s IC
varied less from one date to the next than Ridge’s, so its ICIR was
higher, 0.38 versus 0.34. LightGBM led on both measures. Six-week
Small’s mean IC was 0.025, and Rolling Small’s was −0.010.

Large ranked stocks better than Medium in 1999–2021 and fell
behind in 2022–May 2026. The full-period increase in mean rank IC
was 0.0009, with a paired 95% interval of −0.0014 to +0.0032
using blocks of 21 trading days.
{: #does-the-larger-model-help}

## Return and risk by score decile

Rank IC looks across the whole ranking. For the portfolios, I care
especially about the stocks at either end. I sort each model’s
scores into deciles on the signal date and trade at the next close.
If a decile has $n$ stocks with a return that day, its daily
return is $\sum_i r_i / n$. I average these returns across
the three schedules on days when all three are available. The spread
is the top decile’s daily return minus the bottom decile’s. I compound
returns, annualize using 252 trading days and use zero cash return for Sharpe.
I use the same decile comparison for Ridge in
[*Combining Multiple Predictors*]({% link _posts/2025-02-09-combining-predictors.md %}#figure-3).

<figure id="figure-5" class="research-figure decile-profile-figure responsive-figure">
  {% include blog-chart.html chart="profiles" source="/assets/equity-model-comparison/deciles.json?v=5" base="/assets/equity-model-comparison/scheduled-decile-profile" mobile="/assets/equity-model-comparison/scheduled-decile-profile_mobile" version="10" label="Return, volatility and Sharpe by stock score decile from 1999 through May 2026, with selectable periods and models." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 5.</span> <span class="caption-title">Return, volatility and Sharpe by score decile.</span> Deciles are equal weighted and before costs. Decile 10 holds the highest scores.</figcaption>
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
liquidity, I cap trades at 10% of average daily dollar volume over
the previous 21 trading days. The
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
capital, and annualizes the average over trading days.

Table 1 shows all six runs at 75 candidates per side. For the
original five, I also tried 100 and 150 with the same forecasts,
sizing rules and fees.

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

In the 1999–2021 decile spread, six-week Small had a higher
Sharpe than Medium. Once I sized the portfolios
with 75 new candidates per side, Medium edged ahead before fees,
1.76 versus 1.68. Small also traded
more, at 42.3 times capital per year versus 31.8 for Medium.
After fees, Medium’s lead widened to 1.44 versus 1.24.

Medium also beat Ridge on net Sharpe over 1999–2021, 1.44 versus
1.21, with lower realized volatility. LightGBM led in the decile
spread and in the sized portfolios, reaching a net Sharpe of 2.12.
Resampling the same blocks of 21 trading days for Medium and
LightGBM gives a 95% interval of −0.99 to −0.40 for Medium’s net
Sharpe minus LightGBM’s.

From 2022 to May 2026, net Sharpe at 75 candidates per side was
0.79 for Ridge, 1.04 for LightGBM and 1.20 for Medium. The paired
95% interval for Medium’s Sharpe minus LightGBM’s ran from −0.38
to 0.71 using blocks of 21 trading days.

Medium’s higher average net P&L came from the long side.
I annualize the differences in average daily P&L so the long,
short and fee contributions add up. Compared with LightGBM,
Medium gained 5.5 percentage points on the long side, gave up
3.2 points on the short side and paid 0.6 points more in fees.

Large fell behind Medium in both equal-weight tails over that
later window. Its top decile earned less and its bottom decile
earned more. In the sized portfolios, Large gave up 4.58 percentage
points of annualized P&L on the long side and 1.17 on the short side,
and paid another 0.86 in fees. The paired 95% interval for the net
Sharpe gap was −1.44 to −0.15 with 42-session blocks.

At 100 candidates per side, Medium and LightGBM were closer, with
after-fee Sharpes of 1.18 and 1.14. At 150, LightGBM moved ahead,
at 1.24 versus 1.12 for Medium. Both models traded more
as I gave the optimizer more names. The paired intervals for
the later Sharpe gap include zero at all three widths. Over
the full history, LightGBM led these five runs on net Sharpe at every
width. Medium stayed ahead of Ridge at each width in both the full
history and the later window.

## How the P&L built up

Figure 6 shows when those gaps opened and how deep the drawdowns
were. The curves add up daily net P&L as a share of fixed capital.
Table 1 gives compounded returns. The chart opens with each path
rescaled to 7% annualized volatility in the selected window.
Clear the checkbox to see the original paths. Open **Explore** to
add Rolling Small.

<figure id="figure-6" class="research-figure portfolio-path-figure responsive-figure">
  {% include blog-chart.html chart="pnl" source="/assets/equity-model-comparison/net-pnl.json?v=8" base="/assets/equity-model-comparison/net-pnl" mobile="/assets/equity-model-comparison/net-pnl_mobile" version="7" label="Cumulative net P&L and drawdown through May 2026, rescaled to 7% annualized volatility by default." %}
  <figcaption class="figure-caption"><span class="caption-number">Figure 6.</span> <span class="caption-title">Cumulative P&amp;L and drawdown after fees.</span> These portfolios use 75 new candidates per side. I average daily P&amp;L across the three schedules and add it up. Both panels show percentages of fixed capital.</figcaption>
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

## A shorter context with Rolling Small

I tried sampling recent examples more frequently. Rolling Small
sampled weekly, starting with two years of history and growing to
three.
Over 1999–2021, it ranked stocks worse than expanding Small
and had a net Sharpe of 0.39 versus 1.24. The short book
accounted for most of the gap in average net P&L. From 2022 to
May 2026, Rolling Small lost money before fees at all three
candidate widths.

## References

- Coqueret, Guillaume, and Tony Guida (2020). [*Training Trees on Tails with Applications to Portfolio Choice*](https://doi.org/10.1007/s10479-020-03539-2). *Annals of Operations Research*, 288(1), 181–221.
- Grinsztajn, Léo, Edouard Oyallon, and Gaël Varoquaux (2022). [*Why Do Tree-Based Models Still Outperform Deep Learning on Typical Tabular Data?*](https://proceedings.neurips.cc/paper_files/paper/2022/hash/0378c7692da36807bdec87ab043cdadc-Abstract-Datasets_and_Benchmarks.html). *NeurIPS*, Datasets and Benchmarks Track.
- Grinsztajn, Léo, et al. (2025). [*TabPFN-2.5: Advancing the State of the Art in Tabular Foundation Models*](https://arxiv.org/abs/2511.08667). Technical report, arXiv:2511.08667.
- Molnar, Christoph. [*Tabular Foundation Models: A Short and Opinionated Guide*](https://tabularfoundationmodels.com/). Online book.
- NVIDIA. [*GPU Sizing Guide*](https://docs.nvidia.com/sdgm/structured-data-models/gpu-sizing). *NVIDIA Kumo Documentation*.
- Qu, Jingang, et al. (2026). [*NVIDIA Kumo Tabular: Pushing the Accuracy–Efficiency Frontier for Tabular Prediction*](https://arxiv.org/abs/2611.23001v1). arXiv:2611.23001, version 1.
- Qu, Jingang, David Holzmüller, Gaël Varoquaux, and Marine Le Morvan (2026). [*TabICLv2: A Better, Faster, Scalable, and Open Tabular Foundation Model*](https://proceedings.mlr.press/v306/qu26a.html). *ICML*, PMLR 306, 102477–102555.

[^tree-benchmark]: [LightGBM’s competition results](https://github.com/lightgbm-org/LightGBM/blob/main/examples/README.md) list winning solutions, and [Chen and Guestrin (2016)](https://arxiv.org/abs/1603.02754) document XGBoost’s early Kaggle results. [Ambrosm’s winning Kaggle write-up](https://www.kaggle.com/competitions/bench-tab-v2/writeups/ambrosm-1-solution) uses boosted trees and random forests.

[^new-benchmarks]: See the comparisons with tuned tree models in the [TabPFN-2.5 report](https://arxiv.org/abs/2511.08667) and the [TabICLv2 paper](https://proceedings.mlr.press/v306/qu26a.html).

[^larger-tables]: [TabPFN-2.5](https://arxiv.org/abs/2511.08667) extended the supported table size from 10,000 to 50,000 rows.
