---
layout: post
title: "Performance Attribution, Part 2: When the Portfolio Loses"
description: "The portfolio's P&L by theme in market declines and strong rallies: low volatility and the net long dollars trade places, and what keeps the book positive has changed."
permalink: /quants/short-book-rebounds.html
toc: true
date: 2026-09-09
last_modified_at: 2026-09-28
categories: ["Risk & attribution"]
article_label: Performance attribution · Part 2 of 2
series_id: performance-attribution
series_order: 2
---

Averages over whole periods hide when the money is made and lost. For a book
that is long low-risk stocks and short high-risk ones, the market's direction
should matter a lot, so here I split [Part
1](/quants/portfolio-attribution.html)'s theme P&L by what the market was
doing: falling hard, rallying hard, or neither.

The book, themes and [conventions](/quants/portfolio-attribution.html#pnl-conventions)
are those of Part 1. The backtest assumes shorts can always be borrowed, for
free. That matters most in 2008: the SEC banned short sales of about 800
financial stocks from 19 September to 8 October, inside the 2007–08 decline.
Financials, by sector, made 9.3 of the short book's 32.3 points from October
2007 to October 2008, while the long book lost about 34, and 2.5 of its 9.3
points during the ban itself. Rebalancing inside the ban, the book also opened
38 new short positions in financials, 2.6% of capital, which a real book could
not have done; they made about half a point.

## Market regimes
{: #market-regimes }

I define the regimes from the Russell 1000 alone, so they don't depend on the
portfolio. A **decline** runs from a peak to the lowest close before the index
recovers 15%, when that low is at least 15% below the peak; there are 15 since
1999. A **strong rally** is a stretch in which the index rose more than 13% over
63 sessions, with overlapping windows merged and decline days left out; there
are 16. The rest is the base, apart from 2% of sessions in volatility spikes,
which I leave out.

<details markdown="1">
<summary>How I define the regimes</summary>

With the index level $$I_t$$, a decline starts at a local peak $$I_p$$ and ends
at the lowest close $$I_q$$ before the index rises 15% from that low, and counts
when $$I_q/I_p-1\le-15\%$$; a new decline can only start after that recovery. A
strong rally is any 63-session window with $$I_{t+63}/I_t-1>13\%$$, overlapping
windows merged into one episode and decline sessions removed. A volatility spike
is a stretch where the index's trailing 21-session volatility is above its 90th
percentile since 1999. A leg's return in a regime is its average daily P&L over
those sessions, times 252.

</details>

<div markdown="1">
<p class="table-caption"><strong>Table 1: The book earns in every regime, least in declines and rallies.</strong> % of capital a year within each regime, after costs, January 1999–May 2026, and the number of episodes in which each lost money.</p>

| Regime | Episodes | Share of sessions | Book | Long book | Short book | Book lost |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Declines | 15 | 19% | +5.6 | −46.6 | +52.2 | 3 |
| Strong rallies | 16 | 21% | +6.4 | +45.3 | −38.9 | 5 |
| Base | | 58% | +10.2 | +17.8 | −7.6 | |
{: .research-table .comparison-table .compact-table }
</div>

The long and short books swing by about 40–50% a year in both regimes and mostly
cancel: the long book lost money in all 15 declines, the short book in 15 of
the 16 rallies. The book stays positive in both, just less so than in quieter
markets. Losing in 3 of 15 declines and 5 of 16 rallies is no worse than its
record over 63-session stretches generally: it lost in about a quarter of them,
and at that rate three or more losses in 15 is about a three-in-four chance.

## The stock gap and the net long cancel

Each leg's P&L is its gross times the return of the stocks it holds, so with
long gross $$L$$, short gross $$S$$ and the two sets of stocks returning
$$g_L$$ and $$g_S$$, the book's P&L splits into the gap between the stocks and
the net long dollars, earning the longs' return:

$$
P \approx L g_L-S g_S=S\,(g_L-g_S)+(L-S)\,g_L .
$$

Before costs, in declines the shorted stocks fell much harder than the longs,
so the gap earned 21.5% a year, and the net long dollars lost 15.0%. In strong rallies the shorted stocks
rose faster: the gap lost 7.3% a year and the net long made 14.6%. The book
comes out positive in both because the two halves nearly cancel, which is the
low-risk tilt and the beta limit working as one position.

## Low volatility and net market exposure trade places

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/theme-regimes" mobile="/assets/portfolio-attribution/theme-regimes_mobile" version="5" alt="Each theme's return in market declines and in strong rallies." %}
</div>
<p class="figure-caption"><strong>Figure 1: Low volatility and net market exposure trade places.</strong> Return in % of capital a year within each regime, January 1999–May 2026, before costs except for the whole book. The low-risk package and trading activity are subtotals of the themes below them.</p>

In declines, **low volatility** earns 18% a year and made money in all 15
episodes, while **net market exposure** loses 18% and lost in all 15. In strong
rallies the two swap: low volatility loses 13% a year and net market exposure
earns 15%. Together, as the [low-risk package](/quants/portfolio-attribution.html#where-the-return-comes-from), they net to about zero in both
regimes, but not reliably from one episode to the next: the package made money
in only 4 of the 15 declines and 8 of the 16 rallies, and its average in
declines rests on the 2000–01 bear market. Neither line times the market: the
net long sits at its limit, and exposure timing adds or subtracts less than a
point a year.

What kept the book positive has changed. In the declines up to 2008, short-term
reversal made 10.6 points and the low-risk package 9.7. In the nine declines
since 2009, the package lost 8.9 points and reversal made less than one; the
book's 18.9 points came almost entirely from stock-specific returns. In the
rallies since 2009, reversal and short interest made 12 and 8 points.

## Volatility changes reversal and stock selection

Declines and rallies are known only after the fact. Market volatility over the
previous month is known in advance, so I also split the days into thirds by the
Russell 1000's trailing 21-session volatility.

<div markdown="1">
<p class="table-caption"><strong>Table 2: Reversal pays when markets are volatile; stock selection when they are calm.</strong> % of capital a year, before costs except for the book, January 1999–May 2026. Calm and volatile are the lowest and highest thirds of days by the index's volatility over the previous 21 sessions, below 11% and above 17% a year. The t-statistic of the difference allows for autocorrelation up to 21 sessions.</p>

| | Calm | Volatile | Difference | t |
| :--- | ---: | ---: | ---: | ---: |
| Short-term return | +1.4 | +4.4 | +2.9 | 4.5 |
| Stock-specific | +3.8 | −1.7 | −5.5 | −2.5 |
| Short interest | +0.7 | +1.9 | +1.2 | 1.7 |
| Long-term return | +0.7 | −0.3 | −1.0 | −1.0 |
| Low-risk package | +3.0 | +2.5 | −0.5 | −0.2 |
| Book, after costs | +8.6 | +5.3 | −3.3 | −1.0 |
{: .research-table .comparison-table .compact-table }
</div>

Short-term reversal earns three times as much when markets are volatile, before
and after 2009, which is consistent with reversal as a payment for supplying
liquidity when it is scarce. Stock-specific returns do the opposite over the
whole period, but that comes from before 2009: since then calm and volatile days
differ by about 2.6 points a year, well inside the uncertainty.
The low-risk package barely depends on volatility, and the book as a whole earns
less in volatile markets, by an amount the history can't pin down.

## The two deepest drawdowns

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/theme-drawdowns" mobile="/assets/portfolio-attribution/theme-drawdowns_mobile" version="5" alt="Each theme's P&L over the 2008–09 and 2020–21 drawdowns." %}
</div>
<p class="figure-caption"><strong>Figure 2: The low-risk package and stock-specific returns drove both drawdowns.</strong> P&amp;L points before costs, from the book's peak to its trough: 30 July 2008–16 September 2009 and 13 February 2020–27 January 2021.</p>

The two deepest drawdowns, 13.8 points in 2008–09 and 14.8 in 2020–21 after
costs, look
alike by theme: the low-risk package lost 12.4 and 11.7, mostly through low
volatility, stock-specific returns lost 6.1 and 8.3, and short-term reversal
helped, by 5.1 and 2.5. They differ by leg. In 2008–09 the short book made 21
points into the March 2009 low and lost 35 in the rebound, 14.3 net, while the
longs made 1.3; in 2020–21 the loss was split evenly between the two.

The 2020–21 drawdown came in three steps. From February to early November 2020
the book lost 4.1 points, mostly low volatility through the crash and its
rebound. From the vaccine news on 9 November to the end of the year it lost
another 4.2 in seven weeks, as stock-specific returns, trading activity and
long-term return gave back about 4 points, while the net long's 2 points offset
low volatility's loss. In January 2021, the retail short squeeze, it lost
6.5 points in 17 sessions, to the trough on 27 January, with the package,
reversal and stock-specific returns all losing.

## What the regimes say

Market direction matters much less to the book than to its long and short
books. Low volatility and the net long dollars trade places in declines and
rallies, so the low-risk package earns its keep in the base regime and is a coin
flip in stress. What protected the book in declines has shifted from short-term
reversal and the package before 2009 to stock-specific returns since. Since
2009 the book's defence in declines has been stock selection the themes don't
explain, not the low-risk package.
