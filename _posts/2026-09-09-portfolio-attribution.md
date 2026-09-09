---
layout: post
title: "Performance Attribution, Part 1: Understanding Your P&L"
description: "The portfolio's market beta, factor exposures, and the positions behind its earnings and realized risk."
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

<p class="article-summary">The shorts offset daily fluctuations, but the portfolio retained a small positive market beta and suffered large losses in some recoveries. Attribution connects those outcomes to the positions and exposures I held.</p>

My long–short strategy made money overall, while its shorts lost money.
Before changing the book, I want to understand what those positions
contributed: their earnings, their protection, and the common risks they carried.

I use the strategy from my
[optimizer article](/quants/2026/08/29/portfolio-optimization.html), which ranks
stocks with a prediction model and sizes them within risk limits.
The history runs from **23 September 1998 to 27 May 2026**.
One **P&L point** means 1% of the same fixed strategy notional throughout.

## Start with the positions

Each stock's daily contribution is its signed weight before the session
multiplied by its return. A short has a negative weight, so a price rise
produces a loss. I add these contributions across stocks and days, then
deduct trading costs.

The longs earned **444.27 points**, shorts lost **93.17**, and trading costs
took **38.18**, leaving **312.92 points net**. Figure 1 follows those earnings
through time.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/whole-history" mobile="/assets/portfolio-attribution/whole-history_mobile" version="4" alt="Cumulative long, short and net P&L above the portfolio drawdown, September 1998–May 2026." %}
</div>
<p class="figure-caption"><strong>Figure 1: The longs carried the accumulated result.</strong> Cumulative fixed-notional P&amp;L and drawdown. Net deducts 5 basis points per dollar traded. A fuller implementation would also charge borrow, financing and market impact. Shading marks the two deepest drawdowns.</p>

The two books had standalone annualized volatility of **16.7%** and
**16.4%**, but their daily P&L correlation was **−0.89**. Together, after
costs, portfolio volatility was **7.9%**. The shorts provided a substantial
daily offset while losing money over the history.

## How much market beta?
{: #portfolio-beta }

The portfolio's full-history realized beta to the Russell 1000 was **+0.068**.
I estimate it by regressing daily net P&L per unit of fixed strategy notional
on the index's daily price return, with an intercept. This is a leveraged
long–short portfolio with low average market sensitivity; its average net
dollar exposure was positive, at about 22% of notional.

Figure 2 follows the trailing 252-session estimate alongside the beta-style
exposure used in the attribution model below. That exposure adds signed
positions multiplied by standardized stock betas. A negative value means
the book favours lower-beta stocks relative to the model's universe.
The two panels have different units: market-return sensitivity above,
standardized exposure per strategy notional below.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/beta-history" mobile="/assets/portfolio-attribution/beta-history_mobile" version="1" alt="Trailing 252-session realized Russell 1000 beta above prior-session standardized beta exposure. Market beta is positive at both the 2009 and 2020 lows while beta-style exposure is negative." %}
</div>
<p class="figure-caption"><strong>Figure 2: Low average beta still leaves changing market sensitivity.</strong> September 1998–May 2026. Realized beta uses net fixed-notional P&amp;L and requires 252 sessions. Model exposure uses holdings entering each session and prior-session standardized beta loadings, available for 93.3% of gross exposure on an average day. Missing loadings contribute zero, the universe mean; dates with no coverage are gaps. Vertical lines mark the 2009 and 2020 market lows. Each panel retains its own units and scale.</p>

<div markdown="1">
<p class="table-caption"><strong>Table 1: Beta at the two market lows.</strong> The mean row averages available daily observations of each displayed series; it differs from fitting one regression over the full history. Model exposure uses the covered book and is available before the session; realized beta includes that session's return.</p>

| Observation | Rolling realized beta | Model beta exposure |
| :--- | ---: | ---: |
| Historical daily mean | +0.069 | −0.309 |
| 9 March 2009 | +0.069 | −0.361 |
| 23 March 2020 | +0.230 | −0.178 |
{: .research-table .comparison-table .attribution-table }
</div>

The existing optimizer already limits its own estimated market beta to
**±0.05 at rebalance**. Its estimate combines long-window correlation with
short-window volatility; the attribution descriptor uses a 252-session
regression. Rebalance target beta averaged +0.018, but price moves,
changing holdings and estimation error can separate that target from
subsequent realized beta. The [optimizer study](/quants/2026/08/29/portfolio-optimization.html#forecast-beta-versus-realized-beta)
examines that gap and a shorter-window estimator. Part 3 tests an additional
limit on the standardized beta exposure shown here.

## Locate earnings and risk

I can group the stock contributions by sector, as in Figure 3. To allocate
risk, I measure how each sector's daily P&L moves with the whole portfolio:

$$
v_j=\frac{\operatorname{Cov}(c_{j,t},P_t)}
           {\operatorname{Var}(P_t)}.
$$

Here $c_{j,t}$ is sector $j$'s daily contribution and $P_t$ is daily net
portfolio P&L. The variance shares add to 100%, including costs. A component
that offsets portfolio fluctuations can receive a negative share.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/sector-pnl" mobile="/assets/portfolio-attribution/sector-pnl_mobile" version="5" alt="Sector P&L and share of net portfolio variance on matching rows, ranked by earnings." %}
</div>
<p class="figure-caption"><strong>Figure 3: What each sector earned and the risk it contributed.</strong> September 1998–May 2026. Sector P&amp;L is gross across both books. Variance shares include covariance with the rest of the portfolio; costs contribute −0.01%.</p>

Every sector earned money before costs. Technology made the largest
contribution. Energy's long gains were almost cancelled by short losses,
leaving little earnings for its share of daily risk. That gives me a specific
book to investigate.

These totals reflect stock performance, position size and time held. Sector
labels follow the classification snapshot described in the in-sample notes below. Stocks across sectors can also share
characteristics such as high beta or low volatility; the factor model
measures those common exposures.

## Fit the common returns

Each day, I explain stock returns using their **prior-session**
characteristics: size, momentum, volatility, beta and short-term reversal,
plus sector indicators. I fit them jointly, so each coefficient measures the
return associated with that characteristic after accounting for the others.

$$
r_{i,t}=a_t+\sum_k z_{i,k,t-1}f_{k,t}
        +g_{s(i),t}+\varepsilon_{i,t}.
$$

For stock $i$, $a_t$ is the common return, $z_{i,k,t-1}$ its loading on style
$k$, $f_{k,t}$ the style's fitted return, and $g_{s(i),t}$ its sector effect.
The residual $\varepsilon_{i,t}$ is its realized return minus the fitted
return. A **factor payoff** is the fitted daily return for one unit of
exposure.

<details>
<summary>How I estimate the daily factor model</summary>
<div markdown="1">

I center and scale each descriptor across the eligible stock universe:

$$
z_{i,k,t-1}=\frac{x_{i,k,t-1}-\mu_{k,t-1}}{\sigma_{k,t-1}}.
$$

The mean and standard deviation use weights proportional to the square root
of market capitalization. A loading of +1 is one weighted standard deviation
above the descriptor's average. Ranked descriptors measure relative rank.

Size, momentum and volatility use the strategy's existing descriptors.
Volatility is a rank; beta uses up to 252 daily returns with 126 required;
reversal is the negative preceding five-session return.

I estimate that day's coefficients jointly by weighted least squares:

$$
\underset{a_t,f_t,g_t}{\operatorname{minimize}}\;
\sum_{i\in U_t}q_{i,t-1}\varepsilon_{i,t}^{\,2},
\qquad q_{i,t-1}=\sqrt{\mathrm{cap}_{i,t-1}}.
$$

$U_t$ is the eligible universe with valid returns. The fitting weight $q$
determines each observation's influence: a stock four times as large gets
twice the weight. Characteristics and market caps come from the prior session;
the fit explains the session that has just finished.

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

The portfolio's exposure combines each stock's loading with the signed
position actually held. Its daily factor contribution is that exposure
multiplied by the fitted return:

$$
E_{k,t}=\sum_{i\in H_t}w_{i,t^-}z_{i,k,t-1},
\qquad c_{k,t}=E_{k,t}\widehat f_{k,t}.
$$

$H_t$ contains holdings covered by the fit. A 2% long with a volatility
loading of −1 contributes −0.02 to exposure. A 1% short with a loading of +2
also contributes −0.02. Together they hold **−0.04 units**. If the volatility
payoff is **+1%**, their contribution is **−0.04 P&L points**.
Higher-volatility stocks did better that day, while both positions favoured
lower volatility. Other factors and stock-specific residuals also contribute
to each position's total.

I apply the same signed weights to the residuals, common return and sector
effects. Adding those pieces, uncovered holdings and costs reconstructs
portfolio P&L. Figure 4 shows the full-history allocation.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/factor-pnl" mobile="/assets/portfolio-attribution/factor-pnl_mobile" version="5" alt="Fitted components with P&L beside their signed variance shares, including residual, uncovered holdings and costs." %}
</div>
<p class="figure-caption"><strong>Figure 4: The fitted allocation of earnings and risk.</strong> P&amp;L sums to +312.92 points net; variance shares sum to 100%. The sector terms measure returns associated with sector membership after accounting for the fitted styles.</p>

Momentum, volatility and reversal earned money; beta and size detracted.
The largest component was the **residual, +198.82 points**, with **45.2% of
realized variance**. It contains stock-specific outcomes and any common
effects the chosen model leaves unexplained, such as omitted value, quality
or industry characteristics.

The **common return contributed +84.09 points**, weighted by the portfolio's
net position in covered stocks. The model covered **93.1% of gross exposure**
on average; uncovered positions contributed **22.49 points**.

Other factor and residual contributions can offset the common-return
component's market sensitivity. Figure 2 measures beta from the whole book.

The split depends on the estimated coefficients and chosen factors.
Assigning an extra point to factors takes a point from the residual while
preserving total P&L. Before interpreting the residual as stock-picking skill,
I would examine fitting uncertainty and alternative factor sets.

## Follow exposure and payoff together

Across days, I add the daily contributions:

$$
C_k(T)=100\sum_{t\le T}E_{k,t}\widehat f_{k,t}.
$$

Positions, stock characteristics and factor returns all change. Each day's
payoff therefore needs the exposure held on that day.

Figure 5 lets you inspect that multiplication. The middle panel accumulates
returns for a constant +1 exposure. The bottom accumulates P&L from our actual
changing exposure. The slider shows the calculation for one session.

For readability, the volatility view follows the **low-volatility** bet.
I reverse both signs: model exposure −0.5 and volatility payoff +1% become
low-volatility exposure **+0.5** and payoff **−1%**. Their product remains
**−0.5 P&L points**. Low beta uses the same convention; momentum follows past
winners.

{% include attribution-dynamics.html %}
<p class="figure-caption"><strong>Figure 5: Exposure × return per unit = portfolio P&amp;L.</strong> Daily standardized exposure and cumulative contributions in the two deepest drawdowns. Shading ends at the market low.</p>

Positive exposure gains when the payoff line rises; negative exposure gains
when it falls. In the 2009 momentum view, the exposure changes sign.
That allows portfolio P&L to recover while the momentum payoff keeps falling.

## Daily risk and accumulated losses
{: #judge-protection-over-the-path }

The 2020–21 drawdown illustrates why I need both earnings and variance
attribution. Shorts lost **13.46 points** while receiving just **0.2% of
portfolio variance**. Their standalone volatility was **23.4%**.
Their daily fluctuations largely offset those of the longs, so the covariance
allocation credits that offset even while the shorts accumulate losses.

Variance measures deviations around average daily P&L. Here the shorts earned
**30.74 points** during the market decline, then lost **44.19** during the
recovery.

The shorts reduced daily fluctuations, yet lost heavily once the market
recovered. In [part 2](/quants/short-book-rebounds.html), I examine the stocks
held on each side to understand why that protection reversed.

<aside class="research-note" markdown="1">
**In-sample notes.** This is an explanation of inspected historical returns.
Sector labels use an August 2026 snapshot; the illustrated drawdowns and market
lows are selected retrospectively. Model coverage is incomplete, and the later
2022–26 history has also informed strategy research. The variance shares
allocate realized fluctuations, including covariance with the portfolio.
Forecasting future risk would additionally require factor covariance and
stock-specific risk estimates, calibrated at the intended horizon.
</aside>

## References

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
2021, Chapters 3–4 and 7–8; [*The Elements of Quantitative Investing*](https://linktr.ee/paleologo),
9 September 2024 draft, §7.2 (physical PDF pp. 216–218) and §14.2 (pp. 456–459).

The [dashboard source code](https://github.com/piinghel/portfolio-pnl-dashboard)
is available to explore your own portfolio.
