---
layout: post
title: "Performance Attribution, Part 3: Can Risk Limits Improve Rebounds?"
description: "Tilt limits buy lower drawdown but worsen typical rebounds as they tighten. Direct beta limits offer modest, uneven improvement."
permalink: /quants/managing-rebound-risk.html
toc: true
date: 2026-09-09
categories: ["Risk & attribution"]
article_label: Performance attribution · Part 3 of 3
series_id: performance-attribution
series_order: 3
---

<p class="article-summary">The rebound analysis points to a defensive tilt that can become costly when markets recover. I test limits on that tilt, daily volatility scaling and beta-exposure limits, looking for better rebounds without giving up too much elsewhere.</p>

Once a pattern shows up in attribution, it's tempting to add a constraint
and move on. But a limit changes the portfolio on every date it applies,
including the periods when that exposure was useful. The question is whether
it fixes enough of the problem to justify what it gives up elsewhere.

For the [rebound losses](/quants/short-book-rebounds.html), I try three approaches:
limit the low-volatility tilt, reduce portfolio size when recent volatility
rises, and limit standardized beta exposure directly. I want to know which,
if any, improves the early recovery while preserving protection during declines.

I keep the forecasts, covariance model and execution rules unchanged. Three rebalancing
calendars receive equal capital. The original portfolio is labelled
**Original** in the comparisons below.

I use the same portfolio, period and [conventions as part 1](/quants/portfolio-attribution.html#pnl-conventions):
fixed-notional P&L points, 5 bp trading costs, and no borrow, financing or impact.

## Limit the volatility tilt

The strategy ranks stocks by 21-session volatility on a scale from −1
(least volatile) to +1 (most volatile). I measure the book's tilt as

$$
V_t=\frac{\sum_i w_{i,t}u_{i,t}}{\sum_i |w_{i,t}|},
$$

where $u_{i,t}$ is the volatility rank and $w_{i,t}$ the signed position weight.
Long positions in low-volatility stocks and short positions in high-volatility
stocks both make $V_t$ negative.
Dividing by gross exposure expresses the average tilt per dollar invested.

This measure uses volatility ranks per dollar of gross exposure.
[Part 1's factor exposure](/quants/portfolio-attribution.html#apply-the-fit-to-the-portfolio)
uses centered, standardized characteristics per unit of strategy notional,
so the numerical limits are on different scales.

I replayed the optimizer with five limits: **±0.30, ±0.25, ±0.20, ±0.15
and ±0.10**.
The limits apply whenever each calendar rebalances, about every three weeks.
Prices and ranks continue moving between those decisions.

Even the loosest limit reached its boundary on **53.4% of rebalances**.
Its average daily tilt moved only modestly, from −0.286 to −0.248;
tighter limits were binding more often and reduced the tilt further. The measurements
covered about 99.5% of gross holdings; reported P&L includes every position.

## Reduce size when volatility rises

I also tried reducing the whole book when recent P&L became more volatile.
This keeps the same stock mix while changing the amount at risk. I estimate
volatility from an
exponentially weighted average of squared daily gross P&L, annualized using
252 sessions, with half-lives of **5** and **21 sessions**. The size multiplier is

$$
m_t=\min\left(1,\frac{7\%}{\widehat{\sigma}_t}\right).
$$

The scaling signal uses information available before execution at the following close.
The resized positions then affect the next session's
P&L. Each overlay follows the original scheduled stock book and charges for
both its scheduled trades and additional resizing trades.

I use an illustrative 7% target, below the original's 7.9% realized volatility.
Since the multiplier stays at or below one, this reduces both gains and losses.

Scaling preserves the tilt per dollar. For Table 1, I rescale each overlay's
positions, P&L and costs to match the original's average gross exposure of
183.6% of notional. The rescaled comparison can exceed full size;
the trading rule itself cannot.

## P&L and drawdown
{: #what-the-changes-delivered }

Table 1 compares the P&L given up with the reduction in volatility and drawdown.

<div markdown="1">
<p class="table-caption"><strong>Table 1: Full-history results.</strong> Annual gross/net P&amp;L and worst drawdown are points of fixed notional; volatility is annualized. The two scaling rows match the original's full-history mean end-of-session gross exposure. Tilt-limit rows retain their own gross exposure.</p>

| Rule | Gross / year | Net / year | Volatility | Sharpe | Worst drawdown | Turnover |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Original | 12.71 | 11.33 | 7.90% | 1.43 | −16.32 | 27.6× |
| Tilt limit ±0.30 | 12.58 | 11.16 | 7.67% | 1.45 | −14.12 | 28.4× |
| Tilt limit ±0.20 | 12.10 | 10.65 | 7.44% | 1.43 | −12.76 | 29.0× |
| Tilt limit ±0.10 | 11.15 | 9.68 | 7.16% | 1.35 | −11.48 | 29.4× |
| Scaling · 5 sessions | 12.59 | 10.52 | 7.47% | 1.41 | −15.79 | 41.4× |
| Scaling · 21 sessions | 12.68 | 11.07 | 7.55% | 1.47 | −17.27 | 32.2× |
{: .research-table .comparison-table .portfolio-card-table }
</div>

Figure 1 traces the cost of tighter limits: lower net P&L for a smaller worst
drawdown, with diminishing drawdown gains at the tight end, where Sharpe falls.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/cap-tradeoff" mobile="/assets/portfolio-attribution/cap-tradeoff_mobile" version="1" alt="The original and five tilt limits: tighter limits move towards smaller worst drawdowns and lower annual net P&L." %}
</div>
<p class="figure-caption"><strong>Figure 1: Smaller drawdowns come with lower P&amp;L.</strong> Full-history net P&amp;L per year against worst drawdown. Higher and further right are preferable. Labels give the symmetric tilt limit.</p>

**Fast scaling added no gross P&L advantage over constant sizing, and finished
about 0.7 points a year behind after costs, mostly because of extra trading.**
That comparison uses the fast rule's original average multiplier of 89.4%.
At equal average gross in Table 1, both overlays still earn less net P&L
than the original. Slow scaling improves Sharpe but has a larger maximum drawdown.

In January 2022–May 2026, the tighter ±0.15 limit had a higher Sharpe than the
±0.30 limit, reversing their full-history ranking. The original and both limits
earned similar annual net P&L in that block. With little P&L sacrificed,
the tighter limit's lower daily volatility improves its Sharpe ranking.
That period-specific trade-off differs from the full-history result.

## Did the limits help during rebounds?

The smaller drawdowns don't solve the problem I started with. Table 2 shows
a small positive median rebound difference at ±0.30 and negative medians at
every tighter limit. With eleven episodes, I wouldn't put much
weight on that small gain.

<div markdown="1">
<p class="table-caption"><strong>Table 2: Rebound results across all 11 lows.</strong> Counts show episodes with higher net P&amp;L than the original. Mean and median differences are net P&amp;L points over the first 63 sessions after each low.</p>

| Tilt limit | Improved · 21 sessions | Improved · 63 sessions | Mean difference | Median difference |
| :--- | ---: | ---: | ---: | ---: |
| ±0.30 | 8/11 | 7/11 | +0.20 | +0.13 |
| ±0.25 | 7/11 | 5/11 | +0.11 | −0.06 |
| ±0.20 | 6/11 | 5/11 | −0.09 | −0.08 |
| ±0.15 | 4/11 | 4/11 | −0.28 | −0.18 |
| ±0.10 | 4/11 | 5/11 | −0.47 | −0.41 |
{: .research-table .comparison-table .attribution-table }
</div>

All five limits improved the first three months of the 2009 rebound;
every limit earned less during the equivalent 2020 window.

Table 3 locates the benefit in declines. The ±0.20 limit gains there but
loses more elsewhere, including the early rebounds. That's useful if I'm
willing to give up P&L for more decline protection, but it gives me no reason
to prefer the limit as a rebound fix.

<div markdown="1">
<p class="table-caption"><strong>Table 3: Where the ±0.20 limit gains and loses.</strong> Aggregate net P&amp;L points. Declines run from each preceding market peak to the low, excluding the peak day; the first begins at the available history boundary. Rebounds cover the next 63 sessions after each of the 11 lows. These sets do not overlap, and the three rows reconcile to full-history P&amp;L.</p>

| Sessions | Days | Original | Tilt limit ±0.20 | Difference |
| :--- | ---: | ---: | ---: | ---: |
| Market declines | 1,480 | +53.90 | +59.84 | +5.94 |
| First 63-session rebounds | 693 | +15.37 | +14.38 | −0.99 |
| All other sessions | 4,789 | +243.64 | +219.88 | −23.76 |
{: .research-table .comparison-table .attribution-table }
</div>

## Test beta exposure directly
{: #what-i-would-test-next }

Beta deserves a direct test too: the shorts held higher-beta stocks in both
major rebounds. The existing market-beta limit still leaves the negative
standardized beta exposure shown in
[part 1](/quants/portfolio-attribution.html#portfolio-beta), so I added a limit
on that exposure:

$$
E_{\beta}(w)=\sum_i w_i z_{i,\beta},
\qquad -b\leq E_{\beta}(w)\leq b.
$$

I set three limits before running the comparison: **±0.50, ±0.30 and ±0.10**,
using Part 1's standardized stock-beta descriptor and weights per strategy
notional. Missing loadings receive the universe mean, zero; I measure their
share of gross exposure.

All existing portfolio settings remain, including the separate ±0.05 market-beta
limit. Each new limit applies at scheduled rebalance, with loadings observed
before execution. Table 4 compares their full-history P&L and drawdown.

<div markdown="1">
<p class="table-caption"><strong>Table 4: Direct standardized beta limits over the full history.</strong> Same portfolio, dates, costs and definitions as Table 1. The limits use standardized exposure per strategy notional.</p>

| Rule | Gross / year | Net / year | Volatility | Sharpe | Worst drawdown | Turnover |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Original | 12.71 | 11.33 | 7.90% | 1.43 | −16.32 | 27.6× |
| Beta limit ±0.50 | 12.72 | 11.33 | 7.88% | 1.44 | −16.13 | 27.7× |
| Beta limit ±0.30 | 12.70 | 11.31 | 7.81% | 1.45 | −15.41 | 27.8× |
| Beta limit ±0.10 | 12.55 | 11.16 | 7.70% | 1.45 | −14.30 | 27.8× |
{: .research-table .comparison-table .portfolio-card-table }
</div>

The tightest beta limit gives up about **0.2 points of annual net P&L** while
reducing the worst drawdown. Its median rebound gain in Table 5 is small;
a much larger gain in 2009 lifts the mean.

<div markdown="1">
<p class="table-caption"><strong>Table 5: Beta limits across the same 11 lows.</strong> Counts show higher net P&amp;L than the original. Mean and median differences are fixed-notional points over the first 63 sessions, matching Table 2.</p>

| Beta limit | Improved · 21 sessions | Improved · 63 sessions | Mean difference | Median difference |
| :--- | ---: | ---: | ---: | ---: |
| ±0.50 | 4/11 | 6/11 | −0.01 | +0.03 |
| ±0.30 | 6/11 | 6/11 | +0.16 | +0.01 |
| ±0.10 | 7/11 | 7/11 | +0.48 | +0.17 |
{: .research-table .comparison-table .attribution-table }
</div>

Every beta limit still worsens the first three months of the 2020 rebound.
The tightest limit also earns less across the market-decline windows and lowers
Sharpe in 2022–26. Its median improvement remains positive
at 126 sessions.

Realized market beta rises from **+0.068 to
+0.091** under the tightest limit. Reducing a negative standardized-beta tilt
changes which stocks the optimizer holds and slightly reduces gross exposure.
All solved targets respected both their new limit and the original
market-beta limit. Available loadings covered about 93% of gross target
exposure; two rebalances in September 2001 had no coverage, so the added
limit was ineffective on those dates.

## Would I change the baseline?
{: #what-the-experiment-settles }

For now, I still prefer the original portfolio as a baseline. Tighter tilt limits cost P&L and worsen
typical rebounds; fast scaling loses to constant sizing after trading costs.

The beta limit's small typical gain comes with a worse 2020 rebound and less
decline protection. That's too uneven an improvement for me to include it in the baseline.

<aside class="research-note" markdown="1">
**Calculation notes.** Market lows are selected in hindsight, and
constant sizing and equal-gross rescaling use full-history averages. The
factor model's normalization inherits Part 1's sector labels.
The trading rules use decision-time prices and descriptors.
</aside>
