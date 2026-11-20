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

## The model placed NVIDIA and Vertiv in different groups
{: #would-the-model-have-grouped-nvidia-and-vertiv}

There was an economic link I could have known about before the January 2025 selloff in AI infrastructure stocks. Vertiv and NVIDIA had already published a design for powering and cooling NVIDIA-based data centers. I compared them with another technology firm, Workday, whose HR software NVIDIA used. [Vertiv’s October 2024 announcement](https://www.vertiv.com/en-emea/about/news-and-events/news-releases/vertiv-codevelops-with-nvidia-complete-power-and-cooling-blueprint-for--nvidia-gb200-nvl72-platform/) · [Workday’s customer study](https://forms.workday.com/content/dam/web/en-us/documents/ebooks/power-of-skills-insights-customer-success-story-global-enus.pdf)

Over the 252 trading sessions ending Friday, January 24, 2025, NVIDIA’s stock-return correlation was **0.65 with Vertiv** and **0.16 with Workday**. After the market, sector and style returns came out, those correlations were **0.14 and −0.10**. Yet the groups frozen in December had put all three firms in different clusters. A stock gets only one cluster label. A relationship with a particular customer can matter even when other relationships dominate the grouping.

The following Monday, January 27, U.S. investors repriced AI infrastructure stocks after DeepSeek’s model release. NVIDIA fell 16.97%, Vertiv fell 29.88% and Workday rose 2.29%. Imagine carrying $100 long NVIDIA into that close with $100 short in one of the other two stocks. The Vertiv short gained enough to cover the NVIDIA loss and leave **$12.91**. The Workday short added to the loss, leaving the pair down **$19.26**. Those are close-to-close price changes in dollars on $200 gross, before fees. I picked this episode knowing about the selloff. [NYSE’s account on January 27](https://www.ice.com/insights/conversations/inside-the-ice-house/market-storylines/01-27-2025)

Did I actually hold either hedge? I checked the settled shares in all six Ridge portfolios across their three trading schedules. **None of the 18 accounts held NVIDIA, Vertiv or Workday entering January 27.** Their direct contribution to the day’s P&L was zero. The calibrated stock-shrinkage book gained 0.64% from its other holdings and the calibrated factor-target book gained 1.18%, both before fees and averaged across their three schedules. Other holdings could still have been sensitive to AI spending. Identifying that exposure would take the same business-by-business work as the example above.

Would the price history have pointed me toward the cooling business? At the ends of **2021 and 2022**, NVIDIA’s stock returns were actually more correlated with Workday’s than with Vertiv’s. Removing the market, sector and style moves reversed that ordering in both years. The remaining relationship with Vertiv was also variable. Across the four year-ends before the selloff, its residual correlation ranged from **−0.03 to +0.21**. In 2022 both pairs had negative residual correlations.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/company-pairs" mobile="/assets/residual-risk/company-pairs_mobile" version="1" alt="NVIDIA’s correlations with Vertiv and Workday at five year-ends. Workday had the higher raw correlation in 2021 and 2022. Vertiv had the higher residual correlation at all five year-ends." %}
</div>
<p class="figure-caption">Each dot uses the last 252 trading sessions at that year-end. Read across a row to see what changes when the broad factors are removed. The 2025 row includes the January selloff and could only have been known afterward. <a href="/assets/residual-risk/nvidia-pair-correlations.csv">Download the correlations and exact window dates (CSV).</a></p>

I would use the business link to ask where two positions could lose on the same news. To decide whether residual relationships are reliable enough to change portfolio weights, I would test that idea on stocks I had no particular reason to pick.

## The shared directions persist at a smaller scale

A cluster puts each stock in one group. Principal component analysis lets each stock load by different amounts, and with either sign, on several shared directions. I standardized each stock’s residuals over the formation year and found the weighted combinations with the greatest variance. I froze those directions and measured them over the following year. For the stocks still observable, I restored unit length and orthogonality in their original order. I used the forward year’s own stock volatilities when measuring forward correlation. This test asks whether co-movement persists after stripping out changes in each stock’s volatility.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/directions" mobile="/assets/residual-risk/directions_mobile" version="2" alt="PCA directions lose variance after formation but retain more than shuffled directions with the same industry composition. Development PCs two through five fall from 14.30 to 4.36 versus 1.64 for the shuffle." %}
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

MSCI gives a practical reason to relax that assumption. Two share classes of the same issuer can respond to the same company news after the market and industry moves come out. MSCI calls the correlation it assigns to such securities *linked specific risk*. In its Japan trading model, it also estimates specific correlations for selected pairs of **different** issuers. It uses company information to identify peers and their historical residual returns to estimate the correlations. I use the stock returns left over after fitting my factors to estimate these remaining links. [MSCI Japan Investment Risk Summit, slides 5–7](https://www.msci.com/downloads/web/msci-com/discover-msci/events/event-assets/2025/november/2025-japan-investment-risk-summit/MSCI%20Japan%20Investment%20Risk%20Summit_November%2013%2C%202025.pdf#page=5)

Paleologo treats these as two different modeling choices in the published *Elements*. Sections 6.4.4–6.4.5 discuss clustering and shrinking the unexplained stock covariances after a fundamental factor fit. Chapter 7 examines how to estimate and interpret statistical factors. Here the ordering matters. I first remove the market, sectors and styles, then apply PCA or shrinkage to what remains. [Paleologo, *The Elements of Quantitative Investing*](https://www.wiley.com/en-us/shop/general-finance-investments/the-elements-of-quantitative-investing-p-9781394265466)

For the PCA version, let $$S$$ be the prior year’s sample residual correlation matrix. For each of its first $$k$$ unit eigenvectors $$q_j$$ and eigenvalues $$\lambda_j$$, keep the component $$\lambda_j q_j q_j^\top$$. Their sum is $$L$$. Setting $$R=L+\operatorname{diag}(S-L)$$ gives common residual risk through those directions and returns the unused variance to each stock. In factor language the extra stock loadings are $$D q_j\sqrt{\lambda_j}$$ on unit-variance factors. Each retained direction already uses part of the stock’s specific variance. Keeping the entire old diagonal alongside it would count that part twice.

For residual shrinkage, I used $$R=(1-\alpha)S+\alpha I$$, estimating the weight from the trailing standardized observations. With more stocks than days, the sample correlation has directions of zero estimated variance. Shrinkage raises those low estimates and pulls down the large ones. It can therefore both reduce the risk assigned to a concentrated theme and raise the risk assigned to a supposed hedge. [Ledoit and Wolf, *A well-conditioned estimator for large-dimensional covariance matrices*](https://www.ledoit.net/Well-conditioned2004.pdf)

To combine the two, I estimated a shrinkage weight $$\delta$$ on the standardized residuals remaining after the retained PCs. Writing $$U=S-L$$, the resulting correlation is

$$
R=L+(1-\delta)U+\delta\operatorname{diag}(U).
$$

At zero shrinkage I recover the original sample correlation. At full shrinkage I retain the common PCs and each stock’s remaining diagonal variance. This preserves a diagonal of one throughout. Stocks without the full trailing history retain their named factors and specific variances. In the portfolio test the extra residual covariance applies only to pairs for which it could have been estimated at the time.

What would each forecast have told me about NVIDIA and Vertiv at the end of 2024? Their trailing residual correlation was **0.133**. Ordinary shrinkage took it down to **0.041**. Preserving five PCs and shrinking the remainder kept **0.104**. Their realized residual correlation over the next 252 sessions was **0.247**. The plain trailing estimate came closest for this pair. For NVIDIA and Workday, ordinary shrinkage came closest. I already knew the January selloff when I picked the companies, so I wanted to see whether the lesson carried over to all the other pairs.

At each of 27 year-ends I compared each forecast with the same pair’s correlation in the following 252 sessions. I squared each error, averaged across pairs and then across years, and took the square root. For example, forecasting zero when the measured correlation is 0.10 gives an error of ten correlation points. A year with more eligible stocks has the same influence as any other year.

For stocks in **different sectors and different clusters**, predicting zero gave an error of **7.65 correlation points** over the 23 development cohorts. Ordinary shrinkage gave **7.73**, and preserving five PCs gave **8.50**. Zero beat both in every one of those years and in the four later cohorts too. The forecasts still tended to point the right way in aggregate. Their magnitudes were large enough to wipe out that advantage. For stocks in the **same sector and same group**, zero had an error of **16.88 points** in development and the trailing sample had **12.03**. Where the firms sat in the model made a difference to how much of their past co-movement I could carry forward.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/residual-risk/pair-errors" mobile="/assets/residual-risk/pair-errors_mobile" version="1" alt="Changes in next-year pair correlation error versus forecasting zero. All estimators improved on zero for stocks in the same sector and cluster. The cross-sector, different-cluster forecasts increased error in both periods." %}
  <p class="figure-caption">Left of zero means the model estimated the next year’s pair correlations more accurately than predicting zero for every pair. One unit is 0.01 of correlation. The 23 development cohorts and four later cohorts each receive equal weight within their period. The same stock may enter many pairs.</p>
</div>

I checked whether multiple securities from the same company explained my results. The issuer file linked 17 distinct pairs, observed a total of 93 times across the year-end cohorts. Their next-year residual correlation averaged **0.92** in both periods, and every pair fell in the same sector and the same frozen group. Removing them barely changed the broader comparison. Among securities of different issuers, shrinking residual correlations reduced mean squared forecast error against zero by **2.56%** in development and **7.69%** later. The issuer file is a later snapshot, so this is a check on the historical result.

## Keeping five components overstated their forward risk

There is a subtlety in “keeping” a component. On the full formation sample, a retained eigenvector $$q$$ with eigenvalue $$\lambda$$ satisfies $$Uq=0$$. After shrinking the remainder toward its own diagonal, the forecast variance along that same vector is

$$
q^\top Rq = \lambda + \delta\sum_i q_i^2 U_{ii}.
$$

The estimator keeps the component’s covariance and every stock’s original variance. Removing some of the remainder’s off-diagonal terms also removes some offsets along $$q$$. The forecast variance in that direction can therefore exceed its fitted eigenvalue.

For components two through five in development, the five-component model forecast **14.96** units of variance per direction. The following year delivered **4.36**. Ordinary residual shrinkage forecast **3.95**. In the four later cohorts the comparison was **19.25** for five components and **8.26** for ordinary shrinkage, against **7.34** realized. For each cohort I scored forecast variance $$v$$ against realized variance $$u$$ with $$\log v + u/v$$. Lower is better, and ordinary shrinkage had the lower loss in all 27 comparisons for this band. These are forecasts for particular combinations of standardized stock residuals. To see how much they mattered in dollars, I needed to trade the portfolio.

How much did those residual links matter in the positions I actually held? I kept all the named factors, stock volatilities and historical stock correlations in the factor target. On its own later holdings, removing only the residual correlations from its factor-based half moved the annualized risk forecast from **7.00% to 6.98%**. The same operation on the stock-shrinkage holdings moved it from **9.95% to 9.86%**. Which pairs are long together and which sit on opposite sides makes a difference. On 66 of the 227 later decisions, the residual correlations actually *reduced* the factor-target portfolio’s estimated variance.

Could I improve the estimate by keeping residual correlations only between stocks in the same frozen group? A stock outside the groups kept its own specific variance. On the factor-target book in the later period, this put the annualized forecast at **6.99%**, between 6.98% with diagonal residuals and 7.00% with all the shrunk residual correlations. I also let the model choose its hedges on the same 150 stocks and at the same exposure to the Ridge forecast. Development volatility edged down from **3.040% to 3.033%**. Later it edged up from **3.549% to 3.558%**. The paired intervals included zero in both periods, as they did for 75 and 100 stocks after accounting for the three breadths. I would use the group map to investigate exposures and keep ordinary residual shrinkage for sizing.

I also tried using the differences between pairs directly. I kept the full trailing residual correlation if two stocks shared both their sector and their frozen group, used ordinary shrinkage for other pairs within a sector, and set the residual correlation to zero across sectors. The named factors and the empirical half of the stock covariance still connected sectors. This gave a later risk forecast of **7.41%** on the factor target’s unchanged holdings, against **7.39%** with ordinary residual shrinkage and **7.28%** realized, after applying the same prior calibration. The new rule slightly improved the development forecast score on both books, but both intervals included zero. Its score worsened on the factor target’s later holdings. I stopped at the forecast test. Improving the estimate for some stock pairs had little effect once their actual portfolio weights and hedges entered the calculation.

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
