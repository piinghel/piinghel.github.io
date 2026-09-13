---
layout: post
title: "Fundamental, Statistical and Hybrid Risk Models"
date: 2026-09-13
description: "Adding named factors and residual PCA improved some risk forecasts, but did not give me a better portfolio."
permalink: /quants/hybrid-risk-model.html
toc: false
show_date: false
categories: ["Portfolio risk"]
---

After [comparing Ridge with tree models](/quants/xgboost-vector-leaves.html), I wanted to take a closer look at the risk model. It helps the optimizer decide how much to hold in each stock and which positions work well together.

I use a similar model to the one described in the [portfolio construction article](/quants/2026/08/29/portfolio-optimization.html#covariance-and-risk-forecasts), estimating stock volatility and correlation directly from returns. I wanted to see whether adding named factors and PCA could improve on it. Within each comparison, I kept the Ridge forecasts and trading rules the same, so the difference would come from the risk model.

## Why combine the two?

A **fundamental model** starts with named characteristics: market beta, sectors and styles such as size, momentum and volatility. Daily cross-sectional regressions estimate the factor returns. Here I use price-based characteristics; I haven't added accounting variables.

A **statistical factor model** learns common movement from returns, typically through principal component analysis (PCA). It can pick up patterns that the named factors miss, although the components can change meaning over time.

A **hybrid** fits the named factors first, then applies PCA to their standardized residual returns. That is what interested me: keep the economic structure while allowing for common risk left outside it.

## How the blocks fit together

A factor model writes stock returns as $r=Bf+\varepsilon$: exposures $B$ times factor returns $f$, plus residuals $\varepsilon$. Its stock covariance is[^model]

$$\Sigma=BFB^\top+D.$$

Here $F$ is the covariance of factor returns, and $D$ holds stock-specific variances on its diagonal. The model assumes the remaining specific shocks are uncorrelated with one another and with the factors. For portfolio weights $w$, forecast volatility is $\sqrt{w^\top\Sigma w}$.

In the hybrid, I join the named exposures $B$ and residual-PC loadings $P$ into $L=[B\;P]$. Figure 1 follows the multiplication for $N$ stocks, $K$ named factors and $J$ residual factors.[^blocks]

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/hybrid-risk-model/matrix-multiplication" mobile="/assets/hybrid-risk-model/matrix-multiplication_mobile" version="2" alt="Hybrid covariance: exposure blocks B and P multiply the joint factor covariance and transposed exposures to give common stock covariance C. Diagonal specific variance D completes total stock covariance Sigma H. N stocks, K named factors and J residual factors." %}
</div>
<p class="figure-caption"><strong>Figure 1: From two factor blocks to stock covariance.</strong> Blue marks named factors, ochre residual PCs and green their cross-covariances. The upper product gives common stock covariance; adding diagonal specific variance completes the model. Block sizes are schematic.</p>

The green blocks capture covariance between named and statistical factor returns. Even with orthogonal loadings, those returns can be correlated, so I estimate their covariance together. I convert the residual loadings back to stock-return units first.

## What I compared

I started with three styles, with and without two residual PCs. Both versions earned more than the direct model over the full history, but took more risk and had lower Sharpe ratios.[^earlier] I then added beta, sectors, reversals and liquidity, alongside ten residual PCs.

That gave me three ways to estimate covariance:

- **Direct covariance:** my starting model, combining short-window volatilities with a longer-window correlation estimate shrunk toward the identity.
- **Hybrid:** named factors plus ten residual PCs.
- **50:50 blend:** average the direct and hybrid covariance estimates first, then calibrate the result.

Before calibration, the blend is $\Sigma_{\mathrm{blend}}=0.5\Sigma_{\mathrm{direct}}+0.5\Sigma_H$. I also tried rescaling the direct model's volatility forecasts, using the same calibration rule as the hybrid and blend. That helps me see whether the extra factors add anything beyond correcting the overall level of forecast risk.

The direct model estimates the full stock covariance matrix. I haven't yet compared fundamental-only, standalone PCA and hybrid models under the same conditions. I also tried allowing correlations between the residuals, but couldn't complete that test because some residual histories were missing.

## Are the risk forecasts better?

I found the distinction in *Elements* useful here: how accurate are the risk forecasts, and how good are the resulting portfolios?[^evaluation] To check the forecasts, I hold each target portfolio's weights fixed and compare forecast variance with the sample variance of its daily returns over the next 21 sessions.

A useful score is **QLIKE**, which penalizes variance-forecast errors. Across $T$ windows, with $q_t$ equal to realized variance divided by forecast variance,

$$\mathrm{QLIKE}=\frac{1}{T}\sum_t\bigl(q_t-\log q_t-1\bigr).$$

Lower is better; zero means agreement in every window. I also want to see the large misses. Figure 2 shows the volatility ratios across 1,195 overlapping windows per model, through the end of 2021. A ratio above one means the model underestimated volatility.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/hybrid-risk-model/calibration" mobile="/assets/hybrid-risk-model/calibration_mobile" version="4" alt="Realized divided by forecast volatility for Direct covariance, Direct recalibrated, Hybrid and 50:50 blend. A ratio of one is agreement. All models retain large underprediction outliers, including ratios above four." %}
</div>
<p class="figure-caption"><strong>Figure 2: Smaller typical misses, with large misses still present.</strong> Boxes show the middle 50% of windows and the median. Whiskers extend to observations within 1.5 interquartile ranges; dots show the rest. The log scale keeps the full tail visible. Each model is evaluated on the portfolios it selects.</p>

Mean QLIKE falls from 0.327 for direct covariance to 0.290 after recalibration, 0.279 for the hybrid and 0.238 for the blend. Volatility exceeds its forecast by more than 30% in 24%, 18%, 14% and 12% of windows, respectively.

I wouldn't pick a model from these scores alone. Each model selects different holdings. For the recalibrated versions, the adjustment also depends on their own past forecast errors. A lower score could reflect an easier portfolio to forecast. I'd also want to compare the forecasts for the same holdings.

## Does that help the portfolio?

The optimizer uses the inverse covariance matrix, or precision matrix. In unconstrained mean–variance optimization, weights are proportional to $\Sigma^{-1}\alpha$, where $\alpha$ is expected return. Errors in apparently low-risk directions can therefore have a large effect on positions. That is why I also run each model through the same constrained optimizer.[^evaluation]

Table 1 compares the resulting portfolios over 5,774 common sessions, from 26 January 1999 to 31 December 2021, including 5 basis points of costs per traded dollar.

<p class="table-caption"><strong>Table 1: The hybrid and blend trade lower volatility for lower return and deeper drawdowns.</strong> Return is annual arithmetic net P&amp;L on fixed notional; “Vol.” is annualized volatility. “Max DD” is the largest additive drawdown, in percentage points (pp). Each row uses the combined portfolio return series.</p>
<table class="research-table comparison-table horizon-comparison">
<thead><tr><th>Model</th><th>Return<br>(%/yr)</th><th>Vol.<br>(%)</th><th>Sharpe</th><th>Max DD<br>(pp)</th></tr></thead>
<tbody>
<tr><th scope="row">Direct covariance</th><td>11.87</td><td>7.72</td><td>1.54</td><td>−16.11</td></tr>
<tr><th scope="row">Direct, recalibrated</th><td>11.43</td><td>7.28</td><td>1.57</td><td>−15.52</td></tr>
<tr><th scope="row">Hybrid</th><td>9.91</td><td>6.68</td><td>1.48</td><td>−18.74</td></tr>
<tr><th scope="row">50:50 blend</th><td>10.18</td><td>6.72</td><td>1.52</td><td>−19.09</td></tr>
</tbody>
</table>

The hybrid and blend both give up return, and neither has a higher Sharpe ratio than the recalibrated direct model. Their drawdowns are deeper too. The Sharpe differences remain uncertain: paired bootstrap intervals include zero. In 2017–2021, hybrid and blend Sharpe fall to 1.06 and 1.11, against about 1.43 for either direct-model version. The improved risk forecasts haven't given me a better portfolio.

## Where that leaves me

I still prefer direct covariance as a starting point. Adding a 52-week-high characteristic didn't clearly improve on the same hybrid model without it. The results from adding more PCs varied across portfolios and dates. I don't see a good reason to keep adding factors to this version.

I've already used this market history in earlier research, and I haven't compared the hybrid and blend with the direct model at a common volatility level. Before revisiting the hybrid, I'd compare fundamental, PCA and hybrid models using the same data, estimation dates and calibration rules, then check their forecasts on the same portfolios. Following *Elements*, I'd also compare minimum-variance portfolios under the same budget and trading constraints to see how well each model estimates the inverse covariance.

[^earlier]: Separate test, September 1998–December 2021: intercept, size, momentum and volatility. Annual net return / volatility were 11.97% / 7.72% for direct covariance, 13.67% / 9.83% for named factors, and 12.97% / 9.04% after adding two residual PCs. Return and Sharpe differences were statistically inconclusive. Its specification and sample differ from the expanded comparison.

[^model]: Giuseppe A. Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6), first edition (2021), §§4.3 and 11.1, pp. 40–41 and 168–169 (physical PDF pages 52–53 and 180–181).

[^blocks]: Paleologo, *The Elements of Quantitative Investing*, draft of 9 September 2024, §7.6.1, Figure 7.2, p. 211 (physical PDF page 237). This is an original diagram for named and residual factors.

[^evaluation]: Paleologo, *The Elements of Quantitative Investing*, “Evaluating Risk”: chapter 5 in the published edition; chapter 6 in the September 2024 draft used here. §§6.1–6.2, pp. 164–172 (physical PDF pages 190–198), discuss forecast losses and precision-matrix evaluation.
