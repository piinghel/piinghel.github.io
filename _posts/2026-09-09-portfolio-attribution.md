---
layout: post
title: "Performance Attribution, Part 1: Understanding Your P&L"
description: "The portfolio's market beta, factor exposures, and the positions behind its P&L and realized risk."
permalink: /quants/portfolio-attribution.html
toc: true
date: 2026-09-09
last_modified_at: 2026-09-27
categories: ["Risk & attribution"]
article_label: Performance attribution · Part 1 of 3
series_id: performance-attribution
series_order: 1
github_repositories:
  - label: Dashboard source code
    url: https://github.com/piinghel/portfolio-pnl-dashboard
---

<p class="article-summary">A return chart shows how the portfolio did. Attribution helps explain why. I break down P&amp;L and risk by positions, sectors and shared stock characteristics, then look at what those views reveal during drawdowns.</p>

Once I've built a portfolio, I want to understand what is driving it.
Are returns coming from a few stocks, a sector, or a broader preference for
things like momentum and low volatility? And when the portfolio struggles,
is that same preference behind the losses?

Those questions matter before changing the strategy. A position that loses
money can still offset risk elsewhere, while several apparently different
stocks can depend on the same market move. Looking only at total returns
makes it hard to tell which part deserves a closer look.

I'll start with the positions, then group their contributions by sector and
factor. Along the way, I'll compare accumulated profit and loss (P&L) with
contributions to daily risk. That gives the rest of this series its starting
point: Part 2 looks at why the short book lost money when markets rebounded,
and Part 3 tests ways to reduce those losses.

I use the strategy from my
[optimizer article](/quants/2026/08/29/portfolio-optimization.html), which ranks
stocks with a prediction model and sizes them within risk limits. The
ranking comes from an earlier version of the Ridge model in my
[multiple-predictors article](/quants/2025/02/09/multiple-linear-regression.html),
and the book combines three rebalance schedules at equal notional.
The history runs from **23 September 1998 to 27 May 2026**.

<div id="pnl-conventions" markdown="1">
One **P&L point** is 1% of strategy notional, which stays fixed throughout.
Trading costs are 5 basis points per dollar traded, excluding borrow, financing
and market impact. Turnover is two-way traded notional divided by strategy
notional. Sharpe divides annualized net P&L by annualized volatility, using a
zero cash rate.
</div>

## Start with the positions

Each stock's daily contribution is its signed weight before the session
multiplied by its return. A short has a negative weight, so a price rise
produces a loss. I add these contributions across stocks and days, then
deduct trading costs.

The longs gained **444.3 points**, shorts lost **93.2**, and trading costs
took **38.2**, leaving **312.9 points net**. Figure 1 follows the P&L
through time.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/whole-history" mobile="/assets/portfolio-attribution/whole-history_mobile" version="4" alt="Cumulative long, short and net P&L above the portfolio drawdown, September 1998–May 2026." %}
</div>
<p class="figure-caption"><strong>Figure 1: The longs carried the accumulated result.</strong> Cumulative P&amp;L and drawdown. Shading marks the two deepest strategy drawdowns.</p>

The two books had standalone annualized volatility of **16.7%** and
**16.4%**, but their daily P&L correlation was **−0.89**. Together, after
costs, portfolio volatility was **7.9%**.

Figure 2 shows the dollar sizes behind that offset. At each rebalance the
optimizer caps forecast beta at ±0.05 and net exposure at ±25%. Because the
longs hold lower-beta stocks than the shorts, keeping forecast beta near zero
pushes the book net long, up against the net cap: the median is **24.4% of
notional**, and drift between rebalances takes it above 25% on about 40% of
days.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/book-sizes" mobile="/assets/portfolio-attribution/book-sizes_mobile" version="2" alt="Long gross, short gross and their net difference as percentages of fixed strategy notional. The long book is usually larger." %}
</div>
<p class="figure-caption"><strong>Figure 2: The long book is usually larger.</strong> Beginning-of-session gross exposures and net (long minus short), as a percentage of strategy notional. Shading matches Figure 1.</p>

## Locate P&L and risk
{: #locate-earnings-and-risk }

I group the stock contributions by sector in Figure 3. To allocate
risk, I measure how each sector's daily P&L moves with the whole portfolio:

$$
v_j=\frac{\operatorname{Cov}(c_{j,t},P_t)}
           {\operatorname{Var}(P_t)}.
$$

Here $c_{j,t}$ is sector $j$'s daily contribution and $P_t$ is daily net
portfolio P&L. The variance shares add to 100%, including costs. A component
that offsets portfolio fluctuations can receive a negative share.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/sector-pnl" mobile="/assets/portfolio-attribution/sector-pnl_mobile" version="5" alt="Sector P&L and share of net portfolio variance on matching rows, ranked by P&L." %}
</div>
<p class="figure-caption"><strong>Figure 3: Sector P&amp;L and risk contributions.</strong> Gross P&amp;L across both books; sectors use an August 2026 classification snapshot. Costs contribute −0.01% of variance.</p>

Every sector made money before costs. Technology made the largest
contribution. In energy, the longs made **+17.6 points** and the shorts lost
**15.3**, leaving little P&L for its share of daily risk.

The sector breakdown only gets me so far. Stocks in different sectors can
share high beta or low volatility, so I also fit a factor model to see how
those shared characteristics contributed.

## Factor model
{: #fit-the-common-returns }

Each day, I explain stock returns using their **prior-session**
characteristics: size, momentum, volatility, beta and short-term reversal,
plus sector indicators. I fit them jointly, so each coefficient measures the
return associated with that characteristic after accounting for the others.

$$
r_{i,t}=a_t+\sum_k z_{i,k,t-1}f_{k,t}
        +g_{s(i),t}+\varepsilon_{i,t}.
$$

For stock $i$, $a_t$ is the common return, $z_{i,k,t-1}$ its loading on style
$k$, $f_{k,t}$ its **payoff**—the fitted daily return per unit of exposure—and
$g_{s(i),t}$ its sector effect.
The residual $\varepsilon_{i,t}$ is its realized return minus the fitted
return.

<details>
<summary>How I estimate the daily factor model</summary>
<div markdown="1">

I center and scale each descriptor across the eligible stock universe:

$$
z_{i,k,t-1}=\frac{x_{i,k,t-1}-\mu_{k,t-1}}{\sigma_{k,t-1}}.
$$

The mean and standard deviation use square-root-market-cap weights. A loading
of +1 is one weighted standard deviation above the descriptor's average.

Size, momentum and volatility use the strategy's existing descriptors.
Volatility is a rank; beta uses up to 252 daily returns with 126 required.
I standardize raw estimated betas without first shrinking them towards one,
so estimation noise remains in the descriptor. Reversal is the negative
preceding five-session return: a positive loading denotes a recent loser,
and a positive reversal payoff means those losers bounced, after accounting
for the other fitted characteristics.

I estimate that day's coefficients jointly by weighted least squares:

$$
\begin{gathered}
\underset{a_t,f_t,g_t}{\operatorname{minimize}}\;
\sum_{i\in U_t}q_{i,t-1}\varepsilon_{i,t}^{\,2},\\[6pt]
q_{i,t-1}=\sqrt{\mathrm{cap}_{i,t-1}}.
\end{gathered}
$$

$U_t$ is the eligible universe with valid returns. A stock four times as large
gets twice the fitting weight.

To identify the common return and sector effects, I constrain the weighted
average sector effect to zero:

$$
\sum_s Q_{s,t}g_{s,t}=0,
\qquad Q_{s,t}=\sum_{i\in U_t:s(i)=s}q_{i,t-1}.
$$

</div>
</details>

## From factor returns to portfolio P&L
{: #apply-the-fit-to-the-portfolio }

To use the fit, I multiply each stock's loading by its signed portfolio
weight entering the session, $w_{i,t^-}$, and add them up. That gives the
portfolio's exposure. Multiplying it by the day's fitted payoff
$\widehat f_{k,t}$ gives the factor contribution:

$$
E_{k,t}=\sum_{i\in H_t}w_{i,t^-}z_{i,k,t-1},
\qquad c_{k,t}=E_{k,t}\widehat f_{k,t}.
$$

$H_t$ contains holdings covered by the fit. A 2% long with a volatility
loading of −1 contributes −0.02 to exposure. A 1% short with a loading of +2
also contributes −0.02. Together they hold **−0.04 units**. If the volatility
payoff is **+1%**, their contribution is **−0.04 P&L points**.
Higher-volatility stocks did better that day, while both positions favored
lower volatility. Other factors and residuals complete each position's P&L.

I apply the same signed weights to the residuals, common return and sector
effects. Adding those pieces, uncovered holdings and costs reconstructs
portfolio P&L. Figure 4 shows the full-history allocation.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/factor-pnl" mobile="/assets/portfolio-attribution/factor-pnl_mobile" version="8" alt="Fitted components with P&L beside their signed variance shares, including residual, uncovered holdings and costs." %}
</div>
<p class="figure-caption"><strong>Figure 4: The fitted allocation of P&amp;L and risk.</strong> P&amp;L sums to +312.9 points net and the components reconcile exactly. Sector effects are what remains of sector returns after the styles, so they differ from the sector P&amp;L in Figure 3.</p>

Momentum, volatility and reversal earned money; beta and size detracted.
The largest component was the **residual, +198.8 points**, with **45.2% of
realized variance**. It contains stock-specific outcomes and any common
effects the model leaves out, such as value, quality or industry
characteristics, so I'd be cautious about calling it stock-picking skill; a
different factor set could move some of it into named exposures.

The **common return contributed +84.1 points** through the net long position
in covered stocks.

The fit covered **93.2% of gross exposure** on average. Uncovered holdings
contributed **22.5 points**: a holding can lack a descriptor, sufficient price
history or an eligible sector label.

## Follow exposure and payoff together
{: #follow-exposure-and-payoff-together }

Across days, I add the daily contributions:

$$
C_k(T)=100\sum_{t\le T}E_{k,t}\widehat f_{k,t}.
$$

The factor of 100 turns fractions of notional into P&L points. Because
positions, characteristics and payoffs all change, each day's payoff has to be
paired with that day's exposure.

You can follow that calculation in Figure 5. The middle panel accumulates
payoffs for a constant +1 exposure; the bottom uses the portfolio's changing
exposure. Move the slider to see how the two combine on a single day.

For beta and volatility I flip the sign of both exposure and payoff, so a
rising line means the low-beta or low-volatility side gained; the product is
unchanged.

{% include attribution-dynamics.html %}
<p class="figure-caption"><strong>Figure 5: Exposure × payoff = portfolio P&amp;L.</strong> Daily standardized exposure and cumulative contributions in the two deepest drawdowns. Shading ends at the market low.</p>

In the 2009 momentum view, the exposure changes sign, which lets portfolio P&L recover while the momentum payoff keeps falling.

## Market beta
{: #portfolio-beta }

Three beta measures appear in this series. The optimizer's **forecast beta**
is the estimate it caps at ±0.05 at each rebalance. The **realized beta** regresses
daily net P&L per unit of strategy notional on the Russell 1000's daily price
return, with an intercept; over the full history it was **+0.068**. The
**standardized beta exposure** is the factor model's beta exposure, $E_{k,t}$
for the beta style; it averaged **−0.308**, so the book favored stocks with
lower beta than the universe while staying net long in dollars.

The positive realized beta comes from the common return. Regressed on the index
in the same way, that component has a beta of **+0.25**; the negative beta and
volatility exposures offset most of it (**−0.09** and **−0.05**), and uncovered
holdings and the residual take off a little more.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/beta-history" mobile="/assets/portfolio-attribution/beta-history_mobile" version="5" alt="Trailing 252-session realized Russell 1000 beta above the standardized beta exposure, with the 2008–09 and 2020–21 strategy drawdowns shaded." %}
</div>
<p class="figure-caption"><strong>Figure 6: Low average beta still leaves changing market sensitivity.</strong> Realized beta over the trailing 252 sessions; standardized beta exposure uses holdings entering each session and prior-session loadings, with uncovered holdings at zero. Dots mark the 2009 and 2020 market lows; shading marks the strategy drawdowns.</p>

<div markdown="1">
<p class="table-caption"><strong>Table 1: Whole-book beta and the fitted beta contribution.</strong> Realized beta is one regression over each period; standardized beta exposure is its daily mean; beta P&amp;L sums the fitted contributions in points. The drawdown windows run from 30 July 2008 to 16 September 2009 and 21 February 2020 to 27 January 2021, excluding each peak day.</p>

| Period | Realized beta | Standardized beta exposure | Beta P&L |
| :--- | ---: | ---: | ---: |
| Full history | +0.068 | −0.308 | −15.13 |
| 2008–09 drawdown | +0.026 | −0.476 | −6.55 |
| 2020–21 drawdown | +0.140 | −0.442 | −4.53 |
{: .research-table .comparison-table .compact-table }
</div>

At the 2009 and 2020 lows, the trailing market betas were **+0.069 and
+0.230**, while standardized beta exposures were **−0.361 and −0.178**. A
defensive style tilt coexisted with positive whole-book market sensitivity.
The tilt still cost money in both drawdowns: **6.55** and **4.53 points**,
roughly 40% and 28% of the 16.3- and 16.1-point losses, even in 2008–09, when
the book's realized beta was only +0.026.
Price moves, changing holdings and estimation error pull realized beta away
from the forecast; the
[optimizer study](/quants/2026/08/29/portfolio-optimization.html#forecast-beta-versus-realized-beta)
examines that gap and a shorter-window estimator. Part 3 tests an additional
limit on the standardized beta exposure.

## Daily risk and accumulated losses
{: #judge-protection-over-the-path }

The 2020–21 drawdown illustrates why I need both P&L and variance
attribution. Shorts lost **13.5 points** yet received just **0.2% of portfolio variance**, despite **23.4%** standalone volatility.
Their daily fluctuations largely offset those of the longs, so the covariance
allocation credits that offset even while the shorts accumulate losses.

Variance share measures how the shorts' daily swings move with the portfolio's;
it says nothing about their drift.

So, back to the opening questions. The P&L is broad rather than
concentrated: the book held about 2,900 stocks over the history, the top 20 contributed 57 of the 351
gross points, the largest single name 5.6, and every sector made money. The
named styles added about 40 points net; most of the rest is the common return
from the net long book and the residual. The losses are less clear-cut. The
low-beta preference did cost money in both deep drawdowns, but the bigger
swing was in the shorts: in both episodes they made about 31 points while the
market fell and lost 44 to 49 after the low, more than the longs recovered.

This is what I find useful about attribution: it changes the question from
whether the shorts made money overall to when they helped and when they hurt.
Here, the rebound losses deserve a closer look. In
[Part 2](/quants/short-book-rebounds.html), I turn to the stocks on each side
to understand why the recovery was so difficult for the portfolio.

## References

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
2021, Chapters 3–4 and 7–8; [*The Elements of Quantitative Investing*](https://linktr.ee/paleologo),
9 September 2024 draft, §7.2 and §14.2.

The [dashboard source code](https://github.com/piinghel/portfolio-pnl-dashboard)
is available to explore your own portfolio.
