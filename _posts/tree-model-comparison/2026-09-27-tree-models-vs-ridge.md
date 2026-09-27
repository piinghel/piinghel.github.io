---
published: false
layout: post
title: "Do Tree Models Beat Ridge on the Same Predictors?"
description: "LightGBM against Ridge on the same 80 predictors and target, on a plain rule and the optimizer: a clear lead through 2021, built before 2017, and no measurable difference since."
permalink: /quants/tree-models-vs-ridge.html
toc: true
date: 2026-09-27
categories: ["Machine learning"]
---

In the [multiple-predictors article](/quants/2025/02/09/multiple-linear-regression.html)
Ridge combined 80 predictors into one ranking, and learning the weights beat
equal weights by about 0.2 of Sharpe. Ridge is linear and additive, though. A
tree model can let one predictor's effect depend on another, such as momentum
that matters more among calm stocks, and can bend where a linear weight can't.
Here I test whether that flexibility buys anything on the same data.

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
{: .research-table .comparison-table .compact-table }
</div>

Through 2021 the gap is large and clearly outside noise: LightGBM's Sharpe is about 0.5
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
break: the trees stopped adding anything over Ridge several years before it
began.

Both bursts came while LightGBM made a much smaller low-volatility bet than
Ridge. Early on its scores were almost unrelated to volatility: their rank
correlation with 63-session volatility averaged −0.06 in 1998–2003, against
−0.37 for Ridge. In the dot-com rally, when calm stocks lagged badly (the
[low-volatility portfolio](/quant/2024/12/15/low-volatility-factor.html) lost
38%), LightGBM's book gained 36% and Ridge's about nothing, and in the momentum
crash of March to June 2009 LightGBM gained 5.6% while Ridge lost 1.6%.[^tilt]
The trees then converged on the same bet: by 2019–21 the correlation was −0.52
for LightGBM and −0.66 for Ridge, and the lead stopped growing.

## On the optimizer

The plain rule sizes each stock by its own volatility. The
[optimization article](/quants/2026/08/29/portfolio-optimization.html) sizes
the selected stocks jointly, under risk, beta and sector limits with a penalty
on trading, and that is the allocation the later articles build on. I replay
both models' saved scores through it, each with its best volatility window:
21 sessions for Ridge, as in that article, and 63 for LightGBM.[^optimizer]

<div markdown="1">
<p class="table-caption"><strong>Table 2: The optimizer lifts both models and widens LightGBM's lead before 2022.</strong> Sharpe ratio of the combined three-schedule book after costs, and LightGBM's lead over Ridge with its 95% paired block-bootstrap interval below. 2022–26 runs to May 2026.</p>

| Rule | Period | Ridge | LightGBM | Lead |
| :--- | :--- | ---: | ---: | ---: |
| Plain | 1998–2021 | 1.04 | 1.58 | +0.54<br><small>[+0.24, +0.85]</small> |
| Plain | 2022–26 | 0.75 | 0.85 | +0.10<br><small>[−0.27, +0.46]</small> |
| Optimizer | 1998–2021 | 1.41 | 2.21 | +0.80<br><small>[+0.45, +1.14]</small> |
| Optimizer | 2022–26 | 0.90 | 1.26 | +0.36<br><small>[−0.27, +1.00]</small> |
{: .research-table .comparison-table .compact-table }
</div>

Joint sizing helps both rankings, and LightGBM more: through 2021 its lead
grows to 0.8 of Sharpe, with an interval well clear of zero. After 2021 the
lead is larger than on the plain rule, 0.36, but the interval still runs from
−0.27 to +1.00. The volatility multiplier was calibrated on Ridge's book with the 21-session
window, and LightGBM's book lands below the 7% target, at about 6% per schedule
against Ridge's 7% through 2021. A different multiplier would also change the
weights, so this is a comparison at these settings.

## What I take from this

On the same predictors, LightGBM was the better ranking under both portfolio
rules: steadier and 0.5 to 0.8 of Sharpe ahead through 2021. But
the edge was earned before 2017, mostly in periods when it bet less on low
volatility than Ridge did, and it faded as the trees converged on the same
low-volatility bet. Since 2022 it is still ahead on both rules, by 0.10 and
0.36, and neither difference is distinguishable from noise.

## References

- Ke, Meng, Finley, Wang, Chen, Ma, Ye and Liu (2017), *LightGBM: A Highly Efficient Gradient Boosting Decision Tree*, NeurIPS.
- Daniel and Moskowitz (2016), *Momentum Crashes*, Journal of Financial Economics.

[^settings]: Minimum 20 rows per leaf, 255 histogram bins and deterministic training, with the same three interleaved fits per refit as Ridge. The settings come from the earlier tree study in this project; they were chosen on development data only.

[^bootstrap]: Paired block bootstrap of the combined three-schedule daily returns. The combined book's Sharpe ratios (1.58 and 1.04 through 2021) are higher than the schedule means in Table 1 because combining schedules diversifies.

[^tilt]: Mean daily Spearman correlation between each score and the stock's 63-session volatility rank among tradable stocks. Episode returns compound the mean-schedule long–short net return from 8 October 1998 to 9 March 2000 and from 9 March to 30 June 2009.

[^optimizer]: Saved scores replayed through the optimization article's rule with trading controls and a 7% forecast volatility target, with the volatility multiplier recalibrated to 1.55 on development data for Ridge's scores and the 21-session window. The bootstrap is the one described above, on the combined books.
