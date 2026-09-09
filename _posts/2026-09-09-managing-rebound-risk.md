---
layout: post
title: "Performance Attribution, Part 3: Managing Rebound Risk with Exposure Limits"
description: "Five volatility-tilt limits, daily sizing controls, and the next step: exposure limits from the attribution risk model."
permalink: /quants/managing-rebound-risk.html
toc: true
show_date: false
date: 2026-09-09
categories: ["Portfolio management"]
article_label: Performance attribution · Part 3 of 3
series_previous: /quants/short-book-rebounds.html
series_end: true
---

<p class="article-summary">Volatility-rank limits reduced historical drawdown, with a growing cost in P&amp;L as I tightened them. Recovery results remained mixed. The next step is to use the attribution risk model's factor exposures to set portfolio limits.</p>

The [rebound study](/quants/short-book-rebounds.html) showed defensive longs
facing more volatile, higher-beta shorts. I want to use the
[risk model from part 1](/quants/portfolio-attribution.html#fit-the-common-returns)
to manage those exposures inside the portfolio optimizer. The same model
should connect the risks I constrain before trading with the P&L I explain
afterwards.

I started with two controls: limit the portfolio's volatility-rank tilt,
or reduce the whole portfolio when recent volatility rises. These tests
show what a simple restriction buys before introducing the model's factor
exposure limits.

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

The ±0.30 limit reached its boundary on **53.4% of rebalances**, compared with
**82.9%** at ±0.20 and **96.3%** at ±0.10. Across the actual daily holdings,
the corresponding mean tilts were **−0.248, −0.193 and −0.121**, against
**−0.286** for the original. The measurements covered about 99.5% of gross
holdings; reported P&L includes every position. I added ±0.30, ±0.25 and
±0.15 after inspecting the first two limits, using the same market history.

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
one. For example, constant 89.4% sizing reduces a long position worth 100,000
dollars to 89,400 dollars, and scales shorts by the same amount. This asks whether changing size
through time helps more than simply running a smaller book. The average
multipliers are calculated from the complete history, so these are
retrospective comparisons.

## What the changes delivered

Table 1 compares all ten portfolios. Gross and net P&L make the trading
cost visible alongside volatility and drawdown.

<div markdown="1">
<p class="table-caption"><strong>Table 1: Full-history results.</strong> Annual gross/net P&amp;L and worst drawdown are points of fixed notional. Volatility is annualized; Sharpe uses a zero cash rate. Turnover is annual two-way traded notional divided by capital.</p>

| Rule | Gross / year | Net / year | Volatility | Sharpe | Worst drawdown | Turnover |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Original | 12.71 | 11.33 | 7.90% | 1.43 | −16.32 | 27.6× |
| Tilt limit ±0.30 | 12.58 | 11.16 | 7.67% | 1.45 | −14.12 | 28.4× |
| Tilt limit ±0.25 | 12.40 | 10.97 | 7.57% | 1.45 | −13.83 | 28.7× |
| Tilt limit ±0.20 | 12.10 | 10.65 | 7.44% | 1.43 | −12.76 | 29.0× |
| Tilt limit ±0.15 | 11.76 | 10.29 | 7.29% | 1.41 | −12.00 | 29.3× |
| Tilt limit ±0.10 | 11.15 | 9.68 | 7.16% | 1.35 | −11.48 | 29.4× |
| Daily scaling · 5 sessions | 11.30 | 9.44 | 6.71% | 1.41 | −14.17 | 37.2× |
| Constant 89.4% size | 11.36 | 10.12 | 7.06% | 1.43 | −14.59 | 24.7× |
| Daily scaling · 21 sessions | 11.39 | 9.95 | 6.79% | 1.47 | −15.51 | 28.9× |
| Constant 89.2% size | 11.34 | 10.11 | 7.05% | 1.43 | −14.56 | 24.7× |
{: .research-table .comparison-table .portfolio-card-table }
</div>

The **±0.30 limit** reduced the worst drawdown from **16.32 to 14.12 points**,
giving up **0.16 points** of annual net P&L. At **±0.20**, drawdown fell to
**12.76 points** for an annual sacrifice of **0.68 points**. At **±0.15**, the
figures were **12.00** and **1.03 points**. Tightening the limit progressively
bought more drawdown protection at a higher cost in earnings; full-history
Sharpe also fell below the original at the two tightest limits.

Fast scaling earned almost the same gross P&L as constant 89.4% sizing.
Its extra trading reduced net P&L to **9.44 points a year**, against **10.12**.
The worst drawdown improved by about **0.41 points**. The 21-session rule
traded less and had the highest full-history Sharpe, but a deeper worst
drawdown than its constant-size comparison.

I also checked January 2022–May 2026 separately. The original earned **8.10
points a year**, with Sharpe **0.92** and worst drawdown **9.17 points**.
The ±0.30 cap earned **8.11**, with Sharpe **0.96** and drawdown **8.32**.
The ±0.15 cap earned **8.08**, with Sharpe **1.02** and drawdown **8.21**.
Their Sharpe ranking therefore reversed in this later period.
Both daily-scaling rules earned less than their constant-size comparisons.
This later block had already informed earlier research choices.

## Did the limits help during rebounds?

The ±0.30 cap improved **8 of 11** first-21-session recoveries and **7 of 11**
first-63-session recoveries. Tighter limits were less consistent. Table 2
compares the counts with the average and median effect, so a few large
improvements cannot stand in for the typical episode.

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

All five limits improved the first three months of the **2009** recovery.
The original lost **6.45 points**; losses fell to **4.09** at ±0.30 and
**5.05** at ±0.15. Every limit earned less than the original during the
equivalent **2020** recovery. The original made **0.43 points**, against
**0.09** at ±0.30 and a loss of **0.52** at ±0.15. More drawdown protection
over the full history did not translate into better rebound performance.

Some benefit arrived during the decline itself. From the market peak on
**19 February 2020 through 23 March**, the original lost **8.27 points**;
the ±0.20 cap lost **1.73**. Across the 11 market-decline windows, this
cap also earned more in aggregate. Outside the declines and first
63-session recoveries, it earned less.

The lows are identified retrospectively to evaluate the portfolios. The
tested sizing rules use information available at their decision dates.

## Use the risk model's factor exposures
{: #what-i-would-test-next }

My next test is to put **factor-exposure limits from the attribution risk
model** into the optimizer. I would use the model's stock descriptors and
cross-sectional standardization, including its square-root-cap weights.
For each proposed portfolio, the constraints would be

$$
E_k(w)=\sum_i w_i z_{i,k},
\qquad \ell_k\leq E_k(w)\leq u_k.
$$

Here $z_{i,k}$ is stock $i$'s model loading on factor $k$, calculated from
information available before trading. The signed weight $w_i$ is measured
relative to fixed strategy notional, matching the exposure convention in
part 1. The lower and upper bounds specify how much of each selected factor
the portfolio may hold.

Z-scoring sets the units. The useful connection is to use the **same factor
definitions and exposures** in portfolio construction and attribution. A
volatility constraint can then be assessed alongside the model's momentum,
beta-style and reversal exposures, including where the optimizer moves its
bets when one limit binds. The rank limits above provide an initial
comparison; model-exposure bounds need their own settings in these units.

I would keep the current covariance model and stock forecasts fixed for
this test. That isolates the effect of the exposure constraints. The
decision-time loadings must cover every candidate stock, with missing
descriptors handled explicitly. Historical sector constraints would also
need classifications available at the time; the attribution study uses
retrospective labels.

For now, the original portfolio remains in production. The rank-based
results establish the cost of reducing one tilt. The next question is
whether constraints expressed through the risk model can control the
overlapping exposures behind rebound losses at an acceptable cost in P&L
and trading.
