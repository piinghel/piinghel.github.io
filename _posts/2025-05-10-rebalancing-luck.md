---
layout: post
title: "Combining Rebalance Weeks Reduces Timing Risk"
description: "Three tranches preserve average return while reducing dependence on the rebalance calendar. A comparison of fifteen calendars."
date: 2025-05-10
last_modified_at: 2026-09-06
categories: ["Rebalancing"]
article_label: Portfolio construction · Rebalancing
permalink: /quants/2025/05/10/rebalancing-luck.html
series_previous: /quants/2026/09/05/risk-concentration.html
series_end: true
github_repositories:
  - label: Research code
    url: https://github.com/piinghel/rebalance-tranching
---

<p class="article-summary">I split the strategy into three equal parts, called tranches, each with its own rebalance schedule. Across September 1998–May 2026, combining them leaves average annualized return almost unchanged: 11.37% becomes 11.43%. Average portfolio volatility falls from 8.53% to 7.88%, while the return spread across calendars narrows from 2.06 to 0.40 percentage points.</p>

## The starting-week problem

“Rebalance every three weeks” sounds like a complete rule. It still leaves me
with a choice of three starting weeks. Each one sees a different sequence of
signals and prices, even though I use the same forecasting and allocation
rules. Across all fifteen combinations of starting week and weekday, annualized
net return ranges from **10.21% to 12.27%** over September 1998–May 2026:
a **2.06 percentage-point spread** with the strategy unchanged. Choosing the
best calendar after seeing the results would just give me another way to fit
the backtest.

I use the [same stock strategy](/quants/2026/08/29/portfolio-optimization.html)
throughout: the forecasts, point-in-time universe, selection and sizing rules,
and gross exposure cap stay fixed. Friday refers to the signal date; execution
is at the next trading-session close. All returns include the existing 5 bp
allowance for transaction costs and market impact. The calendar grid and
return–volatility comparison cover the full matched history. I also split the
tables into development (September
1998–December 2021) and later history (January 2022–May 2026), so the much longer
development period cannot hide a change in the more recent results. The later
period has already informed research choices; it is not an untouched test.

The original three Friday calendars have a fairly modest full-history spread
of 0.67 percentage points. Their combined return is 11.67%, close to the 11.61%
average across all three calendars. The larger 2.06-point range above includes
the weekday choice as well.

Figure 1 uses January 2022–May 2026 to make the more recent divergence easier to
see. Over that period, the three Friday calendars return **5.42% to 9.91%**,
a **4.49-point spread**. The shaded band joins the best and worst fixed
calendars, with the three-tranche portfolio in blue. Its 8.02% return is close
to the 7.99% average across all three Friday calendars. This is a larger calendar effect than over the full
history; tranching does not capture that entire best-to-worst gap as extra return.

<div class="research-figure rebalancing-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/tranching/schedule-performance" mobile="/assets/tranching/schedule-performance_mobile" version="6" alt="January 2022–May 2026 Friday calendars: shaded band between fixed Week 2 and Week 3 paths, returning 9.91% and 5.42% annually. The three-tranche portfolio returns 8.02%." %}
</div>

<p class="figure-caption"><strong>Figure 1: A larger divergence in the later period.</strong> 3 January 2022–27 May 2026. Shading joins the fixed Friday calendars with the highest and lowest returns over this period; these need not be the highest and lowest paths at every date. The blue portfolio combines all three offsets. The index compounds daily net P&amp;L per unit of fixed notional; endpoint labels give annualized geometric returns.</p>

## Three tranches

Each tranche receives one third of strategy notional, holds its own portfolio
and continues to rebalance every three weeks. One tranche trades each week,
as Table 1 shows. I participate in all three starting weeks without replacing
the whole portfolio weekly.

<table class="research-table sleeve-schedule">
  <caption><strong>Table 1: Two rotations over six weeks.</strong> W1–W6 denote weeks; ● marks a rebalance and — means hold.</caption>
  <thead><tr><th>Offset</th><th>W1</th><th>W2</th><th>W3</th><th>W4</th><th>W5</th><th>W6</th></tr></thead>
  <tbody>
    <tr class="sleeve-a"><th scope="row">Week 1 <small>⅓ notional</small></th><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td></tr>
    <tr class="sleeve-b"><th scope="row">Week 2 <small>⅓ notional</small></th><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td></tr>
    <tr class="sleeve-c"><th scope="row">Week 3 <small>⅓ notional</small></th><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td><td>—</td><td>—</td><td class="rebalance"><span role="img" aria-label="Rebalance">●</span></td></tr>
  </tbody>
</table>

For daily net P&L per unit of fixed notional $r_{j,t}$, the combined return is

$$
r_{\mathrm{combined},t}=\frac{r_{1,t}+r_{2,t}+r_{3,t}}{3}.
$$

I scale each standalone book's positions and P&L to one third of the total
notional. Its arithmetic mean return therefore equals the average across the
three calendars, including proportional costs. Geometric return can differ
slightly through compounding. Volatility, Sharpe and drawdown must be calculated
from the combined daily returns. I leave the resulting reduction in risk in
place, with no increase in leverage to restore standalone volatility.

## Does the weekday matter?

Once I hold all three offsets, I no longer have to choose a starting week.
I still have to choose a weekday. To see how much that remaining choice matters,
I ran the same comparison for Monday through Friday: fifteen standalone calendars
and five portfolios combining three offsets each. They implement the same
strategy and share much of the same return history.

The three-week cycle is anchored to the week beginning 31 August 1998. A weekly
signal target falling on a holiday rolls forward to the next eligible session;
the three offsets select every third target. All fifteen calendars are evaluated
on the same dates, beginning 22 September 1998 once every calendar is active.

I expected the starting week to matter more than the weekday. Figure 2 shows
why I can't separate them so neatly. Over the full period, Week 3 is the best
offset on Monday and the worst on Friday. There isn't a starting week that
works best regardless of the weekday.

<div class="research-figure rebalancing-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/tranching/calendar-grid" mobile="/assets/tranching/calendar-grid_mobile" version="2" alt="Full-period annualized returns for three starting-week offsets and five signal weekdays, with five three-tranche portfolios below. Standalone returns range from 10.21% to 12.27%." %}
</div>

<p class="figure-caption"><strong>Figure 2: The outcome depends on the weekday–offset combination.</strong> September 1998–May 2026. Rows are starting-week offsets; columns are signal weekdays. Blue shading uses one common return scale. The separated bottom row combines all three offsets within each column.</p>

That reversal also appears in the later period: Week 3 returns 10.55% with
Monday signals and 5.42% with Friday signals. Changing the weekday while keeping
the offset fixed produces spreads of 2.79, 3.75 and 5.13 points for Weeks 1, 2
and 3. A descriptive offset–weekday decomposition assigns most of the variation
to their interaction, over the full history and within both periods. The
particular combination matters. These overlapping returns do not provide
fifteen independent observations.

Combining the offsets still makes a large difference. Table 2 compares all
fifteen standalone outcomes with the five combined outcomes. Across the full
history, the range shrinks by **81%**, from 2.06 to 0.40 percentage points,
while the standard deviation falls by **72%**. Mean return changes by just
**6 bp**. Later, the return range
shrinks by **79%**, from 5.13 to 1.06 percentage points. The standard deviation
across calendars falls by **77%**, from 1.58 to 0.37 points. The average return
changes by just **4 bp**. Both measures of dispersion also fall substantially
in development.

<table class="research-table comparison-table risk-performance-table">
  <caption><strong>Table 2: Less dependence on the calendar.</strong> Annualized net geometric return, its best-to-worst range, and population standard deviation across the stated calendars. Return is in percent; range and SD are in percentage points.</caption>
  <thead><tr><th>Calendars</th><th>Mean return</th><th>Range</th><th>SD</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="4">Full history · September 1998–May 2026</th></tr>
    <tr><th scope="row">15 standalone</th><td>11.37%</td><td>2.06</td><td>0.53</td></tr>
    <tr class="selected-rule"><th scope="row">5 three-tranche</th><td>11.43%</td><td>0.40</td><td>0.15</td></tr>
    <tr class="period-heading"><th colspan="4">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">15 standalone</th><td>12.04%</td><td>2.29</td><td>0.54</td></tr>
    <tr class="selected-rule"><th scope="row">5 three-tranche</th><td>12.10%</td><td>0.50</td><td>0.16</td></tr>
    <tr class="period-heading"><th colspan="4">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">15 standalone</th><td>7.87%</td><td>5.13</td><td>1.58</td></tr>
    <tr class="selected-rule"><th scope="row">5 three-tranche</th><td>7.91%</td><td>1.06</td><td>0.37</td></tr>
  </tbody>
</table>

In the later period, the five combined portfolios still range from 7.25% to
8.31% annualized return.
That remaining 1.06-point spread is economically relevant, even after removing
most of the original dispersion. The reduction also appears in development and
in each complete year from 1999 to 2025, using both range and standard deviation.
I report both measures because the range depends partly on how many calendars
are compared.
Over individual years the remaining weekday differences can be larger:
the combined portfolios' annual return spread is 1.74–4.91 points across
2022–2025. I would expect tranching to reduce the importance of the calendar,
without expecting these particular reduction percentages to repeat exactly.

## Similar return, lower volatility

Calendar dispersion measures how much the outcome changes when I choose a
different schedule. Portfolio volatility measures fluctuations through time.
Figure 3 puts the two results side by side. The mean return barely moves, but
the range of calendar outcomes narrows. The volatility comparison shifts lower:
all five combined portfolios fluctuate less than any of the standalone calendars.

<div class="research-figure rebalancing-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/tranching/calendar-return-risk" mobile="/assets/tranching/calendar-return-risk_mobile" version="3" alt="Full-period mean and range across fifteen standalone calendars versus five three-tranche portfolios. Mean net return is 11.37% versus 11.43%; mean volatility is 8.53% versus 7.88%." %}
</div>

<p class="figure-caption"><strong>Figure 3: Similar return, less calendar dependence and lower volatility.</strong> September 1998–May 2026. Each dot is the mean; each line spans the minimum and maximum across fifteen standalone calendars or five three-tranche portfolios. The two panels use different numerical scales.</p>

Across the full history, average net return moves from 11.37% to 11.43%.
Average volatility falls from 8.53% to 7.88%, a reduction of 0.65 percentage
points, or 7.6%. Lower volatility explains the rise in average Sharpe from
1.30 to 1.41. I get almost the same mean return from a less volatile portfolio.
Table 3 puts those averages beside the range of outcomes.

This pattern holds within each weekday. The later volatility reductions range
from 5.3% to 5.7%, with return differences of just 3–5 bp. In development,
volatility falls by 8.1–8.4%, with about 6 bp difference in return. These are
averages across implementations; each combined portfolio's volatility, Sharpe
and drawdown is first calculated from its own daily returns.

<table class="research-table comparison-table risk-performance-table">
  <caption><strong>Table 3: Similar average return, lower portfolio risk.</strong> Mean [minimum, maximum] across fifteen standalone calendars or five three-tranche portfolios. Brackets give calendar ranges. Net return is geometric; return, volatility and drawdown are percentages. Annualization uses 252 sessions and Sharpe a zero cash rate.</caption>
  <thead><tr><th>Metric</th><th>15 standalone<br>calendars</th><th>5 three-tranche<br>portfolios</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="3">Full history · September 1998–May 2026</th></tr>
    <tr><th scope="row">Net return</th><td>11.37<br>[10.21, 12.27]</td><td>11.43<br>[11.27, 11.67]</td></tr>
    <tr><th scope="row">Volatility</th><td>8.53<br>[8.42, 8.69]</td><td>7.88<br>[7.82, 7.90]</td></tr>
    <tr><th scope="row">Sharpe</th><td>1.30<br>[1.19, 1.40]</td><td>1.41<br>[1.39, 1.44]</td></tr>
    <tr><th scope="row">Max drawdown</th><td>−19.51<br>[−23.63, −14.51]</td><td>−16.82<br>[−18.58, −15.08]</td></tr>
    <tr class="period-heading"><th colspan="3">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Net return</th><td>12.04<br>[10.78, 13.08]</td><td>12.10<br>[11.87, 12.37]</td></tr>
    <tr><th scope="row">Volatility</th><td>8.38<br>[8.23, 8.56]</td><td>7.70<br>[7.62, 7.73]</td></tr>
    <tr><th scope="row">Sharpe</th><td>1.40<br>[1.27, 1.53]</td><td>1.52<br>[1.50, 1.55]</td></tr>
    <tr><th scope="row">Max drawdown</th><td>−19.51<br>[−23.63, −14.51]</td><td>−16.82<br>[−18.58, −15.08]</td></tr>
    <tr class="period-heading"><th colspan="3">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Net return</th><td>7.87<br>[5.42, 10.55]</td><td>7.91<br>[7.25, 8.31]</td></tr>
    <tr><th scope="row">Volatility</th><td>9.31<br>[9.16, 9.41]</td><td>8.80<br>[8.74, 8.83]</td></tr>
    <tr><th scope="row">Sharpe</th><td>0.86<br>[0.62, 1.12]</td><td>0.91<br>[0.84, 0.95]</td></tr>
    <tr><th scope="row">Max drawdown</th><td>−8.98<br>[−10.99, −7.39]</td><td>−8.61<br>[−8.83, −8.30]</td></tr>
  </tbody>
</table>

The tranches select stocks on different dates, so their portfolios differ.
Their daily returns remain highly correlated: pairwise correlations within
weekdays range from 0.75 to 0.77 in development and 0.82 to 0.85 later.
Those differences provide some diversification, while most strategy risk
remains shared. The higher later correlations also fit the smaller volatility
reduction. The tranches' variances and covariances account for the combined
portfolio's lower volatility: what matters is how much they fluctuate and how
closely they move together.

This is also the useful connection to [Concretum's tranching study](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf).
Its Section 4 reports little change in average CAGR before transaction costs
as the number of tranches increases, alongside a substantial reduction in
dispersion across schedules.
Here too, preserving average return while reducing calendar dependence is the
main result. The volatility reduction provides an additional benefit.

## What it takes to implement

Trading each week means more orders, but each tranche trades less capital.
At the same USD 5 million reference notional, the later Friday comparison moves
from roughly 2,807 orders a year for the average standalone calendar to 8,420
for the three-tranche portfolio. Average order size falls from about USD 44,000
to USD 14,700. Annual two-way traded notional remains 24.7 times reference capital,
where two-way turnover sums absolute purchases and sales.

At the existing 5 bp cost rate, annual arithmetic cost drag is therefore
unchanged at 1.24 percentage points for that comparison; it is 1.41 points in
development. The return and risk benefits above already include these costs.
Trades are accounted for separately across tranches, with no netting savings.
Fixed-ticket charges, borrow and financing are outside the model. The practical
change here is tracking three books and sending smaller orders more often.

I would fund all three tranches. The full-history Friday spread is fairly
modest, so I wouldn't base the decision on the striking later-period chart
alone. The volatility reduction is the more useful takeaway for me: from
8.53% to 7.88% across the full calendar comparison, with almost unchanged
average return. This is a useful, incremental reduction in risk. That benefit
appears in both periods, though its size changes,
and the results already include the existing 5 bp costs. For me, that is enough
to justify maintaining three books and sending smaller orders more often.
Less dependence on the calendar comes alongside that reduction in portfolio risk.
