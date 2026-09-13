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

Both variances are on a daily scale; the 21 sessions provide the observations for the realized estimate. QLIKE is lower when the forecast is closer to that estimate. Figure 2 plots $\sqrt{q_t}$, the ratio of realized to forecast volatility. A ratio above one means the model underestimated volatility.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/hybrid-risk-model/calibration" mobile="/assets/hybrid-risk-model/calibration_mobile" version="4" alt="Realized divided by forecast volatility for Direct covariance, Direct recalibrated, Hybrid and 50:50 blend. A ratio of one is agreement. All models retain large underprediction outliers, including ratios above four." %}
</div>
<p class="figure-caption"><strong>Figure 2: Smaller typical forecast errors, with large misses still present.</strong> Each model has 1,195 overlapping 21-session windows, pooled across the three schedules, with outcomes through 2021. Boxes show the middle 50% and median; whiskers extend to observations within 1.5 interquartile ranges, with the rest shown as dots. These are distributions of forecast errors, not confidence intervals. The scale is logarithmic.</p>

Mean QLIKE is 0.327 for direct covariance, 0.290 after recalibration, 0.279 for the hybrid and 0.238 for the blend. Volatility exceeds its forecast by more than 30% in 24%, 18%, 14% and 12% of windows, respectively.

Those are smaller observed errors, but each model is forecasting **its own holdings**. Changing the covariance changes the portfolio, and the scale adjustment also depends on that portfolio's past forecast errors. The comparison therefore combines the risk estimator with the portfolios it selects.

A 21-session variance estimate is noisy, and overlapping windows share returns. These scores describe the errors in this sample; they do not establish a statistically significant ranking of the covariance estimators. To make that comparison, I'd want all four forecasts evaluated on the same holdings, with uncertainty estimates that account for the shared dates.

## Does that help the portfolio?

Covariance errors also affect where the optimizer puts capital. In unconstrained mean–variance optimization, $w^\star\propto\Sigma^{-1}\alpha$, where $\alpha$ is expected return. An underestimated variance in some direction can attract too much weight. The constrained optimizer used here has additional limits and trading penalties, so I assess it by comparing the resulting portfolios.[^evaluation]

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

## Where that leaves me

For this comparison, I still prefer direct covariance. The hybrid and blend make smaller forecast errors on their own portfolios, but that hasn't translated into a better return–risk trade-off. It also doesn't tell me which factor group caused the difference: the hybrid changes several parts of the risk estimate together.

The next comparison I'd find useful is to forecast risk for the same portfolios with all four models. That would separate forecasting differences from the optimizer's choice of holdings. It would give me a clearer reason to change the risk model than adding another factor to these backtests.

[^setup]: The hybrid uses an intercept, beta, sector exposures, size, momentum, short- and long-term reversals, volatility and dollar volume, plus ten residual PCs. All four completed versions share the historical study's additional L2 weight penalty of 0.000625, alongside the 2.5bp optimization trading penalty. This differs from the earlier portfolio-construction article's zero-L2 setup. The 5bp P&amp;L trading cost is separate. Sector classifications are retrospective; return marking and delisting coverage were not independently verified for this comparison. A separate attempt with a dense residual covariance could not complete because of missing residual history.

[^calibration]: Calibration uses each schedule's earlier fixed-weight, 21-session realized-to-raw-forecast variance ratios. Only fully observed, nonoverlapping windows within that schedule enter the trailing five-year calibration history. The squared scale is shrunk toward one with a 12-observation prior; it stays at one until 12 observations are available. Evaluation windows in Figure 2 overlap even though calibration inputs are selected this way.

[^model]: Giuseppe A. Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6), first edition (2021), §§4.3 and 11.1, pp. 40–41 and 168–169 (physical PDF pages 52–53 and 180–181).

[^blocks]: The joint block-matrix idea is illustrated for linked markets in Paleologo, *The Elements of Quantitative Investing*, draft of 9 September 2024, §7.6.1, Figure 7.2, p. 211 (physical PDF page 237). Figure 1 here applies that structure to named and residual factors.

[^evaluation]: Paleologo, *The Elements of Quantitative Investing*, “Evaluating Risk”: chapter 5 in the published edition; chapter 6 in the September 2024 draft used here. §§6.1–6.2, pp. 164–172 (physical PDF pages 190–198), discuss forecast losses and precision-matrix evaluation.

[^uncertainty]: Paired circular block bootstrap of the combined daily portfolio series: 1,000 resamples with 63-session blocks. The same sampled dates are used for each model in a comparison, and differences use unrounded estimates. The intervals describe uncertainty within this development history; they are not adjusted for multiple comparisons.
