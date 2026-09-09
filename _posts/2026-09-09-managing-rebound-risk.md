---
layout: post
title: "Managing Rebound Risk with Exposure Limits"
description: "What happened when I capped the volatility tilt and scaled the portfolio using faster risk estimates."
permalink: /quants/managing-rebound-risk.html
toc: true
show_date: false
date: 2026-09-09
categories: ["Portfolio management"]
article_label: Portfolio attribution · Part 3
series_previous: /quants/short-book-rebounds.html
series_end: true
---

<p class="article-summary">A moderate volatility-style limit reduced the worst historical drawdown while preserving full-history Sharpe. A tighter limit gave up more return. Fast daily volatility scaling added enough trading costs to make constant smaller sizing a useful competitor.</p>

The [rebound study](/quants/short-book-rebounds.html) showed defensive longs
facing more volatile, higher-beta shorts. I tested two ways to manage that
exposure: change the mix of positions, or reduce the whole portfolio when
recent volatility rises.

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

I replayed the optimizer with **$|V_t|\leq0.20$** and **$|V_t|\leq0.10$**,
keeping its existing covariance model, stock forecasts and execution rules.
The limits apply whenever each calendar rebalances, about every three weeks.
Prices and ranks continue moving between those decisions.

The moderate limit reached its boundary on **82.9% of rebalances**; the
tighter one did so on **96.3%**. Both therefore change the portfolio regularly.
Across the actual daily holdings, the mean tilt moved from **−0.286** to
**−0.193** and **−0.121**. The measurements covered about 99.5% of gross
holdings; reported P&L includes every position.

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
one. Those constant sizes are calculated from the complete history and serve
as retrospective comparisons.

## What the changes delivered

Table 1 compares all seven portfolios. Gross and net P&L make the trading
cost visible alongside volatility and drawdown.

<div markdown="1">
<p class="table-caption"><strong>Table 1: Full-history results.</strong> Annual gross/net P&amp;L and worst drawdown are points of fixed notional. Volatility is annualized; Sharpe uses a zero cash rate. Turnover is annual two-way traded notional divided by capital.</p>

| Rule | Gross / year | Net / year | Volatility | Sharpe | Worst drawdown | Turnover |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Original | 12.71 | 11.33 | 7.90% | 1.43 | −16.32 | 27.6× |
| Tilt limit ±0.20 | 12.10 | 10.65 | 7.44% | 1.43 | −12.76 | 29.0× |
| Tilt limit ±0.10 | 11.15 | 9.68 | 7.16% | 1.35 | −11.48 | 29.4× |
| Daily scaling · 5 sessions | 11.30 | 9.44 | 6.71% | 1.41 | −14.17 | 37.2× |
| Constant 89.4% size | 11.36 | 10.12 | 7.06% | 1.43 | −14.59 | 24.7× |
| Daily scaling · 21 sessions | 11.39 | 9.95 | 6.79% | 1.47 | −15.51 | 28.9× |
| Constant 89.2% size | 11.34 | 10.11 | 7.05% | 1.43 | −14.56 | 24.7× |
{: .research-table .comparison-table .portfolio-card-table }
</div>

The **±0.20 limit** reduced the worst drawdown from **16.32 to 12.76 points**,
with essentially the same Sharpe. Annual net P&L fell by **0.68 points**.
Tightening the limit to ±0.10 reduced drawdown further while giving up more
return and lowering full-history Sharpe.

Fast scaling earned almost the same gross P&L as constant 89.4% sizing.
Its extra trading reduced net P&L to **9.44 points a year**, against **10.12**.
The worst drawdown improved by about **0.41 points**. The 21-session rule
traded less and had the highest full-history Sharpe, but a deeper worst
drawdown than its constant-size comparison.

I also checked January 2022–May 2026 separately. The original earned **8.10
points a year**, with Sharpe **0.92** and worst drawdown **9.17 points**.
The moderate cap earned **7.91**, with Sharpe **0.97** and drawdown **7.96**.
Both daily-scaling rules earned less than their constant-size comparisons.
This later block had already informed earlier research choices.

## Did the limits help during rebounds?

The moderate cap improved P&L in **6 of 11** first-21-session recoveries and
**5 of 11** first-63-session recoveries. Table 2 shows why I would be cautious
about choosing it solely from the full-history drawdown.

<div markdown="1">
<p class="table-caption"><strong>Table 2: Recovery gains vary by episode.</strong> Net P&amp;L points over the first 21 and 63 sessions after the market lows of 9 March 2009 and 23 March 2020.</p>

| Window | Original | Limit ±0.20 | Limit ±0.10 |
| :--- | ---: | ---: | ---: |
| 2009 · 21 sessions | +0.01 | −0.12 | −0.45 |
| 2009 · 63 sessions | −6.45 | −4.60 | −5.10 |
| 2020 · 21 sessions | +1.78 | −0.23 | −0.77 |
| 2020 · 63 sessions | +0.43 | −0.28 | −0.50 |
{: .research-table .comparison-table .attribution-table }
</div>

The moderate cap helped over the first three months of the 2009 recovery.
In 2020, both capped books lost money over the first 21 and 63 sessions,
while the original made money.

Some benefit arrived during the decline itself. From the market peak on
**19 February 2020 through 23 March**, the original lost **8.27 points**;
the moderate cap lost **1.73**. Across the 11 market-decline windows, the
moderate cap also earned more in aggregate. Outside the declines and first
63-session recoveries, it earned less. The trade-off extends across market
conditions.

The lows are identified retrospectively to evaluate the portfolios. The
tested sizing rules use information available at their decision dates.

## What I would test next

The moderate cap is a useful candidate: it changes the shared exposure and
improves drawdown at a modest cost to earnings. The mixed recovery results
make me want a more targeted test before adopting it.

I would first test a **daily tolerance band** around the volatility-style
limit. It would trigger a trade when the actual book moves beyond an outer
boundary, then bring it back inside an inner boundary. That directly
addresses drift between scheduled rebalances and lets small daily changes
pass without trading.

I would also test smaller weights for shorts where **large prior losses,
high beta and high volatility overlap**, with a limit on their combined
risk that accounts for correlations. Replacing part of those positions with
a broad market hedge, matched on estimated market sensitivity, would provide
another comparison.

These next tests would keep the predictions fixed and measure net P&L,
turnover, drawdowns and decline protection alongside the resulting exposures.
The original portfolio remains the reference implementation; the completed
historical tests make the trade-offs concrete.
