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

## The long and short books

I start with each stock's daily P&L: its signed position at the start of the
session multiplied by its return. A short position has a negative weight,
so a price rise produces a loss. Adding these contributions across stocks
and days gives the long and short totals; trading costs are kept separate.

Across the full history, longs earned **444.27 points**, shorts lost **93.17**,
and trading costs took another **38.18**. That leaves **312.92 points net**.
Figure 1 shows how much of the long book's gains the strategy kept.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/whole-history" mobile="/assets/portfolio-attribution/whole-history_mobile" version="4" alt="Full-history cumulative long, short and net contributions above the daily net drawdown, with the 2008–09 and 2020–21 declines shaded." %}
</div>
<p class="figure-caption"><strong>Figure 1: The longs carried the accumulated result.</strong> Cumulative fixed-notional P&amp;L and its drawdown, September 1998–May 2026. Net deducts 5 basis points on traded notional; borrow, financing and market impact are excluded. Shading marks the two deepest peak-to-trough declines.</p>

The short book added **5.12
points in 2000–04**, but lost **54.89 in 2010–14**. Its role needs to be
understood across different market conditions.

<div markdown="1">
<p class="table-caption"><strong>Table 1: How the two books contributed over time.</strong> Total P&amp;L points in each block. ¹Partial blocks.</p>

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

Figure 2 groups the stock contributions by sector. Alongside each sector's
earnings, I show its share of the portfolio's daily variance. A sector adds
more risk when its P&L moves with the rest of the portfolio, and less when it
offsets those moves. I measure this as its covariance with portfolio P&L,
divided by portfolio variance. The shares add to 100% including costs, and
an offsetting component can have a negative share. This describes the risk
over the period; a forecast would use only information available beforehand.

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

These totals depend on how much I held and for how long, as well as how the
stocks performed. I use sector labels assigned after the period to locate
the earnings and losses. Stocks in different sectors can still carry similar
risks, which is where the factor model helps.

## Shared exposures

A factor model looks for those common bets. Suppose higher-beta stocks rise
more than lower-beta stocks on a particular day. Some of that difference may
also reflect their sectors or momentum. I fit those characteristics together
to estimate what each one earned after accounting for the others.

**First, describe the stocks before the session.** The model uses size,
momentum, volatility, beta and short-term reversal, plus sector indicators.
Size, momentum and volatility come from the strategy's existing descriptors;
the volatility descriptor is a rank. Beta uses up to 252 daily observations
(126 minimum), and reversal is the negative preceding five-session return.
Each style descriptor is centered and scaled across the eligible universe:

$$
z_{i,k,t-1}=\frac{x_{i,k,t-1}-\mu_{k,t-1}}{\sigma_{k,t-1}}.
$$

Here, $i$ identifies a stock and $k$ a style. The mean and standard deviation
use weights proportional to the square root of market capitalization. A
loading of $+1$ means one weighted standard deviation above the average of
that descriptor. For ranked inputs, the loading measures relative rank.

**Then fit that day's returns across stocks.** For each eligible stock with
a valid return, I write

$$
r_{i,t}=a_t+\sum_k z_{i,k,t-1}f_{k,t}
       +g_{s(i),t}+\varepsilon_{i,t}.
$$

The common return is $a_t$, the style returns are $f_{k,t}$, and
$g_{s(i),t}$ is the effect for the stock's sector. The residual
$\varepsilon_{i,t}$ is the stock's realized return minus its fitted return. This is a new
cross-sectional fit each day, using the eligible stock universe. The
characteristics and market caps come
from the prior session; the returns being explained come from the session
that has just finished. Sector labels are retrospective, as noted above.

I estimate all the coefficients jointly by weighted least squares over that
day's fitting universe $U_t$:

$$
\underset{a_t,f_t,g_t}{\operatorname{minimize}}\;
\sum_{i\in U_t}q_{i,t-1}\varepsilon_{i,t}^{\,2},
$$

where $$q_{i,t-1}=\sqrt{\mathrm{cap}_{i,t-1}}$$ and cap is market capitalization. These are positive
**fitting weights**, distinct from the portfolio's signed position weights.
A stock four times as large gets twice the weight in the fit. To separate
the common return from the sector effects, their loss-weighted average is
constrained to zero: $$\sum_s Q_{s,t}g_{s,t}=0$$, where
$$Q_{s,t}=\sum_{i\in U_t:s(i)=s}q_{i,t-1}$$.

The coefficients use unpenalized least squares, solved jointly by SVD.
A positive fitted volatility return means
higher-volatility descriptors were associated with better returns that day,
conditional on the other terms. The model attributes realized returns to the
stocks' exposures.

**Finally, apply the fit to the positions actually held.** Let $w_{i,t^-}$
be the signed position just before the session, divided by the fixed strategy
notional. The exposure and daily contribution for style $k$ are

$$
E_{k,t}=\sum_{i\in H_t}w_{i,t^-}z_{i,k,t-1},
\qquad c_{k,t}=E_{k,t}\widehat f_{k,t}.
$$

$H_t$ contains the holdings covered by the fit. Long and short contributions
use the same equation, with positive and negative position weights. I also
multiply each covered stock's residual by its position weight. The common
return uses the net weight of covered holdings, and each sector effect uses
the net weight in that sector. Adding these pieces, uncovered holdings and
costs reconstructs daily portfolio P&L; the saved reconciliation also retains
a negligible price-basis difference between the fitting and P&L inputs.

For example, a 2% long position with a volatility loading of $-1$ contributes
$-0.02$ to that exposure. A 1% short with a loading of $+2$ also contributes
$-0.02$. Together, their exposure is $-0.04$. If the fitted volatility return
is $+1\%$ that day, their volatility contribution is $-0.0004$, or
**−0.04 P&L points**. Both positions lose through the same factor despite
being on opposite sides of the book. This is an arithmetic illustration;
their other factor contributions and residuals still affect total P&L.

Across days, I add the contributions, in P&L points:

$$
C_k(T)=100\sum_{t\leq T}E_{k,t}\widehat f_{k,t}.
$$

Both terms can change each day. A stock's characteristics move, positions are
resized or replaced, and the factor payoff changes. The daily calculation
matches each payoff to the exposure held when it arrived.

Figure 3 shows that momentum, volatility and reversal earned money over the
full history, while beta and size detracted. The largest component was the
**residual, +198.82 points**, which also contributed **45.2% of realized
variance**.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/factor-pnl" mobile="/assets/portfolio-attribution/factor-pnl_mobile" version="5" alt="Full-history fitted components with P&L beside signed variance share, including residual, uncovered holdings and costs." %}
</div>
<p class="figure-caption"><strong>Figure 3: Earnings and risk tell different parts of the story.</strong> P&amp;L sums to +312.92 points net; realized variance shares sum to 100%. Sector effects are fitted model terms, distinct from the complete sector P&amp;L in Figure 2.</p>

The **common intercept, +84.09 points**, is the baseline return shared by the
stocks in the fit. The portfolio receives that return in proportion to its
net weight in those stocks. The beta term then measures the extra contribution
from favouring higher- or lower-beta stocks within that universe. To measure
the whole portfolio's sensitivity to the market, I use the benchmark beta
reported earlier.

The model covered about **93.1% of gross exposure** on average. Uncovered
holdings earned **22.49 points** and remain separate from the residual.

The factor split is an estimate. News about individual stocks can influence
the fitted factor returns. If the fit assigns an extra P&L point to factors,
it takes that point away from the residual. The total still adds up, even
though the explanation has changed. This is the attribution uncertainty
discussed in *Elements*, §14.2. The attribution below uses point estimates.

The factors I choose also matter. Value, quality and industry effects can
land in the residual when the model leaves them out. Before calling the
residual stock-picking skill, I'd want to check both the uncertainty in the
fit and what happens when I include other reasonable factors.

Figure 4 shows how the exposures behind those earnings changed. The portfolio
usually favoured larger stocks and maintained a negative volatility tilt.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/whole-exposures" mobile="/assets/portfolio-attribution/whole-exposures_mobile" version="3" alt="Four full-history panels for standardized size, momentum, volatility and beta exposures." %}
</div>
<p class="figure-caption"><strong>Figure 4: Persistent tilts, changing sizes.</strong> Monthly mean signed standardized exposures, September 1998–May 2026, using the original weights of holdings covered by the fit.</p>

For volatility, a negative exposure can come from lower-volatility longs,
higher-volatility shorts, or both. When more volatile stocks outperform after
accounting for the other factors, the fitted volatility return is positive
and the portfolio loses money through that exposure.

The prediction model may favour these characteristics because they help it
find profitable stocks. I want to understand what happens when the strategy
struggles: did it take more of the same risk, or did that risk stop paying?

## When protection reversed

The two deepest drawdowns were **2008–09** and **2020–21**, both just over
**16 P&L points**. I split each at the market low to distinguish losses during
the decline from losses during the recovery.

Table 2 covers the strategy's peak-to-trough windows: 30 July 2008 to
16 September 2009, and 21 February 2020 to 27 January 2021. The market lows
were **9 March 2009** and **23 March 2020**. These dates are identified with
hindsight to divide each episode into decline and recovery.

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
the declines, offsetting part of the long losses. During the rebounds,
short losses exceeded long gains. Figure 5 shows when that protection reversed.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/market-phases" mobile="/assets/portfolio-attribution/market-phases_mobile" version="4" alt="Benchmark levels above cumulative long, short and net P&L, split at the March 2009 and March 2020 market lows. The strategy continues losing during the rebounds." %}
</div>
<p class="figure-caption"><strong>Figure 5: The market rebounded while the strategy lost further ground.</strong> Each window runs from the strategy's peak to its trough. Shading ends at the market low. Benchmark price indices start at 100; portfolio contributions use fixed-notional P&amp;L points on separate axes. Corresponding panels share scales.</p>

The **2009 rebound accounted for more of that episode's loss**. In 2020, the initial
decline was much sharper: **9.32 points in 21 sessions**, followed by another
**6.74 over 214 sessions**. Both the initial decline and the rebound contributed
to the losses.

Was I simply holding on to the old shorts? Table 3 separates names that were
short at the market low from additions during the rebound.

<div markdown="1">
<p class="table-caption"><strong>Table 3: New names also contributed to the rebound losses.</strong> Gross short P&amp;L points from after the market low through the strategy trough. Groups include subsequent resizing, exits and reentries.</p>

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
was still positioned to benefit from lower-beta stocks doing better, just as
higher-beta stocks began to outperform.

A low-volatility strategy buys quieter stocks and shorts more volatile ones.
That gives it **negative exposure to volatility** in the fitted model. It earns
money from this tilt when lower-volatility stocks outperform, after accounting
for the other fitted characteristics. During a sharp rebound, higher-volatility
stocks can lead instead: the volatile shorts rise faster, and the same tilt
loses money. Seeking the low-volatility premium means accepting that it can
reverse over particular periods.

Figure 7 shows this in the direction of the strategy's bet: **low volatility**.
I reverse the signs of both the model's volatility exposure and its payoff.
For example, model exposure −0.5 and volatility payoff +1% become low-volatility
exposure **+0.5** and low-volatility payoff **−1%**. Both give the same
**−0.5 P&L points**. Low beta uses the same convention; momentum follows past
winners.

The **factor payoff** is the model's estimated return for one unit of exposure
on a given day, accounting for the other fitted characteristics. The
**portfolio contribution** multiplies that return by the exposure we actually
held.

Figure 7 puts these together. The middle panel adds the daily payoffs for a
constant +1 exposure. The bottom panel adds the P&L from our changing exposure.
Move the slider or click a chart to inspect the multiplication for one day.

{% include attribution-dynamics.html %}
<p class="figure-caption"><strong>Figure 7: Exposure × return per unit = portfolio P&amp;L.</strong> Exposures use standardized loadings and the original weights of holdings covered by the fit. Portfolio P&amp;L is measured in points of strategy notional. Shading ends at the market low.</p>

Positive exposure gains when the factor-payoff line rises and loses when it
falls. Negative exposure reverses that relationship: a falling factor payoff
produces gains. That is how the momentum contribution can recover while the
momentum payoff keeps falling in the 2009 view. Each cumulative line adds up
daily results, so its slope shows when gains or losses occurred.

Holding each exposure at its average level for the rebound would have
produced larger beta and volatility losses. For example, volatility lost
**8.71 points** in the 2020–21 rebound, compared with **9.68** at its average
exposure. The continuing low-volatility bet is therefore worth examining.
The observed exposure changes combine trading, price moves and changes in the
stocks' characteristics.

A closer look at the holdings makes the imbalance easier to see. Figure 8
compares the stocks held on each side as the recoveries
began. **In both episodes, the shorted stocks had higher estimated market
betas, larger prior losses and higher volatility than the longs.**

<div class="research-figure responsive-figure" id="rebound-holdings">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/rebound-holdings" mobile="/assets/portfolio-attribution/rebound-holdings_mobile" version="1" alt="At the 2009 low, long versus short stock beta was 0.89 versus 1.11; at the 2020 low, 0.86 versus 1.03. Shorts also had larger prior losses and higher volatility in both episodes." %}
</div>
<p class="figure-caption"><strong>Figure 8: The shorts held riskier stocks than the longs.</strong> Average stock characteristics, weighted by position size within each book, entering the first rebound session. Measurements end at the market lows of 9 March 2009 and 23 March 2020. Beta uses up to 252 daily returns against the Russell 1000 (126 minimum); prior return uses 126 sessions; volatility uses 21 sessions, annualized. The lows are identified in hindsight.</p>

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

## Across other recoveries

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

Figure 9 starts with all 11 recoveries. Select an episode to follow the two
books through time, then choose 21, 63 or 126 sessions and move the date slider.
At 63 sessions, **shorted stocks gained more in 9 of 11
episodes**, but the median gap was **2.89 percentage points**. The **41.19-point
gap in 2009** was much larger than the usual episode; the mean gap of
**6.42 points** gives that extreme event more influence.

{% include attribution-recovery-explorer.html %}

The portfolio lost money in **4 of the 11** 63-session windows. In the first 63 sessions
of the 2020 recovery, for example, shorted stocks gained **48.15% per unit
of exposure**, versus **31.80%** for the longs. But the larger long book
earned **17.18 P&L points**, while shorts lost **16.54**. After costs, the
portfolio was still up **0.43 points**. The **6.74-point loss** reported
earlier covers the much longer 214-session recovery through January 2021.
The portfolio's path matters as well as the stocks' relative rebound.

I also checked shorter and longer windows around the same lows (Table 4).
At 21 sessions, shorts were ahead in **9 of 11** episodes. By 126 sessions,
that fell to **3 of 11**, and the median gap had turned negative.

<div markdown="1">
<p class="table-caption"><strong>Table 4: The imbalance is more common early in the recovery.</strong> The same 11 lows at each horizon. Gap = short-stock gains minus long-stock gains per unit of exposure, in percentage points. Net losses use actual portfolio P&amp;L after saved trading costs.</p>

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
The horizons overlap and use market lows identified in hindsight.

## Daily risk and cumulative losses

The 2020–21 episode produces a seemingly contradictory result: the shorts
lost **13.46 P&L points**, yet Table 5 assigns them only **0.2% of the
portfolio's daily variance**. To decide what to change, I need to understand
how a book can look so small in the risk allocation while losing that much.

<div markdown="1">
<p class="table-caption"><strong>Table 5: A losing short book can have a small variance share.</strong> Realized variance shares (%) over the full history and each complete drawdown. Costs account for the small difference from 100%.</p>

| Period | Longs | Shorts |
| :--- | ---: | ---: |
| Full history | 59.6 | 40.4 |
| 2008–09 drawdown | 36.1 | 63.9 |
| 2020–21 drawdown | 99.9 | 0.2 |
{: .research-table .comparison-table .attribution-table }

</div>

The allocation gives the shorts credit for offsetting the rest of the
portfolio. Let $S_t$ be daily short-book P&L and $P_t$ total daily net P&L.
Their variance share is

$$
v_S=\frac{\operatorname{Cov}(S_t,P_t)}{\operatorname{Var}(P_t)}.
$$

The numerator combines the shorts' own variance with their covariance with
the rest of the portfolio. In 2020–21, the short book had **23.4% standalone
volatility**. But its daily fluctuations tended to offset those of the longs,
so the negative covariance almost cancelled its own variance in this
allocation. The combined portfolio's volatility was **13.1%**.

That offset says little about the shorts' accumulated earnings. Variance and
covariance measure deviations from average daily P&L; a negative average
can still add up to a large loss. They also discard the order of the days:
reordering the days leaves Table 5 unchanged,
even though it can change the portfolio's drawdown.

Figure 5 shows why this matters here. During the 2020 decline, shorts earned
**30.74 points**, cushioning the long losses. During the recovery, they lost
**44.19 points**, more than the longs gained. The **0.2% variance share**
reflects how shorts offset daily long-book fluctuations across the whole
episode. The cumulative P&L shows the protection during the decline and its
cost during the rebound. Removing the shorts would also remove their daily
offset against the longs.

I therefore need both measures when judging a short position: how much it
diversifies daily P&L, and what it earns or loses during the declines and
recoveries I care about. The next test is whether I can retain that protection
with less damage during rebounds.

## What I'd test next

The short book has two jobs: profit from stocks the model expects to do poorly
and offset some of the longs' risk. I want to know whether these particular
shorts earn their place, given that a simpler market hedge could provide some
of that protection.

I'd start with a permanent sizing rule for shorts where prior losses, high beta
and high volatility overlap. Sizing them more cautiously all the time avoids
having to recognise a market bottom in real time. I'd keep the predictions
fixed so I can see what changing the positions does.
Alongside smaller individual positions, I'd test a cap on these shorts'
combined risk, accounting for their correlations.

I'd also compare replacing part of those shorts with a broad market hedge,
matching the estimated market sensitivity of the shorts being replaced and
checking how the sector and style exposures change. I want to keep useful
short signals and protection during declines while reducing rebound losses.

I'd judge each position by its full contribution. Annaly, for example, lost
**0.20 points through the volatility component** during the complete 2020–21
drawdown but earned **0.85 points overall**. Removing it would remove both.
Likewise, adding a hedge changes several exposures at once. A losing factor
bar tells me where to look; I still need to check what the whole trade gives up.

I'd rerun the portfolio with these changes across ordinary periods and other
recoveries, allowing for trading costs, borrow and financing. I'd compare net
returns, drawdowns, turnover and protection during declines. These are proposed
tests. This history has already helped shape the model,
and the two major drawdowns have shaped the hypothesis.

## References

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
2021 edition, Chapters 3–4 and 7–8;
[*The Elements of Quantitative Investing*](https://linktr.ee/paleologo),
9 September 2024 draft, cross-sectional fitting in §7.2, physical PDF
pp. 216–218; attribution uncertainty in §14.2,
physical PDF pp. 456–459.

Kent Daniel and Tobias Moskowitz, [*Momentum Crashes*](https://www.kentdaniel.net/papers/published/jfe_16.pdf),
*Journal of Financial Economics*, 2016, Sections 2–3.

The [dashboard source code](https://github.com/piinghel/portfolio-pnl-dashboard)
is available if you'd like to explore your own portfolio.
