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
recoveries remained costly. I wanted to see whether a portfolio limit could
reduce those losses at an acceptable cost during the rest of the history.

I tested volatility-rank caps, daily portfolio scaling and limits on the
standardized beta exposure from
[part 1](/quants/portfolio-attribution.html#portfolio-beta), keeping the
existing covariance model fixed.

I kept the stock predictions fixed. The comparison covers **23 September 1998
to 27 May 2026**, combining the same three rebalancing calendars with equal
capital. Results use fixed-notional P&L; one point is 1% of strategy notional.
I use [Part 1's cost, turnover and Sharpe conventions](/quants/portfolio-attribution.html#start-with-the-positions),
including 5 basis points per dollar traded and no borrow, financing or impact
charge.

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
attribution explorer. On the same covered holdings, the conversion is

$$
E_{\mathrm{vol},t}=\frac{A_t V_t-\mu_t N_t}{\sigma_t},
\qquad A_t=\sum_i|w_{i,t}|,\quad N_t=\sum_i w_{i,t}.
$$

Here $\mu_t$ and $\sigma_t$ are the model's weighted rank mean and standard
deviation. A rank cap therefore has no fixed standardized equivalent: it
also depends on gross and net exposure. With the holdings entering the 2009
rebound held fixed, ±0.30 maps to roughly **[−0.515, +0.678]** standardized
units; at the 2020 low it maps to **[−0.425, +0.515]**. Those are coordinate
conversions of the original book, not the reoptimized portfolios.

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

The 7% target is an illustrative level below the original's 7.9% realized
volatility. The cap at one makes the trading rule reduce size only; whether
that helps depends on which gains and losses it scales down.

Scaling every position together reduces the dollars behind the bet while
preserving its volatility tilt per dollar. For Table 1, I rescale each saved
overlay by a constant so its average gross exposure matches the original's
183.6% of notional, scaling its P&L and trading costs together. This comparison
requires multipliers of about 1.114 for both rules and can exceed the original
rule's size ceiling; it is a retrospective leverage comparison.

## P&L and drawdown
{: #what-the-changes-delivered }

Table 1 compares the P&L given up with the reduction in volatility and drawdown.

<div markdown="1">
<p class="table-caption"><strong>Table 1: Full-history results.</strong> Annual gross/net P&amp;L and worst drawdown are points of fixed notional; volatility is annualized. The two scaling rows match the original's full-history mean end-of-session gross exposure. Rank-cap rows retain their own gross exposure.</p>

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

Tightening the cap trades earnings for a smaller worst drawdown. The trade-off
has diminishing drawdown gains at the tight end, where Sharpe also falls.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/cap-tradeoff" mobile="/assets/portfolio-attribution/cap-tradeoff_mobile" version="1" alt="The original and five volatility-rank caps: tighter caps move towards smaller worst drawdowns and lower annual net P&L." %}
</div>
<p class="figure-caption"><strong>Figure 1: Smaller drawdowns come with lower earnings.</strong> Full-history net P&amp;L per year against worst fixed-notional drawdown. Higher and further right are preferable. Labels give the symmetric rank bound; the connecting line follows the tested caps.</p>

**Fast scaling added no gross P&L advantage over constant sizing, and finished
about 0.7 points a year behind after costs, mostly because of extra trading.**
That comparison uses the fast rule's original average multiplier of 89.4%.
At equal average gross in Table 1, both overlays still earn less net P&L
than the original. Slow scaling improves Sharpe but has a worse worst drawdown.

In January 2022–May 2026, the tighter ±0.15 cap had a higher Sharpe than the
±0.30 cap, reversing their full-history ranking. The original and both caps
earned similar annual net P&L in that block. With little earnings sacrificed,
the tighter cap's lower daily volatility improves its Sharpe ranking.
That period-specific trade-off differs from the full-history result.

## Did the limits help during rebounds?

The caps do not deliver a convincing rebound improvement. In Table 2, the
loosest cap adds **0.13 points** to the median 63-session rebound; every
tighter cap has a negative median difference. Eleven inspected episodes
give little basis for treating that small gain as a reliable improvement.

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

The benefit arrived during declines. Table 3 partitions the whole history:
the ±0.20 cap earns more during the market sell-offs, but gives up more in
the remaining sessions than it gains there. The early recoveries also worsen.

<div markdown="1">
<p class="table-caption"><strong>Table 3: Where the ±0.20 cap gains and loses.</strong> Aggregate net P&amp;L points. Declines run from each preceding market peak to the low, excluding the peak day; the first begins at the available history boundary. Recoveries cover the next 63 sessions after each of the 11 lows. These sets do not overlap, and the three rows reconcile to full-history P&amp;L.</p>

| Sessions | Days | Original | Tilt limit ±0.20 | Difference |
| :--- | ---: | ---: | ---: | ---: |
| Market declines | 1,480 | +53.90 | +59.84 | +5.94 |
| First 63-session recoveries | 693 | +15.37 | +14.38 | −0.99 |
| All other sessions | 4,789 | +243.64 | +219.88 | −23.76 |
{: .research-table .comparison-table .attribution-table }
</div>

## Test beta exposure directly
{: #what-i-would-test-next }

The baseline already bounds its estimated market beta at rebalance, yet it
retains the negative beta-style tilt shown in
[part 1](/quants/portfolio-attribution.html#portfolio-beta). I added a limit
on that exposure, using the same standardized stock-beta descriptor as the
attribution model.

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
before execution. Table 4 compares their full-history P&L and drawdown.

<div markdown="1">
<p class="table-caption"><strong>Table 4: Direct beta-style limits over the full history.</strong> Same portfolio, dates, costs and definitions as Table 1. These bounds are standardized exposure per strategy notional, not market-return beta.</p>

| Rule | Gross / year | Net / year | Volatility | Sharpe | Worst drawdown | Turnover |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Original | 12.71 | 11.33 | 7.90% | 1.43 | −16.32 | 27.6× |
| Beta limit ±0.50 | 12.72 | 11.33 | 7.88% | 1.44 | −16.13 | 27.7× |
| Beta limit ±0.30 | 12.70 | 11.31 | 7.81% | 1.45 | −15.41 | 27.8× |
| Beta limit ±0.10 | 12.55 | 11.16 | 7.70% | 1.45 | −14.30 | 27.8× |
{: .research-table .comparison-table .portfolio-card-table }
</div>

The tightest beta cap gives up about **0.16 points of annual net P&L** while
reducing the worst drawdown. Table 5 shows a small positive median rebound
difference at ±0.10, with a much larger gain in 2009 lifting the mean.

<div markdown="1">
<p class="table-caption"><strong>Table 5: Beta limits across the same 11 lows.</strong> Counts show higher net P&amp;L than the original. Mean and median differences are fixed-notional points over the first 63 sessions, matching Table 2.</p>

| Beta limit | Improved · 21 sessions | Improved · 63 sessions | Mean difference | Median difference |
| :--- | ---: | ---: | ---: | ---: |
| ±0.50 | 4/11 | 6/11 | −0.01 | +0.03 |
| ±0.30 | 6/11 | 6/11 | +0.16 | +0.01 |
| ±0.10 | 7/11 | 7/11 | +0.48 | +0.17 |
{: .research-table .comparison-table .attribution-table }
</div>

Every beta cap still worsens the first three months of the 2020 recovery.
The tightest cap also earns less across the market-decline windows and lowers
Sharpe in the reused 2022–26 block. Its median improvement remains positive
at 126 sessions.

Realized market beta rises from **+0.068 to
+0.091** under the tightest cap. Reducing a negative standardized-beta tilt
changes which stocks the optimizer holds and slightly reduces gross exposure.
All solved targets respected both their new cap and the original
market-beta limit. Available loadings covered about 93% of gross target
exposure; two rebalances in September 2001 had no coverage, so the added
restriction was ineffective on those dates.

## Would I use these limits?
{: #what-the-experiment-settles }

I would keep the original portfolio for now. The volatility caps cost P&L
and worsen typical rebounds as they tighten. Fast volatility scaling loses
to constant sizing after trading costs.

The direct beta cap is more promising, but its small typical rebound gain
comes with a worse 2020 recovery and less protection during market declines.
That is too uneven for me to adopt it as a rebound limit.

The open question is whether limiting several persistent factor exposures
together can reduce the early-recovery losses while preserving the shorts'
protection during declines. The limits tested here have not achieved that
consistently.

I would judge a further test on median and aggregate first-63-session P&L,
preserved aggregate decline-window P&L, and a full-history earnings budget
fixed before running it. I have not set that budget or tested a joint-factor
limit. Replacing the covariance is a separate question: it would also need
stock-specific risk forecasts and calibration checks at 21 and 63 sessions.

<aside class="research-note" markdown="1">
**In-sample notes.** All comparisons use inspected history. The ±0.30, ±0.25
and ±0.15 rank caps were added after inspecting the first two; the beta caps
were fixed after reviewing those results. The 2022–26 block has already
informed research choices. Market lows are identified retrospectively, and
constant sizing and equal-gross rescaling use full-history averages. The
attribution model's normalization inherits retrospective sector availability.
The trading rules use decision-time prices and descriptors, but these results
remain exploratory comparisons rather than an untouched validation.
</aside>

<details markdown="1">
<summary>Appendix: intermediate caps and original sizing comparisons</summary>

Table 6 retains intermediate caps and the original, unrescaled sizing rules.

<div markdown="1">
<p class="table-caption"><strong>Table 6: Additional full-history comparisons.</strong> Annual gross/net P&amp;L and worst drawdown are fixed-notional points; volatility is annualized. Scaling rows retain the original cap at full size; each constant-size row uses its overlay's historical average multiplier.</p>

| Rule | Gross / year | Net / year | Volatility | Sharpe | Worst drawdown | Turnover |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Tilt limit ±0.25 | 12.40 | 10.97 | 7.57% | 1.45 | −13.83 | 28.7× |
| Tilt limit ±0.15 | 11.76 | 10.29 | 7.29% | 1.41 | −12.00 | 29.3× |
| Daily scaling · 5 sessions | 11.30 | 9.44 | 6.71% | 1.41 | −14.17 | 37.2× |
| Constant 89.4% size | 11.36 | 10.12 | 7.06% | 1.43 | −14.59 | 24.7× |
| Daily scaling · 21 sessions | 11.39 | 9.95 | 6.79% | 1.47 | −15.51 | 28.9× |
| Constant 89.2% size | 11.34 | 10.11 | 7.05% | 1.43 | −14.56 | 24.7× |
{: .research-table .comparison-table .portfolio-card-table }
</div>

</details>
