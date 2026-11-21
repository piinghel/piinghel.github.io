---
published: true
layout: post
interactive_charts: true
toc: true
title: "Reducing Rebalancing Luck"
description: "Staggering three Ridge portfolios lowers realized volatility and narrows the spread of returns across rebalance calendars."
date: 2026-09-05
last_modified_at: 2026-11-21
categories: ["Portfolio construction"]
article_label: Portfolio construction · Rebalancing
permalink: /quants/rebalancing-luck.html
home_after: _posts/2026-08-29-joint-sizing.md
github_repositories:
  - label: Research code
    url: https://github.com/piinghel/rebalance-tranching
---

<link rel="stylesheet" href="{{ '/assets/css/rebalancing-luck.css' | relative_url }}?v=2">

Rebalance every three weeks and you still have to choose which week to start.
Suppose I use Friday signals. I can start this Friday, next Friday, or the
Friday after. Each schedule uses the same Ridge model and sizing rules, yet
the choice can make a sizeable difference to the backtest.

I wanted to see what happens if I put a third of the notional on each
schedule. The three books get new targets in different weeks, so there are
two ways this might help. Their daily returns can partly offset each other,
and the result can depend less on which dates I happen to pick.

I use the saved walk-forward predictions from the Ridge model, with September
1998–December 2021 and January 2022–May 2026 shown separately. Both periods
come from the existing research backtest. The sizing rules come from
[From Volatility Scaling to Joint Sizing]({% link _posts/2026-08-29-joint-sizing.md %}).

## The starting week
{: #the-starting-week-matters }

Figure 1 shows what that choice meant for Friday signals from January 2022
to May 2026. The weakest starting week earned **5.73%** a year after costs
and the strongest earned **8.95%**. The three together earned **7.70%**.
Had I picked the weakest week, the entire portfolio would have followed that
path. In the blend, it accounts for a third of each day's P&L.

<figure class="research-figure rebalancing-figure responsive-figure">
  {% include blog-chart.html chart="schedules" source="/assets/rebalancing-luck/ridge-paths.json?v=4" base="/assets/rebalancing-luck/ridge-paths" mobile="/assets/rebalancing-luck/ridge-paths_mobile" label="The three Friday starting weeks finish at different levels. The equal-notional blend ends between the strongest and weakest schedules." version="3" %}
  <figcaption class="figure-caption"><strong>Figure 1. The three Friday starting weeks diverged.</strong> Growth compounds daily net P&amp;L per unit of fixed notional from 100 at the 31 December 2021 close through May 2026. The vertical scale is logarithmic.</figcaption>
</figure>

All three schedules use the same 80 ranking predictors, rank buffer and trade
penalty. The backtest fills orders at the next session's close and charges
5 bp per dollar traded. It uses the same 7% forecast risk budget as the
joint-sizing article, with a lower volatility forecast for the same holdings
that allows larger positions.

## Three staggered books
{: #split-the-portfolio-across-three-weeks }

I split the notional into three books. In week 1, the first book gets a new
target and the other two carry their positions. In week 2, the second book
gets its turn. By week 4, the first book is due again. The portfolio has a
rebalance scheduled each week, while each book keeps its three-week cycle.

<figure class="sleeve-figure">
  <table class="sleeve-schedule" aria-label="Two cycles of the staggered rebalance schedule">
    <colgroup span="1"></colgroup><colgroup span="3"></colgroup><colgroup span="3"></colgroup>
    <thead>
      <tr><td></td><th scope="colgroup" colspan="3">First cycle</th><th scope="colgroup" colspan="3">Second cycle</th></tr>
      <tr><th scope="col">Book</th>{% for week in (1..6) %}<th scope="col" aria-label="Week {{ week }}">W{{ week }}</th>{% endfor %}</tr>
    </thead>
    <tbody>
      {% for book in (1..3) %}
      {% assign repeat = book | plus: 3 %}
      <tr>
        <th scope="row">{{ book }} <small>⅓ notional</small></th>
        {% for week in (1..6) %}
        {% if week == book or week == repeat %}
        <td><span class="sleeve-trade" role="img" aria-label="Rebalance">↻</span></td>
        {% else %}
        <td><span class="sleeve-hold" role="img" aria-label="Carry positions">—</span></td>
        {% endif %}
        {% endfor %}
      </tr>
      {% endfor %}
    </tbody>
  </table>
  <figcaption class="figure-caption"><strong>Figure 2. One book rebalances each week.</strong> Shaded cells mark scheduled rebalances. Holidays can move the actual signal and fill dates.</figcaption>
</figure>

The backtest scales each standalone book's executed positions and trades to a
third of their original size. If $$r_{j,t}$$ is the daily net P&L of book
$$j$$ per unit of its fixed notional, the blend earns

$$
r_{\mathrm{combined},t}=\frac{r_{1,t}+r_{2,t}+r_{3,t}}{3}.
$$

The blend earns exactly the average daily net return of its three books.
With the average return fixed, I can focus on how much volatility the
three books take out when I hold them together.

## Lower volatility
{: #staggering-the-books-lowers-volatility }

The three books share many holdings. When their positions differ, a bad day
for one book can be milder for another. The less closely they move together,
the more volatility the blend removes. For three books with the same
volatility $$\sigma$$ and pairwise correlation $$\rho$$, the equal-weight
blend has volatility

$$
\sigma_{\mathrm{combined}}=\sigma\sqrt{\frac{1+2\rho}{3}}.
$$

I repeat the Friday comparison for all five weekdays. For every weekday
in both periods, the blend had lower volatility than any of its
three standalone books. Average volatility fell from **8.75% to 8.15%**
in development and from **9.65% to 9.26%** later. The books moved more
closely together in the later sample. Their average correlation rose
from 0.80 to 0.88. With similar standalone volatilities, the formula gives
reductions of about 7% and 4%, close to what I find.

I calculate each blend's Sharpe from its combined daily returns. In the
later period, the average went from **0.81 to 0.84**. The same arithmetic
return came with a little less volatility, and the compounded return was
slightly higher. The drawdown changed very little.

<table class="research-table comparison-table risk-performance-table">
  <caption><strong>Table 1. Lower volatility at the same notional.</strong> Mean statistics across 15 standalone schedules and five weekday blends. Return is annualized and compounded. Return, volatility and drawdown are percentages. Sharpe uses the daily mean and sample standard deviation, 252 sessions per year and a zero cash rate.</caption>
  <thead><tr><th>Metric</th><th>Single<br>schedule</th><th>Three<br>tranches</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="3">September 1998–December 2021</th></tr>
    <tr><th scope="row">Net return</th><td>11.67</td><td>11.73</td></tr>
    <tr><th scope="row">Volatility</th><td>8.75</td><td>8.15</td></tr>
    <tr><th scope="row">Sharpe</th><td>1.30</td><td>1.40</td></tr>
    <tr><th scope="row">Max drawdown</th><td>−18.48</td><td>−17.50</td></tr>
    <tr class="period-heading"><th colspan="3">January 2022–May 2026</th></tr>
    <tr><th scope="row">Net return</th><td>7.62</td><td>7.66</td></tr>
    <tr><th scope="row">Volatility</th><td>9.65</td><td>9.26</td></tr>
    <tr><th scope="row">Sharpe</th><td>0.81</td><td>0.84</td></tr>
    <tr><th scope="row">Max drawdown</th><td>−9.85</td><td>−9.64</td></tr>
  </tbody>
</table>

## Less calendar dispersion
{: #staggering-narrows-the-spread-across-calendars }

The other question is how much the annualized return changes when I pick
a different calendar. With a single book I have 15 choices, one for each
weekday and starting-week combination. With three books I use all the
starting weeks and have five choices left, one per weekday. I measure the
spread by taking the standard deviation of the annualized returns across
the choices in each case.

I included the middle option too. Two books still leave a choice of which
starting week to skip. In the later sample, dispersion fell from **1.11**
percentage points with one book to **0.62** with two and **0.31** with
three. The fall was smaller in development, from **0.75 to 0.50** points.
That was still more weekday sensitivity than the quietest single starting
week in development, at **0.34** points.

Figure 3 shows where those returns landed. In the later period, the fifteen
single schedules ranged from **5.65% to 9.42%** a year. The five blends
ranged from **7.13% to 8.08%**. Holding all three starting weeks lifted the
weakest outcome and gave up the strongest. Picking the weekday still matters.

<figure class="research-figure rebalancing-figure responsive-figure">
  {% include blog-chart.html chart="calendars" source="/assets/rebalancing-luck/ridge-calendars.json?v=7" base="/assets/rebalancing-luck/ridge-calendars" mobile="/assets/rebalancing-luck/ridge-calendars_mobile" label="Annualized net returns for 15 single schedules, 15 pairs and five three-book blends in each period. After 2021, the range narrows from 5.65–9.42% for one book to 7.13–8.08% for three." version="7" %}
  <figcaption class="figure-caption"><strong>Figure 3. Returns cluster more tightly with three books.</strong> Each dot is one of 15 single schedules, 15 same-weekday pairs or five three-book blends. The lines mark each group's range. Both panels use the same return scale.</figcaption>
</figure>

## Week and weekday
{: #the-week-and-weekday-interact }

I expected the starting week to matter more than the weekday. Then I
looked at the third starting week after 2021. It was the best of the three
with Monday signals at **8.80%** a year, and the weakest with Friday
signals at **5.73%**. Averaging over weekdays makes the starting-week
differences look small because those differences can reverse.

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 2. Where the calendar differences show up.</strong> Share of squared deviations in compounded annual net returns across the 15 standalone calendars. Each main effect averages over the other calendar choice. The interaction measures how the week effect varies by weekday.</caption>
  <thead><tr><th>Component</th><th>1998–2021</th><th>2022–May 2026</th></tr></thead>
  <tbody>
    <tr><th scope="row">Weekday</th><td>45.2</td><td>7.7</td></tr>
    <tr><th scope="row">Starting week</th><td>23.1</td><td>0.2</td></tr>
    <tr><th scope="row">Week × weekday</th><td>31.7</td><td>92.0</td></tr>
  </tbody>
</table>

That interaction accounts for about **92%** of the squared differences
from the average calendar return after 2021. The starting week mattered quite
a bit for Friday even though it explained little on average.

## The historical spread
{: #putting-the-spread-in-context }

A calendar that wins in a backtest might have a persistent advantage.
Before preferring it, though, I want to know how unusual the full spread
across the fifteen standalone calendars is.

I give the 15 calendars the same mean daily return, then resample blocks
of 63 sessions. Every calendar gets the same blocks, so the returns
still move together within each sampled block. For each of 2,000 draws,
I measure the distance from the lowest to the highest compounded annual
return.

In development, **48%** of the draws produced a range at least as wide
as the observed **2.65 points**. Later, **87%** matched or exceeded the
observed **3.77 points**. Across block lengths of 21, 63 and 126 sessions,
the frequencies were 45–55% and 87–90%, respectively. A gap this wide
is common in these simulations even when every schedule has the same
mean daily return. The size of the gap alone gives me little reason to
back the historical winner.

## Smaller trades, more orders
{: #smaller-trades-more-rebalance-cycles }

The average order count rose from **2,429 to 7,288 a year** after 2021.
Each book's order sizes were scaled to a third, so the total amount
traded stayed the same on average. Two-way turnover, the value of purchases
plus sales divided by portfolio notional, was **18.83 times notional
a year** in both cases. At 5 bp per dollar traded, that works out to
**0.94 percentage points a year** in either case and **1.29 points** in
development.

Smaller orders spread demand for liquidity across dates and may reduce
market impact. More orders and rebalance cycles can also add ticket
charges and operational work. Which matters more depends on order size
relative to available liquidity and how the orders are worked. The
backtest prices traded notional at a flat rate. Market impact, fixed
charges, borrow and financing sit outside that calculation. A study by
Zarattini and Pagani models how these execution trade-offs vary with account
size.

## Weekly thirds
{: #combining-starting-weeks-is-the-better-default }

What I like about weekly thirds is that I can keep the three-week cycle and
take the starting-week decision off the table. In this replay, the
portfolio moved a little less day to day and the annual return depended
less on the calendar. The later Sharpe gain was small enough that the way
I price and work the extra orders could matter more than the backtest gain.

## References

- Corey Hoffstein, Justin Sibears and Nathan Faber, *Rebalancing Timing Luck: The Difference between Hired and Fired*, summarized in [Newfound Research's rebalance timing luck overview](https://www.thinknewfound.com/rebalance-timing-luck).
- Carlo Zarattini and Alberto Pagani, [*The Tranching Dilemma: A Cost-Aware Approach to Mitigate Rebalance Timing Luck in Factor Portfolios*](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf), 14 November 2025 version, PDF pp. 9–14.
