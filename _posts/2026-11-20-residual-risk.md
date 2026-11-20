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

The sector and style model left an average stock-pair correlation of **−0.06%**. If I took that number literally for every pair, an equal-dollar long and short in two chip suppliers would have about the same residual risk as two longs. Yet if both firms depend on the same customer orders, the short could hedge part of the long. The average across all stock pairs tells me very little about the particular two I hold.

In [Shrinking Stock Correlations Toward a Factor Model]({% link _posts/2026-11-20-factor-risk-sizing.md %}), I compared three ways to size the same Ridge stock forecasts. Here I look inside the factor model. I wanted to find out whether stocks that moved together after the named factors came out would keep moving together the following year. If that relationship persisted, I could then test how much of it was worth keeping in a portfolio.

## The sign of the position changes the answer

Each day I explain stock returns using exposures known at the previous close to the market, broad sectors and seven styles. A stock’s residual is its actual return less its fitted return that day. These residuals are what remain after a particular model has had its say. A common shock missing from the model can appear in the residuals of several companies.

Suppose two stocks have equal specific volatility $$d$$ and residual correlation $$\rho$$. Give each a position of size $$w$$ in absolute terms. The residual variance of two longs is $$2w^2d^2(1+\rho)$$. Flip the second position to a short and the variance becomes $$2w^2d^2(1-\rho)$$. At a correlation of 0.25, the two longs have 25% more residual variance than the diagonal model predicts. The long/short pair has 25% less. That example concerns **variance**. To compare volatility, take the square root.

I measured average correlation over 252 completed sessions at each of 1,429 weekly decisions. The same pairs averaged 29.71% on stock returns and −0.06% on residuals, giving each week equal weight. The regression itself helps explain the second number. Because it includes a market intercept, the weighted residuals balance across stocks each day. This does not force the equally weighted mean of standardized pair correlations to zero, but it gives me a reason to look beyond that average.

## Groups identified in one year still move together in the next

At each year-end I grouped stocks using a year of residual correlations. I used average-linkage clustering, joining groups whose stock pairs had a small average distance, with distance defined as one minus correlation. I stopped at eleven groups, the number of broad sectors. The stocks could group across sector boundaries. I then froze both the membership and the order and measured the next 252 sessions. Forward measurements use the stocks with complete observations in both windows. On average, 92.6% of the formation stocks qualified.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/matrix" mobile="/assets/residual-risk/matrix_mobile" version="1" alt="Residual correlations among 850 stocks grouped through December 2021. With the same stocks in the same order the next year, several positive blocks remain along the diagonal, although they weaken." %}
  <p class="figure-caption">Both panels show the same 850 stocks. Each tile averages distinct pairs in small blocks of stocks, and the boundaries mark the eleven original groups. Red is positive, blue is negative, and the color scale is identical in both panels. A stock’s correlation with itself is excluded.</p>
</div>

The December 2021 example is useful because you can see exactly what persisted. The stocks grouped together in the left panel had a mean pairwise correlation **8.45 percentage points** higher than pairs from different groups. In the following year that gap was **5.05 points**, with the group boundaries fixed. I would expect a weaker gap once the data used to choose the groups are behind us.

Across **all 27 annual cohorts**, the gap went from **4.74 points in formation to 2.06 points the following year**. Some groups had recognizable businesses in them. In the December 2021 formation, one had 21 industrial-products stocks among 31 members. Another had 21 hardware and semiconductor stocks among 39. I shuffled the labels within industries and sectors, keeping each group’s industry composition intact. That produced a forward gap of only **0.35 points** on average. The actual gap exceeded the 95th percentile of those shuffles in all 27 cohorts. The stocks carried information about one another beyond the industry mix. These returns alone cannot identify the economic cause.

Could the grouping have picked up a relationship like the chip designer and its cooling supplier? I took only pairs from different sectors. For a semiconductor and machinery pair placed in the same cluster, I used semiconductor and machinery pairs placed in different clusters as the comparison. I repeated this for every industry pair and gave the comparison pairs the same industry mix as the pairs sharing a cluster.

In the 23 development years, the next year’s mean residual correlation for those cross-sector pairs was **0.55% inside a cluster and −0.12% for the matched comparison**. The difference was **0.67 percentage points**, with a two-year-block 95% interval of **0.52 to 0.83 points**. It was positive in all 23 years. Applying the same test to pairs from the same sector gave a much larger **7.78-point** gap. The four later cohorts averaged **2.41 and 10.37 points**, respectively. So the groups did pick up some common movement across sector boundaries. Two stocks in the same sector showed a much larger increase in correlation when the clustering put them together. A specific AI supply-chain connection would still need business evidence.

## The shared directions persist at a smaller scale

A cluster puts each stock in one group. Principal component analysis lets each stock load by different amounts, and with either sign, on several shared directions. I standardized each stock’s residuals over the formation year and found the weighted combinations with the greatest variance. I froze those directions and measured them over the following year. For the stocks still observable, I restored unit length and orthogonality in their original order. I used the forward year’s own stock volatilities when measuring forward correlation. This test asks whether co-movement persists after stripping out changes in each stock’s volatility.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/directions" mobile="/assets/residual-risk/directions_mobile" version="1" alt="PCA directions lose variance after formation but retain more than shuffled directions with the same industry composition. Development PCs two through five fall from 14.30 to 4.36 versus 1.64 for the shuffle." %}
  <p class="figure-caption">Each stock starts with residual variance one. A direction with squared weights summing to one would also have variance one if all residuals were uncorrelated. The axis doubles at each tick. Each cohort receives equal weight, and each band reports the average per direction.</p>
</div>

Take components two through five. In the 23 development cohorts their average variance fell from **14.30** to **4.36**. Four units of variance represent twice the standard deviation of the uncorrelated reference. Shuffling the stock loadings within industry and sector gave **1.64** units the following year. The difference was **2.72** units, with a two-year-block 95% interval of **2.41 to 3.04**. In the four later cohorts the corresponding comparison was **7.34 against 2.14**. Four cohorts provide a short record for judging stability over time.

This distinction matters for sizing. A model assigning variance one to these directions misses persistent co-movement. A model carrying the entire formation-year variance forward can make the opposite error. PCA identifies a direction by maximizing the variance on the sample in front of it. Its eigenvalue has already benefited from that choice.

## Putting a residual correlation into the portfolio

I kept the named factor exposures $$B$$, their daily covariance $$F$$ and the diagonal matrix of current stock-specific volatilities $$D$$. Only the residual correlation matrix $$R$$ changed. The total stock covariance is

$$
\Sigma = B F B^\top + D R D.
$$

I started with $$R=I$$. This gives each stock its own specific variance and sets the forecast covariance between two stocks’ residuals to zero. I also assume zero forecast covariance between named factor returns and residual shocks. Both are second-moment assumptions. Neither requires independence.

For the PCA version, let $$S$$ be the prior year’s sample residual correlation matrix. For each of its first $$k$$ unit eigenvectors $$q_j$$ and eigenvalues $$\lambda_j$$, keep the component $$\lambda_j q_j q_j^\top$$. Their sum is $$L$$. Setting $$R=L+\operatorname{diag}(S-L)$$ gives common residual risk through those directions and returns the unused variance to each stock. In factor language the extra stock loadings are $$D q_j\sqrt{\lambda_j}$$ on unit-variance factors. Each retained direction already uses part of the stock’s specific variance. Keeping the entire old diagonal alongside it would count that part twice.

For residual shrinkage, I used $$R=(1-\alpha)S+\alpha I$$, estimating the weight from the trailing standardized observations. With more stocks than days, the sample correlation has directions of zero estimated variance. Shrinkage raises those low estimates and pulls down the large ones. It can therefore both reduce the risk assigned to a concentrated theme and raise the risk assigned to a supposed hedge. [Ledoit and Wolf, *A well-conditioned estimator for large-dimensional covariance matrices*](https://www.ledoit.net/Well-conditioned2004.pdf)

To combine the two, I estimated a shrinkage weight $$\delta$$ on the standardized residuals remaining after the retained PCs. Writing $$U=S-L$$, the resulting correlation is

$$
R=L+(1-\delta)U+\delta\operatorname{diag}(U).
$$

At zero shrinkage I recover the original sample correlation. At full shrinkage I retain the common PCs and each stock’s remaining diagonal variance. This preserves a diagonal of one throughout. Stocks without the full trailing history retain their named factors and specific variances. In the portfolio test the extra residual covariance applies only to pairs for which it could have been estimated at the time.

## Keeping five components overstated their forward risk

There is a subtlety in “keeping” a component. On the full formation sample, a retained eigenvector $$q$$ with eigenvalue $$\lambda$$ satisfies $$Uq=0$$. After shrinking the remainder toward its own diagonal, the forecast variance along that same vector is

$$
q^\top Rq = \lambda + \delta\sum_i q_i^2 U_{ii}.
$$

The estimator keeps the component’s covariance and every stock’s original variance. Removing some of the remainder’s off-diagonal terms also removes some offsets along $$q$$. The forecast variance in that direction can therefore exceed its fitted eigenvalue.

For components two through five in development, the five-component model forecast **14.96** units of variance per direction. The following year delivered **4.36**. Ordinary residual shrinkage forecast **3.95**. In the four later cohorts the comparison was **19.25** for five components and **8.26** for ordinary shrinkage, against **7.34** realized. For each cohort I scored forecast variance $$v$$ against realized variance $$u$$ with $$\log v + u/v$$. Lower is better, and ordinary shrinkage had the lower loss in all 27 comparisons for this band. These are forecasts for particular combinations of standardized stock residuals. To see how much they mattered in dollars, I needed to trade the portfolio.

## What changed in the long/short book

The daily portfolio test used the same Ridge forecasts, 75 new candidates per side, 7% annual risk budget, trade penalty, position limits and fill rules throughout. I computed annual net return, volatility and Sharpe separately for three staggered rebalance schedules before averaging each statistic. The table reports what their filled positions earned after the dated fees.

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

Starting from diagonal residuals, ordinary shrinkage cut later volatility from **8.29% to 8.04%**, reduced maximum drawdown from **10.54% to 9.40%** and raised annual net return from **2.72% to 3.97%**. Fees fell by about 0.03 percentage points per year. In development the modest reduction in volatility came with slightly lower net return. The 4.70-point later return gap from the original factor model to stock shrinkage fell to 3.45 points. There is value in allowing residuals to share risk, but this accounts for only part of the portfolio difference.

Going from ordinary residual shrinkage to five components plus shrinkage changed later annual net return from **3.969% to 3.975%**. Annual volatility fell a further **0.046 percentage points**. Turnover rose from **17.84× to 18.05× capital**. The later Sharpe difference was **+0.003**, with a paired 63-session-block 95% interval of **−0.058 to +0.066**. In development it was **+0.007** with an interval of **−0.030 to +0.045**. These intervals compare the two named policies on the same dates. I had already studied this history when I chose to test five directions.

I would keep ordinary residual shrinkage in the factor model. The frozen groups helped me see where the diagonal assumption breaks down. PCA showed that several shared directions survived the next year, and by how much their strength faded. Ordinary shrinkage came substantially closer to their forward variance, and giving five PCs special treatment added little to the traded book. I would still use the directions to inspect a portfolio’s exposures. For assigning risk to them, I prefer the forecast that survived the forward test.
