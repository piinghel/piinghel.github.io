---
layout: post
interactive_charts: true
toc: false
title: "Factor Risk Models, Part 1: An Introduction"
description: "How factor exposures become portfolio risk, and what changes in hedges and position sizing when the Ridge forecasts stay fixed."
date: 2026-11-20
last_modified_at: 2026-11-21
categories: ["Portfolio construction"]
article_label: Factor risk · Part 1 of 2
series_id: factor-risk
series_order: 1
permalink: /quants/factor-risk-sizing.html
---

Suppose I’m long a chipmaker and want to hedge it. I could short another chipmaker or a stock from a different sector. Both shorts could offset the same amount of broad market risk. A short in another chipmaker could also protect the spread in a semiconductor selloff. How can I tell which risks the hedge takes out and which ones it leaves in?

A factor risk model starts with the moves that several stocks can share, such as a market decline or a sector selloff. It uses those shared moves and the risk left over in each stock to estimate how volatile the whole portfolio might be. That estimate helps determine both which stocks hedge one another and how much of the resulting spread fits inside a risk budget.

I use the Ridge forecasts as a worked example and keep them fixed. First I test which covariance estimates find quieter hedges on the same stocks. Then I compare risk forecasts on identical holdings. Finally I let each estimate change the positions under the same risk budget and check what happens to exposure, realized volatility and returns after fees.

## From stock exposures to portfolio risk

### A three-stock example

Take three stocks, A, B and C, and start with two factors. The market factor captures a move common to all three. The momentum factor captures a move associated with recent winners and losers. I assign A a momentum exposure of +1 because it has been a winner, B an exposure of −1 because it has been a loser, and C an exposure of zero. Each stock has a market exposure of one in this example.

{% assign example = site.data.factor_risk_example %}
<div class="matrix-calculation" role="group" aria-label="Market and momentum exposures for stocks A, B and C">
  {% include worked-matrix.html matrix=example.exposures symbol="B" label="Stock exposures" %}
</div>

An exposure tells me how much of a factor move a stock picks up. If momentum returns +1% on a given day, it contributes +1 percentage point to A, −1 to B and zero to C. The exposures come from information I have before the session. The factor return is the size and direction of the shared move during the session, which I estimate after seeing the stock returns.

### One day gives one set of factor returns

Say A falls 4.5%, B falls 0.5%, and C falls 4%. With equal weight on each of the three observations, the fit puts the common market move at −3%, the average of the three returns. A and B differ by four percentage points in return and by two units in momentum exposure. With the same market exposure for both, the fit attributes that difference to a momentum return of −2% per unit of exposure. C has zero momentum exposure, so it helps estimate the market move and contributes no information about the momentum slope.

The factors explain −5% for A, from −3% on the market and −2% on momentum. A actually fell 4.5%, so its residual return is +0.5 percentage points. B’s residual is also +0.5 points, and C’s is −1 point. A residual is what the fitted factors leave unexplained for that stock on that day.

Stack the stocks into a vector and the same calculation becomes

$$
r_t = B_{t-1} f_t + \epsilon_t.
$$

Here $$r_t$$ contains the stock returns, $$B_{t-1}$$ the exposures known the previous close, $$f_t$$ the factor returns fitted that day and $$\epsilon_t$$ the stock residuals. I repeat the regression across stocks each day to build a history of factor returns and residuals. In the Russell 1000 fit I weight each observation by the square root of prior market cap. I give all stocks a market exposure of one and center the sector returns under those weights to separate sector moves from the market term.

### A long and a short can cancel one exposure

Put 50% of capital long A and 50% short B, with nothing in C. A market move affects the two stocks equally. The gains and losses from that move cancel in the spread because one stock is long and the other is short. Momentum goes the other way. The long is a recent winner, and shorting a recent loser adds to the same momentum exposure.

With signed weights $$w=(0.5,-0.5,0)^\top$$, the portfolio exposures are $$b=B^\top w$$. The market exposure is $$0.5(1)-0.5(1)=0$$ and the momentum exposure is $$0.5(1)-0.5(-1)=1$$. On the day above, the factor contribution $$b^\top f_t$$ is therefore −2%. The two +0.5-point residuals also cancel. Their equality comes from the way momentum is fitted in this three-stock example. When I fit the factors across a larger universe, A and B can have different residuals and the spread can move even when momentum is flat.

### A history of daily moves gives a risk estimate

That −2% explains one day. To estimate risk going forward, I keep the latest exposures fixed and use the history of fitted factor returns to estimate how much the factors vary and how they move together. Call their covariance matrix $$F$$. For the example, give the market a daily volatility of 2% and momentum a daily volatility of 1%, and assume the two factor returns are uncorrelated. Their variances are 4 and 1 in squared percentage points. The fitted model uses a full $$F$$, so a tendency for factors to rise or fall together also enters the risk estimate.

The spread picks up the full momentum move and zero of the market move, so its factor variance is 1. For the residual calculation, think of A, B and C as three names in the larger fit. Suppose they have residual volatilities of 2%, 2% and 1%. For now assume these residuals are uncorrelated across stocks. At half weight, each of A and B contributes $$0.5^2\times 2^2=1$$ unit of residual variance. The spread has three units of daily variance in total, or about 1.73% daily volatility.

In matrix form, $$\Omega$$ is the covariance of the stock residuals. The assumption of zero residual correlations makes $$\Omega$$ diagonal. If factor returns and residuals are uncorrelated, portfolio variance is the sum of the two contributions we just calculated.

$$
w^\top\Sigma w = b^\top F b + w^\top\Omega w.
$$

### The factors imply a covariance for each stock pair

The same model gives a covariance matrix $$\Sigma$$ for all the stocks. Its diagonal entries are stock variances. The other entries measure how each pair moves together. For A and B, the market contributes +4 to their covariance because both stocks carry the same market exposure. Momentum contributes −1 because their exposures have opposite signs. Their factor covariance is therefore 3. The pair tends to move together under these assumptions because the market effect is larger.

To calculate all the pairs at once, start with $$BF$$. In the example, multiplying by the diagonal $$F$$ scales the market exposures by 4 and the momentum exposures by 1. A’s row becomes $$(4,1)$$.

<div class="matrix-calculation" role="group" aria-label="Stock exposures multiplied by factor covariance">
  <div class="matrix-product">
    {% include worked-matrix.html matrix=example.exposures symbol="B" label="Stock exposures" %}
    <span class="matrix-operator" aria-hidden="true">×</span>
    {% include worked-matrix.html matrix=example.factor_covariance symbol="F" label="Factor covariance" %}
  </div>
</div>

Then multiply by $$B^\top$$, where each stock’s exposures are now a column. A’s scaled row times B’s column gives the same covariance as before, $$4(1)+1(-1)=3$$.

<div class="matrix-calculation" role="group" aria-label="Scaled exposures times transposed exposures equals stock covariance from factors">
  <div class="matrix-product">
    {% include worked-matrix.html matrix=example.scaled_exposures symbol="BF" label="Scaled exposures" mark_row="A" %}
    <span class="matrix-operator" aria-hidden="true">×</span>
    {% include worked-matrix.html matrix=example.transposed_exposures symbol="Bᵀ" label="Transposed exposures" mark_column="B" %}
  </div>
  <div>
    <span class="matrix-operator" aria-hidden="true">=</span>
    {% include worked-matrix.html matrix=example.factor_stock_covariance symbol="BFBᵀ" label="Stock covariance from factors" mark_row="A" mark_column="B" %}
  </div>
</div>

Finally, add the residual covariance to get $$\Sigma=BFB^\top+\Omega$$. With zero residual correlations, this adds 4, 4 and 1 to the stock variances and leaves the A–B covariance at 3.

<div class="matrix-calculation" role="group" aria-label="Total stock covariance with a diagonal residual model">
  {% include worked-matrix.html matrix=example.total_stock_covariance symbol="Σ" label="Total stock covariance" mark_row="A" mark_column="B" %}
</div>

With half the capital long A and half short B, each stock variance is multiplied by $$0.5^2$$. The two covariance entries are multiplied by the product of the long and short weights, which is negative. This gives the same spread variance as summing the factor and residual contributions.

$$
w^\top\Sigma w=\frac{9+9-2(3)}{4}=3.
$$

There are 499,500 distinct pairs in a universe of 1,000 stocks. With diagonal residuals, the model estimates their co-movement through the much smaller factor covariance matrix. That simplification matters when the factors leave a shared move behind. If the model leaves some momentum effects in the residuals, a diagonal $$\Omega$$ omits the covariance they create between stocks. [Part 2]({% link _posts/2026-11-20-residual-risk.md %}) asks whether estimating some of that residual co-movement improves the hedge.
{: #the-average-residual-hides-groups}

### The factors in this study

The market intercept and sector indicators capture broad moves. The seven styles describe how stocks within and across sectors can still move together.

- Momentum and short-term return describe price behavior over different horizons. Momentum blends 12–1 return with a moving-average trend measure. Short-term return measures the last month.
- Beta and residual volatility separate sensitivity to the Russell 1000 from the volatility left after fitting that index alone. Residual volatility is a stock characteristic here. The specific variance in $$\Omega$$ comes from the full factor fit.
- Size, liquidity and short interest capture differences in market capitalization, trading volume relative to capitalization, and the share of stock sold short. They describe different ways stocks can react together when investors trade or unwind positions.

A characteristic can help explain co-movement even when the return forecast omits it.

## What goes into a position

So far I’ve held the weights fixed and estimated their risk. To choose new weights, I also need a score for each stock and limits on how much the portfolio can hold and trade.

The Ridge target is the stock’s rank within its sector on forward return per unit of risk. I turn each Ridge score $$s_i$$ into a sizing input $$\mu_i=s_i\widehat\sigma_i$$, using the stock’s trailing 21-session daily volatility $$\widehat\sigma_i$$. This is a return-like score for sizing. All three joint rules use the same scores, so the comparison varies how they estimate risk.

At rebalance, new longs come from the top 75 scores in the Russell 1000 universe and new shorts from the bottom 75. Existing positions can stay eligible beyond the entry cutoff, so a small rank change needn’t trigger a round trip.

To see what modeling co-movement adds, I compare a stock-by-stock sizing rule with three joint rules that use different covariance estimates.

- Volatility scaling starts with equal weights on each side and multiplies each by 20% divided by its trailing 60-session annualized volatility, with a 5% volatility floor. A 40%-volatility stock starts at half its equal weight. Each sleeve is capped at one dollar per dollar of capital.
- Stock shrinkage halves pairwise correlations estimated over 756 sessions. Stock volatilities use 21 sessions and the reference backtest’s fixed risk adjustment.
- Sector and style factors use $$\Sigma=BFB^\top+\Omega$$ with a diagonal $$\Omega$$.
- Factor target keeps the stock-shrinkage volatilities and averages the historical correlations with factor-based correlations that include shrunk residual co-movement.

Suppose two stocks have a historical correlation of 0.40 and a factor-based estimate of 0.30. The word *target* means the value I move the historical estimate toward. Stock shrinkage goes halfway from 0.40 to zero and uses 0.20. Factor target goes halfway from the original 0.40 to 0.30 and uses 0.35. If I short both stocks, 0.35 assigns more risk to a rally that hurts both shorts. If I go long one and short the other, 0.35 gives the pair more credit as a hedge.

Written as a correlation estimate, both methods take the weighted average

$$
\widehat R=(1-\lambda)R_{\rm sample}+\lambda R_{\rm target}.
$$

Here $$\lambda=1/2$$. A factor target can preserve a shared sector or style move when a pair’s own estimate is unreliable. It also passes along errors in the factor model.

### The objective and constraints

At each rebalance the three joint optimizers maximize the portfolio’s sizing score after a turnover penalty. Each uses the same limits and prices portfolio risk with its own covariance estimate.

$$
\begin{aligned}
\max_w\quad & \mu^\top w - c\lVert w-w_{\rm prev}\rVert_1 \\
\text{subject to}\quad & A\,w^\top\Sigma w \le \sigma_{\rm target}^2 \\
& \lVert w\rVert_1 \le G_{\max},\quad |\mathbf{1}^\top w| \le N_{\max} \\
& |\beta^\top w| \le \beta_{\max} \\
& |w_i| \le w_{\max} \quad \text{for each stock }i \\
& |a_g^\top w| \le S_{\max} \quad \text{for each sector }g \\
& \lVert w_{g\cap\ell}\rVert_1 \le q_{\max}\lVert w_\ell\rVert_1
  \quad \text{for each sector }g\text{ and sleeve }\ell.
\end{aligned}
$$

Here $$w$$ gives the signed target weights and $$w_{\rm prev}$$ the weights held at rebalance. Eligible longs have nonnegative weights, eligible shorts have nonpositive weights, and other weights are zero. The rate $$c$$ is 2.5 basis points per unit of two-way turnover, the sum of absolute weight changes. Trading fees apply separately to fills.

<table class="research-table constraint-settings" id="table-1">
  <caption><span class="caption-number">Table 1.</span> <span class="caption-title">Optimizer settings.</span></caption>
  <thead><tr><th scope="col">Parameter</th><th scope="col">Setting</th></tr></thead>
  <tbody>
    <tr><th scope="row">Sessions per year <var>A</var></th><td>252</td></tr>
    <tr><th scope="row">Annual forecast volatility <var>σ<sub>target</sub></var></th><td>7%</td></tr>
    <tr><th scope="row">Gross exposure, longs plus absolute shorts <var>G<sub>max</sub></var></th><td>200%</td></tr>
    <tr><th scope="row">Absolute net exposure <var>N<sub>max</sub></var></th><td>25%</td></tr>
    <tr><th scope="row">Absolute Russell 1000 beta <var>β<sub>max</sub></var></th><td>0.05</td></tr>
    <tr><th scope="row">Absolute weight per stock <var>w<sub>max</sub></var></th><td>4%</td></tr>
    <tr><th scope="row">Absolute net exposure per sector <var>S<sub>max</sub></var></th><td>20%</td></tr>
    <tr><th scope="row">Share of either sleeve in one sector <var>q<sub>max</sub></var></th><td>30%</td></tr>
  </tbody>
</table>

These constraints address different risks. A 3% long with beta 1.4 and a 3% short with beta 0.8 add zero net exposure and 0.018 of market beta. The volatility constraint also captures how sector and style exposures combine. If two estimates price the same positions differently, the same volatility target can support different amounts of gross exposure.

For the replay, I stagger the starting week across three schedules to see how sensitive the results are to when the book trades. Each rebalances every three weeks against $5 million. All four rules trade from filled holdings, with next-close execution and a 10% cap on participation in average daily dollar volume for ordinary fills. From 2011 I charge 5 bp on long trades and 7.5 bp on short trades, with higher rates earlier.

The portfolio comparisons use 5,773 common sessions from 26 January 1999 through 31 December 2021 and 1,103 from 3 January 2022 through 27 May 2026. The later period includes history I had already seen in related research.

## Comparing the hedges on the same stocks

I give stock shrinkage and two factor estimates the same sampled stocks. One factor estimate uses diagonal residuals and the other shrinks their correlations. Each minimizes $$w^\top\Sigma w$$ while holding $$w^\top s$$ at the equal-weight spread’s Ridge score. The long and short sides each use 50% of capital, and each name stays between one-quarter and three times its side’s equal weight. Multiplying the whole covariance matrix by a positive constant gives the same solution. This test isolates how the model weighs one hedge against another.

I drew 32 groups per weekly decision at 75, 100 and 150 stocks in total and measured gross returns for the session after the next close. The stock draws vary the names on the same dates. Later 150-stock spreads fell from 3.69% to 3.53% annualized volatility when I added shrunk residual correlations to the factor model.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/stock-draws" mobile="/assets/factor-risk-sizing/stock-draws_mobile" version="1" alt="32 stock selections at each decision. Point estimates of spread volatility favor shrunk residuals at all three stock counts. The left panel compares with stock shrinkage. The right compares with diagonal residuals." %}
</div>
<p class="figure-caption"><span class="caption-number">Figure 1.</span> <span class="caption-title">Realized volatility of matched spreads.</span> Negative values favour shrunk residual correlations. The paired 95% intervals account for six comparisons per period.</p>

I also compared one session with the three-week holding period used in the portfolio replay. For the same eight stock paths and 227 later starting dates, the test assumes full fills where the next close has a quote and leaves other allocations in cash. The returns are gross. At 150 stocks, adding shrunk residuals reduced annualized 15-session volatility from 3.35% to 3.22%, a 0.13-point reduction with a simultaneous 95% interval of 0.04 to 0.21 points. Against stock shrinkage the estimate also favored shrunk residuals, but all three stock counts had intervals that crossed zero at 15 sessions.

<table class="research-table comparison-table compact-table">
  <caption><span class="caption-number">Table 2.</span> <span class="caption-title">Volatility saved by estimating residual correlations.</span> Percentage points relative to the same factor model with zero residual correlations, 2022–May 2026.</caption>
  <thead><tr><th>Total stocks</th><th>1 session</th><th>15 sessions</th></tr></thead>
  <tbody>
    <tr><th>75</th><td>0.12</td><td>0.08</td></tr>
    <tr><th>100</th><td>0.15</td><td>0.07</td></tr>
    <tr><th>150</th><td>0.16</td><td>0.13</td></tr>
  </tbody>
</table>

At three weeks the smaller spreads gave inconclusive results. The draws vary the stocks and share the same market dates.

## The same holdings reveal a gap in risk forecasts

A model can find a good hedge and still misjudge its risk. I give both models the same holdings and score their variance forecasts against the returns those holdings delivered.

I score variance forecasts with QLIKE. Let $$x=u/v$$ be the mean squared daily return divided by forecast daily variance. The loss $$x-\log x-1$$ is zero at a match. Forecast half the realized variance and the loss is about 0.31. Forecast twice the realized variance and it is about 0.19. The loss penalizes underestimation more heavily for the same multiplicative error. On identical holdings, $$\log v+u/v$$ gives the same paired comparison.

For a check without Ridge scores, I assigned the longs and shorts at random and gave names equal weights on each side. On these identical holdings, the factor target’s raw forecasts had lower QLIKE than stock shrinkage at 75, 100 and 150 names in the later period. All three paired intervals favored it. At 150 names, stock shrinkage forecast 3.6% volatility and the factor target 3.4%, against 2.7% realized. Both estimates ran high.

On the filled stock-shrinkage book, the same models forecast 7% and about 10% across 227 later cycles, against 9.6% annualized gross volatility. Absolute risk matters here because the lower forecast leaves room to take larger positions. I checked how much of the QLIKE gap came from forecast scale by rescaling each forecast with the mean ratio of realized to forecast variance over its last 52 completed cycles. Both forecasts then came out near 9.7%. Stock shrinkage had a lower QLIKE on its own holdings, and the paired intervals on the other two filled books included zero.

Calibration can help when a model consistently under- or overestimates risk on the holdings it will size. A uniform adjustment leaves the correlations intact. Here the direction of the error depended on the holdings. Stock shrinkage forecast too much risk on the random spreads and too little on the optimized book.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/fixed-book" mobile="/assets/factor-risk-sizing/fixed-book_mobile" version="1" alt="On the same stock-shrinkage holdings, the two models forecast 7% and about 10% in the later period. Calibration brings both forecasts close to the 9.6% realized gross volatility." %}
</div>
<p class="figure-caption"><span class="caption-number">Figure 2.</span> <span class="caption-title">Risk forecasts on identical holdings.</span> Circles show original forecasts, diamonds use 52 completed holding periods for calibration, and the dashed line marks realized risk.</p>

## The portfolio comparison after fees
{: #how-the-risk-estimate-changes-the-portfolio}

I now let each risk estimate choose its own positions and compare the portfolios after trading fees.

<table class="research-table comparison-table compact-table">
  <caption><span class="caption-number">Table 3.</span> <span class="caption-title">Portfolio outcomes before and after fees.</span> Three-schedule means. Returns are compounded and annualized. Return and Sharpe are net above, gross below. Volatility and drawdown use net returns. Turnover is two-way, in multiples of capital per year.</caption>
  <thead><tr><th>Sizing rule</th><th>Return</th><th>Vol.</th><th>Sharpe</th><th>Drawdown</th><th>Turnover</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="6">January 1999 – December 2021</th></tr>
    <tr><th scope="row">Volatility scaling</th><td>7.12%<span class="secondary-metric">9.34%</span></td><td>8.07%</td><td>0.89<span class="secondary-metric">1.15</span></td><td>20.07%</td><td>28.49×</td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>10.77%<span class="secondary-metric">12.91%</span></td><td>8.74%</td><td>1.21<span class="secondary-metric">1.43</span></td><td>18.52%</td><td>25.65×</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>7.95%<span class="secondary-metric">10.11%</span></td><td>8.13%</td><td>0.98<span class="secondary-metric">1.23</span></td><td>19.10%</td><td>26.49×</td></tr>
    <tr><th scope="row">Factor target</th><td>9.50%<span class="secondary-metric">11.56%</span></td><td>7.47%</td><td>1.25<span class="secondary-metric">1.50</span></td><td>15.79%</td><td>25.17×</td></tr>
    <tr class="period-heading"><th colspan="6">January 2022 – May 2026</th></tr>
    <tr><th scope="row">Volatility scaling</th><td>6.96%<span class="secondary-metric">8.47%</span></td><td>10.16%</td><td>0.71<span class="secondary-metric">0.85</span></td><td>9.41%</td><td>24.36×</td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>7.42%<span class="secondary-metric">8.66%</span></td><td>9.65%</td><td>0.79<span class="secondary-metric">0.91</span></td><td>9.84%</td><td>18.76×</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>2.72%<span class="secondary-metric">3.88%</span></td><td>8.29%</td><td>0.37<span class="secondary-metric">0.50</span></td><td>10.54%</td><td>18.28×</td></tr>
    <tr><th scope="row">Factor target</th><td>4.59%<span class="secondary-metric">5.64%</span></td><td>7.27%</td><td>0.65<span class="secondary-metric">0.79</span></td><td>7.64%</td><td>16.66×</td></tr>
  </tbody>
</table>

<div id="figure-3" class="research-figure portfolio-path-figure responsive-figure">
  {% include blog-chart.html chart="performance" source="/assets/factor-risk-sizing/performance.json" initial_wealth=1 periods_visible=true base="/assets/factor-risk-sizing/performance" mobile="/assets/factor-risk-sizing/performance_mobile" version="3" label="Growth of one dollar after fees and drawdown for the three Ridge portfolios. Choose the full history, development period, later period or custom dates." %}
</div>
<p class="figure-caption"><span class="caption-number">Figure 3.</span> <span class="caption-title">Growth and drawdown after fees.</span> Each window starts at $1 and compounds the mean daily return across three schedules. Drawdown is measured from the peak within that window.</p>

The Factor target row shows the portfolio sized with the 50/50 correlation estimate. From January 2022 through May 2026 it earned 4.59% a year after fees at 7.27% volatility, close to the 7% budget. Stock shrinkage earned 7.42% at 9.65% volatility. How much of that extra return came from holding a bigger book?

## Why the same risk budget produced different volatility

Imagine the same weights have forecast volatility of 7% under one model and 10% under another. If I keep their proportions, the second model fits the 7% budget at 70% of the original size. Volatility scales linearly with position size. The optimizer can also change the proportions if the second model sees a better hedge elsewhere. The next test separates the change in scale from the change in stock relationships.

The same 7% cap can produce a smaller book if one model forecasts more risk for a given set of positions. In the later period the factor target held $1.24 of gross exposure per dollar of capital, against $1.56 for stock shrinkage. It also had smaller drawdowns. The next comparison asks how much of the volatility gap follows the forecast level.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/realized-risk" mobile="/assets/factor-risk-sizing/realized-risk_mobile" version="1" alt="Trailing annualized volatility of the original sizing rules before the rolling calibration." %}
</div>
<p class="figure-caption"><span class="caption-number">Figure 4.</span> <span class="caption-title">Realized volatility against the 7% forecast limit.</span> Monthly observations use 252 sessions of net returns, averaged across schedules.</p>

I use the stock-shrinkage positions held at each decision close as a reference, $$w_0$$. Let $$\Sigma_s$$ and $$\Sigma_f$$ be the stock-shrinkage and factor-target covariance estimates. To give the factor target the stock model’s risk level, I use

$$
\widetilde\Sigma_f =
\frac{w_0^\top\Sigma_s w_0}{w_0^\top\Sigma_f w_0}\,\Sigma_f.
$$

If the models forecast 7% and 10% on those weights, I multiply the factor target’s covariance by $$7^2/10^2=0.49$$. Both then price that reference book at 7%, while their correlations and relative stock volatilities still differ. I also do the reverse and put stock shrinkage at the factor target’s risk level. Each optimizer chooses its own holdings under each comparison.

<table class="research-table comparison-table compact-table">
  <caption><span class="caption-number">Table 4.</span> <span class="caption-title">Portfolio outcomes at a common risk scale.</span> Each cell gives annualized net compound return and realized volatility. Rows share the forecast scale named above their block.</caption>
  <thead><tr><th scope="col">Stock relationships</th><th scope="col">1999–2021</th><th scope="col">2022–26</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="3">Stock-shrinkage risk level</th></tr>
    <tr><th scope="row">Stock shrinkage</th><td>10.77% / 8.74%</td><td>7.42% / 9.65%</td></tr>
    <tr><th scope="row">Factor target</th><td>10.48% / 8.84%</td><td>6.00% / 9.70%</td></tr>
    <tr class="period-heading"><th colspan="3">Factor-target risk level</th></tr>
    <tr><th scope="row">Stock shrinkage</th><td>9.67% / 7.45%</td><td>5.96% / 7.30%</td></tr>
    <tr><th scope="row">Factor target</th><td>9.50% / 7.47%</td><td>4.59% / 7.27%</td></tr>
  </tbody>
</table>

In the later period, moving to the factor target’s forecast scale reduced realized volatility by about 2.4 percentage points for both covariance models. Swapping the stock relationships at the same scale barely moved volatility, with paired intervals spanning roughly 0.2 points either way. The factor target earned less at both scales in this sample, with considerable uncertainty around the return difference.

## Trading with a calibrated risk budget

The scale swap puts the two models on a common footing. To size the portfolio at a volatility target, I also want the forecast close to the risk the book actually takes. I multiply each covariance estimate by a factor $$k$$ learned from the last 52 completed holding periods of its reference book. With forecast variance $$v$$ and mean squared daily return $$u$$, the part of mean QLIKE that depends on $$k$$ is $$\log k + \overline{u/v}/k$$. It is minimized at $$k=\overline{u/v}$$. I apply that estimate to the next decision, then let the weights adjust to the new risk forecast.

A fixed adjustment estimated through 2021 also brought the stock-shrinkage book close to the budget later, at 7.5% realized volatility. The rolling adjustment brought it to 7.1%. Both replays point to the importance of the risk level, with less evidence for the value of updating the adjustment.

<table class="research-table comparison-table compact-table">
  <caption><span class="caption-number">Table 5.</span> <span class="caption-title">Portfolios after rolling risk calibration.</span> Return and Sharpe are net above, gross below. Gross exposure counts both longs and shorts at market value per dollar of capital.</caption>
  <thead><tr><th>Sizing rule</th><th>Return</th><th>Vol.</th><th>Sharpe</th><th>Gross exposure</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="5">January 1999 – December 2021</th></tr>
    <tr><th scope="row">Stock shrinkage</th><td>9.80%<span class="secondary-metric">11.73%</span></td><td>7.41%</td><td>1.30<span class="secondary-metric">1.54</span></td><td>1.65</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>7.56%<span class="secondary-metric">9.55%</span></td><td>7.25%</td><td>1.04<span class="secondary-metric">1.29</span></td><td>1.44</td></tr>
    <tr><th scope="row">Factor target</th><td>9.38%<span class="secondary-metric">11.38%</span></td><td>7.12%</td><td>1.29<span class="secondary-metric">1.55</span></td><td>1.62</td></tr>
    <tr class="period-heading"><th colspan="5">January 2022 – May 2026</th></tr>
    <tr><th scope="row">Stock shrinkage</th><td>6.10%<span class="secondary-metric">7.00%</span></td><td>7.13%</td><td>0.87<span class="secondary-metric">0.99</span></td><td>1.19</td></tr>
    <tr><th scope="row">Sector and style factors</th><td>2.44%<span class="secondary-metric">3.41%</span></td><td>6.92%</td><td>0.38<span class="secondary-metric">0.52</span></td><td>0.96</td></tr>
    <tr><th scope="row">Factor target</th><td>4.48%<span class="secondary-metric">5.49%</span></td><td>7.00%</td><td>0.66<span class="secondary-metric">0.80</span></td><td>1.19</td></tr>
  </tbody>
</table>

The calibrated Factor target row uses the same 50/50 correlation estimate. Calibration adjusts the overall risk forecast used to size the positions. In the later period, stock shrinkage and the factor target both averaged $1.19 of gross exposure per dollar of capital and realized close to 7% volatility. Their compounded annual returns after fees were 6.10% and 4.48%, respectively. The paired interval for their net Sharpe difference included zero.

The two books took different risks at that size. I applied the same factor model to both portfolios’ opening holdings each day. At their average exposures, a 1% rise in the fitted momentum factor would add 0.88% to the stock-shrinkage portfolio and 0.59% to the factor-target portfolio. A 1% fall would reverse those contributions. Multiplying each day’s exposure by that day’s momentum return, I get 1.68 percentage points a year in stock shrinkage’s favor, including 0.96 points from the shorts. Other contributions partly offset that gain, leaving a 1.44-point advantage before fees. These figures use annualized arithmetic returns so the contributions add up.

Similar overall volatility can come with different market exposure. The estimated beta limit applies at rebalance. Realized beta measures how the filled book moved with the Russell 1000. When measured over the same window, beta equals correlation with the index times the ratio of portfolio to index volatility, $$\beta_{p,m}=\rho_{p,m}\sigma_p/\sigma_m$$. At the same market correlation, a more volatile book has a larger beta in magnitude.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/factor-risk-sizing/market-exposure" mobile="/assets/factor-risk-sizing/market-exposure_mobile" version="2" alt="Rolling 63-session market beta and 252-session correlation with the Russell 1000 across the full backtest for the three calibrated portfolios." %}
</div>
<p class="figure-caption"><span class="caption-number">Figure 5.</span> <span class="caption-title">Market beta and correlation.</span> Monthly observations use 63 sessions for beta and 252 for correlation against the Russell 1000. Both average the three schedules’ net-return estimates.</p>

To understand what market exposure misses, I looked at the deepest drawdown of an equal mix of the calibrated stock-shrinkage and factor-target books. In that early-2023 window, each book lost about 8% while the Russell 1000 rose 11%. The losses came from the short side as its stocks rose.

## A wider candidate list changes both holdings and turnover

I used 75 entry candidates per side in the experiments above. I widened the list to 100 and 150 per side to see how much the results depend on that choice. A wider list gives the optimizer more potential hedges, including stocks with weaker forecasts. I kept the reference retention rule, which lets the joint optimizers keep holdings in the top or bottom 175 ranks. With that rule fixed, going from 75 to 150 leaves only 25 ranks of room at the entry boundary, down from 100.

At 150 per side stock shrinkage held about 175 stocks and the factor target 123 in the later period. Net Sharpe fell for all three joint optimizers as the entry list widened. Stock shrinkage and the factor target also had lower gross Sharpe at 150 than at 75, so trading fees explain only part of the decline.

<table class="research-table comparison-table compact-table">
  <caption><span class="caption-number">Table 6.</span> <span class="caption-title">Portfolio outcomes by entry breadth.</span> Each column sets the candidate count per side. Annualized net return appears above net Sharpe, averaged across three schedules.</caption>
  <thead><tr><th>Sizing rule</th><th>75 per side</th><th>100 per side</th><th>150 per side</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="4">1999–2021</th></tr>
    <tr><th scope="row">Volatility scaling</th><td>7.12%<span class="secondary-metric">0.89</span></td><td>6.43%<span class="secondary-metric">0.85</span></td><td>5.75%<span class="secondary-metric">0.84</span></td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>10.77%<span class="secondary-metric">1.21</span></td><td>10.41%<span class="secondary-metric">1.17</span></td><td>10.44%<span class="secondary-metric">1.17</span></td></tr>
    <tr><th scope="row">Sector and style factors</th><td>7.95%<span class="secondary-metric">0.98</span></td><td>7.71%<span class="secondary-metric">0.94</span></td><td>8.12%<span class="secondary-metric">0.97</span></td></tr>
    <tr><th scope="row">Factor target</th><td>9.50%<span class="secondary-metric">1.25</span></td><td>9.06%<span class="secondary-metric">1.19</span></td><td>9.32%<span class="secondary-metric">1.22</span></td></tr>
    <tr class="period-heading"><th colspan="4">2022–May 2026</th></tr>
    <tr><th scope="row">Volatility scaling</th><td>6.96%<span class="secondary-metric">0.71</span></td><td>6.76%<span class="secondary-metric">0.73</span></td><td>5.51%<span class="secondary-metric">0.65</span></td></tr>
    <tr><th scope="row">Stock shrinkage</th><td>7.42%<span class="secondary-metric">0.79</span></td><td>7.20%<span class="secondary-metric">0.76</span></td><td>6.69%<span class="secondary-metric">0.71</span></td></tr>
    <tr><th scope="row">Sector and style factors</th><td>2.72%<span class="secondary-metric">0.37</span></td><td>2.51%<span class="secondary-metric">0.34</span></td><td>2.17%<span class="secondary-metric">0.29</span></td></tr>
    <tr><th scope="row">Factor target</th><td>4.59%<span class="secondary-metric">0.65</span></td><td>4.37%<span class="secondary-metric">0.62</span></td><td>3.75%<span class="secondary-metric">0.53</span></td></tr>
  </tbody>
</table>

To isolate the retention rule, I kept entry at 150 and let positions remain eligible through rank 250. Later annual turnover fell from roughly 25× capital to 21× for stock shrinkage and 22× for the factor target. Most of the saving came from less trading on exits beyond the cutoff and on new entries. Net Sharpe rose from 0.71 to 0.79 and from 0.53 to 0.59, respectively. Both paired Sharpe intervals included zero. The clearest effect of a wider retention band was less trading.

The later Sharpe comparison at 150 per side is sensitive to which years are included. Leaving out 2024 put stock shrinkage and the factor target close to even.

## What changes when the risk model changes

The covariance estimate does two jobs. It tells the optimizer which positions offset one another, and it determines how much exposure fits inside the risk budget. A model can improve the first job for a broadly diversified spread while pushing the optimizer toward quite different positions once names can be dropped. In the Ridge replay, most of the gap in headline volatility came from how the models priced a dollar of exposure. Matching total volatility still left room for different market exposures and different stock weights.

## References

- Factor exposures, risk and attribution. [Paleologo, *Linear Models of Asset Returns*, Columbia Quantitative Investing, Lecture 3](https://www.dropbox.com/scl/fi/1nqzz8zfikjace6g5fa5j/FINC_B8420_3_simple.pdf?rlkey=pj6boer325ci9e3bys5rt5vdz&dl=0)
- The linear factor model applied to equity portfolios. [Zhang, *Modeling Equities Returns: The Linear Case*, Hudson River Trading](https://www.hudsonrivertrading.com/hrtbeat/modeling-equities-returns/)
- Practitioner examples. [MSCI Barra US Equity Model (USE4)](https://www.msci.com/documents/10199/242721/Barra_US_Equity_Model_USE4.pdf) · [Bloomberg Portfolio & Risk Analytics](https://professional.bloomberg.com/products/bloomberg-terminal/portfolio-analytics/)
- Volatility scaling. [Paleologo, *Advanced Portfolio Management*, §6.3](https://www.wiley.com/en-us/advanced-portfolio-management-a-quant%27s-guide-for-fundamental-investors-p-9781119789802)
- Correlation shrinkage. [Pedersen, Babu and Levine, *Enhanced Portfolio Optimization*](https://doi.org/10.1080/0015198X.2020.1854543)
