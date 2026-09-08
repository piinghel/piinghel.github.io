---
layout: post
title: "Understanding portfolio performance attribution"
description: "Understanding a strategy through its changing exposures, sources of return, drawdowns and individual positions."
article_label: Portfolio attribution
permalink: /quants/portfolio-attribution.html
toc: true
show_date: false
published: false
navigation: false
---

<p class="article-summary">I want to understand what my strategy is actually doing: which exposures it takes, how they change over time, and what produces its gains and drawdowns. Performance attribution lets me connect the portfolio's overall behaviour to sectors, industries, factors and individual positions.</p>

The investigation starts with the whole strategy. I then select periods when
its behaviour changes and work down to the holdings behind that change.
The loss from **29 December 2022–2 February 2023** provides a worked example;
Rocket provides a closer look at one position within it.

This is a personal study alongside Giuseppe Paleologo's *Advanced Portfolio
Management* (2021), Chapter 8, and *The Elements of Quantitative Investing*,
Chapter 14. The figures use saved backtest observations based on real market
data. The portfolio is the constrained Ridge strategy with trading controls
from the [optimizer article](/quants/2026/08/29/portfolio-optimization.html),
allocated equally across [three starting weeks](/quants/2025/05/10/rebalancing-luck.html).
This history has already been used in model selection.

## What is the strategy doing over time?

Before explaining a good or bad month, I want to see how the portfolio itself
has evolved. Has the balance between long and short exposure changed? Have
particular sectors become larger? Are the same factors driving risk throughout
the history, or does that concentration move?

The useful comparison places the return and drawdown path alongside exposure and risk
contributions on the same date axis. **Exposure** tells me the size and
direction of a bet. **Risk contribution** tells me how it interacts with
the rest of the portfolio. **P&L contribution** tells me what it earned or
lost. Seeing all three helps distinguish taking a larger bet from experiencing
a different outcome on a similar bet.

The comparison through time matters. If a factor's P&L deteriorates, did its
return turn against the strategy, did the strategy increase its exposure, or
did both happen? If an industry becomes a larger holding, did that result from
new trades or from the prices of existing positions moving? These questions
give the portfolio overview a purpose before I zoom into any one episode.

The episode below shows how to investigate a period within that broader
history: locate the loss, identify the shared exposures, then inspect the
positions behind them.

## Where did this period's P&L come from?

In the dashboard, I select the episode and open the P&L breakdown. The first
question is whether the loss sits in the long book, the short book, or recorded
costs. Figure 1 answers it: longs earned **7.306 points**, shorts lost
**16.356 points**, and costs subtracted another **0.120 points**.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/episode-bridge" mobile="/_draft_assets/portfolio-attribution/episode-bridge_mobile" version="1" alt="Real portfolio P&L bridge: longs add 7.306 percentage points, shorts subtract 16.356 and costs subtract 0.120, leaving a net loss of 9.170 points." %}
</div>

<p class="figure-caption"><strong>Figure 1: Following the loss through the two books.</strong> Saved three-schedule portfolio, 29 December 2022–2 February 2023. Longs, shorts and costs build the additive net P&amp;L, all on the same fixed notional.</p>


The short loss was more than twice the long gain. That gives me a reason to
inspect the short side more closely. Next I want to know whether the loss was
spread across unrelated holdings or concentrated in common industries and
factor exposures.

The bars add to the net loss because both books use the **same fixed
notional**, with recorded trading costs kept separate. That lets me move from
the portfolio total to individual stocks without changing the scale.

<details>
<summary>Why the dashboard adds daily P&L</summary>
<div markdown="1">

The backtest charges five basis points on traded notional; borrow, financing
and market impact are absent. Net means after that recorded charge.

For each date, $r_{p,t}=c_{L,t}+c_{S,t}+c_{C,t}$$ is net P&L divided by fixed
notional. The dashboard accumulates it as

$$
A_t=\sum_{s\le t}r_{p,s},\qquad
D_t=A_t-\max(0,A_1,\ldots,A_t).
$$

The drawdown measures the distance below the earlier peak of that additive
path. This is why all comparisons here keep the same dates and notional.

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

The changing multiplier $$V_{t-1}$$ is the reason a component's linked
contribution differs from its additive P&L. The dashboard uses the additive
convention. The linked convention below describes a separately constructed
compounded index; it requires the actual daily series, not just the period totals.

</div>
</details>

## Which groups and stocks explain it?

I keep the dates fixed and look at the loss in two ways. **Sector and industry
groupings** collect the complete P&L of stocks belonging to each group.
**Factor attribution** divides stock returns into modeled common effects
and residuals. These are alternative explanations of the same portfolio P&L.

For an industry with a large loss, I want to see the stocks inside it:
was one name responsible, or did most holdings move together? For a losing
factor, I want to see which stocks contributed to that particular factor term.
Ranking stocks by their total P&L would not answer the second question.

For example, a stock's contribution to a particular factor comes from its
signed position weight multiplied by its loading on that factor and the
factor's return. A stock can lose through that exposure while earning money
overall through other effects. Following the factor term down to its stocks
keeps that distinction visible.

The practical comparison is then with the period before the drawdown:
were these exposures already present, and did the same stocks carry them?
This helps separate a change in portfolio construction from a change in the
returns experienced by existing exposures.

The factor bridge must retain residual, uncovered and unreconciled P&L so
that every part of the loss remains accounted for.

<details>
<summary>Derive the factor contribution, then check its limits</summary>
<div markdown="1">

In a linear factor attribution, I write the stock return as

$
r_{i,t}=\sum_k b_{i,k,t^-}f_{k,t}+\varepsilon_{i,t}.
$

The loadings $b$ describe the stock's exposures before the return;
$f$ contains the period's factor returns. Multiplying by signed starting
weights and adding across holdings produces each factor's portfolio P&L.
The residual collects the part of modeled stock returns left unexplained by
that specification. A common intercept, when present, can be represented as
a factor with loading 1; it needs its own interpretation rather than being
automatically labelled market beta.


Reading: *Advanced Portfolio Management*, §8.1.1.

There are two different checks here. The components must add to the ledger.
Then I need to judge how well the model allocates P&L between factors and
residuals. *Elements*, §14.2.2, makes that second problem explicit. In its
fixed-loading setup, write estimated factor returns as
$\widehat f_t=f_t+\eta_t$. Holding the observed stock return fixed gives

$
\widehat\varepsilon_t=\varepsilon_t-B\eta_t.
$

At portfolio level the estimated factor component gains $w_t^\top B\eta_t$
and the estimated residual component loses the same amount. **The two errors
cancel in total P&L.** A perfectly reconciled chart can therefore contain an
uncertain factor/residual split. This is a model identity, not an estimate of
the error in my portfolio. See *The Elements of Quantitative Investing*,
§14.2.2.

</div>
</details>

## What happened inside one position?

I switch to **Stocks → Short**, keep the same dates, and open Rocket.
The aim is to connect the stock's movement to the loss actually borne by the
portfolio.

Rocket's adjusted price rose **62.35%** over the episode. The portfolio held it
short on all **24 sessions**, recording a gross loss of **1.104 percentage
points of strategy notional**. This is one contributor to the −16.356-point
short-book loss, not an explanation of the entire book.

The absolute weight was **1.643%** on the first saved date and **2.610%** on
the last. A larger dollar weight can result from an adverse price move as well
as from trading. Those endpoints alone do not show that the strategy actively
increased the short.

I read the shared date axis from top to bottom:
**price → cumulative P&L → position size → predictor contributions → model inputs**.
The first three panels establish when the loss accumulated and what exposure
was present. The last two help me understand the saved model output.

I keep the episode fixed while moving between the stock and portfolio views.

<details>
<summary>How a short stock contributes to portfolio P&L</summary>
<div markdown="1">

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


The negative position turns a positive price move into negative P&L. Across
multiple sessions, I sum the actual daily contributions. Rocket's period
return multiplied by its final weight would not reconstruct the saved
−1.104-point loss.

*Elements*, §14.1, separates holdings-snapshot P&L from trading within the
interval. For a stock traded during the episode, daily holdings and trade
timing are needed to reconcile the result.

Reading: *The Elements of Quantitative Investing*, §14.1.

</div>
</details>

### What did the model say?

A loss while holding a short raises a practical question: had the model changed
its view while the position remained? A positive patch in a predictor heatmap
could suggest that, but I need to check the full prediction.

Figure 2 compares the same five displayed predictor contributions at the first
and last saved dates. Their subtotal changed from **−0.0266 to +0.0196**.
The full prediction stayed negative, changing from **−0.0793 to −0.0869**.
The remaining terms and intercept offset the positive subtotal at the end.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/rocket-prediction" mobile="/_draft_assets/portfolio-attribution/rocket-prediction_mobile" version="1" alt="Rocket's five displayed predictors change from a negative to a positive subtotal, but remaining terms plus intercept keep the full prediction negative at both observed endpoints." %}
</div>

<p class="figure-caption"><strong>Figure 2: A partial explanation can point the other way.</strong> Rocket, 29 December 2022 (circles) and 2 February 2023 (diamonds). Lines compare endpoints. The first two rows add to the full prediction on each date. Values are model scores, not portfolio returns.</p>


The full prediction was negative throughout the 24 sessions. The positive
subtotal therefore gives me no reason to conclude that the model had changed
its overall view.

The useful follow-up is **what kept the score negative as the stock rose,
and how did that score translate into the position?** That takes me from
the predictor chart to the complete model output and the position rules.

<details>
<summary>Reconcile the predictor panel to the full score</summary>
<div markdown="1">

For a saved linear prediction,

$$
s_{i,t}=a_t+\sum_j\theta_{j,t}x_{i,j,t}.
$$

Each predictor contributes its saved coefficient times its transformed input,
$$\theta_{j,t}x_{i,j,t}$$. A change can come from the input or from a coefficient
refit. These are model-score units, distinct from realized factor P&L.

In Figure 2, the remaining terms plus intercept are calculated as the saved
full score minus the subtotal of the same five predictors. The first two rows
therefore add to the last on each date. Missing predictions on trading
sessions should stay blank rather than being interpreted as zero scores.

</div>
</details>

## Did the strategy take the risks I expected?

One position helps explain a specific outcome; the strategy-level question is
whether such positions add up to the intended portfolio. I want to compare
which stocks and factors contributed most to risk before the drawdown with
which contributed most to the subsequent loss.

That comparison also belongs in stronger periods. Are gains repeatedly coming
from the same intended exposures, or from occasional bets elsewhere? Are
residual gains broad across stocks, or dependent on a handful of names?
Looking at both gains and losses keeps one memorable episode from defining
the entire strategy.



Placing P&L and risk contributions side by side answers another question:
did the biggest losing stocks also contribute most to portfolio variation
during the episode?

<details>
<summary>Why standalone volatility does not answer the risk question</summary>
<div markdown="1">

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


This realized calculation uses holdings that changed during the window.
Forecast risk instead applies the covariance model available at a decision
time to that snapshot of holdings: $$\sqrt{w^\top\Sigma w}$$. A comparison
needs consistent horizons and explicit model coverage. Missing forecasts
remain missing; they are not zero risk.

</div>
</details>

## From understanding to a research decision

The purpose of these views is to identify which part of the strategy needs
closer examination. Persistent factor concentration raises a construction
question. Poor residual outcomes raise questions about forecasts and stock
selection. Larger allocations to worse outcomes raise a sizing question.
The evidence needed for each is different.

Paleologo's selection/sizing distinction gives the next investigation a
purpose: did the strategy choose losing stocks, or allocate more risk to
its worse choices? *Advanced Portfolio Management*, §8.2.1, approaches this
by comparing actual positions with equal-sized positions, examining their
idiosyncratic P&L.

For my portfolio, I want to establish whether larger risk allocations
coincided with worse stock-specific outcomes. The relevant comparison puts
**actual and equal-risk idiosyncratic contributions side by side**, on the
same dates and with the same included positions. That would test an allocation
question that the observed stock P&L alone cannot answer.

<details>
<summary>Work through the selection and sizing identity</summary>
<div markdown="1">

*Elements*, §14.4, gives me a complementary way to work through the question.
For one date, let $$\varepsilon_i$$ be a stock's idiosyncratic return,
$$\sigma_i>0$$ its matching idiosyncratic volatility, and $$w_i$$ its signed
position weight. Define

$$
u_i=\frac{\varepsilon_i}{\sigma_i}\operatorname{sign}(w_i),
\qquad a_i=\sigma_i|w_i|.
$$

The first quantity measures the signed outcome in volatility units; the second
measures the size of the risk taken. Their product is exactly
$$u_i a_i=w_i\varepsilon_i$$. Averaging across the $$n$$ included positions,
with cross-sectional covariance defined using divisor $$n$$, gives

$$
\sum_i w_i\varepsilon_i
=\overline u\sum_i a_i
+n\operatorname{Cov}_{i}(u_i,a_i).
$$

This identity makes the question concrete. The first term uses the average
signed outcome. The second is positive when larger risk positions coincide
with better signed outcomes on that date. A hit rate discards the magnitude
of those standardized outcomes, so it answers a different question.

If idiosyncratic returns are uncorrelated under the model, the corresponding
portfolio volatility is $$\sqrt{\sum_i a_i^2}$$. Dividing the identity by it
gives a selection term multiplied by diversification,
$$\sum_i a_i/\sqrt{\sum_i a_i^2}$$, plus a sizing term. This is a
single-period risk-normalized result; a reported time-series information
ratio requires its own aggregation convention. See *The Elements of
Quantitative Investing*, §14.4.

</div>
</details>

For the episode examined here, the evidence locates the loss on the short
side and shows one short held through a large price rise while its full
prediction remained negative. The open question is whether this reflects
common exposures across the book, stock-specific forecast errors, or the way
those views were sized. Resolving that question determines which strategy
decision deserves testing.

## References

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
Chapter 8; [*The Elements of Quantitative Investing*](https://linktr.ee/paleologo),
Chapter 14.

The dashboard's [source code and bundle format](https://github.com/piinghel/portfolio-pnl-dashboard)
are available for exploring another portfolio.
