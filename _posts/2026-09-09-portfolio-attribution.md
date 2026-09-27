---
layout: post
title: "Performance Attribution, Part 1: What the Strategy Is Paid For"
description: "Which of the ranking's themes earn their share of the portfolio's risk, and how that has changed since 1999."
permalink: /quants/portfolio-attribution.html
toc: true
date: 2026-09-09
last_modified_at: 2026-09-28
categories: ["Risk & attribution"]
article_label: Performance attribution · Part 1 of 2
series_id: performance-attribution
series_order: 1
github_repositories:
  - label: Dashboard source code
    url: https://github.com/piinghel/portfolio-pnl-dashboard
---

The portfolio from my [optimizer
article](/quants/2026/08/29/portfolio-optimization.html) earned about 8.8% a
year after costs at 6.6% volatility from September 1998 to May 2026. A return
chart says how much it made. It doesn't say what for.

The ranking behind it combines predictors from several themes: short interest,
momentum, trend, short-term reversal, low volatility, size and more, as in the
[multiple-predictors article](/quants/2025/02/09/multiple-linear-regression.html).
So the question I want to answer is which of those themes the portfolio is
actually paid for, which take risk without paying for it, and whether that has
changed.

The book is the 80-predictor Ridge ranking run through the optimizer, with its
volatility target recalibrated, combining three rebalance schedules at equal
notional.

<div id="pnl-conventions" markdown="1">
One **P&L point** is 1% of strategy notional, which stays fixed throughout.
Trading costs are 5 basis points per dollar traded, excluding borrow, financing
and market impact. Returns by theme are before costs; the book's costs were
about 1.1 points a year.
</div>

## The book

The longs made **372 points**, the shorts lost **101** and trading costs took
**30**, leaving **242 points** net. Because the longs hold lower-beta stocks
than the shorts, keeping forecast beta near zero leaves the book about 24% net
long in dollars. The shorts lose money over the history even though they made
money in every market decline.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/whole-history" mobile="/assets/portfolio-attribution/whole-history_mobile" version="6" alt="Cumulative long, short and net P&L above the portfolio drawdown, September 1998–May 2026." %}
</div>
<p class="figure-caption"><strong>Figure 1: The longs carried the accumulated result.</strong> Cumulative P&amp;L and drawdown. Shading marks the two deepest drawdowns, February 2020–January 2021 and July 2008–September 2009.</p>

## Attributing P&L to the ranking's themes
{: #follow-exposure-and-payoff-together }

Each day I regress stock returns on the previous day's theme characteristics
and industry indicators, weighting larger stocks more. The coefficients are the
day's payoffs: what one unit of each characteristic earned, holding the others
fixed. The book's exposure to a theme is its signed weights times the stocks'
characteristics, and exposure times payoff is that theme's P&L for the day.
What the themes don't explain is stock-specific.[^model]

<div markdown="1">
<p class="table-caption"><strong>Table 1: The themes.</strong> Each theme groups the characteristics behind related predictors in the ranking.</p>

| Theme | What it measures |
| :--- | :--- |
| Short interest | Short interest relative to volume, and its changes |
| Momentum | Returns and risk-adjusted returns over one to twelve months |
| Trend | Price relative to moving averages, and how long it has stayed above them |
| Short-term reversal | Returns over the last one to 21 sessions |
| Price position | Price relative to recent highs and lows |
| Loss frequency | The share of losing days over windows up to three years |
| Liquidity &amp; volume | Turnover, illiquidity and the behaviour of trading volume |
| Low volatility | Stock volatility |
| Size | Market capitalization, its variability and its change |
| Beta &amp; market correlation | Market beta and correlation with the index |
| Net market exposure | Net dollars times the market's move |
| Sector tilt | Industry exposure beyond the net dollars |
{: .research-table .comparison-table .compact-table }
</div>

To allocate risk, I measure how each theme's daily P&L moves with the whole
book: a theme's **share of risk** is the covariance of its daily P&L with the
book's, divided by the book's variance. The shares add to 100%, and a theme
that offsets the rest of the book gets a negative share.

## Where the return comes from

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/theme-pnl" mobile="/assets/portfolio-attribution/theme-pnl_mobile" version="1" alt="Return and share of risk of each theme, 1999–May 2026." %}
</div>
<p class="figure-caption"><strong>Figure 2: Short interest pays most for its risk; trend and size cost money.</strong> Return before costs, in % of capital a year, and share of the book's daily variance, January 1999–May 2026.</p>

The steadiest earner is **short interest**: 2.2% a year for 9% of the risk,
and positive in every five-year block. **Net market exposure** earns more, 3.2%
a year, but that is the market's return on the net long dollars the beta limit
forces on the book. Low volatility adds 1.6%, stock-specific returns 1.4%, and
price position, reversal, loss frequency, liquidity and momentum 0.7–1.4%
each.

Two themes cost money over the whole history. **Trend** lost 2.1% a year and
**size** 1.9%, and size did it while carrying 18% of the book's risk, more than
any other theme. That is risk the book is not paid for.

## How it changed
{: #how-it-changed }

The full-history bars average over very different periods. Figures 3 and 4
show each theme year by year, with the five-year average as a line.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/theme-return-years" mobile="/assets/portfolio-attribution/theme-return-years_mobile" version="1" alt="Each theme's return per year, 1999–2026, with five-year averages." %}
</div>
<p class="figure-caption"><strong>Figure 3: Short interest paid in every period; trend rarely did.</strong> Return before costs, % of capital a year, per calendar year; lines are the five-year averages. 2026 is January–May, annualized. Bars beyond ±10 are clipped and marked.</p>

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/theme-risk-years" mobile="/assets/portfolio-attribution/theme-risk-years_mobile" version="1" alt="Each theme's share of the book's risk per year, 1999–2026, with five-year averages." %}
</div>
<p class="figure-caption"><strong>Figure 4: Low volatility and size took over the risk after 2019.</strong> Share of the book's daily variance, %, per calendar year; lines are the five-year averages. Bars beyond ±40 are clipped and marked.</p>

Low volatility, size, liquidity and the net long dollars move together, so I
also read them as one defensive package. It took 26–42% of the book's risk in
each block to 2018, 49% in 2019–21 and 44% since 2022. Its return went the
other way: positive in every block to 2021, about zero since 2022, with low
volatility alone losing 3.3% a year on 30% of the risk.

Stock-specific returns faded too, from 1.2–2.6% a year in every block to 2018
to slightly negative since. What held up is short interest, and momentum and
loss frequency had their best block since 2022, at about 2.2% a year each.

## What I'd change

The book is paid mainly for short interest, a handful of smaller signal themes
and stock selection. It pays for two things: trend and size, which have lost
money for most of 27 years, and a defensive tilt that earned its keep until
2021 and now carries close to half the risk for nothing. Limits on the
portfolio don't fix either. The lever is the ranking's mix of themes: less
weight on trend and size, and a defensive tilt sized for what it earns now.
[Part 2](/quants/short-book-rebounds.html) looks at when the book loses, and
which themes are behind it.

## References

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
2021, Chapters 3–4 and 7–8.

The [dashboard source code](https://github.com/piinghel/portfolio-pnl-dashboard)
is available to explore your own portfolio.

[^model]: Weighted by the square root of market capitalization, with 20 industries; about 1% of gross exposure lacks theme data and is shown separately.
