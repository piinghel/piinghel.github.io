---
layout: post
title: "Performance Attribution, Part 2: Why the Short Book Loses in Strong Rallies"
description: "Higher-beta, higher-volatility shorts lose in strong rallies. Those rallies cluster early in rebounds, but not only there."
permalink: /quants/short-book-rebounds.html
toc: true
date: 2026-09-09
last_modified_at: 2026-09-27
categories: ["Risk & attribution"]
article_label: Performance attribution · Part 2 of 3
series_id: performance-attribution
series_order: 2
---

<p class="article-summary">A market recovery can be difficult for a portfolio that shorts volatile stocks. I look at the holdings behind two large drawdowns, then compare eleven rebounds with the rest of the history to see when the same imbalance appears.</p>

The market can recover well before a long–short portfolio does. That gap is
what I want to understand here. In [Part 1](/quants/portfolio-attribution.html),
the short book helped during declines but gave back more during the rebounds.
The next step is to look at the positions behind that reversal.

Were a few short positions responsible, or did the stocks across the book
share characteristics that made them vulnerable to a recovery? I'll start
with the 2009 and 2020 rebounds, compare the holdings and their factor
contributions, then check eleven episodes. The aim is to see whether the
problem repeats and whether it is concentrated in the first few months.

I use the same portfolio, period and [conventions as Part 1](/quants/portfolio-attribution.html#pnl-conventions):
fixed-notional P&L points, 5 bp trading costs, and no borrow, financing or impact.
Missing borrow costs flatter the short book most in crashes and squeezes, and
the backtest also ignores the SEC's ban on shorting about 800 financial stocks
from 19 September to 8 October 2008, inside the 2008–09 decline.

## Protection during the decline, losses during the rebound

The strategy's two deepest drawdowns were **2008–09** and **2020–21**, both just over
**16 P&L points**. I split each at the market low to distinguish losses during
the decline from losses during the rebound.

Table 1 covers the strategy's peak-to-trough windows: 30 July 2008 to
16 September 2009, and 21 February 2020 to 27 January 2021. The market lows
were **9 March 2009** and **23 March 2020**.

<div markdown="1">
<p class="table-caption"><strong>Table 1: Losses continued after the market bottomed.</strong> Fixed-notional P&amp;L points, excluding the strategy's peak day. The decline includes the market-low session; the rebound follows it. Longs and shorts are gross; net includes costs.</p>

| Phase | Sessions | Longs | Shorts | Net |
| :--- | ---: | ---: | ---: | ---: |
| 2008–09 decline | 152 | −36.28 | +30.63 | −6.18 |
| 2009 rebound | 133 | +39.59 | −49.14 | −10.14 |
| 2020 decline | 21 | −39.95 | +30.74 | −9.32 |
| 2020–21 rebound | 214 | +38.41 | −44.19 | −6.74 |
{: .research-table .comparison-table .compact-table }

</div>

In both episodes, gains on the long side during the rebound were smaller
than the short-book losses. Figure 1 follows the two contributions through time.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/market-phases" mobile="/assets/portfolio-attribution/market-phases_mobile" version="4" alt="Benchmark levels above cumulative long, short and net P&L, split at the March 2009 and March 2020 market lows. The strategy continues losing during the rebounds." %}
</div>
<p class="figure-caption"><strong>Figure 1: The market rebounded while the strategy lost further ground.</strong> Each window runs from the strategy's peak to its trough. Shading ends at the market low. Benchmark price indices start at 100; portfolio contributions use fixed-notional P&amp;L points on separate axes.</p>

I first checked whether the losses came from holding on to the old shorts.
Table 2 separates names that were short at the market low from additions
during the rebound.

<div markdown="1">
<p class="table-caption"><strong>Table 2: New names also contributed to the rebound losses.</strong> Gross short P&amp;L points from after the market low through the strategy trough. "Short at the market low" means held during the low session; groups include subsequent resizing, exits and reentries.</p>

| Short-book names | 2009 rebound | 2020–21 rebound |
| :--- | ---: | ---: |
| Short at the market low | −20.90 | −23.12 |
| Rebound additions | −28.24 | −21.08 |
| **Total** | **−49.14** | **−44.19** |
{: .research-table .comparison-table .compact-table }

</div>

Around half the short-book losses came from names added during the rebound,
and the five worst contributors explained only 12% and 9%. Looking only at
old shorts or the worst few names would miss most of the loss, so I next look
at what the stocks across the book had in common.

Figure 2 splits the two rebounds into the factor model's components. In both,
the net long book earned about **15 points** from the common market move, and
the beta and volatility tilts gave back about the same: **−15.6** and **−14.5
points** together. Size and the residual then turned each rebound into a loss.
Beta and volatility are correlated characteristics fitted jointly, so the
split between them depends on the model; their sum is the sturdier number.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/drawdown-factors" mobile="/assets/portfolio-attribution/drawdown-factors_mobile" version="4" alt="Rebound P&L by component for 2009 and 2020–21: the common return adds about 15 points in each, while beta and volatility together lose about the same." %}
</div>
<p class="figure-caption"><strong>Figure 2: In both rebounds, the defensive tilt gave back what the net long position earned.</strong> P&amp;L points from the session after the market low through the strategy trough, on one shared scale. The components add up to the rebound net P&amp;L in Table 1.</p>

Table 3 separates beta exposure from its payoff using
[Part 1's calculation](/quants/portfolio-attribution.html#follow-exposure-and-payoff-together).

<div markdown="1">
<p class="table-caption"><strong>Table 3: Negative beta exposure met a positive rebound payoff.</strong> Same phases as Table 1. Mean standardized beta exposure per notional; cumulative payoff for +1 exposure, in percentage points. P&amp;L uses each day's actual exposure, so it need not equal mean exposure times cumulative payoff.</p>

| Phase | Standardized beta exposure | Beta payoff | Beta P&L |
| :--- | ---: | ---: | ---: |
| 2008–09 decline | −0.443 | −3.68 | +3.32 |
| 2009 rebound | −0.513 | +21.18 | −9.87 |
| 2020 decline | −0.192 | −3.94 | +1.27 |
| 2020–21 rebound | −0.466 | +12.65 | −5.80 |
{: .research-table .comparison-table .compact-table }
</div>

The beta payoff changed sign in both episodes while exposure remained negative.
In 2020 the book even added to the bet as the market turned: standardized beta
exposure went from **−0.18** at the low to **−0.32** the next session and
**−0.40** two sessions later, as rebalancing moved it further into lower-beta
stocks. In 2009 it stayed near −0.35.

## The stocks on each side

Figure 3 compares the stocks held on each side as the rebounds
began. **In both episodes, the shorted stocks had higher estimated market
betas, larger prior losses and higher volatility than the longs.**

<div class="research-figure responsive-figure" id="rebound-holdings">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/rebound-holdings" mobile="/assets/portfolio-attribution/rebound-holdings_mobile" version="1" alt="At the 2009 low, long versus short stock beta was 0.89 versus 1.11; at the 2020 low, 0.86 versus 1.03. Shorts also had larger prior losses and higher volatility in both episodes." %}
</div>
<p class="figure-caption"><strong>Figure 3: The shorts held riskier stocks than the longs.</strong> Average stock characteristics, weighted by position size within each book, entering the first rebound session. Measurements end at the market lows of 9 March 2009 and 23 March 2020. Beta uses up to 252 daily returns against the Russell 1000 (126 minimum); prior return uses 126 sessions; volatility uses 21 sessions, annualized.</p>

This is the mechanism Daniel and Moskowitz describe for momentum crashes: a
book short high-beta past losers going into a rebound. Here it runs through
the beta and volatility tilt rather than momentum itself, which added 1.6
points in the 2009 rebound and cost 0.8 in 2020–21.

## Does the pattern repeat?

To see how often the same imbalance appeared elsewhere, I identified **11 market
declines of at least 10%** and followed the first
63 sessions after each low. A new episode starts only after the previous market peak has been regained; intervening declines belong to the same episode.

The long book is usually larger than the short book, so comparing their
P&L totals alone mixes stock performance with position size. I measure
the return of the stocks on each side per unit of that
side's gross exposure. For book $\ell$, with gross exposure
$A_{\ell,t}=\sum_{i\in\ell}|w_{i,t^-}|$, the measure is

$$
G_\ell(H)=100\sum_{t=1}^{H}
\frac{\sum_{i\in\ell}|w_{i,t^-}|r_{i,t}}{A_{\ell,t}}.
$$

It adds up the returns of each day's positions, counting a price rise as a gain on either side, even though that rise hurts the portfolio when the stock is short. I compare $G_{\mathrm{short}}-G_{\mathrm{long}}$, then
look separately at the actual portfolio P&L over exactly the same sessions.

Figure 4 starts with all 11 rebounds. Select an episode to follow the two
books through time, then choose 21, 63 or 126 sessions and move the date slider.
At 63 sessions, **shorted stocks gained more in 9 of 11
episodes**, with a median gap of **2.9 percentage points**. The 2009 gap was
far larger than the typical episode.

{% include attribution-recovery-explorer.html figure="4" %}

How unusual is that? Across every 63-session window in the history, shorted
stocks outgained the longs only **28%** of the time. In windows where the
Russell 1000 rose more than 13%, they did so **82%** of the time, and
across the 11 episodes the gap grows with the size of the rally (correlation
0.7). The imbalance is a strong-rally effect; rebounds just tend to start with
strong rallies.

Faster-rising shorted stocks need not produce a portfolio loss: the long book
is larger. In the first 63 sessions of the 2020 rebound the portfolio still
gained **0.4 points** after costs, and by 6 November 2020 it was up **5.7**.
The whole 2020–21 rebound loss came after that: **12.4 points** by 27 January
2021, while the index rose another 8%. The stretch runs from the last session
before the vaccine announcement of 9 November to the closing peak of January's
retail short squeeze; whether either event drove the loss is untested. The shorts lost 18.7 points in those
eleven weeks against 6.5 gained on the longs, and volatility was again the
largest style (−6.1), ahead of size (−2.6) and beta (−2.0).

Table 4 checks shorter and longer windows around the same lows.

<div markdown="1">
<p class="table-caption"><strong>Table 4: The imbalance is more common early in the rebound.</strong> The same 11 lows at each horizon; the windows overlap. Gap = short-stock gains minus long-stock gains per unit of exposure, in percentage points. Net losses use portfolio P&amp;L after recorded trading costs.</p>

| Sessions after low | Shorts gained more | Median gap | Net portfolio losses |
| ---: | ---: | ---: | ---: |
| 21 | 9 / 11 | +2.73 | 4 / 11 |
| 63 | 9 / 11 | +2.89 | 4 / 11 |
| 126 | 3 / 11 | −2.49 | 1 / 11 |
{: .research-table .comparison-table .compact-table }

</div>

By 126 sessions the median imbalance has reversed and only one portfolio
window remains negative, as the rallies slow. Over all 63-session windows,
the portfolio lost money 24% of the time, so 4 of 11 after lows is only
somewhat worse; what stands out after lows is the stock-level gap.

## What the rebounds show

The rebound losses weren't a few bad shorts. They came from what the shorts
had in common: higher beta, higher volatility and larger
prior losses than the longs. In a strong rally that defensive tilt gives back
roughly what the net long position earns, and size and the residual decide
the rest.

That changes what I'd try to manage. The problem isn't the first three months
after a low; it's exposure to strong rallies in high-beta, high-volatility
stocks. Those cluster early in rebounds but, as late 2020 showed, not only
there. Any fix also has to keep what the shorts provide on the way down: about
31 points in both declines.

Two questions stay open. Do the predictors choose these shorts because of
their beta and volatility, or despite it? And was the late-2020 loss, led by
volatility and size, the same mechanism as the early rebounds or a different
rotation? In [Part 3](/quants/managing-rebound-risk.html), I test tilt limits,
standardized beta limits and daily portfolio scaling against that trade-off.

## References

Kent Daniel and Tobias Moskowitz, [*Momentum Crashes*](https://www.kentdaniel.net/papers/published/jfe_16.pdf),
*Journal of Financial Economics*, 2016, Sections 2–3. Their rebound mechanism
motivates the comparison with the observed holdings here.
