---
layout: post
title: "Factor Risk, Part 2: Residual Risk After Sectors and Styles"
description: "I froze groups of stocks and principal directions learned from a year of residual returns, then followed them through the next year and into a long/short portfolio."
date: 2026-11-20
last_modified_at: 2026-11-20
categories: ["Portfolio construction"]
article_label: Factor risk · Part 2 of 2
series_id: factor-risk
series_order: 2
toc: false
permalink: /quants/residual-risk.html
---

In [Part 1]({% link _posts/2026-11-20-factor-risk-sizing.md %}#from-stock-exposures-to-portfolio-risk), a spread that was long A and short B had three units of daily variance. Part of that came from factors and part from the two individual residuals. The calculation gave A and B zero residual correlation. Here I change that assumption while keeping the same stocks, exposures and positions.

A sector factor can capture a broad move while a smaller group within the sector still moves together. I look for those groups in one year of residuals and follow the same groups into the next. Principal components give me another way to measure the shared moves and test how much of their strength is worth carrying into a risk forecast.

## The sign of the position changes the answer

Keep the specific volatilities of A, B and C at 2%, 2% and 1%. Suppose A and B have a residual correlation of 0.6, with the other pair correlations at zero. Write the specific volatilities on the diagonal of $$D$$ and the residual correlations in $$R$$. Both matrices are in stock order A, B, C.

$$
\begin{aligned}
D&=\begin{pmatrix}2&0&0\\0&2&0\\0&0&1\end{pmatrix},\\
R&=\begin{pmatrix}1&0.6&0\\0.6&1&0\\0&0&1\end{pmatrix}.
\end{aligned}
$$

Right-multiplying by $$D$$ scales the columns of $$R$$. Left-multiplying by $$D$$ scales the rows. The A–B entry is now $$2(0.6)2=2.4$$ squared percentage points of covariance. Each diagonal stays at the stock’s specific variance.

$$
\begin{gathered}
RD=\begin{pmatrix}2&1.2&0\\1.2&2&0\\0&0&1\end{pmatrix},\\
DRD=D(RD)\\
=
\begin{pmatrix}2&0&0\\0&2&0\\0&0&1\end{pmatrix}
\begin{pmatrix}2&1.2&0\\1.2&2&0\\0&0&1\end{pmatrix}\\
=\begin{pmatrix}4&2.4&0\\2.4&4&0\\0&0&1\end{pmatrix}.
\end{gathered}
$$

Add that matrix to the factor covariance from Part 1. The A–B stock covariance goes from 3 to 5.4. Their individual total variances stay at 9 each. The same 50%-long A and 50%-short B spread now has daily variance

$$
\begin{aligned}
w^\top\Sigma w&=0.5^2(9)+(-0.5)^2(9)\\
&\quad+2(0.5)(-0.5)(5.4)\\
&=1.8.
\end{aligned}
$$

The cross term gets a minus sign from the short. If both positions were long, the same positive covariance would add to risk. For the spread, the extra residual covariance lowers daily variance from 3 to 1.8. The research question is whether a correlation estimated from past returns holds up when the spread is held.

## Groups identified in one year still move together in the next

I use the residuals from the daily market, sector and seven-style fit in Part 1. The sector and industry labels come from the same August 2026 snapshot. At each year-end I group stocks by their trailing 252-session residual correlations, then hold the groups and stock order fixed for the next 252 sessions. The forward comparison uses names observed in both windows, about 93% of the formation names on average.

Read the heatmaps from left to right. In the first two panels, the dates, stocks and order are identical. The first uses stock returns and the second uses the returns left by the factor fit. The third keeps the same order and uses the next 252 sessions. A block in the same place in the last two panels means that group still moves together.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/matrix" mobile="/assets/residual-risk/matrix_mobile" version="3" alt="Raw returns, formation residuals, and the following year's residuals for the same 850 stocks. Average correlation falls from about 25% to near zero after removing factors. Positive residual blocks weaken but remain visible in the following year." %}
  <p class="figure-caption">The same 850 stocks appear in all three panels. Each tile averages correlations between distinct stock pairs, and the outlines mark the groups formed in December 2021. Zero has the same neutral color in each panel. The shared scale stops at ±40%. This cohort had the strongest forward gap.</p>
</div>

Removing the factors brought the average correlation from **about 25% to near zero**. Pairs in the same group were still about **8.5 correlation points** more correlated than pairs in different groups. The gap shrank to **about 5 points** over the next 252 sessions with the groups held fixed.

Across all 27 cohorts, within-group correlation was about **5 points** higher than between-group correlation in formation and about **2 points** higher the next year. Shuffling group labels within industries produced a forward gap of less than half a point on average. The original groups beat the 95th percentile of those industry shuffles in all 27 cohorts.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/residuals" mobile="/assets/factor-risk-sizing/residuals_mobile" version="1" alt="Average stock correlation varies over time while average residual correlation stays near zero. Pairs in the same group were more correlated the following year than the sector-shuffle threshold in all 27 cohorts." %}
  <p class="figure-caption">The upper panel shows how far the market-wide average correlation falls after fitting the factors. Each dot below is one year-end cohort’s following-year difference between within-group and between-group correlation. The short mark for that cohort is the 95th percentile from shuffling labels within sectors. The industry shuffle in the text is a separate check.</p>
</div>

The forward correlation gap was much larger within sectors. In the 23 development cohorts it was **about 8 points** for same-sector pairs and **less than 1 point** for cross-sector pairs matched on industry mix. The cross-sector difference was positive in all 23 cohorts. The clustering picked up some co-movement across sectors, but much more of it was within sectors.

## The model placed NVIDIA and Vertiv in different groups
{: #would-the-model-have-grouped-nvidia-and-vertiv}

Vertiv and NVIDIA published a design for powering and cooling NVIDIA-based data centers before the January 2025 selloff. [Vertiv’s October 2024 announcement](https://www.vertiv.com/en-emea/about/news-and-events/news-releases/vertiv-codevelops-with-nvidia-complete-power-and-cooling-blueprint-for--nvidia-gb200-nvl72-platform/)

In the 252 sessions through January 24, NVIDIA’s residual correlation was **0.14 with Vertiv** and **−0.10 with Workday**. The December groups had placed all three firms in different clusters. A group summarizes many stock pairs, so its label can miss a relationship between two particular names.

On January 27, NVIDIA and Vertiv fell while Workday rose. I picked the date after seeing the selloff. The episode illustrates the kind of exposure a cluster can miss; hedge quality is measured on the broader set of dates and stocks in the portfolio article.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/company-pairs" mobile="/assets/residual-risk/company-pairs_mobile" version="1" alt="NVIDIA’s correlations with Vertiv and Workday at five year-ends. Workday had the higher raw correlation in 2021 and 2022. Vertiv had the higher residual correlation at all five year-ends." %}
</div>
<p class="figure-caption">Each dot uses the last 252 sessions at that year-end. Workday had the higher raw correlation with NVIDIA in 2021 and 2022. Removing the broad factors reversed the ordering. The 2025 window includes the selloff.</p>

The January selloff lifted the year-end 2025 residual correlation for NVIDIA–Vertiv. Omitting that single day brought the estimate close to its pre-selloff level.

## The shared directions persist at a smaller scale

A cluster gives each stock one label. Principal component analysis (PCA) lets the same stock contribute to several shared moves. To estimate those moves, I first subtract each stock’s mean residual return and divide by its own standard deviation over the fit window. That puts the stock columns on equal footing. For example, if A’s residuals over four days are $$3,-1,3,-1$$, subtracting its mean of 1 and dividing by its standard deviation of 2 gives $$1,-1,1,-1$$.

Take four days of standardized residuals for A, B and C. The rows of $$Z$$ are days and its columns are stocks. Transposing gives $$Z^\top$$, with one row per stock.

$$
\begin{aligned}
Z^\top&=
\begin{pmatrix}
1&-1&1&-1\\
1.4&0.2&-0.2&-1.4\\
1&-1&-1&1
\end{pmatrix},\\
Z&=
\begin{pmatrix}
1&1.4&1\\
-1&0.2&-1\\
1&-0.2&-1\\
-1&-1.4&1
\end{pmatrix}.
\end{aligned}
$$

To get the A–B entry of $$Z^\top Z/4$$, multiply A’s row by B’s column and divide by four.

$$
\begin{gathered}
4S_{AB}=\text{row A}\cdot\text{column B}\\
=\begin{pmatrix}1&-1&1&-1\end{pmatrix}
\begin{pmatrix}1.4\\0.2\\-0.2\\-1.4\end{pmatrix}\\
=1.4-0.2-0.2+1.4=2.4.
\end{gathered}
$$

Dividing by four gives a correlation of 0.6. Repeating that operation for all pairs gives the same matrix used in the spread example.

$$
\begin{aligned}
S&=\frac{Z^\top Z}{4}
=\frac14\begin{pmatrix}4&2.4&0\\2.4&4&0\\0&0&4\end{pmatrix}\\
&=\begin{pmatrix}1&0.6&0\\0.6&1&0\\0&0&1\end{pmatrix}.
\end{aligned}
$$

For any weights $$q$$, $$Zq$$ gives the combined daily moves and $$q^\top Sq$$ gives their variance. The first component chooses the weights with the most variance, with squared weights adding to one. That constraint puts all directions on the same scale. Here the strongest direction holds A and B with the same sign. Multiplying it by $$S$$ returns the same direction scaled by 1.6, its variance.

$$
\begin{aligned}
Sq&=\frac{1}{\sqrt{2}}
\begin{pmatrix}1&0.6&0\\0.6&1&0\\0&0&1\end{pmatrix}
\begin{pmatrix}1\\1\\0\end{pmatrix}\\
&=\frac{1}{\sqrt{2}}\begin{pmatrix}1.6\\1.6\\0\end{pmatrix}.
\end{aligned}
$$

The other orthogonal directions here are C on its own, with variance one, and the A–B spread, with variance 0.4. On the real weekly residual data, the first component explained about 3% of total standardized residual variance in a typical fit. Its importance to a particular portfolio also depends on how closely the holdings line up with it.

For the chart, I fit the directions on 252 sessions and measure their variance over the following 252, using stocks observed in both windows. Each window is standardized with its own stock volatilities so the comparison tracks changes in co-movement. The portfolio replay estimates the scales and directions from the trailing history available at each decision.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/directions" mobile="/assets/residual-risk/directions_mobile" version="2" alt="PCA directions lose variance after formation but retain more than shuffled directions with the same industry composition. Development PCs two through five fall from 14.30 to 4.36 versus 1.64 for the shuffle." %}
  <p class="figure-caption">Within each band, compare the formation estimate with the same directions in the following year. The industry shuffle redistributes the stock weights within industries as a reference. A value of one is the variance of a unit-length direction if residuals are uncorrelated. The axis doubles at each tick and each cohort receives equal weight.</p>
</div>

In the 23 development cohorts, components two through five fell from **about 14** units of variance per direction to **about 4** the following year. The industry shuffle came in below **2**. There is some persistence, and the observed strength is well below what the formation fit suggests. The four later cohorts show the same drop from formation and the same separation from the shuffle.

## Putting a residual correlation into the portfolio

The comparisons keep the named-factor covariance and $$D$$ fixed. The specific volatilities in $$D$$ use a 63-session exponential half-life. The residual correlations in $$R$$ use the trailing 252 sessions. Changing $$R$$ changes the cross-covariances in $$DRD$$ while preserving the individual specific variances.

The baseline uses $$R=I$$. A stock without a complete trailing residual window keeps its named exposures and its specific variance, with zero pairwise residual correlations.

- **Shrink toward zero.** For the trailing residual correlation matrix $$S$$, use $$R=(1-\alpha)S+\alpha I$$, with the weight estimated by Ledoit–Wolf shrinkage. This pulls pairwise residual correlations toward zero while preserving each stock’s specific variance. [Ledoit and Wolf](https://www.econ.uzh.ch/dam/jcr:ffffffff-961c-1dd9-ffff-ffffceb83f14/wellCond.pdf)
- **Keep one principal component.** Keep its contribution $$L$$ to residual correlation and return the remaining variance to each stock’s diagonal, giving $$R=L+\operatorname{diag}(S-L)$$.
- **Combine them.** Keep one or five components in $$L$$, shrink the leftover matrix $$U=S-L$$ toward its diagonal and add $$L$$ back once. This gives $$R=L+(1-\delta)U+\delta\operatorname{diag}(U)$$ and keeps the diagonal at one.

In the three-stock example, shrinking halfway toward zero cuts the A–B correlation from 0.6 to 0.3. Keeping only the first component can push it the other way. Take its variance $$1.6$$ and multiply by the outer product of its weights.

$$
\begin{aligned}
L &= 0.8\begin{pmatrix}1\\1\\0\end{pmatrix}
              \begin{pmatrix}1&1&0\end{pmatrix}\\
  &= \begin{pmatrix}0.8&0.8&0\\0.8&0.8&0\\0&0&0\end{pmatrix}.
\end{aligned}
$$

Restoring the diagonal to one leaves the A–B entry at 0.8. Their opposite-sign direction contributed −0.2 to the original correlation of 0.6. Keeping the first component and discarding that offset raises the estimated correlation. This is one reason I check the retained components against subsequent returns.

Every year I compared each forecast with the same pairs’ correlations over the next 252 sessions. Each cohort gets equal weight. For pairs in the **same sector and group**, carrying the trailing correlation forward reduced development root mean squared error from **about 17 to 12 correlation points** against a forecast of zero. For pairs in **different sectors and groups**, predicting zero or using ordinary shrinkage gave errors of around **8 points**, and keeping five components pushed the error higher. I would be cautious about sizing an individual cross-sector hedge from those estimates alone.

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

I would keep ordinary shrinkage when estimating residual covariance. The groups show where co-movement persisted. The component tests show how easily the formation sample can exaggerate its strength. Keeping five components at their estimated strength made the variance forecasts worse in the directions I tested and barely changed the later portfolio Sharpe.
