---
layout: post
title: "Performance Attribution, Part 3: Can Risk Limits Improve Rebounds?"
description: "At equal risk, moderate tilt limits help in declines and most strong rallies at no measurable cost, but not in the 2020–21 rebound; beta limits mostly add market beta."
permalink: /quants/managing-rebound-risk.html
toc: true
date: 2026-09-09
last_modified_at: 2026-09-27
categories: ["Risk & attribution"]
article_label: Performance attribution · Part 3 of 3
series_id: performance-attribution
series_order: 3
---

<p class="article-summary">The rebound analysis points to a defensive tilt that becomes costly in strong rallies. I test limits on that tilt, direct limits on beta exposure and daily volatility scaling, and ask what each one buys in rallies and gives up elsewhere.</p>

Once a pattern shows up in attribution, it's tempting to add a constraint
and move on. But a limit changes the portfolio on every date it applies,
including the periods when that exposure was useful. The question is whether
it fixes enough of the problem to justify what it gives up elsewhere.

[Part 2](/quants/short-book-rebounds.html) located the problem: the shorts
hold higher-beta, higher-volatility stocks than the longs, and in strong
rallies that defensive tilt gives back roughly what the net long position
earns. Rallies cluster early in rebounds, but the 2020–21 rebound lost its
money seven months after the low. So I judge each rule on strong rallies,
on market declines and on the two complete rebounds, not on a fixed window
after each low.

I try three rules: limit the low-volatility tilt, limit standardized beta
exposure directly, and reduce the whole book when recent volatility rises. I
keep the forecasts, covariance model and execution rules unchanged, and label
the unchanged portfolio **Original**. The same portfolio, period and
[conventions as Part 1](/quants/portfolio-attribution.html#pnl-conventions)
apply: fixed-notional P&L points, 5 bp trading costs, and no borrow, financing
or impact.

## Three rules

**Tilt limits.** The strategy ranks stocks by 21-session volatility on a scale
from −1 (least volatile) to +1 (most volatile). I measure the book's tilt as

$$
V_t=\frac{\sum_i w_{i,t}u_{i,t}}{\sum_i |w_{i,t}|},
$$

where $u_{i,t}$ is the volatility rank and $w_{i,t}$ the signed position weight,
so long positions in calm stocks and shorts in volatile ones both make $V_t$
negative. I replayed the optimizer with limits of **±0.30, ±0.25, ±0.20, ±0.15
and ±0.10** on $V_t$, applied at each rebalance. Even the loosest bound was
binding on about half of all rebalances, and it moved the average tilt only
from −0.29 to −0.25.

**Standardized beta limits.** The optimizer already caps its forecast beta at
±0.05, which still leaves the negative standardized beta exposure from
[Part 1](/quants/portfolio-attribution.html#portfolio-beta). I added a limit on
that exposure,

$$
-b\leq\sum_i w_i z_{i,\beta}\leq b,
$$

with $b$ at **±0.50, ±0.30 and ±0.10**. Loadings cover about 93% of gross
exposure; a missing loading counts as the universe mean, zero.

**Volatility scaling.** Instead of changing which stocks the book holds, I
shrink the whole book when its recent P&L becomes more volatile:

$$
m_t=\min\left(1,\frac{7\%}{\widehat{\sigma}_t}\right),
$$

where $\widehat{\sigma}_t$ is an exponentially weighted estimate of daily
gross P&L volatility, annualized, with a half-life of **5 sessions** (fast) or
**21 sessions** (slow). The multiplier uses only information available before
the trade and pays for its extra resizing trades.

## Full-history results

<div markdown="1">
<p class="table-caption"><strong>Table 1: Each rule as run.</strong> Net P&amp;L in points of fixed notional; volatility annualized; realized beta is the full-history regression of daily net P&amp;L on the Russell 1000.</p>

| Rule | Net / year | Volatility | Sharpe | Realized beta |
| :--- | ---: | ---: | ---: | ---: |
| Original | 11.33 | 7.90% | 1.43 | 0.068 |
| Tilt limit ±0.30 | 11.16 | 7.67% | 1.45 | 0.064 |
| Tilt limit ±0.20 | 10.65 | 7.44% | 1.43 | 0.048 |
| Tilt limit ±0.10 | 9.68 | 7.16% | 1.35 | 0.021 |
| Beta limit ±0.30 | 11.31 | 7.81% | 1.45 | 0.081 |
| Beta limit ±0.10 | 11.16 | 7.70% | 1.45 | 0.091 |
| Fast scaling | 9.44 | 6.71% | 1.41 | 0.048 |
| Slow scaling | 9.95 | 6.79% | 1.47 | 0.053 |
{: .research-table .comparison-table .attribution-table }
</div>

Every rule earns less P&L than the Original, but every rule also takes less
risk, and on Sharpe most of them are level with it; only the tightest tilt
limit falls clearly behind. The tilt limits run a smaller book, and scaling
cuts size whenever volatility rises, so comparing raw P&L would mostly
measure size. I compare the rules at equal risk instead, scaling each one's
daily P&L to the Original's 7.9% volatility. That assumes the smaller books
could be levered up: by about 3% for the ±0.30 tilt limit and 6% for ±0.20, but
17% for slow scaling, which would have to add that size back on average while
cutting it whenever volatility rises.

The rules also move market beta, in opposite directions. The beta limit
raises realized beta to 0.091: removing the negative beta exposure leaves more
of the net long book's market sensitivity, the mechanism from Part 1. The tilt
limits lower it, to 0.021 at ±0.10, for reasons I haven't traced. A rule that
simply holds more market will look better in rallies and worse in declines,
so that direction is worth keeping in view.

## Declines and rallies

Table 2 splits each rule's equal-risk difference from the Original by market
regime. A strong rally is a period in which the Russell 1000 rose more than
13% over 63 sessions, as in Part 2; merging overlapping windows leaves 16
distinct rallies since 1998. The Original itself made 45.6 points across them,
but lost money in six, including both of the rebounds from Part 2.

<div markdown="1">
<p class="table-caption"><strong>Table 2: What each rule changes at equal risk.</strong> Net P&amp;L points of fixed notional, rule minus Original, after scaling each rule to the Original's full-history volatility. Declines run from each of the 11 market peaks to the low; strong rallies give the total over the 16 rallies, with the number improved in parentheses; rebounds run from the 2009 and 2020 lows to the strategy troughs.</p>

| Rule | Full history | Declines | Strong rallies | 2009 rebound | 2020–21 rebound |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Tilt limit ±0.30 | +4.7 | +2.8 | +4.5 (11) | +1.9 | −1.5 |
| Tilt limit ±0.20 | −0.3 | +9.7 | +7.1 (11) | +1.8 | −2.9 |
| Tilt limit ±0.10 | −17.7 | +20.2 | +3.8 (8) | +1.9 | −2.6 |
| Beta limit ±0.30 | +3.2 | −4.0 | +5.9 (12) | +2.8 | +0.7 |
| Beta limit ±0.10 | +3.5 | −10.7 | +12.8 (12) | +5.3 | +1.0 |
| Fast scaling | −5.5 | +5.9 | +1.3 (9) | +1.0 | +2.2 |
| Slow scaling | +7.2 | +6.5 | +3.7 (7) | −0.5 | +2.4 |
{: .research-table .comparison-table .attribution-table }
</div>

None of the full-history differences means much: block-bootstrap intervals
for them all include zero. The pattern across regimes is more informative,
and Figure 1 shows it for every rule.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/control-tradeoff" mobile="/assets/portfolio-attribution/control-tradeoff_mobile" version="2" alt="Each rule's equal-risk difference from the Original in market declines against strong rallies. Beta limits lie along the line for extra market beta; tilt limits arc into the region that is better in both; scaling sits slightly better in both." %}
</div>
<p class="figure-caption"><strong>Figure 1: Beta limits mostly add market beta; tilt limits improve both regimes.</strong> Equal-risk differences from the Original, in net P&amp;L points over the 11 declines and the 16 strong rallies. Lines join each family from the Original to its tightest limit (tilt ±0.30 to ±0.10, beta ±0.50 to ±0.10). The dashed line shows where a book that only added or removed market beta would land.</p>

The beta limits lie almost exactly on the market-beta line: what they gain in
rallies they give back in declines, as a small index position would. Net of
their extra beta, the ±0.10 limit's rally gain falls from 12.8 to 4.7 points
and it improves only 8 of the 16 rallies.

The tilt limits do something different. The moderate ones, ±0.30 and ±0.20,
do better in declines and in 11 of the 16 rallies at no measurable
full-history cost, and at equal risk they make both deep drawdowns 1.6 to 3
points shallower (−13.3 and −13.6 at ±0.20, against −16.3 and −16.1). Tighter
than that, the rally gain fades and the full-history cost appears.

But the episode that motivated all this barely moves. Every tilt limit does
worse over the complete 2020–21 rebound, and none of them changes the
12.4-point loss from November 2020 to January 2021 by more than 1.3 points.
Only scaling cushioned that leg, by about 3.5 points, because both versions
were holding a much smaller book when the rally began. In 2008–09, where the
tilt limits helped, scaling made the drawdown deeper.

## Would I change the baseline?
{: #what-the-experiment-settles }

Not yet. The one rule I would consider is a moderate tilt limit: at the same
risk it gives up nothing I can measure, does a little better in declines and
in most strong rallies, and makes the deep drawdowns shallower. What it doesn't
do is fix the loss that started this series, and the case for it rests on
sixteen rallies, two drawdowns and full-history differences well inside the
noise. The beta limit, which looked cheapest on raw P&L, mostly buys market
beta.

Three questions stay open. Why did the 2020–21 rally, which began seven months
after the low, hurt a less defensive book as much as the Original, when the
same limits helped in 2009? Why do the tilt limits lower realized beta, when a
less defensive tilt might be expected to raise it? And does the later version
of the Ridge ranking carry the same defensive tilt and pay for it the same way?
