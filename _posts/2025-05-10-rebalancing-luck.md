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

<p class="article-summary">The same strategy can deliver quite different returns depending on its rebalance calendar. Splitting it into three tranches preserves average return while reducing that dependence. Across fifteen calendars, the later-period return spread falls from 5.13 to 1.06 percentage points. Portfolio volatility falls too.</p>

## The starting-week problem

“Rebalance every three weeks” sounds like a complete rule. It still leaves me
with a choice of three starting weeks. Each one sees a different sequence of
signals and prices, even though I use the same forecasting and allocation
rules. From January 2022 to May 2026, annualized net return ranges from **5.42%
to 9.91%** across the three Friday schedules: a **4.49 percentage-point spread**.
That is a lot to leave to the calendar. Choosing the best week after seeing the
results would just give me another way to fit the backtest.

I use the [same stock strategy](/quants/2026/08/29/portfolio-optimization.html)
throughout: the forecasts, point-in-time universe, selection and sizing rules,
and gross exposure cap stay fixed. Friday refers to the signal date; execution
is at the next trading-session close. All returns include the existing 5 bp
allowance for transaction costs and market impact. I report development
(September 1998–December 2021) and later history (January 2022–May 2026)
separately. The later period has already informed research choices.

Figure 1 shows the experience of committing to each Friday calendar. The
highlighted three-tranche portfolio combines them with equal notional. Its
return sits near their average; it does not capture the gap between the best
and worst schedules.

<div class="research-figure rebalancing-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/tranching/schedule-performance" mobile="/assets/tranching/schedule-performance_mobile" version="4" alt="Three fixed Friday calendars diverge from January 2022 to May 2026. Annualized returns are 8.63%, 9.91% and 5.42%; the three-tranche portfolio returns 8.02%." %}
</div>

<p class="figure-caption"><strong>Figure 1: The calendar changes the investor's experience.</strong> January 2022–27 May 2026. Each path uses one fixed calendar throughout. The index compounds daily net P&amp;L per unit of fixed notional; endpoint labels give annualized geometric returns. The combined portfolio retains its lower volatility.</p>

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

Combining three offsets removes the starting-week choice by construction.
The empirical question is how much that choice mattered, and how much calendar
dependence remains. I extended the comparison to all five signal weekdays:
fifteen standalone calendars and five portfolios that each combine their
weekday's three offsets. These are overlapping implementations of one strategy.

The three-week cycle is anchored to the week beginning 31 August 1998. A weekly
signal target falling on a holiday rolls forward to the next eligible session;
the three offsets select every third target. All fifteen calendars are evaluated
on the same dates, beginning 22 September 1998 once every calendar is active.

I expected the starting week to matter more than the weekday. Figure 2 makes
that claim harder to sustain in a simple form. The within-weekday return spread
is 3.64–4.49 percentage points for four weekdays, but only 0.67 for Thursday.
Reading across a row gives weekday spreads of 2.79, 3.75 and 5.13 points.
Week 3 is the best offset on Monday and the worst on Friday.

<div class="research-figure rebalancing-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/tranching/calendar-grid" mobile="/assets/tranching/calendar-grid_mobile" version="1" alt="Later-period annualized returns for three offsets and five signal weekdays, with the five combined portfolios below. Week 3 ranges from 10.55% on Monday to 5.42% on Friday." %}
</div>

<p class="figure-caption"><strong>Figure 2: The outcome depends on the weekday–offset combination.</strong> Rows are starting-week offsets; columns are signal weekdays. Darker cells indicate higher annualized net returns on one common scale. The separated bottom row combines all three offsets within each column.</p>

A descriptive split into offset, weekday and their interaction attributes
83% of the later variation to the interaction, and 87% in development.
In other words, the particular combination matters more than a consistent
advantage for one week or weekday. These percentages describe this anchored
grid; the shared returns do not provide fifteen independent observations.

The practical benefit of tranching is clearer. Table 2 compares all fifteen
standalone outcomes with the five combined outcomes. Later, the return range
shrinks by **79%**, from 5.13 to 1.06 percentage points. The standard deviation
across calendars falls by **77%**, from 1.58 to 0.37 points. The average return
changes by just **4 bp**. Both measures of dispersion also fall substantially
in development.

<table class="research-table comparison-table risk-performance-table">
  <caption><strong>Table 2: Less dependence on the calendar.</strong> Annualized net geometric return, its best-to-worst range, and population standard deviation across the stated calendars. Return is in percent; range and SD are in percentage points.</caption>
  <thead><tr><th>Calendars</th><th>Mean return</th><th>Range</th><th>SD</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="4">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">15 standalone</th><td>12.04%</td><td>2.29</td><td>0.54</td></tr>
    <tr class="selected-rule"><th scope="row">5 three-tranche</th><td>12.10%</td><td>0.50</td><td>0.16</td></tr>
    <tr class="period-heading"><th colspan="4">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">15 standalone</th><td>7.87%</td><td>5.13</td><td>1.58</td></tr>
    <tr class="selected-rule"><th scope="row">5 three-tranche</th><td>7.91%</td><td>1.06</td><td>0.37</td></tr>
  </tbody>
</table>

The range depends on how many calendars are included, which is why I report
standard deviation alongside it. The combined calendars have a smaller range
and standard deviation in each complete year from 1999 to 2025 as well.
The remaining weekday effect can still matter over shorter periods: across
2022–2025, the combined portfolios' annual return range varies from 1.74 to
4.91 percentage points. Tranching reduces calendar dependence considerably;
it does not make every implementation deliver the same experience.

## Similar return, lower volatility

Calendar dispersion measures how much the outcome changes when I choose a
different schedule. Portfolio volatility measures fluctuations through time.
Figure 3 separates the return and volatility comparisons for each weekday.
The blue squares sit close to the standalone mean returns, while combined
volatility falls below every individual offset's volatility.

<div class="research-figure rebalancing-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/tranching/calendar-return-risk" mobile="/assets/tranching/calendar-return-risk_mobile" version="1" alt="For every signal weekday, the three-tranche portfolio has nearly the mean standalone annualized return and lower volatility than all three offsets. Later period, January 2022 to May 2026." %}
</div>

<p class="figure-caption"><strong>Figure 3: The improvement comes from lower risk.</strong> January 2022–May 2026. Dots show the three offsets, open diamonds their mean statistic, and blue squares the combined daily portfolio. Horizontal segments span observed calendars. The return and volatility panels use different numerical scales.</p>

For the original Friday comparison in Table 3, net return moves from a
standalone mean of 7.99% to 8.02%. Volatility falls from 9.32% to 8.83%:
0.49 percentage points, or 5.3%. That reduction drives the Sharpe increase
from 0.87 to 0.92. Across all five weekdays, the later volatility reduction is
5.3–5.7%, with return differences of only 3–5 bp. In development, the volatility
reduction is 8.1–8.4%, with about 6 bp difference in return.

<table class="research-table comparison-table risk-performance-table">
  <caption><strong>Table 3: The original three Friday offsets.</strong> Standalone entries are mean [minimum, maximum] across those three offsets. Brackets give calendar ranges. Return, volatility and drawdown are percentages; Sharpe uses a zero cash rate. Annualization uses 252 sessions.</caption>
  <thead><tr><th>Metric</th><th>Standalone<br>mean [min, max]</th><th>Three-tranche<br>portfolio</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="3">Development · September 1998–December 2021</th></tr>
    <tr><th scope="row">Net return</th><td>12.31<br>[11.95, 12.53]</td><td>12.37</td></tr>
    <tr><th scope="row">Volatility</th><td>8.40<br>[8.32, 8.48]</td><td>7.72</td></tr>
    <tr><th scope="row">Sharpe</th><td>1.43<br>[1.40, 1.45]</td><td>1.55</td></tr>
    <tr><th scope="row">Max drawdown</th><td>−18.06<br>[−19.70, −15.21]</td><td>−15.53</td></tr>
    <tr class="period-heading"><th colspan="3">Later · January 2022–May 2026</th></tr>
    <tr><th scope="row">Net return</th><td>7.99<br>[5.42, 9.91]</td><td>8.02</td></tr>
    <tr><th scope="row">Volatility</th><td>9.32<br>[9.17, 9.41]</td><td>8.83</td></tr>
    <tr><th scope="row">Sharpe</th><td>0.87<br>[0.62, 1.05]</td><td>0.92</td></tr>
    <tr><th scope="row">Max drawdown</th><td>−9.05<br>[−9.16, −8.92]</td><td>−8.83</td></tr>
  </tbody>
</table>

The tranches select stocks on different dates, so their portfolios differ.
Their daily returns remain highly correlated: pairwise correlations within
weekdays range from 0.75 to 0.77 in development and 0.82 to 0.85 later.
Those differences provide some diversification, while most strategy risk
remains shared. The higher later correlations also fit the smaller volatility
reduction. Averaging their covariances reproduces the combined variance; the
risk reduction comes from how the tranches move together.

This is also the useful connection to [Concretum's tranching study](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf).
Its Section 4 reports little change in average CAGR as the number of tranches
increases, alongside a substantial reduction in dispersion across schedules.
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

I would fund all three tranches. The average return is essentially preserved,
and much less depends on having chosen a fortunate calendar. The full grid
also keeps the conclusion honest: the weekday still matters, and the strategy's
shared risks remain. Three tranches address a sizeable part of the calendar
problem with a simple change in how the same strategy is scheduled.
