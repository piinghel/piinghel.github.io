---
layout: post
title: "Performance Attribution, Part 3: What Volatility-Tilt Limits Cost, and What They Don't Fix"
description: "Volatility-tilt caps buy lower drawdown but worsen typical rebounds as they tighten. Direct beta limits offer modest, uneven improvement."
permalink: /quants/managing-rebound-risk.html
toc: true
show_date: false
date: 2026-09-09
categories: ["Portfolio management"]
article_label: Performance attribution · Part 3 of 3
series_id: performance-attribution
series_order: 3
series_previous: /quants/short-book-rebounds.html
series_end: true
---

<p class="article-summary">Volatility-rank caps buy lower historical drawdown at a cost to P&amp;L. Tighter caps worsen the median rebound result. Direct beta-style limits give modest, uneven improvement; daily volatility scaling adds costs without beating constant sizing on gross P&amp;L.</p>

The [rebound study](/quants/short-book-rebounds.html) found an early-recovery
vulnerability: higher-beta, more volatile shorts often rose faster than the
longs. By six months the typical imbalance had reversed, although a few severe
paths remained costly. A permanent restriction therefore has to improve those
paths without giving away too much during the rest of the history.

I first tested volatility-rank caps and daily portfolio scaling. The rank
caps reduced full-history drawdown, but their rebound results did not justify
the protection I was looking for. I then tested limits on the standardized
beta exposure from [part 1](/quants/portfolio-attribution.html#portfolio-beta),
keeping the existing covariance model fixed.

I kept the stock predictions fixed. The comparison covers **23 September 1998
to 27 May 2026**, combining the same three rebalancing calendars with equal
capital. Results use fixed-notional P&L; one point is 1% of strategy notional.
Trading costs are **5 basis points per dollar traded**. Borrow, financing and
market impact would require additional estimates.

## Limit the volatility tilt

The strategy ranks stocks by 21-session volatility on a scale from −1
(least volatile) to +1 (most volatile). I measure the book's tilt as

$$
V_t=\frac{\sum_i w_{i,t}u_{i,t}}{\sum_i |w_{i,t}|},
$$

where $u_{i,t}$ is the volatility rank and $w_{i,t}$ the signed position weight.
Buying quiet stocks and shorting volatile stocks both make $V_t$ negative.
Dividing by gross exposure expresses the average tilt per dollar invested.

This uses the raw volatility ranks. In [part 1](/quants/portfolio-attribution.html#apply-the-fit-to-the-portfolio),
I standardize those ranks and measure exposure relative to fixed strategy
notional. Here the limit is in rank units per dollar of gross exposure;
negative values represent the low-volatility tilt shown as positive in the
attribution explorer.

I replayed the optimizer with five limits: **±0.30, ±0.25, ±0.20, ±0.15
and ±0.10**, keeping its existing covariance model, stock forecasts and execution rules.
The limits apply whenever each calendar rebalances, about every three weeks.
Prices and ranks continue moving between those decisions.

Even the loosest cap reached its boundary on **53.4% of rebalances**.
Its average daily tilt moved only modestly, from −0.286 to −0.248;
tighter caps bound more often and reduced the tilt further. The measurements
covered about 99.5% of gross holdings; reported P&L includes every position.

## Reduce size when volatility rises

I also tested daily portfolio scaling. I estimate volatility from an
exponentially weighted average of squared daily gross P&L, annualized using
252 sessions, with half-lives of **5** and **21 sessions**. The size multiplier is

$$
m_t=\min\left(1,\frac{7\%}{\widehat{\sigma}_t}\right).
$$

The first 21 observations stay at full size. A signal calculated after one
close changes positions at the following close and affects the next session's
P&L. Each overlay follows the original scheduled stock book and charges for
both its scheduled trades and additional resizing trades.

Scaling every position together reduces the dollars behind the bet while
preserving its volatility tilt per dollar. To assess the value of changing
size through time, I compare each overlay with a constant multiplier equal
to its average size: **89.4%** for the fast rule and **89.2%** for the slower
one. This asks whether changing size through time helps more than simply
running a smaller book. Table 1 shows the fast rule; the slower comparison
and intermediate rank caps are retained in the appendix.

## What the changes delivered

Table 1 keeps the main comparisons together. Gross and net P&L make the trading
cost visible alongside volatility and drawdown.

<div markdown="1">
<p class="table-caption"><strong>Table 1: Full-history results.</strong> Annual gross/net P&amp;L and worst drawdown are points of fixed notional. Volatility is annualized; Sharpe uses a zero cash rate. Turnover is annual two-way traded notional divided by capital.</p>

| Rule | Gross / year | Net / year | Volatility | Sharpe | Worst drawdown | Turnover |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Original | 12.71 | 11.33 | 7.90% | 1.43 | −16.32 | 27.6× |
| Tilt limit ±0.30 | 12.58 | 11.16 | 7.67% | 1.45 | −14.12 | 28.4× |
| Tilt limit ±0.20 | 12.10 | 10.65 | 7.44% | 1.43 | −12.76 | 29.0× |
| Tilt limit ±0.10 | 11.15 | 9.68 | 7.16% | 1.35 | −11.48 | 29.4× |
| Daily scaling · 5 sessions | 11.30 | 9.44 | 6.71% | 1.41 | −14.17 | 37.2× |
| Constant 89.4% size | 11.36 | 10.12 | 7.06% | 1.43 | −14.59 | 24.7× |
{: .research-table .comparison-table .portfolio-card-table }
</div>

Tightening the cap trades earnings for a smaller worst drawdown. The trade-off
has diminishing drawdown gains at the tight end, where Sharpe also falls.
That is a result about the full path; the recovery windows below determine
whether it addresses the original problem.

**Fast scaling added no gross P&L advantage over constant sizing, and finished
about 0.7 points a year behind after costs, mostly because of extra trading.**
The drawdown improvement was small. The slower rule traded less, but also
earned less net P&L than its constant-size comparison.

In January 2022–May 2026, the tighter ±0.15 cap had a higher Sharpe than the
±0.30 cap, reversing their full-history ranking. The original and both caps
earned similar annual net P&L in that block. This sensitivity to the period
weakens any claim that one bound is a durable optimum.

## Did the limits help during rebounds?

Table 2 compares improvement counts with the mean and median effect.
The loosest cap adds just **0.13 points** to the median 63-session rebound.
Every tighter cap has a negative median difference. These 11 episodes give
little support for adopting rank caps as reliable rebound protection.

<div markdown="1">
<p class="table-caption"><strong>Table 2: Recovery results across all 11 lows.</strong> Counts show episodes with higher net P&amp;L than the original. Mean and median differences are net P&amp;L points over the first 63 sessions after each low.</p>

| Tilt limit | Improved · 21 sessions | Improved · 63 sessions | Mean difference | Median difference |
| :--- | ---: | ---: | ---: | ---: |
| ±0.30 | 8/11 | 7/11 | +0.20 | +0.13 |
| ±0.25 | 7/11 | 5/11 | +0.11 | −0.06 |
| ±0.20 | 6/11 | 5/11 | −0.09 | −0.08 |
| ±0.15 | 4/11 | 4/11 | −0.28 | −0.18 |
| ±0.10 | 4/11 | 5/11 | −0.47 | −0.41 |
{: .research-table .comparison-table .attribution-table }
</div>

All five limits improved the first three months of the 2009 recovery;
every limit earned less during the equivalent 2020 window. More drawdown
protection over the full history did not translate into consistent rebound
protection.

Some benefit arrived during the decline itself. The ±0.20 cap reduced the
loss between the February 2020 market peak and the March low, and earned more
in aggregate across the 11 market-decline windows. Outside the declines and
first 63-session recoveries, it earned less.

## Test beta exposure directly
{: #what-i-would-test-next }

The baseline already bounds its estimated market beta at rebalance. The
[beta diagnostics in part 1](/quants/portfolio-attribution.html#portfolio-beta)
show why that does not eliminate either realized beta or a negative beta-style
tilt. This comparison directly constrains the latter, using the same
standardized stock-beta descriptor that explains returns in the attribution.

$$
E_{\beta}(w)=\sum_i w_i z_{i,\beta},
\qquad -b\leq E_{\beta}(w)\leq b.
$$

I fixed three bounds before running this comparison: **±0.50, ±0.30 and
±0.10**. Stock beta uses up to 252 daily observations, with 126 required;
the model centers and scales it using square-root-cap weights. The signed
portfolio weights use fixed strategy notional. An unavailable standardized
loading is set to the universe mean, zero, and its share of gross exposure
is measured explicitly.

All existing portfolio settings remain, including the separate ±0.05 market-beta
limit. Each new cap applies at scheduled rebalance, with loadings observed
before execution. This tests an additional beta-style restriction at the
same frequency as the rank limits.

<div markdown="1">
<p class="table-caption"><strong>Table 3: Direct beta-style limits over the full history.</strong> Same portfolio, dates, costs and definitions as Table 1. These bounds are standardized exposure per strategy notional, not market-return beta.</p>

| Rule | Gross / year | Net / year | Volatility | Sharpe | Worst drawdown | Turnover |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Original | 12.71 | 11.33 | 7.90% | 1.43 | −16.32 | 27.6× |
| Beta limit ±0.50 | 12.72 | 11.33 | 7.88% | 1.44 | −16.13 | 27.7× |
| Beta limit ±0.30 | 12.70 | 11.31 | 7.81% | 1.45 | −15.41 | 27.8× |
| Beta limit ±0.10 | 12.55 | 11.16 | 7.70% | 1.45 | −14.30 | 27.8× |
{: .research-table .comparison-table .portfolio-card-table }
</div>

The tightest beta cap gives up about **0.16 points of annual net P&L** while
reducing the worst drawdown. Unlike tightening the volatility caps, tightening
beta to ±0.10 leaves a positive median rebound difference. The improvement
is modest, and the mean is helped by a much larger gain in 2009.

<div markdown="1">
<p class="table-caption"><strong>Table 4: Beta limits across the same 11 lows.</strong> Counts show higher net P&amp;L than the original. Mean and median differences are fixed-notional points over the first 63 sessions, matching Table 2.</p>

| Beta limit | Improved · 21 sessions | Improved · 63 sessions | Mean difference | Median difference |
| :--- | ---: | ---: | ---: | ---: |
| ±0.50 | 4/11 | 6/11 | −0.01 | +0.03 |
| ±0.30 | 6/11 | 6/11 | +0.16 | +0.01 |
| ±0.10 | 7/11 | 7/11 | +0.48 | +0.17 |
{: .research-table .comparison-table .attribution-table }
</div>

Every beta cap still worsens the first three months of the 2020 recovery.
The tightest cap also earns less across the market-decline windows and lowers
Sharpe in the reused 2022–26 block. At 126 sessions its median improvement
remains positive, but that does not make the protection consistent across
episodes.

There is another trade-off: realized market beta rises from **+0.068 to
+0.091** under the tightest cap. Reducing a negative standardized-beta tilt
changes which stocks the optimizer holds and slightly reduces gross exposure;
it does not necessarily bring the whole portfolio's market sensitivity closer
to zero. All solved targets respected both their new cap and the original
market-beta limit. Available loadings covered about 93% of gross target
exposure; two rebalances in September 2001 had no coverage, so the added
restriction was ineffective on those dates.

## What the experiment settles

The volatility-rank caps reduce historical drawdown at a cost in earnings,
but tighter caps worsen the typical rebound result. Fast volatility scaling
also fails to earn back its additional trading costs against constant sizing.
Those results do not justify adopting either as rebound protection.

Constraining the attribution model's beta exposure directly gives a more
encouraging historical comparison, but the typical rebound gain is small,
the 2020 rebound gets worse, and some decline protection is lost. It closes
the missing comparison without establishing a reliable fix.

The series therefore ends with an identified early-recovery vulnerability
and measured costs of trying to control it. Whether jointly limiting persistent
factor exposures can improve that path remains open. These results support
keeping the original portfolio as the reference, rather than adopting a
rebound-protection rule from this inspected history.

<aside class="research-note" markdown="1">
**In-sample notes.** All comparisons use inspected history. The ±0.30, ±0.25
and ±0.15 rank caps were added after inspecting the first two; the beta caps
were fixed after reviewing those results. The 2022–26 block has already
informed research choices. Market lows are identified retrospectively, and
constant sizing uses each overlay's full-history average multiplier. The
attribution model's normalization inherits retrospective sector availability.
The trading rules use decision-time prices and descriptors, but these results
remain exploratory comparisons rather than an untouched validation.
</aside>

<details markdown="1">
<summary>Appendix: intermediate caps and slower scaling</summary>

Table 5 retains the remaining full-history comparisons on the same basis
as Table 1.

<div markdown="1">
<p class="table-caption"><strong>Table 5: Additional full-history comparisons.</strong> Annual gross/net P&amp;L and worst drawdown are fixed-notional points; volatility is annualized. Turnover is annual two-way traded notional divided by capital.</p>

| Rule | Gross / year | Net / year | Volatility | Sharpe | Worst drawdown | Turnover |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Tilt limit ±0.25 | 12.40 | 10.97 | 7.57% | 1.45 | −13.83 | 28.7× |
| Tilt limit ±0.15 | 11.76 | 10.29 | 7.29% | 1.41 | −12.00 | 29.3× |
| Daily scaling · 21 sessions | 11.39 | 9.95 | 6.79% | 1.47 | −15.51 | 28.9× |
| Constant 89.2% size | 11.34 | 10.11 | 7.05% | 1.43 | −14.56 | 24.7× |
{: .research-table .comparison-table .portfolio-card-table }
</div>

</details>
