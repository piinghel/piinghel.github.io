---
layout: post
title: "Reducing Rebalancing Timing Risk with Tranching"
date: 2025-05-10
last_modified_at: 2026-08-22
categories: [Quants]
article_mark: /assets/brand/quant-notes-mark.svg
article_label: Portfolio construction · Rebalancing
permalink: /quants/2025/05/10/rebalancing-luck.html
---

Rebalancing every three weeks sounds precise, but it leaves one arbitrary
choice: which week and which weekday? Two otherwise identical portfolios can
compound to different outcomes simply because one trades a few days earlier
than the other. That dispersion is usually called *rebalance timing luck*.

[Newfound Research](https://www.thinknewfound.com/rebalance-timing-luck) has
shown that the effect can be material in concentrated or faster-moving
strategies. A common response is tranching: split the capital across overlapping
portfolios and rebalance a smaller part more frequently. I use my own long/short
stock-ranking strategy to ask a practical question: how much of the result
depends on the chosen schedule, and how much of that dependence can three
overlapping tranches remove?

## Fifteen ways to run the same strategy

The strategy uses LightGBM predictions and holds each portfolio for three
weeks. A full-rebalance implementation has three possible starting-week offsets
and five possible weekdays, giving 15 schedules:

$$
3\text{ offsets}\times 5\text{ weekdays}=15\text{ schedules}.
$$

The model, universe, ranking rule, and holding period are unchanged. What moves
is the signal and execution date. That small shift changes the predictions
available at the rebalance and the returns subsequently earned by the selected
stocks.

<div class="research-figure rebalancing-figure">
  <img src="/assets/tranching/all_perf_plots.png" alt="Cumulative return paths for fifteen full-rebalance schedules, highlighting the best and worst outcomes" loading="lazy" decoding="async">
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Fifteen full-rebalance schedules, with the best and worst paths highlighted.</p>

The paths separate gradually rather than around one isolated event. That is the
important feature of timing luck: small differences in holdings accumulate into
large differences in terminal wealth even when no schedule has a persistent
informational advantage.

<table class="research-table comparison-table rebalancing-summary-table">
  <thead>
    <tr>
      <th>Metric</th>
      <th>Range across schedules</th>
      <th>Mean</th>
    </tr>
  </thead>
  <tbody>
    <tr><th scope="row">Geometric return</th><td data-label="Range">10.10%–12.53%</td><td data-label="Mean">11.32%</td></tr>
    <tr><th scope="row">Volatility</th><td data-label="Range">6.45%–6.97%</td><td data-label="Mean">6.68%</td></tr>
    <tr><th scope="row">Sharpe ratio</th><td data-label="Range">1.50–1.75</td><td data-label="Mean">1.64</td></tr>
    <tr><th scope="row">Maximum drawdown</th><td data-label="Range">10.70%–14.77%</td><td data-label="Mean">12.77%</td></tr>
    <tr><th scope="row">Time underwater</th><td data-label="Range">248–593 days</td><td data-label="Mean">413 days</td></tr>
  </tbody>
</table>

<p class="figure-caption"><strong>Table 1:</strong> Dispersion across the 15 full-rebalance schedules.</p>

Annualized return differs by 2.43 percentage points between the best and worst
schedules, while the Sharpe ratio ranges from 1.50 to 1.75. The widest gap is in
time underwater: 248 days for one schedule and 593 for another. Reporting only
one of these backtests would hide how sensitive the result is to a choice that
has no economic meaning.

## Spreading the rebalance across three tranches

The tranched implementation splits the portfolio into three equal-capital
sleeves. One sleeve rebalances each week on the chosen weekday, and each remains
on the same three-week holding cycle. After three weeks the whole portfolio has
been refreshed, but no single day replaces every position at once.

This construction averages across the three starting-week offsets. It does not
average across weekdays: a Monday version still trades every sleeve on Monday,
and the same is true for Tuesday through Friday. Figure 2 therefore shows five
tranched portfolios, one for each weekday.

<div class="research-figure rebalancing-figure">
  <img src="/assets/tranching/tranched_perf_plots.png" alt="Cumulative return paths for five three-tranche portfolios, one for each rebalance weekday" loading="lazy" decoding="async">
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Three-tranche portfolios by rebalance weekday.</p>

<table class="research-table comparison-table rebalancing-results-table">
  <thead>
    <tr>
      <th>Weekday</th>
      <th>Return</th>
      <th>Volatility</th>
      <th>Sharpe</th>
      <th>Max drawdown</th>
      <th>Underwater</th>
    </tr>
  </thead>
  <tbody>
    <tr><th scope="row">Monday</th><td data-label="Return">11.32%</td><td data-label="Volatility">6.08%</td><td data-label="Sharpe">1.80</td><td data-label="Max drawdown">11.08%</td><td data-label="Underwater">370 days</td></tr>
    <tr><th scope="row">Tuesday</th><td data-label="Return">11.23%</td><td data-label="Volatility">6.04%</td><td data-label="Sharpe">1.79</td><td data-label="Max drawdown">11.63%</td><td data-label="Underwater">301 days</td></tr>
    <tr><th scope="row">Wednesday</th><td data-label="Return">11.24%</td><td data-label="Volatility">6.08%</td><td data-label="Sharpe">1.78</td><td data-label="Max drawdown">11.89%</td><td data-label="Underwater">299 days</td></tr>
    <tr><th scope="row">Thursday</th><td data-label="Return">11.63%</td><td data-label="Volatility">6.06%</td><td data-label="Sharpe">1.85</td><td data-label="Max drawdown">11.01%</td><td data-label="Underwater">303 days</td></tr>
    <tr><th scope="row">Friday</th><td data-label="Return">11.43%</td><td data-label="Volatility">6.11%</td><td data-label="Sharpe">1.80</td><td data-label="Max drawdown">12.37%</td><td data-label="Underwater">364 days</td></tr>
    <tr class="summary-row"><th scope="row">Mean</th><td data-label="Return">11.37%</td><td data-label="Volatility">6.07%</td><td data-label="Sharpe">1.80</td><td data-label="Max drawdown">11.60%</td><td data-label="Underwater">327 days</td></tr>
  </tbody>
</table>

<p class="figure-caption"><strong>Table 2:</strong> Performance of the three-tranche portfolios by weekday.</p>

The mean geometric return is almost unchanged: 11.32% for the full-rebalance
schedules and 11.37% after tranching. The difference is in dispersion and risk.
Average volatility falls from 6.68% to 6.07%, maximum drawdown from 12.77% to
11.60%, and time underwater from 413 to 327 days. The five lines in Figure 2
also sit much closer together than the 15 paths in Figure 1.

This is the useful role of tranching. It does not create a new stock-selection
signal; it diversifies when the existing signal enters the portfolio. Combining
partially independent timing outcomes can preserve the average return while
reducing the risk of committing all capital on one arbitrary date.

## What the comparison does not isolate

Three tranches reduce starting-week sensitivity, but weekday choice remains.
Eliminating all 15 schedule choices would require many more overlapping sleeves,
which adds operational complexity and smaller orders. The saved result summary
also does not separate gross from net performance or document a transaction-cost
sensitivity, so the return levels should not be treated as implementation-grade
estimates.

There is a second distinction. The tranched portfolio incorporates a fresh set
of predictions each week, whereas the full-rebalance portfolio waits three
weeks before replacing every position. Tranching therefore changes signal
freshness as well as diversifying timing. The experiment shows that the complete
tranched implementation is more stable; it does not attribute every part of the
improvement to one mechanism.

Costs can also change the preferred number of sleeves. [Zarattini and
Pagani](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5747964) find that
tranching consistently reduces timing dispersion, but its net benefit depends
on assets under management and trading costs. Smaller investors may lose more
to minimum commissions and small orders, while larger portfolios can benefit
from spreading market impact over time. That trade-off should be measured with
the actual execution model rather than assumed from turnover alone.

## Conclusion

The experiment changes how I would report and run a fixed-cycle strategy. A
single rebalance schedule is one draw from a wider set of plausible outcomes,
so it is not enough evidence on its own. Testing the full timing grid makes that
uncertainty visible.

Three weekly tranches are a practical compromise. In this sample they leave
average return almost unchanged while reducing volatility, drawdown, time
underwater, and the spread between schedules. I would use the tranched version
as the working implementation, while keeping the remaining weekday sensitivity
and trading-cost assumptions visible.

## References

- [Rebalance Timing Luck](https://www.thinknewfound.com/rebalance-timing-luck) — Newfound Research
- [Rebalance Timing Luck and GTAA Portfolios](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5230603) — Carlo Zarattini and Alberto Pagani
- [The Tranching Dilemma](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5747964) — Carlo Zarattini and Alberto Pagani
