---
layout: post
title: "Does a Hybrid Risk Model Improve the Portfolio?"
description: "Combining named factors with residual principal components improves average risk calibration, but the optimized portfolios still trail the incumbent."
permalink: /quants/hybrid-risk-model.html
toc: false
show_date: false
categories: ["Portfolio risk"]
---

After looking at [performance attribution](/quants/portfolio-attribution.html), I wanted to return to the model used to size the portfolio. Named factors make risk interpretable. Statistical factors can pick up common movements that those exposures leave behind. Combining them seems worth trying—but I care about the portfolio the optimizer builds with the resulting covariance matrix.

The completed tests give me a mixed answer: the hybrid forecasts risk more accurately on average, yet its portfolio earns less and has deeper drawdowns.

## What I combined

The named-factor model uses market beta, sectors and price-derived styles: size, momentum, reversals, volatility and liquidity. I then extract ten principal components from standardized residual returns and estimate the joint covariance of both factor blocks. The cross-covariances stay in the model: projecting loadings away from named exposures does not make the factor-return histories independent.[^model]

Here, “fundamental” describes a model built from specified stock characteristics. This comparison uses beta, sectors and price-based descriptors; accounting variables are a later extension.

I compare four constructions: the incumbent with fixed calibration, the incumbent with adaptive calibration, the hybrid, and a 50:50 covariance blend. The blend averages the raw hybrid and incumbent covariance matrices before applying its own calibration. All three adaptive versions update their scale using previously completed outcomes of their own target portfolios. Predictions and the remaining portfolio rules are held fixed.

## Better calibration

Figure 1 compares realized volatility with the model’s forecast over the following 21 sessions, holding each decision’s target portfolio fixed. A ratio of one means the two agree; values above one indicate underprediction. There are 1,195 overlapping windows per model, with outcomes through 2021.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/hybrid-risk-model/calibration" mobile="/assets/hybrid-risk-model/calibration_mobile" version="1" alt="Mean realized to predicted volatility ratios: incumbent 1.135, adaptive incumbent 1.075, hybrid 1.034 and covariance blend 1.020." %}
</div>
<p class="figure-caption"><strong>Figure 1: Average volatility calibration improves.</strong> Each point averages the ratio across that model’s own frozen target portfolios. The vertical reference marks one. Portfolios differ across models, so the comparison includes both estimation and allocation choices.</p>

The mean ratio falls from 1.135 for the incumbent to 1.034 for the hybrid and 1.020 for the blend. Adaptive calibration alone gets the incumbent to 1.075, which is a useful control: part of the improvement comes from changing how the forecast scale adapts.

The average still hides difficult windows. Realized volatility exceeds the forecast by more than 30% in about 14% of hybrid windows and 12% of blend windows. Their mean realized-to-predicted variance ratios remain 1.24 and 1.18. I would judge calibration from the distribution of misses as well as its average.

## The portfolio tradeoff

Figure 2 shows what happens when those risk estimates drive allocation. The financial comparison uses 5,774 common sessions from 26 January 1999 through 31 December 2021, with 5 basis points of costs per traded dollar.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/hybrid-risk-model/portfolio-tradeoff" mobile="/assets/hybrid-risk-model/portfolio-tradeoff_mobile" version="1" alt="Annual net return falls from 11.87 percent for the incumbent to 9.91 for the hybrid and 10.18 for the blend, while additive drawdowns deepen." %}
</div>
<p class="figure-caption"><strong>Figure 2: Better calibration does not improve the allocation.</strong> Annual arithmetic net return on fixed notional, and maximum additive drawdown in percentage points. A less negative drawdown is better. These financial metrics use the combined portfolio return series.</p>

The hybrid earns 9.91% a year, against 11.87% for the incumbent. Its volatility also falls, but Sharpe slips from 1.54 to 1.48 and maximum drawdown deepens from −16.11 to −18.74 percentage points. The blend earns 10.18%, with Sharpe 1.52 and drawdown −19.09 points. The adaptive incumbent has the highest observed Sharpe, 1.57, although the Sharpe differences remain statistically inconclusive.

I’m keeping the incumbent. The hybrid is useful evidence that improving average risk calibration and improving portfolio construction are separate objectives. These comparisons use already-inspected history. Before changing the risk model, I want a candidate that forecasts risk reliably and improves the allocation decisions it drives. Accounting variables remain a later extension.

[^model]: For the construction of characteristic-based factor models, see Giuseppe A. Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6), first edition (2021), §4.3, pp. 40–41 (physical PDF pages 52–53). The residual-PCA specification and results here are my own research comparison.
