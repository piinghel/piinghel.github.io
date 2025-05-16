---
layout: post
title: "Rebalancing Luck"
date: 2025-05-10
categories: [Quants]
---

# Todo
 - Can lower turnover and transaction costs but don't fully understand how
 - Also refer to the the original article of concretum research
 - Make writing style slightly more personal. Write form the I and sometimes give your own opinion.

# Rebalancing Schedules, Tranching, and Cleaner Portfolio Paths

In most backtests, the rebalancing schedule is hardcoded — for example, every three weeks on a Friday — and rarely questioned. But that choice can have a real impact on performance. Shifting the execution day by just a few days can change inputs, alter positions, and affect returns, volatility, and drawdowns.

What also matters is how much of the portfolio you rebalance at once. Rebalancing the full book in one shot can amplify path dependency. A more gradual approach — rebalancing just one-third each week — might lead to smoother results without changing the model at all.

In this post, I look at both: how different rebalancing schedules affect performance, and how tranching improves stability across the board.

## Setup

The strategy is a long-short equity model that rebalances every three weeks, always on a single weekday. Since there are three possible offset weeks and five weekdays, that gives 15 potential rebalancing schedules.

I simulate all 15 variants. The only difference is the day on which the portfolio is rebalanced:

- 3 offset weeks × 5 weekdays = 15 combinations
- Each run uses the same trained model, applied using the predictions available on that day
- The signals, logic, and asset universe remain unchanged

In the base case, I rebalance the entire portfolio once every 3 weeks — for example, always on Friday of offset week 0.

Then I compare it to a tranching setup: the portfolio is split into three parts, and one-third is rebalanced each week. Over a three-week cycle, the full portfolio is still updated — just more gradually. This smoother execution path helps reduce sensitivity to any one day’s noise.

## Rebalancing Day Does Matter

Here’s the cumulative return of the 15 full-rebalance variants:


![Figure 1](/assets/tranching/all_perf_plots.png) 

**Figure 1:** Cumulative returns for each rebalancing schedule (15 variants).


And the table of results:

| Tranche           | Geometric Return | Volatility | Modified Sharpe | Max Drawdown | Time Underwater |
|-------------------|------------------|------------|-----------------|--------------|-----------------|
| offset=0, day=1   | 11.67%           | 6.56%      | 1.78            | 9.79%        | 375             |
| offset=0, day=2   | 11.72%           | 6.61%      | 1.77            | 12.08%       | 314             |
| offset=0, day=3   | 11.25%           | 6.56%      | 1.71            | 13.27%       | 253             |
| offset=0, day=4   | 12.73%           | 6.63%      | 1.92            | 11.98%       | 236             |
| offset=0, day=5   | 12.79%           | 6.76%      | 1.89            | 15.54%       | 264             |
| offset=1, day=1   | 12.52%           | 6.71%      | 1.86            | 14.75%       | 569             |
| offset=1, day=2   | 12.83%           | 6.74%      | 1.90            | 13.23%       | 269             |
| offset=1, day=3   | 12.18%           | 6.65%      | 1.83            | 11.92%       | 251             |
| offset=1, day=4   | 11.16%           | 6.57%      | 1.70            | 10.80%       | 330             |
| offset=1, day=5   | 12.95%           | 6.53%      | 1.98            | 10.89%       | 236             |
| offset=2, day=1   | 12.29%           | 6.60%      | 1.88            | 10.17%       | 297             |
| offset=2, day=2   | 11.43%           | 6.47%      | 1.77            | 11.42%       | 266             |
| offset=2, day=3   | 11.34%           | 6.61%      | 1.72            | 10.70%       | 578             |
| offset=2, day=4   | 11.31%           | 6.54%      | 1.73            | 10.14%       | 341             |
| offset=2, day=5   | 11.28%           | 6.57%      | 1.72            | 14.28%       | 608             |

**Table 1:** Performance metrics for each full-rebalance variant.



I found that returns were fairly stable across rebalancing schedules, which honestly surprised me a bit. I expected more divergence. That said, there’s still a meaningful spread — modified Sharpe ratios range from 1.71 to 1.98, and some variants spent quite a bit longer in drawdown than others. It’s not huge, but it’s enough to notice. And none of it comes from the model itself — it’s just small shifts in execution timing that end up compounding over time.


## Tranching: A Simple, Effective Fix

Instead of picking one rebalancing day, we can average across them.

In the tranching setup, one-third of the portfolio is rebalanced each week, rotating through all three offsets. The full portfolio still turns over every 3 weeks, but in a staggered way.

Then, for interpretability, I group results by weekday, averaging across the three offsets.


![Figure 2](/assets/tranching/tranched_perf_plots.png) 
**Figure 2:** Cumulative returns with tranching by weekday (averaged over offsets).

| Weekday | Geometric Return | Volatility | Modified Sharpe | Max Drawdown | Time Underwater |
|---------|------------------|------------|-----------------|--------------|-----------------|
| 1 (Mon) | 12.18%           | 6.06%      | 2.01            | 11.30%       | 388             |
| 2 (Tue) | 12.02%           | 6.06%      | 1.98            | 12.23%       | 300             |
| 3 (Wed) | 11.62%           | 6.07%      | 1.91            | 11.59%       | 262             |
| 4 (Thu) | 11.73%           | 6.05%      | 1.94            | 10.82%       | 265             |
| 5 (Fri) | 12.34%           | 6.06%      | 2.04            | 12.80%       | 364             |

**Table 2:** Tranche-averaged performance by weekday.



The improvements are not just cosmetic. Modified Sharpe ratios move up and stabilize around 1.91, 2.04. Volatility compresses, especially compared to the 6.5–6.9% range seen earlier. Drawdowns get shallower and spend less time underwater.

This doesn’t happen because we’re adding return. It happens because we’re executing more evenly, avoiding sharp jumps.

## Why It Works


Tranching reduces path dependency. A single full-book rebalance can reflect one-off shocks, price dislocations, or liquidity gaps — all of which inject noise into a strategy that’s otherwise stable.

By spreading rebalancing over time, you soften those shocks. You’re still following the model, just in a way that filters out randomness from any specific day. The full portfolio is still turned over every three weeks, so turnover doesn’t increase — but transitions are smoother and less vulnerable to execution timing.

There’s also an effect on the signal itself. In the standard setup, you only express the model’s predictions once every three weeks. With tranching, you use the most recent predictions each week — even though you're only rebalancing part of the capital. That means the portfolio reflects more prediction points, more frequently, and benefits from a kind of temporal diversification across model outputs. That added reactivity may also contribute to the improvement in Sharpe ratios.


## A Few Trade-Offs and Extra Benefits


One thing to watch out for is execution complexity. Rebalancing every week means running the pipeline and sending orders more often. It’s not just the code — it’s the extra monitoring, mental overhead, and operational stress that comes with doing something three times instead of once. And if some positions are small, the trades might not even be worth it. Whether that matters depends on the signal structure and execution setup — but it’s worth keeping in mind.

That said, I’ve found tranching to be surprisingly helpful in research. By smoothing out the noise from timing, it gives a cleaner view of the strategy’s true performance. That makes it easier to evaluate whether a new feature or model change actually adds value — instead of just getting lucky on a rebalance date.

There’s also a small benefit I didn’t expect at first. While we still rebalance each slice only once every three weeks, we use the most recent model predictions each week. So we’re injecting new signal into the portfolio every week — just on a fraction of the AUM. That adds a bit of temporal diversification and keeps the portfolio more responsive without needing to go all-in.


## Final Thoughts


This started as a quick curiosity around rebalancing schedules, but it turned into a clear case for using tranching by default.

It makes the strategy more stable and less path-dependent. The signal stays the same. The logic stays the same. But the outcome gets cleaner.

For research purposes, that clarity really helps. When adding a new feature or modifying a signal, it becomes easier to see if we actually improved things.

I’ll be using this setup going forward for any model that rebalances in fixed cycles. It’s simple, and it works.


