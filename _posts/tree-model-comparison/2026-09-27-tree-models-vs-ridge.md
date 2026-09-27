---
published: false
layout: post
title: "Do Tree Models Beat Ridge on the Same Predictors?"
description: "LightGBM against Ridge on the same 80 predictors, target and portfolio rule: a clear lead through 2021, built before 2017, and no measurable difference since."
permalink: /quants/tree-models-vs-ridge.html
toc: false
date: 2026-09-27
categories: ["Machine learning"]
---

In the [multiple-predictors article](/quants/2025/02/09/multiple-linear-regression.html)
Ridge combined 80 predictors into one ranking, and learning the weights beat
equal weights by about 0.2 of Sharpe. Ridge is linear and additive, though. A
tree model can let one predictor's effect depend on another, such as momentum
that matters more among calm stocks, and can bend where a linear weight can't.
Does that flexibility buy anything on the same data?

## The comparison

I change only the estimator. Everything else is the Ridge article's setup: the
same 80 predictors and 20-session sector-relative Sharpe target, the same
expanding walk-forward from 1995 with three interleaved fits, and the same plain
portfolio rule, trading costs and three rebalance schedules. Development runs
from September 1998 to December 2021 and the later period from January 2022 to
May 2026.

The tree model is LightGBM with 350 shallow trees (depth 5, 32 leaves), a
learning rate of 0.05 and a quarter of the predictors sampled for each tree.
These are the reference settings from an earlier tree study, not tuned here:
shallow enough that each tree captures a few interactions, with column sampling
so that no small group of predictors dominates.[^settings]

## Results

<div markdown="1">
<p class="table-caption"><strong>Table 1: LightGBM ranks more steadily and earns more per unit of risk, until 2021.</strong> Mean daily rank IC with the 20-session target and its information ratio; portfolio statistics are means over the three rebalance schedules, after 5 bp costs: annualized volatility and maximum drawdown, in percent.</p>

| Model | IC | IC IR | Vol. | Sharpe | Drawdown |
| :--- | ---: | ---: | ---: | ---: | ---: |
| **Development · 1998–2021** | | | | | |
| Ridge | 0.048 | 0.53 | 8.1 | 0.98 | −19.8 |
| LightGBM | 0.055 | 0.72 | 6.8 | 1.48 | −16.4 |
| **Later · 2022–May 2026** | | | | | |
| Ridge | 0.042 | 0.35 | 10.2 | 0.73 | −9.4 |
| LightGBM | 0.044 | 0.42 | 8.1 | 0.81 | −7.7 |
{: .research-table .comparison-table .attribution-table }
</div>

Through 2021 the gap is large and not luck: LightGBM's Sharpe is about 0.5
higher, with a block-bootstrap interval of 0.24 to 0.85 on the combined
book.[^bootstrap] It ranks stocks a little better on average and much more
consistently from day to day, and it does so at lower risk and similar
turnover (about 28 times capital a year for both): it earns 10.1% a year
against 7.9% while running about 1.2 points less volatility and a smaller net
long position, 26% of capital against 36%. After 2021 LightGBM returns less,
6.6% against 7.4%, at lower volatility; the Sharpe difference is 0.10, with an
interval of −0.27 to +0.46.

Figure 1 shows when the lead was earned.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/tree-model-comparison/relative-growth" mobile="/assets/tree-model-comparison/relative-growth_mobile" version="1" alt="LightGBM's growth divided by Ridge's since September 1998: it rises in 1999–2000 and 2009–10, drifts up to about 1.75 by 2017 and moves sideways to about 1.64 by May 2026." %}
</div>
<p class="figure-caption"><strong>Figure 1: The lead was built before 2017.</strong> Mean-schedule growth of LightGBM divided by Ridge's, net of costs; each keeps its own risk level. The shaded area is the later period.</p>

Most of it came in two bursts, around the dot-com peak and in the 2009–10
rebound, then accumulated slowly until about 2016. The ratio peaked in
November 2017 and has drifted slightly down since. So the later period isn't a
break: on this evidence the trees stopped adding anything over Ridge several
years before it began.

## What I take from this

On the same predictors and the same portfolio rule, LightGBM was the better
ranking over the full history: steadier, less risky and about half a point of
Sharpe ahead through 2021. But all of that edge was earned before 2017, and
nothing since distinguishes the two. I'd hold the conclusion loosely in both
directions: the trees clearly found something Ridge missed, and whatever it was
has not shown up for the best part of a decade.

Two questions follow. What did the trees capture in 1999–2000 and 2009–10?
The second is the rebound that hurt the Ridge book in the
[attribution series](/quants/short-book-rebounds.html), so the obvious
suspect is that the trees held fewer high-beta shorts into strong rallies. And
why did the lead stop: did the relationships the trees exploited fade, or did
the two models converge on the same low-volatility bet?

[^settings]: Minimum 20 rows per leaf, 255 histogram bins and deterministic training, with the same three interleaved fits per refit as Ridge. The settings come from the earlier tree study in this project; they were chosen on development data only.

[^bootstrap]: Paired block bootstrap of the combined three-schedule daily returns. The combined book's Sharpe ratios (1.58 and 1.04 through 2021) are higher than the schedule means in Table 1 because combining schedules diversifies.
