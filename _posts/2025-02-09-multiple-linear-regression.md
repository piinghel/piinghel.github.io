---
layout: post
title: "Combining Stock Signals with Multiple Linear Regression"
date: 2025-02-09
last_modified_at: 2026-08-23
categories: [Quants]
article_label: Factor combination · Multiple linear regression
permalink: /quants/2025/02/09/multiple-linear-regression.html
---

<p class="article-summary"><strong>TL;DR:</strong> This article compares a fixed five-theme benchmark with two learned combinations, OLS and Ridge. During development, OLS records a net Sharpe of 0.98, compared with 0.71 for the benchmark. Ridge reduces coefficient size and refit movement by roughly one third while keeping a 0.991 rank correlation with OLS. From January 2022 through May 2026, OLS records 0.87 and Ridge 0.82. This four-year pseudo-holdout offers limited evidence about long-run performance.</p>

A stock model can combine several predictors in one ranking. The central choice
is how much influence each predictor receives. I compare a hand-built benchmark
with weights learned from history.

Each method produces an ordered list of stocks. The highest scores become long
candidates and the lowest scores become short candidates. Position sizing,
execution, and trading costs then turn that ranking into a portfolio.

The comparison has three versions: a fixed-weight score, ordinary least squares
(OLS), and Ridge. Fixed weights versus OLS compares two complete specifications. OLS
versus Ridge keeps the predictors, target, and portfolio fixed, so it isolates
the estimator.

## Benchmark

The benchmark uses familiar signals with fixed signs and equal theme weights.
Every choice is visible, and each theme receives the same influence. The factor
choices, lookbacks, and signs still reflect my judgment.

The benchmark has five economic themes. Six raw signals enter because the
defensive theme combines two related questions:

**Defensive.** Low volatility rewards stocks whose returns have been
quiet over one, three, and six months. Upper-tail avoidance penalises a recent
path that depends on a few unusually large gains. Together they form one
defensive theme, with lower values preferred for both ingredients.

**Momentum.** The signal looks for a return pattern that has
survived several months, while skipping the latest month to keep short-term
reversal separate from the trend. Higher values are preferred.

**Low short interest.** The signal favours stocks with less reported short
positioning relative to their trading activity. Publication lagging keeps the
measure aligned with the signal date. Lower values are preferred.

**Large capitalisation.** Market capitalisation supplies a size and
investability tilt. Higher values are preferred.

**Return consistency.** The signal counts losing days over roughly three years,
separating their frequency from the size of any one loss. Lower values are
preferred.

The benchmark turns those ideas into six measures. For stock $$i$$ on date
$$t$$, let $$r_{i,t}$$ be its daily total return, $$v_{i,t}$$ its daily volume,
$$h^{\mathrm{lag}}_{i,t}$$ the publication-lagged shares short available on that
date, and $$m_{i,t}$$ its market capitalisation. I cap positive daily returns at
100%, so $$\widetilde r_{i,t}=\min(r_{i,t},1)$$. Each rolling measure requires at
least 80% of its stated window.

The two defensive measures are

$$
\begin{aligned}
x^{\mathrm{vol}}_{i,t}
&=\min\left\{2,\frac{1}{3}\sum_{h\in\{21,63,126\}}
\max\left[0.05,\sqrt{252}\,\operatorname{sd}
\{r_{i,t-j}\}_{j=0}^{h-1}\right]\right\}, \\
x^{\mathrm{tail}}_{i,t}
&=\frac{1}{3}\sum_{k=1}^{3}
Q^{\mathrm{higher}}_{i,t}\!\left(\frac{21-k}{21}\right).
\end{aligned}
$$

The first line averages annualised volatility over 21, 63, and 126 sessions,
with a 5% floor and a 200% cap. In the second line,
$$Q^{\mathrm{higher}}_{i,t}(p)$$ is the higher-interpolated empirical quantile of
the latest 21 capped returns. The three quantiles recover the three largest
returns in a full window, and their mean measures reliance on a small upper
tail. Partial windows use the same fast rolling-quantile approximation after at
least 16 observations. The remaining measures are

$$
\begin{aligned}
x^{\mathrm{mom}}_{i,t}
&=\sum_{h\in\{63,126,189,252\}}
\left[\prod_{j=21}^{h+20}(1+\widetilde r_{i,t-j})-1\right], \\
\overline v^{(63)}_{i,t}
&=\frac{1}{63}\sum_{j=0}^{62}v_{i,t-j}, \\
x^{\mathrm{short}}_{i,t}
&=\log\left(\frac{h^{\mathrm{lag}}_{i,t}}
{\overline v^{(63)}_{i,t}}\right), \\
x^{\mathrm{size}}_{i,t}&=m_{i,t}, \\
x^{\mathrm{cons}}_{i,t}
&=\frac{1}{756}\sum_{j=0}^{755}\mathbf 1\{\widetilde r_{i,t-j}<0\}.
\end{aligned}
$$

Let $$k$$ index the six measures. I set $$d_k=+1$$ for momentum and
capitalisation, and $$d_k=-1$$ for the other four. The signed percentile rank is

$$
z^{(k)}_{i,t}
=\frac{\operatorname{rank}^{\mathrm{avg}}_t
\!\left(d_kx^{(k)}_{i,t}\right)}{N^{(k)}_t},
$$

where $$N^{(k)}_t$$ is the available stock count for measure $$k$$. A higher
rank is always more attractive. I first form the defensive theme, then average
the five themes:

$$
\begin{aligned}
z^{\mathrm{def}}_{i,t}
&=\frac{z^{\mathrm{vol}}_{i,t}+z^{\mathrm{tail}}_{i,t}}{2}, \\
b_{i,t}
&=\frac{z^{\mathrm{def}}_{i,t}+z^{\mathrm{mom}}_{i,t}
+z^{\mathrm{short}}_{i,t}+z^{\mathrm{size}}_{i,t}
+z^{\mathrm{cons}}_{i,t}}{5}.
\end{aligned}
$$

Low volatility and tail avoidance share the defensive weight. Each remaining
theme receives 20%. A stock enters the benchmark when all six measures
are available. This produces one ranking and one portfolio. Benchmark and
regression then share the same selection, weighting, execution, and cost rules.

Those six measures define the transparent benchmark; OLS and Ridge receive a
broader deck of 144 ranked predictors, including
multiple horizons of return and trend, total and downside volatility, technical
price location, market-cap and market-correlation measures, trading activity and
price-volume interaction, and publication-lagged short positioning. Examples
include price relative to a moving average, RSI, ATR, upside and downside
volatility, share turnover, illiquidity, market-cap variability, and
short-interest-to-volume. The extra horizons and related transformations are
deliberate: the regression tests whether a learned combination improves on the
small hand-built benchmark.

The benchmark reflects research judgment in its factors, horizons, and signs.
Several themes overlap, and their data histories differ. Benchmark versus OLS
therefore compares two complete methods. OLS versus Ridge isolates the estimator
because those models use identical inputs.

## A common score scale

Predictors measured in dollars, returns, and ratios need a common scale. I rank
every predictor across the eligible Russell 1000 universe before fitting the
model.
Let $$R^{\mathrm{dense}}_{i,j,t}$$ be
stock $$i$$'s dense rank on predictor $$j$$, and let $$K_{j,t}$$ be the number of
distinct ranks on that date. The normalized predictor is

$$
x^{\mathrm{rank}}_{i,j,t}
=2\frac{R^{\mathrm{dense}}_{i,j,t}}{K_{j,t}}-1.
$$

This mapping places every predictor inside $[-1,1]$; a flat cross-section
receives zero. Predictors in different units become comparable, and adjacent
ranks receive the same spacing.

Missing inputs are first carried forward within the same stock when an earlier
observation exists, then filled with that date-and-sector mean. The completed
predictor is ranked across all current index members on the date. The traded
universe later removes stocks below $5, announced merger
targets, and duplicate share classes.

The target uses the next 20 daily returns. I calculate their mean, cap annualised
volatility at 1,000% for numerical stability, and form a Sharpe-like outcome:

$$
\begin{aligned}
\overline r^{(20)}_{i,t}
&=\frac{1}{20}\sum_{h=1}^{20}r_{i,t+h}, \\
s^{(20)}_{i,t}
&=\min\left\{\operatorname{sd}\{r_{i,t+h}\}_{h=1}^{20},
\frac{10}{\sqrt{252}}\right\}, \\
q^{(20)}_{i,t}
&=\sqrt{252}\,\frac{\overline r^{(20)}_{i,t}}{s^{(20)}_{i,t}}.
\end{aligned}
$$

I use this forward Sharpe-like outcome to prefer a return distributed through
the month over the same return produced by a few volatile days. The model ranks
this target; portfolio Sharpe remains a downstream outcome. The annualization
factor leaves the ordering unchanged. A raw-return target is a plausible
alternative and could produce a riskier learned score.

I rank the outcome within its date and sector. Targets remain observed-only.
Predictor ranks retain cross-sector information, while target ranks ask which
stocks subsequently did better than their sector peers. This reduces
sector-level movement in the label. Portfolio selection remains global, so the
final holdings can still carry sector exposures; an allocation risk model would
have to constrain them explicitly.

## Learning the signal weights

Regression learns the combination that best orders the forward outcomes in the
training data. Let
$$\mathbf x_{i,t}\in[-1,1]^{144}$$ contain the normalized predictors and let
$$y_{i,t}$$ be the sector-ranked forward target. In walk-forward fold $$f$$,
ordinary least squares estimates

$$
(\widehat\beta^{\mathrm{OLS}}_{0,f},
\widehat{\boldsymbol\beta}^{\mathrm{OLS}}_f)
=\arg\min_{\beta_0,\boldsymbol\beta}
\frac{1}{n_f}\sum_{(i,t)\in\mathcal T_f}
\left(y_{i,t}-\beta_0-\mathbf x_{i,t}^{\top}
\boldsymbol\beta\right)^2.
$$

Here $$\mathcal T_f$$ is the training sample and $$n_f=|\mathcal T_f|$$. The
fitted score $$\widehat y_{i,t}=\widehat\beta_{0,f}
+\mathbf x_{i,t}^{\top}\widehat{\boldsymbol\beta}_f$$ becomes the learned stock
ranking. A positive coefficient rewards a high predictor rank; a negative
coefficient reverses the preference.

The model contains 144 normalized inputs drawn from far fewer economic ideas.
They cover return and trend, total and asymmetric risk, technical location and
price path, size and market correlation, trading activity and price-volume
interaction, and publication-lagged short positioning. Many ideas appear at
several horizons. That redundancy is precisely why the joint model can behave
differently from a list of standalone factors.

I refit the model as the historical sample expands and score only the next
block—a walk-forward design. The research history begins in January 1995. The
first 900 dates establish the initial training sample, so mechanical
out-of-sample predictions begin in September 1998. Each of 12 fits leaves a
21-session gap around the overlapping 20-session target, then scores the next
600-date block. At each refit, I average three models trained on complementary
every-third-date samples to reduce dependence among adjacent target windows.

<div class="research-figure walk-forward-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/walk-forward-mobile.svg?v=4">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/walk-forward-mobile.png?v=4">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/walk-forward.svg?v=4">
    <img src="/assets/multiple-linear-regression/walk-forward.png?v=4" alt="Expanding walk-forward training windows separated from each next test block by a 21-session gap" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Expanding walk-forward estimation, with each training history separated from its next 600-date prediction block by a 21-session purge.</p>

Each refit predicts a mechanically out-of-sample block. The wider 1995–2021
history is still the **research and development period** because I repeatedly
inspected it while revising predictors, normalization, targets, and portfolio
rules. Walk-forward estimation protects each prediction from future training
data; repeated research reuse makes the period development evidence.

Every score then enters the same portfolio construction, derived in more detail
in the earlier [low-volatility allocation article](/quant/2024/12/15/low-volatility-factor.html).
The top and bottom 75 stocks form the long and short books. Each starts at
$1/75$, is scaled by 20% divided by trailing 60-session volatility, and is capped
at 4% of sleeve capital; volatility is floored at 5% and the multiplier at four.
Each side is scaled down if gross exposure exceeds 100%; a smaller side keeps
its lower exposure. The rule therefore reduces single-stock risk while allowing
cross-stock correlations, dollar exposure, beta, and total portfolio volatility
to emerge from the holdings. Three equal-capital sleeves rebalance on offset
third Fridays, execute at the next close, and hold for three weeks. Reported
returns charge 5 bp per dollar traded.

## Ridge and the penalty choice

OLS creates a practical problem. Several predictors describe almost the same
idea, so their individual coefficients can move sharply while the final ranking
barely moves. Ridge asks the model to prefer smaller coefficients by adding an
L2 penalty:

$$
(\widehat\beta^{(c)}_{0,f},\widehat{\boldsymbol\beta}^{(c)}_f)
=\arg\min_{\beta_0,\boldsymbol\beta}
\left\{
\frac{1}{n_f}\sum_{(i,t)\in\mathcal T_f}
\left(y_{i,t}-\beta_0-\mathbf x_{i,t}^{\top}
\boldsymbol\beta\right)^2
+c\lVert\boldsymbol\beta\rVert_2^2
\right\}.
$$

The penalty applies to the slopes and leaves the intercept free. Setting $c=0$
gives the exact OLS baseline. Positive values shrink coefficients and can make
correlated inputs share weight more evenly. Shrinkage follows directly from the
objective; any predictive improvement has to appear in the data.

The implementation uses
[`sklearn.linear_model.Ridge`](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html),
whose objective uses a residual sum rather than the mean above. For a fold with
$n_f$ rows, $\alpha_f=n_fc$. This keeps $c$ comparable as the sample expands.
The $c=0$ case uses `LinearRegression`.

The rows share market and sector shocks, predictors move slowly, and adjacent
20-session targets overlap. A 21-session purge keeps a
training target out of the next prediction block, while 600-date walk-forward
blocks avoid random row-level validation. Some overlap remains. The penalty
choice is a sensitivity check. The effective sample contains far fewer
independent observations than the raw row count suggests.

All four candidates use the same predictors, target, universe, dates,
walk-forward procedure, portfolio construction, and 5 bp cost assumption. The grid
$$c\in\{0,0.001,0.01,0.1\}$$ uses data through 2021. I prefer a value that
behaves consistently across the full development period, its final ten years,
and its final five years. Consistency takes priority over winning a single slice.

To judge Ridge, I separate the model from the trading layer. Rank information
coefficient (IC), prediction changes, and coefficient behavior ask what
shrinkage changes before costs. The portfolio table reports both gross and net
return because the final choice still has to work as an implementation. Annual
cost drag ranges only from 1.43 to 1.46 percentage points across the grid.
Similar deductions keep cost differences from driving the penalty choice: gross
return isolates the portfolio result before the stated trading cost, while net
return shows what remains after it.

| Estimator | Gross return | Net return | Net volatility | Net Sharpe |
| --- | ---: | ---: | ---: | ---: |
| OLS, $c=0$ | 8.49% | 7.03% | 7.15% | 0.983 |
| Ridge, $c=0.001$ | 8.51% | 7.05% | 7.19% | 0.981 |
| **Ridge, $c=0.01$** | **8.82%** | **7.38%** | **7.36%** | **1.003** |
| Ridge, $c=0.1$ | 9.26% | 7.83% | 7.92% | 0.989 |
{: .research-table .comparison-table .alpha-selection-table }

<p class="table-caption"><strong>Table 1:</strong> Development-period annualized arithmetic return across the matched OLS–Ridge penalty grid before and after 5 bp per dollar traded; volatility and Sharpe use net returns.</p>

I choose the moderate $c=0.01$ specification as a development-period
compromise. Relative to OLS, annualized return rises by 0.35 percentage points
and volatility by 0.21, lifting Sharpe by 0.020. OLS and the two moderate Ridge
penalties remain tightly grouped over the final ten and five development years.
The $c=0.1$ model earns more return and takes more risk, while recording weaker
Sharpes in both shorter windows.
{: .table-followup }

Two diagnostics measure how Ridge differs from OLS. Portfolio membership counts
how many of the 75 longs and 75 shorts change on an average rebalance.
Coefficient shrinkage reports the reduction in the coefficients' Euclidean size
(L2 norm) and their mean absolute change between adjacent refits. Prediction
accuracy is evaluated separately with rank IC and portfolio results.

<div class="research-figure alpha-sensitivity-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/alpha-sensitivity-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/alpha-sensitivity-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/alpha-sensitivity.svg">
    <img src="/assets/multiple-linear-regression/alpha-sensitivity.png" alt="Average portfolio-membership changes and coefficient shrinkage relative to OLS across the Ridge penalty grid" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Average portfolio-membership changes and coefficient shrinkage relative to matched OLS during the development period.</p>

At $c=0.01$, about 14 of the 150 selected names change on a typical rebalance.
Across the full cross-section, the average stock moves 2.71 percentile-rank
points and prediction ranks retain a 0.991 correlation with OLS. At the same
time, the coefficient norm and refit movement fall by roughly one third. The
stronger $c=0.1$ penalty changes about 39 names, moves the average stock 7.79
rank points, and cuts both coefficient measures by about 70%. Coefficients move
far more than the resulting stock list. The later IC evidence measures whether
the changed ranking is more accurate.

Correlated predictors can exchange coefficient weight while keeping their
combined score close. More generally,

$$
\Delta\widehat{\mathbf y}
=\mathbf X\,\Delta\boldsymbol\beta.
$$

The feature matrix can absorb a large $\Delta\boldsymbol\beta$ when related
predictors substitute for one another. OLS identifies the combined prediction
more clearly than the individual weights, and Ridge chooses a smaller-norm point
among many similar combinations. The 0.991 rank correlation supports a stable
stock ordering, while attribution belongs at the predictor-group level.

The coefficient heatmap shows where those smaller weights go. It keeps the
ten predictors with the largest mean absolute coefficient in the selected Ridge
model and shows their signed value at each refit, averaged across the three
date-thinned ensemble members. Because every input is mapped to the same
$[-1,1]$ rank scale, values are comparable within the model. Positive cells
raise the score when a stock ranks highly on that predictor; negative cells
reverse the preference. These weights describe conditional relationships among
correlated inputs. Standalone factor returns and causal effects require separate
tests. The 2022 and 2024 columns are later-period diagnostics, while the
selection statistics use development data only.

<div class="research-figure coefficient-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/top-coefficients-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/top-coefficients-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/top-coefficients.svg">
    <img src="/assets/multiple-linear-regression/top-coefficients.png" alt="Heatmap of the ten largest average absolute coefficients for the selected Ridge specification across twelve walk-forward refits" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Signed coefficients for the selected Ridge model's ten largest mean absolute weights across walk-forward refits; the 2022 and 2024 columns are later-period diagnostics.</p>

The clearest directions persist: price relative to its 126-session moving
average stays positive, while short-horizon moving-average convergence/divergence
(MACD) and illiquidity stay negative.
Other weights weaken or change sign as the sample expands. Combined with the
summary statistics above, this suggests Ridge mainly reduces coefficient scale
and concentration; time variation remains in which correlated predictor
receives the weight.

## Development-period results

The portfolio comparison begins with the first mechanical walk-forward
predictions in 1998, inside the 1995–2021 development period. The benchmark uses
a smaller hand-built signal set and different data histories. OLS and Ridge
share the same 144 predictors.

| Development metric | Fixed | OLS | Ridge $c=0.01$ |
| --- | ---: | ---: | ---: |
| Annualized return, gross | 7.61% | 8.49% | 8.82% |
| Annualized return, net | 6.92% | 7.03% | 7.38% |
| Annualized volatility | 9.73% | 7.15% | 7.36% |
| Sharpe ratio | 0.71 | 0.98 | 1.00 |
| Maximum drawdown | −31.55% | −18.77% | −19.03% |
| Market beta | 0.093 | 0.084 | 0.091 |
| Turnover per rebalance | 78.78% | 167.67% | 165.72% |
| Annual cost drag | 0.69 pp | 1.46 pp | 1.44 pp |
{: .research-table .comparison-table .period-metrics-table }

<p class="table-caption"><strong>Table 2:</strong> Development-period portfolio results. Gross return is before the stated trading cost; all risk statistics use returns after 5 bp per dollar traded.</p>

The learned portfolios have higher Sharpes than the benchmark, with similar
annualized returns, lower volatility, and shallower drawdowns. The price is
roughly double the benchmark's turnover and annual cost drag. Ridge reduces
turnover by only 1.95 percentage points per rebalance relative to OLS and saves
about 0.02 percentage points a year. Coefficient shrinkage is meaningful; the
trading-cost change is negligible.
{: .table-followup }

## January 2022 to May 2026

I selected $c=0.01$ using data through 2021. Later history had already influenced
earlier feature, target, portfolio, and presentation work, so January 2022–May
2026 is a **pseudo-holdout**. Its four years provide a diagnostic rather than a
full market cycle.

| Later-period metric | Fixed | OLS | Ridge $c=0.01$ |
| --- | ---: | ---: | ---: |
| Annualized return, gross | 7.85% | 8.84% | 8.68% |
| Annualized return, net | 7.24% | 7.50% | 7.37% |
| Annualized volatility | 11.33% | 8.64% | 8.95% |
| Sharpe ratio | 0.64 | 0.87 | 0.82 |
| Maximum drawdown | −10.98% | −7.59% | −8.05% |
| Market beta | 0.036 | 0.075 | 0.078 |
| Turnover per rebalance | 69.70% | 152.75% | 149.61% |
| Annual cost drag | 0.61 pp | 1.34 pp | 1.31 pp |
{: .research-table .comparison-table .period-metrics-table }

<p class="table-caption"><strong>Table 3:</strong> Later-period portfolio results. Gross return is before the stated trading cost; all risk statistics use returns after 5 bp per dollar traded.</p>

From January 2022 through May 2026, Ridge return is 0.13 percentage points below
OLS, volatility is 0.30 points higher, and Sharpe is 0.82 versus 0.87. Turnover
and costs are slightly lower. Four years contain few distinct market regimes,
so I treat these differences as diagnostics. The $c=0.001$ candidate records the
highest Sharpe in this window at 0.89. The development-period rule keeps
$c=0.01$ as the selected model.
{: .table-followup }

## Ranking accuracy

The information coefficient asks a different question from portfolio Sharpe. On
each date it is the cross-sectional Spearman correlation between the predicted
score and the subsequently realized, sector-ranked target on their common stock
sample:

$$
\mathrm{IC}_t
=\rho_{\mathrm S}\!\left(
\{\widehat y_{i,t}\}_{i\in\mathcal U_t},
\{y_{i,t}\}_{i\in\mathcal U_t}
\right).
$$

The IC history starts with the first walk-forward predictions in September 1998
and ends on April 28, 2026, the last date for which the full 20-session outcome
is available.

The cumulative path adds those daily correlations. A rising path means the model has
usually ordered future outcomes correctly; a flat path means zero additional
cumulative rank association, and a decline means a run of negative IC. The sum
is a prediction diagnostic, distinct from a return series and a significance
statistic.

<div class="research-figure ic-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/cumulative-ic-mobile.svg?v=4">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/cumulative-ic-mobile.png?v=4">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/cumulative-ic.svg?v=4">
    <img src="/assets/multiple-linear-regression/cumulative-ic.png?v=4" alt="Cumulative daily cross-sectional rank information coefficient for fixed weights, OLS, and selected Ridge with the 2022 boundary marked" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Cumulative daily cross-sectional Spearman information coefficient for the fixed score, OLS, and selected Ridge predictions; the rule marks the 2022 boundary.</p>

<table class="research-table comparison-table ic-summary-table">
  <thead>
    <tr>
      <th>Period and ranking</th>
      <th>Mean daily IC</th>
      <th>IC SD</th>
      <th>IC IR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Development · Fixed score</th>
      <td data-label="Mean daily IC">0.0399</td>
      <td data-label="IC standard deviation">0.1217</td>
      <td data-label="IC IR">0.328</td>
    </tr>
    <tr>
      <th scope="row">Development · OLS</th>
      <td data-label="Mean daily IC">0.0461</td>
      <td data-label="IC standard deviation">0.0864</td>
      <td data-label="IC IR">0.534</td>
    </tr>
    <tr>
      <th scope="row">Development · Ridge $c=0.01$</th>
      <td data-label="Mean daily IC">0.0469</td>
      <td data-label="IC standard deviation">0.0885</td>
      <td data-label="IC IR">0.530</td>
    </tr>
    <tr class="period-break">
      <th scope="row">2022–2026 · Fixed score</th>
      <td data-label="Mean daily IC">0.0502</td>
      <td data-label="IC standard deviation">0.1392</td>
      <td data-label="IC IR">0.361</td>
    </tr>
    <tr>
      <th scope="row">2022–2026 · OLS</th>
      <td data-label="Mean daily IC">0.0417</td>
      <td data-label="IC standard deviation">0.1068</td>
      <td data-label="IC IR">0.390</td>
    </tr>
    <tr>
      <th scope="row">2022–2026 · Ridge $c=0.01$</th>
      <td data-label="Mean daily IC">0.0415</td>
      <td data-label="IC standard deviation">0.1113</td>
      <td data-label="IC IR">0.373</td>
    </tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 4:</strong> Mean and standard deviation of daily rank IC, with IC IR defined as mean divided by standard deviation, shown separately for development and later periods.</p>

During development, Ridge raises mean IC over OLS by only 0.0008 and also raises
its standard deviation, leaving IC IR fractionally lower at 0.530 versus 0.534.
In the later period its mean IC is fractionally lower than OLS and its dispersion
is higher. The cumulative paths therefore tell the same story as the table: OLS
and moderate Ridge produce almost the same ordering, while shrinkage adds little
prediction-quality gain.

The fixed score has the highest later-period mean IC and the most variable daily
IC. Its IC IR remains below OLS. This aligns with the portfolio results:
IC measures the ordering of the entire eligible cross-section against
the normalized target; portfolio return depends only on names near the tails,
then adds position sizing, stock-level volatility scaling, execution, and
costs. The differing predictor sets also prevent fixed score versus OLS from
being a controlled estimator comparison.

## Performance through time

Portfolio performance adds selection, volatility scaling, execution, and costs
to the prediction evidence. The complete net path shows the drawdowns behind the
period summaries.

<div class="research-figure performance-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/performance-and-drawdowns-mobile.svg?v=5">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/performance-and-drawdowns-mobile.png?v=5">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/performance-and-drawdowns.svg?v=5">
    <img src="/assets/multiple-linear-regression/performance-and-drawdowns.png?v=5" alt="Net growth and drawdowns for fixed weights, OLS, and selected Ridge with development and later periods separated" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Net cumulative performance and drawdowns for the three ranking systems after charging 5 bp per dollar traded; the rule separates development from the later period.</p>

The learned portfolios have lower development-period volatility and shallower
drawdowns. Ridge stays close to OLS throughout the sample. From January 2022
through May 2026, OLS records the higher Sharpe. The vertical rule marks the
specification boundary.

## What the portfolio is actually doing

### Turnover and cost

Portfolio evaluation includes turnover and implementation costs. Turnover is
the absolute long- and short-side trading at each
rebalance, divided by equity. I charge 5 basis points per dollar traded and
compound the resulting net returns. The estimate covers stock trading. A fuller
implementation estimate would add borrow, financing, market impact, and taxes. Applying the same rule to
every portfolio shows how much turnover reduces returns.

<div class="research-figure turnover-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/turnover-and-costs-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/turnover-and-costs-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/turnover-and-costs.svg">
    <img src="/assets/multiple-linear-regression/turnover-and-costs.png" alt="Turnover per rebalance and annual cost drag for fixed weights, OLS, and selected Ridge in development and later periods" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 6:</strong> Average two-way turnover per rebalance and annual return drag from the 5 bp trading-cost assumption, shown separately for development and the later period.</p>

The fixed score has about half the turnover and cost drag of the learned
rankings. Ridge barely changes the higher turnover: versus OLS, the selected
penalty saves 0.02 percentage points of annual return in development and 0.03 in
the later period. The cost difference provides little reason to prefer Ridge.

### Capital and market exposure

The selected Ridge portfolio's capital use changes through time. Long
gross is the value of the long book divided by portfolio equity; short gross is
the absolute value of the short book; net stock exposure is long gross minus
short gross. The lines are monthly averages of daily floating weights across
the three execution sleeves. A net exposure of zero is dollar neutral, while a
positive value means the portfolio has more dollars long than short.

<div class="research-figure portfolio-exposure-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/portfolio-exposures-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/portfolio-exposures-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/portfolio-exposures.svg">
    <img src="/assets/multiple-linear-regression/portfolio-exposures.png" alt="Monthly long gross, short gross, and net stock exposure of the selected Ridge portfolio" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 7:</strong> Monthly average floating exposures for the selected Ridge portfolio; the rule marks the 2022 boundary.</p>

The long book stays near its 100% ceiling for much of the sample. Most of the
movement in net exposure comes from the short book, which contracts when the
selected high-volatility stocks receive smaller inverse-volatility weights.
Average net exposure rises from +30.0% in development to +46.9% after 2021.
Market beta remains much smaller because the short stocks carry more beta per
dollar. A portfolio risk model would control both quantities directly. That
would make the offset an explicit allocation choice.

### Realized predictor tilts

The realised tilts show which predictor characteristics the Ridge portfolio
owns. Let $$\mathcal H_t$$ be the held stocks on date $$t$$,
$$x_{i,j,t}$$ stock $$i$$'s normalized rank on predictor $$j$$, and $$w_{i,t}$$
its signed portfolio weight. I calculate

$$
T_{j,t}
=\frac{\sum_{i\in\mathcal H_t}w_{i,t}x_{i,j,t}}
{\sum_{i\in\mathcal H_t}\lvert w_{i,t}\rvert}.
$$

The denominator uses the gross weight with a non-missing value for that
predictor; all ten displayed series have complete coverage. Positive values mean
that the long book owns higher ranks than the short book; negative values mean
lower ranks; zero means a neutral tilt. I calculate the tilts daily and
average them by quarter. Each panel includes zero and uses its own range, rounded
outward. The panels therefore show changes through time. Use the labelled
full-sample means for cross-panel magnitudes because each panel has its own scale.

ATR is average true range relative to price, so it captures both the daily
high-low range and gaps from the previous
close. Total, upside, and downside volatility are rolling standard deviations of
all, positive, or negative daily returns; in the one-sided versions, returns on
the other side are set to zero. A trend streak such as 200/126d is the share of
the last 126 sessions that price spent above its 200-session moving average.
Price/prior high compares price with its 252-session high while skipping the
latest 21 sessions, and 252-day RSI compares average gains with average losses
over the past year. As with the other inputs, the model sees cross-sectional
ranks of these quantities.

<div class="research-figure exposure-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/portfolio-feature-tilts-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/portfolio-feature-tilts-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/portfolio-feature-tilts.svg">
    <img src="/assets/multiple-linear-regression/portfolio-feature-tilts.png" alt="Quarterly portfolio-weighted predictor-rank tilts for the selected Ridge portfolio on independent zero-inclusive panel scales" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 8:</strong> Quarterly paths of the ten largest average absolute realized predictor tilts; panels use their own zero-inclusive scales and label the full-sample mean.</p>

Among its ten largest realized tilts, the portfolio is mostly defensive and
trend-following. The long book owns quieter stocks: its ranks are lower on ATR
and the volatility measures. It also owns stocks that have spent
more time above their long-run moving average and remain closer to an earlier
high.

The chart keeps the largest realised tilts rather than a hand-picked diverse
set. It describes the finished portfolio rather than independent alpha
attribution. The top-ten rule hides smaller tilts, several lines are close
variations of one idea, and stock-level volatility scaling can strengthen the
defensive pattern after ranking. Correlated predictors can also exchange
coefficient weight while continuing to identify similar stocks. These two
mechanisms make the portfolio look steadier, and more concentrated by theme,
than the coefficient heatmap suggests.

The broader limitation is feature diversification. Of the 144 inputs, 92 are
direct transformations of returns, price paths, volatility, technical state,
or market correlation; four more combine price with volume. Market
capitalization, trading volume, and publication-lagged short interest add some
breadth. Price history still dominates the deck. The penalty experiment is
consistent with several correlated inputs expressing much the same underlying
effects. At $c=0.1$, about 39 of 150 selected names change relative to OLS on a
typical rebalance. Development Sharpe remains close at 0.99, and the largest
realized tilts are still defensive and trend-led.

The finished signal has limited feature diversification, though the changed
portfolios can still own different sources of alpha. Cross-sectional ranking
removes magnitude, broad 75-stock tails preserve substantial overlap, and
inverse-volatility sizing can pull different rankings toward similar defensive
exposures and returns. A grouped leave-one-family-out test, run both before and
after the allocation rule, would distinguish genuinely incremental information
from convergence introduced by normalization, selection, and sizing.

## Conclusion

Multiple linear regression turns many stock predictors into one ranking. The OLS
portfolio records a development Sharpe of 0.98, compared with 0.71 for the benchmark.
Annualized return stays close, while volatility and maximum drawdown fall. This
comparison covers two complete specifications. A stricter weights-only test
would give both methods the same predictors and data history.

Ridge produces a tidier coefficient vector and nearly the same portfolio. At
$c=0.01$, coefficient magnitude and refit movement fall by roughly
one third, while the rank correlation with OLS remains 0.991. Development
Sharpe is 1.00 for Ridge and 0.98 for OLS. From January 2022 through May 2026,
the figures are 0.82 and 0.87. The regularisation changes coefficient scale far
more than the trading signal.

The main limits come from the research design and the allocation. Overlapping
targets, common shocks within each date, and repeated use of the development
history reduce the independent information in the sample. The 21-session purge
and date-blocked walk-forward design address leakage across test boundaries;
equal-date weighting and genuinely non-overlapping training dates remain
robustness tests. A fuller implementation estimate would add borrow, financing,
market impact, and taxes. The
predictor deck also remains concentrated in related price-based measures, so a
stable final ranking sits alongside limited feature diversification.

The clearest next step is a better portfolio risk model. The current allocation
scales each stock by its own volatility. A covariance model would also capture
correlations between positions and size the portfolio jointly. The objective
could penalize turnover from current holdings, while constraints control gross
and net exposure, market beta, sectors, and the largest realized factor tilts.
I would test that risk model on frozen OLS and Ridge predictions, then lock the
complete prediction-and-allocation rule before opening a genuinely new period.
