---
layout: post
interactive_charts: true
title: "Removing Style Bets from a Ridge Forecast"
description: "Half of the Ridge forecast is style. Taking part of it out before the portfolio is built lowers volatility at every strength and raised the Sharpe ratio before 2019."
permalink: /quants/ridge-style-removal.html
toc: true
date: 2026-10-26
last_modified_at: 2026-10-26
categories: ["Portfolio construction"]
article_label: Portfolio construction · Style removal
---

In the attribution articles I split the Ridge portfolio's return by what it is
paid for, and style characteristics kept showing up on both sides of the
ledger. They earn a good part of the return, and in
[Part 2]({% link _posts/2026-09-09-short-book-rebounds.md %}) they were also
behind the deepest drawdowns. That split happens after the fact, on the book.
Here I wanted to go one step earlier, to the forecast the book is built from,
and see what happens if part of its style content comes out before the
portfolio is formed.

The short version: half of the
[Ridge forecast]({% link _posts/2025-02-09-combining-predictors.md %}) is style.
Taking some of it out lowers the book's volatility at every strength I tried,
and up to a removal of about three quarters it raises the Sharpe ratio. That gain
was earned before 2019; since then it has mostly disappeared.

## Why take style out of a forecast at all

A stock-ranking forecast mixes two kinds of bets. Some are on characteristics
that many stocks share: low volatility, momentum, size. Others are on what is
specific to a company. Both can pay, but they behave very differently in a
portfolio. Style bets are common risk. When momentum turns, every past winner
in the book turns together, and holding more names doesn't help. Stock-specific
bets mostly cancel out across 150 positions.

That is why people clean forecasts before using them. Giuseppe Paleologo's
*Advanced Portfolio Management* regresses a fundamental investor's alphas on
factor loadings and sizes positions from the residual.[^book] Numerai subtracts
part of the fitted feature exposure from machine-learning predictions; a forum
study there finds that it adds bias and takes away variance.[^numerai]
MSCI evaluates published equity signals after neutralizing them to eight style
factors, and the average signal's information ratio rises from 0.17 to 0.28.[^msci]

The benefits are easy to state. A forecast with less style in it gives a book
with less common risk, so at the same risk budget more of the risk goes into
stock-specific bets. The signal also becomes steadier from day to day. The cost
is that you give up style premia that do pay, and you trade a bit more. Most of
these sources remove the style part completely. A Ridge forecast learns part of
its style content from returns, so I treat the share removed as a dial,
$$\lambda$$, and measure what each setting does.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/removal-diagram" mobile="/assets/ridge-style-removal/removal-diagram_mobile" alt="Flow from the Ridge forecast through a regression on sectors and styles, subtraction of a share of the style part and the portfolio optimizer to the book, whose P&L splits into a style part and a stock-specific part." version="3" %}
</div>
<p class="figure-caption"><strong>Figure 1: The removal sits between the forecast and the optimizer.</strong> A share λ of the fitted style part is subtracted from the forecast; the optimizer then selects and sizes the book exactly as before. The attribution articles read the same split in the other direction, on the book's P&L.</p>

The book is the joint-sizing optimizer: 75 long and 75 short names, a 7%
forecast volatility target, and its position, sector and beta limits, with the
1.18 volatility multiplier of
[Reducing Rebalancing Luck]({% link _posts/2026-09-05-rebalancing-luck.md %}).
All results are means over its three rebalance schedules, after 5 bp per dollar
traded, from January 1999 to April 2026. Intervals are paired 120-session
block-bootstrap 95% intervals against no removal. I judge each variant on its
net Sharpe ratio: a lower return is fine if volatility falls by more.

## The style part comes from a regression on each date

On each date I take the Ridge forecasts for about 1,000 stocks and regress them
on eleven sector indicators and six style exposures:

$$
y_i=\sum_{s}\gamma_s D_{is}+\sum_{k}\beta_k x_{ik}+e_i .
$$

$$D_{is}$$ is 1 when stock $$i$$ is in sector $$s$$, and the sector indicators
also carry the intercept. $$x_{ik}$$ is the stock's exposure to style $$k$$
(Table 1). Each exposure uses prices up to that day's close and is standardized
across stocks the same way: winsorized at five median absolute deviations,
centred so that the capitalization-weighted average is zero, and scaled to an
equal-weighted standard deviation of one. If one of the first five styles is
missing, the stock gets the capitalization-weighted average.

<table class="research-table settings-table">
  <caption><strong>Table 1: The six styles.</strong> Each is measured per stock on each date and then standardized across stocks.</caption>
  <thead><tr><th>Style</th><th>Measure</th><th>Window</th></tr></thead>
  <tbody>
    <tr><th scope="row">Beta</th><td>Slope of the stock's daily returns on the Russell 1000, shrunk toward 1 by its sampling variance (prior variance 0.25), clipped at ±4</td><td>252 sessions, at least 126</td></tr>
    <tr><th scope="row">Residual volatility</th><td>Log standard deviation of that regression's residuals, made orthogonal to beta and size</td><td>252 sessions</td></tr>
    <tr><th scope="row">Momentum</th><td>Sum of daily log returns, leaving out the latest 21 sessions</td><td>252 sessions</td></tr>
    <tr><th scope="row">Size</th><td>Log market capitalization</td><td>That day</td></tr>
    <tr><th scope="row">Liquidity</th><td>Log of the median daily dollar volume divided by market capitalization</td><td>63 sessions</td></tr>
    <tr><th scope="row">Short-term reversal</th><td>Minus the stock's return</td><td>21 sessions</td></tr>
  </tbody>
</table>

The regression is weighted by the square root of market capitalization, as in the
attribution articles, so large stocks count more without a few of them taking
over. Each $$\hat\beta_k$$ is how much the forecast leans toward style $$k$$ that
day, holding sectors and the other styles fixed. Removal subtracts a share of
that lean and leaves the sector part and the rest of the forecast alone:

$$
y'_i=y_i-\lambda\sum_{k}\hat\beta_k\,x_{ik}.
$$

The adjusted forecasts go into the optimizer as they are, without re-ranking. I
tried $$\lambda$$ = 25%, 50%, 75% and 100%. At 25%, the forecast's variance falls
by about a fifth. Momentum turns out to be the style that matters most: leaving it
out of the removal at 50% costs 0.10 of Sharpe and adds half a point of volatility.

## Half of the Ridge forecast is style

The same regression splits the forecast's cross-sectional variance into three
parts. Style carries 50% of it on average and 58% since 2019 (Figure 2). Part of
that comes from the target: the model predicts a forward 20-session Sharpe ratio,
which naturally favours low-volatility stocks.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/forecast-style-share" mobile="/assets/ridge-style-removal/forecast-style-share_mobile" alt="Stacked shares of the Ridge forecast's cross-sectional variance by year, adding to 100%: style between 40% and 65%, stock-specific most of the rest, and a thin band for sectors and overlap." version="3" %}
</div>
<p class="figure-caption"><strong>Figure 2: Style is about half of the Ridge forecast.</strong> Share of each year's cross-sectional forecast variance. The three parts add to 100%: style, the stock-specific remainder, and a thin band for sectors plus the overlap between the sector and style parts, which are fitted together and are not perfectly independent.</p>

## The optimizer's risk model discounts style risk

The optimizer sees risk through $$\Sigma=DCD$$: each stock's 21-session
volatility times the multiplier in $$D$$, and correlations over 756 sessions
shrunk halfway to zero in $$C$$. Shrinking correlations makes the optimizer more
robust, but it also understates common risk, because halving every correlation
halves their average. With the 1.18 multiplier, that is why this book realizes
8.9% volatility against its 7% target. The level itself doesn't matter for
Sharpe. What matters is the mix: style bets carry exactly the common risk that
shrinkage discounts, so they get through the optimizer a little too cheaply.

This also says how removal should help. It isn't that style is a poor bet; in the
unadjusted book the style P&L has a Sharpe ratio of 0.93, against 0.49 for the
stock-specific P&L. Removal changes which stocks are held. The unadjusted book's
names carrying the 50%-removal book's style exposures would have earned a Sharpe
ratio of 1.19, the same as doing nothing, while the actual 50% book earned 1.38;
about a third of its weight sits in different names. So removal works when the
stocks it brings in earn stock-specific return.

## Removal lowers volatility at every strength and raises the Sharpe ratio up to 75%

Figure 3 shows the two numbers that matter side by side. Volatility falls at
every step, from 8.9% with no removal to 7.3% with full removal. Up to 75% the
return doesn't fall with it, so the Sharpe ratio rises, from 1.20 to 1.38 at 50%
and 1.41 at 75%. At full removal the return gives way and the Sharpe ratio is back
at 1.20.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/risk-return" mobile="/assets/ridge-style-removal/risk-return_mobile" alt="Volatility and net Sharpe ratio for each variant: volatility falls with every step of style removal, and the Sharpe ratio rises to 1.38 at 50% and 1.41 at 75% before falling back to 1.20 at full removal." version="2" %}
</div>
<p class="figure-caption"><strong>Figure 3: Less style means less volatility, and up to 75% a higher Sharpe ratio.</strong> Realized volatility and net Sharpe ratio, January 1999–April 2026, mean of three rebalance schedules. The dotted line is no removal.</p>

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 2: The Sharpe gain is concentrated before 2019.</strong> Net Sharpe ratio and its difference against no removal, with a 95% interval for the full period, January 1999–April 2026.</caption>
  <thead>
    <tr><th>Removal</th><th>Net Sharpe</th><th>Δ full [95%]</th><th>Δ 1999–2018</th><th>Δ 2019–2026</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">None</th><td>1.20</td><td>—</td><td>—</td><td>—</td></tr>
    <tr><th scope="row">Style 25%</th><td>1.27</td><td>+0.07 [−0.01, +0.16]</td><td>+0.12</td><td>−0.02</td></tr>
    <tr><th scope="row">Style 50%</th><td>1.38</td><td>+0.19 [+0.02, +0.36]</td><td>+0.32</td><td>−0.11</td></tr>
    <tr><th scope="row">Style 75%</th><td>1.41</td><td>+0.22 [−0.06, +0.47]</td><td>+0.39</td><td>−0.18</td></tr>
    <tr><th scope="row">Style 100%</th><td>1.20</td><td>0.00 [−0.39, +0.40]</td><td>+0.21</td><td>−0.54</td></tr>
    <tr><th scope="row">PCA 25%</th><td>1.19</td><td>−0.01 [−0.08, +0.07]</td><td>−0.01</td><td>−0.01</td></tr>
    <tr><th scope="row">PCA 50%</th><td>1.23</td><td>+0.04 [−0.12, +0.19]</td><td>0.00</td><td>+0.09</td></tr>
  </tbody>
</table>

The 50% gain has an interval clear of zero; adjusted for all the variants in the
table it has a p-value of about 0.07. Turnover rises with removal, from 24.7 to
27.2 times capital a year at 50%, and the net Sharpe ratio already pays for it.

## The Sharpe gain was earned before 2019

Before 2019, every strength from 25% to 75% beat no removal with room to spare
(Figure 4). Since 2019 the style estimates are negative and close to zero, and the
change between the two periods is clear at 50% and 75%. The weak stretch is mostly
2021 and 2024–2025; 2019–2023 on its own is about flat. I picked 2019 as the
split after looking at the data, and with a split at 2016 the later period is
slightly positive, so the boundary is soft.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/delta-sharpe" mobile="/assets/ridge-style-removal/delta-sharpe_mobile" alt="Net Sharpe difference against no removal by strength with 95% intervals: clearly positive for 25 to 75 percent before 2019, and intervals spanning zero from 2019." version="3" %}
</div>
<p class="figure-caption"><strong>Figure 4: Before 2019 the gain is clear for 25–75%; since then it is about zero.</strong> Net Sharpe difference against no removal, mean of three schedules, with paired block-bootstrap 95% intervals. Circles are style removal and diamonds are PCA.</p>

Figure 5 shows when the gain built up. Every variant is scaled to the volatility of
no removal, so the gap tracks the Sharpe difference rather than extra risk taken.
The 50% removal was 54 points ahead at the end of 2018 and ends at 45; 25% gained
less and kept most of it.

<div class="research-figure responsive-figure">
  {% include blog-chart.html chart="gap" source="/assets/ridge-style-removal/equal-vol-gap.json?v=3" base="/assets/ridge-style-removal/equal-vol-gap" mobile="/assets/ridge-style-removal/equal-vol-gap_mobile" version="2" label="Cumulative net return against no removal at equal volatility for style 25%, style 50% and PCA 50%, 1999 to April 2026, with 2019 onward shaded." %}
</div>
<p class="figure-caption"><strong>Figure 5: The gains were built before 2019.</strong> Cumulative daily net return difference against no removal, in points of capital, with each variant scaled to the full-period volatility of no removal; mean of three schedules. Shaded: 2019 onward.</p>

Why the fade? Removal shifts risk from style bets to stock-specific ones, and since
2019 the book's stock-specific P&L has paid much less (a Sharpe ratio of 0.10,
against 0.63 before) while the style P&L kept paying. When the part you are moving
risk into stops paying, the trade stops working. Interestingly, a plain
score-weighted portfolio of the adjusted forecast, with no optimizer, still
improves at every strength after 2019, so the fade comes in somewhere in
selection or sizing.

## PCA and portfolio-level limits do less

Replacing the styles with the first 10 principal components of trailing returns
lowers volatility about as much but adds little Sharpe (+0.04 at 50%). It falls
short of style removal before 2019 and does a bit better since. The components
start only in 2002, so I read it as a cross-check.

Limiting style on the finished portfolio did worse. A cost-free style-beta limit
on the book was 0.13 Sharpe behind 25% forecast removal, and hard style caps in the
optimizer had no feasible solution on 24 April 2009 other than the empty book. The
150 names are chosen from the forecast before the optimizer weights them, so a
limit on the weights can't undo a selection that leans one way. That fits Clarke,
de Silva and Thorley's point that constraints limit how much of a signal reaches
the weights.[^clarke] A stronger alternative is to hedge the unpriced part of
the risk with covariance-based portfolios, as Daniel, Mota, Rottke and Santos do
for characteristic portfolios.[^daniel] I haven't tried that here.

## What I take from this

Removing part of the style component is a reasonable cleaning step for a
style-heavy forecast. It reliably lowers volatility, and over most of the history
it also raised the Sharpe ratio. A quarter of the style part is the setting I'd
pick: it captures part of the early gain, gives back very little since 2019 and
costs about one turn of turnover a year. Stronger removal did better before 2019
and worse since, and full removal, the rule most sources use, adds nothing here.

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
[^numerai]: See also Numerai's [feature-neutral correlation](https://docs.numer.ai/numerai-tournament/scoring/feature-neutral-correlation).
[^msci]: Mean post-publication information ratio across the signals; these are neutralized signals, not a model's forecast.
[^clarke]: Their transfer coefficient is 1 when the signal reaches the weights unconstrained; constrained managers typically sit between 0.3 and 0.8.
[^daniel]: The squared Sharpe ratio of their five characteristic portfolios rises from 1.16 to 2.16, per the authors' abstract.
