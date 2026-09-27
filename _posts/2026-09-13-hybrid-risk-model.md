---
layout: post
title: "Does a Hybrid Risk Model Build Better Portfolios?"
date: 2026-09-13
last_modified_at: 2026-09-27
description: "A hybrid factor model forecasts its own portfolios' risk a little better than a recalibrated direct model, but at equal risk its portfolios are no better. Only a 50:50 blend forecasts clearly better."
permalink: /quants/hybrid-risk-model.html
toc: false
show_date: false
published: false
categories: ["Risk & attribution"]
---

The optimizer needs a covariance matrix to decide how much of each stock to
hold and which positions offset each other. The one I use, described in the
[portfolio construction article](/quants/2026/08/29/portfolio-optimization.html#covariance-and-risk-forecasts),
estimates stock volatilities and correlations directly from returns. A factor
model is the obvious alternative, and a hybrid of named factors plus
statistical ones is a popular version of it. The question here is whether a
model that forecasts portfolio risk better also gives the optimizer better
portfolios.

## What I compared

I kept the earlier version of the Ridge ranking used in the optimizer article,
its sizing scores, trading rules and constraints, including a 7% annual
forecast-volatility cap, and three rebalance schedules with equal notional.
The comparison covers the development history through 2021.[^setup]

- **Direct covariance:** short-window stock volatilities combined with
  longer-window correlations, shrunk halfway toward the identity, with the
  optimizer article's volatility multiplier of 1.18.
- **Direct, recalibrated:** the same matrix, with the multiplier re-estimated
  from past forecast errors instead of fixed.
- **Hybrid:** named factors (beta, sectors and price-based styles) plus ten
  principal components of what they leave unexplained.
- **50:50 blend:** the average of the direct and hybrid matrices.

The recalibrated direct model is the control that matters. Recalibration
scales the whole matrix by $s_t^2$, estimated only from earlier forecasts whose
21-session outcomes are known, so it corrects the overall level of forecast
risk without changing any correlations. The hybrid and blend are recalibrated
the same way.[^calibration] Whatever the hybrid adds beyond that control comes
from its structure, not from fixing the level.

## How the hybrid estimates risk

A fundamental factor model explains returns with characteristics named in
advance, such as beta, sector and size; a statistical model finds common
movements in the returns themselves, usually by principal component analysis
(PCA). The hybrid does both: the named factors first, then PCA on what they
leave unexplained, to catch shared movement the named factors miss.
[HRT's introduction to factor models](https://www.hudsonrivertrading.com/hrtbeat/modeling-equities-returns/)
is a good starting point. For the next day's stock returns $r$,

$$
r=Bf+Pg+\varepsilon,
$$

where $B$ holds the named exposures and $f$ their factor returns, $P$ the
loadings on ten residual components and $g$ their returns, and $\varepsilon$
the stock-specific rest.[^model]

<p class="table-caption"><strong>The named exposures.</strong> Definitions before cross-sectional winsorization and standardization. Windows count trading observations; the reversal, beta and volume calculations additionally require consecutive sessions.</p>
<table class="research-table settings-table">
<thead><tr><th>Exposure</th><th>Definition and interpretation</th></tr></thead>
<tbody>
<tr><th scope="row">Common return</th><td>An intercept equal to one for every stock. It captures the fitted common move.</td></tr>
<tr><th scope="row">Sectors</th><td>One indicator per sector: Communications, Consumer Discretionary, Consumer Staples, Energy, Financials, Health Care, Industrials, Materials, Real Estate, Technology and Utilities.</td></tr>
<tr><th scope="row">Beta</th><td>252-session covariance with the benchmark return divided by benchmark variance, clipped to [−4, 4]. Higher values mean greater historical market sensitivity.</td></tr>
<tr><th scope="row">Size</th><td>Log market capitalization. Higher values mean larger companies.</td></tr>
<tr><th scope="row">Momentum</th><td>Sum of the 20-, 60-, 125- and 252-observation price returns, including the most recent month. Higher values mean stronger past performance.</td></tr>
<tr><th scope="row">Short reversal</th><td>Negative compounded return over the past 21 sessions. Recent losers have higher exposure.</td></tr>
<tr><th scope="row">Long reversal</th><td>Negative compounded return over 504 sessions, ending 252 sessions ago: approximately years one to three in the past.</td></tr>
<tr><th scope="row">Volatility</th><td>Standard deviation of the past 21 daily returns, using divisor 21. Higher values mean more volatile stocks.</td></tr>
<tr><th scope="row">Trading activity</th><td>Log mean daily dollar volume over 21 sessions. This is the model's liquidity proxy; it does not directly measure spreads or market impact.</td></tr>
</tbody>
</table>

Each day's factor returns come from a cross-sectional regression of that
day's stock returns on the previous session's exposures, weighted by square-root
market cap, with sector returns constrained to average zero so that the
intercept carries the common move.[^descriptors] Exposures are winsorized and
standardized; momentum includes the recent month and so overlaps with short
reversal, and size overlaps with dollar volume, which makes individual
coefficients less stable but not the risk forecast they add up to.

The residual components come from PCA on the regression residuals, each
stock's history divided by its residual volatility so that the most volatile
stocks don't dominate. I keep ten components, a fixed research choice, and
make their loadings orthogonal to the named exposures so that the two blocks
don't describe the same direction.[^estimation]

Stacking the exposures as $L=[\,B\;P\,]$ gives the stock covariance

$$
\Sigma_H=L F_H L^\top+D,
$$

where $F_H$ is the joint covariance of all factor returns, including how named
and residual factors move together, and $D$ is diagonal with each stock's
specific variance. Factor volatilities use a 42-session half-life and factor
correlations a 360-session one, so the size of factor moves adapts quickly
while their pattern of co-movement, which needs more data, changes slowly.
Specific variances are shrunk toward a cross-sectional estimate, more so for
short histories, so that a stock with an unusually quiet past doesn't look
riskless.

## Forecast accuracy

For each rebalance I hold the chosen portfolio fixed for the next 21 sessions
and compare its realized daily variance with the forecast, using

$$
\begin{aligned}
q_t&=\frac{v_t^{\mathrm{real}}}{\widehat v_t},\\[4pt]
\mathrm{QLIKE}&=\frac{1}{T}\sum_t\left(q_t-\log q_t-1\right).
\end{aligned}
$$

QLIKE is zero when the two agree and treats the same proportional miss alike in
quiet and volatile periods; it penalizes underprediction more than
overprediction.[^evaluation]

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/hybrid-risk-model/calibration" mobile="/assets/hybrid-risk-model/calibration_mobile" version="4" alt="Realized divided by forecast volatility for Direct covariance, Direct recalibrated, Hybrid and 50:50 blend. A ratio of one is agreement. All models retain large underprediction outliers, including ratios above four." %}
</div>
<p class="figure-caption"><strong>Figure 1: Smaller typical errors, with large misses in every model.</strong> Realized divided by forecast volatility over 1,195 overlapping 21-session windows per model, pooled across the three schedules, through 2021. Boxes show the middle half and median; whiskers reach 1.5 interquartile ranges; log scale.</p>

Mean QLIKE is 0.327 for the fixed direct model, 0.290 recalibrated, 0.279 for
the hybrid and 0.238 for the blend. Most of the improvement is recalibration:
the fixed model's forecasts drifted low, especially after 2015, where its QLIKE
reaches 0.57. Beyond recalibration, the hybrid's gain of 0.012 has a
block-bootstrap interval of −0.063 to +0.040, which is noise; the blend's gain
of 0.052, with an interval of −0.083 to −0.024, is the only clear one. The
hybrid also shifts its misses rather than removing them: realized volatility
exceeds its forecast by more than 30% in 14% of windows against 18%, but falls
more than 23% short in 21% against 17%.

These are forecasts of each model's own holdings. On five common, fixed books
from an earlier study, the hybrid does no better than the recalibrated direct
model, and on that model's own book it does worse; the blend is the most
accurate on every one.

## Portfolio results

<div markdown="1">
<p class="table-caption"><strong>Table 1: Similar portfolios at equal risk.</strong> 26 January 1999–31 December 2021, 5,774 sessions, after 5 bp costs per traded dollar. Return is annual arithmetic net P&amp;L on fixed notional, in percent; the equal-risk column rescales each book to the recalibrated direct model's 7.28% volatility. The last two columns are the deepest additive drawdowns in each episode, in points.</p>

| Model | Return | Sharpe | Equal risk | 2008–09 | 2019–21 |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Direct | 11.87 | 1.54 | 11.20 | −16.1 | −15.6 |
| Direct, recalibrated | 11.43 | 1.57 | 11.43 | −15.5 | −14.5 |
| Hybrid | 9.91 | 1.48 | 10.79 | −11.3 | −18.7 |
| 50:50 blend | 10.18 | 1.52 | 11.03 | −12.7 | −19.1 |
{: .research-table .comparison-table .attribution-table }
</div>

The hybrid and blend earn less, but they also run smaller books: their
forecasts run a little high, so the same 7% cap leaves them at about 1.7 times
capital gross against 1.8 for the recalibrated direct model, and at 6.7%
realized volatility against 7.3%. At equal risk the hybrid's shortfall is about
0.6 points a year, not 1.5, and its Sharpe differs from the recalibrated direct
model's by −0.09, with a block-bootstrap interval of −0.34 to +0.14; the blend's
by −0.06, from −0.21 to +0.10.[^uncertainty] Trading costs are almost identical,
so the gap is in gross P&amp;L.[^costs]

The drawdowns don't favour one model either. The hybrid lost less in 2008–09
(11 points against 16) and in 2000–02 (5 against 7), and more in late 2019 to
early 2021 (19 against 14), which is where its deepest drawdown sits. Its
smaller daily tail losses are only its lower volatility: the average of the
worst 5% of days is about 2.1 times daily volatility for all four books.

## Which covariance I prefer

For this strategy, the recalibrated direct model. The hybrid forecasts its own
portfolios' risk no better once the direct model's level is recalibrated, and
its portfolios are indistinguishable at equal risk. The blend is the one
result worth keeping: it forecasts clearly better, on its own holdings and on
common ones, even though its portfolios are no better either.

That gap between better forecasts and unchanged portfolios is the interesting
part. The hybrid's books carry noticeably smaller momentum and low-volatility
tilts than the direct model's: is the factor model treating part of what the
ranking earns as risk? A named-factors-only version, with the same calibration,
would show whether the residual components help at all; and fitting the
residual components and their weights under one consistent objective would show
whether the way they are estimated is part of the problem.

[^setup]: The hybrid uses an intercept, beta, sector exposures, size, momentum, short- and long-term reversals, volatility and dollar volume, plus ten residual PCs. All four completed versions share the historical study's additional L2 weight penalty of 0.000625, alongside the 2.5bp optimization trading penalty. This differs from the earlier portfolio-construction article's zero-L2 setup. The 5bp P&amp;L trading cost is separate. Sector classifications are retrospective; return marking and delisting coverage were not independently verified for this comparison.

[^calibration]: Calibration uses each schedule's earlier fixed-weight, 21-session realized-to-raw-forecast variance ratios. Only fully observed, nonoverlapping windows within that schedule enter the trailing five-year calibration history. The squared scale is shrunk toward one with a 12-observation prior; it stays at one until 12 observations are available. Evaluation windows in Figure 2 overlap even though calibration inputs are selected this way.

[^model]: Giuseppe A. Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6), first edition (2021), §§4.3 and 11.1, pp. 40–41 and 168–169.

[^evaluation]: Paleologo, *The Elements of Quantitative Investing*, “Evaluating Risk”: chapter 5 in the published edition; chapter 6 in the September 2024 draft used here. §§6.1–6.2, pp. 164–172, discuss forecast losses and precision-matrix evaluation.

[^uncertainty]: Paired circular block bootstrap of the combined daily portfolio series: 1,000 resamples with 63-session blocks. The same sampled dates are used for each model in a comparison, and differences use unrounded estimates. The intervals describe uncertainty within this development history; they are not adjusted for multiple comparisons.

[^costs]: Two-way turnover is recovered from the modeled trading charge divided by 5bp per traded dollar, with no division by two. Costs are charged within each schedule before aggregation. Borrow fees, financing and market impact are not included.

[^descriptors]: Styles are winsorized at the cross-sectional 1st and 99th percentiles, then centred and scaled with the regression weights. Invalid numeric descriptors receive the same-date cross-sectional median before fitting. Momentum sums $p_t/p_{t-h}-1$ over $h\in\lbrace20,60,125,252\rbrace$; the inherited feature sums available horizons if some are missing, and its lags count stock observations. This is a coverage limitation to check for young or interrupted histories. The long-reversal return uses sessions $t-755$ through $t-252$. Sector gaps use a prior observed label where available, otherwise the current cross-sectional mode; sector vintage remains a limitation of the study.

[^estimation]: PCA requires at least 252 sessions; its equations describe the complete-history eligible universe. Specific-risk shrinkage toward the structural variance estimate has weight $0.3+0.7\times60/(60+n_i)$, where $n_i$ counts observed residual sessions; fewer than 60 observations receive the full structural estimate. Daily variance floors and caps precede a 1.5 variance buffer for PCA-excluded stocks, whose specific variance is also bounded below by the buffered pre-PCA estimate. Prior observed exposures may be carried for at most 21 sessions. The separate stale-exposure buffer applies $Q\Sigma Q$, with diagonal $Q_{ii}=\sqrt{1.5}$ for stale names and one otherwise. This is equivalent to replacing $L$ by $QL$ and $D$ by $QDQ$, preserving the factor form. Missing residual observations retain their dates and receive zero estimation weight.
