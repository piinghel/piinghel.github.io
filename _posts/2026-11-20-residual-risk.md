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

Two chip suppliers can move together even on a day when the market, their sector and common styles barely move. Some of that shared risk cancels if I’m long one and short the other. The average residual correlation across all stock pairs was **−0.06%**. It tells me very little about those two stocks.

In [Shrinking Stock Correlations Toward a Factor Model]({% link _posts/2026-11-20-factor-risk-sizing.md %}), I kept the Ridge forecasts fixed and changed the risk estimate. Here I look at what remains after the factor fit, how long it persists, and how much of it I would carry into a risk forecast.

## The sign of the position changes the answer

Each day I fit stock returns to the market, broad sectors and seven styles using exposures lagged by one close. The residual is the actual return minus the fitted return. The same August 2026 sector and industry classification snapshot is used throughout the historical fit and the industry comparisons.

Suppose two stocks have equal specific volatility $$d$$ and residual correlation $$\rho$$. Give each a position of size $$w$$ in absolute terms. The residual variance of two longs is $$2w^2d^2(1+\rho)$$. Flip the second position to a short and the variance becomes $$2w^2d^2(1-\rho)$$. At a correlation of 0.25, the two longs have 25% more residual variance than the diagonal model predicts. The long/short pair has 25% less. That example concerns **variance**. To compare volatility, take the square root.

## Groups identified in one year still move together in the next

At each year-end I used 252 sessions of residual returns to group stocks. I repeatedly joined the two groups with the highest average correlation between their members, stopping at eleven groups. I kept the groups and the stock order fixed for the next 252 sessions. The forward comparisons use only stocks with complete observations in both windows, about 93% of the formation names on average.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/matrix" mobile="/assets/residual-risk/matrix_mobile" version="2" alt="Raw returns, formation residuals, and the following year's residuals for the same 850 stocks. Average correlation falls from 24.68% to near zero after removing factors. Positive residual blocks weaken but remain visible in the following year." %}
  <p class="figure-caption">All three panels use the same 850 stocks, ordered by the residual groups formed in December 2021. Each tile averages distinct stock pairs. The outlines mark the original groups and the common color scale saturates at ±40%.</p>
</div>

This cohort had the strongest forward gap of the 27. After removing the factors, the average correlation fell from **24.68% to −0.02%**, but pairs in the same group were **8.45 percentage points** more correlated than pairs in different groups. Over the next 252 sessions the same groups still showed a **5.05-point** gap.

Across all 27 cohorts, the gap went from **4.74 points in formation to 2.06 points the following year**. Shuffling group labels within industries produced a forward gap of **0.35 points** on average. The original groups beat the 95th percentile of those industry shuffles in all 27 cohorts.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/residuals" mobile="/assets/factor-risk-sizing/residuals_mobile" version="1" alt="Average stock correlation varies over time while average residual correlation stays near zero. Pairs in the same group were more correlated the following year than the sector-shuffle threshold in all 27 cohorts." %}
  <p class="figure-caption">The upper panel averages pair correlations over rolling 252-session windows. Each dot below is the following year’s within-group minus between-group residual correlation. The short marks show the 95th percentile of a sector-only shuffle.</p>
</div>

The groups mostly helped within sectors. In the 23 development cohorts the forward gap was **7.78 points** for same-sector pairs and **0.67 points** for cross-sector pairs matched on industry mix. The cross-sector difference was positive in all 23 cohorts, with a two-year-block interval of **0.52 to 0.83 points**. Matching the industry mix helps distinguish the grouping signal from the effect of putting similar businesses together.

## The model placed NVIDIA and Vertiv in different groups
{: #would-the-model-have-grouped-nvidia-and-vertiv}

Vertiv and NVIDIA published a design for powering and cooling NVIDIA-based data centers before the January 2025 selloff. NVIDIA also used Workday’s HR software. These links exposed the companies to different customer decisions. [Vertiv’s October 2024 announcement](https://www.vertiv.com/en-emea/about/news-and-events/news-releases/vertiv-codevelops-with-nvidia-complete-power-and-cooling-blueprint-for--nvidia-gb200-nvl72-platform/) · [Workday’s customer study](https://forms.workday.com/content/dam/web/en-us/documents/ebooks/power-of-skills-insights-customer-success-story-global-enus.pdf)

In the 252 sessions through January 24, NVIDIA’s return correlation was **0.65 with Vertiv** and **0.16 with Workday**. After removing market, sector and style returns, those correlations were **0.14 and −0.10**. The December groups had placed all three firms in different clusters. A stock can share a risk with another firm even when its strongest relationships put it in a different group.

On January 27, NVIDIA fell 16.97%, Vertiv fell 29.88% and Workday rose 2.29% after DeepSeek’s model release. On $100 long NVIDIA, a $100 Vertiv short would have left a **$12.91 gain**, while a Workday short would have left a **$19.26 loss**, before fees. I selected the episode after the selloff. None of the three stocks was in the simulated Ridge portfolios entering that session. [NYSE’s account of the selloff](https://www.ice.com/insights/conversations/inside-the-ice-house/market-storylines/01-27-2025)
{: .mathjax-ignore}

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/company-pairs" mobile="/assets/residual-risk/company-pairs_mobile" version="1" alt="NVIDIA’s correlations with Vertiv and Workday at five year-ends. Workday had the higher raw correlation in 2021 and 2022. Vertiv had the higher residual correlation at all five year-ends." %}
</div>
<p class="figure-caption">Each dot uses the last 252 sessions at that year-end. Workday had the higher raw correlation with NVIDIA in 2021 and 2022. Removing the broad factors reversed the ordering. The 2025 window includes the selloff. <a href="/assets/residual-risk/nvidia-pair-correlations.csv">Download the correlations and dates (CSV).</a></p>

The one-day selloff pushed NVIDIA–Vertiv’s year-end 2025 residual correlation to **0.25**. Removing it brought the estimate back to **0.15**. That is close to the **0.14** measured before the event. I would use that history and the business link to investigate shared exposures, particularly when the group labels alone miss a plausible hedge. [Single-day sensitivity (CSV)]({{ '/assets/residual-risk/nvidia-single-session-sensitivity.csv' | relative_url }})

## The shared directions persist at a smaller scale

A cluster gives each stock one label. Principal component analysis lets the same stock load on several shared directions. I estimated the directions on standardized residuals from the formation year and measured their variance over the following year. Each stock was scaled to unit variance within its own window so the comparison tracks changes in co-movement.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/directions" mobile="/assets/residual-risk/directions_mobile" version="2" alt="PCA directions lose variance after formation but retain more than shuffled directions with the same industry composition. Development PCs two through five fall from 14.30 to 4.36 versus 1.64 for the shuffle." %}
  <p class="figure-caption">Each stock starts with residual variance one. A direction with squared weights summing to one would also have variance one if all residuals were uncorrelated. The axis doubles at each tick. Each cohort receives equal weight, and each band reports the average per direction.</p>
</div>

In the 23 development cohorts, components two through five averaged **14.30** units of variance in formation and **4.36** the following year. Shuffling loadings within industry gave **1.64** forward units. The four later cohorts averaged **7.34** versus **2.14** under the shuffle. PCA chooses the directions with the largest variance in the formation sample. Some of that variance persists, and carrying all of it forward would overstate the risk.

## Putting a residual correlation into the portfolio

I kept the named factor exposures $$B$$, factor covariance $$F$$ and specific volatilities $$D$$ fixed. Only the residual correlation matrix $$R$$ changed.

$$
\Sigma = B F B^\top + D R D.
$$

The starting model uses $$R=I$$. Each stock has its own specific variance, and the forecast assigns zero covariance to stock pairs’ residuals and between residuals and factor shocks. I compared three ways of allowing residuals to move together. [Paleologo, *The Elements of Quantitative Investing*, §§6.4.4–6.4.5 and chapter 7](https://www.wiley.com/en-us/shop/general-finance-investments/the-elements-of-quantitative-investing-p-9781394265466)

- **Shrink toward zero.** For the trailing residual correlation matrix $$S$$, use $$R=(1-\alpha)S+\alpha I$$, with the weight estimated by Ledoit–Wolf shrinkage. With more stocks than observations, this raises the lowest estimated variances and reduces the largest. [Ledoit and Wolf](https://www.econ.uzh.ch/dam/jcr:ffffffff-961c-1dd9-ffff-ffffceb83f14/wellCond.pdf)
- **Keep principal components.** Keep the covariance $$L$$ explained by the first one or five components and return the remaining variance to each stock’s diagonal, giving $$R=L+\operatorname{diag}(S-L)$$.
- **Combine them.** Shrink the leftover matrix $$U=S-L$$ toward its diagonal and add the components back once, giving $$R=L+(1-\delta)U+\delta\operatorname{diag}(U)$$. The diagonal stays at one in all three cases.

Every year I compared each forecast with the same pairs’ correlations over the next 252 sessions. Each cohort gets equal weight. For pairs in the **same sector and group**, carrying the trailing correlation forward reduced development root mean squared error from **16.88 to 12.03 correlation points** against a forecast of zero. For pairs in **different sectors and groups**, zero had an error of **7.65**, plain shrinkage **7.73**, and five components plus shrinkage **8.50**. Some cross-sector co-movement persisted on average, but those estimates were too large to improve the individual pair forecasts in that group.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/pair-errors" mobile="/assets/residual-risk/pair-errors_mobile" version="1" alt="Changes in next-year pair correlation error versus forecasting zero. All estimators improved on zero for stocks in the same sector and cluster. The cross-sector, different-cluster forecasts increased error in both periods." %}
  <p class="figure-caption">Left of zero means the model estimated the next year’s pair correlations more accurately than predicting zero for every pair. One unit is 0.01 of correlation. The 23 development cohorts and four later cohorts each receive equal weight within their period. The same stock may enter many pairs.</p>
</div>

Excluding pairs of securities issued by the same company barely changed the overall result. For pairs of different issuers, ordinary shrinkage reduced mean squared error against zero by **2.56%** in development and **7.69%** later.

## Keeping five components overstated their forward risk

In development the five-component estimate assigned **14.96** units of forecast variance per direction to components two through five. The following year delivered **4.36**. Ordinary shrinkage forecast **3.95**, much closer. It also had the lower variance-forecast loss for that band in all 27 cohorts.

Keeping a component can give it *more* forecast variance than its original eigenvalue. On the formation sample the remainder $$U$$ has zero variance along a retained direction. Shrinking its off-diagonal entries removes some of the offsets that kept that variance at zero. The component then receives its original variance plus part of the remainder’s diagonal.

The difference was much smaller on the filled Ridge portfolios. Removing residual correlations from the factor target’s later risk forecasts moved the estimate from **7.00% to 6.98%** on its own holdings and from **9.95% to 9.86%** on the stock-shrinkage holdings. The residual terms can reinforce or offset one another once the long and short weights enter the calculation. Keeping only the residual correlations within each frozen group also gave similar forecasts and showed no clear hedge improvement over ordinary shrinkage.

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

Ordinary residual shrinkage improved on diagonal residuals in the later sample. Annual return after fees went from **2.72% to 3.97%**, with volatility down from **8.29% to 8.04%**. In development it also lowered volatility, with a small decline in return. Adding five components on top of shrinkage moved later net Sharpe by **+0.003**, with a paired 95% interval of **−0.058 to +0.066**.

I would keep ordinary residual shrinkage within the factor model. The groups and components help show where the stocks share risk. Shrinkage carries forward a more plausible amount of that co-movement, and giving five components special treatment added little to the simulated portfolio.
