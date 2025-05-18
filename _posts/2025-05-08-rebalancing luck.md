---
layout: post
title: "Rebalancing Timing Luck"
date: 2025-05-10
categories: [Quants]
---

Rebalance timing plays a big role in medium- to long-term strategies that don’t trade often. Shifting the execution day by just a few days can meaningfully impact performance — changing the exact positions held, and affecting returns, volatility, and drawdowns.


This issue is often referred to as *rebalance timing luck*: the variation in performance that comes purely from the day you happen to rebalance, even when the strategy and signals stay the same.

Others have explored this too. [Newfound Research](https://www.thinknewfound.com/rebalance-timing-luck) wrote a great piece highlighting how impactful this effect can be. And the [Concretum Group](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5230603) analyzed it in a GTAA context, showing that spreading rebalances out over time — instead of doing it all at once — can reduce timing risk and even lower turnover.

That got me curious: how much does timing luck affect my own long-short strategy? And could a more gradual rebalancing approach make it more stable, without changing the core logic?

## Setup

The strategy is a long-short market-neutral model based on LightGBM predictions (see [this earlier post](https://piinghel.github.io/quants/2025/02/20/lgbm.html)). It rebalances every three weeks, with the entire portfolio updated on a fixed weekday at the closing price. Since there are three possible starting weeks (offsets) and five weekdays, that gives us 15 possible rebalancing schedules.

I simulate all 15 combinations:
- 3 offsets × 5 weekdays = 15 setups  
- Each uses the same trained model and applies predictions available on that specific day  
- Signals, logic, and universe stay exactly the same  

Then, I compare this to a *tranching* setup — a common approach where the portfolio is divided into parts and rebalanced gradually. Here, the portfolio is split into three equal tranches. One-third is rebalanced each week, rotating through the offsets. Over three weeks, the full portfolio is still updated — just in smaller, smoother steps. This helps reduce sensitivity to any single day’s noise.



## Rebalancing Day Does Matter

Here’s the cumulative return of the 15 full-rebalance variants:


![Figure 1](/assets/tranching/all_perf_plots.png) 

**Figure 1:** Cumulative returns for each rebalancing schedule (15 variants).


And the table of results:

| Tranche           | Geometric Return | Volatility | Sharpe Ratio | Max Drawdown | Time Underwater |
|-------------------|------------------|------------|--------------|--------------|-----------------|
| offset=0, day=1   | 10.38%           | 6.58%      | 1.53         | 12.41%       | 548 days        |
| offset=0, day=2   | 10.10%           | 6.54%      | 1.50         | 14.77%       | 573 days        |
| offset=0, day=3   | 10.61%           | 6.54%      | 1.57         | 13.79%       | 582 days        |
| offset=0, day=4   | 12.10%           | 6.73%      | 1.73         | 13.19%       | 548 days        |
| offset=0, day=5   | 12.17%           | 6.91%      | 1.70         | 13.59%       | 369 days        |
| offset=1, day=1   | 12.53%           | 6.90%      | 1.75         | 12.35%       | 360 days        |
| offset=1, day=2   | 12.21%           | 6.97%      | 1.69         | 12.13%       | 387 days        |
| offset=1, day=3   | 12.30%           | 6.87%      | 1.72         | 10.70%       | 375 days        |
| offset=1, day=4   | 11.64%           | 6.70%      | 1.68         | 12.72%       | 360 days        |
| offset=1, day=5   | 11.62%           | 6.76%      | 1.66         | 14.76%       | 298 days        |
| offset=2, day=1   | 10.90%           | 6.50%      | 1.67         | 11.38%       | 248 days        |
| offset=2, day=2   | 11.27%           | 6.60%      | 1.56         | 12.56%       | 331 days        |
| offset=2, day=3   | 10.61%           | 6.60%      | 1.63         | 11.01%       | 275 days        |
| offset=2, day=4   | 10.99%           | 6.53%      | 1.63         | 13.10%       | 352 days        |
| offset=2, day=5   | 10.37%           | 6.45%      | 1.56         | 13.10%       | 593 days        |


**Table 1:** Performance metrics for each full-rebalance variant.



I was actually surprised by how much divergence there was. Even though all tranches follow the same model, returns varied quite a bit — from around 10.1% to 12.5% annually. Sharpe ratios ranged from 1.50 to 1.75, and some tranches spent hundreds of days longer in drawdown than others. These are meaningful differences for something as simple as shifting the rebalance day.

None of this comes from the model or the signal — it's purely due to small shifts in rebalance timing that compound over time. Even when overall performance looks stable, this kind of noise makes it harder to tell whether a change is genuinely better or just lucky on timing.




## Tranching: A Simple, Effective Fix

Instead of picking a single rebalancing day, we can average across them.

In the tranching setup, I split the portfolio into three equal parts. Each week, I rebalance one-third of the portfolio — always on the same weekday (say, every Wednesday) — but each tranche follows a different offset within the three-week cycle. So over three weeks, the full portfolio is refreshed, just not all at once.

This staggered execution spreads risk more evenly across time without changing the model or signals.

To analyze the results, I group performance by weekday and average across the three offsets. This gives a cleaner comparison to the previous “all-at-once” setup.

![Figure 2](/assets/tranching/tranched_perf_plots.png)  
**Figure 2:** Cumulative returns with tranching by weekday (averaged over offsets).

| Weekday | Geometric Return | Volatility | Sharpe Ratio | Max Drawdown | Time Underwater |
|---------|------------------|------------|--------------|--------------|-----------------|
| 1 (Mon) | 11.32%           | 6.08%      | 1.80         | 11.08%       | 370 days        |
| 2 (Tue) | 11.23%           | 6.04%      | 1.79         | 11.63%       | 301 days        |
| 3 (Wed) | 11.24%           | 6.08%      | 1.78         | 11.89%       | 299 days        |
| 4 (Thu) | 11.63%           | 6.06%      | 1.85         | 11.01%       | 303 days        |
| 5 (Fri) | 11.43%           | 6.11%      | 1.80         | 12.37%       | 364 days        |

**Table 2:** Tranche-averaged performance by weekday.


The improvements are actually quite solid. Sharpe ratios climb into the 1.78–1.85 range, with Friday and Thursday performing best. Volatility compresses to just above 6%, and drawdowns are generally smaller and recover more quickly. On the cumulative return chart, the dispersion tightens massively — the lines almost sit on top of each other, which wasn't the case before.

This isn’t just about higher returns — most of the gains come from smoother execution. By spreading out rebalances, you avoid abrupt shifts in exposure, which reduces noise and leads to more stable performance.

From a research perspective, this makes a big difference. It cuts down the randomness introduced by timing luck and makes it easier to tell whether a model change is actually improving things — or just benefiting from better timing.


## Why It Works

Tranching softens the impact of short-term shocks. A single full-book rebalance can pick up temporary price dislocations or liquidity gaps — injecting noise into an otherwise stable strategy. By spreading rebalancing over time, those effects average out.

The logic and signal stay exactly the same. The full portfolio still turns over every three weeks, just more gradually. That reduces sensitivity to any one day’s conditions, without changing overall turnover.

There’s also a subtle benefit on the signal side. In the standard setup, you only act on the model’s predictions once every three weeks. With tranching, you fold in new predictions each week — even if it’s only on a third of the capital. That introduces a kind of temporal diversification and makes the strategy more responsive to new information.

## A Few Trade-Offs and Extra Benefits

Tranching isn’t free. Weekly rebalancing means running the pipeline more often, sending more orders, and keeping an eye on execution regularly. That adds a bit of overhead — especially when some trades are small and barely move the portfolio.

But in practice, it’s felt worth it. Not just in research — even in live runs, it makes the strategy feel more stable and less twitchy around timing noise.

I also came across something interesting in the GTAA literature: tranching might reduce turnover and transaction costs. I’m not entirely sure why — maybe it avoids large shifts or cancels out trades across tranches. Still figuring that part out. If you’ve got ideas or experience with it, let me know — I’m curious.

And a small bonus: by updating just a slice each week, you keep injecting fresh signal without going all-in. The portfolio stays a bit more responsive without overtrading.



## Final Thoughts

What started as a small curiosity around rebalancing schedules turned into a strong case for using tranching by default.

The signal and logic don’t change — but the results become cleaner and more stable. That’s especially helpful when evaluating model tweaks, since it reduces noise from execution timing.

I’ll be using this setup going forward for any strategy that rebalances on a fixed cycle. It’s simple, effective, and makes the whole process easier to trust.



