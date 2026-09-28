---
layout: post
interactive_charts: true
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

<link rel="stylesheet" href="/assets/css/attribution-article.css?v=4">

Averages over whole periods hide when the money is made and lost. For a book
that is long low-risk stocks and short high-risk ones, the market's direction
should matter a lot, so here I split [Part
1](/quants/portfolio-attribution.html)'s theme P&L by what the market was
doing. I use two separate views: the direction of whole market episodes, then
the size of daily market moves. A rally can be volatile, and a decline can
contain calm days; the two classifications overlap.

The book, [attribution groups](/quants/portfolio-attribution.html#factor-definitions) and [conventions](/quants/portfolio-attribution.html#pnl-conventions)
are those of Part 1. The backtest assumes shorts can always be borrowed, for
free.

<details markdown="1">
<summary>Short-sale assumptions in 2008</summary>

That assumption matters in 2008: the SEC's [temporary short-sale ban](https://www.sec.gov/newsroom/press-releases/2008-211-sec-halts-short-selling-financial-stocks-protect-investors-markets)
initially covered 799 financial companies from 19 September and
[expired on 8 October](https://www.nasdaqtrader.com/TraderNews.aspx?id=RA2008-036),
inside the 2007–08 decline.
Short positions in the financial sector made 9.3 of the short book's 32.3
points from October 2007 to October 2008; the long book lost about 34.
Of those 9.3 points, 2.5 came during the ban itself. During that period, the book also opened
38 new short positions in financials, 2.6% of capital; they made about half a
point. These sector-level returns assume unrestricted shorting; they do not
measure the gain available under the ban's security-specific restrictions.

</details>

## Declines and rallies describe market direction
{: #market-regimes }

I define the regimes from the Russell 1000 alone, so they don't depend on the
portfolio. A **decline** runs from a peak to the lowest close before the index
recovers 15%, when that low is more than 15% below the peak; there are 15 since 1999.
A **strong rally** is a stretch in which the index rose more than 13% over
63 sessions, with overlapping windows merged and decline days left out; there
are 16. These labels use later prices to identify the endpoints, so they
describe history rather than signals available at the time.

The remaining days are split into **volatility spikes only** (2% of all days)
and **base** (58%). A spike means trailing 21-session market volatility is
above its full-history 90th percentile. Declines take priority, then rallies,
then spikes; each day appears in only one row of Table 1. Base means none of
those three conditions, not necessarily a calm market.

<details markdown="1">
<summary>How I define the regimes</summary>

With the index level $$I_t$$, a decline starts at a local peak $$I_p$$ and ends
at the lowest close $$I_q$$ before the index rises 15% from that low, and counts
when $$I_q/I_p-1<-15\%$$; a new decline can only start after that recovery. A
strong rally is any 63-session window with $$I_{t+63}/I_t-1>13\%$$, overlapping
windows merged into one episode and decline sessions removed. A volatility spike
is a stretch where the index's trailing 21-session volatility, including that
day's return, is above its 90th percentile since 1999. This historical spike
label differs from the lagged volatility thirds in Table 2. A leg's return in a regime is its average daily P&L over
those sessions, times 252.

</details>

<div markdown="1">
<p class="table-caption"><strong>Table 1: Average book P&amp;L is positive in each group, lowest in declines and rallies.</strong> Average daily P&amp;L after costs × 252, as % of capital a year within each group, January 1999–May 2026. The rows partition all attributed days. “Book lost” counts episodes with negative summed net P&amp;L; rally and spike episodes include only their days remaining after the priority rules.</p>

| Regime | Episodes | Share of sessions | Book | Long book | Short book | Book lost |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Declines | 15 | 19% | +5.2 | −47.6 | +52.8 | 3 |
| Strong rallies | 16 | 21% | +6.4 | +45.3 | −38.9 | 5 |
| Spikes only | 12 | 2% | +12.3 | +74.0 | −61.7 | 5 |
| Base | | 58% | +10.3 | +17.7 | −7.4 | |
{: .research-table .comparison-table .compact-table .attribution-regimes }
</div>

The long and short books swing by about 40–50% a year in both regimes and mostly
cancel: the long book lost money in all 15 declines, the short book in 15 of
the 16 rallies. The book's average is positive in both, but it lost in 3 of
15 declines and 5 of 16 rallies. The episodes differ in length and share market
conditions, so these counts alone do not establish a stable probability of loss.

## The stock gap and the net long cancel

Each leg's P&L is its gross times the return of the stocks it holds, so with
long gross $$L$$, short gross $$S$$ and the two sets of stocks returning
$$g_L$$ and $$g_S$$, the book's P&L splits into the gap between the stocks and
the net long dollars, earning the longs' return. This net-long term uses
the held stocks' return; the attribution model's **net market exposure**
below uses the fitted market payoff, so their contributions differ:

$$
P \approx L g_L-S g_S=S\,(g_L-g_S)+(L-S)\,g_L .
$$

Before costs, in declines the shorted stocks fell much harder than the longs,
so the gap earned 21.5% a year, and the net long dollars lost 15.3%. In strong rallies the shorted stocks
rose faster: the gap lost 7.2% a year and the net long made 14.5%. The two terms
largely offset, leaving a smaller positive return in each regime. The theme
decomposition below shows where that remaining return comes from.

## The low-risk package mostly cancels in declines and rallies

<div class="research-figure responsive-figure">
  {% include blog-chart.html chart="regimes" source="/assets/portfolio-attribution/interactive-themes.json" base="/assets/portfolio-attribution/theme-regimes" mobile="/assets/portfolio-attribution/theme-regimes_mobile" version="6" label="Theme-group returns in declines and rallies, with the low-risk subtotal and its indented components." %}
</div>
<p class="figure-caption"><strong>Figure 1: The low-risk package combines offsetting contributions.</strong> Return in % of capital a year within each regime, January 1999–May 2026, before costs except for the whole book. The bold low-risk subtotal sums its three indented components: low volatility, beta and net market exposure. Explore reveals the other themes; trading activity combines turnover, volume surge and price-volume correlation.</p>

In declines, **low volatility** earns 18% a year and made money in all 15
episodes, while **net market exposure** loses 19% and lost in all 15. In strong
rallies the two swap: low volatility loses 13% a year and net market exposure
earns 15%. Adding beta gives the [low-risk package](/quants/portfolio-attribution.html#factor-definitions):
roughly flat in declines and +0.7% a year in strong rallies. These small averages hide
variation between episodes: the package made money
in only 4 of the 15 declines and 8 of the 16 rallies, and its average in
declines rests on the 2000–01 bear market. Neither line times the market: the
net long sits at its limit, and exposure timing adds or subtracts less than a
point a year.

What kept the book positive has changed. In the declines up to 2008, short-term
reversal made 10.4 points and the low-risk package 8.7. In the nine declines
since 2009, the package lost 8.9 points and reversal made less than one; the
book's 18.9 points coincided with 18.6 points in the stock-specific remainder.
That remainder still has market exposure: its estimated beta of −0.035 to the
model's market payoff since 2009 accounts for about 7.3 of those decline points. The 2011 decline alone
contributed 8.6 points. These are reasons to avoid interpreting the whole line
as stock-selection skill. In the
rallies since 2009, reversal and short interest made 12 and 8 points.

## Reversal earns more on volatile days

Now I classify individual days by **market volatility**, regardless of whether
they fall in a decline, rally or base period. I take the standard deviation of
the Russell 1000's returns over the previous 21 trading sessions and annualize
it. Calm days are the lowest third, below about 11.1%; volatile days are the
highest third, above about 17.4%. The middle third is omitted from Table 2.
“Difference” means volatile minus calm.

This measures the size of market moves, not their direction or the volatility
of the stocks held. A sharp rebound can be both a strong rally in Table 1 and
volatile in Table 2. The daily measure uses information available before the
day's return, but the cutoffs use the full history. The comparison therefore
describes the sample; it is not a tested rule for changing the portfolio.

<div markdown="1">
<p class="table-caption"><strong>Table 2: Reversal earns more on volatile days; the stock-specific remainder earns less.</strong> % of capital a year, before costs except for the book, January 1999–May 2026. Calm and volatile are the lowest and highest thirds of days by the index's volatility over the previous 21 sessions, below 11% and above 17% a year. The t-statistic of the difference allows for autocorrelation up to 21 sessions, retaining calendar gaps between selected days.</p>

| | Calm | Volatile | Difference | t |
| :--- | ---: | ---: | ---: | ---: |
| Short-term return | +1.4 | +4.4 | +3.0 | 3.9 |
| Stock-specific | +3.7 | −1.6 | −5.3 | −2.4 |
| Short interest | +0.6 | +1.8 | +1.2 | 1.7 |
| Long-term return | +0.7 | −0.2 | −1.0 | −1.0 |
| Low-risk package | +2.9 | +2.3 | −0.7 | −0.3 |
| Book, after costs | +8.4 | +5.1 | −3.3 | −1.0 |
{: .research-table .comparison-table .compact-table }
</div>

Short-term reversal earns more on volatile days both before and after 2009,
which is consistent with reversal as a payment for supplying
liquidity when it is scarce. Stock-specific returns do the opposite over the
whole period, but that comes from before 2009: since then calm and volatile days
differ by about 2.6 points a year, well inside the uncertainty.
The low-risk package's average differs little between the two states, but the
uncertainty is wide. The book as a whole earns less in volatile markets, by an
amount the history can't pin down.

## The two deepest drawdowns

<div class="research-figure responsive-figure">
  {% include blog-chart.html chart="drawdowns" source="/assets/portfolio-attribution/interactive-themes.json" base="/assets/portfolio-attribution/theme-drawdowns" mobile="/assets/portfolio-attribution/theme-drawdowns_mobile" version="6" label="Theme-group P&L over the 2008–09 and 2020–21 drawdowns." %}
</div>
<p class="figure-caption"><strong>Figure 2: The low-risk package and stock-specific returns drove both drawdowns.</strong> P&amp;L points before costs, from the book's peak to its trough: 30 July 2008–16 September 2009 and 13 February 2020–27 January 2021. Explore reveals the low-risk package's three components.</p>

The two deepest drawdowns, 13.8 points in 2008–09 and 14.8 in 2020–21 after
costs, look alike by theme: the low-risk package lost 12.4 and 11.7, mostly through low
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
books. Within the low-risk package, low volatility and the net long dollars
largely trade places, with beta completing the subtotal. Its gains concentrate
in the base regime; it was positive in only 4 of 15 declines and 8 of 16 strong
rallies. The small regime averages do not make it reliable protection in stress.

Since 2009, the positive contribution in declines appears mostly in the
stock-specific remainder. Its negative market exposure and concentration in
2011 make that a weaker conclusion than saying stock selection protected the
book. The model locates the gains, but does not fully identify what earned them.
