---
layout: post
title: "Factor Risk Models, Part 2: Residual Risk After Sectors and Styles"
description: "I froze groups of stocks and principal directions learned from a year of residual returns, then followed them through the next year and into a long/short portfolio."
date: 2026-11-20
last_modified_at: 2026-11-23
categories: ["Portfolio construction"]
article_label: Factor risk · Part 2 of 2
series_id: factor-risk
series_order: 2
toc: false
permalink: /quants/residual-risk.html
---

On the day we fitted in [*Factor Risk Models, Part 1*]({% link _posts/2026-11-20-factor-risk-sizing.md %}#a-three-stock-example), A and B both did half a percentage point better than their fitted returns. In a spread that’s 50% long A and 50% short B, those equal residuals cancel.

That happened on one day. Now imagine A and B rely on the same supplier. When it has a problem, both stocks might do worse than the market, sector and style moves would suggest. If that keeps happening, B might be a better hedge for A than a model with zero residual correlations would suggest. How much of that offset can we count on?

## Four days of residuals give one correlation

A stock’s **residual volatility** tells us how big its unexplained moves tend to be. Residual correlation tells us whether two stocks tend to make those moves on the same days. Start by looking at A on its own.

A’s residual returns over four days are +3%, −1%, +3% and −1%. Subtract their average of 1% and divide by their standard deviation of 2%. The four returns become +1, −1, +1 and −1. Each entry now says how many of A’s own standard deviations it was above or below its average. Do the same for B and C and put the resulting series side by side in $$Z$$. For this example the variance calculation divides by four, the number of observations.

{% assign example = site.data.factor_risk_example %}
<div class="matrix-calculation" role="group" aria-label="Standardized daily stock residuals and the resulting correlation matrix">
  <div>
    {% include worked-matrix.html matrix=example.standardized_residuals symbol="Z" label="Standardized residuals" tone="residual" mark_column="A" %}
  </div>
  <div>
    <span class="matrix-operator" aria-hidden="true">→</span>
    {% include worked-matrix.html matrix=example.residual_correlations symbol="S" label="Residual correlation" tone="residual" mark_row="A" mark_column="B" %}
  </div>
</div>

Read across the first row of $$Z$$. A and B are both above their averages, so $$1\times1.4=1.4$$. On day 2 they’re on opposite sides, so $$-1\times0.2=-0.2$$. Do that for all four days and you get $$1.4,-0.2,-0.2,1.4$$. The moves on days 1 and 4 matter more here because their products are larger in magnitude. The average is 0.6, which goes in the A–B cell on the right. C’s products average to zero with either stock.

Doing that for every pair gives $$S=Z^\top Z/T$$, the sample correlation matrix. The denominator $$T$$ is four in this example.

## The sign of the position changes the answer

Take the same 50%-long A, 50%-short B spread. If both residuals are +2%, A adds one percentage point to the spread and the short in B takes one away. If A has a +2% residual and B has a −2% residual, both positions add a point. The variance forecast gives more credit to the hedge when A and B tend to move together.

In Part 1 the spread had daily variance of 3 in squared percentage points. Momentum contributed 1, and each position added 1 of residual variance. Keep that factor risk and the stock residual volatilities of 2%, 2% and 1%. The only change is to give A and B the 0.6 correlation from the four-day example.

Correlation puts every stock on the same scale. Now we need to put the actual volatilities back in. Follow the A–B entry below. Start with the correlation of 0.6 and multiply by B’s volatility, 2%, to get 1.2. Then multiply by A’s volatility, also 2%, to get 2.4 in squared percentage points.

The matrix $$R$$ contains the correlations I use in the forecast. The diagonal matrix $$D=\operatorname{diag}(2,2,1)$$ contains the three residual volatilities. Multiplying $$R$$ on the right by $$D$$ scales each column by its stock’s volatility. Multiplying that on the left by $$D$$ scales each row. The result is the residual covariance matrix $$\Omega=DRD$$.

<div class="matrix-calculation" role="group" aria-label="Scale the columns of the residual correlation matrix by specific volatilities, then scale its rows">
  <div class="matrix-product">
    {% include worked-matrix.html matrix=example.residual_correlations symbol="R" label="Residual correlation" tone="residual" mark_row="A" mark_column="B" %}
    <span class="matrix-operator" aria-hidden="true">→</span>
    {% include worked-matrix.html matrix=example.scaled_correlations symbol="RD" label="Columns scaled" tone="residual" mark_row="A" mark_column="B" %}
  </div>
  <div>
    <span class="matrix-operator" aria-hidden="true">→</span>
    {% include worked-matrix.html matrix=example.residual_covariance symbol="DRD" label="Residual covariance" tone="residual" mark_row="A" mark_column="B" %}
  </div>
</div>

Each of the two A–B entries contributes $$0.5(-0.5)(2.4)=-0.6$$ to spread variance. Together they take 1.2 units off the original estimate of 3, leaving 1.8. With both positions on the same side, the product of weights would be positive and the same covariance would add risk.

The calculation also works directly from the total stock covariance. Add the residual covariance of 2.4 to the factor covariance of 3. The A–B entry rises to 5.4 and both stock variances stay at 9. With +0.5 and −0.5 weights, the result is

$$
w^\top\Sigma w=\frac{9+9-2(5.4)}{4}=1.8.
$$

Using all of the sample correlation assumes the relationship carries forward at full strength. Shrink 0.6 halfway toward zero and the spread gets half as much hedging credit. The three rows show how the choice feeds through from correlation to variance. Covariance and variance are both in squared percentage points.

<div class="matrix-calculation" role="group" aria-label="Spread variance if the forecast uses zero, half, or all of the sample residual correlation">
  {% include worked-matrix.html matrix=example.residual_spread_variance label="How much of the sample correlation to use" tone="residual" mark_column="Spread variance" %}
</div>

We can calculate all three forecasts from the same four days. To choose between them, we need to see how much of the relationship survives in the next window.

## Groups identified in one year still move together in the next

In the example, A and B have a stronger residual relationship with each other than either has with C. In a larger universe I can look for groups of stocks with that pattern. The groups give me a way to test many related pairs at once.

I use residuals from a daily fit with a market intercept, broad sectors and seven style factors. At each year-end I group stocks by their trailing 252-session residual correlations. I keep each stock’s group fixed through the following year and measure the correlations again. If pairs in the same group still move together more than pairs in different groups, the grouping has picked up a relationship that lasts beyond the year used to find it. The comparison uses stocks observed in both windows, about 93% of the initial names on average.

The first two heatmaps compare stock returns and residual returns on the same dates and in the same stock order. The third keeps that order for the next 252 sessions. A block in the same place in the last two panels means the group still moves together.
{: #stock-correlations }

<div id="figure-1" class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/matrix" mobile="/assets/residual-risk/matrix_mobile" version="4" alt="Raw returns, formation residuals, and the following year's residuals for the same 850 stocks. Average correlation falls from about 25% to near zero after removing factors. Positive residual blocks weaken but remain visible in the following year." %}
  <p class="figure-caption"><span class="caption-number">Figure 1.</span> <span class="caption-title">Stock correlations before and after factor removal.</span> The same 850 stocks and December 2021 groups appear in all three panels. Tile colours saturate at ±40%. This cohort had the strongest forward gap.</p>
</div>

After removing the factors, average correlation fell from about 25% to near zero. Look within the blocks, though. Stocks in the same group were still about 8.5 correlation points more correlated than stocks in different groups. The difference was about 5 points in the next 252 sessions, using the same groups.

That heatmap shows the strongest year. Across all 27 formation years, the average gap was about 5 points in the year that formed the groups and about 2 points the next year. Some of that could come from having stocks from the same sectors in each group. To check, I shuffle group labels within sectors, keeping each group’s sector mix. The resulting gaps average less than half a point in the following year. In Figure 2, the dots for the original groups sit above the 95th percentile of the shuffles in all 27 years.

<div id="figure-2" class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/residuals" mobile="/assets/factor-risk-sizing/residuals_mobile" version="1" alt="Average stock correlation varies over time while average residual correlation stays near zero. Pairs in the same group were more correlated the following year than the sector-shuffle threshold in all 27 cohorts." %}
  <p class="figure-caption"><span class="caption-number">Figure 2.</span> <span class="caption-title">Residual groups one year later.</span> Dots show next-year within-group minus between-group correlation. Short marks give the 95th percentile after shuffling labels within sectors.</p>
</div>

Most of the persistence was within sectors. In the 23 development cohorts the forward gap was about 8 points for same-sector pairs and less than 1 point for cross-sector pairs matched on industry mix. The cross-sector gap was positive in all 23 cohorts.

## The shared directions persist at a smaller scale

A and B belong together in our example, but look back at their four days. On day 1, their standardized residuals are 1 and 1.4. Adding gives 2.4, and subtracting gives −0.4. On day 2 the residuals are −1 and 0.2. The sum is −0.8 and the difference is −1.2. The sum picks up what they do together. The difference picks up how far they move apart.

Let $$z_A$$, $$z_B$$ and $$z_C$$ be the three columns of standardized residuals. Give each series weights whose squares sum to one so their variances can be compared with C on its own. Since A and B each have standardized variance one and correlation 0.6, the three combinations have these variances.

- A and B together give $$(z_A+z_B)/\sqrt{2}$$, with variance $$(1+1+2(0.6))/2=1.6$$.
- A against B gives $$(z_A-z_B)/\sqrt{2}$$, with variance $$(1+1-2(0.6))/2=0.4$$.
- C alone gives $$z_C$$, with variance 1 and zero correlation with either combination.

Principal component analysis (PCA) searches over these kinds of combinations. A **direction** $$q$$ is a set of weights on the standardized residuals. Its daily series is $$Zq$$ and its variance is $$q^\top S q$$. The first principal component finds the unit-length direction with the largest variance. Here that’s the common A–B move, $$q=(1,1,0)^\top/\sqrt{2}$$, with variance 1.6. The three combinations above are the three principal components in this example. In a typical weekly fit on the real residual data, the first component explained about 3% of standardized residual variance.

To see which move reaches the portfolio, multiply each position weight by its stock’s residual volatility. For the spread, $$Dw=(1,-1,0)^\top$$. The spread’s centered residual return is therefore $$z_A-z_B$$ in percentage points. The largest component, the one that moves A and B together, cancels. The spread has $$\sqrt{2}$$ times the exposure of the unit-length opposing direction, so its residual variance is $$0.4(\sqrt{2})^2=0.8$$. Add one unit from momentum and the total is back to 1.8. In general a component with variance $$\lambda$$ contributes $$\lambda(q^\top Dw)^2$$ to the portfolio’s residual variance.

The first direction will look strong in the window that chose it. The test is to hold its weights fixed and ask how much variance that same direction has over the next 252 sessions. I use stocks observed in both windows and standardize each window by its own stock volatilities so the comparison tracks changes in co-movement.

<div id="figure-3" class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/directions" mobile="/assets/residual-risk/directions_mobile" version="2" alt="PCA directions lose variance after formation but retain more than shuffled directions with the same industry composition. Development PCs two through five fall from 14.30 to 4.36 versus 1.64 for the shuffle." %}
  <p class="figure-caption"><span class="caption-number">Figure 3.</span> <span class="caption-title">Principal directions after formation.</span> Compare formation, following-year and industry-shuffled variances on the same doubling scale. One is the reference for uncorrelated residuals. Cohorts have equal weight.</p>
</div>

In development, components two through five fell from about 14 units of variance per direction to about 4 the following year. That was still above the industry shuffle, which came in below 2. The four later cohorts showed the same pattern.

## Putting a residual correlation into the portfolio

The earlier comparisons show some shared residual moves persist into
the next year. To test whether using them improves risk forecasts, I
vary the residual correlation matrix $$R$$ while keeping the named
factors and specific volatilities fixed. The baseline uses $$R=I$$,
which gives no credit for an offset between residuals. The other
estimates start from the trailing 252-session residual correlations.

For a principal direction $$q$$ with variance $$\lambda$$, its contribution is the matrix $$\lambda qq^\top$$. Let $$L$$ be the sum over the directions I keep. In the formulas below, $$\operatorname{diag}(U)$$ means a matrix with only the diagonal entries of $$U$$.

- Shrink toward zero. For the trailing residual correlation matrix $$S$$, use $$R=(1-\alpha)S+\alpha I$$, with the weight estimated by Ledoit–Wolf shrinkage. This pulls pairwise residual correlations toward zero while preserving each stock’s specific variance.
- Keep one principal component. Keep its contribution $$L$$ to residual correlation and return the remaining variance to each stock’s diagonal, giving $$R=L+\operatorname{diag}(S-L)$$.
- Combine them. Keep one or five components in $$L$$, shrink the leftover matrix $$U=S-L$$ toward its diagonal and add $$L$$ back once. This gives $$R=L+(1-\delta)U+\delta\operatorname{diag}(U)$$ and keeps the diagonal at one.

Return to A and B. The sample correlation of 0.6 comes from two pieces. The direction that moves them together contributes $$1.6(1/\sqrt{2})(1/\sqrt{2})=0.8$$. The direction that moves them apart contributes −0.2. Keep just the common component and the A–B correlation rises to 0.8. Each stock’s volatility stays at 2% because the remaining variance goes back on the diagonal. That gives the short more credit as a hedge and brings the spread’s variance down to 1.4. Keeping fewer components can make the hedge estimate more aggressive.

Every year I compared each forecast with the same pairs’ correlations over the next 252 sessions. I use root mean squared error so large misses count for more, and the result stays in correlation points. Each cohort gets equal weight. For pairs in the same sector and group, carrying the trailing correlation forward reduced development error from about 17 to 12 correlation points against a forecast of zero. For pairs in different sectors and groups, predicting zero or using ordinary shrinkage gave errors of around 8 points, and keeping five components pushed the error higher. An individual cross-sector hedge can be sensitive to a miss of that size.

<div id="figure-4" class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/pair-errors" mobile="/assets/residual-risk/pair-errors_mobile" version="1" alt="Changes in next-year pair correlation error versus forecasting zero. All estimators improved on zero for stocks in the same sector and cluster. The cross-sector, different-cluster forecasts increased error in both periods." %}
  <p class="figure-caption"><span class="caption-number">Figure 4.</span> <span class="caption-title">Next-year correlation error by stock-pair group.</span> Negative values mean smaller errors than forecasting zero correlation. Units are correlation points. Cohorts have equal weight within each panel.</p>
</div>

## Keeping five components overstated their forward risk

In development the five-component estimate assigned about 15 units of variance per direction to components two through five. The following year delivered about 4, close to the ordinary-shrinkage forecast. Ordinary shrinkage also had lower forecast loss for that band in all 27 cohorts.

The three stocks show how this can happen. Take out the common A–B component, and each stock has 0.2 of standardized variance left. Their covariance in that remainder is −0.2. Along the common direction, the residual variances contribute +0.2 and the remaining covariance contributes −0.2, so the remainder adds up to zero in that direction. Shrink the remaining covariance halfway toward zero and the offset falls to −0.1. The remainder now puts 0.1 of variance back into the common direction. Add the retained component’s 1.6 and the forecast for that direction is 1.7.

In general, a retained unit direction $$q$$ starts with $$q^\top Uq=0$$ in the remainder. Shrinking its off-diagonal terms gives the forecast

$$
q^\top Rq=\lambda+\delta\,q^\top\operatorname{diag}(U)q.
$$

On the filled books, dropping residual correlations moved the factor target’s later volatility forecasts by less than a tenth of a percentage point on either set of holdings. Each covariance enters portfolio variance multiplied by the two signed weights. Contributions can cancel across the long and short sides even when individual residual correlations are material.

## What changed in the long/short book

In the replay, the residual estimate can change which stocks the optimizer holds. I keep the Ridge scores, trading penalty and [limits from Part 1]({% link _posts/2026-11-20-factor-risk-sizing.md %}#the-objective-and-constraints) fixed, including the 3.5% absolute target weight per stock. I compare what the resulting portfolios delivered after fees.

<table id="table-1" class="research-table comparison-table compact-table">
  <caption><span class="caption-number">Table 1.</span> <span class="caption-title">Portfolios across residual risk estimates.</span> Annual results after fees. The residual methods share factors and specific volatilities. Stock shrinkage is the stock-level reference.</caption>
  <thead><tr><th>Risk estimate</th><th>Net return</th><th>Volatility</th><th>Sharpe</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="4">January 1999 – December 2021</th></tr>
    <tr><th scope="row">Diagonal residuals</th><td>7.93%</td><td>8.12%</td><td>0.98</td></tr>
    <tr><th scope="row">One residual PC</th><td>7.94%</td><td>8.02%</td><td>0.99</td></tr>
    <tr><th scope="row">Residual shrinkage</th><td>7.89%</td><td>7.89%</td><td>1.00</td></tr>
    <tr><th scope="row">One PC + shrinkage</th><td>7.89%</td><td>7.86%</td><td>1.00</td></tr>
    <tr><th scope="row">Five PCs + shrinkage</th><td>7.89%</td><td>7.83%</td><td>1.01</td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>10.78%</td><td>8.73%</td><td>1.22</td></tr>
    <tr class="period-heading"><th colspan="4">January 2022 – May 2026</th></tr>
    <tr><th scope="row">Diagonal residuals</th><td>2.70%</td><td>8.28%</td><td>0.36</td></tr>
    <tr><th scope="row">One residual PC</th><td>3.03%</td><td>8.24%</td><td>0.40</td></tr>
    <tr><th scope="row">Residual shrinkage</th><td>3.96%</td><td>8.04%</td><td>0.52</td></tr>
    <tr><th scope="row">One PC + shrinkage</th><td>3.90%</td><td>8.06%</td><td>0.52</td></tr>
    <tr><th scope="row">Five PCs + shrinkage</th><td>3.98%</td><td>7.99%</td><td>0.53</td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>7.45%</td><td>9.65%</td><td>0.79</td></tr>
  </tbody>
</table>

Ordinary residual shrinkage improved on diagonal residuals in the later sample. Annual return after fees went from 2.7% to 4.0%, with a modest drop in volatility. In development it also lowered volatility, with a small decline in return. Adding five components barely moved later net Sharpe, and the paired interval allowed small gains or losses.

The groups tell me where to look for residual co-movement. The next-year tests tell me how much of it to carry into the forecast. The estimates weakened after formation, especially across sectors, and keeping five fitted directions at full strength overstated their forward risk. In a long/short book, the sign of each position determines which of those relationships actually matters for total risk.

## References

- Letchford, Adrian (2025). “[Statistical Factor Modeling](https://osquant.com/papers/2025/statistical-factor-modelling/).” OSQuant.
