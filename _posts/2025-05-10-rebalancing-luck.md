---
layout: post
title: "Reducing Rebalancing Timing Risk with Tranching"
date: 2025-05-10
last_modified_at: 2026-08-22
categories: [Quants]
article_label: Portfolio construction · Rebalancing
permalink: /quants/2025/05/10/rebalancing-luck.html
---

"Rebalance every three weeks" sounds precise, but it leaves two calendar choices:
where the three-week cycle begins, and which weekday the portfolio trades. Two
otherwise identical implementations can then compound to different outcomes merely
because one starts a few days earlier. That dispersion is usually called
*rebalance timing luck*.

[Newfound Research](https://www.thinknewfound.com/rebalance-timing-luck) finds
that the effect is largest when turnover is high, portfolios are concentrated,
or holdings change quickly. [Concretum Research](https://concretumgroup.com/wp-content/uploads/2026/02/The-Tranching-Dilemma.pdf)
makes the same problem concrete in a monthly momentum strategy: average return
hardly changes as more schedules are combined, but the gap between the luckiest
and unluckiest schedule contracts sharply. That is the appeal of tranching: it
spreads the portfolio across several execution schedules, making any one
arbitrary calendar choice matter less.

I use my own long/short stock-ranking strategy to ask a narrower question. If I
split the portfolio across three overlapping sleeves, can I preserve the return
while making the path less dependent on the starting week?

## Fifteen ways to run the same strategy

The strategy uses LightGBM predictions and holds each portfolio for three
weeks. A full-rebalance implementation has three possible starting-week offsets
and five possible weekdays, giving 15 schedules:

$$
3\text{ offsets}\times 5\text{ weekdays}=15\text{ schedules}.
$$

The model, universe, ranking rule, and holding period are unchanged. Only the
signal and execution date move. That small shift changes which predictions are
available at the rebalance and, sometimes, which stocks enter the book.

The archive retains the schedule grid and summary results, but not enough daily
detail to reproduce them. I therefore use the evidence descriptively. The axes
suggest a sample of roughly 1999–2025; the exact endpoints were not retained.

<div class="research-figure rebalancing-figure">
  <img src="/assets/tranching/all_perf_plots.png" alt="Cumulative wealth on a logarithmic scale for fifteen full-rebalance schedules, with two terminal extremes highlighted after the backtest" width="1800" height="1200" loading="lazy" decoding="async">
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Cumulative wealth for 15 full-rebalance schedules; highest and lowest terminal paths highlighted ex post; log scale, start = 1.</p>

The paths part gradually, as small differences in signal dates and holdings
compound into a large gap in terminal wealth. This is evidence of schedule
sensitivity. Because the best and worst lines were labelled after the full
sample was known, their order says nothing about a persistent weekday edge.

<table class="research-table comparison-table rebalancing-summary-table">
  <thead>
    <tr>
      <th>Metric</th>
      <th>Range across schedules</th>
      <th>Mean</th>
    </tr>
  </thead>
  <tbody>
    <tr><th scope="row">Annualized geometric return</th><td data-label="Range">10.10%–12.53%</td><td data-label="Mean">11.32%</td></tr>
    <tr><th scope="row">Volatility</th><td data-label="Range">6.45%–6.97%</td><td data-label="Mean">6.68%</td></tr>
    <tr><th scope="row">Sharpe ratio</th><td data-label="Range">1.50–1.75</td><td data-label="Mean">1.64</td></tr>
    <tr><th scope="row">Maximum drawdown</th><td data-label="Range">10.70%–14.77%</td><td data-label="Mean">12.77%</td></tr>
    <tr><th scope="row">Maximum underwater duration</th><td data-label="Range">248–593 days</td><td data-label="Mean">413 days</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Dispersion across the 15 full-rebalance schedules.</p>

Annualized geometric return differs by 2.43 percentage points between the best
and worst schedules; the Sharpe ratio ranges from 1.50 to 1.75, and time
underwater from 248 to 593 days. A single backtest would hide all of that behind
one arbitrary calendar choice. The differences are large enough to matter.
Their ex-post ranking has no forecasting value, and the missing cost record
limits the comparison to timing dispersion before documented implementation
costs.

## Spreading the rebalance across three tranches

The tranched implementation splits the portfolio into three equal-capital
sleeves. One sleeve rebalances each week on the chosen weekday, and each remains
on the same three-week holding cycle. After three weeks the whole portfolio has
been refreshed, but no single day replaces every position at once.

This construction averages across the three starting-week offsets while keeping
the weekday fixed. A Monday version trades every sleeve on Monday, and the same
is true for Tuesday through Friday. Figure 2 therefore shows five tranched
portfolios, one for each weekday.

<div class="research-figure rebalancing-figure">
  <img src="/assets/tranching/tranched_perf_plots.png" alt="Cumulative wealth on a logarithmic scale for five three-tranche portfolios, one for each rebalance weekday" width="1800" height="1200" loading="lazy" decoding="async">
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Cumulative wealth for five three-tranche weekday portfolios; log scale, start = 1.</p>

<table class="research-table comparison-table rebalancing-results-table">
  <thead>
    <tr>
      <th>Weekday</th>
      <th>Annualized geometric return</th>
      <th>Volatility</th>
      <th>Sharpe</th>
      <th>Max drawdown</th>
      <th>Max underwater</th>
    </tr>
  </thead>
  <tbody>
    <tr><th scope="row">Monday</th><td data-label="Annualized geometric return">11.32%</td><td data-label="Volatility">6.08%</td><td data-label="Sharpe">1.80</td><td data-label="Max drawdown">11.08%</td><td data-label="Max underwater">370 days</td></tr>
    <tr><th scope="row">Tuesday</th><td data-label="Annualized geometric return">11.23%</td><td data-label="Volatility">6.04%</td><td data-label="Sharpe">1.79</td><td data-label="Max drawdown">11.63%</td><td data-label="Max underwater">301 days</td></tr>
    <tr><th scope="row">Wednesday</th><td data-label="Annualized geometric return">11.24%</td><td data-label="Volatility">6.08%</td><td data-label="Sharpe">1.78</td><td data-label="Max drawdown">11.89%</td><td data-label="Max underwater">299 days</td></tr>
    <tr><th scope="row">Thursday</th><td data-label="Annualized geometric return">11.63%</td><td data-label="Volatility">6.06%</td><td data-label="Sharpe">1.85</td><td data-label="Max drawdown">11.01%</td><td data-label="Max underwater">303 days</td></tr>
    <tr><th scope="row">Friday</th><td data-label="Annualized geometric return">11.43%</td><td data-label="Volatility">6.11%</td><td data-label="Sharpe">1.80</td><td data-label="Max drawdown">12.37%</td><td data-label="Max underwater">364 days</td></tr>
    <tr class="summary-row"><th scope="row">Mean</th><td data-label="Annualized geometric return">11.37%</td><td data-label="Volatility">6.07%</td><td data-label="Sharpe">1.80</td><td data-label="Max drawdown">11.60%</td><td data-label="Max underwater">327 days</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Performance of the three-tranche portfolios by weekday.</p>

Mean annualized geometric return barely moves: 11.37% across the five tranched
portfolios, against 11.32% across the 15 full-rebalance schedules. The
improvement is in the path. Mean volatility falls from 6.68% to 6.07%, or about
9%; mean maximum drawdown falls
from 12.77% to 11.60%; and mean time underwater falls by 86 days. With nearly
the same return and less volatility, the descriptive mean Sharpe rises from 1.64
to 1.80.

The dispersion narrows as well. The geometric-return range contracts from 2.43
to 0.40 percentage points, the maximum-drawdown range from 4.07 to 1.36 points,
and the underwater-duration range from 345 to 71 days. Put differently, once
the three starting-week offsets are combined, roughly five-sixths of the
observed return range disappears. The five remaining weekday portfolios are
close: their volatilities span only 6.04% to 6.11%, and their Sharpes 1.78 to
1.85.

The visible calendar dispersion is much larger across starting-week offsets
than across weekdays. Two mechanisms could produce the smoother tranched path:
averaging those offsets, and refreshing one-third of the predictions each week.
The saved experiment cannot tell them apart.

## What the comparison identifies—and what remains open

Three tranches directly average the three starting-week offsets. I would not add
weekday sleeves on the strength of these results. The remaining weekday range is
small, and more sleeves would mean smaller orders, more frequent runs, and more
operational state for an uncertain incremental gain.

My preference is therefore for the complete three-tranche implementation, not a
claim that timing diversification alone caused the improvement. A cleaner test
would hold the prediction vintage fixed while changing only the execution
schedule, and then test fresher weekly predictions separately.

The retained research archive contains the two return-path charts and the
summary metrics reported here, but not the daily schedule returns or the
figure-generation code. The saved tables are internally consistent with the
older detailed table in repository history, and the charts visually agree with
their dispersion, but the statistics cannot be recomputed from raster images.
I also cannot recompute turnover, inspect individual trades, or run new tests.
The results do not document whether costs were included or how they were
defined. They should therefore be treated as evidence about timing dispersion
with undocumented cost treatment, not as implementation-grade return estimates.

Costs decide whether the smoother observed path is worth implementing. Smaller
orders may incur minimum fees and fixed operational overhead; spreading a large
order, however, may reduce market impact. More frequent rebalancing creates both
fresher signals and more opportunities to trade. The practical choice should
rest on net results using current holdings, turnover, spread and impact
estimates, borrow costs, and operational overhead—not on reported backtest
smoothness alone.

## Conclusion

The experiment changes how I would report a fixed-cycle strategy. One rebalance
schedule is one draw from a wider set of plausible outcomes, not the backtest.
The full timing grid makes that uncertainty visible.

The complete three-tranche implementation leaves mean annualized geometric
return almost unchanged, reduces mean volatility by 0.61 percentage points, and lifts the descriptive
Sharpe from 1.64 to 1.80. It also shows much less dispersion than the 15
full-rebalance schedules; the remaining variation across weekdays is
comparatively small. That is enough for me to prefer the three-sleeve
implementation as a working design, not because it earns more, but because it
relies less on getting one starting week right.

The reservation is practical. Fresher predictions may share credit for the
improvement, and the missing daily archive prevents a realistic cost replay. I
would freeze the three-sleeve design, rebuild the daily evidence, and compare it
with a full-rebalance version using the same prediction vintages. Only then can
turnover, spreads, impact, borrow, and operational overhead decide whether the
observed risk reduction survives implementation.

## References

- [Rebalance Timing Luck](https://www.thinknewfound.com/rebalance-timing-luck) — Newfound Research
- [Global Tactical Asset Allocation: Updated Results and Real-Market Implementation Using Python and IBKR](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5230603) — Mohamed Gabriel, Alberto Pagani, and Carlo Zarattini
- [The Tranching Dilemma](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5747964) — Carlo Zarattini and Alberto Pagani
