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

The retained archive preserves the schedule grid and summary results, but not
enough daily detail to recompute them, so I use the evidence descriptively. The
chart axes indicate a sample of roughly 1999–2025; the exact endpoints were not
retained.

<div class="research-figure rebalancing-figure">
  <img src="/assets/tranching/all_perf_plots.png" alt="Cumulative wealth on a logarithmic scale for fifteen full-rebalance schedules, with two terminal extremes highlighted after the backtest" width="1800" height="1200" loading="lazy" decoding="async">
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Cumulative wealth for 15 full-rebalance schedules; highest and lowest terminal paths highlighted ex post; log scale, start = 1.</p>

The paths separate gradually rather than around one isolated event. Small
differences in signal dates and holdings accumulate into large differences in
terminal wealth. The chart shows schedule sensitivity; it does not establish
that any schedule has a persistent informational advantage.

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

<p class="figure-caption"><strong>Table 1:</strong> Dispersion across the 15 full-rebalance schedules.</p>

Annualized geometric return differs by 2.43 percentage points between the best and worst
schedules, while the Sharpe ratio ranges from 1.50 to 1.75. The widest gap is in
time underwater: 248 days for one schedule and 593 for another. Reporting only
one of these backtests would hide a 2.43-point annualized-return spread and a
345-day underwater-duration gap around an arbitrary implementation choice.
Those differences are large enough to matter operationally, but their net
economic value is unknown because the cost treatment was not preserved. The
result does not say which weekday or offset will be best next time; the realized
ordering could itself be luck.

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

<p class="figure-caption"><strong>Table 2:</strong> Performance of the three-tranche portfolios by weekday.</p>

Across the saved summaries, the five tranched portfolios have a mean annualized
geometric return of 11.37%, versus 11.32% across the 15 full-rebalance
schedules. Mean volatility is 6.07% versus 6.68%, mean maximum drawdown is
11.60% versus 12.77%, and mean maximum underwater duration is 327 versus 413
days. The descriptive mean Sharpe is 1.80 versus 1.64. These are descriptive
differences, not isolated effects of timing diversification.

The observed dispersion also narrows. The geometric-return range contracts
from 2.43 to 0.40 percentage points, the maximum-drawdown range from 4.07 to
1.36 points, and the underwater-duration range from 345 to 71 days. These are
descriptive ranges across 15 full schedules and five overlapping tranched
portfolios, not independent or like-for-like statistical samples.

Those differences are potentially meaningful in this sample, especially the
roughly 9% reduction in volatility and 86-day reduction in maximum underwater
duration. Their economic value after costs is unknown. The five tranched return
estimates still span 11.23% to 11.63%, however, and maximum drawdown spans
11.01% to 12.37%. Tranching removes the starting-week choice by combining the
three offsets; it does not remove weekday sensitivity. No sampling-uncertainty
estimate or independent-period replication survives, so neither the lower risk
nor the narrower ranges are guaranteed to persist.

The interpretation is that overlapping sleeves diversify when the existing
signal enters the portfolio, reducing the risk of committing all capital on
one arbitrary date. It remains an interpretation because the implementation
also changes how quickly new information reaches the book.

## What the comparison does not isolate

Three tranches reduce starting-week sensitivity, but weekday choice remains.
Using more sleeves could spread execution across weekdays as well, at the cost
of more frequent runs, smaller orders, and more operational state to manage.
There is no reason to assume that adding sleeves keeps helping indefinitely.

There is a second distinction. The tranched portfolio incorporates a fresh set
of predictions each week, whereas the full-rebalance portfolio waits three
weeks before replacing every position. Tranching therefore changes signal
freshness as well as diversifying timing. The experiment shows that the complete
tranched implementation has less dispersion and lower realized risk in this
sample; it does not attribute the improvement solely to timing diversification.
A cleaner identification test would hold the prediction vintage fixed while
changing only the execution schedule, then separately test the value of fresher
weekly predictions.

The retained research archive contains the two return-path charts and the
summary metrics reported here, but not the daily schedule returns or the
figure-generation code. The saved tables are internally consistent with the
older detailed table in repository history, and the charts visually agree with
their dispersion, but the statistics cannot be recomputed from raster images.
I also cannot recompute turnover, inspect individual trades, or run new tests.
The results do not document whether costs were included or how they were
defined. They should therefore be treated as evidence about timing dispersion
with undocumented cost treatment, not as implementation-grade return estimates.

Costs can change the preferred number of sleeves. Smaller orders may face
minimum fees and fixed operational overhead, while spreading a large order can
reduce market impact. Signal freshness can also improve as sleeves rebalance
more often, but more frequent decisions create more opportunities to trade.
The practical choice should be based on net results using current holdings,
turnover, spread and impact estimates, borrow costs, and the operational cost of
maintaining each sleeve—not on gross backtest smoothness alone.

## Conclusion

The experiment changes how I would report and run a fixed-cycle strategy. A
single rebalance schedule is one draw from a wider set of plausible outcomes,
so it is not enough evidence on its own. Testing the full timing grid makes that
uncertainty visible.

Three weekly tranches are a practical hypothesis. In the saved summaries, the
tranched portfolios exhibit nearly unchanged mean return, 0.61 percentage
points less mean volatility, 1.17 points less mean drawdown, and 86 fewer mean
underwater days. The trade-off is a more frequent and operationally involved
implementation. Fresher predictions and undocumented costs prevent attributing
those differences to timing diversification alone, while the missing daily
archive prevents a realistic cost replay.
I would use three sleeves as the working hypothesis, not a universal optimum.
The most useful next test is a matched signal-vintage experiment across several
sleeve counts, evaluated net of turnover, spreads, market impact, borrow, and
operational constraints.

## References

- [Rebalance Timing Luck](https://www.thinknewfound.com/rebalance-timing-luck) — Newfound Research
- [Global Tactical Asset Allocation: Updated Results and Real-Market Implementation Using Python and IBKR](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5230603) — Mohamed Gabriel, Alberto Pagani, and Carlo Zarattini
- [The Tranching Dilemma](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5747964) — Carlo Zarattini and Alberto Pagani
