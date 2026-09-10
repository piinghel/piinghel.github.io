---
layout: post
title: "Performance Attribution, Part 1: Understanding Your P&L"
description: "The portfolio's market beta, factor exposures, and the positions behind its P&L and realized risk."
permalink: /quants/portfolio-attribution.html
toc: true
show_date: false
date: 2026-09-09
categories: ["Portfolio management"]
article_label: Performance attribution · Part 1 of 3
series_id: performance-attribution
series_order: 1
series_previous: /quants/2026/09/05/risk-concentration.html
series_next: /quants/short-book-rebounds.html
---

<p class="article-summary">The shorts offset daily fluctuations, but the portfolio retained a small positive market beta and suffered large losses in some rebounds. Attribution connects those outcomes to the positions and exposures I held.</p>

The short book lost money over the full history. Before cutting it back,
I want to know how much protection I'd give up and what drove those losses.
That means following the positions through both the falls and the rebounds.

I use the strategy from my
[optimizer article](/quants/2026/08/29/portfolio-optimization.html), which ranks
stocks with a prediction model and sizes them within risk limits.
The history runs from **23 September 1998 to 27 May 2026**.

<div id="pnl-conventions" markdown="1">
One **P&L point** means 1% of the same fixed strategy notional throughout.
Trading costs are 5 basis points per dollar traded, excluding borrow, financing
and market impact. Turnover is two-way traded notional divided by strategy
capital. Sharpe divides annualized net P&L by annualized volatility, using a
zero cash rate; collateral return and funding belong to the financing decision.
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

Figure 2 shows the dollar sizes behind that offset. The long book was
usually larger, leaving average net exposure of about **22% of notional**.
Its more defensive stocks partly offset that dollar imbalance; the beta
estimates below measure the whole book's market sensitivity.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/book-sizes" mobile="/assets/portfolio-attribution/book-sizes_mobile" version="1" alt="Long gross, short gross and their net difference as percentages of fixed strategy notional. The long book is usually larger." %}
</div>
<p class="figure-caption"><strong>Figure 2: The two books have different dollar sizes.</strong> Beginning-of-session exposures. Both gross series are positive; net is long gross minus short gross. Shading matches Figure 1.</p>

## How much market beta?
{: #portfolio-beta }

The portfolio's full-history realized beta to the Russell 1000 was **+0.068**.
I estimate it by regressing daily net P&L per unit of fixed strategy notional
on the index's daily price return, with an intercept.

Figure 3 follows trailing 126- and 252-session estimates above the model's
standardized beta exposure: signed positions multiplied by standardized stock
betas. Negative exposure favours lower-beta stocks relative to the universe.
The panels use different units. Centering stock betas and the net dollar
position help explain their difference, alongside changes in realized sensitivity.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/beta-history" mobile="/assets/portfolio-attribution/beta-history_mobile" version="2" alt="Trailing 126- and 252-session realized Russell 1000 beta above prior-session standardized beta exposure, with the 2008–09 and 2020–21 strategy drawdowns shaded." %}
</div>
<p class="figure-caption"><strong>Figure 3: Low average beta still leaves changing market sensitivity.</strong> Each regression requires a complete trailing window. Model exposure uses holdings entering each session and prior-session standardized beta loadings, available for 93.3% of gross exposure on an average day. Missing loadings contribute zero, the universe mean; dates with no coverage are gaps. Dots mark the two market lows; shading marks the strategy drawdowns. Each panel retains its own units and scale.</p>

<div markdown="1">
<p class="table-caption"><strong>Table 1: Whole-book beta and the fitted beta contribution.</strong> Realized beta is one regression over each period. Model exposure is its daily mean; beta P&amp;L sums the fitted contributions in points. The drawdown windows run from 30 July 2008 to 16 September 2009 and 21 February 2020 to 27 January 2021, excluding each peak day.</p>

| Period | Realized beta | Mean model exposure | Beta P&L |
| :--- | ---: | ---: | ---: |
| Full history | +0.068 | −0.309 | −15.13 |
| 2008–09 drawdown | +0.026 | −0.476 | −6.55 |
| 2020–21 drawdown | +0.140 | −0.442 | −4.53 |
{: .research-table .comparison-table .attribution-table }
</div>

At the 2009 and 2020 lows, the trailing 252-session market betas were
**+0.069 and +0.230**, while entering-session model exposures were
**−0.361 and −0.178**. A defensive style tilt coexisted with positive
whole-book market sensitivity.

The existing optimizer already limits its own estimated market beta to
**±0.05 at rebalance**. Its estimate combines long-window correlation with
short-window volatility; the attribution descriptor uses a 252-session
regression. Rebalance target beta averaged +0.018, but price moves,
changing holdings and estimation error can separate that target from
subsequent realized beta. The [optimizer study](/quants/2026/08/29/portfolio-optimization.html#forecast-beta-versus-realized-beta)
examines that gap and a shorter-window estimator. Part 3 tests an additional
limit on the standardized beta exposure shown here.

## Locate P&L and risk
{: #locate-earnings-and-risk }

I group the stock contributions by sector in Figure 4. To allocate
risk, I measure how each sector's daily P&L moves with the whole portfolio:

$$
v_j=\frac{\operatorname{Cov}(c_{j,t},P_t)}
           {\operatorname{Var}(P_t)}.
$$

Here $c_{j,t}$ is sector $j$'s daily contribution and $P_t$ is daily net
portfolio P&L. The variance shares add to 100%, including costs. A component
that offsets portfolio fluctuations can receive a negative share.
That distinction matters in the 2020–21 drawdown: the shorts lost more than
13 points despite receiving only 0.2% of portfolio variance.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/sector-pnl" mobile="/assets/portfolio-attribution/sector-pnl_mobile" version="5" alt="Sector P&L and share of net portfolio variance on matching rows, ranked by P&L." %}
</div>
<p class="figure-caption"><strong>Figure 4: Sector P&amp;L and risk contributions.</strong> Gross P&amp;L across both books. Variance shares include covariance with the portfolio; costs contribute −0.01%.</p>

Every sector made money before costs. Technology made the largest
contribution. Energy's long gains were almost cancelled by short losses,
leaving little P&L for its share of daily risk.

The sector breakdown only gets me so far. Stocks in different sectors can
share high beta or low volatility, so I also fit a factor model to see how
those shared characteristics contributed.

## Fit the factor returns
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
\underset{a_t,f_t,g_t}{\operatorname{minimize}}\;
\sum_{i\in U_t}q_{i,t-1}\varepsilon_{i,t}^{\,2},
\qquad q_{i,t-1}=\sqrt{\mathrm{cap}_{i,t-1}}.
$$

$U_t$ is the eligible universe with valid returns. A stock four times as large
gets twice the fitting weight. Prior-session characteristics and market caps
explain the session that has just finished.

To identify the common return and sector effects, I constrain the weighted
average sector effect to zero:

$$
\sum_s Q_{s,t}g_{s,t}=0,
\qquad Q_{s,t}=\sum_{i\in U_t:s(i)=s}q_{i,t-1}.
$$

The coefficients use unpenalized least squares, solved jointly by SVD.

</div>
</details>

## Apply the fit to the portfolio

To use the fit, I multiply each stock's loading by the signed position I
held and add them up. That gives the portfolio's exposure. Multiplying it
by the day's payoff gives the factor contribution:

$$
E_{k,t}=\sum_{i\in H_t}w_{i,t^-}z_{i,k,t-1},
\qquad c_{k,t}=E_{k,t}\widehat f_{k,t}.
$$

$H_t$ contains holdings covered by the fit. A 2% long with a volatility
loading of −1 contributes −0.02 to exposure. A 1% short with a loading of +2
also contributes −0.02. Together they hold **−0.04 units**. If the volatility
payoff is **+1%**, their contribution is **−0.04 P&L points**.
Higher-volatility stocks did better that day, while both positions favoured
lower volatility. Other factors and residuals complete each position's P&L.

I apply the same signed weights to the residuals, common return and sector
effects. Adding those pieces, uncovered holdings and costs reconstructs
portfolio P&L. Figure 5 shows the full-history allocation.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/factor-pnl" mobile="/assets/portfolio-attribution/factor-pnl_mobile" version="5" alt="Fitted components with P&L beside their signed variance shares, including residual, uncovered holdings and costs." %}
</div>
<p class="figure-caption"><strong>Figure 5: The fitted allocation of P&amp;L and risk.</strong> P&amp;L sums to +312.9 points net; variance shares sum to 100%. Sector terms account for the fitted styles.</p>

Momentum, volatility and reversal earned money; beta and size detracted.
The largest component was the **residual, +198.8 points**, with **45.2% of
realized variance**. It contains stock-specific outcomes and any common
effects the chosen model leaves unexplained, such as omitted value, quality
or industry characteristics.

The **common return contributed +84.1 points** through the net long position
in covered stocks. It is the fitted intercept under square-root-cap weighting.
Other factor and residual contributions offset much of its market sensitivity;
Figure 3 measures the resulting beta of the whole book.

The fit covered **93.1% of gross exposure** on average. Uncovered holdings
contributed **22.5 points**: a holding can lack a descriptor, sufficient price
history or an eligible sector label. Part 3 records this coverage and assigns
missing beta loadings the universe mean when imposing its beta limit.

Changing the factors reallocates P&L between fitted contributions and the
residual. Stock-picking skill and omitted common effects remain mixed there.

## Follow exposure and payoff together

Across days, I add the daily contributions:

$$
C_k(T)=100\sum_{t\le T}E_{k,t}\widehat f_{k,t}.
$$

Positions, stock characteristics and payoffs all change. Each day's
payoff therefore needs the exposure held on that day.

You can follow that calculation in Figure 6. The middle panel accumulates
payoffs for a constant +1 exposure; the bottom uses my actual changing
exposure. Move the slider to see how the two combine on a single day.

For readability, the volatility view follows the **low-volatility** bet.
I reverse both signs: model exposure −0.5 and volatility payoff +1% become
low-volatility exposure **+0.5** and payoff **−1%**. Their product remains
**−0.5 P&L points**. Low beta uses the same convention; momentum follows past
winners.

{% include attribution-dynamics.html %}
<p class="figure-caption"><strong>Figure 6: Exposure × payoff = portfolio P&amp;L.</strong> Daily standardized exposure and cumulative contributions in the two deepest drawdowns. Shading ends at the market low.</p>

Positive exposure gains when the payoff line rises; negative exposure gains
when it falls. In the 2009 momentum view, the exposure changes sign.
That allows portfolio P&L to recover while the momentum payoff keeps falling.

## Daily risk and accumulated losses
{: #judge-protection-over-the-path }

The 2020–21 drawdown illustrates why I need both P&L and variance
attribution. Shorts lost **13.5 points** while receiving just **0.2% of
portfolio variance**. Their standalone volatility was **23.4%**.
Their daily fluctuations largely offset those of the longs, so the covariance
allocation credits that offset even while the shorts accumulate losses.

Variance measures deviations around average daily P&L. Here the shorts earned
**30.7 points** during the market decline, then lost **44.2** during the
rebound.

So the shorts did provide protection, but the losses once the market
rebounded were substantial. Before changing the portfolio, I want to
understand why. In [part 2](/quants/short-book-rebounds.html), I look at the
stocks held on each side of the book.

<aside class="research-note" markdown="1">
**In-sample notes.** This is an explanation of inspected historical returns.
Sector labels use an August 2026 snapshot. Drawdowns and market lows are
selected in hindsight; the 2022–26 history also informed strategy research.
Forecast risk requires factor covariance and stock-specific risk estimates
calibrated at the intended horizon.
</aside>

## References

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
2021, Chapters 3–4 and 7–8; [*The Elements of Quantitative Investing*](https://linktr.ee/paleologo),
9 September 2024 draft, §7.2 (physical PDF pp. 216–218) and §14.2 (pp. 456–459).

The [dashboard source code](https://github.com/piinghel/portfolio-pnl-dashboard)
is available to explore your own portfolio.
