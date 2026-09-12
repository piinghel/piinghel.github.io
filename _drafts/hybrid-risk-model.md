---
layout: post
title: "Fundamental, Statistical and Hybrid Risk Models"
description: "How factor exposures become a covariance matrix, how a hybrid combines named and statistical factors, and what my completed portfolio comparisons show."
permalink: /quants/hybrid-risk-model.html
toc: false
show_date: false
categories: ["Portfolio risk"]
---

After looking at [performance attribution](/quants/portfolio-attribution.html), I wanted to return to the risk model used to size the portfolio. A fundamental model starts with named exposures. A statistical model learns common movement from returns. A hybrid combines the two. What changes inside the covariance matrix, and does that help the portfolio?

## From factors to stock risk

A factor model writes stock returns as $r=Bf+\varepsilon$. Each row of $B$ belongs to a stock; each column belongs to a factor. Multiplying that row by the factor-return vector $f$ gives the stock’s modeled return. The residual $\varepsilon$ is what remains.[^model]

For risk, the corresponding calculation is

$$\Sigma=BFB^\top+D.$$

Here $F$ is the covariance matrix of factor returns and $D$ contains stock-specific variances on its diagonal. This form assumes the remaining stock-specific shocks are mutually uncorrelated and uncorrelated with the factors. With $N$ stocks and $K$ factors, the dimensions are $(N\times K)(K\times K)(K\times N)$, producing an $N\times N$ stock covariance matrix.

For portfolio weights $w$, forecast volatility is $\sqrt{w^\top\Sigma w}$. Equivalently, $B^\top w$ gives portfolio factor exposures first, so portfolio variance is $(B^\top w)^\top F(B^\top w)+w^\top Dw$.

## Where the factors come from

**Fundamental.** I specify the columns of $B$: market beta, sectors and styles such as size, momentum or volatility. Cross-sectional regressions estimate their daily factor returns; those histories estimate $F$. Here “fundamental” means a model built from specified characteristics. The available tests use price-based descriptors; accounting variables are a later extension.

**Statistical.** A PCA factor model estimates its loadings from return co-movement. In a simple covariance-PCA construction, the leading eigenvectors form $P$, their eigenvalues form $\Lambda$, and $\Sigma\approx P\Lambda P^\top+D$. The retained components explain broad common variation, though their economic meaning may be less stable. Purely return-based estimation can also keep the full stock matrix. My current model takes that route: short-window stock volatilities surround a longer-window correlation estimate shrunk toward the identity. It uses no named factor exposures and no PCA reduction.

**Hybrid.** I first fit named factors, then extract statistical components from standardized residual returns. Let $P$ now denote these residual loadings, restored to stock-return units. With $K$ named factors and $J$ residual factors, the combined exposure matrix is $L=[B\;P]$. Figure 1 shows how the two blocks enter the same covariance calculation.[^blocks]

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/hybrid-risk-model/matrix-multiplication" mobile="/assets/hybrid-risk-model/matrix-multiplication_mobile" version="2" alt="Symbolic hybrid covariance: loadings L combine named block B and residual statistical block P. The factor covariance has BB, BP, PB and PP blocks. Multiplication by L and its transpose gives common stock covariance C; adding diagonal specific variance D gives total covariance Sigma H." %}
</div>
<p class="figure-caption"><strong>Figure 1: The hybrid as a block-matrix product.</strong> Blue marks named-factor blocks, ochre statistical blocks, and green their cross-covariances. Multiplication maps the factor covariance into the stock space; diagonal specific risk completes the model. Dimensions are symbolic and block sizes schematic.</p>

The off-diagonal blocks matter. Expanding the product gives named-factor risk $BF_{BB}B^\top$, statistical risk $PF_{PP}P^\top$, and the two cross terms $BF_{BP}P^\top+PF_{PB}B^\top$. Projecting loadings away from named exposures does not guarantee that the factor-return histories are uncorrelated. I estimate those cross-covariances in the hybrid.

A **50:50 covariance blend** combines completed covariance estimates instead: $\Sigma_{\mathrm{blend}}=0.5\Sigma_{\mathrm{current}}+0.5\Sigma_H$, before its own calibration. This averages variance estimates for any fixed portfolio; taking the square root means it does not average volatility directly. It also differs from splitting capital equally between two optimized portfolios.

## What the completed tests show

The earlier fundamental-only test used size, momentum and volatility, plus a common intercept. Over September 1998–December 2021 it earned 13.67% a year at 9.83% volatility, against 11.97% at 7.72% for the current model. Adding two residual PCs reduced volatility to 9.04% and return to 12.97%; neither improved the observed Sharpe. This was a narrow factor specification, and the return and Sharpe differences were statistically inconclusive.

The expanded comparison below adds beta, sectors, reversals and liquidity, with ten residual PCs. Its four completed constructions are the current model, the current model with adaptive calibration, the hybrid, and their 50:50 covariance blend. All three adaptive versions scale forecasts using previously completed outcomes of their own target portfolios. Predictions and the other portfolio rules stay fixed within this comparison.

These are separate studies with different specifications and common periods. A standalone PCA-only portfolio is not among their completed runs. The expanded beta/sector variant with dense residual covariance also stopped because some eligible stocks lacked residual history; it supplies no completed financial result.

## Calibration and allocation

Figure 2 compares realized volatility with the forecast over the following 21 sessions, holding each decision’s target portfolio fixed. One means agreement; values above one indicate underprediction. There are 1,195 overlapping windows per model, with outcomes through 2021.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/hybrid-risk-model/calibration" mobile="/assets/hybrid-risk-model/calibration_mobile" version="3" alt="Boxplots of realized to forecast volatility for the current model, adaptive current model, hybrid and covariance blend. All retain long upper tails, including windows above four times forecast volatility." %}
</div>
<p class="figure-caption"><strong>Figure 2: Better average calibration still leaves large misses.</strong> Boxes contain the middle 50% of windows; the internal line is the median. Whiskers extend to observations within 1.5 interquartile ranges of the box, with all remaining observations plotted as dots. The logarithmic axis retains the full upper tail. Portfolios differ across models, so the comparison includes both estimation and allocation choices.</p>

The mean realized-to-forecast volatility ratio falls from 1.135 for the current model to 1.075 with adaptive calibration, 1.034 for the hybrid and 1.020 for the blend. The frequency of volatility exceeding its forecast by more than 30% falls from 24% to 18%, 14% and 12%, respectively. The blend’s mean variance ratio remains 1.18: average volatility near one leaves room for large misses.

Lower volatility matters when judging the return the portfolio gives up. Table 1 puts both beside Sharpe and drawdown over 5,774 common sessions from 26 January 1999 through 31 December 2021, with 5 basis points of costs per traded dollar, as in the earlier comparison.

<p class="table-caption"><strong>Table 1: The hybrid and blend have lower volatility, lower return and deeper drawdowns.</strong> Annual arithmetic net return and annualized volatility (%), Sharpe, and maximum additive drawdown (percentage points), computed from each combined portfolio return series on fixed notional.</p>
<table class="research-table comparison-table horizon-comparison">
<thead><tr><th>Model</th><th>Return (%)</th><th>Vol. (%)</th><th>Sharpe</th><th>Max DD (pp)</th></tr></thead>
<tbody>
<tr><th scope="row">Current model</th><td>11.87</td><td>7.72</td><td>1.54</td><td>−16.11</td></tr>
<tr><th scope="row">Current model, adaptive</th><td>11.43</td><td>7.28</td><td>1.57</td><td>−15.52</td></tr>
<tr><th scope="row">Hybrid</th><td>9.91</td><td>6.68</td><td>1.48</td><td>−18.74</td></tr>
<tr><th scope="row">50:50 covariance blend</th><td>10.18</td><td>6.72</td><td>1.52</td><td>−19.09</td></tr>
</tbody>
</table>

The blend reduces annual volatility from 7.72% to 6.72%, but return falls from 11.87% to 10.18% and drawdown deepens from −16.11 to −19.09 percentage points. Lower daily volatility therefore does not translate into a smaller peak-to-trough loss. The adaptive current model has the highest observed Sharpe, 1.57, although the Sharpe differences remain statistically inconclusive.

I’m keeping the current model. The 50:50 blend improves average calibration, but I want evidence of better allocation decisions before switching. There is no matched-volatility blend test here to establish how it would compare at the current model’s risk level. These results use already-inspected history; they are a comparison of the tested constructions, with accounting-based extensions left for later.

[^model]: For characteristic-based estimation and the covariance identity, see Giuseppe A. Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6), first edition (2021), §4.3 and §11.1, pp. 40–41 and 168–169 (physical PDF pages 52–53 and 180–181).

[^blocks]: Giuseppe A. Paleologo, *The Elements of Quantitative Investing*, draft of 9 September 2024, §7.6.1, Figure 7.2, p. 211 (physical PDF page 237). The diagram here is an original application to named and residual statistical factors; the book’s example links asset classes and geographies.
