---
layout: post
title: "Residual Risk After Sectors and Styles"
description: "I froze groups of stocks and principal directions learned from a year of residual returns, then followed them through the next year and into a long/short portfolio."
date: 2026-11-20
last_modified_at: 2026-11-20
categories: ["Portfolio construction"]
article_label: Portfolio construction · Residual risk
permalink: /quants/residual-risk.html
home_after: _posts/2026-11-20-factor-risk-sizing.md
---

Pairwise correlations average near zero after removing sectors and styles. For sizing, what matters is whether the particular stocks in the portfolio still move together. In a universe of hundreds of stocks, one year of returns gives an imprecise estimate for each pair.

I freeze the relationships estimated in one year and measure them in the next. Then I compare three ways to carry that information into a portfolio. The [portfolio article]({% link _posts/2026-11-20-factor-risk-sizing.md %}) asks the separate question of what those weights earn after fees.

## The sign of the position changes the answer

Each day I fit stock returns to a common market intercept, broad sectors and seven styles, with exposures lagged by one close. The intercept has unit loading for each stock, so its portfolio exposure is net weight. The fit weights squared errors by the square root of prior market cap and uses the August 2026 sector and industry labels across history. A residual is the return left after that fit. The weighted residuals balance within each fitted sector by construction, even when particular pairs still move together.

Suppose two stocks have equal specific volatility $$d$$ and residual correlation $$\rho$$. Give each a position of size $$w$$ in absolute terms. The residual variance of two longs is $$2w^2d^2(1+\rho)$$. Flip the second position to a short and the variance becomes $$2w^2d^2(1-\rho)$$. At a correlation of 0.25, the two longs have 25% more residual variance than the diagonal model predicts. The long/short pair has 25% less. That example concerns **variance**. To compare volatility, take the square root.

## Groups identified in one year still move together in the next

At each year-end I used 252 sessions of residual returns to group stocks. I repeatedly joined the two groups with the highest average correlation between their members, stopping at eleven groups. I kept the groups and the stock order fixed for the next 252 sessions. The forward comparisons use only stocks with complete observations in both windows, about 93% of the formation names on average.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/matrix" mobile="/assets/residual-risk/matrix_mobile" version="3" alt="Raw returns, formation residuals, and the following year's residuals for the same 850 stocks. Average correlation falls from about 25% to near zero after removing factors. Positive residual blocks weaken but remain visible in the following year." %}
  <p class="figure-caption">All three panels use the same 850 stocks, ordered by the residual groups formed in December 2021. Each tile averages distinct stock pairs. The outlines mark the original groups and the common color scale saturates at ±40%.</p>
</div>

This cohort had the strongest forward gap of the 27. Removing the factors brought the average correlation from **about 25% to near zero**. Pairs in the same group were still about **8.5 correlation points** more correlated than pairs in different groups. The gap shrank to **about 5 points** over the next 252 sessions with the groups held fixed.

Across all 27 cohorts, the gap went from **4.74 points in formation to 2.06 points the following year**. Shuffling group labels within industries produced a forward gap of **0.35 points** on average. The original groups beat the 95th percentile of those industry shuffles in all 27 cohorts.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/residuals" mobile="/assets/factor-risk-sizing/residuals_mobile" version="1" alt="Average stock correlation varies over time while average residual correlation stays near zero. Pairs in the same group were more correlated the following year than the sector-shuffle threshold in all 27 cohorts." %}
  <p class="figure-caption">The upper panel averages pair correlations over rolling 252-session windows. Each dot below is the following year’s within-group minus between-group residual correlation. The short marks show the 95th percentile of a sector-only shuffle.</p>
</div>

The groups mostly helped within sectors. In the 23 development cohorts the forward gap was **7.78 points** for same-sector pairs and **0.67 points** for cross-sector pairs matched on industry mix. The cross-sector difference was positive in all 23 cohorts, with a two-year-block interval of **0.52 to 0.83 points**. Matching the industry mix helps distinguish the grouping signal from the effect of putting similar businesses together.

## The model placed NVIDIA and Vertiv in different groups
{: #would-the-model-have-grouped-nvidia-and-vertiv}

<details markdown="1">
<summary>A case from the January 2025 selloff</summary>

Vertiv and NVIDIA published a design for powering and cooling NVIDIA-based data centers before the January 2025 selloff. [Vertiv’s October 2024 announcement](https://www.vertiv.com/en-emea/about/news-and-events/news-releases/vertiv-codevelops-with-nvidia-complete-power-and-cooling-blueprint-for--nvidia-gb200-nvl72-platform/)

In the 252 sessions through January 24, NVIDIA’s return correlation was **0.65 with Vertiv** and **0.16 with Workday**. After removing market, sector and style returns, those correlations were **0.14 and −0.10**. The December groups had placed all three firms in different clusters. A stock can share a risk with another firm even when its strongest relationships put it in a different group.

On January 27, NVIDIA fell about 17%, Vertiv fell 30% and Workday rose 2%. At equal dollar weights, the Vertiv short would have more than offset the NVIDIA loss. The Workday short would have added to it. I selected the episode after the selloff. None of the three stocks was in the simulated Ridge portfolios entering that session.
{: .mathjax-ignore}

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/company-pairs" mobile="/assets/residual-risk/company-pairs_mobile" version="1" alt="NVIDIA’s correlations with Vertiv and Workday at five year-ends. Workday had the higher raw correlation in 2021 and 2022. Vertiv had the higher residual correlation at all five year-ends." %}
</div>
<p class="figure-caption">Each dot uses the last 252 sessions at that year-end. Workday had the higher raw correlation with NVIDIA in 2021 and 2022. Removing the broad factors reversed the ordering. The 2025 window includes the selloff.</p>

The January selloff lifted the year-end 2025 residual correlation for NVIDIA–Vertiv. Omitting that single day brought the estimate close to its pre-selloff level.

</details>

## The shared directions persist at a smaller scale

A cluster gives each stock one label. Principal component analysis lets the same stock load on several shared directions. I estimated the directions on standardized residuals from the formation year and measured their variance over the following year. Each stock was scaled to unit variance within its own window so the comparison tracks changes in co-movement.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/directions" mobile="/assets/residual-risk/directions_mobile" version="2" alt="PCA directions lose variance after formation but retain more than shuffled directions with the same industry composition. Development PCs two through five fall from 14.30 to 4.36 versus 1.64 for the shuffle." %}
  <p class="figure-caption">Each stock starts with residual variance one. A direction with squared weights summing to one would also have variance one if all residuals were uncorrelated. The axis doubles at each tick. Each cohort receives equal weight, and each band reports the average per direction.</p>
</div>

In the 23 development cohorts, components two through five averaged **14.30** units of variance in formation and **4.36** the following year. Shuffling loadings within industry gave **1.64** forward units. The four later cohorts averaged **7.34** versus **2.14** under the shuffle. PCA chooses the directions with the largest variance in the formation sample. Some of that variance persists, and carrying all of it forward would overstate the risk.

## Putting a residual correlation into the portfolio

Let $$B$$ hold one row of factor exposures per stock and $$F$$ be the covariance of factor returns. The first term below measures risk from those common factors. For signed weights $$w$$, the portfolio holds factor exposure $$B^\top w$$ and its factor variance is $$(B^\top w)^\top F(B^\top w)$$. The second term combines the diagonal matrix of stock-specific volatilities $$D$$ with the residual correlation matrix $$R$$.

$$
\Sigma = B F B^\top + D R D.
$$

I keep $$B$$, $$F$$ and $$D$$ fixed and change $$R$$. The model starts with $$R=I$$ and treats factor shocks and residuals as uncorrelated. A stock without a complete trailing residual window keeps its named exposures and specific variance, with zero pairwise residual correlations.

- **Shrink toward zero.** For the trailing residual correlation matrix $$S$$, use $$R=(1-\alpha)S+\alpha I$$, with the weight estimated by Ledoit–Wolf shrinkage. With more stocks than observations, this raises the lowest estimated variances and reduces the largest. [Ledoit and Wolf](https://www.econ.uzh.ch/dam/jcr:ffffffff-961c-1dd9-ffff-ffffceb83f14/wellCond.pdf)
- **Keep one principal component.** Keep its contribution $$L$$ to residual correlation and return the remaining variance to each stock’s diagonal, giving $$R=L+\operatorname{diag}(S-L)$$.
- **Combine them.** Keep one or five components in $$L$$, shrink the leftover matrix $$U=S-L$$ toward its diagonal and add $$L$$ back once. This gives $$R=L+(1-\delta)U+\delta\operatorname{diag}(U)$$ and keeps the diagonal at one.

Every year I compared each forecast with the same pairs’ correlations over the next 252 sessions. Each cohort gets equal weight. For pairs in the **same sector and group**, carrying the trailing correlation forward reduced development root mean squared error from **about 17 to 12 correlation points** against a forecast of zero. For pairs in **different sectors and groups**, predicting zero or using ordinary shrinkage gave errors of around **8 points**, and keeping five components pushed the error higher. I would be cautious about sizing an individual cross-sector hedge from those estimates alone.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/pair-errors" mobile="/assets/residual-risk/pair-errors_mobile" version="1" alt="Changes in next-year pair correlation error versus forecasting zero. All estimators improved on zero for stocks in the same sector and cluster. The cross-sector, different-cluster forecasts increased error in both periods." %}
  <p class="figure-caption">Left of zero means the model estimated the next year’s pair correlations more accurately than predicting zero for every pair. One unit is 0.01 of correlation. The 23 development cohorts and four later cohorts each receive equal weight within their period. The same stock may enter many pairs.</p>
</div>

Ordinary shrinkage still reduced overall forecast error compared with predicting zero after excluding pairs of securities issued by the same company.

## Keeping five components overstated their forward risk

In development the five-component estimate assigned **about 15** units of variance per direction to components two through five. The following year delivered **about 4**, close to the ordinary-shrinkage forecast. Ordinary shrinkage also had lower forecast loss for that band in all 27 cohorts.

Keeping a component can give it *more* forecast variance than its original eigenvalue. On the formation sample the remainder $$U$$ has zero variance along a retained direction. Shrinking its off-diagonal entries removes some of the offsets that kept that variance at zero. The component then receives its original variance plus part of the remainder’s diagonal.

On the filled books, dropping residual correlations moved the factor target’s later volatility forecasts by **less than a tenth of a percentage point** on either set of holdings. Long and short weights can offset these contributions. The risk of a shared direction matters in proportion to how much of it the portfolio holds.

## What changed in the long/short book

The replay kept the Ridge scores, rebalance schedules, optimizer constraints and dated transaction fees fixed. Each covariance model chose its own positions. The table averages the three schedule-level results, and the portfolios realized different levels of risk. [Portfolio comparison at similar realized risk]({% link _posts/2026-11-20-factor-risk-sizing.md %}#trading-with-a-calibrated-risk-budget)

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

I would keep ordinary residual shrinkage within the factor model. The groups and components help show where the stocks share risk. Shrinkage carries forward a more plausible amount of that co-movement, and giving five components special treatment added little to the simulated portfolio.
