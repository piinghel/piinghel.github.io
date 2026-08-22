---
layout: post
title: "Multiple Linear Regression"
date: 2025-02-09
last_modified_at: 2026-08-22
categories: [Quants]
article_mark: /assets/brand/multiple-linear-regression-mark.svg
article_label: Factor combination · Multiple linear regression
permalink: /quants/2025/02/09/multiple-linear-regression.html
---

A stock-selection process rarely has one convincing predictor. It has several
imperfect views of momentum, risk, size, liquidity, and positioning. The
practical problem is turning those views into one ranking without letting a
large or redundant group dominate.

The question here is simple: **Can we combine multiple predictors into a more
useful stock ranking?**

I begin with a fixed-weight factor score, then let ordinary multiple linear
regression learn the combination from earlier data. Ridge appears later as a
penalized version of the same regression. That order matters: the main idea is
the learned linear combination, while the penalty is a stability choice whose
benefit has to be measured.

The result is useful but not a model-victory story. The learned rankings are
stronger than the compact benchmark, although that comparison changes both the
estimator and the information set. In the controlled comparison, a moderate
Ridge penalty makes coefficients smaller and changes the ranking only modestly.
It slightly improves development-period Sharpe, then trails OLS in the later
period. Regularization changes how the model combines predictors; it does not
reliably improve the resulting portfolio in this test.

## A transparent fixed-weight reference

The benchmark contains five economic themes. Six component signals enter
because the defensive theme deliberately groups two related measurements:

- **Defensive:** low volatility is the mean of 21-, 63-, and 126-session
  annualized volatility; upper-tail avoidance is the third-largest daily return
  over 21 sessions. Lower values are preferred. Their normalized signals are
  averaged first, so together they receive one 20% theme weight—not two.
- **Momentum:** the sum of compounded 63-, 126-, 189-, and 252-session returns,
  each skipping the most recent 21 sessions. Higher is preferred and the theme
  receives 20%.
- **Low short interest:** publication-lagged shares short relative to 63-session
  mean trading volume, expressed as a log ratio. Short interest is delayed by
  21 sessions; lower is preferred and the theme receives 20%.
- **Large capitalization:** log market capitalization. Higher is preferred and
  the theme receives 20%.
- **Fewer loss days:** the share of negative daily returns over 756 sessions.
  Lower is preferred and the theme receives 20%.

Each raw component is ranked across current Russell 1000 members on the same
date and signed so that a higher value is more attractive. The two defensive
ranks are averaged, then the five theme ranks are averaged. This is **signal-level
aggregation**: the result is one stock ranking, not an average of five portfolio
returns. That ranking passes through the same long-short portfolio machinery as
the regression. The arrangement is practical because benchmark and model share
the downstream selection, weighting, execution, and cost rules. A stock must
have the required component ranks; missing themes do not cause the available
themes to be silently reweighted.

Before combining the factors, I ran each component separately on their common
May 1997–May 2026 sample. Every portfolio holds 75 longs and 75 shorts, uses
volatility-scaled positions, averages three offset execution calendars, and
pays 5 basis points per dollar traded.

| Component | Return | Volatility | Sharpe |
| --- | ---: | ---: | ---: |
| Low volatility | 6.38% | 10.42% | 0.61 |
| Upper-tail avoidance | 5.03% | 8.81% | 0.57 |
| Momentum | 4.27% | 10.37% | 0.41 |
| Low short interest | 1.85% | 4.96% | 0.37 |
| Large capitalization | 1.66% | 7.32% | 0.23 |
| Fewer loss days | 5.48% | 8.90% | 0.62 |
{: .research-table .comparison-table .component-performance-table }

The table says the ingredients have positive standalone histories, but not
that each adds value after the others are controlled for. Large capitalization,
for example, has a positive return but a low Sharpe. Upper-tail avoidance loses
1.51 percentage points a year to the stated cost assumption. Standalone success
can disappear when signals overlap or when a model assigns conditional weights.
{: .table-followup }

Figure 1 separates two kinds of dependence. **Signal correlation** asks whether
two factors rank the same stocks similarly on the same date. **Return
correlation** asks whether portfolios formed from those signals subsequently
earn similar daily returns. Low signal correlation indicates differentiated
rankings; low return correlation indicates diversification in realized paths.
Neither proves incremental value after combination.

<div class="research-figure component-evidence-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/benchmark-dependence-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/benchmark-dependence-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/benchmark-dependence.svg">
    <img src="/assets/multiple-linear-regression/benchmark-dependence.png" alt="Heatmaps comparing same-date component rank correlations with subsequent component-portfolio return correlations" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 1:</strong> The defensive components
are close both as signals and portfolios. Other pairs can have distinct stock
rankings yet moderately correlated realized returns.</p>

The numbers reinforce the distinction. Low volatility and tail avoidance have
a 0.75 signal correlation, while every other signal pair has absolute
correlation no greater than 0.32. Their portfolio-return correlation is higher
still at 0.85; the median return correlation across all pairs is 0.30. Shared
holdings and common risk exposures can make realized returns converge even when
the original rankings differ. This is a diversification diagnostic, not a test
that either signal adds conditional forecasting value.

The benchmark is intentionally modest. Its factors and horizons were chosen
with historical knowledge; some themes are correlated; availability is unequal
through time; and positive standalone performance need not survive after
controlling for the remaining factors. It is a transparent reference, not a
claim that these are the uniquely correct economic factors.

## Putting unlike predictors on one scale

Regression coefficients are not comparable when one input is measured in
billions of dollars and another in percentage points. On each date I therefore
replace every raw predictor with its relative ordering across the eligible
Russell 1000 universe, then map the ranks to $[-1,1]$:

$$
x^{\mathrm{rank}}_{i,t}=2\frac{\operatorname{rank}(x_{i,t})-1}{N_t-1}-1.
$$

This is not literal winsorization. Ranking discards the raw magnitudes and
replaces them with bounded ranks. Predictors in different units become
comparable, and an extreme raw observation cannot dominate merely because it
is numerically large. The cost is real: the model no longer knows whether two
adjacent ranks were almost tied or far apart.

Missing inputs are first carried forward within the same stock when an earlier
observation exists, then filled with that date-and-sector mean. The completed
predictor is ranked across all current index members on the date, not within
sector. The traded universe later removes stocks below $5, announced merger
targets, and duplicate share classes.

The target uses a different grouping rule. I calculate each stock's annualized
Sharpe-like outcome over the next 20 sessions,

$$
q_{i,t}^{(20)}=\sqrt{252}\,
\frac{\overline r_{i,t+1:t+20}}
{\sigma(r_{i,t+1:t+20})},
$$

and rank that outcome within its date and sector. Targets are never imputed.
Predictor ranks retain cross-sector
information, while target ranks ask which stocks subsequently did better than
their sector peers. This reduces sector-level movement in the label, but it does
not make the final portfolio sector neutral; selection remains global and no
sector constraint is imposed.

## Learning the combination with multiple linear regression

With normalized predictors in $x_{i,t}$ and the normalized forward target in
$y_{i,t}$, ordinary multiple linear regression estimates

$$
(\widehat\beta_0,\widehat\beta)
=\arg\min_{\beta_0,\beta}
\sum_{(i,t)\in\mathcal T}
\left(y_{i,t}-\beta_0-x_{i,t}^{\top}\beta\right)^2.
$$

The fitted score $\widehat y_{i,t}=\widehat\beta_0+x_{i,t}^{\top}\widehat\beta$
is the learned stock ranking. A positive coefficient raises the score when a
stock ranks highly on that predictor; a negative coefficient reverses the
preference. The experiment uses 144 separately normalized predictors; the
substantive question is how their information is combined.

Predictions are walk-forward. The research history begins in January 1995. The
first 900 dates establish the initial training sample, so mechanical
out-of-sample predictions begin in September 1998. Each of 12 fits uses an
expanding history, leaves a 21-session gap around the overlapping 20-session
target, and scores the next 600-date block. Three models trained on complementary
every-third-date samples are averaged at each refit to reduce dependence on
adjacent target windows.

<div class="research-figure walk-forward-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/walk-forward-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/walk-forward-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/walk-forward.svg">
    <img src="/assets/multiple-linear-regression/walk-forward.png" alt="Expanding walk-forward training windows separated from each next test block by a 21-session gap" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 2:</strong> The restored walk-forward
design. Each fit uses past data, a 21-session leakage buffer, and an unseen next
block.</p>

Those predictions are mechanically out of sample at each refit, but 1995–2021
is still the **research and development period**. I repeatedly inspected that
history while revising predictors, normalization, targets, and portfolio rules.
Walk-forward mechanics do not undo research reuse.

## Ridge as a stability extension

Correlated predictors can divide weight erratically. Ridge changes the same
linear regression by adding an L2 penalty:

$$
(\widehat\beta_0,\widehat\beta)
=\arg\min_{\beta_0,\beta}
\left\{
\sum_{(i,t)\in\mathcal T}
\left(y_{i,t}-\beta_0-x_{i,t}^{\top}\beta\right)^2
+\alpha_t\lVert\beta\rVert_2^2
\right\}.
$$

The intercept is not penalized. Setting $\alpha_t=0$ gives the exact OLS
baseline. Positive values shrink coefficients and can make correlated inputs
share weight more evenly. Shrinkage is guaranteed; stronger predictions are not.

The implementation minimizes a **summed** squared error. I set
$\alpha_t=c\,n_t$, where $n_t$ is the number of training rows, so dividing the
objective by $n_t$ gives
$\operatorname{MSE}+c\lVert\beta\rVert_2^2$. This only expresses the penalty
relative to mean rather than summed loss as the window expands. It is not an
argument that millions of stock-date rows are millions of independent pieces
of information.

They are not independent. Stocks on one date share market and sector effects;
predictors move gradually; 20-session forward targets overlap; and expanding
windows reuse related observations. The experiment therefore compares
$c\in\{0,0.001,0.01,0.1\}$ with chronological blocks, a 21-session purge,
three date-thinned ensemble members, and full/final-10-year/final-5-year
development checks. It does not invent a precise effective sample size. Rows
remain equally weighted, so dates with more eligible stocks receive slightly
more aggregate influence; exact equal-date weighting is an important remaining
test.

## Development evidence: choosing the penalty

All four models use the same predictors, target, universe, dates, walk-forward
procedure, portfolio construction, and 5 bp cost assumption. The selection rule
uses only evidence through 2021 and prefers consistency across development
windows rather than the highest Sharpe in any single slice.

| Estimator | Full period | Final 10y | Final 5y |
| --- | ---: | ---: | ---: |
| OLS, $c=0$ | 0.983 | 1.118 | 0.975 |
| Ridge, $c=0.001$ | 0.981 | 1.119 | 0.987 |
| **Ridge, $c=0.01$** | **1.003** | **1.120** | **0.983** |
| Ridge, $c=0.1$ | 0.989 | 1.060 | 0.941 |
{: .research-table .comparison-table .alpha-selection-table }

The moderate $c=0.01$ specification is the most balanced choice. Relative to
OLS, full-development Sharpe rises by 0.020, the final-ten-year result is nearly
unchanged, and the final-five-year result rises by 0.008. These are small
differences, not an economically decisive victory. The stronger $c=0.1$
penalty raises mean daily rank IC from 0.0459 to 0.0476, but also raises IC
dispersion, volatility, drawdown, and beta while reducing Sharpe in the two
shorter development windows. Selecting it on mean IC alone would ignore the
rest of the implementation.
{: .table-followup }

At $c=0.01$, mean daily rank IC rises from 0.0459 to 0.0468, a gain of 0.0009
or about 1.9% of the OLS level, while its daily dispersion rises from 0.0811 to
0.0833. Predictions retain a 0.991 rank correlation with OLS. The average stock
moves 2.71 percentile-rank points and about 14 of the 150 selected names change
on a rebalance.

Using only refits whose test blocks begin before 2022, the coefficient L2 norm and
absolute movement between refits both fall by roughly one third. Adjacent
coefficient-vector correlation is essentially unchanged at 0.932 versus 0.934
for OLS; sign agreement improves only from 89.4% to 90.0%. The top 20
coefficients' share of total absolute weight falls from 41.4% to 38.6%. Ridge
makes weights smaller and a little less concentrated, but it does not turn an
unstable model into a stable one.

<div class="research-figure alpha-sensitivity-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/alpha-sensitivity-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/alpha-sensitivity-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/alpha-sensitivity.svg">
    <img src="/assets/multiple-linear-regression/alpha-sensitivity.png" alt="Development Sharpe, prediction similarity to OLS, and coefficient shrinkage across the OLS and Ridge penalty grid" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 3:</strong> $c=0.01$ is a compromise:
moderate coefficient shrinkage, rankings still close to OLS, and the most
consistent development Sharpe. The later period is not used here.</p>

The development portfolio comparison is also informative, with two important
caveats. Portfolio evidence begins with the first mechanical walk-forward
predictions in 1998, although it belongs to the declared 1995–2021 research
period. The fixed score also uses a smaller, hand-built signal set and has
different availability; OLS and Ridge use the same larger deck. Only OLS versus
Ridge is a controlled estimator comparison.

| Development metric | Fixed | OLS | Ridge $c=0.01$ |
| --- | ---: | ---: | ---: |
| Annualized return | 6.96% | 7.03% | 7.38% |
| Annualized volatility | 9.69% | 7.15% | 7.36% |
| Sharpe ratio | 0.72 | 0.98 | 1.00 |
| Maximum drawdown | −31.70% | −18.77% | −19.03% |
| Market beta | 0.089 | 0.084 | 0.091 |
| Turnover per rebalance | 79.56% | 167.67% | 165.72% |
| Annual cost drag | 0.69 pp | 1.46 pp | 1.44 pp |
{: .research-table .comparison-table .period-metrics-table }

The learned portfolios improve Sharpe mainly by lowering volatility and
drawdown relative to the benchmark, not by producing dramatically higher
returns. Their cost is roughly twice the turnover and annual cost drag. Ridge
reduces turnover by only 1.95 percentage points per rebalance versus OLS and
saves about 0.02 percentage points a year. Coefficient shrinkage is meaningful;
the trading-cost change is not.
{: .table-followup }

## The 2022–2026 later-period evaluation

The reported $c=0.01$ choice follows the development-only rule above; no
2022–2026 result enters that rule. The later history had nevertheless already
influenced earlier feature, target, portfolio, and presentation work. Calling it
a pristine holdout would be false. I therefore treat 2022–May 2026 as a
**pseudo-holdout robustness test**. A genuinely untouched test would require a
specification demonstrably locked before anyone examined those outcomes.

| Later-period metric | Fixed | OLS | Ridge $c=0.01$ |
| --- | ---: | ---: | ---: |
| Annualized return | 6.92% | 7.50% | 7.37% |
| Annualized volatility | 11.35% | 8.64% | 8.95% |
| Sharpe ratio | 0.61 | 0.87 | 0.82 |
| Maximum drawdown | −10.78% | −7.59% | −8.05% |
| Market beta | 0.032 | 0.075 | 0.078 |
| Turnover per rebalance | 68.80% | 152.75% | 149.61% |
| Annual cost drag | 0.60 pp | 1.34 pp | 1.31 pp |
{: .research-table .comparison-table .period-metrics-table }

The main later-period observation is not dramatic but it is unfavorable to the
selected penalty. Ridge return is 0.13 percentage points lower than OLS,
volatility is 0.30 points higher, and Sharpe falls from 0.87 to 0.82. Its maximum
drawdown and beta are also slightly worse. Turnover and costs fall modestly,
but not enough to offset the risk-adjusted performance gap. The tiny
$c=0.001$ candidate happens to have the best later Sharpe at 0.89; promoting it
after seeing this period would be post-hoc selection, so I do not.
{: .table-followup }

<div class="research-figure ic-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/cumulative-ic-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/cumulative-ic-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/cumulative-ic.svg">
    <img src="/assets/multiple-linear-regression/cumulative-ic.png" alt="Cumulative daily cross-sectional rank information coefficient for fixed weights, OLS, and selected Ridge with the 2022 boundary marked" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 4:</strong> OLS and moderate Ridge
produce nearly the same cumulative rank-IC path. Both remain ahead of the fixed
score, but Ridge does not separate from OLS after the specification boundary.</p>

<div class="research-figure performance-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/performance-and-drawdowns-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/performance-and-drawdowns-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/performance-and-drawdowns.svg">
    <img src="/assets/multiple-linear-regression/performance-and-drawdowns.png" alt="Net growth and drawdowns for fixed weights, OLS, and selected Ridge with development and later periods separated" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Net performance after
5 bp per dollar traded. The vertical rule separates development evidence from
the later robustness period; it is not a claim of an untouched holdout.</p>

## What the portfolio is actually doing

Aggregate returns cannot show whether the learned score expresses a plausible,
stable portfolio. The full-history coefficient heatmap makes the internal
combination concrete. Most leading directions persist, including positive
weight on price relative to its 126-session moving average and negative weight
on short-horizon MACD and illiquidity. Market-cap variability has opposing signs
at short and long horizons, and a few effects decay or change sign. These are
conditional regression weights among correlated ranks, not standalone factor
returns or causal effects. The 2022 and 2024 columns are interpretation
diagnostics and did not enter the development-only selection statistics above.

<div class="research-figure coefficient-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/top-coefficients-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/top-coefficients-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/top-coefficients.svg">
    <img src="/assets/multiple-linear-regression/top-coefficients.png" alt="Heatmap of the ten largest average absolute coefficients for the selected Ridge specification across twelve walk-forward refits" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 6:</strong> The ten largest average
absolute coefficients for Ridge $c=0.01$ across the full refit history. Blue
raises the learned score; coral lowers it.</p>

Figure 7 makes the implementation cost explicit. The fixed score is cheaper;
Ridge barely changes the higher turnover inherited from the learned monthly
ranking.

<div class="research-figure turnover-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/turnover-and-costs-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/turnover-and-costs-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/turnover-and-costs.svg">
    <img src="/assets/multiple-linear-regression/turnover-and-costs.png" alt="Turnover per rebalance and annual cost drag for fixed weights, OLS, and selected Ridge in development and later periods" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 7:</strong> Development bars are
solid; later-period bars are hatched. Regularization saves little trading cost
relative to OLS.</p>

The realized long-minus-short exposures provide a second check. The strongest
persistent tilts are defensive: the long book ranks lower on volatility, range,
and downside-volatility measures. Positive tilts toward trend persistence,
distance from a prior high, and long-horizon RSI form the other side. These
paths are generally stable but not constant, and several weaken or briefly
reverse around stressed periods.

<div class="research-figure exposure-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/portfolio-feature-tilts-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/portfolio-feature-tilts-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/portfolio-feature-tilts.svg">
    <img src="/assets/multiple-linear-regression/portfolio-feature-tilts.png" alt="Quarterly long-minus-short predictor-rank exposures for the selected Ridge portfolio" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 8:</strong> Realized predictor-rank
tilts, not coefficients. Negative values mean the long book ranks lower than
the short book on that predictor.</p>

This exposure pattern offers a plausible mechanism for the portfolio's lower
volatility than the fixed benchmark, but it does not establish causality. The
plots are selected by average absolute coefficient or exposure, so they are
descriptive diagnostics rather than independent evidence.

## What was learned—and what remains uncertain

Multiple linear regression is a practical way to turn many stock predictors
into one ranking. In this study the learned OLS score improves development
Sharpe from 0.72 for the compact fixed benchmark to 0.98, largely through lower
volatility and drawdown. Because the signal decks and availability differ, that
is evidence that the complete learned system is useful, not proof that learning
weights beats fixed weights on identical inputs.

The controlled lesson is narrower. Ridge $c=0.01$ cuts coefficient magnitude
and refit movement by roughly one third while keeping a 0.991 rank correlation
with OLS. Its development Sharpe is slightly more consistent, but the advantage
is small and does not persist in 2022–2026. Turnover and cost savings are also
minor. The practical trade-off is therefore coefficient regularity versus an
almost unchanged ranking—not a dependable performance gain.

The next tests should target the remaining design risks: equal aggregate weight
per date, wider date-thinning and block choices, purged date-level validation
blocks, alternative non-overlapping target horizons, and leave-one-theme-out or
residualized tests of incremental value. Most importantly, the next genuine
holdout must begin with the full specification locked in advance. Until then,
the later result is encouraging evidence that the learned ranking remains
useful, but a warning against claiming that Ridge won.
