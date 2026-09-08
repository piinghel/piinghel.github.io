---
layout: post
title: "Understanding portfolio performance attribution"
description: "Following portfolio P&L through holdings, risk contributions, factors and saved predictions."
article_label: Portfolio attribution · Working draft
permalink: /quants/portfolio-attribution.html
toc: true
show_date: false
published: false
navigation: false
---

<p class="article-summary">I want to understand how a portfolio earned its return: which positions contributed, how they interacted, and what the model was seeing while the positions were held. This article works from the daily P&L ledger towards risk, factor attribution and individual predictions, using the dashboard I built to keep those views connected.</p>

This is a working draft that I intend to develop as I work through the attribution.
The [public dashboard](https://piinghel-portfolio-pnl.streamlit.app/) uses synthetic
data. The historical example below comes from the saved research portfolio;
the two should not be compared as if they were the same strategy.

## Follow the loss back to the positions

The [optimizer article](/quants/2026/08/29/portfolio-optimization.html) raises a
question about losses on the short side. Before changing a constraint, I want
to understand where those losses accumulated and what decisions put the
portfolio there.

I separate four questions. **P&L attribution** locates the gains and losses.
**Risk attribution** measures how each component contributed to portfolio
variation. **Factor attribution** decomposes returns under a particular model.
**Prediction explanations** reconstruct the score used to assess a stock.
Keeping those questions distinct makes it easier to connect their answers.

Here I attribute the portfolio's own P&L. Attribution relative to a benchmark
would need an additional definition of active weights and returns. The optional
benchmark line in the dashboard is a separate reference; it does not enter
the portfolio's P&L partition.

I use its constrained Ridge portfolio with trading controls, split equally
across the three starting weeks. The [timing
article](/quants/2025/05/10/rebalancing-luck.html) explains that mixture. The
saved portfolio ends on 27 May 2026. This history has already participated in
model selection; the examples are retrospective diagnostics.

## Start with the daily P&L

For a simple price-only position in one currency, daily contribution can be
written as

$$
c_{i,t}=\frac{q_{i,t^-}(P_{i,t}-P_{i,t-1})}{N}
       =w_{i,t^-}r_{i,t}.
$$

Here $$N$$ is fixed strategy notional, $$q_{i,t^-}$$ is the signed position held
over the price move, and $$w_{i,t^-}$$ is its signed starting dollar exposure
divided by $$N$$. The position is negative for a short. The price and holdings
bases must agree, including adjustments for splits and other corporate actions.

Suppose a short position starts at 2% of fixed notional and the stock rises
10%. Its contribution is $$-0.02\times0.10=-0.002$$: a loss of **0.20 percentage
points of portfolio notional**, before costs. This example holds the position
fixed over the move. With trading during the period, I need the actual daily
holdings and P&L; multiplying the period's stock return by its final weight
would give a different calculation.

Summing securities by their actual daily holding side gives

$$
r_{p,t}=c_{L,t}+c_{S,t}+c_{C,t}.
$$

The first two terms are signed before-cost contributions from the long and
short books. A rally in a stock sold short gives a negative short contribution.
The last term is the negative five-basis-point proportional trading charge.
These components reconcile to the saved net daily series before any chart or
statistic is produced. Borrow, financing and market impact are absent from
this simulation. Its net P&L is therefore net of the recorded trading charge.

Long and short contributions use the **same fixed notional**. Renormalizing
each side to 100% would change the question and break this reconciliation.
Shared costs remain a separate component; I do not invent a cost allocation
to individual stocks. When the chart shows only the largest contributors,
“Other” contains the exact sum of the omitted rows.

## Adding P&L through time

The dashboard accumulates daily contributions on fixed notional:

$$
A_t=\sum_{s\le t}r_{p,s},\qquad
D_t=A_t-\max(0,A_1,\ldots,A_t).
$$

The drawdown is the distance below the earlier peak of this additive path,
in units of fixed notional. The initial zero is included. When I narrow the
view, the total drawdown chart retains earlier peaks, while period P&L is
recalculated for the selected dates.

Table 1 shows the 24 sessions from 29 December 2022 through 2 February 2023.
The long book earned 7.306 percentage points, but the short book lost 16.356.
Recorded trading costs account for another 0.120 points. That places the
first investigation on the short holdings: the long gains were less than
half the short losses.

<p class="table-caption"><strong>Table 1:</strong> Saved equal-notional three-schedule portfolio, 29 December 2022–2 February 2023. Signed additive P&L in percentage points of fixed notional. Values are rounded; the underlying contributions reconcile to net P&L.</p>

<table class="research-table comparison-table">
  <thead><tr><th>Component</th><th>Additive P&L</th></tr></thead>
  <tbody>
    <tr><th scope="row">Long book, gross</th><td>+7.306 pp</td></tr>
    <tr><th scope="row">Short book, gross</th><td>−16.356 pp</td></tr>
    <tr><th scope="row">Trading costs</th><td>−0.120 pp</td></tr>
    <tr><th scope="row">Portfolio, net</th><td>−9.170 pp</td></tr>
  </tbody>
</table>

That finding does not tell me what removing shorts would have earned. A
long-only alternative would need its own sizing, capital and risk constraints.
The observed long contribution is one component of the portfolio that actually
ran.

### When returns are compounded

Adding daily P&L answers how much the strategy earned per unit of its fixed
notional. It does not reproduce a compounded drawdown. To reconcile the latter,
let $$V_t=V_{t-1}(1+r_{p,t})$$ with $$V_0=1$$. The linked contribution of
component $$k$$ over the window is

$$
C_k=\sum_t V_{t-1}c_{k,t},
\qquad
\sum_k C_k=V_T-1.
$$

Every component on a date receives the same prior net index level. For an
episode beginning after a peak, I reset the index to 1 at that peak and start
with the following session's P&L. This makes the linked contributions add to
the compounded change over that episode.

A two-day example shows why the distinction matters. Returns of +10% and
−10% add to zero, while an index moves from 1 to 1.10 to 0.99. Applying the
prior index level gives linked contributions of +10% and −11%, adding to −1%.
The dashboard uses the additive convention. The linked convention below
describes a separately constructed compounded index.

<details>
<summary>Earlier draft: linked drawdown contributions</summary>
<div markdown="1">

Table 2 retains the linked figures from the earlier draft. Their original
export still needs to be recovered and matched before publication; only the
additive totals in Table 1 have been reconfirmed in this editing pass.

<p class="table-caption"><strong>Table 2:</strong> Provisional linked contributions, 29 December 2022–2 February 2023, with the net index reset to 1 at the preceding peak. These are not the additive values displayed by the dashboard.</p>

<table class="research-table comparison-table">
  <thead><tr><th>Component</th><th>Linked contribution</th></tr></thead>
  <tbody>
    <tr><th scope="row">Long book, gross</th><td>+7.044 pp</td></tr>
    <tr><th scope="row">Short book, gross</th><td>−15.758 pp</td></tr>
    <tr><th scope="row">Trading costs</th><td>−0.116 pp</td></tr>
    <tr><th scope="row">Portfolio, net</th><td>−8.830 pp</td></tr>
  </tbody>
</table>

</div>
</details>

## How a component contributes to risk

A book's own volatility does not say how much risk it contributes alongside
the rest of the portfolio. For the realized daily component series, define

$$
RC_k=\sqrt{252}\,
\frac{\widehat{\operatorname{Cov}}(c_k,r_p)}
{\widehat\sigma(r_p)}.
$$

The numerator measures how the component's daily P&L moves with total daily
P&L. The denominator converts that covariance into a contribution to
volatility. The factor $$\sqrt{252}$$ applies the dashboard's current daily
annualization convention.

The signed contributions sum to annualized net portfolio volatility because
$$\sum_k\operatorname{Cov}(c_k,r_p)=\operatorname{Var}(r_p)$$. Dividing each
covariance by portfolio variance instead gives its share of variance. All
components must use the same dates, including zero contributions on flat
sessions and the separately recorded costs. If portfolio variance is zero,
these shares are undefined.

A component with negative covariance reduces observed portfolio variation.
Its own volatility remains positive. Shares can also exceed 100% when other
components offset some of that variation. This is why ranking stocks by
their own volatility gives a different answer from ranking their contribution
to portfolio risk.

P&L and risk can disagree for a simple reason: P&L concerns the sum of the
observations; covariance concerns their co-movement around their means. A
position can lose money over the period while tending to help on the
portfolio's worse days. I therefore want the contribution to P&L and the
contribution to risk side by side, on the same selected dates.

<details>
<summary>Earlier draft: whole-period risk and linked returns</summary>
<div markdown="1">

Table 3 preserves the earlier draft's comparison over
3 January 2022–27 May 2026. Its original numerical export still needs to be matched before these
values can support a final interpretation. It is a different window from
Table 1, so its risk shares cannot be used as the risk split of that drawdown.

<p class="table-caption"><strong>Table 3:</strong> Provisional earlier-draft values for 1,103 daily observations. Linked returns are whole-period contributions; volatility contributions are annualized. These figures have not been reverified for this combined draft.</p>

<table class="research-table comparison-table">
  <thead><tr><th>Component</th><th>Linked return</th><th>Contribution to annual volatility</th><th>Share of net variance</th></tr></thead>
  <tbody>
    <tr><th scope="row">Long book, gross</th><td>+62.72 pp</td><td>+2.564 pp</td><td>29.05%</td></tr>
    <tr><th scope="row">Short book, gross</th><td>−16.15 pp</td><td>+6.265 pp</td><td>70.97%</td></tr>
    <tr><th scope="row">Trading cost</th><td>−6.40 pp</td><td>−0.002 pp</td><td>−0.02%</td></tr>
    <tr><th scope="row">Portfolio, net</th><td>+40.17 pp</td><td>8.827 pp</td><td>100.00%</td></tr>
  </tbody>
</table>

If confirmed, the negative cost contribution to volatility would describe
the timing of costs relative to portfolio P&L. Costs still subtract from
the total return.

</div>
</details>

### Forecast risk and realized risk

The covariance calculation above uses the P&L of holdings that changed through
the historical window. Forecast risk asks how the holdings at a particular
decision time might behave under the covariance model available then. Its
portfolio volatility is $$\sqrt{w^\top\Sigma w}$$, with weights and covariance
in consistent units.

Comparing the two requires attention to horizon, changes in holdings and model
coverage. A missing forecast for part of the book must remain missing; treating
it as zero or scaling up the covered positions would change the portfolio
being described. A discrepancy is a useful diagnostic, but a single realized
episode cannot identify which covariance estimate was wrong.

## Stocks, sectors and factors

Grouping stock P&L by sector answers where the gains and losses occurred.
Every stock's complete contribution goes into its classification. A sector
factor answers a different question: how much P&L the attribution model assigns
to that shared exposure after accounting for its other factors.

For example, profitable stocks in one industry might earn their gains through
momentum exposure or stock-specific residual returns even while the model's
industry component loses money. Both decompositions can reconcile to the same
portfolio. Adding their totals together would count the same P&L twice.

In a linear factor attribution, I write the stock return as

$$
r_{i,t}=\sum_k b_{i,k,t^-}f_{k,t}+\varepsilon_{i,t}.
$$

The loadings $$b$$ describe the stock's exposures before the return;
$$f$$ contains the period's factor returns. Multiplying by signed starting
weights and adding across holdings produces each factor's portfolio P&L.
The residual collects the part of modeled stock returns left unexplained by
that specification. A common intercept, when present, can be represented as
a factor with loading 1; it needs its own interpretation rather than being
automatically labelled market beta.

Paleologo develops this progression from total P&L to factor groups and
individual factors in *Advanced Portfolio Management*, first edition (2021),
§8.1.1, printed pp. 124–126 (physical PDF pp. 136–138). It is a useful way to
organise the investigation: first locate a component, then examine what is
inside it. [Book details](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6).

For the dashboard, the complete bridge also retains trading costs, uncovered
holdings and any reconciliation difference between ledger and model P&L.
Those terms should remain identifiable. A large residual can reflect omitted
factors or imperfect loadings as well as stock-specific outcomes; its name
alone does not establish alpha.

The current classification sidecars are retrospective. They are useful for
describing the saved holdings but do not establish which industry classification
was available when a trade was chosen. Likewise, attributing P&L to correlated
factors depends on the specification. I want to inspect that dependence before
turning a factor label into an economic explanation.

## Connecting the charts

I built the dashboard so that I can follow this investigation without losing
the selected dates. I start with a drawdown or an unusually strong month,
then inspect stock, sector, industry and factor contributions. Clicking a stock
bar opens its history; returning brings me back to the same breakdown.

The stock view stacks **price → cumulative P&L → position size → predictor
contributions → model inputs** on one date axis. Price defaults to a logarithmic
scale. Dragging across a shorter period recalculates the analysis, and Reset
period restores the wider selection.

I read the first three panels together. Did the price move against the
position? Was the position already large, or did it grow through trading or
price drift? Was the loss spread across sessions or concentrated in one move?
Holding markers locate changes in the saved positions; verifying execution
would require the corresponding trade records.

### What the predictor panels explain

For a saved linear prediction, the score is

$$
s_{i,t}=a_t+\sum_j\theta_{j,t}x_{i,j,t}.
$$

The contribution panel displays $$\theta_{j,t}x_{i,j,t}$$ in model-score units;
the input panel shows the saved transformed input $$x_{i,j,t}$$. These are
different quantities from realized factor P&L. A contribution can change
because the input changed or because a refit changed its coefficient.

The displayed top predictors are only part of the score. The remaining terms
and intercept can offset them, so I check the full saved explanation before
interpreting the heatmap's colour as the model's overall view. Empty trading
sessions stay blank when predictions are missing.

The next distinction is between a score and a position. The public demo has
a simple top-N selection rule. In an optimized strategy, sizing, constraints,
turnover controls and existing holdings also affect the decision. The score
explains a model output; explaining a trade requires that additional decision
context.

## Working through the attribution

For the next pass, I want to follow the selected drawdown from the reconciled
book totals to the stocks and factor exposures underneath it. I will compare
the loss concentration with the risk contributions over those same dates,
then use the position and predictor histories to identify a specific decision
worth examining.

Finally, an accounting attribution cannot establish what a different decision
would have earned. Testing the retention rule requires a matched portfolio
replay with the same forecasts, information dates, and cost convention. The
attribution should tell me which counterfactual is worth running.

The [public dashboard](https://piinghel-portfolio-pnl.streamlit.app/) is available
to try, with fictional companies, prices, holdings and predictions. Its
[source code and bundle format](https://github.com/piinghel/portfolio-pnl-dashboard)
are available for exploring another portfolio. The synthetic example demonstrates
the workflow; the historical attribution above remains a separate working study.
