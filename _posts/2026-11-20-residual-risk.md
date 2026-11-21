---
layout: post
title: "Factor Risk Models, Part 2: Residual Risk After Sectors and Styles"
description: "I froze groups of stocks and principal directions learned from a year of residual returns, then followed them through the next year and into a long/short portfolio."
date: 2026-11-20
last_modified_at: 2026-11-21
categories: ["Portfolio construction"]
article_label: Factor risk · Part 2 of 2
series_id: factor-risk
series_order: 2
toc: false
permalink: /quants/residual-risk.html
---

The factor model in Part 1 explains shared risk through the market, sectors and styles. Its simplest version gives each stock its own residual variance and sets the residual correlations to zero. That works as a starting point, but a broad sector factor can miss a move shared by a smaller group.

That matters when one stock is supposed to hedge another. I return to the same three-stock spread to show how residual correlation changes the hedge, then check how much of that co-movement survives into the following year.

## The sign of the position changes the answer

Write the residual covariance as $$\Omega=DRD$$, where $$D$$ is the diagonal matrix of specific volatilities and $$R$$ is the residual correlation matrix. Changing $$R$$ lets me vary how stocks move together while keeping each stock’s specific risk fixed.

The spread is 50% long A and 50% short B, with daily variance of 3 squared percentage points when residual correlations are zero. Keep the specific volatilities at 2%, 2% and 1%, so $$D=\operatorname{diag}(2,2,1)$$ in percentage points. Give A and B a residual correlation of 0.6 in $$R$$. Right multiplication by $$D$$ scales the columns, and left multiplication scales the rows.

{% assign example = site.data.factor_risk_example %}
<div class="matrix-calculation" role="group" aria-label="Scale the columns of the residual correlation matrix by specific volatilities, then scale its rows">
  <div>
    {% include worked-matrix.html matrix=example.residual_correlations symbol="R" label="Residual correlation" mark_row="A" mark_column="B" %}
    <span class="matrix-operator" aria-hidden="true">→</span>
    {% include worked-matrix.html matrix=example.scaled_correlations symbol="RD" label="Columns scaled" mark_row="A" mark_column="B" %}
  </div>
  <div>
    <span class="matrix-operator" aria-hidden="true">→</span>
    {% include worked-matrix.html matrix=example.residual_covariance symbol="DRD" label="Residual covariance" mark_row="A" mark_column="B" %}
  </div>
</div>

The A–B entry becomes $$2(0.6)2=2.4$$ in squared percentage points. Add it to the factor covariance of 3 and the total A–B covariance rises to 5.4. The individual variances stay at 9 each. The same 50%-long A and 50%-short B spread now has daily variance

$$
w^\top\Sigma w=\frac{9+9-2(5.4)}{4}=1.8.
$$

Positive residual covariance lowers the spread’s estimated variance because the two positions have opposite signs. The same covariance adds variance when both positions are long. The practical question is whether the stocks will still move together when I hold the spread.

## Groups identified in one year still move together in the next

I use residuals from a daily fit with a market intercept, broad sectors and seven style factors. At each year-end I group stocks by their trailing 252-session residual correlations. Holding those groups fixed for the following year lets me measure whether yesterday’s neighbours still move together. The comparison uses stocks observed in both windows, about 93% of the initial names on average.

The first two heatmaps compare stock returns and residual returns on the same dates and in the same stock order. The third keeps that order for the next 252 sessions. A block in the same place in the last two panels means the group still moves together.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/matrix" mobile="/assets/residual-risk/matrix_mobile" version="3" alt="Raw returns, formation residuals, and the following year's residuals for the same 850 stocks. Average correlation falls from about 25% to near zero after removing factors. Positive residual blocks weaken but remain visible in the following year." %}
  <p class="figure-caption">The same 850 stocks appear in all three panels. Each tile averages correlations between distinct stock pairs, and the outlines mark the groups formed in December 2021. Zero has the same neutral color in each panel. The shared scale stops at ±40%. This cohort had the strongest forward gap.</p>
</div>

Removing the factors brought the average correlation from **about 25% to near zero**. Pairs in the same group were still about **8.5 correlation points** more correlated than pairs in different groups. The gap shrank to **about 5 points** over the next 252 sessions with the groups held fixed.

Across all 27 cohorts, within-group correlation was about **5 points** higher than between-group correlation in formation and about **2 points** higher the next year. I shuffle group labels within industries to see how much the grouping adds beyond industry composition. That shuffle produced a forward gap of less than half a point on average. The original groups beat the 95th percentile of those industry shuffles in all 27 cohorts.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/residuals" mobile="/assets/factor-risk-sizing/residuals_mobile" version="1" alt="Average stock correlation varies over time while average residual correlation stays near zero. Pairs in the same group were more correlated the following year than the sector-shuffle threshold in all 27 cohorts." %}
  <p class="figure-caption">The upper panel tracks the rolling 252-session average stock-pair correlation before and after fitting the factors. Each dot below is one year-end cohort’s following-year difference between within-group and between-group correlation. The short mark for that cohort is the 95th percentile from shuffling labels within sectors. The industry shuffle in the text is a separate check.</p>
</div>

Most of the persistence was within sectors. In the 23 development cohorts the forward gap was **about 8 points** for same-sector pairs and **less than 1 point** for cross-sector pairs matched on industry mix. The cross-sector gap was positive in all 23 cohorts.

## The model placed NVIDIA and Vertiv in different groups
{: #would-the-model-have-grouped-nvidia-and-vertiv}

To see what a group label can miss, I compared NVIDIA with Vertiv, a data-center power and cooling supplier, and with Workday, an enterprise software company.

In the 252 sessions through January 24, 2025, NVIDIA’s residual correlation was **0.14 with Vertiv** and **−0.10 with Workday**. The December groups put all three firms in different clusters. On January 27, NVIDIA and Vertiv fell and Workday rose. I picked the date after seeing the selloff.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/company-pairs" mobile="/assets/residual-risk/company-pairs_mobile" version="1" alt="NVIDIA’s correlations with Vertiv and Workday at five year-ends. Workday had the higher raw correlation in 2021 and 2022. Vertiv had the higher residual correlation at all five year-ends." %}
</div>
<p class="figure-caption">Each dot uses the last 252 sessions at that year-end. Workday had the higher raw correlation with NVIDIA in 2021 and 2022. Removing the broad factors reversed the ordering. The 2025 window includes the selloff.</p>

That one day lifted the year-end 2025 estimate for NVIDIA and Vertiv. Removing it brought the estimate close to its pre-selloff level.

## The shared directions persist at a smaller scale

A cluster gives each stock one label. Principal components let a stock contribute to several shared moves. I center the residuals and scale each stock to unit variance, using the number of days $$T$$ as the divisor. For A’s residual returns $$3,-1,3,-1$$, I subtract the mean of 1 and divide by the standard deviation of 2 to get the A column below.

<div class="matrix-calculation" role="group" aria-label="Standardized daily stock residuals and the resulting correlation matrix">
  <div>
    {% include worked-matrix.html matrix=example.standardized_residuals symbol="Z" label="Standardized residuals" mark_column="A" %}
  </div>
  <div>
    <span class="matrix-operator" aria-hidden="true">→</span>
    {% include worked-matrix.html matrix=example.residual_correlations symbol="S" label="Residual correlation" mark_row="A" mark_column="B" %}
  </div>
</div>

The correlation matrix $$S=Z^\top Z/T$$ averages the products of each pair of columns. Transposing $$Z$$ makes A’s column a row for the dot product with B’s column. The four products are $$1.4,-0.2,-0.2,1.4$$, giving $$2.4/4=0.6$$.

For a vector of weights $$q$$, $$Zq$$ is the combined daily return series and $$q^\top S q$$ is its variance. The first principal component finds the highest-variance combination with squared weights summing to one. In this example it is $$q=(1,1,0)^\top/\sqrt{2}$$. Multiplying $$S$$ by $$q$$ gives $$Sq=1.6q$$. The same-sign A–B combination has variance 1.6, C alone has variance 1, and the opposing A–B combination has variance 0.4.

In a typical weekly fit on the real residual data, the first component explained about 3% of standardized residual variance. Its importance to a portfolio depends on how closely the holdings line up with it.

For the chart, I fit the directions on 252 sessions and measure their variance over the following 252, using stocks observed in both windows. Each window is standardized with its own stock volatilities so the comparison tracks changes in co-movement. The portfolio replay estimates the scales and directions from the trailing history available at each decision.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/directions" mobile="/assets/residual-risk/directions_mobile" version="2" alt="PCA directions lose variance after formation but retain more than shuffled directions with the same industry composition. Development PCs two through five fall from 14.30 to 4.36 versus 1.64 for the shuffle." %}
  <p class="figure-caption">Within each band, first look at how far variance falls from formation to the following year. Then compare that forward variance with the industry shuffle, which redistributes stock weights within industries. A value of one is the variance of a unit-length direction if residuals are uncorrelated. The axis doubles at each tick and each cohort receives equal weight.</p>
</div>

In development, components two through five fell from **about 14** units of variance per direction to **about 4** the following year. That was still above the industry shuffle, which came in below **2**. The four later cohorts showed the same pattern.

## Putting a residual correlation into the portfolio

To see how much of that structure helps forecast risk, I vary the residual correlation matrix $$R$$ and hold the named factors and specific volatilities fixed. Specific volatilities use a 63-session exponential half-life. Residual correlations use the trailing 252 sessions.

The baseline uses $$R=I$$. A stock without a complete trailing residual window keeps its named exposures and specific variance. Assigning it zero residual correlations keeps it eligible without estimating co-movement from an incomplete window.

For a principal direction $$q$$ with variance $$\lambda$$, its contribution is the matrix $$\lambda qq^\top$$. Let $$L$$ be the sum over the directions I keep. In the formulas below, $$\operatorname{diag}(U)$$ means a matrix with only the diagonal entries of $$U$$.

- **Shrink toward zero.** For the trailing residual correlation matrix $$S$$, use $$R=(1-\alpha)S+\alpha I$$, with the weight estimated by Ledoit–Wolf shrinkage. This pulls pairwise residual correlations toward zero while preserving each stock’s specific variance.
- **Keep one principal component.** Keep its contribution $$L$$ to residual correlation and return the remaining variance to each stock’s diagonal, giving $$R=L+\operatorname{diag}(S-L)$$.
- **Combine them.** Keep one or five components in $$L$$, shrink the leftover matrix $$U=S-L$$ toward its diagonal and add $$L$$ back once. This gives $$R=L+(1-\delta)U+\delta\operatorname{diag}(U)$$ and keeps the diagonal at one.

In the example, shrinking halfway toward zero takes the A–B correlation from 0.6 to 0.3. The first component alone contributes $$1.6(1/\sqrt{2})(1/\sqrt{2})=0.8$$ to that entry. The opposing A–B component contributes $$-0.2$$. Keeping the first component at full strength and putting the remaining variance back on the diagonal therefore raises that pair’s correlation to 0.8. This is why I check how much of the fitted components’ variance survives.

Every year I compared each forecast with the same pairs’ correlations over the next 252 sessions. I use root mean squared error so large misses count for more, and the result stays in correlation points. Each cohort gets equal weight. For pairs in the **same sector and group**, carrying the trailing correlation forward reduced development error from **about 17 to 12 correlation points** against a forecast of zero. For pairs in **different sectors and groups**, predicting zero or using ordinary shrinkage gave errors of around **8 points**, and keeping five components pushed the error higher. An individual cross-sector hedge can be sensitive to a miss of that size.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/pair-errors" mobile="/assets/residual-risk/pair-errors_mobile" version="1" alt="Changes in next-year pair correlation error versus forecasting zero. All estimators improved on zero for stocks in the same sector and cluster. The cross-sector, different-cluster forecasts increased error in both periods." %}
  <p class="figure-caption">Each row is a different set of stock pairs. The dots show how much each estimator changes the following year’s correlation error relative to a forecast of zero. Left of zero is better. A difference of −4 means four correlation points less error. Cohorts receive equal weight within each panel.</p>
</div>

Ordinary shrinkage still reduced overall forecast error compared with predicting zero after excluding pairs of securities issued by the same company.

## Keeping five components overstated their forward risk

In development the five-component estimate assigned **about 15** units of variance per direction to components two through five. The following year delivered **about 4**, close to the ordinary-shrinkage forecast. Ordinary shrinkage also had lower forecast loss for that band in all 27 cohorts.

Keeping a component can give it *more* forecast variance than its original eigenvalue. On the formation sample the remainder $$U$$ has zero variance along a retained direction. Shrinking its off-diagonal entries removes some of the offsets that kept that variance at zero. The component then receives its original variance plus part of the remainder’s diagonal.

On the filled books, dropping residual correlations moved the factor target’s later volatility forecasts by **less than a tenth of a percentage point** on either set of holdings. Each covariance enters portfolio variance multiplied by the two signed weights. Contributions can cancel across the long and short sides even when individual residual correlations are material.

## What changed in the long/short book

So far I’ve measured how much residual co-movement survives and how much it changes a risk forecast. In the replay, the optimizer can also change the holdings. I keep the Ridge scores, risk budget, constraints and trading penalty fixed and compare what the new positions delivered after fees.

<table class="research-table comparison-table compact-table">
  <caption>Annual after-fee performance. Each residual method uses the same named factors and specific volatilities. Stock shrinkage is the separate stock-level reference.</caption>
  <thead><tr><th>Risk estimate</th><th>Net return</th><th>Volatility</th><th>Sharpe</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="4">January 1999 – December 2021</th></tr>
    <tr><th scope="row">Diagonal residuals</th><td>7.95%</td><td>8.13%</td><td>0.98</td></tr>
    <tr><th scope="row">One residual PC</th><td>7.95%</td><td>8.04%</td><td>0.99</td></tr>
    <tr><th scope="row">Residual shrinkage</th><td>7.91%</td><td>7.90%</td><td>1.00</td></tr>
    <tr><th scope="row">One PC + shrinkage</th><td>7.94%</td><td>7.87%</td><td>1.01</td></tr>
    <tr><th scope="row">Five PCs + shrinkage</th><td>7.92%</td><td>7.84%</td><td>1.01</td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>10.77%</td><td>8.74%</td><td>1.21</td></tr>
    <tr class="period-heading"><th colspan="4">January 2022 – May 2026</th></tr>
    <tr><th scope="row">Diagonal residuals</th><td>2.72%</td><td>8.29%</td><td>0.37</td></tr>
    <tr><th scope="row">One residual PC</th><td>3.05%</td><td>8.25%</td><td>0.41</td></tr>
    <tr><th scope="row">Residual shrinkage</th><td>3.97%</td><td>8.04%</td><td>0.52</td></tr>
    <tr><th scope="row">One PC + shrinkage</th><td>3.81%</td><td>8.07%</td><td>0.50</td></tr>
    <tr><th scope="row">Five PCs + shrinkage</th><td>3.98%</td><td>8.00%</td><td>0.53</td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>7.42%</td><td>9.65%</td><td>0.79</td></tr>
  </tbody>
</table>

Ordinary residual shrinkage improved on diagonal residuals in the later sample. Annual return after fees went from **2.7% to 4.0%**, with a modest drop in volatility. In development it also lowered volatility, with a small decline in return. Adding five components barely moved later net Sharpe, and the paired interval allowed small gains or losses.

The groups tell me where to look for residual co-movement. The next-year tests tell me how much of it to carry into the forecast. The estimates weakened after formation, especially across sectors, and keeping five fitted directions at full strength overstated their forward risk. In a long/short book, the sign of each position determines which of those relationships actually matters for total risk.

Keeping only within-group residual covariances barely moved the risk forecasts on the filled books. The groups held together out of sample, and their effect on forecast portfolio risk depended on which positions the book held.
