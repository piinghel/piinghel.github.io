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

<p class="article-summary">I want to understand my strategy beyond its return curve: what it owns, which bets are paying off, and what's going on when it loses money. Here I work through a real backtest, starting with the whole portfolio and following one difficult period down to individual stocks.</p>

Two profitable years can tell very different stories. In one, the longs might
do most of the work. In another, the shorts might keep the portfolio afloat.
I'd like to know which story I'm looking at, and whether it's changing.

The example is the long–short equity strategy from my
[optimizer article](/quants/2026/08/29/portfolio-optimization.html).
It ranks stocks with a prediction model and sizes positions within risk limits.
Here I want to understand what those positions added up to.

One **P&L point** means 1% of the same fixed strategy notional throughout.

<details>
<summary>Backtest assumptions</summary>
<div markdown="1">

The backtest uses real market data and history already used to help choose
the model. It charges five basis points on traded notional and excludes
borrow, financing and market impact.

</div>
</details>

## What is the strategy doing over time?

The long-term return curve looks encouraging, but the weaker stretches in
Figure 1 make me want to know which parts of the portfolio stopped working.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/strategy-history" mobile="/_draft_assets/portfolio-attribution/strategy-history_mobile" version="1" alt="Cumulative net P&L, additive drawdown and annual P&L from September 1998 to May 2026." %}
</div>
<p class="figure-caption"><strong>Figure 1: Growth punctuated by difficult periods.</strong> Additive P&amp;L, 23 September 1998–27 May 2026; first and last years are partial. Shading marks the early-2023 drawdown explored below.</p>

The two books take turns carrying the result (Table 1).
In 2022 the shorts offset losing longs. In 2023 and 2024,
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

With a strong 2025 between weaker stretches, I wouldn't describe this as a
steady decline. But the portfolio is clearly earning its money in different
ways. Did its positions change, or did similar bets start paying off differently?

## Have the exposures changed?

**Exposure** tells me how much of a bet the portfolio is taking, and in which
direction. Start with the dollars: average marked long exposure was 107% of
notional in 2021, against 89% short. In 2025 those figures were 105% and 79%:
net dollar exposure had risen from about 18% to 25%. These weights include
the effect of prices moving between trades.

The types of stocks matter too. I can have more dollars invested long while
holding lower-beta stocks long and higher-beta stocks short. Figure 2 looks
at these shared characteristics for the holdings covered by the attribution
model.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/style-exposures" mobile="/_draft_assets/portfolio-attribution/style-exposures_mobile" version="1" alt="Monthly mean modeled exposures from 2021 to May 2026: positive size and momentum, negative volatility, and a beta tilt that became negative after 2021 and later moderated." %}
</div>
<p class="figure-caption"><strong>Figure 2: Persistent tilts, with a changing beta exposure.</strong> Monthly average standardized exposures on covered holdings, without rescaling missing positions. Positive values indicate a tilt towards the characteristic; negative values indicate the reverse. Panels have different scales.</p>

The size tilt stays positive, momentum is predominantly positive, and
volatility exposure stays negative. These are persistent features of the portfolio.
The beta tilt changes more: its annual average moves from about +0.02 in
2021 to −0.41 in 2022, then moderates to −0.22 in 2025 and −0.15 in partial
2026. Here beta is a standardized characteristic in a joint factor model;
that number is not the portfolio's regression beta to a benchmark.

There's a gap here that I can't ignore. The model covers roughly 92–98%
of gross exposure on average across these years, but the holdings it misses
lost **8.76 P&L points in 2024**. That is a lot to leave out when explaining
the year. I keep those holdings separate from the fitted residual: the return
left unexplained for stocks the model did cover.

## Where did the loss come from?

In the drawdown from **29 December 2022–2 February 2023**, longs earned
**7.306 points**, shorts lost **16.356 points**, and costs subtracted another
**0.120 points** (Figure 3). I'm choosing this period with hindsight to
understand what went wrong.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/episode-bridge" mobile="/_draft_assets/portfolio-attribution/episode-bridge_mobile" version="1" alt="Real portfolio P&L bridge: longs add 7.306 percentage points, shorts subtract 16.356 and costs subtract 0.120, leaving a net loss of 9.170 points." %}
</div>

<p class="figure-caption"><strong>Figure 3: Shorts more than wiped out the long gains.</strong> 29 December 2022–2 February 2023. Both books use the same notional; trading costs are separate.</p>


The short loss was more than twice the long gain. The five worst stocks lost
4.037 points in total, only **24.7% of the short-book loss**. This is broader
than a few bad names. It also reverses the preceding 24 sessions, when the
shorts earned 4.778 points and the whole portfolio earned 1.412 points.

<details>
<summary>Adding contributions and measuring drawdowns</summary>
<div markdown="1">

For each date, $$r_{p,t}=c_{L,t}+c_{S,t}+c_{C,t}$$ is net P&L divided by fixed
notional. Accumulating these contributions gives

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
gains. In Financials, Rocket contributes −1.104 points. These names give me
somewhere to start: I can open the positions and see what happened.

Going one level deeper, Financial Services loses −1.324 points, while the
whole Financials sector loses −1.292. Other industries in the sector partly
offset it. I'm using later classifications to group these historical holdings,
so the labels may differ from those used at the time.

The factor model asks a different question: how much of those stock returns
is associated with shared characteristics? Figure 4 attributes **−3.271
points to beta**, **−3.064 to volatility** and **−1.923 to momentum**.
The model includes the displayed styles and sector terms, but omits other
potential common drivers, including value and quality. Some of those effects
could end up in the residual. I need to keep that in mind before treating
the unexplained part as evidence of stock-picking skill.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/episode-factors-risk" mobile="/_draft_assets/portfolio-attribution/episode-factors-risk_mobile" version="1" alt="Episode factor contributions to P&L and realized portfolio volatility. Beta and volatility are the largest modeled losses; residual is the largest contributor to realized volatility." %}
</div>
<p class="figure-caption"><strong>Figure 4: The biggest loss and the biggest risk contribution differ.</strong> 29 December 2022–2 February 2023. P&amp;L contributions total −9.170 points; contributions to annualized realized volatility total 11.116 points. Panels have different scales.</p>

It's useful to compare Health Care's **−3.074-point stock P&L** with
its **+0.157-point modeled sector effect**. Health Care stocks also have
beta, volatility and other exposures, and their own residual returns. Adding
the sector-group loss to the factor losses would count the same P&L twice.

The risk panel adds something the loss ranking misses. Residual P&L loses
1.872 points, but contributes **4.604 points of realized volatility**, more
than any single factor. Beta contributes 1.991 volatility points and
volatility 1.191. Here **risk contribution** measures how each daily component
moves with total daily P&L. This tells me what moved together during the loss.
To know whether the risk model saw it coming, I'd need its forecasts from
before the episode.

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
volatility. The factor $$\sqrt{252}$$ annualizes it using 252 trading days.

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
So the portfolio lost through beta even with a slightly smaller negative
exposure: the factor's return had turned against it.

Volatility combines both changes: the negative exposure grew, and its factor
return switched from −0.394 to +2.665 points. Momentum exposure also grew
while its factor return became negative. These are conditional returns from
the joint model, whose correlated factors share the explanation; they are
not returns on independently tradable factor portfolios.

Could I keep the stock views I want with less of these shared bets? That's
worth testing, but reducing an exposure could also give up gains in other
periods. I'd need to build the alternative portfolio and account for its
trading costs to find out.

<details>
<summary>The factor calculation and where it can mislead</summary>
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

Rocket, NCR and BJ's contributed most to the beta loss. But a stock can lose
through one factor and still make money overall, as Table 3 shows.

<div markdown="1">
<p class="table-caption"><strong>Table 3: A factor loss inside a winning stock.</strong> Contributions in P&amp;L points, 29 December 2022–2 February 2023. Stock totals are gross.</p>

| Stock | Beta component | Total stock P&L |
| :--- | ---: | ---: |
| Rocket | −0.225 | −1.104 |
| NCR | −0.220 | −0.584 |
| BJ's | −0.181 | +0.217 |
{: .research-table .comparison-table .risk-performance-table }

</div>

BJ's is a good example: it lost through beta but made money overall because
its other components more than offset that loss. Rocket lost through beta
too, but that accounts for only about a fifth of its total loss. To understand
the rest, I need to look at the other components and how the position changed.

## What happened to the Rocket position?

Rocket's adjusted price rose **62.35%** over the episode. The portfolio held it
short on all **24 sessions**, recording a gross loss of **1.104 percentage
points of strategy notional**.

The absolute weight grew from **1.643%** to **2.610%** over the period.
A larger dollar weight can result from an adverse price move as well
as from trading. Those endpoints alone do not show that the strategy actively
increased the short.

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
return multiplied by its final weight would not reconstruct the
−1.104-point loss.

*Elements*, §14.1, separates holdings-snapshot P&L from trading within the
interval. For a stock traded during the episode, daily holdings and trade
timing are needed to reconcile the result.

Reading: *The Elements of Quantitative Investing*, §14.1.

</div>
</details>

### What did the model say?

As Rocket rose, did the model change its mind while the portfolio kept the
short? A positive patch in the predictor heatmap might give that impression.
Let's check the full prediction.

The five predictors in Figure 5 went from a combined **−0.0266 to +0.0196**
between the start and end of the period.
The full prediction stayed negative, changing from **−0.0793 to −0.0869**.
The remaining terms and intercept offset the positive subtotal at the end.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/rocket-prediction" mobile="/_draft_assets/portfolio-attribution/rocket-prediction_mobile" version="1" alt="Rocket's five displayed predictors change from a negative to a positive subtotal, but remaining terms plus intercept keep the full prediction negative at both observed endpoints." %}
</div>

<p class="figure-caption"><strong>Figure 5: Some predictors improved, but the overall score stayed negative.</strong> Rocket, 29 December 2022 (circles) and 2 February 2023 (diamonds). Values are model scores.</p>


The full prediction was negative throughout the 24 sessions, so the positive
patch doesn't mean the model had turned positive on Rocket. The score is an
input to ranking and sizing, not a calibrated
expected return or a complete explanation of the trade. Candidate ranks,
existing holdings and trading constraints also affect the position.

Now I want to understand **what kept the score negative as the stock rose,
and how that score translated into the position**. For that, I'll need the
complete model output and the rules that turn it into holdings.

<details>
<summary>How the predictors add up to the full score</summary>
<div markdown="1">

For a linear prediction,

$$
s_{i,t}=a_t+\sum_j\theta_{j,t}x_{i,j,t}.
$$

Each predictor contributes its coefficient times its transformed input,
$$\theta_{j,t}x_{i,j,t}$$. A change can come from the input or from a coefficient
refit. These are model-score units, distinct from realized factor P&L.

The remaining terms plus intercept equal the full score minus the subtotal
of the five predictors. Together they account for the full prediction.

</div>
</details>

## What would I look at next?

The early-2023 loss gives me a concrete place to start. The portfolio kept
several style tilts whose payoffs turned against it together. I'd like to
try changing one exposure limit while keeping the forecasts and risk model
fixed, then compare the holdings, turnover and net P&L across both good and
bad periods. A limit that helps in this drawdown still has to earn its place
over the rest of the history.

There is also a stock-selection and sizing question. The fitted residual
contributed +7.411 points in 2025 but −4.595 through May 2026, even though
momentum contributed +6.052 in that partial year. I'd miss that change by
looking only at the total. Are the residual losses spread across many stocks,
or did the portfolio put more weight on the ones that did badly? Before
blaming stock selection or sizing, I also need to check that changes in model
coverage or specification aren't driving the comparison.

This is where I find Paleologo's distinction between selection and sizing
helpful. I can compare
**actual and equal-risk idiosyncratic contributions**, using the same dates,
positions and a common risk budget. If the larger positions systematically
receive worse signed outcomes, sizing deserves attention; if the equal-risk
comparison also performs poorly, selection remains a concern. *Advanced
Portfolio Management*, §8.2.1, develops comparisons with equal-sized positions;
*Elements*, §14.4, separates signed outcomes from risk allocations.

<details>
<summary>The calculation behind selection and sizing</summary>
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

Before changing the strategy, I'd first account for the losses on holdings
the factor model missed, then work through the selection and sizing comparison.
That should help me decide where to spend time: the exposure limits, the
position sizes, or the predictions themselves. Any change would still need
a realistic backtest with trading costs, covering more than the drawdown
that gave me the idea.

## References

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
Chapter 8; [*The Elements of Quantitative Investing*](https://linktr.ee/paleologo),
Chapter 14.

The [dashboard source code](https://github.com/piinghel/portfolio-pnl-dashboard)
is available if you'd like to explore your own portfolio.
