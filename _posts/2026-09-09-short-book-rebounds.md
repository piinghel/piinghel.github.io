---
layout: post
title: "Performance Attribution, Part 2: Why the Short Book Struggles in Rebounds"
description: "Higher-beta, harder-hit shorts rebound faster than the longs across many market recoveries."
permalink: /quants/short-book-rebounds.html
toc: true
show_date: false
date: 2026-09-09
categories: ["Portfolio management"]
article_label: Performance attribution · Part 2 of 3
series_previous: /quants/portfolio-attribution.html
series_next: /quants/managing-rebound-risk.html
---

<p class="article-summary">The shorts held higher-beta, more volatile stocks than the longs at the 2009 and 2020 lows. That helped during declines and hurt during rebounds. The imbalance also appears across other recoveries.</p>

In [part 1](/quants/portfolio-attribution.html), the shorts reduced daily
portfolio fluctuations while losing money overall. Here I want to understand
where their protection failed. Did the two sides hold stocks with very
different rebound potential?

I follow the same portfolio from September 1998 to May 2026. Contributions
use fixed-notional P&L points; one point is 1% of strategy notional.
Net P&L deducts 5 basis points per dollar traded. Borrow, financing and market
impact would require additional cost estimates.

## Protection during the decline, losses during the rebound

The strategy's two deepest drawdowns were **2008–09** and **2020–21**, both just over
**16 P&L points**. I split each at the market low to distinguish losses during
the decline from losses during the recovery.

Table 1 covers the strategy's peak-to-trough windows: 30 July 2008 to
16 September 2009, and 21 February 2020 to 27 January 2021. The market lows
were **9 March 2009** and **23 March 2020**. These dates are identified with
hindsight to divide each episode into decline and recovery.

<div markdown="1">
<p class="table-caption"><strong>Table 1: Losses continued after the market bottomed.</strong> Fixed-notional P&amp;L points, excluding the strategy's peak day. The decline includes the market-low session; the rebound follows it. Longs and shorts are gross; net includes costs.</p>

| Phase | Sessions | Longs | Shorts | Net |
| :--- | ---: | ---: | ---: | ---: |
| 2008–09 decline | 152 | −36.28 | +30.63 | −6.18 |
| 2009 rebound | 133 | +39.59 | −49.14 | −10.14 |
| 2020 decline | 21 | −39.95 | +30.74 | −9.32 |
| 2020–21 rebound | 214 | +38.41 | −44.19 | −6.74 |
{: .research-table .comparison-table .attribution-table }

</div>

**The strategy lost in both phases, in both episodes.** Shorts helped during
the declines, offsetting part of the long losses. During the rebounds,
short losses exceeded long gains. Figure 1 shows when that protection reversed.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/market-phases" mobile="/assets/portfolio-attribution/market-phases_mobile" version="4" alt="Benchmark levels above cumulative long, short and net P&L, split at the March 2009 and March 2020 market lows. The strategy continues losing during the rebounds." %}
</div>
<p class="figure-caption"><strong>Figure 1: The market rebounded while the strategy lost further ground.</strong> Each window runs from the strategy's peak to its trough. Shading ends at the market low. Benchmark price indices start at 100; portfolio contributions use fixed-notional P&amp;L points on separate axes.</p>

The **2009 rebound accounted for more of that episode's loss**. In 2020, the initial
decline was much sharper: **9.32 points in 21 sessions**, followed by another
**6.74 over 214 sessions**. Both the initial decline and the rebound contributed
to the losses.

Was I simply holding on to the old shorts? Table 2 separates names that were
short at the market low from additions during the rebound.

<div markdown="1">
<p class="table-caption"><strong>Table 2: New names also contributed to the rebound losses.</strong> Gross short P&amp;L points from after the market low through the strategy trough. Groups include subsequent resizing, exits and reentries.</p>

| Short-book names | 2009 rebound | 2020–21 rebound |
| :--- | ---: | ---: |
| Short at the market low | −20.90 | −23.12 |
| Rebound additions | −28.24 | −21.08 |
| **Total** | **−49.14** | **−44.19** |
{: .research-table .comparison-table .attribution-table }

</div>

Names absent from the short book at the low accounted for **57.5%** of its
2009 rebound loss and **47.7%** in 2020–21. The five worst short contributors
explained only **12.4%** and **8.8%** of the respective losses.
The losses were spread across many stocks, including names added during the
recovery. That makes a shared exposure worth investigating.

The positions also matter when looking at an individual stock's price chart.
Zscaler was the largest short entering the 2020 rebound. Its price more than
tripled between the market low and January 2021, but the strategy closed
the short in early June. The position lost **0.12 P&L points during the rebound**;
much of the stock's later rise happened after the strategy had left it.

{% include attribution-stock-examples.html %}

The beta and volatility tilts helped during both market declines, then hurt
during both rebounds. Figure 2 shows their contributions over each complete
drawdown, alongside the residual and other terms.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/drawdown-factors" mobile="/assets/portfolio-attribution/drawdown-factors_mobile" version="3" alt="The 2008–09 and 2020–21 attribution side by side: beta and residual lead the first loss; residual and volatility lead the second." %}
</div>
<p class="figure-caption"><strong>Figure 2: Similar total losses, different factor contributions.</strong> Peak-to-trough P&amp;L points. Each panel includes factor terms, residual, uncovered holdings and costs.</p>

In **2008–09**, beta was the largest losing style at **−6.55 points**, and the
residual lost **6.14**. In **2020–21**, volatility lost **8.10 points** and the
residual **11.41**. Other contributions partly offset those losses.

Inside those totals, beta went from **+3.32 during the decline to −9.87 during
the rebound** in 2008–09, and from **+1.27 to −5.80** in 2020–21. The negative beta exposure favoured lower-beta stocks as higher-beta stocks began to outperform. [Part 1](/quants/portfolio-attribution.html#follow-exposure-and-payoff-together) shows the daily exposure × payoff calculation.

## The stocks on each side

The holdings make the imbalance easier to see. Figure 3
compares the stocks held on each side as the recoveries
began. **In both episodes, the shorted stocks had higher estimated market
betas, larger prior losses and higher volatility than the longs.**

<div class="research-figure responsive-figure" id="rebound-holdings">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/rebound-holdings" mobile="/assets/portfolio-attribution/rebound-holdings_mobile" version="1" alt="At the 2009 low, long versus short stock beta was 0.89 versus 1.11; at the 2020 low, 0.86 versus 1.03. Shorts also had larger prior losses and higher volatility in both episodes." %}
</div>
<p class="figure-caption"><strong>Figure 3: The shorts held riskier stocks than the longs.</strong> Average stock characteristics, weighted by position size within each book, entering the first rebound session. Measurements end at the market lows of 9 March 2009 and 23 March 2020. Beta uses up to 252 daily returns against the Russell 1000 (126 minimum); prior return uses 126 sessions; volatility uses 21 sessions, annualized.</p>

This helps explain the rebound losses. A rising market tends to lift
higher-beta stocks more, so their recovery hurts the short book while the
lower-beta longs participate less. In 2020, the estimated stock betas were
**0.86 for longs and 1.03 for shorts**. Position sizes still determine the
portfolio's overall sensitivity: the chart compares the stocks within each
book, before allowing for the books' different sizes and opposite signs.
Beta is only part of the explanation, alongside the
volatility tilt and residual losses above.

Momentum can add to the same bet. During a sell-off, a stock can rank as a
winner simply because it fell less than the others. A momentum signal may
therefore favour the defensive stocks the low-volatility tilt already favours,
while both point away from the harder-hit stocks. This resembles the rebound
mechanism in Daniel and Moskowitz's *Momentum Crashes*. During the 2009 rebound,
the portfolio's momentum
exposure changed sign and its fitted momentum contribution was positive,
while the low-volatility tilt continued to hurt.

## Does the pattern repeat?

The two largest strategy drawdowns helped form the hypothesis. To see how
often the same imbalance appeared elsewhere, I identified **11 market
drawdowns of at least 10%** in the available history and followed the first
63 sessions after each low. A new drawdown episode starts only after the
previous market peak has been regained; intervening sell-offs belong to the
same episode. Every low is identified in hindsight.

The long book is usually larger than the short book, so comparing their
P&L totals alone mixes stock performance with position size. For this check,
I first measure the return of the stocks on each side per unit of that
side's gross exposure. For book $\ell$, with gross exposure
$A_{\ell,t}=\sum_{i\in\ell}|w_{i,t^-}|$, the measure is

$$
G_\ell(H)=100\sum_{t=1}^{H}
\frac{\sum_{i\in\ell}|w_{i,t^-}|r_{i,t}}{A_{\ell,t}}.
$$

This follows the changing positions and adds daily returns. A price rise
counts as a stock gain on either side; it hurts the portfolio when the stock
is short. I compare $G_{\mathrm{short}}-G_{\mathrm{long}}$, then
look separately at the actual portfolio P&L over exactly the same sessions.

Figure 4 starts with all 11 recoveries. Select an episode to follow the two
books through time, then choose 21, 63 or 126 sessions and move the date slider.
At 63 sessions, **shorted stocks gained more in 9 of 11
episodes**, but the median gap was **2.89 percentage points**. The **41.19-point
gap in 2009** was much larger than the usual episode; the mean gap of
**6.42 points** gives that extreme event more influence.

{% include attribution-recovery-explorer.html figure="4" %}

The portfolio lost money in **4 of the 11** 63-session windows. In the first 63 sessions
of the 2020 recovery, for example, shorted stocks gained **48.15% per unit
of exposure**, versus **31.80%** for the longs. But the larger long book
earned **17.18 P&L points**, while shorts lost **16.54**. After costs, the
portfolio was still up **0.43 points**. The **6.74-point loss** reported
earlier covers the much longer 214-session recovery through January 2021.
The portfolio's path matters as well as the stocks' relative rebound.

I also checked shorter and longer windows around the same lows (Table 3).
At 21 sessions, shorts were ahead in **9 of 11** episodes. By 126 sessions,
that fell to **3 of 11**, and the median gap had turned negative.

<div markdown="1">
<p class="table-caption"><strong>Table 3: The imbalance is more common early in the recovery.</strong> The same 11 lows at each horizon. Gap = short-stock gains minus long-stock gains per unit of exposure, in percentage points. Net losses use actual portfolio P&amp;L after saved trading costs.</p>

| Sessions after low | Shorts gained more | Median gap | Net portfolio losses |
| ---: | ---: | ---: | ---: |
| 21 | 9 / 11 | +2.73 | 4 / 11 |
| 63 | 9 / 11 | +2.89 | 4 / 11 |
| 126 | 3 / 11 | −2.49 | 1 / 11 |
{: .research-table .comparison-table .attribution-table }

</div>

This points towards an **early-recovery vulnerability**, with a few severe
episodes. Because the positions change throughout these windows, the longer-horizon improvement
could reflect different stocks as well as a change in market behaviour.
The horizons overlap.


## What this changes

The holdings and fitted contributions point to a shared vulnerability:
defensive longs face higher-beta, more volatile shorts when the market
rebounds. Momentum can reinforce that positioning during a sell-off, although
its exposure changed direction in 2009 while the low-volatility tilt persisted.

I want to preserve useful short signals and decline protection while reducing
that concentration. In [part 3](/quants/managing-rebound-risk.html), I compare
the exposure limits and daily volatility-scaling rules I tested, including
their costs and results across these recoveries.

## References

Kent Daniel and Tobias Moskowitz, [*Momentum Crashes*](https://www.kentdaniel.net/papers/published/jfe_16.pdf),
*Journal of Financial Economics*, 2016, Sections 2–3. Their rebound mechanism
motivates the comparison with the observed holdings here.
