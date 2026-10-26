---
layout: post
interactive_charts: true
title: "Removing Style Bets from a Ridge Forecast"
description: "Half of the Ridge forecast is style. Removing part of it before the portfolio is built raises the Sharpe ratio before 2019 and not since; adding short interest to the removal does best."
permalink: /quants/ridge-style-removal.html
toc: true
date: 2026-10-26
last_modified_at: 2026-10-26
categories: ["Portfolio construction"]
article_label: Portfolio construction · Style removal
---

The attribution articles split the Ridge portfolio's return by what it is paid
for, and style characteristics turned up on both sides of the ledger. They earn
return, and in
[Part 2]({% link _posts/2026-09-09-short-book-rebounds.md %}) the deepest
drawdowns came mostly from the low-risk package. That split is made after the
fact, on the book. Here I make it earlier, on the forecast the book is built
from, and ask whether part of the style content should come out before the
portfolio is formed.

Style characteristics explain half of the
[Ridge forecast's]({% link _posts/2025-02-09-combining-predictors.md %})
cross-sectional variance. Removing part of it lowers volatility at every
strength I tried. Whether it raises the Sharpe ratio depends on the period:
light-to-moderate removal does before 2019 and not since. Adding lagged short
interest to the removal does best of the variants I tried, and fades less.

Figure 1 shows where the removal sits. The forecast is split on each date into a
sector part, a style part and a stock-specific remainder, a share of the style
part is subtracted, and the adjusted scores go through selection and sizing as
before. The attribution articles read the same split in the other direction, on
the book's P&L.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/removal-diagram" mobile="/assets/ridge-style-removal/removal-diagram_mobile" alt="Flow from the Ridge forecast through a split into sector, style and stock-specific parts, subtraction of a share of the style part, selection of 75 long and 75 short names and sizing, ending in book weights, whose P&L splits into a style part and a stock-specific part." version="2" %}
</div>
<p class="figure-caption"><strong>Figure 1: Removal acts on the forecast, and attribution reads the result in the book.</strong> The dial λ is the share of the fitted style part subtracted from the forecast. The book's style exposure X′w is inherited from the forecast; the stock-specific part w′e is what remains.</p>

The idea is not new. Giuseppe Paleologo's *Advanced Portfolio Management*
regresses a fundamental investor's alphas on factor loadings and sizes from the
residual.[^book] Numerai subtracts a tunable proportion of the fitted feature
exposure from machine-learning predictions, and a forum study there finds bias
rising and variance falling as the proportion grows.[^numerai] MSCI neutralizes
published equity signals to eight style factors before evaluating them.[^msci]
Those settings treat full removal as the natural rule. A Ridge forecast learns
part of its style content from returns, so I treat the removed share as a dial
to measure.

The book is the joint-sizing optimizer with 75 long and 75 short names, a 7%
forecast volatility target and its position, sector and beta limits, with the
1.18 volatility multiplier of
[Reducing Rebalancing Luck]({% link _posts/2026-09-05-rebalancing-luck.md %}).
Results are means over its three rebalance schedules, after 5 bp per dollar
traded, from January 1999 to April 2026; intervals are paired 120-session
block-bootstrap 95% intervals against no removal. Costs are linear, with no borrow
or financing. I judge each variant by its net Sharpe ratio: a lower return is fine
if volatility falls by more.

## The style part comes from a weighted regression on each date

On each date I take the cross-section of Ridge forecasts, about 1,000 stocks, and
regress it on eleven sector indicators and six style exposures:

$$
y_i=\sum_{s}\gamma_s D_{is}+\sum_{k}\beta_k x_{ik}+e_i ,
$$

where $$D_{is}$$ is 1 when stock $$i$$ is in sector $$s$$ (the indicators also
carry the intercept) and $$x_{ik}$$ is its exposure to style $$k$$, defined in
Table 1. Every exposure uses prices up to that day's close. Each is standardized
across stocks the same way: winsorized at five median absolute deviations from
the median, centred so that its capitalization-weighted average is zero and
scaled to an equal-weighted standard deviation of one. A missing value of the
first five styles is set to the capitalization-weighted average.

<table class="research-table settings-table">
  <caption><strong>Table 1: The six styles, and short interest in one variant.</strong> Each is measured per stock on each date and then standardized across stocks.</caption>
  <thead><tr><th>Style</th><th>Measure</th><th>Window</th></tr></thead>
  <tbody>
    <tr><th scope="row">Beta</th><td>Slope of the stock's daily returns on the Russell 1000, shrunk toward 1 by its sampling variance (prior variance 0.25), clipped at ±4</td><td>252 sessions, at least 126</td></tr>
    <tr><th scope="row">Residual volatility</th><td>Log standard deviation of that regression's residuals, made orthogonal to beta and size</td><td>252 sessions</td></tr>
    <tr><th scope="row">Momentum</th><td>Sum of daily log returns, leaving out the latest 21 sessions</td><td>252 sessions</td></tr>
    <tr><th scope="row">Size</th><td>Log market capitalization</td><td>That day</td></tr>
    <tr><th scope="row">Liquidity</th><td>Log of the median daily dollar volume divided by market capitalization</td><td>63 sessions</td></tr>
    <tr><th scope="row">Short-term reversal</th><td>Minus the stock's return</td><td>21 sessions</td></tr>
    <tr><th scope="row">Short interest (variant only)</th><td>Log of short interest times price over market capitalization, the share of shares outstanding sold short; a plain z-score, with no short interest scored zero</td><td>Lagged 21 sessions</td></tr>
  </tbody>
</table>

The regression is weighted by the square root of market capitalization, as in the
attribution articles, so large stocks count more without a few of them dominating,
and it is solved jointly on each date. Each $$\hat\beta_k$$ is the forecast's
tilt toward style $$k$$ that day, holding sectors and the other styles fixed. The
style part is $$\sum_k\hat\beta_k x_{ik}$$; removal subtracts a share
$$\lambda$$ of it and keeps the sector part and the remainder:

$$
y'_i=y_i-\lambda\sum_{k}\hat\beta_k\,x_{ik}.
$$

The adjusted scores go through selection and the optimizer unchanged, in their
native units and without re-ranking. I run $$\lambda$$ = 25%, 50%, 75% and 100%.
At 25% the forecast's variance falls by about a fifth, $$\lambda(2-\lambda)$$
times the style share. Momentum is the style that matters most: leaving it out of
the removal at 50% costs 0.10 of Sharpe and adds 0.5 points of volatility.

## Half of the forecast is style

The same regression splits the forecast's cross-sectional variance into a sector
part, a style part and a stock-specific remainder. Style carries 50% on average and 58%
after 2019 (Figure 2). Part of that may be built in by the target: the model predicts
a forward 20-session Sharpe ratio, which favours low-volatility stocks.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/forecast-style-share" mobile="/assets/ridge-style-removal/forecast-style-share_mobile" alt="Stacked shares of the Ridge forecast's cross-sectional variance by year: style between 40% and 65%, stock-specific most of the rest." version="2" %}
</div>
<p class="figure-caption"><strong>Figure 2: Style is half of the Ridge forecast.</strong> Share of each year's cross-sectional forecast variance explained by the six styles (blue), left to the stock-specific remainder (grey), or assigned to sectors and cross terms (light grey), fitted with square-root-of-market-cap weights.</p>

## Style gets through the optimizer at a discount

The optimizer prices risk with $$\Sigma=DCD$$: 21-session volatilities times the
multiplier in $$D$$, and correlations of volatility-standardized returns over 756
sessions shrunk halfway to the identity in $$C$$. Halving every correlation halves
their average, so the model understates common risk. With a multiplier below its
calibrated 1.55, that is why the book realizes 8.9% volatility against its 7% target. A constant multiplier rescales every book
alike and leaves Sharpe ratios unchanged, so the level is not the point. The mix
is: style bets carry exactly the common risk that shrinkage discounts, so they get
through the optimizer more cheaply than stock-specific bets.

Removal does not help by cutting a weak component. In the unadjusted book the style
P&L has a Sharpe ratio of 0.93 and the stock-specific P&L 0.49. It helps by
changing the stocks. The unadjusted book's names carrying the 50%-removal book's
style exposures earn a Sharpe ratio of 1.19, no better than the unadjusted 1.20,
while the 50% book earns 1.38; about a third of its weight sits in different
names. So removal pays only while the names it adds earn stock-specific return.
Before 2019 the unadjusted book's stock-specific P&L had a Sharpe ratio of 0.63;
since then it is 0.10. That is the shape of everything that follows.

## Moderate removal raises the Sharpe ratio, almost all of it before 2019

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 2: Removal lowers volatility at every strength and raises the Sharpe ratio up to 75%.</strong> January 1999–April 2026, mean of three schedules, net of 5 bp per dollar traded. Δ is the Sharpe difference against no removal, with a 95% interval for the full period. Turnover is two-way, as a multiple of capital a year.</caption>
  <thead>
    <tr><th>Removal</th><th>Net Sharpe</th><th>Δ full [95%]</th><th>Δ 1999–2018</th><th>Δ 2019–2026</th><th>Vol.</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">None</th><td>1.20</td><td>—</td><td>—</td><td>—</td><td>8.89%</td><td>24.7x</td></tr>
    <tr><th scope="row">Style 25%</th><td>1.27</td><td>+0.07 [−0.01, +0.16]</td><td>+0.12</td><td>−0.02</td><td>8.70%</td><td>25.7x</td></tr>
    <tr><th scope="row">Style 50%</th><td>1.38</td><td>+0.19 [+0.02, +0.36]</td><td>+0.32</td><td>−0.11</td><td>8.36%</td><td>27.2x</td></tr>
    <tr><th scope="row">Style 75%</th><td>1.41</td><td>+0.22 [−0.06, +0.47]</td><td>+0.39</td><td>−0.18</td><td>7.76%</td><td>28.9x</td></tr>
    <tr><th scope="row">Style 100%</th><td>1.20</td><td>0.00 [−0.39, +0.40]</td><td>+0.21</td><td>−0.54</td><td>7.29%</td><td>30.2x</td></tr>
    <tr><th scope="row">25% + short interest</th><td>1.34</td><td>+0.15 [+0.06, +0.24]</td><td>+0.21</td><td>+0.02</td><td>8.71%</td><td>26.0x</td></tr>
    <tr><th scope="row">PCA 25%</th><td>1.19</td><td>−0.01 [−0.08, +0.07]</td><td>−0.01</td><td>−0.01</td><td>8.67%</td><td>25.6x</td></tr>
    <tr><th scope="row">PCA 50%</th><td>1.23</td><td>+0.04 [−0.12, +0.19]</td><td>0.00</td><td>+0.09</td><td>8.38%</td><td>26.4x</td></tr>
  </tbody>
</table>

The Sharpe ratio rises from 1.20 to 1.38 at 50% and 1.41 at 75%, and falls back to
1.20 at full removal. Volatility falls at every step, from 8.9% to 7.3%, and up to
75% the return does not fall with it, so the risk reduction is where most of the
gain comes from. Among the strengths only the 50% gain has an interval clear of
zero; it is the best of the variants in Table 2, and adjusting for all of them
with a max-t bootstrap gives a p-value of about 0.09. The gain is uneven across
schedules (+0.13, +0.11 and +0.32 at 50%), and turnover rises by up to six turns,
which the net Sharpe already pays for.

Figure 3 splits the result at 2019, a date I chose after seeing the weak recent
years. Before it, 25% to 75% all have intervals clear of zero (+0.12, +0.32 and
+0.39). From 2019 every style strength has a negative point estimate and none is
distinguishable from zero; the change from the early period is clear at 50%
(−0.43 [−0.78, −0.15]) and 75% (−0.57 [−1.18, −0.06]) and not at 25%. Most of the
shortfall comes from 2021 and 2024–2025: 2019–2023 alone is about flat, and with a
split at 2016 the later period is slightly positive.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/delta-sharpe" mobile="/assets/ridge-style-removal/delta-sharpe_mobile" alt="Net Sharpe difference against no removal by strength with 95% intervals: clearly positive for 25 to 75 percent before 2019, and intervals spanning zero from 2019; the short-interest variant is positive before 2019 and near zero after." version="2" %}
</div>
<p class="figure-caption"><strong>Figure 3: Before 2019 the gain is clear for 25–75%; from 2019 no difference is.</strong> Net Sharpe difference against no removal, mean of three schedules, with paired block-bootstrap 95% intervals. Circles are style removal, the square adds short interest (SI) and diamonds are PCA.</p>

Figure 4 shows when the gain accrued, with every variant scaled to the volatility
of no removal so that the gap measures the Sharpe difference and not risk taken.
The 50% removal was 54 points ahead at the end of 2018, peaked at 57 in 2021 and
ends at 45. Plain 25% gained less and gave back less, ending at 18.

<div class="research-figure responsive-figure">
  {% include blog-chart.html chart="gap" source="/assets/ridge-style-removal/equal-vol-gap.json?v=2" base="/assets/ridge-style-removal/equal-vol-gap" mobile="/assets/ridge-style-removal/equal-vol-gap_mobile" version="1" label="Cumulative net return against no removal at equal volatility for style 25%, style 50%, 25% plus short interest and PCA 50%, 1999 to April 2026, with 2019 onward shaded." %}
</div>
<p class="figure-caption"><strong>Figure 4: The style gains were made before 2019; short interest kept most of its gain.</strong> Cumulative daily net return difference against no removal, in points of capital, with each variant scaled to the full-period volatility of no removal; mean of three schedules. Shaded: 2019 onward.</p>

The fade has the same cause as the gain. Removal moves risk from style bets to
stock-specific ones, and since 2019 the book's stock-specific P&L has stopped
paying while its style P&L has not. Style 50% earns about 1.9 points a year more
than no removal before 2019 and 1.7 less afterwards, almost all of it in
stock-specific return. One result does not fit neatly: a plain score-weighted
portfolio of the forecast, with no optimizer, improves at every strength in both
periods. The fade appears only after selection and sizing, and I have not
separated which of the two produces it.

## Adding short interest to the removal does best and fades less

One variant adds a seventh column to the removal regression: the share of shares
outstanding sold short (Table 1). Short interest is reported twice a month and
published about eight business days after its settlement date, so I lag it 21
sessions. Everything else is as in plain 25% removal.

It is the strongest result in the study: a Sharpe ratio of 1.34, +0.15
[+0.06, +0.24] against no removal and +0.07 [+0.04, +0.11] against plain 25%,
positive on all three schedules, at the same volatility as plain 25%. It is the
only variant whose gain survives adjustment for the others in Table 2 (max-t
p ≈ 0.002). Before 2019 it adds +0.21 [+0.11, +0.32], and it beats plain 25% in
every five-year block. From 2019 it is +0.02 [−0.16, +0.15], so it fades too
(−0.18 [−0.39, −0.03] against the early period), but at equal volatility it keeps
most of its accumulated gain (Figure 4).

What I know about why is limited to four facts. The book is a bet against heavily
shorted stocks: its short leg sits at the 66th percentile of short interest as a
share of shares outstanding and its long leg at the 33rd. The change is small: 93% of the weight is
shared with plain 25%. The gain is stock-specific, with the factor share of book
variance unchanged. And since 2019 it comes entirely from the short leg, where
plain removal loses most, recovering about half of that loss. Two readings fit:
trimming the part of the forecast aligned with short interest reduces squeeze and
borrow risk the forecast does not price, or it removes a noisy loading the Ridge
fit learned. The evidence does not separate them.

It would not help where the short-interest lean pays, which the attribution
articles show it has done more since 2022, where short-interest data are stale or
mis-dated, or in a forecast without that lean. Tail days and about ten names carry
much of its edge over plain 25%. And it is one of about 28 removal variants tried
on this history, so it is a lead to confirm on data it has not seen.

## PCA and portfolio-level limits are weaker substitutes

Replacing the styles with the first 10 principal components of trailing returns
lowers volatility by as much but adds almost no Sharpe (+0.04 [−0.12, +0.19] at
50%). All of its shortfall against style removal is before 2019, and since 2019 it
is ahead (+0.09 against −0.11 for style 50%). The components start only in 2002,
and equal $$\lambda$$ removes different amounts of variance, so it is a partial
cross-check rather than a replacement.

Limits on the finished portfolio did worse. A cost-free 75% style-beta limit on the
book was 0.13 [0.04, 0.24] of Sharpe behind 25% forecast removal, and hard style
caps inside the optimizer had no feasible solution on 24 April 2009 other than
the empty book. The 150 names are chosen from the forecast before the optimizer
weights them, so a limit on weights cannot undo a selection that leans one way;
removal changes the selection.

## Related work acts on style in the optimizer and the finished book

Clarke, de Silva and Thorley show how constraints limit the transfer of a signal
into portfolio weights, which the infeasible caps here illustrate.[^clarke]
Daniel, Mota, Rottke and Santos hedge the unpriced risk of characteristic
portfolios with covariance estimated from past returns and nearly double the
squared Sharpe ratio of their combination, a stronger version of the overlay
tested here.[^daniel] Neither was tested on this book.

## Light removal is the least regret, and short interest the lead

On Sharpe, the evidence supports moderate removal before 2019 and nothing since. A
quarter of the style part is the least regret: it earns about a third of the 50%
gain before 2019 and takes about a sixth of its loss since, at a cost of one turn
of turnover. Stronger removal buys more Sharpe on the early history and reverses
after it, and full removal, the natural rule in the literature, adds nothing here.

Adding lagged short interest is the best variant: higher Sharpe at the same
volatility, a gain that survives adjustment for the variants compared, and a
smaller fade. It was found on this history, so I hold it as the lead and not as a
conclusion. All of this describes a risk model that shrinks correlations; one that
priced style risk directly could take over part of what removal does here.

## References

Giuseppe A. Paleologo, *Advanced Portfolio Management: A Quant's Guide for
Fundamental Investors*, Wiley, 2021, Chapters 6 and 8.

by256,
[*Feature Neutralization Increases Bias and Reduces Variance*](https://forum.numer.ai/t/feature-neutralization-increases-bias-and-reduces-variance/7486),
Numerai Forum, 4 June 2024.

Mark Horvath, Dominik Zvara and Mihaly Berndt,
[*Constructing Portfolios from Published Equity Research*](https://www.msci.com/research-and-insights/blog-post/constructing-portfolios-from-published-equity-research),
MSCI Research, 7 October 2026.

Roger Clarke, Harindra de Silva and Steven Thorley,
*Portfolio Constraints and the Fundamental Law of Active Management*, Financial
Analysts Journal 58(5), 2002, 48–66.

Kent Daniel, Lira Mota, Simon Rottke and Tano Santos,
[*The Cross-Section of Risk and Returns*](https://doi.org/10.1093/rfs/hhaa021),
Review of Financial Studies 33(5), 2020, 1927–1979.

[^book]: Paleologo (2021), Chapter 6, Procedure 6.3; Chapter 8 uses the same factor decomposition to separate style from idiosyncratic P&L.
[^numerai]: See also Numerai's [feature-neutral correlation](https://docs.numer.ai/numerai-tournament/scoring/feature-neutral-correlation), which uses full removal.
[^msci]: The average post-publication information ratio of a signal rises from 0.17 raw to 0.28 style-neutral; these are signals, not a model's forecast.
[^clarke]: The transfer coefficient is 1 when the signal reaches the weights unconstrained; constrained managers typically sit between 0.3 and 0.8.
[^daniel]: The squared Sharpe ratio of five characteristic portfolios rises from 1.16 to 2.16, per the authors' abstract.
