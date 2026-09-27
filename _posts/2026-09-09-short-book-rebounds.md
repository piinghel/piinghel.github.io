---
layout: post
title: "Performance Attribution, Part 2: When the Strategy Loses"
description: "The portfolio's P&L by theme in market declines and strong rallies: the defensive tilt pays on the way down and gives it back when the market surges."
permalink: /quants/short-book-rebounds.html
toc: true
date: 2026-09-09
last_modified_at: 2026-09-28
categories: ["Risk & attribution"]
article_label: Performance attribution · Part 2 of 2
series_id: performance-attribution
series_order: 2
---

[Part 1](/quants/portfolio-attribution.html) asked what the portfolio is paid
for over the whole history. Averages hide when the money is made and lost, and
for a book that is long calm stocks and short volatile ones, the market's
direction should matter a lot. So here I split the same theme P&L by what the
market was doing: falling hard, rallying hard, or neither.

The book, themes and [conventions](/quants/portfolio-attribution.html#pnl-conventions)
are those of Part 1. Missing borrow costs flatter the short book most in
crashes and squeezes, and the backtest ignores the SEC's ban on shorting about
800 financial stocks from 19 September to 8 October 2008.

## Market regimes

I define the regimes from the Russell 1000 alone, so they don't depend on the
portfolio. A **decline** runs from a peak to a low at least 15% below it, ending
once the index has recovered 15% from that low; there are 15 since 1999. A
**strong rally** is a stretch in which the index rose more than 13% over 63
sessions, with overlapping windows merged and decline days left out; there are
16. Everything else is the base.[^regimes]

<div markdown="1">
<p class="table-caption"><strong>Table 1: The book earns in every regime, least in rallies and declines.</strong> % of capital a year within each regime, January 1999–May 2026. The book is after costs, the long and short books before; the remaining 2% of sessions are volatility spikes outside declines.</p>

| Regime | Episodes | Share of sessions | Book, net | Long book | Short book |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Declines | 15 | 18% | +5.6 | −46.6 | +52.2 |
| Strong rallies | 16 | 21% | +6.4 | +45.3 | −38.9 |
| Base | | 58% | +10.2 | +17.8 | −7.6 |
{: .research-table .comparison-table .compact-table }
</div>

The long and short books swing hard in both regimes and mostly cancel: in
declines the shorts made money in all 15 episodes, and in strong rallies they
lost in 15 of 16. The book as a whole stays positive in both, just less so
than in quieter markets.

## Which themes win and lose

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/theme-regimes" mobile="/assets/portfolio-attribution/theme-regimes_mobile" version="3" alt="Each theme's return in market declines and in strong rallies." %}
</div>
<p class="figure-caption"><strong>Figure 1: Low volatility and the net long dollars trade places.</strong> Return in % of capital a year within each regime, before costs except for the whole book. Declines include every decline session; strong rallies exclude decline days.</p>

The mechanism is the defensive tilt. In declines, **low volatility** earns 16%
a year and loses money in only one of 15 episodes, while the net long dollars
lose 20%. In strong rallies the two swap: low volatility loses 9.2% a year
and **size** 7.6%, and the net long dollars earn 18%. **Trend** loses in both.
Short interest, momentum and loss frequency barely notice the regime.

So the rally losses aren't a few bad shorts. The shorts are the high-beta,
high-volatility stocks the ranking dislikes, and those are exactly the stocks
that rally hardest. The loss is the defensive tilt paying out in reverse, and
the net long position the beta limit forces on the book is what keeps the
total positive.

## The two deepest drawdowns

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/theme-drawdowns" mobile="/assets/portfolio-attribution/theme-drawdowns_mobile" version="3" alt="Each theme's P&L over the 2008–09 and 2020–21 drawdowns." %}
</div>
<p class="figure-caption"><strong>Figure 2: Different themes behind each drawdown.</strong> P&amp;L points before costs, from the book's peak to its trough: 30 July 2008–16 September 2009 and 13 February 2020–27 January 2021.</p>

The two deepest drawdowns, 13.8 points in 2008–09 and 14.8 in 2020–21, had
different causes. In 2008–09 it was size and short-term reversal, and the
short book lost 14.6 points while the longs broke even. In 2020–21 it was low
volatility, down 15.1 points, and trend, down 7.7, with the losses split evenly
between the two books.

I also tested three portfolio responses on an earlier version of this book,
each at the same risk: limiting the low-volatility tilt, limiting beta
exposure, and shrinking the book when its volatility rises. Moderate tilt
limits did a little better in declines and most strong rallies, but barely
changed the late-2020 loss. Beta limits mostly added market beta, and
volatility scaling only helped by holding a smaller book, while deepening
2008–09.

## What the losses say

The book loses in strong rallies because of what the ranking bets on, not
because of a few positions: low volatility, which earns 16% a year in
declines, gives much of it back when the market surges. That trade-off was
worth it while the tilt paid over the cycle. [Part 1](/quants/portfolio-attribution.html#how-it-changed)
shows it has carried close to half the risk for no return since 2022, so the
case for keeping it at its current size has weakened, and the place to change
it is the ranking's theme weights rather than the portfolio's limits.

## References

Kent Daniel and Tobias Moskowitz, [*Momentum Crashes*](https://www.kentdaniel.net/papers/published/jfe_16.pdf),
*Journal of Financial Economics*, 2016.

[^regimes]: Volatility spikes, when the index's 21-session volatility is above its 90th percentile, are the book's weakest days at 0.9% a year, and most of them fall inside declines.
