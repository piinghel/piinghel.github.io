---
layout: post
title: "Reducing Rebalancing Timing Risk with Tranching"
date: 2025-05-10
categories: [Quants]
---

## Introduction

Rebalance timing plays a big role in medium- to long-term strategies that don't trade often. Shifting the execution day by just a few days can meaningfully impact performance, changing the exact positions held, and affecting returns, volatility, and drawdowns.

This issue is often referred to as *rebalance timing luck*: the variation in performance that comes purely from the day you happen to rebalance, even when the strategy and signals stay the same.

Others have explored this too. [Newfound Research](https://www.thinknewfound.com/rebalance-timing-luck) wrote a great piece highlighting how impactful this effect can be. And the [Concretum Group](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5230603) analyzed it in a GTAA context, showing that spreading rebalances out over time, instead of doing it all at once, can reduce timing risk and even lower turnover.

That got me curious: how much does timing luck affect my own long-short strategy? And could a more gradual rebalancing approach make it more stable, without changing the core logic?

## Setup

The strategy is a long-short market-neutral model based on LightGBM predictions (see [this earlier post](https://piinghel.github.io/quants/2025/02/20/lgbm.html)). It rebalances every three weeks, with the entire portfolio updated on a fixed weekday at the closing price. Since there are three possible starting weeks (offsets) and five weekdays, that gives us 15 possible rebalancing schedules.

I simulate all 15 combinations:
- 3 offsets × 5 weekdays = 15 setups  
- Each uses the same trained model and applies predictions available on that specific day  
- Signals, logic, and universe stay exactly the same  

Then, I compare this to a *tranching* setup, a common approach where the portfolio is divided into parts and rebalanced gradually. Here, the portfolio is split into three equal tranches. One-third is rebalanced each week, rotating through the offsets. Over three weeks, the full portfolio is still updated, just in smaller, smoother steps. This helps reduce sensitivity to any single day’s noise.



## Rebalancing Day Does Matter

Here's the cumulative return of the 15 full-rebalance variants:


![Figure 1](/assets/tranching/all_perf_plots.png)  
<p class="figure-caption"><strong>Figure 1:</strong> Cumulative returns for each rebalancing schedule (15 variants).</p>


And the table of results:

<div style="overflow-x: auto;">
<table style="width: 100%; border-collapse: collapse; margin: 1em 0;">
<thead>
<tr>
<th style="padding: 0.6em; text-align: left; border-bottom: 2px solid #333;">Tranche</th>
<th style="padding: 0.6em; text-align: center; border-bottom: 2px solid #333;">Geometric Return</th>
<th style="padding: 0.6em; text-align: center; border-bottom: 2px solid #333;">Volatility</th>
<th style="padding: 0.6em; text-align: center; border-bottom: 2px solid #333;">Sharpe Ratio</th>
<th style="padding: 0.6em; text-align: center; border-bottom: 2px solid #333;">Max Drawdown</th>
<th style="padding: 0.6em; text-align: center; border-bottom: 2px solid #333;">Time Underwater</th>
</tr>
</thead>
<tbody>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">offset=0, day=1</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">10.38%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.58%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.53</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">12.41%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">548 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">offset=0, day=2</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">10.10%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.54%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.50</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">14.77%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">573 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">offset=0, day=3</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">10.61%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.54%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.57</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">13.79%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">582 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">offset=0, day=4</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">12.10%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.73%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.73</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">13.19%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">548 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">offset=0, day=5</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">12.17%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.91%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.70</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">13.59%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">369 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">offset=1, day=1</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">12.53%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.90%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.75</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">12.35%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">360 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">offset=1, day=2</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">12.21%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.97%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.69</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">12.13%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">387 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">offset=1, day=3</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">12.30%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.87%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.72</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">10.70%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">375 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">offset=1, day=4</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">11.64%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.70%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.68</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">12.72%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">360 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">offset=1, day=5</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">11.62%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.76%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.66</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">14.76%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">298 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">offset=2, day=1</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">10.90%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.50%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.67</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">11.38%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">248 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">offset=2, day=2</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">11.27%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.60%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.56</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">12.56%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">331 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">offset=2, day=3</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">10.61%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.60%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.63</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">11.01%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">275 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">offset=2, day=4</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">10.99%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.53%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.63</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">13.10%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">352 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">offset=2, day=5</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">10.37%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.45%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.56</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">13.10%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">593 days</td></tr>
<tr style="background: #f5f5f5; font-weight: bold;"><td style="padding: 0.6em;"><strong>Mean</strong></td><td style="padding: 0.6em; text-align: center;"><strong>11.32%</strong></td><td style="padding: 0.6em; text-align: center;"><strong>6.68%</strong></td><td style="padding: 0.6em; text-align: center;"><strong>1.64</strong></td><td style="padding: 0.6em; text-align: center;"><strong>12.77%</strong></td><td style="padding: 0.6em; text-align: center;"><strong>413 days</strong></td></tr>
</tbody>
</table>
</div>
<p class="table-caption"><strong>Table 1:</strong> Performance metrics for each full-rebalance variant.</p>



I was actually surprised by how much divergence there was. Even though all variants follow the same model, returns varied quite a bit, from around 10.1% to 12.5% annually. Sharpe ratios ranged from 1.50 to 1.75, and some variants spent hundreds of days longer in drawdown than others. These are meaningful differences for something as simple as shifting the rebalance day.

None of this comes from the model or the signal. It's purely due to small shifts in rebalance timing that compound over time. Even when overall performance looks stable, this kind of noise makes it harder to tell whether a change is genuinely better or just lucky on timing.




## Tranching: A Simple, Effective Fix

Instead of picking a single rebalancing day, we can average across them.

In the tranching setup, I split the portfolio into three equal parts. Each week, I rebalance one-third of the portfolio, always on the same weekday (say, every Wednesday), but each tranche follows a different offset within the three-week cycle. So over three weeks, the full portfolio is refreshed, just not all at once.

This staggered execution spreads risk more evenly across time without changing the model or signals.

To analyze the results, I group performance by weekday and average across the three offsets. This gives a cleaner comparison to the previous "all-at-once" setup.

![Figure 2](/assets/tranching/tranched_perf_plots.png)  
<p class="figure-caption"><strong>Figure 2:</strong> Cumulative returns with tranching by weekday (averaged over offsets).</p>

<div style="overflow-x: auto;">
<table style="width: 100%; border-collapse: collapse; margin: 1em 0;">
<thead>
<tr>
<th style="padding: 0.6em; text-align: left; border-bottom: 2px solid #333;">Weekday</th>
<th style="padding: 0.6em; text-align: center; border-bottom: 2px solid #333;">Geometric Return</th>
<th style="padding: 0.6em; text-align: center; border-bottom: 2px solid #333;">Volatility</th>
<th style="padding: 0.6em; text-align: center; border-bottom: 2px solid #333;">Sharpe Ratio</th>
<th style="padding: 0.6em; text-align: center; border-bottom: 2px solid #333;">Max Drawdown</th>
<th style="padding: 0.6em; text-align: center; border-bottom: 2px solid #333;">Time Underwater</th>
</tr>
</thead>
<tbody>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">1 (Mon)</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">11.32%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.08%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.80</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">11.08%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">370 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">2 (Tue)</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">11.23%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.04%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.79</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">11.63%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">301 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">3 (Wed)</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">11.24%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.08%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.78</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">11.89%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">299 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">4 (Thu)</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">11.63%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.06%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.85</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">11.01%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">303 days</td></tr>
<tr><td style="padding: 0.6em; border-bottom: 1px solid #eee;">5 (Fri)</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">11.43%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">6.11%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.80</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">12.37%</td><td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">364 days</td></tr>
<tr style="background: #f5f5f5; font-weight: bold;"><td style="padding: 0.6em;"><strong>Mean</strong></td><td style="padding: 0.6em; text-align: center;"><strong>11.37%</strong></td><td style="padding: 0.6em; text-align: center;"><strong>6.07%</strong></td><td style="padding: 0.6em; text-align: center;"><strong>1.80</strong></td><td style="padding: 0.6em; text-align: center;"><strong>11.60%</strong></td><td style="padding: 0.6em; text-align: center;"><strong>327 days</strong></td></tr>
</tbody>
</table>
</div>
<p class="table-caption"><strong>Table 2:</strong> Tranche-averaged performance by weekday.</p>


Comparing the means tells the story clearly: average return is essentially unchanged (11.32% to 11.37%), but volatility drops from 6.68% to 6.07%, max drawdown improves from 12.77% to 11.60%, and Sharpe ratio rises from 1.64 to 1.80. Time underwater falls by nearly 90 days.

The key insight: tranching doesn't generate extra return. It delivers the same return with less risk. By spreading rebalances across time, you smooth out the noise from any single day's conditions. The cumulative return chart makes this visible: the lines almost sit on top of each other, which wasn't the case before.

From a research perspective, this matters a lot. It cuts down the randomness from timing luck, making it easier to tell whether a model change is actually improving things or just benefiting from better timing.


There's also a subtle benefit on the signal side: with tranching, you fold in new predictions each week instead of once every three weeks. That introduces a kind of temporal diversification and makes the strategy more responsive to new information.

## Trade-Offs

Tranching isn't free. Weekly rebalancing means running the pipeline more often, sending more orders, and keeping an eye on execution regularly. That adds overhead, especially when some trades are small.

But in practice, it's felt worth it. Not just in research, but even in live runs, the strategy feels more stable and less twitchy around timing noise.

I also came across something interesting in the GTAA literature: tranching might reduce turnover and transaction costs. I'm not entirely sure why, maybe it avoids large shifts or cancels out trades across tranches. If you've got ideas or experience with it, let me know.



## Conclusion

What started as a small curiosity around rebalancing schedules turned into a strong case for using tranching by default. The results are cleaner and more stable, which is especially helpful when evaluating model tweaks.

I'll be using this setup going forward for any strategy that rebalances on a fixed cycle. It's simple, effective, and makes the whole process easier to trust.

## References

- [Rebalance Timing Luck](https://www.thinknewfound.com/rebalance-timing-luck) - Newfound Research. A clear explanation of how rebalance timing affects performance.

- [Rebalance Timing Luck and GTAA Portfolios](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5230603) - Zarattini & Pagani, Concretum Group. Shows that spreading rebalances over time can reduce timing risk and even lower turnover in a GTAA context.

- [The Tranching Dilemma: A Cost-Aware Approach to Mitigate Rebalance Timing Luck in Factor Portfolios](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5747964) - Zarattini & Pagani, Concretum Group (2025). A follow-up paper that develops a framework for optimal tranching under realistic transaction costs. Key finding: while tranching consistently reduces RTL, its net benefit depends on AUM. For large investors it's clearly worth it; for smaller investors the extra trading costs can outweigh the benefits. Worth reading if you're thinking about implementation.


