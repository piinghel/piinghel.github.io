---
layout: post
title: "Where the Portfolio Takes Risk—and Where It Makes Money"
article_label: Portfolio attribution · Working draft
permalink: /quants/portfolio-attribution.html
toc: true
show_date: false
---

<p class="article-summary">The short book can offset market exposure and still account for most of a portfolio's risk. It can also lose money while the portfolio earns a positive return. I start this attribution with the frozen constrained Ridge portfolio: reconcile every day's long, short, and trading-cost contributions, then ask how those same components covary with total P&L. The accounting locates the gains and losses. Explaining them as sector, style, or stock-selection returns requires another layer of evidence.</p>

This is a working draft. The book-level calculations below are reproduced from
saved backtests; the sector, style, and forecast-risk attribution is still to
be built. I am keeping it unpublished until those distinctions have been tested
through the holdings as well as the return series.

## Start with a P&L identity

The [optimizer article](/quants/2026/08/29/portfolio-optimization.html) ends
with a short-book drawdown that market beta explains poorly. Before adding a
new constraint, I want an account of what actually lost money.

I use its constrained Ridge portfolio with trading controls, split equally
across the three starting weeks. The [timing
article](/quants/2025/05/10/rebalancing-luck.html) explains that mixture. The
later sample runs from 3 January 2022 to 27 May 2026 and has already been reused
during research, so this analysis uses a period that has participated in model selection.

For daily P&L per unit of fixed strategy notional,

$$
r_{p,t}=c_{L,t}+c_{S,t}+c_{C,t}.
$$

The first two terms are signed before-cost contributions from the long and
short books. A rally in a stock sold short gives a negative short contribution.
The last term is the negative five-basis-point proportional trading charge.
These components reconcile to the saved net daily series before any chart or
statistic is produced. There is no balancing item labelled “other.” Borrow,
financing, and impact are absent from the underlying simulation, so they cannot
appear as measured contributions here.

## A drawdown needs linked contributions

Adding daily P&L answers how much the strategy earned per unit of its fixed
notional. It does not reproduce a compounded drawdown. To reconcile the latter,
let $$V_t=V_{t-1}(1+r_{p,t})$$ with $$V_0=1$$. The linked contribution of
component $$k$$ over the window is

$$
C_k=\sum_t V_{t-1}c_{k,t},
\qquad
\sum_k C_k=V_T-1.
$$

Every component on a given date receives the same prior net index level. This
is a transparent linking convention for the compounded performance index,
not a reconstruction of a financed account or a claim that the simulated
portfolio reinvested daily.

Table 1 applies it to the 24 sessions after the 28 December 2022 peak through
the 2 February 2023 trough. The daily observations begin on 29 December. The
long book helps, but its gain is less than half the short book's loss. Trading
cost is too small to explain this episode.

<table class="research-table comparison-table">
  <thead><tr><th>Component</th><th>Additive P&L</th><th>Linked contribution</th></tr></thead>
  <tbody>
    <tr><th scope="row">Long book, gross</th><td>+7.306 pp</td><td>+7.044 pp</td></tr>
    <tr><th scope="row">Short book, gross</th><td>−16.356 pp</td><td>−15.758 pp</td></tr>
    <tr><th scope="row">Trading cost</th><td>−0.120 pp</td><td>−0.116 pp</td></tr>
    <tr><th scope="row">Portfolio, net</th><td>−9.170 pp</td><td>−8.830 pp</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Equal-notional three-schedule portfolio, 29 December 2022–2 February 2023. Additive contributions sum daily normalized P&L; linked contributions sum to the compounded net loss. Displayed values are rounded.</p>

The optimization article assigns cost to each book before summing its daily
contributions. Here I separate cost so the bridge remains visible. Both
conventions reconcile, but mixing gross book contributions with a net portfolio
total would leave an unexplained gap.

## Risk contribution is a covariance, not a loss

A book's own volatility does not say how much risk it contributes alongside
the rest of the portfolio. For the realized daily component series, define

$$
RC_k=\sqrt{252}\,
\frac{\widehat{\operatorname{Cov}}(c_k,r_p)}
{\widehat\sigma(r_p)}.
$$

The signed contributions sum to annualized net portfolio volatility. A
negative contribution means the component covaries negatively with total
P&L; it is not a negative standalone volatility. I retain the trading-cost
component in this calculation to preserve the identity.

Table 2 uses the whole later period rather than estimating a risk profile from
the short drawdown alone. The long book produces a positive linked return,
while the short book loses money and contributes about 71% of realized net
variance. A covariance share answers a different question from the capital
allocated to either book.

<table class="research-table comparison-table">
  <thead><tr><th>Component</th><th>Linked return</th><th>Contribution to annual volatility</th><th>Share of net variance</th></tr></thead>
  <tbody>
    <tr><th scope="row">Long book, gross</th><td>+62.72 pp</td><td>+2.564 pp</td><td>29.05%</td></tr>
    <tr><th scope="row">Short book, gross</th><td>−16.15 pp</td><td>+6.265 pp</td><td>70.97%</td></tr>
    <tr><th scope="row">Trading cost</th><td>−6.40 pp</td><td>−0.002 pp</td><td>−0.02%</td></tr>
    <tr><th scope="row">Portfolio, net</th><td>+40.17 pp</td><td>8.827 pp</td><td>100.00%</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Book-level attribution, 3 January 2022–27 May 2026, using 1,103 daily observations. Linked returns are whole-period contributions, not annual returns. Risk shares equal each component's covariance with net P&L divided by net P&L variance; they may be negative.</p>

The tiny negative risk contribution of cost is a sample covariance, not a
reason to trade more. The charge subtracts return on every trading day. Its
timing happens to offset a negligible amount of variation in this sample.

These are ex-post contributions. They say where realized variation sat, not
where the optimizer intended to spend its risk budget. A forecast decomposition
must use the covariance matrix and weights available at the decision time,
then follow those holdings through execution and drift. Comparing the two
would locate the risk-model miss identified in the previous article.

## The short book is a location, not yet an explanation

This first pass changes the next question. I do not need another aggregate
Sharpe comparison to establish that the short book mattered. I need to know
whether its losses came from a few names, a shared sector or style exposure,
or a retention rule that kept deteriorating positions too long.

The next layer will join signed security-level P&L to point-in-time holdings
and classifications, with an explicit unclassified bucket. Sector sums should
reconcile exactly to book P&L. A style model has an additional estimation
problem: correlated factors can redistribute the fitted contribution, and
the residual is not automatically alpha. I would show that sensitivity before
giving the residual an economic name.

Finally, an accounting attribution cannot establish what a different decision
would have earned. Testing the retention rule requires a matched portfolio
replay with the same forecasts, information dates, and cost convention. The
attribution should tell me which counterfactual is worth running.

### Reproduction notes

The research project's `portfolio_optimization.pnl_attribution` command saves
`outputs/review/attribution/book_attribution.csv`, compact daily component
evidence, and a convention manifest. It uses the same source schedules as the
timing study. Before publication, complete the holdings-level reconciliation,
forecast-versus-realized risk comparison, and a figure that links the two
questions without mixing their units.
