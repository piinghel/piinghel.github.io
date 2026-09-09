---
layout: post
title: "Understanding Your P&L"
description: "Understanding a strategy through its changing exposures, sources of return, drawdowns and individual positions."
article_label: Portfolio attribution
permalink: /quants/portfolio-attribution.html
toc: true
show_date: false
date: 2026-09-09
categories: ["Portfolio management"]
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

The strategy has made money over the full history, with several difficult
stretches along the way (Figure 1). The recent years show why the return curve
alone isn't enough: a positive year can hide a losing part of the portfolio.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/strategy-history" mobile="/assets/portfolio-attribution/strategy-history_mobile" version="1" alt="Cumulative net P&L, additive drawdown and annual P&L from September 1998 to May 2026." %}
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

The recent weakness is concentrated on the short side, with a recovery in
2025. What changed in the portfolio as these results unfolded?

## Have the exposures changed?

**Exposure** tells me how much of a bet the portfolio is taking, and in which
direction. Start with the dollars: average marked long exposure was 107.2% of
notional in 2021, against 89.1% short. In 2025 those figures were 104.6% and 79.1%:
net dollar exposure had risen from about 18.1% to 25.5%. These weights include
the effect of prices moving between trades.

The types of stocks matter too. I can have more dollars invested long while
holding lower-beta stocks long and higher-beta stocks short. Figure 2 looks
at these shared characteristics for the holdings covered by the attribution
model.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/style-exposures" mobile="/assets/portfolio-attribution/style-exposures_mobile" version="1" alt="Monthly mean modeled exposures from 2021 to May 2026: positive size and momentum, negative volatility, and a beta tilt that became negative after 2021 and later moderated." %}
</div>
<p class="figure-caption"><strong>Figure 2: Persistent tilts, with a changing beta exposure.</strong> Monthly average standardized exposures on covered holdings, without rescaling missing positions. Positive values indicate a tilt towards the characteristic; negative values indicate the reverse. Panels have different scales.</p>

The size tilt stays positive, momentum is predominantly positive, and
volatility exposure stays negative. These are persistent features of the portfolio.
The beta tilt changes more: its annual average moves from about +0.02 in
2021 to −0.41 in 2022, then moderates to −0.22 in 2025 and −0.15 in partial
2026. Here beta is a standardized characteristic in a joint factor model;
that number is not the portfolio's regression beta to a benchmark.

The short book has become smaller in dollars, while several style tilts have
persisted. To see how the portfolio responded to market movements, I also
need to look at its returns against a benchmark.

I used the Russell 1000 price-return benchmark.
Over September 1998–May 2026, beginning net dollar exposure averages **+22.0%**
of notional, but the slope from regressing daily net P&L on the benchmark,
including a constant, is only **+0.068**. The intercept component alone has a slope of +0.249; the remaining
components contribute −0.181, leaving +0.068 overall. These slopes use the same
6,962 dates and fixed-notional denominator, so they add up. The other components
offset much of the intercept's market sensitivity. Reading its bar alone would
give the wrong impression of the whole portfolio.

This is low historical sensitivity, rather than exact neutrality. The five-year
blocks from 2000 through 2024 have slopes between +0.039 and +0.078. These are
realized relationships for a changing portfolio; they do not establish that
each day's positions were beta-neutral before trading.

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
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/episode-bridge" mobile="/assets/portfolio-attribution/episode-bridge_mobile" version="1" alt="Real portfolio P&L bridge: longs add 7.306 percentage points, shorts subtract 16.356 and costs subtract 0.120, leaving a net loss of 9.170 points." %}
</div>

<p class="figure-caption"><strong>Figure 3: Shorts more than wiped out the long gains.</strong> 29 December 2022–2 February 2023. Both books use the same notional; trading costs are separate.</p>


The short loss was more than twice the long gain. The five worst stocks lost
4.037 points in total, only **24.7% of the short-book loss**. A handful of bad
positions therefore cannot explain the episode. It was a broad short-book
loss, reversing the preceding 24 sessions when shorts earned 4.778 points.
That makes shared exposures worth examining alongside individual names.

<details>
<summary>Adding contributions and measuring drawdowns</summary>
<div markdown="1">

For each date, $$r_{p,t}=c_{L,t}+c_{S,t}+c_{C,t}$$ is net P&L divided by fixed
notional. Accumulating these contributions gives

$$
\begin{aligned}
A_t&=\sum_{s\le t}r_{p,s},\\
D_t&=A_t-\max(0,A_1,\ldots,A_t).
\end{aligned}
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
and residuals. These are complementary views of the same portfolio P&L.

Health Care has the largest sector loss, **−3.074 points**, followed by
Consumer Discretionary (−1.516), Materials (−1.330) and Financials (−1.292).
Within Health Care, Sotera and Dentsply account for −1.070 and −0.764 points.
Together they explain about 60% of that sector's gross loss after offsetting
gains. In Financials, Rocket contributes −1.104 points. The concentration is
clearer at this level: the whole short-book loss is broad, but a few names
explain a large part of the losses within particular sectors.

Going one level deeper, Financial Services loses −1.324 points, while the
whole Financials sector loses −1.292. Other industries in the sector partly
offset it. I'm using later classifications to group these historical holdings,
so the labels may differ from those used at the time.

## How does the risk model explain the loss?

Adding up the stocks tells me where I lost money. To ask how much came from
shared bets, I need a **factor model**. It gives each stock a set of exposures,
then uses them to split its return into common effects and a residual.
This is the starting point in *Advanced Portfolio Management*, §8.1.1.

There are three steps behind the factor breakdown:

1. **Describe the stocks' characteristics.** In this example I use size,
   momentum, volatility, beta, short-term reversal and sector membership.
   The style scores are standardized so their scale is consistent across stocks.
   These are the model's **loadings**: how much of each characteristic a stock has.
2. **Estimate what those characteristics earned that day.** I fit the day's
   stock returns across the eligible stock universe, using the prior day's
   loadings. All factors enter the regression together. The fitted coefficients
   are that day's **factor returns**; the difference between each stock's actual
   and fitted return is its **residual**.
3. **Apply the portfolio's positions.** For each stock and factor, multiply the
   signed starting weight by the loading and the estimated factor return.
   Add across stocks for the day's contribution, then across days for the period.

$$
c_{i,k,t}=w_{i,t^-}\,b_{i,k,t^-}\,\widehat f_{k,t}.
$$

For Rocket's beta contribution, these three pieces are the short weight,
Rocket's beta loading and the day's estimated beta return. The short weight
is negative, so a positive loading and positive factor return produce a loss.
Repeating that calculation over the drawdown gives the **−0.225-point beta
contribution** we'll examine below.

### From a stock return to portfolio attribution

The same multiplication applies to the residual. For a covered stock, on the
model's return basis, the pieces add back to its contribution:

$$
\begin{aligned}
c_{i,t}&=w_{i,t^-}r_{i,t}\\
&=\sum_k c_{i,k,t}+w_{i,t^-}\widehat\varepsilon_{i,t}.
\end{aligned}
$$

Now imagine a grid: one row per stock, one column per factor, plus a residual
column. **Adding across a row gives that stock's P&L. Adding down a factor
column gives that factor's portfolio contribution.** Grouping the rows by
sector gives the modeled stocks' sector P&L. Full sector totals also include
uncovered stocks and any return-basis differences, as the reconciliation below
shows.

For the beta bar, I add every stock's signed beta exposure each day, multiply
by that day's beta return, then add the daily contributions over the period:

$$
\begin{aligned}
e_{k,t}&=\sum_i w_{i,t^-}b_{i,k,t^-},\\
C_k&=\sum_t e_{k,t}\widehat f_{k,t}.
\end{aligned}
$$

That is how Rocket's **−0.225 points** become part of the portfolio's
**−3.271-point beta loss**. A stock can contribute through several factors;
I don't assign its entire P&L to whichever factor looks most important.

<details>
<summary>What is fitted, and where does the risk model enter?</summary>
<div markdown="1">

For one day, stack stock returns in $$r$$ and prior-day loadings in $$B$$.
The fitted decomposition is

$$
\begin{aligned}
r&=B\widehat f+\widehat\varepsilon,\\
\widehat f&=\arg\min_{f\in\mathcal F}(r-Bf)^\top W(r-Bf).
\end{aligned}
$$

Here $$W$$ controls how much each stock matters in the fit. This example uses
square-root market-cap weights. The fit includes a common intercept and sector
effects constrained to have a weighted mean of zero; $$\mathcal F$$ denotes
that constraint. Without it, the intercept and the full set of sector indicators
would not give a unique set of coefficients. The intercept is the model's common
baseline; it is not the return
of a traded market index. Different universes, regression weights or factor
definitions can change the attribution.

Because each covered stock has intercept loading one, portfolio intercept
exposure is $$\sum_i w_i$$ on that covered set. Raw holdings beta instead is
$$\sum_i w_i\beta_i$$, using stock betas to the same named benchmark. Unequal
long and short dollars can therefore offset in beta. The standardized beta
loading used in this fit is different again. I keep the intercept contribution
in the factor split: moving it into residuals would change what "residual"
means, without improving the explanation of market sensitivity.

The factor returns are estimated **after** observing that day's stock returns.
Using today's return as the outcome is appropriate for explaining today's P&L;
using it to build yesterday's exposure or risk forecast would introduce look-ahead.
This is a cross-sectional fit across stocks each day, rather than a regression
of the portfolio's return history on factor returns.

To forecast portfolio risk, I also need a factor covariance matrix $$\Omega_f$$
and a residual covariance matrix $$D$$. Under the model's assumption that factor
and residual shocks are uncorrelated,

$$
\begin{aligned}
\Sigma&=B\Omega_f B^\top+D,\\
\sigma_p&=\sqrt{w^\top\Sigma w}.
\end{aligned}
$$

The covariance estimates give more weight to recent returns and use return
history through the previous session. But the sector classifications are
retrospective, so this is not a fully point-in-time test of risk forecasts.
The model assumes $$D$$ is diagonal: residual shocks in different stocks are uncorrelated.
That assumption can miss risk if the model leaves a shared driver unexplained.
The ordinary P&L split above uses realized factor returns; the covariance
estimates answer the additional question of how risky the positions were.

*Elements*, §14.1, also stresses that holdings must match the return interval.
If the portfolio trades within it, a single snapshot cannot explain all P&L.
The difference can include trading gains and losses as well as costs.

</div>
</details>

Applying this calculation to the drawdown attributes **−3.271
points to beta**, **−3.064 to volatility** and **−1.923 to momentum**.
Figure 4 puts those contributions alongside their contribution to realized risk.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/episode-factors-risk" mobile="/assets/portfolio-attribution/episode-factors-risk_mobile" version="1" alt="Episode factor contributions to P&L and realized portfolio volatility. Beta and volatility are the largest modeled losses; residual is the largest contributor to realized volatility." %}
</div>
<p class="figure-caption"><strong>Figure 4: The biggest loss and the biggest risk contribution differ.</strong> 29 December 2022–2 February 2023. P&amp;L contributions total −9.170 points; contributions to annualized realized volatility total 11.116 points. Panels have different scales.</p>

The last step is to reconcile the attribution with what the portfolio actually
lost. Table 2 adds all modeled factors—including the intercept and sector
effects—then the residuals, uncovered holdings and costs. Any difference
between the model's return basis and the accounting P&L gets its own line.

<div markdown="1">
<p class="table-caption"><strong>Table 2: Rebuilding the drawdown from its contributions.</strong> P&amp;L points, 29 December 2022–2 February 2023.</p>

| Component | Contribution |
| :--- | ---: |
| All modeled factors | −6.9142 |
| Residual on covered stocks | −1.8722 |
| Stocks outside model coverage | −0.2634 |
| Trading costs | −0.1205 |
| Return-basis reconciliation | 0.0000 |
| **Net portfolio P&L** | **−9.1703** |
{: .research-table .comparison-table .risk-performance-table }

</div>

The reconciliation difference is negligible here. Keeping it separate matters:
otherwise a mismatch in prices or trade timing could be mistaken for a
stock-selection result. The residual only describes the stocks the model
actually covered.

It's useful to compare Health Care's **−3.074-point stock P&L** with
its **+0.157-point modeled sector effect**. Health Care stocks also have
beta, volatility and other exposures, and their own residual returns. Adding
the sector-group loss to the factor losses would count the same P&L twice.

The risk panel adds something the loss ranking misses. Residual P&L loses
1.872 points, but contributes **4.604 points of realized volatility**, more
than any single factor. Beta contributes 1.991 volatility points and
volatility 1.191. Here **risk contribution** measures how each daily component
moves with total daily P&L. The residual was therefore a major source of day-to-day portfolio variation,
even though the modeled factors explain more of the accumulated loss. That is
why the largest P&L bar and the largest risk bar differ. These figures describe
what happened during the episode; they do not establish whether a forecast
made beforehand anticipated it.

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

## How did exposures and factor returns combine?

For a factor, daily contribution is the portfolio's signed exposure multiplied
by that day's factor return. Comparing the episode with the preceding 24
sessions helps me see how both pieces changed: the bets the strategy took
and what those bets earned.

<div markdown="1">
<p class="table-caption"><strong>Table 3: What changed across the turn of the year?</strong> Prior period: 23 November–28 December 2022. Loss period: 29 December 2022–2 February 2023. Exposure is the average signed standardized exposure on matched model-covered holdings; P&amp;L is in points.</p>

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

The averages in Table 3 summarize the change, but the attribution uses daily
positions. Multiplying the average beta exposure by the period's summed factor
return gives about −3.131 points; adding the actual daily products gives
−3.271. The difference comes from how exposure varied through the period.

Volatility combines both changes: the negative exposure grew, and its factor
return switched from −0.394 to +2.665 points. Momentum exposure also grew
while its factor return became negative. These are jointly estimated factor
returns. They need not match the returns of a separately constructed momentum
or low-volatility investment strategy.

So **both exposure changes and factor returns mattered**. The larger
volatility and momentum tilts added to the losses, while beta lost money
even with a slightly smaller tilt.

Would tighter exposure limits have helped? That's worth testing across the
full history, since they could also remove gains in other periods. The limits
would need to account for correlations too: **zero direct
exposure does not mean protection from a factor move**. Other factors held by
the portfolio can move with it, as *Elements*, §14.3, explains below.

<details>
<summary>What changes when factors move together?</summary>
<div markdown="1">

For a fixed portfolio with factor exposures $$e$$ and factor covariance
$$\Omega_f$$, its factor-P&L sensitivity to factor $$k$$ is

$$
\beta_{p,k}^{\mathrm{factor}}
=\frac{(\Omega_f e)_k}{(\Omega_f)_{kk}}.
$$

When that factor has positive variance, this can be nonzero even if $$e_k=0$$.
The other exposures enter through their covariance with it. It is a linear
sensitivity, not evidence that the factor caused every associated move.

The chapter's **maximal attribution** uses these correlations to collect the
modeled P&L associated with a chosen factor or group, including the part carried
through other factors. It offers another way to examine the same loss; the
figures here use ordinary attribution. Individual factor totals can also change
when the model's factors are re-expressed, even while total modeled P&L and
forecast risk stay the same. That is why a factor label alone cannot settle
what economic bet was responsible.

</div>
</details>

## Which stocks carried the losing factor?

Rocket, NCR and BJ's contributed most to the beta loss. But a stock can lose
through one factor and still make money overall, as Table 4 shows.

<div markdown="1">
<p class="table-caption"><strong>Table 4: A factor loss inside a winning stock.</strong> Contributions in P&amp;L points, 29 December 2022–2 February 2023. Stock totals are gross.</p>

| Stock | Beta component | Total stock P&L |
| :--- | ---: | ---: |
| Rocket | −0.225 | −1.104 |
| NCR | −0.220 | −0.584 |
| BJ's | −0.181 | +0.217 |
{: .research-table .comparison-table .risk-performance-table }

</div>

BJ's lost through beta but made money overall because its other components
more than offset that loss. Rocket's beta contribution accounts for only about
a fifth of its total loss. The beta ranking therefore identifies stocks
carrying that particular exposure; the stock-P&L ranking identifies the names
that actually cost the portfolio money. Rocket matters under both views, so
I'll use it to connect the attribution to an actual position.

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

The attribution model explains realized returns. To understand why the portfolio
held Rocket short, I now look at the strategy's **prediction model**. Its
predictor contributions explain a score used to rank stocks, so they answer a
different question from the factor P&L above.

The five predictors in Figure 5 went from a combined **−0.0266 to +0.0196**
between the start and end of the period.
The full prediction stayed negative, changing from **−0.0793 to −0.0869**.
At the end, the remaining terms and intercept contributed **−0.1065**:
$$+0.0196-0.1065=-0.0869$$. Those terms kept the overall score negative despite
the improvement in the five displayed predictors.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/rocket-prediction" mobile="/assets/portfolio-attribution/rocket-prediction_mobile" version="1" alt="Rocket's five displayed predictors change from a negative to a positive subtotal, but remaining terms plus intercept keep the full prediction negative at both observed endpoints." %}
</div>

<p class="figure-caption"><strong>Figure 5: Some predictors improved, but the overall score stayed negative.</strong> Rocket, 29 December 2022 (circles) and 2 February 2023 (diamonds). Values are model scores.</p>


The full prediction was negative throughout the 24 sessions. But its sign alone
doesn't tell me where Rocket ranked against other stocks, or whether that rank
improved. The score is not a calibrated expected return. Candidate ranks,
existing holdings and trading constraints together determine the position.

Rocket rose while the portfolio stayed short, and the full score remained
negative even as the displayed predictors improved. To explain why the
strategy kept the position, I'd need to follow Rocket's rank and the binding
constraints at each trading decision. The score alone can't answer that.

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

## How much should I trust that split?

The portfolio lost **9.17 P&L points**. That number is known. But how much
was due to common factors, and how much was specific to the stocks? That split
is estimated. This is the uncertainty that *Elements*, §14.2, asks us to take
seriously.

Think about how we estimated momentum's return. Stocks with high momentum can
also move on earnings announcements, company news and other individual events.
Across a finite set of stocks, those effects won't cancel perfectly. Some can
be picked up by the regression as momentum return. **Even a correctly specified
factor model has estimation noise.**

Here is the math for one day. Let $$r$$ be the vector of stock returns and
$$B$$ the matrix of loadings. Within the assumed model, $$f$$ is the underlying
factor return and $$\varepsilon$$ the stock-specific return. A hat marks an
estimate, and $$\eta$$ is the factor-return estimation error:

$$
\begin{aligned}
r&=Bf+\varepsilon,\\
\widehat f&=f+\eta.
\end{aligned}
$$

The estimated residual is whatever remains after subtracting the fitted factor
effects. Substituting the second equation into that subtraction gives

$$
\begin{aligned}
\widehat\varepsilon
&=r-B\widehat f\\
&=(Bf+\varepsilon)-B(f+\eta)\\
&=\varepsilon-B\eta.
\end{aligned}
$$

That last term is the important one: the error picked up by the factors is
removed from the residual. To translate it into portfolio P&L, multiply by
the signed position weights $$w$$. Call this attribution error $$\delta$$:

$$
\delta=w^\top B\eta=e^\top\eta,
\qquad e=B^\top w.
$$

For the covered positions, call the underlying factor contribution $$F=w^\top Bf$$
and the stock-specific contribution $$I=w^\top\varepsilon$$. Figure 6 shows what estimation does to
them. The same error appears twice, with opposite signs; these are **not two
independent errors**.

<div class="research-figure">
  {% include attribution-error-diagram.html %}
</div>
<p class="figure-caption"><strong>Figure 6: The split moves; its sum stays fixed.</strong> Within the assumed model, estimation adds the same amount to factor P&amp;L that it subtracts from residual P&amp;L. The error can have either sign.</p>

Getting the attribution to add up therefore cannot tell me whether either
piece is precise. If the factor-return error has covariance $$V_\eta$$, the
standard error of each portfolio attribution is

$$
s=\sqrt{e^\top V_\eta e}.
$$

This measures uncertainty in the **explanation of the P&L**. It is different
from the volatility of the portfolio's returns. Factor errors can move together,
so the off-diagonal entries of $$V_\eta$$ matter too.

For this drawdown, **−1.87 points is the fitted residual loss, not yet evidence
of poor stock-selection skill**. The distinction has a precise test: compare
that estimate with its attribution uncertainty. If the interval includes zero,
zero stock-specific P&L remains compatible with the estimate under the model.
If the whole interval is below zero, the episode supports a negative
stock-specific contribution under that model. Establishing a persistent
selection weakness would require evidence across other periods too.

For the whole period, write the residual estimate as $$\widehat I_T$$ and its
attribution standard error as $$s_T$$. With zero-mean Gaussian estimation errors
and known error variance, a 95% interval takes the form

$$
\widehat I_T\;\pm\;1.96\,s_T.
$$

The same width applies to the total factor attribution under these assumptions.
The empirical figures here show point estimates; $$s_T$$ has not been
calculated for this example. **The conclusion I can draw is that the chosen
model allocates most of the loss to common factors. I cannot tell from these
figures whether the residual loss is distinguishable from estimation noise.**
A reconciled total or a residual-volatility chart cannot answer that question.

There is a second uncertainty: **did I choose a suitable model?** Mine omits
value, quality and finer industry effects, so some common returns can end up
in the residual. An interval for estimation noise within this model would not
automatically cover those omissions. To attribute the residual loss to stock
selection, the interpretation would also have to survive a reasonable change
in factor specification. Otherwise the conclusion concerns this particular
model's unexplained return.

<details>
<summary>Computing the standard error, including across days</summary>
<div markdown="1">

The remaining ingredient is $$V_\eta$$. For weighted least squares in an
identified, full-rank factor basis, write the estimator as

$$
\begin{aligned}
A&=(B^\top WB)^{-1}B^\top W,\\
\widehat f&=Ar=f+A\varepsilon.
\end{aligned}
$$

Since $$\eta=A\varepsilon$$, residual-noise covariance $$D$$ implies

$$
V_\eta=ADA^\top.
$$

*Elements*, §14.2.2, uses generalized least squares with known $$D$$.
Setting $$W=D^{-1}$$ simplifies this to

$$
V_\eta=(B^\top D^{-1}B)^{-1}.
$$

My market-cap weighting requires the more general expression. The sector
constraint also requires working in an independent factor basis, with matching
portfolio exposures. And $$D$$ describes the underlying stock-specific noise;
it cannot simply be assumed equal to the covariance of fitted residuals, from
which the regression has already removed some noise.

One practical estimate is the **HC3 sandwich covariance**. With regression
leverage $$h_i=(BA)_{ii}$$, it uses

$$
\widehat V_{\eta,\mathrm{HC3}}
=A\,\operatorname{diag}\!\left(
\frac{\widehat\varepsilon_i^2}{(1-h_i)^2}
\right)A^\top.
$$

The leverage adjustment allows for the way fitting reduces residuals,
especially for influential observations. It permits different noise variances
across stocks, but assumes their errors are uncorrelated. Correlated omitted
drivers can still make the interval too narrow. Because this covariance is
estimated, normal intervals based on it are approximate; the exact
known-variance calculation above is a reference case. The interval also says
nothing by itself about persistent stock-selection skill. HC3 needs residual
degrees of freedom and $$h_i<1$$; otherwise the interval is unavailable.

Across days, the attribution error is $$\Delta_T=\sum_t\delta_t$$. Treating
the loadings and portfolio weights as fixed, its variance is

$$
s_T^2=\sum_t\operatorname{Var}(\delta_t)
+2\sum_{t<u}\operatorname{Cov}(\delta_t,\delta_u).
$$

If the daily estimation errors are uncorrelated, the cross-day terms vanish:

$$
s_T^2=\sum_t e_t^\top V_{\eta,t}e_t.
$$

So I add daily **error variances**, then take the square root. I don't add
standard errors or annualize the result: the interval concerns this particular
period's P&L. Dependence across days, estimated residual risks and changing
model parameters require more care. Even a well-calculated interval remains
conditional on the model and does not cover every omitted factor or mistaken
loading.

</div>
</details>

## What does this tell me about the strategy?

The early-2023 drawdown brought several parts of the strategy into focus. Long gains were
outweighed by a broad short-book loss. Within the factor model, beta,
volatility and momentum were the main losing styles: existing bets met
unfavourable payoffs, with larger average tilts adding to the volatility and
momentum losses. At the position level, Rocket shows how a rising stock and a
persistently negative model score can coexist with a costly short position.

My next test would be tighter exposure limits, keeping predictions fixed and
including the resulting trades and costs. I'd compare the full history,
including the periods when these tilts paid off, before deciding whether
the change helped.

I'd also want to separate stock selection from sizing. Did the stocks generally
do badly in the direction I held them, did I put more risk on the losers, or
did both happen? The calculation below separates those effects, though I
haven't evaluated it for this episode. Model coverage and attribution
uncertainty would still matter when interpreting the result.

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

I now have a clearer picture of the loss and a specific change to investigate.
Whether that change improves the strategy is the next test.

## References

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
Chapter 8; [*The Elements of Quantitative Investing*](https://linktr.ee/paleologo),
Chapter 14.

The [dashboard source code](https://github.com/piinghel/portfolio-pnl-dashboard)
is available if you'd like to explore your own portfolio.
