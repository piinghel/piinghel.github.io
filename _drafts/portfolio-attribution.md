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

<p class="article-summary">A strategy can make money for years and still be difficult to understand. I use performance attribution to connect its changing positions to what it earns and loses. In this portfolio, persistent style exposures help explain an early-2023 drawdown, while the remaining losses raise questions about stock selection and sizing.</p>

When I look at a strategy, I want to know what I am relying on. Does it earn
money from selecting stocks, from carrying common exposures, or from changing
those exposures at useful times? Has that mix changed? And when it loses,
is the loss consistent with the risks it was taking?

I work through those questions using the constrained Ridge strategy with trading controls
from the [optimizer article](/quants/2026/08/29/portfolio-optimization.html),
allocated equally across [three starting weeks](/quants/2025/05/10/rebalancing-luck.html).
It ranks stocks using a linear prediction model, then sizes long and short
positions jointly under risk and exposure limits. A rank buffer and a trade
penalty discourage unnecessary replacements. Each schedule rebalances every
three weeks, so the combined portfolio spreads those decisions through time.

The figures are saved backtest results using real market data. This history
has already informed model selection. Trading costs are five basis points on
traded notional; borrow, financing and market impact are absent. Throughout,
one **P&L point** means 1% of the same fixed strategy notional.
Paleologo's *Advanced Portfolio Management*, Chapter 8, and *The Elements of
Quantitative Investing*, Chapter 14, guide the questions and the interpretation.

## What is the strategy doing over time?

Figure 1 starts with the whole available history. The cumulative path shows
what the strategy has earned; the drawdown below it shows how far it fell
from an earlier peak. Calendar-period P&L makes weaker stretches easier to see
than the slope of a long cumulative line alone.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/strategy-history" mobile="/_draft_assets/portfolio-attribution/strategy-history_mobile" version="1" alt="Aligned cumulative net P&L, additive drawdown and calendar-period P&L for the saved strategy from September 1998 to May 2026." %}
</div>
<p class="figure-caption"><strong>Figure 1: Put the difficult period in the strategy's history.</strong> 23 September 1998–27 May 2026. All panels use additive P&amp;L on fixed notional. The first and last calendar years are partial. The shaded band marks 29 December 2022–2 February 2023, examined below.</p>

The more recent years show why a single performance number is insufficient.
In 2022 the shorts earned enough to offset losing longs. In 2023 and 2024,
longs carried the result while shorts lost money. Both sides contributed in
2025; the short side is again the source of the loss through May 2026.

<div markdown="1">
<p class="table-caption"><strong>Table 1: Which book is carrying the result?</strong> P&amp;L points on fixed notional. Longs and shorts are gross; costs are recorded for the whole portfolio. ¹Through 27 May 2026.</p>

| Period | Longs | Shorts | Costs | Net |
| :--- | ---: | ---: | ---: | ---: |
| 2021 | +31.87 | −0.21 | −1.21 | +30.45 |
| 2022 | −11.90 | +20.31 | −1.18 | +7.23 |
| 2023 | +21.50 | −16.10 | −1.32 | +4.07 |
| 2024 | +22.23 | −11.75 | −1.30 | +9.17 |
| 2025 | +10.73 | +8.59 | −1.16 | +18.16 |
| 2026¹ | +6.75 | −9.47 | −0.45 | −3.17 |
{: .research-table .comparison-table .risk-performance-table }

</div>

This is uneven performance, with a strong 2025 between weaker stretches.
It does not establish a steady decline in the strategy's ability to earn.
The more useful question is whether the portfolio changed, or whether
similar positions encountered different returns.

## Have the exposures changed?

**Exposure** measures the size and direction of a position or a shared
characteristic. The portfolio's average marked long exposure was 107% of
notional in 2021, against 89% short. In 2025 those figures were 105% and 79%:
net dollar exposure had risen from about 18% to 25%. Those are observed
positions, including price drift between trades.

Dollars alone hide another layer. A portfolio can have more long dollars
while holding lower-beta stocks long and higher-beta stocks short.
Figure 2 looks at the common characteristics of the holdings that the
attribution model covers. Positive exposure means a net tilt towards higher
values of that standardized characteristic; negative exposure means the reverse.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/style-exposures" mobile="/_draft_assets/portfolio-attribution/style-exposures_mobile" version="1" alt="Monthly mean modeled exposures from 2021 to May 2026: positive size and momentum, negative volatility, and a beta tilt that became negative after 2021 and later moderated." %}
</div>
<p class="figure-caption"><strong>Figure 2: Persistent tilts, with a changing beta exposure.</strong> Monthly means of signed weight × standardized descriptor for holdings with fitted factor P&amp;L. The two panels have different vertical ranges. Missing holdings are omitted without scaling up the covered positions. The shaded band is the selected loss episode.</p>

The size tilt stays positive, momentum is predominantly positive, and
volatility exposure stays negative. These are persistent features of the portfolio.
The beta tilt changes more: its annual average moves from about +0.02 in
2021 to −0.41 in 2022, then moderates to −0.22 in 2025 and −0.15 in partial
2026. Here beta is a standardized characteristic in a joint factor model;
that number is not the portfolio's regression beta to a benchmark.

Coverage matters when reading the changes. The model covers roughly 92–98%
of gross exposure on average across these years. It leaves **−8.76 P&L
points uncovered in 2024**, large enough to affect any conclusion about that
year's sources of return. I keep those holdings separate from the fitted
residual, which is the return left unexplained for stocks the model did cover.

With that distinction in place, I can ask a more precise question about a loss:
did one of these established exposures become larger, or did its payoff reverse?

## Where did this period's P&L come from?

I select **29 December 2022–2 February 2023**, a loss spanning 24 trading
sessions. These dates capture the decline following the 28 December peak;
they are chosen retrospectively to understand the episode. The first
question is whether the loss sits in the long book, the short book, or recorded
costs. Figure 3 answers it: longs earned **7.306 points**, shorts lost
**16.356 points**, and costs subtracted another **0.120 points**.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/episode-bridge" mobile="/_draft_assets/portfolio-attribution/episode-bridge_mobile" version="1" alt="Real portfolio P&L bridge: longs add 7.306 percentage points, shorts subtract 16.356 and costs subtract 0.120, leaving a net loss of 9.170 points." %}
</div>

<p class="figure-caption"><strong>Figure 3: Following the loss through the two books.</strong> Saved three-schedule portfolio, 29 December 2022–2 February 2023. Longs, shorts and costs build the additive net P&amp;L, all on the same fixed notional.</p>


The short loss was more than twice the long gain. The five worst stocks lost
4.037 points in total, only **24.7% of the short-book loss**. This is broader
than a few bad names. It also reverses the preceding 24 sessions, when the
shorts earned 4.778 points and the whole portfolio earned 1.412 points.

The bars add to the net loss because both books use the **same fixed
notional**, with recorded trading costs kept separate. That lets me move from
the portfolio total to individual stocks without changing the scale.

<details>
<summary>Why the dashboard adds daily P&L</summary>
<div markdown="1">

For each date, $$r_{p,t}=c_{L,t}+c_{S,t}+c_{C,t}$$ is net P&L divided by fixed
notional. The dashboard accumulates it as

$$
A_t=\sum_{s\le t}r_{p,s},\qquad
D_t=A_t-\max(0,A_1,\ldots,A_t).
$$

The drawdown measures the distance below the earlier peak of that additive
path. This is why all comparisons here keep the same dates and notional.

The −9.170-point episode loss is measured on this additive path. A compounded
return index would require linking every component with the same prior index
value; I keep one convention throughout this article.

</div>
</details>

## Which groups and stocks explain it?

I keep the dates fixed and look at the loss in two ways. **Sector and industry
groupings** collect the complete P&L of stocks belonging to each group.
**Factor attribution** divides stock returns into modeled common effects
and residuals. These are alternative explanations of the same portfolio P&L.

Health Care has the largest sector loss, **−3.074 points**, followed by
Consumer Discretionary (−1.516), Materials (−1.330) and Financials (−1.292).
Within Health Care, Sotera and Dentsply account for −1.070 and −0.764 points.
Together they explain about 60% of that sector's gross loss after offsetting
gains. In Financials, Rocket contributes −1.104 points. The classification
breakdown gives me specific holdings to examine rather than a sector label
as an explanation.

The industry view refines that location: Financial Services loses −1.324
points, while the whole Financials sector loses −1.292. Other industries in
the sector partly offset it. These classifications are retrospective, so
they describe the historical holdings using a later classification snapshot.

The factor model asks a different question: how much of those stock returns
is associated with shared characteristics? Figure 4 attributes **−3.271
points to beta**, **−3.064 to volatility** and **−1.923 to momentum**.
The fitted intercept contributes +3.035 points, partly offsetting the losses.
It is the model's common baseline multiplied by net covered dollars.
The model includes the displayed styles and sector terms, but omits other
potential common drivers, including value and quality. Its residual is
therefore a starting point for examining stock selection, rather than a
direct measure of selection skill.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/episode-factors-risk" mobile="/_draft_assets/portfolio-attribution/episode-factors-risk_mobile" version="1" alt="Episode factor contributions to P&L and realized portfolio volatility. Beta and volatility are the largest modeled losses; residual is the largest contributor to realized volatility." %}
</div>
<p class="figure-caption"><strong>Figure 4: The largest loss and the largest risk contribution need not coincide.</strong> Same 24 sessions as Figure 3. P&amp;L components sum to −9.170 points; signed contributions to annualized realized volatility sum to 11.116 points. The panels use different scales. Sector effects collect the model's sector terms; residual, uncovered holdings, reconciliation and costs remain separate.</p>

Notice the difference between Health Care's **−3.074-point stock P&L** and
its **+0.157-point modeled sector effect** within the −0.429-point total
for sector effects. There is no contradiction. Health Care stocks also have
beta, volatility and other exposures, and their own residual returns. Adding
the sector-group loss to the factor losses would count the same P&L twice.

The risk panel adds something the loss ranking misses. Residual P&L loses
1.872 points, but contributes **4.604 points of realized volatility**, more
than any single factor. Beta contributes 1.991 volatility points and
volatility 1.191. Here **risk contribution** measures how each daily component
moves with total daily P&L. It describes variation during the episode; it
does not establish what the model forecast before the loss.

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

## A larger exposure, or a different payoff?

For a factor, daily contribution is the portfolio's signed exposure multiplied
by that day's factor return. Comparing the episode with the preceding 24
sessions separates two possibilities: the strategy took a different bet,
or an existing bet started losing.

<div markdown="1">
<p class="table-caption"><strong>Table 2: What changed across the turn of the year?</strong> Prior period: 23 November–28 December 2022. Loss period: 29 December 2022–2 February 2023. Exposure is the average signed standardized exposure on matched model-covered holdings; P&amp;L is in points.</p>

| Factor | Exposure before | During loss | P&L before | During loss |
| :--- | ---: | ---: | ---: | ---: |
| Beta | −0.437 | −0.419 | +0.876 | −3.271 |
| Volatility | −0.834 | −1.075 | +0.349 | −3.064 |
| Momentum | +0.433 | +0.594 | +0.026 | −1.923 |
{: .research-table .comparison-table .risk-performance-table }

</div>

The beta exposure was slightly less negative during the loss. Its fitted
factor return changed sign, from a summed −1.943 points to +7.472 points.
The loss therefore did not require a larger negative beta bet. The payoff
to the characteristic reversed while the exposure remained negative.
The table summarizes average exposures; each P&L total still sums the actual
daily exposure times the matching daily factor return.

Volatility combines both changes: the negative exposure grew, and its factor
return switched from −0.394 to +2.665 points. Momentum exposure also grew
while its factor return became negative. These are conditional returns from
the joint model, whose correlated factors share the explanation; they are
not returns on independently tradable factor portfolios.

That narrows the construction question. Is this a tolerable cost of carrying
the strategy's persistent tilts, or could the portfolio express its stock
views with less of that shared exposure? The attribution locates the trade-off.
It does not tell me what a constrained, costed alternative would have earned.

<details>
<summary>Derive the factor contribution, then check its limits</summary>
<div markdown="1">

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


Reading: *Advanced Portfolio Management*, §8.1.1.

There are two different checks here. The components must add to the ledger.
Then I need to judge how well the model allocates P&L between factors and
residuals. *Elements*, §14.2.2, makes that second problem explicit. In its
fixed-loading setup, write estimated factor returns as
$$\widehat f_t=f_t+\eta_t$$. Holding the observed stock return fixed gives

$$
\widehat\varepsilon_t=\varepsilon_t-B\eta_t.
$$

At portfolio level the estimated factor component gains $$w_t^\top B\eta_t$$
and the estimated residual component loses the same amount. **The two errors
cancel in total P&L.** A perfectly reconciled chart can therefore contain an
uncertain factor/residual split. This is a model identity, not an estimate of
the error in my portfolio. See *The Elements of Quantitative Investing*,
§14.2.2.

</div>
</details>

## Which stocks carried the losing factor?

I follow the beta contribution down to its holdings, keeping the same dates.
Rocket, NCR and BJ's are its three largest losing contributors. Table 3 shows
why this ranking differs from a list of the worst stock trades.

<div markdown="1">
<p class="table-caption"><strong>Table 3: A factor loss inside a winning stock.</strong> Contributions in P&amp;L points, 29 December 2022–2 February 2023. Stock totals are gross.</p>

| Stock | Beta component | Total stock P&L |
| :--- | ---: | ---: |
| Rocket | −0.225 | −1.104 |
| NCR | −0.220 | −0.584 |
| BJ's | −0.181 | +0.217 |
{: .research-table .comparison-table .risk-performance-table }

</div>

BJ's lost through the beta term while its other components more than offset
that loss. Rocket lost through beta too, but that term accounts for only
about a fifth of its total loss. A factor breakdown helps locate a shared
exposure; understanding the whole position needs the other components and
the holding path.

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

Figure 5 compares the same five displayed predictor contributions at the first
and last saved dates. Their subtotal changed from **−0.0266 to +0.0196**.
The full prediction stayed negative, changing from **−0.0793 to −0.0869**.
The remaining terms and intercept offset the positive subtotal at the end.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/rocket-prediction" mobile="/_draft_assets/portfolio-attribution/rocket-prediction_mobile" version="1" alt="Rocket's five displayed predictors change from a negative to a positive subtotal, but remaining terms plus intercept keep the full prediction negative at both observed endpoints." %}
</div>

<p class="figure-caption"><strong>Figure 5: A partial explanation can point the other way.</strong> Rocket, 29 December 2022 (circles) and 2 February 2023 (diamonds). Lines compare endpoints. The first two rows add to the full prediction on each date. Values are model scores, not portfolio returns.</p>


The full prediction was negative throughout the 24 sessions. The positive
subtotal therefore gives me no reason to conclude that the model had changed
its overall view. The score is an input to ranking and sizing, not a calibrated
expected return or a complete explanation of the trade. Candidate ranks,
existing holdings and trading constraints also affect the position.

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

In Figure 5, the remaining terms plus intercept are calculated as the saved
full score minus the subtotal of the same five predictors. The first two rows
therefore add to the last on each date. Missing predictions on trading
sessions should stay blank rather than being interpreted as zero scores.

</div>
</details>

## From understanding to a research decision

The history and the episode point to two different decisions. The portfolio
carries persistent style tilts, and several of their payoffs turned against
it together in early 2023. That motivates a construction test: hold the
forecasts and risk model fixed, change one exposure limit, and compare the
resulting holdings, turnover and net P&L across favorable and adverse periods.
A limit that softens this loss may also remove gains elsewhere.

There is also a stock-selection and sizing question. The fitted residual
contributed +7.411 points in 2025 but −4.595 through May 2026, even though
momentum contributed +6.052 in that partial year. Total performance can hide
that change in composition. Before calling it weaker stock selection, I need
to see whether the residual losses are broad and whether larger positions
received worse outcomes. Coverage and the factor specification need to stay
comparable in that comparison.

Paleologo's selection/sizing distinction makes that test concrete. Compare
**actual and equal-risk idiosyncratic contributions**, using the same dates,
positions and a common risk budget. If the larger positions systematically
receive worse signed outcomes, sizing deserves attention; if the equal-risk
comparison also performs poorly, selection remains a concern. *Advanced
Portfolio Management*, §8.2.1, develops comparisons with equal-sized positions;
*Elements*, §14.4, separates signed outcomes from risk allocations.

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

I would start by resolving the material uncovered P&L, then make the matched
selection-versus-sizing comparison. Those checks determine whether an exposure
limit, a sizing rule or the forecasts themselves deserve attention. The
article's evidence explains where to look; any proposed change still has to
survive a feasible replay with trading costs and a broader evaluation than
the drawdown that suggested it.

## References

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
Chapter 8; [*The Elements of Quantitative Investing*](https://linktr.ee/paleologo),
Chapter 14.

The dashboard's [source code and bundle format](https://github.com/piinghel/portfolio-pnl-dashboard)
are available for exploring another portfolio.
