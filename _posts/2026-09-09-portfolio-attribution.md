---
layout: post
title: "Understanding Your P&L"
description: "What the long and short books earned, and why their protection broke down during market recoveries."
permalink: /quants/portfolio-attribution.html
toc: true
show_date: false
date: 2026-09-09
categories: ["Portfolio management"]
---

<p class="article-summary">The shorts reduced the portfolio's daily fluctuations, but their protection reversed during market recoveries. I use attribution to understand that trade-off.</p>

A profitable backtest leaves me with a practical question: which risks were
worth taking? My long–short strategy made money overall, but the short book
lost money across the full history. Before changing it, I want to understand
both the protection it provided and the losses it created.

I'll use the strategy from my
[optimizer article](/quants/2026/08/29/portfolio-optimization.html), which ranks
stocks with a prediction model and sizes positions within risk limits.
The history runs from **23 September 1998 to 27 May 2026**.
One **P&L point** means 1% of the same fixed strategy notional throughout.

<details>
<summary>Backtest assumptions</summary>
<div markdown="1">

This history has already helped shape the model. The backtest charges five
basis points on traded notional and excludes borrow, financing and market
impact. Long and short contributions use the same notional, with costs
recorded separately.

</div>
</details>

## The long and short books

Across the full history, longs earned **444.27 points**, shorts lost **93.17**,
and trading costs took another **38.18**. That leaves **312.92 points net**.
Figure 1 shows how much of the long book's gains the strategy kept.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/whole-history" mobile="/assets/portfolio-attribution/whole-history_mobile" version="4" alt="Full-history cumulative long, short and net contributions above the daily net drawdown, with the 2008–09 and 2020–21 declines shaded." %}
</div>
<p class="figure-caption"><strong>Figure 1: The longs carried the accumulated result.</strong> Cumulative fixed-notional P&amp;L and its drawdown, September 1998–May 2026. Longs and shorts are gross; net includes trading costs. Shading marks the two deepest peak-to-trough declines.</p>

The short book wasn't a constant drag. Table 1 shows that it added **5.12
points in 2000–04**, but lost **54.89 in 2010–14**. Its role needs to be
understood across different market conditions.

<div markdown="1">
<p class="table-caption"><strong>Table 1: How the two books contributed over time.</strong> P&amp;L points. ¹Partial blocks; totals are not annualized.</p>

| Period | Longs | Shorts | Costs | Net |
| :--- | ---: | ---: | ---: | ---: |
| 1998–99¹ | +31.84 | −8.45 | −1.74 | +21.66 |
| 2000–04 | +67.61 | +5.12 | −7.77 | +64.97 |
| 2005–09 | +57.41 | −14.98 | −7.54 | +34.88 |
| 2010–14 | +112.99 | −54.89 | −7.03 | +51.08 |
| 2015–19 | +87.54 | −5.35 | −6.36 | +75.83 |
| 2020–24 | +69.39 | −13.74 | −6.15 | +49.51 |
| 2025–26¹ | +17.48 | −0.87 | −1.61 | +15.00 |
{: .research-table .comparison-table .attribution-table }

</div>

The long and short books had standalone annualized volatility of **16.7%**
and **16.4%**, but their daily P&L had a correlation of **−0.89**. Together,
after costs, portfolio volatility was **7.9%**. The shorts lost money while
offsetting a lot of the longs' fluctuations. Removing them would change both.

The portfolio was net long **22.0% of notional on average**, yet its historical
beta to the Russell 1000 price-return benchmark was only **0.068**. A larger
book of lower-beta longs can offset a smaller book of higher-beta shorts.
The drawdowns will show where that balance broke down.

## Where returns and risk came from

Figure 2 groups the stock contributions by sector and puts earnings beside
each sector's share of realized portfolio variance. That share measures how
its daily P&L moves with the whole portfolio: covariance with portfolio P&L,
divided by portfolio variance. It includes the offsets between positions.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/sector-pnl" mobile="/assets/portfolio-attribution/sector-pnl_mobile" version="5" alt="Sector P&L and share of net portfolio variance on matching rows, ranked by full-history earnings." %}
</div>
<p class="figure-caption"><strong>Figure 2: Compare what each sector earned with the risk it contributed.</strong> September 1998–May 2026. P&amp;L is gross across both books. Variance shares include covariance with the rest of the portfolio; unallocated costs contribute −0.01% and are omitted.</p>

**Every sector contributed positively before costs.** Technology led with
**63.45 points**, followed by Consumer Discretionary and Industrials.
Health Care and Technology each accounted for about **15% of variance**,
although Technology earned considerably more.

Energy earned only **2.32 points** while contributing **6.1% of variance**.
Its longs earned **17.64 points**, almost cancelled by **15.33 points of short
losses**. That is a useful place to investigate whether the shorts provided
enough protection to justify their cost.

These totals reflect position size and time held as well as stock performance.
The sector labels are retrospective. They help locate the earnings and losses;
the next question is whether different sectors contained similar bets.

## Shared exposures

A factor model looks for those common bets. I fit each day's stock returns
jointly to prior-day size, momentum, volatility, beta, reversal and sector
characteristics. A factor's contribution combines the portfolio's exposure
with that day's fitted factor return. The **residual** is the part of covered
stocks' returns the model leaves unexplained.

Figure 3 shows that momentum, volatility and reversal earned money over the
full history, while beta and size detracted. The largest component was the
**residual, +198.82 points**, which also contributed **45.2% of realized
variance**.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/factor-pnl" mobile="/assets/portfolio-attribution/factor-pnl_mobile" version="5" alt="Full-history fitted components with P&L beside signed variance share, including residual, uncovered holdings and costs." %}
</div>
<p class="figure-caption"><strong>Figure 3: Earnings and risk tell different parts of the story.</strong> P&amp;L sums to +312.92 points net; realized variance shares sum to 100%. Sector effects are fitted model terms, distinct from the complete sector P&amp;L in Figure 2.</p>

The common intercept earned **84.09 points**. It represents the fitted
baseline shared by covered stocks; its exposure is their net dollar weight.
The standardized beta term measures a separate tilt within the stock universe.
Neither label alone gives the portfolio's sensitivity to a market index.

The model covered about **93.1% of gross exposure** on average. Uncovered
holdings earned **22.49 points** and remain separate from the residual.
I also wouldn't equate the residual with stock-picking skill: omitted value,
quality and industry effects can land there, and the fitted split has
estimation noise. I haven't calculated attribution uncertainty for these
episodes.

Figure 4 shows how the exposures behind those earnings changed. The portfolio
usually favoured larger stocks and maintained a negative volatility tilt.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/whole-exposures" mobile="/assets/portfolio-attribution/whole-exposures_mobile" version="3" alt="Four full-history panels for standardized size, momentum, volatility and beta exposures." %}
</div>
<p class="figure-caption"><strong>Figure 4: Persistent tilts, changing sizes.</strong> Monthly mean signed standardized exposures, September 1998–May 2026, on fitted holdings. Missing positions are not rescaled. Each panel has its own vertical scale.</p>

Those exposures can be part of the prediction model's intended return.
What matters is how they behave when the strategy struggles: did the bets
become larger, or did their payoffs reverse?

## When protection reversed

The two deepest drawdowns were **2008–09** and **2020–21**, both just over
**16 P&L points**. I split each at the market low to distinguish losses during
the decline from losses during the recovery.

Table 2 covers the strategy's peak-to-trough windows: 30 July 2008 to
16 September 2009, and 21 February 2020 to 27 January 2021. The market lows
were **9 March 2009** and **23 March 2020**. These dates are identified with
hindsight and describe the episodes; they weren't trading signals.

<div markdown="1">
<p class="table-caption"><strong>Table 2: Losses continued after the market bottomed.</strong> Fixed-notional P&amp;L points, excluding the strategy's peak day. The decline includes the market-low session; the rebound follows it. Longs and shorts are gross; net includes costs.</p>

| Phase | Sessions | Longs | Shorts | Net |
| :--- | ---: | ---: | ---: | ---: |
| 2008–09 decline | 152 | −36.28 | +30.63 | −6.18 |
| 2009 rebound | 133 | +39.59 | −49.14 | −10.14 |
| 2020 decline | 21 | −39.95 | +30.74 | −9.32 |
| 2020–21 rebound | 214 | +38.41 | −44.19 | −6.74 |
{: .research-table .comparison-table .attribution-table }

</div>

**The strategy lost in both phases, in both episodes.** Shorts helped during
the declines, but didn't fully offset the long losses. During the rebounds,
short losses exceeded long gains. Figure 5 shows when that protection reversed.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/market-phases" mobile="/assets/portfolio-attribution/market-phases_mobile" version="3" alt="Benchmark levels above cumulative long, short and net P&L, split at the March 2009 and March 2020 market lows. The strategy continues losing during the rebounds." %}
</div>
<p class="figure-caption"><strong>Figure 5: The market rebounded while the strategy lost further ground.</strong> Each window runs from the strategy's peak to its trough. Shading ends at the market low. Benchmark price indices start at 100; portfolio contributions use fixed-notional P&amp;L points on separate axes. Corresponding panels share scales.</p>

The **2009 rebound caused more of that episode's loss**. In 2020, the initial
decline was much sharper: **9.32 points in 21 sessions**, followed by another
**6.74 over 214 sessions**. Rebound risk matters in both cases, but it doesn't
explain the initial failure to protect the portfolio.

Was I simply holding on to the old shorts? Table 3 separates names that were
short at the market low from names that weren't.

<div markdown="1">
<p class="table-caption"><strong>Table 3: New names also contributed to the rebound losses.</strong> Gross short P&amp;L points from after the market low through the strategy trough. Groups include subsequent resizing, exits and reentries.</p>

| Short-book names | 2009 rebound | 2020–21 rebound |
| :--- | ---: | ---: |
| Short at the market low | −20.90 | −23.12 |
| Not short at the market low | −28.24 | −21.08 |
| **Total** | **−49.14** | **−44.19** |
{: .research-table .comparison-table .attribution-table }

</div>

Names absent from the short book at the low accounted for **57.5%** of its
2009 rebound loss and **47.7%** in 2020–21. The five worst short contributors
explained only **12.4%** and **8.8%** of the respective losses.
The damage was broad and involved changing positions, which points back
towards shared characteristics.

The beta and volatility tilts helped during both market declines, then hurt
during both rebounds. Figure 6 shows their contributions over each complete
drawdown, alongside the residual and other terms.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/drawdown-factors" mobile="/assets/portfolio-attribution/drawdown-factors_mobile" version="3" alt="The 2008–09 and 2020–21 attribution side by side: beta and residual lead the first loss; residual and volatility lead the second." %}
</div>
<p class="figure-caption"><strong>Figure 6: Similar total losses, different factor contributions.</strong> Peak-to-trough P&amp;L points on equal scales. Each panel includes factor terms, residual, uncovered holdings and costs.</p>

In **2008–09**, beta was the largest losing style at **−6.55 points**, and the
residual lost **6.14**. In **2020–21**, volatility lost **8.10 points** and the
residual **11.41**. Other contributions partly offset those losses.

Inside those totals, beta went from **+3.32 during the decline to −9.87 during
the rebound** in 2008–09, and from **+1.27 to −5.80** in 2020–21. The strategy
kept a negative tilt as the fitted payoff changed sign.

Exposure variation within the rebounds actually softened the beta and
volatility losses relative to each phase's average exposure. For example,
2020–21 volatility lost **8.71 points**, compared with **9.68** at the phase's
average exposure. That directs my attention towards the persistent bet.
This comparison combines trades, price drift and changing stock characteristics;
it doesn't isolate the quality of the sizing decisions.

A closer look at the holdings supports the defensive-long/aggressive-short
explanation. At the March 2020 low, the longs had lost **17% over the preceding
126 sessions**, versus **35% for the shorts**, weighted by starting exposure.
Their estimated market betas were **0.86 and 1.03**. The long book entered the
recovery with smaller prior losses and lower estimated market sensitivity.
The same ordering appeared in 2009.

Momentum can reinforce that overlap: during a sell-off, the relative winners
can be the defensive stocks that fell least. This resembles the rebound
mechanism in Daniel and Moskowitz's *Momentum Crashes*. But momentum isn't the
whole explanation here. During the 2009 rebound, the portfolio's momentum
orientation reversed and its fitted momentum contribution was positive,
while the low-volatility tilt continued to hurt.

## What variance misses

Portfolio volatility rose from **7.9%** over the full history to **9.3%** in
the 2008–09 drawdown and **13.1%** in 2020–21. Yet Table 4 shows why a variance
allocation alone would miss an important part of the problem.

<div markdown="1">
<p class="table-caption"><strong>Table 4: A losing short book can have a small variance share.</strong> Realized variance shares (%) over the full history and each complete drawdown. Costs account for the small difference from 100%.</p>

| Period | Longs | Shorts |
| :--- | ---: | ---: |
| Full history | 59.6 | 40.4 |
| 2008–09 drawdown | 36.1 | 63.9 |
| 2020–21 drawdown | 99.9 | 0.2 |
{: .research-table .comparison-table .attribution-table }

</div>

Shorts lost **13.46 P&L points** over the complete 2020–21 drawdown, yet
contributed only **0.2% of its daily variance**. Their standalone volatility
was **23.4%**, but their negative covariance with the longs almost cancelled
that variance in the allocation.

The short book could offset daily fluctuations while still losing money over
the recovery. Its small variance share therefore doesn't settle whether those
positions were useful. I need the path of the losses alongside the risk totals.

## What I'd test next

I'd start with a permanent sizing rule for shorts where prior losses, high beta
and high volatility overlap. That targets the shared vulnerability without
requiring me to recognise a market bottom in real time. The prediction model
would stay fixed so the comparison tests portfolio construction.

I'd also compare replacing part of those shorts with a broad market hedge,
keeping comparable intended market sensitivity and checking the resulting
sector and style risks. The objective is to preserve useful negative stock
signals and decline protection while reducing the rebound losses.

Both changes need a costed portfolio replay across ordinary periods and other
recoveries. I'd compare net returns, drawdowns, turnover and protection during
declines, including borrow and financing. The sizing rule and hedge comparison
haven't been tested here; the two major drawdowns have already shaped the
hypothesis.

## References

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
2021 edition, Chapters 3–4 and 7–8;
[*The Elements of Quantitative Investing*](https://linktr.ee/paleologo),
9 September 2024 draft, Chapters 6 and 14.

Kent Daniel and Tobias Moskowitz, [*Momentum Crashes*](https://www.kentdaniel.net/papers/published/jfe_16.pdf),
*Journal of Financial Economics*, 2016, Sections 2–3.

The [dashboard source code](https://github.com/piinghel/portfolio-pnl-dashboard)
is available if you'd like to explore your own portfolio.
