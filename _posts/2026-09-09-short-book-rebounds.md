---
layout: post
title: "Performance Attribution, Part 2: When the Portfolio Loses"
description: "The portfolio's P&L by theme in market declines and strong rallies: low volatility and the net long dollars trade places, and the book earns in both."
permalink: /quants/short-book-rebounds.html
toc: true
date: 2026-09-09
last_modified_at: 2026-09-27
categories: ["Risk & attribution"]
article_label: Performance attribution · Part 2 of 2
series_id: performance-attribution
series_order: 2
---

Averages over whole periods hide when the money is made and lost. For a book
that is long low-volatility stocks and short high-volatility ones, the market's
direction should matter a lot, so here I split [Part
1](/quants/portfolio-attribution.html)'s theme P&L by what the market was
doing: falling hard, rallying hard, or neither.

The book, themes and [conventions](/quants/portfolio-attribution.html#pnl-conventions)
are those of Part 1. Missing borrow costs flatter the short book most in
crashes and squeezes, and the backtest ignores the SEC's ban on shorting about
800 financial stocks from 19 September to 8 October 2008.

## Market regimes

I define the regimes from the Russell 1000 alone, so they don't depend on the
portfolio. A **decline** runs from a peak to the lowest close before the index
recovers 15%, when that low is at least 15% below the peak; there are 15 since
1999. A **strong rally** is a stretch in which the index rose more than 13% over
63 sessions, with overlapping windows merged and decline days left out; there
are 16. The rest is the base, apart from 2% of sessions in volatility spikes,
which I leave out.

<div markdown="1">
<p class="table-caption"><strong>Table 1: The book earns in every regime, least in declines and rallies.</strong> % of capital a year within each regime, after costs, January 1999–May 2026.</p>

| Regime | Episodes | Share of sessions | Book | Long book | Short book |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Declines | 15 | 19% | +5.6 | −46.6 | +52.2 |
| Strong rallies | 16 | 21% | +6.4 | +45.3 | −38.9 |
| Base | | 58% | +10.2 | +17.8 | −7.6 |
{: .research-table .comparison-table .compact-table }
</div>

The long and short books swing by 40–50% a year in both regimes and mostly
cancel: in declines the shorts made money in all 15 episodes, and in strong
rallies they lost in 15 of 16. The book stays positive in both, just less so
than in quieter markets, and lost money in 3 of the declines and 5 of the
rallies.

## Low volatility and net market exposure trade places

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/theme-regimes" mobile="/assets/portfolio-attribution/theme-regimes_mobile" version="4" alt="Each theme's return in market declines and in strong rallies." %}
</div>
<p class="figure-caption"><strong>Figure 1: Low volatility and net market exposure trade places.</strong> Return in % of capital a year within each regime, before costs except for the whole book.</p>

In declines, **low volatility** earns 16% a year and loses money in only one of
15 episodes, while **net market exposure** loses 20%. In strong rallies the two
swap: low volatility loses 9.2% a year and **size** 7.6%, and net market
exposure earns 18%. The shorts are the high-beta, high-volatility stocks the
ranking dislikes, which rally hardest, and the net long dollars the beta limit
adds are what keep the book positive. **Trend** loses in both regimes; short
interest, momentum and loss frequency change little.

## The two deepest drawdowns

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/theme-drawdowns" mobile="/assets/portfolio-attribution/theme-drawdowns_mobile" version="4" alt="Each theme's P&L over the 2008–09 and 2020–21 drawdowns." %}
</div>
<p class="figure-caption"><strong>Figure 2: Size and reversal drove 2008–09; low volatility and trend drove 2020–21.</strong> P&amp;L points before costs, from the book's peak to its trough: 30 July 2008–16 September 2009 and 13 February 2020–27 January 2021.</p>

The two deepest drawdowns, 13.8 points in 2008–09 and 14.8 in 2020–21, had
different causes. In 2008–09 it was size and short-term reversal, down 10.0 and
8.4 points; before costs the short book lost 14.3 points while the longs made
1.3. In 2020–21 it was low volatility, down 15.1, and trend, down 7.7, with the
loss split evenly between the long and short books. Both ran through the
rebound after a crash: the rally from February to October 2009 cost the book
7.1 points and the one from September 2020 to February 2021 cost 4.4.

## What the regimes say

Market direction matters much less to the book than to its long and short
books. Low volatility earns 16% a year in declines and loses 9% in strong
rallies, but net market exposure swings the other way, so the book earns 5.6%
and 6.4% a year in the two regimes against 10.2% in the base. That regime
profile is the price of the defensive package, and it was worth paying while
the package earned 3–8% a year. Since 2022 the package has earned about nothing
on 44% of the risk ([Part 1](/quants/portfolio-attribution.html#how-it-changed)),
so the ranking's weight on low volatility is the first thing I would reduce.
