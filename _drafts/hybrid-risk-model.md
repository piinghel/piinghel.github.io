---
layout: post
title: "Fundamental, Statistical and Hybrid Risk Models"
description: "Combining named factors with residual PCA improves some risk forecasts in my tests, but has not improved the portfolios. I separate forecast accuracy from allocation quality."
permalink: /quants/hybrid-risk-model.html
toc: false
show_date: false
categories: ["Portfolio risk"]
---

My current risk model estimates stock volatility and correlation directly from returns. I wanted to see whether adding some economic structure would help: start with named factors, then let statistical factors capture common movement left in the residuals. The attraction is straightforward—give the model both a specified structure and a way to learn what that structure misses.

I’m evaluating the covariance model here, with return forecasts and portfolio rules held fixed within each comparison. The tests gave me two different answers: some risk forecasts improved, but the portfolios did not establish an improvement. The distinction in *Elements* between evaluating covariance forecasts and evaluating their use in optimization is a useful way to understand that result.[^evaluation]

## From factors to stock risk

A factor model writes stock returns as $r=Bf+\varepsilon$. Each row of $B$ belongs to a stock; each column belongs to a factor. Multiplying that row by the factor-return vector $f$ gives the stock’s modeled return. The residual $\varepsilon$ is what remains.[^model]

For risk, the corresponding calculation is

$$\Sigma=BFB^\top+D.$$

Here $F$ is the covariance matrix of factor returns and $D$ contains stock-specific variances on its diagonal. This form assumes the remaining stock-specific shocks are mutually uncorrelated and uncorrelated with the factors. With $N$ stocks and $K$ factors, the dimensions are $(N\times K)(K\times K)(K\times N)$, producing an $N\times N$ stock covariance matrix.

For portfolio weights $w$, forecast volatility is $\sqrt{w^\top\Sigma w}$. The factor exposures of the portfolio are $B^\top w$.

## Where the factors come from

**Fundamental.** I specify the columns of $B$: market beta, sectors and styles such as size, momentum or volatility. Cross-sectional regressions estimate their daily factor returns; those histories estimate $F$. Here “fundamental” means a model built from specified characteristics. The available tests use price-based descriptors; accounting variables are a later extension.

**Statistical.** A PCA factor model estimates its loadings from return co-movement. In a simple covariance-PCA construction, the leading eigenvectors form $P$, their eigenvalues form $\Lambda$, and $\Sigma\approx P\Lambda P^\top+D$. The retained components explain broad common variation, though their economic meaning may be less stable. Purely return-based estimation can also keep the full stock matrix. My current model takes that route: short-window stock volatilities surround a longer-window correlation estimate shrunk toward the identity. It uses no named factor exposures and no PCA reduction.

**Hybrid.** I first fit named factors, then extract statistical components from standardized residual returns. Let $P$ now denote these residual loadings, restored to stock-return units. With $K$ named factors and $J$ residual factors, the combined exposure matrix is $L=[B\;P]$. Figure 1 shows how the two blocks enter the same covariance calculation.[^blocks]

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/hybrid-risk-model/matrix-multiplication" mobile="/assets/hybrid-risk-model/matrix-multiplication_mobile" version="2" alt="Symbolic hybrid covariance: loadings L combine named block B and residual statistical block P. The factor covariance has BB, BP, PB and PP blocks. Multiplication by L and its transpose gives common stock covariance C; adding diagonal specific variance D gives total covariance Sigma H." %}
</div>
<p class="figure-caption"><strong>Figure 1: The hybrid as a block-matrix product.</strong> Blue marks named-factor blocks, ochre statistical blocks, and green their cross-covariances. Multiplication maps the factor covariance into the stock space; diagonal specific risk completes the model. Dimensions are symbolic and block sizes schematic.</p>

I retain the off-diagonal blocks. Expanding the product gives named-factor risk $BF_{BB}B^\top$, statistical risk $PF_{PP}P^\top$, and the two cross terms $BF_{BP}P^\top+PF_{PB}B^\top$. Orthogonal loadings do not guarantee uncorrelated factor returns. The hybrid estimates their joint covariance, including the cross blocks, without correlation shrinkage.

In a later diagnostic, the PCs’ strongest links to the named factors were generally sector links, with weaker full-period correlations to the beta factor. That is a clue about what the statistical block adds; the components rotate over time, so a single full-period correlation gives an incomplete description.

A **50:50 covariance blend** combines completed covariance estimates instead: $\Sigma_{\mathrm{blend}}=0.5\Sigma_{\mathrm{current}}+0.5\Sigma_H$, before its own calibration. This averages variance estimates for any fixed portfolio; taking the square root means it does not average volatility directly. It also differs from splitting capital equally between two optimized portfolios.

## What the completed tests show

The earlier fundamental-only test used size, momentum and volatility, plus a common intercept. Over September 1998–December 2021 it earned 13.67% a year at 9.83% volatility, against 11.97% at 7.72% for the current model. Adding two residual PCs reduced volatility to 9.04% and return to 12.97%; neither improved the observed Sharpe. This was a narrow factor specification, and the return and Sharpe differences were statistically inconclusive.

The expanded comparison adds beta, sectors, reversals and liquidity, with ten residual PCs. It compares the current model, an adaptively recalibrated version of it, the hybrid, and their 50:50 covariance blend. The last three use the same calibration procedure, learning a multiplier from previously completed outcomes of their own target portfolios. The recalibrated current model is the relevant control for that procedure; the original current model anchors the operational comparison.

These studies have different specifications and sample periods. **A matched fundamental-only, standalone PCA and hybrid comparison is still missing.** The earlier “PCA” arm adds PCs to named factors. The expanded variant with dense residual covariance stopped at its history-coverage guard and supplies no completed financial result.

## Does it forecast risk better?

Following *Elements*, I look beyond average bias. For each fixed target portfolio, let $q_t$ be realized variance over the next 21 sessions divided by the forecast variance:

$$\begin{gathered}
q_t=\frac{\widetilde{\sigma}_{t,21}^{\,2}}{\widehat{\sigma}_t^{\,2}},\\[6pt]
\mathrm{QLIKE}=\frac{1}{T}\sum_t\bigl(q_t-\log q_t-1\bigr).
\end{gathered}$$

Lower QLIKE is better; zero means agreement in every window. Here realized variance is the sample variance of the frozen portfolio’s following daily returns. I also check underprediction tails, since offsetting misses can leave the average looking reasonable.

Figure 2 compares realized volatility with the forecast over the following 21 sessions, holding each decision’s target portfolio fixed. One means agreement; values above one indicate underprediction. There are 1,195 overlapping windows per model, with outcomes through 2021.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/hybrid-risk-model/calibration" mobile="/assets/hybrid-risk-model/calibration_mobile" version="3" alt="Boxplots of realized to forecast volatility for the current model, adaptive current model, hybrid and covariance blend. All retain long upper tails, including windows above four times forecast volatility." %}
</div>
<p class="figure-caption"><strong>Figure 2: Better average calibration still leaves large misses.</strong> Boxes contain the middle 50% of windows; the internal line is the median. Whiskers extend to observations within 1.5 interquartile ranges of the box, with all remaining observations plotted as dots. The logarithmic axis retains the full upper tail. Portfolios differ across models, so the comparison includes both estimation and allocation choices.</p>

Mean QLIKE is 0.327 for the current model, 0.290 for its recalibrated version, 0.279 for the hybrid and 0.238 for the blend. The frequency of volatility exceeding its forecast by more than 30% falls from 24% to 18%, 14% and 12%, respectively. Those are improvements on the portfolios each model selects. Since both their holdings and their calibration feedback differ, they do not establish which covariance estimate forecasts an identical portfolio best. The blend’s mean variance ratio remains 1.18, despite mean volatility being close to forecast.

## Does it build a better portfolio?

Optimization depends on the inverse covariance matrix, also called the precision matrix. In unconstrained mean–variance optimization, weights are proportional to $\Sigma^{-1}\alpha$, where $\alpha$ is the expected-return vector. That makes errors in estimated low-risk directions especially consequential. The practical test here feeds each covariance estimate through the same constrained optimizer and evaluates the resulting net returns.[^evaluation]

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

The hybrid and blend give up return as well as volatility, and their drawdowns deepen. Both also trail the recalibrated current model. The paired bootstrap intervals for their Sharpe differences include zero, so these tests establish no Sharpe improvement. The result is also weaker in 2017–2021: hybrid and blend Sharpe are 1.06 and 1.11, against about 1.43 for either current-model control. Lower QLIKE has not translated into a better allocation.

## What I would improve next

Adding a 52-week-high descriptor at ten PCs did not establish an improvement over its matched hybrid control. Increasing the PC count also gave no stable answer: gains in a small frozen-portfolio screen depended on the portfolio and individual dates. These results give me little reason to keep adding factors to the tested specification.

The next useful comparison is the missing three-way test, with a common universe, estimation dates and calibration rule. I would score each model on the same prespecified portfolios, then on portfolios it constructs itself. A minimum-variance portfolio test, as proposed in *Elements*, would help assess the precision matrix, with the same budget and trading constraints for every model. Portfolio return, volatility, turnover and costs would remain the economic check. These are proposed tests, rather than completed evidence.

For now, I’m keeping the current covariance model. The completed hybrids improved some forecast scores but have not earned a change in portfolio construction. All these results use previously inspected history, and there is no matched-volatility hybrid or blend replay here. Accounting-based factors remain a later extension.

[^model]: For characteristic-based estimation and the covariance identity, see Giuseppe A. Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6), first edition (2021), §4.3 and §11.1, pp. 40–41 and 168–169 (physical PDF pages 52–53 and 180–181).

[^blocks]: Giuseppe A. Paleologo, *The Elements of Quantitative Investing*, draft of 9 September 2024, §7.6.1, Figure 7.2, p. 211 (physical PDF page 237). The diagram here is an original application to named and residual statistical factors; the book’s example links asset classes and geographies.

[^evaluation]: Giuseppe A. Paleologo, *The Elements of Quantitative Investing*, “Evaluating Risk”: chapter 5 in the published edition; chapter 6 in the 9 September 2024 draft used here. See §§6.1–6.2, pp. 164–172 (physical PDF pages 190–198), for forecast losses, portfolio-dependent tests and precision-matrix evaluation; §6.3.1, pp. 173–174 (physical PDF pages 199–200), for model-induced turnover.
