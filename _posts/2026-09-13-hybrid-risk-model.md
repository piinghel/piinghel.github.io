---
layout: post
title: "Fundamental, Statistical and Hybrid Risk Models"
date: 2026-09-13
description: "A hybrid factor model makes smaller risk-forecast errors on its own portfolios, but that improvement does not carry through to portfolio performance."
permalink: /quants/hybrid-risk-model.html
toc: false
show_date: false
categories: ["Portfolio risk"]
---

After [comparing Ridge with tree models](/quants/xgboost-vector-leaves.html), I wanted to take a closer look at the risk model. It helps the optimizer decide how much to hold in each stock and which positions work well together.

I use a similar model to the one described in the [portfolio construction article](/quants/2026/08/29/portfolio-optimization.html#covariance-and-risk-forecasts), estimating stock volatility and correlation directly from returns. I wanted to see whether a factor model could improve on it. There are two questions here: does it forecast portfolio risk more accurately, and does the optimizer build better portfolios with it?

## What I compared

I kept the Ridge ranking, sizing scores, trading rules and portfolio constraints the same. Each version uses a 7% annual forecast-volatility cap and three rebalance schedules with equal capital. This is a comparison on development history through 2021, which has already informed earlier research.[^setup]

The three covariance estimates are:

- **Direct covariance:** short-window stock volatilities combined with longer-window correlations, shrunk toward the identity matrix.
- **Hybrid:** named factors—beta, sectors and price-based styles—plus ten principal components of the residual returns.
- **50:50 blend:** an equal average of the direct and hybrid covariance estimates before either is rescaled.

The direct model uses its existing volatility multiplier of 1.18. I also tried adjusting that multiplier from past forecast errors, using the same rule as the hybrid and blend. This is the “Direct, recalibrated” row in the results. It lets me check whether the extra factors help beyond correcting the overall level of forecast risk.

For each of those three recalibrated versions, the covariance used by the optimizer is $s_t^2\Sigma_t^{\mathrm{raw}}$. The scale $s_t$ is estimated only from earlier forecasts whose full 21-session outcomes are already known. The blend has its own scale, applied after averaging the two raw covariance estimates.[^calibration]

<h2 id="how-the-blocks-fit-together">How the hybrid estimates risk</h2>

A **fundamental factor model** starts with named stock characteristics, such as beta, sector and size. Cross-sectional regressions estimate the daily factor returns. A **statistical factor model** uses patterns in returns to find common sources of risk, typically through principal component analysis (PCA).

The hybrid combines these ideas. I fit the named factors first, then apply PCA to their volatility-standardized residual returns. At a given estimation date, the daily return model is

$$
r=Bf+Pg+\varepsilon.
$$

Here $r$ contains the returns of $N$ stocks. The $K$ named factor returns are $f$, with exposures $B$; the $J$ residual-PC returns are $g$, with loadings $P$. Thus $B$ is $N\times K$ and $P$ is $N\times J$. The remaining stock-specific returns are $\varepsilon$.[^model]

I put the two sets of exposures together as $L=[\,B\;P\,]$, an $N\times(K+J)$ matrix, and estimate the **joint factor covariance**:

$$
F_H=
\begin{pmatrix}
F_{ff} & F_{fg}\\
F_{fg}^{\top} & F_{gg}
\end{pmatrix}.
$$

The diagonal blocks $F_{ff}=\operatorname{Cov}(f)$ and $F_{gg}=\operatorname{Cov}(g)$ describe covariance within each factor group. The cross block $F_{fg}=\operatorname{Cov}(f,g)$ is $K\times J$: it describes how the named and statistical factor returns move together. The lower block is its transpose, so the whole matrix is symmetric.

Mapping that factor covariance back to stocks gives shared covariance $C=L F_H L^\top$. Adding the remaining stock-specific variances gives

$$
\Sigma_H=\underbrace{L F_H L^\top}_{\text{shared stock covariance}}+D.
$$

The diagonal matrix $D$ contains $\operatorname{Var}(\varepsilon_i)$ for each stock. It measures what remains after **both** factor groups. This model treats those remaining shocks as uncorrelated across stocks and with the factors. Both $C$ and $D$, and therefore $\Sigma_H$, are $N\times N$ daily covariance matrices.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/hybrid-risk-model/matrix-multiplication" mobile="/assets/hybrid-risk-model/matrix-multiplication_mobile" version="3" alt="Joint factor covariance F H contains named-factor, residual-PC and cross-covariance blocks. Applying the stock exposures L equals B P on both sides gives shared stock covariance C. Adding diagonal specific covariance D changes only the diagonal to produce total covariance Sigma H. Matrix blocks and diagonal tiles are schematic." %}
</div>
<p class="figure-caption"><strong>Figure 1: From factor covariance to stock covariance.</strong> The first arrow applies the stock exposures: $C=L F_H L^\top$. The second adds $D$ to the diagonal. Green blocks retain covariance between the two factor groups. Colours and diagonal tiles show structure, not measured values.</p>

Figure 1 makes the role of the cross terms explicit.[^blocks] Orthogonal loadings describe a relationship across stocks; $F_{fg}$ describes factor returns moving together over time. One does not force the other to zero. I therefore estimate the full joint covariance, after converting the residual-PC loadings back to stock-return units.

For signed portfolio weights $w$, daily forecast variance is $w^\top\widehat\Sigma w$, where $\widehat\Sigma$ includes the scale adjustment used by the optimizer. Annual forecast volatility is $\sqrt{252\,w^\top\widehat\Sigma w}$. This is the quantity constrained by the 7% risk cap.

## Are the risk forecasts better?

I follow the distinction in *Elements* between assessing the forecasts and assessing the portfolios they produce.[^evaluation] For the forecast check, I hold each selected portfolio's weights fixed and calculate its daily returns over the next 21 sessions. Their sample variance is the realized-variance proxy.

Let $\widehat v_t=w_t^\top\widehat\Sigma_t w_t$ be the forecast daily variance and $v_t^{\mathrm{real}}$ that subsequent sample variance. Across $T$ forecast windows, I compare them using

$$
\begin{aligned}
q_t&=\frac{v_t^{\mathrm{real}}}{\widehat v_t},\\[6pt]
\mathrm{QLIKE}&=\frac{1}{T}\sum_{t=1}^{T}
\left(q_t-\log q_t-1\right).
\end{aligned}
$$

Both variances are on a daily scale; the 21 sessions provide the observations for the realized estimate. QLIKE is zero when the two agree and increases as they diverge. Because it uses their ratio, the same proportional miss receives the same loss in a quiet period and a volatile one. It also treats underprediction and overprediction differently: forecasting half the realized variance gives a loss of about 0.31; forecasting twice as much gives about 0.19.

That is one useful view of forecast error. I also want to know whether risk is systematically too low, how often the model misses badly, and whether those misses arrive together. Figure 2 starts with $\sqrt{q_t}$, the ratio of realized to forecast volatility. A ratio of 1.3 means volatility came in 30% above forecast; the corresponding variance ratio is $1.3^2=1.69$.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/hybrid-risk-model/calibration" mobile="/assets/hybrid-risk-model/calibration_mobile" version="4" alt="Realized divided by forecast volatility for Direct covariance, Direct recalibrated, Hybrid and 50:50 blend. A ratio of one is agreement. All models retain large underprediction outliers, including ratios above four." %}
</div>
<p class="figure-caption"><strong>Figure 2: Smaller typical forecast errors, with large misses still present.</strong> Each model has 1,195 overlapping 21-session windows, pooled across the three schedules, with outcomes through 2021. Boxes show the middle 50% and median; whiskers extend to observations within 1.5 interquartile ranges, with the rest shown as dots. These are distributions of forecast errors, not confidence intervals. The scale is logarithmic.</p>

Mean QLIKE is 0.327 for direct covariance, 0.290 after recalibration, 0.279 for the hybrid and 0.238 for the blend. Volatility exceeds its forecast by more than 30% in 24%, 18%, 14% and 12% of windows, respectively.

The average level still matters. Mean variance ratios are 1.47, 1.33, 1.24 and 1.18 in the same order. Even the blend therefore has realized variance averaging about 18% above its own forecast when each window receives equal weight. Its mean **volatility** ratio is only 1.02. Those statements can coexist because averaging after taking a square root gives large misses less weight. A volatility ratio close to one on average is too weak a check on its own.

I read the centre and tails together. A model can reduce the frequency of underprediction simply by forecasting more risk everywhere, which may leave capital unused. I would check the opposite tail too, then split the errors by forecast-risk level and calendar period. That would show whether an apparently good average hides poor calibration in the periods when risk is highest. The 30% threshold here is a descriptive tolerance; it has no associated confidence level or guaranteed exceedance rate.

Those are smaller observed errors, but each model is forecasting **its own holdings**. Changing the covariance changes the portfolio, and the scale adjustment also depends on that portfolio's past forecast errors. The comparison therefore combines the risk estimator with the portfolios it selects.

A 21-session variance estimate is noisy, and overlapping windows share returns. These scores describe the errors in this sample; they do not establish a statistically significant ranking of the covariance estimators. Comparing forecasts on common holdings would help separate those effects. I return to that test below.

## Does that help the portfolio?

Covariance errors also affect where the optimizer puts capital. Consider a long position in one stock and an equally sized short position in another, with weights $a$ and $-a$. Their combined variance is

$$
a^2\left(\sigma_1^2+\sigma_2^2-2\rho\sigma_1\sigma_2\right).
$$

Here $\rho$ is their correlation. If the model overstates that correlation, the two positions look like a better hedge than they really are. Accurate forecasts of each stock's volatility would not catch this error.

In unconstrained mean–variance optimization, $w^\star\propto\Sigma^{-1}\alpha$, where $\alpha$ is expected return. The inverse covariance, or **precision matrix**, determines which combinations of positions look attractive relative to their risk. Underestimated risk in one of those combinations can attract too much capital. The constrained optimizer used here also has position limits and trading penalties, so the relevant check is what happens to its chosen portfolios.[^evaluation]

Table 1 uses 5,774 common sessions, from 26 January 1999 to 31 December 2021, including 5 basis points of costs per traded dollar. These are the combined portfolios with their actual changing weights, whereas Figure 2 holds each target portfolio fixed for its forecast check.

<p class="table-caption"><strong>Table 1: The hybrid and blend have lower return and volatility, but deeper drawdowns.</strong> Return is annual arithmetic net P&amp;L on fixed notional; “Vol.” is annualized volatility. Sharpe is annualized mean net P&amp;L divided by volatility, with a zero risk-free rate. “Max DD” is the largest additive drawdown, in percentage points (pp).</p>
<table class="research-table comparison-table horizon-comparison">
<thead><tr><th>Model</th><th>Return<br>(%/yr)</th><th>Vol.<br>(%)</th><th>Sharpe</th><th>Max DD<br>(pp)</th></tr></thead>
<tbody>
<tr><th scope="row">Direct covariance</th><td>11.87</td><td>7.72</td><td>1.54</td><td>−16.11</td></tr>
<tr><th scope="row">Direct, recalibrated</th><td>11.43</td><td>7.28</td><td>1.57</td><td>−15.52</td></tr>
<tr><th scope="row">Hybrid</th><td>9.91</td><td>6.68</td><td>1.48</td><td>−18.74</td></tr>
<tr><th scope="row">50:50 blend</th><td>10.18</td><td>6.72</td><td>1.52</td><td>−19.09</td></tr>
</tbody>
</table>

The hybrid and blend both give up return, and neither has a higher Sharpe ratio than the recalibrated direct model. Their drawdowns are deeper too. The common forecast-risk cap has produced different realized volatilities, so lower return alone would be an incomplete comparison.

Relative to the recalibrated direct model, the hybrid's Sharpe difference is −0.09, with a 95% block-bootstrap interval of [−0.34, 0.14]. The blend's difference is −0.06, with an interval of [−0.21, 0.10]. These intervals include both improvement and deterioration; the point estimates don't establish a reliable Sharpe advantage for either approach.[^uncertainty]

### Losses, exposure and trading costs

Sharpe treats positive and negative variation symmetrically. I also look at **historical expected shortfall**: the average daily net P&amp;L among the worst 5% of days. It describes how severe those bad days were in this backtest. Maximum drawdown answers a different question: how far cumulative P&amp;L fell from a previous peak. The order of returns matters for drawdown, so a long sequence of moderate losses can be more damaging than a single large loss followed by a recovery.

<p class="table-caption"><strong>Table 2: Daily tail losses improve, while trading costs stay similar.</strong> Same combined portfolios and 5,774 sessions as Table 1. Tail P&amp;L is the average of the worst 5% of daily net observations, as a percentage of fixed notional. Two-way turnover counts purchases plus sales, in multiples of capital per year. Cost is the annual modeled trading charge, in percentage points.</p>
<table class="research-table comparison-table horizon-comparison">
<thead><tr><th>Model</th><th>Tail P&amp;L<br>(%/day)</th><th>Turnover<br>(×/yr)</th><th>Cost<br>(pp/yr)</th></tr></thead>
<tbody>
<tr><th scope="row">Direct covariance</th><td>−1.04</td><td>28.19</td><td>1.41</td></tr>
<tr><th scope="row">Direct, recalibrated</th><td>−0.99</td><td>27.46</td><td>1.37</td></tr>
<tr><th scope="row">Hybrid</th><td>−0.89</td><td>28.70</td><td>1.44</td></tr>
<tr><th scope="row">50:50 blend</th><td>−0.89</td><td>27.47</td><td>1.37</td></tr>
</tbody>
</table>

The hybrid and blend have smaller daily tail losses, even though their maximum drawdowns are deeper. These portfolios also have different overall volatilities, so the comparison leaves open whether the hybrid offers better tail protection at equal risk. Historical expected shortfall has sampling uncertainty and says little about losses beyond those observed here.

The cost comparison helps explain the return gap. The hybrid earns 11.34% a year before modeled costs, against 12.80% for the recalibrated direct model. Its cost is only about 0.06 percentage points higher. Most of the net-return gap therefore comes from gross portfolio P&amp;L. The blend's trading cost is almost identical to that direct model's.[^costs]

The portfolios also carry different exposures. Gross exposure adds the absolute sizes of the long and short positions. It averages about 1.68 times capital for the hybrid and 1.73 for the blend, versus 1.81 for recalibrated direct covariance. Their full-period realized market betas—the regression slopes of daily net P&amp;L on the study's market return—are about 0.01, 0.03 and 0.08, respectively. The covariance choice has changed position sizes and market sensitivity. Identifying which holdings or factor tilts caused the lost return would require a matched attribution.

## What I would test next

I would keep the full portfolio comparison and add two focused tests. They answer different questions about the same risk model.

First, I would evaluate every model on the same dated portfolios, including holdings selected by each model. Each candidate would forecast risk for every portfolio, so choosing one model's holdings would not determine the whole comparison. Alongside QLIKE and the calibration ratios, I would add **mean squared error of variance**:

$$
\mathrm{MSE}=\frac{1}{T}\sum_{t=1}^{T}
\left(v_t^{\mathrm{real}}-\widehat v_t\right)^2.
$$

MSE measures the absolute size of variance errors. Large errors in high-volatility periods carry more weight than they do under QLIKE. That makes the two losses useful companions. For common holdings, QLIKE and variance MSE also have a useful theoretical property: under the required conditional-unbiasedness assumptions, using a noisy variance proxy preserves their expected forecast ranking. That result does not guarantee a reliable ranking in this finite sample, or establish that our 21-session proxy satisfies those assumptions.[^losses]

I would report paired loss differences by calendar period and forecast-risk level, with confidence intervals that resample blocks of common dates. All models and schedules would stay together within each sampled block, preserving their shared shocks. This would show whether an improvement is broad or concentrated in a few episodes, while accounting for overlapping outcomes.

Second, I would construct **minimum-variance portfolios** under identical investment constraints, with no alpha forecast in the objective. A simple version fixes total investment to one, requires long-only weights and applies the same name cap to every model. Each covariance estimate then chooses the portfolio it considers least risky. Comparing subsequent realized variance, concentration and turnover would test the diversification choices more directly. Fixing investment prevents the zero portfolio from winning; this test addresses a different use case from the long–short Ridge strategy.[^evaluation]

## Where that leaves me

For this comparison, I still prefer direct covariance. The hybrid and blend improve their own-portfolio forecast scores and have smaller daily tail losses, but they also give up return and experience deeper drawdowns. The Sharpe differences remain uncertain. I would want the common-portfolio forecast test and the minimum-variance comparison to explain where the extra structure helps before changing the risk model on that basis.

[^setup]: The hybrid uses an intercept, beta, sector exposures, size, momentum, short- and long-term reversals, volatility and dollar volume, plus ten residual PCs. All four completed versions share the historical study's additional L2 weight penalty of 0.000625, alongside the 2.5bp optimization trading penalty. This differs from the earlier portfolio-construction article's zero-L2 setup. The 5bp P&amp;L trading cost is separate. Sector classifications are retrospective; return marking and delisting coverage were not independently verified for this comparison. A separate attempt with a dense residual covariance could not complete because of missing residual history.

[^calibration]: Calibration uses each schedule's earlier fixed-weight, 21-session realized-to-raw-forecast variance ratios. Only fully observed, nonoverlapping windows within that schedule enter the trailing five-year calibration history. The squared scale is shrunk toward one with a 12-observation prior; it stays at one until 12 observations are available. Evaluation windows in Figure 2 overlap even though calibration inputs are selected this way.

[^model]: Giuseppe A. Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6), first edition (2021), §§4.3 and 11.1, pp. 40–41 and 168–169 (physical PDF pages 52–53 and 180–181).

[^blocks]: The joint block-matrix idea is illustrated for linked markets in Paleologo, *The Elements of Quantitative Investing*, draft of 9 September 2024, §7.6.1, Figure 7.2, p. 211 (physical PDF page 237). Figure 1 here applies that structure to named and residual factors.

[^evaluation]: Paleologo, *The Elements of Quantitative Investing*, “Evaluating Risk”: chapter 5 in the published edition; chapter 6 in the September 2024 draft used here. §§6.1–6.2, pp. 164–172 (physical PDF pages 190–198), discuss forecast losses and precision-matrix evaluation.

[^uncertainty]: Paired circular block bootstrap of the combined daily portfolio series: 1,000 resamples with 63-session blocks. The same sampled dates are used for each model in a comparison, and differences use unrounded estimates. The intervals describe uncertainty within this development history; they are not adjusted for multiple comparisons.

[^costs]: Two-way turnover is recovered from the modeled trading charge divided by 5bp per traded dollar, with no division by two. Costs are charged within each schedule before aggregation. Borrow fees, financing and market impact are not included.

[^losses]: Andrew J. Patton, [“Volatility forecast comparison using imperfect volatility proxies”](https://public.econ.duke.edu/~ap172/Patton_vol_proxies_JoE_2011.pdf), *Journal of Econometrics* 160 (2011), pp. 246–256, especially §3. MSE here is squared error in variance units, not squared error in the variance ratio. The common-portfolio MSE and minimum-variance comparisons above are proposed tests, with no results reported here.
