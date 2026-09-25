---
layout: post
title: "Fundamental, Statistical and Hybrid Risk Models"
date: 2026-09-13
description: "A hybrid factor model makes smaller risk-forecast errors on its own portfolios, but that improvement does not carry through to portfolio performance."
permalink: /quants/hybrid-risk-model.html
toc: false
show_date: false
published: false
categories: ["Risk & attribution"]
---

After [comparing Ridge with tree models](/quants/xgboost-vector-leaves.html), I wanted to take a closer look at the risk model. It helps the optimizer decide how much to hold in each stock and which positions work well together.

I use a similar model to the one described in the [portfolio construction article](/quants/2026/08/29/portfolio-optimization.html#covariance-and-risk-forecasts), estimating stock volatility and correlation directly from returns. I wanted to see whether a factor model could improve on it. There are two questions here: does it forecast portfolio risk more accurately, and does the optimizer build better portfolios with it?

The results pull in different directions. The hybrid and blend make smaller forecast errors on their own portfolios and have smaller daily tail losses, but they also earn less and have deeper drawdowns. The Sharpe differences are uncertain. That leaves me with the question I want to work through here: when does a better risk forecast actually help the portfolio?

## What I compared

I kept the Ridge ranking, sizing scores, trading rules and portfolio constraints the same. Each version uses a 7% annual forecast-volatility cap and three rebalance schedules with equal capital. The comparison covers development history through 2021.[^setup]

The three covariance estimates are:

- **Direct covariance:** short-window stock volatilities combined with longer-window correlations, shrunk toward the identity matrix.
- **Hybrid:** named factors—beta, sectors and price-based styles—plus ten principal components of the residual returns.
- **50:50 blend:** an equal average of the direct and hybrid covariance estimates before either is rescaled.

The direct model uses its existing volatility multiplier of 1.18. I also tried adjusting that multiplier from past forecast errors, using the same rule as the hybrid and blend. This is the “Direct, recalibrated” row in the results. It lets me check whether the extra factors help beyond correcting the overall level of forecast risk.

For each of those three recalibrated versions, the covariance used by the optimizer is $s_t^2\Sigma_t^{\mathrm{raw}}$. The scale $s_t$ is estimated only from earlier forecasts whose full 21-session outcomes are already known. The blend has its own scale, applied after averaging the two raw covariance estimates.[^calibration]

<h2 id="how-the-blocks-fit-together">How the hybrid estimates risk</h2>

A **fundamental factor model** starts with named stock characteristics, such as beta, sector and size. Two stocks with similar exposures should respond similarly to a move in those factors. A **statistical factor model** looks for common movements directly in returns, typically through principal component analysis (PCA). The hybrid asks what shared movement remains after the named factors have been fitted. [HRT's introduction to factor models](https://www.hudsonrivertrading.com/hrtbeat/modeling-equities-returns/) gives a useful starting point for this decomposition.

Fix a forecast date and treat the stock exposures as known at that date. Suppressing the date subscripts for a moment, the model for the next daily return is

$$
r=Bf+Pg+\varepsilon.
$$

Here $r$ contains the returns of $N$ stocks. The $K$ named factor returns are $f$, with exposures $B$; the $J$ residual-factor returns are $g$, with loadings $P$. Thus $B$ is $N\times K$ and $P$ is $N\times J$. For stock $i$, the equation says that its return is the sum of its exposures times the corresponding factor moves, plus a remaining stock-specific return $\varepsilon_i$.[^model]

### Estimating the named factors

The named block has an intercept, eleven sector indicators and seven styles. Here, “fundamental” means that I specify the characteristics in advance. The styles use prices, market capitalization and trading volume; this version has no accounting-based value, profitability or leverage exposures.

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

These choices matter. Momentum includes the recent month, so it overlaps with short reversal. Size and dollar volume overlap too. Joint regression estimates each factor's contribution while controlling for the others, but correlated descriptors can make the individual coefficients less stable. A factor's inclusion says that its exposure may help describe shared risk; it does not assume a positive expected return for that factor.

The exposures and factor returns play different roles. I winsorize and standardize the style exposures across stocks, then use the **previous session's exposures** to explain each day's returns. The factor returns are the regression coefficients fitted across stocks on that day. For example, a size exposure of +1 means one weighted cross-sectional standard deviation above the mean; a fitted size return of 0.2% contributes 0.2% to that stock's fitted return, holding its other exposures fixed.[^descriptors]

Writing $u$ for a historical return date, the fit minimizes a weighted sum of squared errors, $\mathcal L_u$:

$$
\begin{aligned}
\widehat f_u&=\arg\min_{f\in\mathcal C_{u-1}}\mathcal L_u(f),\\[4pt]
\mathcal L_u(f)&=\sum_i\omega_{i,u-1}\left(r_{i,u}-b_{i,u-1}^{\top}f\right)^2,\\[4pt]
e_u&=r_u-B_{u-1}\widehat f_u.
\end{aligned}
$$

The vector $b_i$ contains stock $i$'s named exposures. The positive regression weights $\omega_i$ are proportional to square-root market capitalization, capped at their cross-sectional 95th percentile and normalized to sum to one. They determine each stock's influence on the fit; they are separate from the portfolio weights $w_i$ used later.

The constraint set $\mathcal C$ makes the intercept and sector returns identifiable. With one intercept and all sector indicators, the columns otherwise repeat the same common move. I constrain the sector returns to have a weighted mean of zero, using each sector's share of regression weight. The intercept then captures the common component and sector coefficients describe departures from it. The residual $e_u$ is what the named factors leave unexplained; it still contains shared risk that PCA may find.

The beta coefficient needs particular care. The **exposure** is a stock's historical regression beta; the **factor return** is today's cross-sectional payoff to standardized beta after controlling for the other characteristics. It is not the benchmark return itself. The intercept and beta column therefore serve different purposes. There are 19 named columns, with one sector-identification constraint; full identification also requires sufficient independent exposures in the day's estimation universe.

### Finding common movement in the residuals

Applying PCA to raw residuals can let the most volatile stocks dominate. I first divide each stock's centred residual history by its estimated residual volatility. I also apply the stock regression weights and exponential time weights. The following PCA equations apply to the stocks with complete estimation-window history. If $E_c$ is that history centred using the time weights, with dates in rows and stocks in columns, the matrix used for extraction is

$$
X=A^{1/2}E_c S^{-1}W^{1/2}.
$$

$S$ is diagonal, containing residual volatilities estimated with a 42-session half-life; $W=\operatorname{diag}(\omega_i)$ contains stock weights; and diagonal $A$ contains normalized time weights with a 90-session half-life. $S$ and $W$ act on stock columns; $A$ acts on date rows. The leading right singular vectors of $X$ identify directions that explain the most weighted, standardized residual variation. I retain ten directions. This is a fixed research choice, not a count selected from these portfolio results.

Those vectors live in transformed units. If $V_J$ contains the retained vectors, the initial loadings in stock-return coordinates are

$$
P_0=S W^{-1/2}V_J.
$$

I then remove the current named-factor exposure space from $P_0$ and normalize the remaining columns under $W$. The resulting $P$ satisfies $B^\top W P=0$ and $P^\top W P=I_J$ on the eligible stocks. This prevents the two loading blocks from representing the same cross-sectional direction. The projection can change the extracted eigenvectors, so the final residual factors need not have diagonal covariance.

For each forecast, I score the historical residuals in that forecast's loading basis. With the normalization above, the weighted least-squares scores and remaining residuals are

$$
g_u=P^\top W e_u,\qquad
\varepsilon_u=e_u-Pg_u.
$$

This is also a useful implementation check: adding the fitted residual-factor component back to $\varepsilon_u$ must recover $e_u$. The eigenvector extraction is refreshed every 21 sessions; projection and score estimation use the current exposures and eligible universe. The basis is aligned to its previous estimate by an orthogonal rotation where overlap permits. Stocks without complete PCA-window history stay outside that extraction and receive extra specific-risk protection.[^estimation]

There is an estimation choice hidden in those steps. Extraction minimizes reconstruction error in standardized units, weighting stock $i$ by $\omega_i/S_{ii}^2$. The later projection and score fit use $\omega_i$ instead. Also, each historical $e_u$ was fitted against that date's $B_{u-1}$, while the final projection uses today's $B$. Consequently, “extract ten PCs, then project” generally differs from finding the best ten directions subject to the named-factor constraint. It is a valid way to construct loadings, but I would not describe it as an optimal joint fit. I return to a more consistent alternative after the results.

### From factors to stock covariance

I put the two sets of exposures together as $L=[\,B\;P\,]$, an $N\times(K+J)$ matrix. The model's **joint factor covariance** is

$$
F_H=
\begin{pmatrix}
F_{ff} & F_{fg}\\
F_{fg}^{\top} & F_{gg}
\end{pmatrix}.
$$

The subscript $H$ means hybrid. All covariances in this construction are conditional on the information at the forecast date and refer to daily returns. The diagonal blocks $F_{ff}=\operatorname{Cov}(f)$ and $F_{gg}=\operatorname{Cov}(g)$ describe covariance within each factor group. The cross block $F_{fg}=\operatorname{Cov}(f,g)$ is $K\times J$: it describes how the named and residual-factor returns move together. The lower block is its transpose, so the whole matrix is symmetric.

Mapping that factor covariance back to stocks gives shared covariance $C=L F_H L^\top$. Adding the remaining stock-specific variances gives

$$
\Sigma_H=\underbrace{L F_H L^\top}_{\text{shared stock covariance}}+D.
$$

The diagonal matrix $D$ contains $d_i=\operatorname{Var}(\varepsilon_i)$ for each stock. It measures what remains after **both** factor groups. The equation assumes $\operatorname{Cov}((f^\top,g^\top)^\top,\varepsilon)=0$ and uncorrelated remaining shocks across stocks. These are modelling assumptions; regression fit alone does not establish them for future returns. If they fail, the omitted covariance terms can matter. Both $C$ and $D$, and therefore $\Sigma_H$, are $N\times N$ matrices.

<div class="research-figure responsive-figure" markdown="0">
{% include theme-svg-figure.html base="/assets/hybrid-risk-model/matrix-multiplication" mobile="/assets/hybrid-risk-model/matrix-multiplication_mobile" version="3" alt="Joint factor covariance F H contains named-factor, residual-PC and cross-covariance blocks. Applying the stock exposures L equals B P on both sides gives shared stock covariance C. Adding diagonal specific covariance D changes only the diagonal to produce total covariance Sigma H. Matrix blocks and diagonal tiles are schematic." %}
</div>
<p class="figure-caption"><strong>Figure 1: From factor covariance to stock covariance.</strong> The first arrow applies the stock exposures: $C=L F_H L^\top$. The second adds $D$ to the diagonal. Green blocks retain covariance between the two factor groups. Colours and diagonal tiles show structure, not measured values.</p>

Expanding the multiplication in Figure 1 makes the four shared-risk terms visible:[^blocks]

$$
\begin{aligned}
C={}&B F_{ff}B^\top+P F_{gg}P^\top\\
   &+B F_{fg}P^\top+P F_{fg}^\top B^\top.
\end{aligned}
$$

The first line gives risk within each factor group. The second lets the two groups reinforce or offset each other. Dropping it would assume their returns are uncorrelated. The loading condition $B^\top W P=0$ concerns a weighted sum **across stocks**; $F_{fg}$ concerns co-movement **over time**. One does not force the other to zero. The named exposures also change through the historical fit, while residual scores are reconstructed in the current basis. I therefore estimate the full joint covariance.

For a particular pair of stocks, shared covariance is $C_{ij}=\ell_i^\top F_H\ell_j$, where $\ell_i$ is stock $i$'s exposure vector across both groups. Specific risk adds $d_i$ only when $i=j$. This is the intuition behind the matrix: shared exposures create co-movement; the diagonal allows each stock to retain risk of its own.

### Estimating risk levels and dependence

The equations above describe the model. Its inputs still have to be estimated. For the hybrid, I estimate factor volatilities with a 42-session half-life and factor correlations with a 360-session half-life, using up to 756 past sessions. A half-life of $h$ assigns an observation $h$ sessions older half as much weight: weights at age $a$ are proportional to $2^{-a/h}$. This lets the size of factor moves respond faster than the estimated pattern of co-movement.

Let $S_f$ contain the fast factor-volatility estimates and $\widehat R_f$ the slow correlation estimate of the **joint** factor history. The daily estimate is

$$
\widehat F_H=S_f\widehat R_f S_f.
$$

The hybrid uses no additional shrinkage of these factor correlations. The direct model, by contrast, shrinks stock correlations halfway toward the identity matrix. In either case, a positive semidefinite correlation matrix and nonnegative scales give a positive semidefinite covariance. Adding strictly positive specific variances makes the hybrid stock covariance positive definite, even when the factor covariance is singular. It follows that every nonzero portfolio has positive model variance; this is a mathematical validity check, not evidence of forecast accuracy.

I estimate specific variances from the post-PCA residuals with a 42-session half-life, then shrink them toward a cross-sectional estimate based on size, volatility and sector. Short histories receive more shrinkage. This reduces the chance that an accidentally quiet residual history makes a stock look almost riskless.[^estimation]

The coverage adjustments preserve this factor-plus-diagonal form.[^estimation] For portfolio weights $w$, first collect the portfolio's factor exposures as $x=L^\top w$, using the adjusted loadings where required. Its raw daily forecast variance is then

$$
v^{\mathrm{raw}}=x^\top\widehat F_H x+\sum_i w_i^2\widehat d_i.
$$

The first term depends on the portfolio's **net factor exposures**. Long and short positions can offset there. The specific term adds squared position sizes, so opposite signs do not cancel stock-specific risk under the diagonal assumption. This calculation gives exactly the same result as $w^\top\widehat\Sigma_H w$, while avoiding the full stock-by-stock matrix.

Finally, the chronological multiplier adjusts the level: $\widehat v=s_t^2 v^{\mathrm{raw}}$. It scales every variance and covariance by the same amount, leaving correlations unchanged. It can correct overall underprediction, but cannot repair a wrong relative-risk estimate between two portfolios. The blend averages the two raw matrices first; its own multiplier then scales that average.

Annual forecast volatility is reported as $\sqrt{252\widehat v}$ and constrained by the 7% cap. This is an annualization convention for daily risk. With serially correlated returns, the variance of a multi-session sum also includes lag covariances; it is generally not just the number of sessions times daily variance. The comparisons below use the daily matrix and a subsequent daily-variance estimate.[^horizon]

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

## Would I build the hybrid this way again?

I would keep the idea of named factors plus residual structure as a candidate. Named exposures give the model an interpretable starting point, while residual factors can pick up common movements those exposures miss. *Elements* discusses this complementarity. Its treatment of weighted, two-stage PCA also makes clear that scaling, noise estimation and factor selection are part of the estimator, rather than incidental preparation.[^weighted-pca]

The current results compare complete risk-model choices. They do not isolate the contribution of residual PCA: there is no named-factors-only portfolio in these tables, and the direct and hybrid models use different correlation shrinkage. Before adding more complexity, I would add that missing baseline with the same specific-risk and calibration rules. Otherwise, we cannot tell whether the named block helped and PCA hurt, the reverse happened, or their interaction mattered.

### Use one fitting objective

For a cleaner residual-PCA comparison, I would make the weighting and exclusion constraint consistent from extraction through scoring. Let $M$ be a chosen positive diagonal stock-weight matrix. On the eligible stocks, consider

$$
\begin{gathered}
\min_{G,P}\;\left\|A^{1/2}(E_c-GP^\top)M^{1/2}\right\|_F^2,\\
\text{subject to }P^\top MP=I_J,\\
B^\top MP=0.
\end{gathered}
$$

Here $G$ contains historical scores, and the squared Frobenius norm sums the squared entries of the weighted reconstruction error. The first constraint fixes factor units; the second reserves the current named-factor space for $B$. A direct solution projects the **data before extracting the retained directions**:

$$
\begin{aligned}
Z&=M^{1/2}B,\qquad \Pi_Z=ZZ^\dagger,\\
Y&=A^{1/2}E_cM^{1/2}(I-\Pi_Z),\\
P&=M^{-1/2}V_J(Y).
\end{aligned}
$$

$Z^\dagger$ is the Moore–Penrose pseudoinverse, which handles the redundant intercept/sector representation; $V_J(Y)$ contains the leading right singular vectors in the orthogonal complement of $Z$. There must be at least $J$ usable directions. The scores are $G=E_cMP$. This solves the stated constrained reconstruction problem, so extraction and scoring now have the same objective. It is an alternative specification, not the procedure behind the reported results.

Choosing $M$ remains a statistical decision. Square-root-cap weights emphasize larger stocks. Inverse specific-variance weights emphasize observations thought to contain less unexplained noise; their efficiency argument requires the residual covariance assumptions to be appropriate. The two-stage approach in *Elements* first estimates residual scale, then refits PCA after reweighting. Applying that idea to the named-factor residuals would provide a useful challenger. I would regularize the scale estimates so an accidentally quiet stock cannot receive enormous influence. A consistent objective makes the construction easier to defend, but cannot establish better future risk forecasts by itself.[^weighted-pca]

### Check whether the answer depends on factor coordinates

For an exact covariance calculation, rotating the residual basis changes its coordinates while preserving stock risk. If $O^\top O=I$, then $P_{\star}=PO$ and $g_{\star}=O^\top g$ describe the same fitted returns. Their covariance transforms as $F_{gg,\star}=O^\top F_{gg}O$, giving

$$
P_{\star}F_{gg,\star}P_{\star}^\top=PF_{gg}P^\top.
$$

The named–residual cross block must transform too: $F_{fg,\star}=F_{fg}O$. With that change, the full shared covariance is unchanged.

Our estimator adds a complication: it combines fast estimates of each factor's variance with slow correlations. Taking the diagonal is coordinate-dependent. For example, suppose the slow covariance is $I_2$ and the fast covariance is $\operatorname{diag}(4,1)$, in arbitrary variance units. The split estimator gives $\operatorname{diag}(4,1)$. Rotate both inputs by 45 degrees: the slow matrix stays $I_2$, while both fast diagonal entries become 2.5. Reapplying the split estimator and rotating back gives $2.5I_2$. The underlying factor space has not changed, yet the estimated risk has.

That is a mathematical property of this estimation rule, not evidence that basis rotation caused the backtest's return gap. It does mean the alignment rule belongs in the model specification. A useful control would estimate the full joint factor covariance with one common time-weighting rule; orthogonal changes of the residual coordinates would then leave stock covariance unchanged. Comparing that control with the current fast/slow rule would test whether the extra responsiveness is worth the coordinate dependence.

### Ask whether the remaining structure is broad or local

Ten residual components may include noise, and a large sample eigenvalue does not guarantee a reliable factor direction. Kolm and Ritter's recent residual-PCA working paper distinguishes detecting an unusual eigenvalue from recovering a useful hidden-factor loading. Its finite-sample calibration is a relevant direction for selecting components, although our exponential weights and changing universe would need to be reflected in the calibration.[^hidden-factors]

There is another possibility: some remaining dependence may concern a few related stocks rather than a broad factor. Adding PCs is then only one way to model it. The POET literature studies low-rank shared risk plus a sparse residual covariance, relaxing the assumption that every off-diagonal residual covariance is zero. That suggests a separate challenger to our diagonal $D$, with thresholding and positive-definiteness checks. Its assumptions and tuning would need testing here; it is not an automatic upgrade.[^poet]

For the next comparison, I would prioritize the named-only baseline and the consistent residual-PCA fit. They address what the extra block contributes and how it is estimated. Factor-count calibration, a common-weight covariance control and sparse residuals address distinct questions that should follow from those diagnostics.

## How I would evaluate those changes

I would keep the full portfolio comparison and add two focused tests. They answer different questions about the same risk model.

First, I would evaluate every model on the same dated portfolios, including holdings selected by each model. Each candidate would forecast risk for every portfolio, so choosing one model's holdings would not determine the whole comparison. Alongside QLIKE and the calibration ratios, I would add **mean squared error of variance**:

$$
\mathrm{MSE}=\frac{1}{T}\sum_{t=1}^{T}
\left(v_t^{\mathrm{real}}-\widehat v_t\right)^2.
$$

MSE measures the absolute size of variance errors. Large errors in high-volatility periods carry more weight than they do under QLIKE. That makes the two losses useful companions. For common holdings, QLIKE and variance MSE also have a useful theoretical property: under the required conditional-unbiasedness assumptions, using a noisy variance proxy preserves their expected forecast ranking. That result does not guarantee a reliable ranking in this finite sample, or establish that our 21-session proxy satisfies those assumptions.[^losses]

I would report paired loss differences by calendar period and forecast-risk level, with confidence intervals that resample blocks of common dates. All models and schedules would stay together within each sampled block, preserving their shared shocks. This would show whether an improvement is broad or concentrated in a few episodes, while accounting for overlapping outcomes.

Second, I would construct **minimum-variance portfolios** under identical investment constraints, with no alpha forecast in the objective. A simple version fixes total investment to one, requires long-only weights and applies the same name cap to every model. Each covariance estimate then chooses the portfolio it considers least risky. Comparing subsequent realized variance, concentration and turnover would test the diversification choices more directly. Fixing investment prevents the zero portfolio from winning; this test addresses a different use case from the long–short Ridge strategy.[^evaluation]

For an estimation extension, I would separate uncertainty in the cross block from uncertainty in the risk level. One way is to blend the joint factor estimate with its block-diagonal version:

$$
\begin{aligned}
\widehat F_H(\eta)&=(1-\eta)\widehat F_H+\eta F_0,\\
F_0&=\operatorname{blockdiag}(\widehat F_{ff},\widehat F_{gg}),\\
&\quad 0\leq\eta\leq1.
\end{aligned}
$$

This keeps the within-group blocks and attenuates only the cross-covariances. Both endpoint matrices are positive semidefinite, so every blend is too. The statistical question is whether reducing estimation noise helps more than the discarded dependence hurts. I would assess a small, predeclared set of shrinkage strengths with the same calibration rule and portfolio controls. The tabled hybrid keeps the full cross block; these equations describe an extension, not a revised result.

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

[^descriptors]: Styles are winsorized at the cross-sectional 1st and 99th percentiles, then centred and scaled with the regression weights. Invalid numeric descriptors receive the same-date cross-sectional median before fitting. Momentum sums $p_t/p_{t-h}-1$ over $h\in\lbrace20,60,125,252\rbrace$; the inherited feature sums available horizons if some are missing, and its lags count stock observations. This is a coverage limitation to check for young or interrupted histories. The long-reversal return uses sessions $t-755$ through $t-252$. Sector gaps use a prior observed label where available, otherwise the current cross-sectional mode; sector vintage remains a limitation of the study.

[^weighted-pca]: Paleologo, *The Elements of Quantitative Investing*, draft of 9 September 2024, chapter 8 introduction (physical PDF page 255) and §8.5.1, “Weighted and Two-Stage PCA,” pp. 267–271 (physical PDF pages 293–297), especially Procedure 8.1. This is the draft's general statistical-model estimation framework; the constrained residual fit above is an alternative derived for this article, not a claim that the book prescribes our hybrid implementation.

[^hidden-factors]: Petter N. Kolm and Gordon Ritter, [“Hidden Factors in Portfolio Risk Models: A Finite-Sample Approach to Residual PCA”](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6913458), working paper dated 10 June 2026, posted 3 July 2026. The public abstract describes separate eigenvalue-detection and eigenvector-alignment calibration questions; I have not evaluated that procedure on this study.

[^poet]: Jianqing Fan, Yuan Liao and Martina Mincheva, [“Large covariance estimation by thresholding principal orthogonal complements”](https://pmc.ncbi.nlm.nih.gov/articles/PMC3859166/), *Journal of the Royal Statistical Society: Series B* 75 (2013), §§2.1–2.2. Their approximate-factor model allows a sparse residual covariance; transferring its estimator to a dynamic hybrid requires additional design and validation.

[^estimation]: PCA requires at least 252 sessions; its equations describe the complete-history eligible universe. Specific-risk shrinkage toward the structural variance estimate has weight $0.3+0.7\times60/(60+n_i)$, where $n_i$ counts observed residual sessions; fewer than 60 observations receive the full structural estimate. Daily variance floors and caps precede a 1.5 variance buffer for PCA-excluded stocks, whose specific variance is also bounded below by the buffered pre-PCA estimate. Prior observed exposures may be carried for at most 21 sessions. The separate stale-exposure buffer applies $Q\Sigma Q$, with diagonal $Q_{ii}=\sqrt{1.5}$ for stale names and one otherwise. This is equivalent to replacing $L$ by $QL$ and $D$ by $QDQ$, preserving the factor form. Missing residual observations retain their dates and receive zero estimation weight.

[^horizon]: For a covariance-stationary vector return process with lag covariance $\Gamma_\ell=\operatorname{Cov}(r_u,r_{u-\ell})$, the covariance of an $H$-session arithmetic sum is $H\Gamma_0+\sum_{\ell=1}^{H-1}(H-\ell)(\Gamma_\ell+\Gamma_\ell^\top)$. The implementation also constructs a separate 21-session estimate with a two-lag Bartlett adjustment. That horizon matrix is not the daily covariance used by this allocation and forecast-score comparison; compounded returns and changing holdings require further care.
