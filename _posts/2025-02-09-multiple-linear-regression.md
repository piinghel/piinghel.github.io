---
layout: post
title: "Combining Stock Signals with Multiple Linear Regression"
date: 2025-02-09
last_modified_at: 2026-08-23
categories: [Quants]
article_label: Factor combination · Multiple linear regression
permalink: /quants/2025/02/09/multiple-linear-regression.html
---

<p class="article-summary"><strong>TL;DR:</strong> Stock signals often disagree, so the practical problem is how to combine them into one ranking. I compare a transparent fixed score with weights learned by OLS and Ridge. During development, OLS raises net Sharpe from 0.72 to 0.98 while keeping annualised net return near 7% and cutting volatility from 9.69% to 7.15%. That advantage does not survive the 2022–2026 period: net Sharpe is 0.82 for Ridge and 0.87 for OLS. Learning the combination can improve the historical fit, but it does not guarantee a better later-period ranking.</p>

The problem is not a lack of signals; it is disagreement. A stock can have strong
momentum but high risk, or attractive size but crowded positioning. The measures
also use different units and lookback periods, so averaging their raw values
would be meaningless. I need one score that turns those imperfect, overlapping
clues into a ranking. Fixed weights make that choice by hand; multiple linear
regression uses past data to learn the combination.

The model's job is simple: put the stocks in order. On each date, the
highest-scoring stocks become long candidates and the lowest-scoring ones become
short candidates. The score is not a return forecast; only the order matters.

I compare three ways to form that order: a transparent fixed-weight score,
ordinary least squares (OLS), and Ridge, which discourages large coefficients.
Fixed weights versus OLS is a practical comparison, but both the inputs and the
combination rule change. OLS versus Ridge is controlled: the predictors, target,
and portfolio remain fixed, and only the estimation method changes.

## The fixed benchmark

I do not want the regression to win merely because it is more complicated. The
benchmark therefore uses a small set of familiar, economically motivated signals with fixed signs
and equal theme weights. Every choice is visible, the score still works with
uneven data histories, and I know in advance how much influence one strong theme
can have. That makes it a useful hurdle for the learned ranking. The trade-off is
that the factor choices, lookbacks, and signs all embed judgment.

The benchmark has five economic themes. Six raw signals enter because the
defensive theme combines two related questions:

**Is risk contained?** Low volatility rewards stocks whose returns have been
quiet over one, three, and six months. Upper-tail avoidance penalises a recent
path that depends on a few unusually large gains. Together they form one
defensive theme, with lower values preferred for both ingredients.

**Is there a persistent trend?** Momentum looks for a return pattern that has
survived several months, while skipping the latest month so that a short-term
reversal does not masquerade as a trend. Higher values are preferred.

**Is the trade crowded?** Low short interest favours stocks with less reported
short positioning relative to their trading activity. The measure is deliberately
lagged, so the score uses information that could have been known at the signal
date. Lower values are preferred.

**Is the company large and investable?** Capitalisation supplies a plain size
and investability tilt. Higher values are preferred.

**Is the return path dependable?** Return consistency counts how often a stock
has lost money on a daily basis over roughly three years. It treats the
frequency of losing days separately from the size of any one loss. Lower values
are preferred.

### Exact construction

The paragraphs above explain the economic intent. The equations below are the
implementation record: they fix the exact windows and transformations used by
the benchmark. The reader need not memorise the notation. For stock $$i$$ on
date $$t$$, let $$r_{i,t}$$ be its daily total return, $$v_{i,t}$$ its daily
trading volume, $$h_{i,t}$$ its reported shares short, $$m_{i,t}$$ its raw market
capitalisation, and $$\mathcal U_t$$ the eligible cross-section.

**Low volatility.** Average annualised standard deviation over three trailing
windows:

$$
\sigma^{\mathrm{low}}_{i,t}
= \frac{1}{3}\sum_{k\in\{21,63,126\}}
  \sqrt{252}\,\operatorname{sd}(r_{i,t-k+1:t}).
$$

**Upper-tail avoidance.** The third-largest daily return in the most recent
21 sessions:

$$
\tau_{i,t}=\operatorname{3rd\ largest}\{r_{i,t-j}:j=0,\ldots,20\}.
$$

**Momentum.** Average compounded return over four horizons, always starting
after the most recent 21 sessions:

$$
\mu_{i,t}=\frac{1}{4}\sum_{k\in\{63,126,189,252\}}
\left(\prod_{j=21}^{k+20}(1+r_{i,t-j})-1\right).
$$

**Short positioning.** Reported shares short, lagged by 21 sessions, divided by
the preceding 63-session average trading volume. The logarithm keeps a ratio
from being dominated by its raw scale:

$$
\kappa_{i,t}=\log\left(\frac{h_{i,t-21}}
  {\frac{1}{63}\sum_{j=21}^{83}v_{i,t-j}}\right).
$$

**Capitalisation.** Raw market capitalisation:

$$
c_{i,t}=m_{i,t}.
$$

**Return consistency.** Fraction of negative daily returns over the preceding
756 sessions:

$$
\rho_{i,t}=\frac{1}{756}\sum_{j=0}^{755}
\mathbf 1\{r_{i,t-j}<0\}.
$$

Lower $$\sigma^{\mathrm{low}}$$, $$\tau$$, $$\kappa$$, and $$\rho$$ are
preferred; higher $$\mu$$ and $$c$$ are preferred. The notation is deliberately
explicit: it records the information cutoff, the lookback, and the direction
of every benchmark ingredient.

Each raw measure is converted into a signed cross-sectional rank. For a measure
whose preferred direction is high, the score is

$$
s_{i,t}(x)
=2\frac{\operatorname{rank}_{\mathcal U_t}(x_{i,t})-1}
{|\mathcal U_t|-1}-1;
$$

for a measure whose preferred direction is low, I use $$-s_{i,t}(x)$$. Thus
the largest eligible company receives a capitalisation score near $$+1$$ and
the smallest receives a score near $$-1$$. The model uses these ranks rather
than the raw units.

Each raw component is ranked across current Russell 1000 members on the same
date, mapped to a score from −1 to +1, and signed so that a higher value is more
attractive. For each stock and date, I first average the low-volatility and
tail-avoidance scores. I then give that defensive score and each of the other
four themes an equal 20% weight. The two related measurements therefore share
one theme weight.

I combine the five themes at the **signal level**, before portfolio formation.
That gives me one stock ranking and one portfolio to manage, rather than five
separate factor portfolios. I chose this deliberately simple implementation
because it is practical: benchmark and regression can share the same selection,
weighting, execution, and cost machinery. A stock must have every required
component rank, so missing themes remove it from that date's benchmark universe
instead of changing the weights on the remaining themes.

Those six measures define the transparent benchmark, not the full regression
input. OLS and Ridge receive a broader deck of 144 ranked predictors, including
multiple horizons of return and trend, total and downside volatility, technical
price location, market-cap and market-correlation measures, trading activity and
price-volume interaction, and publication-lagged short positioning. Examples
include price relative to a moving average, RSI, ATR, upside and downside
volatility, share turnover, illiquidity, market-cap variability, and
short-interest-to-volume. The extra horizons and related transformations are
deliberate: the regression tests whether a learned combination improves on the
small hand-built benchmark.

### Testing the ingredients

Before combining the factors, I ran the six components separately over their
common May 1997–May 2026 sample. Each component ranks the universe, buys the top 75,
and shorts the bottom 75. Positions start equally within each leg and are then
scaled by inverse 60-session stock volatility, subject to the common 4% cap and
100% gross ceiling per leg described below. The reported portfolio averages
three offset execution calendars and pays 5 basis points per dollar traded.

| Component | Gross return | Net return | Net volatility | Net Sharpe |
| --- | ---: | ---: | ---: | ---: |
| Low volatility | 7.04% | 6.38% | 10.42% | 0.61 |
| Upper-tail avoidance | 6.54% | 5.03% | 8.81% | 0.57 |
| Momentum | 4.90% | 4.27% | 10.37% | 0.41 |
| Low short interest | 2.53% | 1.85% | 4.96% | 0.37 |
| Large capitalization | 1.94% | 1.66% | 7.32% | 0.23 |
| Return consistency | 5.90% | 5.48% | 8.90% | 0.62 |
{: .research-table .comparison-table .component-performance-table }

<p class="table-caption"><strong>Table 1:</strong> Gross and after-cost performance of each standalone 75-long/75-short component portfolio using the common volatility-scaled allocation, May 1997–May 2026. Returns are annualized arithmetic means; net statistics deduct 5 bp per dollar traded.</p>

The defensive measurements and return-consistency signal have the strongest
standalone Sharpes. Together they provide three overlapping views of defensive
behaviour: low volatility and tail avoidance are close variants, while loss
frequency describes another part of the return path. Grouping the first two
keeps the defensive theme at the same weight as momentum, positioning, size,
and return consistency.

The weaker components still clarify the hurdle. Low short interest has a modest
return but also low volatility; large capitalization has a positive return and
the lowest Sharpe. Upper-tail avoidance loses 1.51 percentage points a year to
the stated cost assumption, the largest gross-to-net gap in the table. These histories make each theme a plausible
benchmark ingredient. Their incremental value remains an empirical question
because standalone success can disappear when signals overlap or when a model
assigns conditional weights.
{: .table-followup }

The table also shows that equal signal weights produce unequal risk
contributions. The defensive components produce much higher standalone
volatility than low short interest, and their realized portfolios overlap more.
The fixed score is equal-weighted before stock selection; the portfolio process
can still concentrate the resulting risk in a smaller set of related themes.

Figure 1 separates two kinds of dependence. **Signal correlation** asks whether
two factors rank the same stocks similarly on the same date. **Return
correlation** asks whether portfolios formed from those signals subsequently
earn similar daily returns. Low signal correlation indicates differentiated
rankings; low return correlation indicates diversification in realized paths.
Together they describe dependence at two different stages. Incremental value
after combination requires the controlled model and portfolio evidence that
follows.

<div class="research-figure component-evidence-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/benchmark-dependence-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/benchmark-dependence-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/benchmark-dependence.svg">
    <img src="/assets/multiple-linear-regression/benchmark-dependence.png" alt="Heatmaps comparing same-date component rank correlations with subsequent component-portfolio return correlations" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Same-date rank correlations between component signals (left) and subsequent daily-return correlations between their standalone portfolios (right), on the common sample.</p>

The two heatmaps show different forms of dependence. Low volatility and tail avoidance have
a 0.75 signal correlation, while every other signal pair has absolute
correlation no greater than 0.32. Their portfolio-return correlation is higher
still at 0.85; the median return correlation across all pairs is 0.30. Shared
holdings and common risk exposures can make realized returns converge even when
the original rankings differ. The heatmaps are diversification diagnostics; the
later joint models test conditional forecasting value.

The benchmark is intentionally modest. I chose its factors and horizons with
historical results in mind; several themes are correlated; and data availability
changes through time. Positive standalone performance may also disappear once the
other factors enter the model. The regression receives a broader predictor
set, so benchmark versus OLS compares two complete ranking methods. The
controlled estimator comparison begins with OLS versus Ridge, where the inputs
are identical.

## A common score scale

A regression can combine billions of dollars with percentage points, but its
raw coefficients then live on incomparable scales. For the 144-predictor
regression deck, I therefore replace every predictor with its relative ordering
across the eligible Russell 1000 universe, then map the ranks to $[-1,1]$:

$$
x^{\mathrm{rank}}_{i,t}=2\frac{\operatorname{rank}(x_{i,t})-1}{N_t-1}-1.
$$

Ranking discards the raw magnitudes and replaces them with bounded ranks.
Predictors in different units become
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
{\sigma(r_{i,t+1:t+20})}.
$$

I use this forward Sharpe-like outcome to prefer a return distributed through
the month over the same return produced by a few volatile days. The model ranks
this target; portfolio Sharpe remains a downstream outcome. The annualization
factor leaves the ordering unchanged. A raw-return target is a plausible
alternative and could produce a riskier learned score.

I rank the outcome within its date and sector. Targets are never imputed.
Predictor ranks retain cross-sector information, while target ranks ask which
stocks subsequently did better than their sector peers. This reduces
sector-level movement in the label. Portfolio selection remains global, so the
final holdings can still carry sector exposures; an allocation risk model would
have to constrain them explicitly.

## Learning the signal weights

With normalized predictors in $x_{i,t}$ and the normalized forward target in
$y_{i,t}$, ordinary multiple linear regression estimates

$$
(\widehat\beta_0,\widehat\beta)
=\arg\min_{\beta_0,\beta}
\sum_{(i,t)\in\mathcal T}
\left(y_{i,t}-\beta_0-x_{i,t}^{\top}\beta\right)^2.
$$

The fitted score $\widehat y_{i,t}=\widehat\beta_0+x_{i,t}^{\top}\widehat\beta$
becomes the learned stock ranking. A positive coefficient rewards a high rank
on that predictor; a negative coefficient reverses the preference.

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
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/walk-forward-mobile.png?v=3">
    <img src="/assets/multiple-linear-regression/walk-forward.png?v=3" alt="Expanding walk-forward training windows separated from each next test block by a 21-session gap" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Expanding walk-forward estimation, with each training history separated from its next 600-date prediction block by a 21-session purge.</p>

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

## Adding coefficient shrinkage

Correlated predictors can divide weight erratically. Ridge changes the same
linear regression by adding an L2 penalty:

$$
(\widehat\beta_0,\widehat\beta)
=\arg\min_{\beta_0,\beta}
\left\{
\frac{1}{n_t}\sum_{(i,s)\in\mathcal T_t}
\left(y_{i,s}-\beta_0-x_{i,s}^{\top}\beta\right)^2
+c\lVert\beta\rVert_2^2
\right\}.
$$

The penalty applies to the slopes and leaves the intercept free. Setting $c=0$
gives the exact OLS baseline. Positive values shrink coefficients and can make
correlated inputs share weight more evenly. Shrinkage follows directly from the
objective; any predictive improvement has to appear in the data.

Here $c$ is the penalty next to **mean** squared error. The implementation uses
[`sklearn.linear_model.Ridge`](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html),
whose documented objective is a residual sum of squares plus
$\alpha\lVert\beta\rVert_2^2$. The equivalent parameter in training fold $t$ is
therefore $\alpha_t=n_t c$. Divide scikit-learn's objective by $n_t$ and the
equation above follows exactly. This scaling keeps the relative penalty fixed as
an expanding fold contains more rows. It is an algebraic conversion between sum
and mean loss, while the dependence between rows remains a separate statistical
problem. At $c=0$ the objective is OLS;
scikit-learn recommends `LinearRegression` rather than `Ridge(alpha=0)` for
numerical reasons.

The rows are not independent: stocks share market and sector shocks, predictors
move slowly, and adjacent 20-session targets overlap. A 21-session purge keeps a
training target out of the next prediction block, while 600-date walk-forward
blocks avoid random row-level validation. Some overlap remains, so the penalty
choice is a sensitivity check rather than a claim of millions of independent
observations.

## Choosing the Ridge penalty

All four candidates use the same predictors, target, universe, dates,
walk-forward procedure, portfolio construction, and 5 bp cost assumption. The
penalty is not estimated by the regression. I compare the small grid
$$c\in\{0,0.001,0.01,0.1\}$$ using only data through 2021, and prefer a value
that behaves consistently across the full development period, its final ten
years, and its final five years rather than one that wins a single slice.

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

<p class="table-caption"><strong>Table 2:</strong> Development-period annualized arithmetic return across the matched OLS–Ridge penalty grid before and after 5 bp per dollar traded; volatility and Sharpe use net returns.</p>

I choose the moderate $c=0.01$ specification as a development-period
compromise. Relative to OLS, annualized return rises by 0.35 percentage points
and volatility by 0.21, producing a Sharpe improvement of only 0.020. Over the
final ten years, the Sharpe is nearly unchanged; over the final five, the gain
is 0.008, and $c=0.001$ does slightly better. These differences are economically
small. Although $c=0.1$ earns more return, it also takes more risk, and its
weaker shorter-window Sharpes argue against selecting it on full-period return
or mean IC alone. Across the final ten and five development years, respectively,
Sharpe is 1.118/0.975 for OLS, 1.119/0.987 for $c=0.001$, 1.120/0.983 for the
selected $c=0.01$, and 1.060/0.941 for $c=0.1$.
{: .table-followup }

### What shrinkage changes

Figure 3 shows two practical changes relative to OLS.
Portfolio membership counts how many of the 75 longs and 75 shorts differ from
the OLS portfolio on an average rebalance. Coefficient shrinkage reports the
percentage reduction in the coefficients' Euclidean size (L2 norm) and in their
mean absolute change between adjacent refits. Higher values in either panel mean
that Ridge has moved further away from OLS. Prediction accuracy is evaluated
separately with rank IC and portfolio results.

<div class="research-figure alpha-sensitivity-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/alpha-sensitivity-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/alpha-sensitivity-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/alpha-sensitivity.svg">
    <img src="/assets/multiple-linear-regression/alpha-sensitivity.png" alt="Average portfolio-membership changes and coefficient shrinkage relative to OLS across the Ridge penalty grid" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Average portfolio-membership changes and coefficient shrinkage relative to matched OLS during the development period.</p>

At $c=0.01$, about 14 of the 150 selected names change on a typical rebalance.
Across the full cross-section, the average stock moves 2.71 percentile-rank
points and prediction ranks retain a 0.991 correlation with OLS. At the same
time, the coefficient norm and refit movement fall by roughly one third. The
stronger $c=0.1$ penalty changes about 39 names, moves the average stock 7.79
rank points, and cuts both coefficient measures by about 70%. Shrinkage is
therefore material before the portfolio becomes radically different. Figure 3
measures distance from OLS; the later IC evidence measures whether the changed
ranking is more accurate.

Other development-only coefficient diagnostics change less. Adjacent
coefficient-vector correlation is 0.932 for $c=0.01$ versus 0.934 for OLS, sign
agreement rises from 89.4% to 90.0%, and the top 20 coefficients' share of total
absolute weight falls from 41.4% to 38.6%. Ridge makes the weights smaller and a
little less concentrated. Adjacent-refit correlation remains essentially
unchanged, so overall coefficient stability is still limited.

How can coefficients move this much while the final rankings remain so similar?
The prediction depends on $X\beta$, not on $\beta$ by itself. If two predictors
move together, adding weight to one and removing offsetting weight from the
other can leave their combined score almost unchanged. More generally,

$$
\Delta\widehat y=X\,\Delta\beta
$$

can be small even when $\Delta\beta$ is large if the coefficient change lies in
a direction where the correlated feature matrix has little variation. OLS then
has weakly identified individual weights but a better-identified prediction.
Ridge chooses a smaller-norm point among many nearly equivalent coefficient
combinations. That numerical regularity is useful. Economic attribution remains
weak because the data identify combinations of correlated predictors more
clearly than the coefficient on any single horizon.

A narrower alternative is that rank stability comes only from the 75-stock
selection cutoff: scores may move without enough names crossing the boundary.
That explains some portfolio overlap, but not the 0.991 rank correlation
measured across the whole stock universe. The broader evidence therefore points
more strongly to substitution among correlated predictors than to a cutoff
artifact alone.

This is the distinction I care about. The 0.991 prediction-rank
correlation says the stock ordering is robust to moderate shrinkage; the less
stable coefficient cells say attribution to individual, correlated inputs is
fragile. Economic interpretation should therefore emphasize persistent groups
of related predictors and realized portfolio tilts. If individual coefficients
were the research target, the next experiment would need grouped or
orthogonalized inputs and explicit tests of group-level stability—not a stronger
claim from the same heatmap.

The heatmap provides a less aggregated coefficient check. It keeps the ten
predictors with the largest mean absolute coefficient in the selected Ridge
model and shows their signed value at each refit, averaged across the three
date-thinned ensemble members. Because every input is mapped to the same
$[-1,1]$ rank scale, values are comparable within the model. Positive cells
raise the score when a stock ranks highly on that predictor; negative cells
reverse the preference. These are conditional weights among correlated inputs,
not standalone factor returns or causal effects. The 2022 and 2024 columns are
later-period diagnostics and did not enter the development-only selection
statistics.

<div class="research-figure coefficient-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/top-coefficients-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/top-coefficients-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/top-coefficients.svg">
    <img src="/assets/multiple-linear-regression/top-coefficients.png" alt="Heatmap of the ten largest average absolute coefficients for the selected Ridge specification across twelve walk-forward refits" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Signed coefficients for the selected Ridge model's ten largest mean absolute weights across walk-forward refits; the 2022 and 2024 columns are later-period diagnostics.</p>

The clearest directions persist: price relative to its 126-session moving
average stays positive, while short-horizon moving-average convergence/divergence
(MACD) and illiquidity stay negative.
Other weights weaken or change sign as the sample expands. Combined with the
summary statistics above, this suggests Ridge mainly reduces coefficient scale
and concentration; it does not eliminate time variation in which correlated
predictor receives the weight.

### Development-period portfolio results

The development portfolio comparison needs two caveats. Its return history
begins with the first mechanical walk-forward predictions in 1998, within the
declared 1995–2021 research period. The fixed score also uses a smaller,
hand-built signal set and has different data availability; OLS and Ridge use
the same larger predictor set. Only OLS versus Ridge is a controlled estimator
comparison.

| Development metric | Fixed | OLS | Ridge $c=0.01$ |
| --- | ---: | ---: | ---: |
| Annualized return, gross | 7.66% | 8.49% | 8.82% |
| Annualized return, net | 6.96% | 7.03% | 7.38% |
| Annualized volatility | 9.69% | 7.15% | 7.36% |
| Sharpe ratio | 0.72 | 0.98 | 1.00 |
| Maximum drawdown | −31.70% | −18.77% | −19.03% |
| Market beta | 0.089 | 0.084 | 0.091 |
| Turnover per rebalance | 79.56% | 167.67% | 165.72% |
| Annual cost drag | 0.69 pp | 1.46 pp | 1.44 pp |
{: .research-table .comparison-table .period-metrics-table }

<p class="table-caption"><strong>Table 3:</strong> Development-period portfolio results. Gross return is before the stated trading cost; all risk statistics use returns after 5 bp per dollar traded.</p>

The learned portfolios have higher Sharpes than the benchmark, with similar
annualized returns, lower volatility, and shallower drawdowns. The price is
roughly double the benchmark's turnover and annual cost drag. Ridge reduces
turnover by only 1.95 percentage points per rebalance relative to OLS and saves
about 0.02 percentage points a year. Coefficient shrinkage is meaningful; the
trading-cost change is negligible.
{: .table-followup }

## The 2022–2026 evaluation

The reported $c=0.01$ choice follows the development-only rule above; no
2022–2026 result enters that rule. The later history had nevertheless already
influenced earlier feature, target, portfolio, and presentation work. Calling it
a pristine holdout would be false. I therefore treat 2022–May 2026 as a
**pseudo-holdout robustness test**. A genuinely untouched test would require a
specification demonstrably locked before anyone examined those outcomes.

| Later-period metric | Fixed | OLS | Ridge $c=0.01$ |
| --- | ---: | ---: | ---: |
| Annualized return, gross | 7.52% | 8.84% | 8.68% |
| Annualized return, net | 6.92% | 7.50% | 7.37% |
| Annualized volatility | 11.35% | 8.64% | 8.95% |
| Sharpe ratio | 0.61 | 0.87 | 0.82 |
| Maximum drawdown | −10.78% | −7.59% | −8.05% |
| Market beta | 0.032 | 0.075 | 0.078 |
| Turnover per rebalance | 68.80% | 152.75% | 149.61% |
| Annual cost drag | 0.60 pp | 1.34 pp | 1.31 pp |
{: .research-table .comparison-table .period-metrics-table }

<p class="table-caption"><strong>Table 4:</strong> Later-period portfolio results. Gross return is before the stated trading cost; all risk statistics use returns after 5 bp per dollar traded.</p>

The later period reverses the small development-period advantage. Ridge return is 0.13
percentage points lower than OLS,
volatility is 0.30 points higher, and Sharpe falls from 0.87 to 0.82. Its maximum
drawdown and beta are also slightly worse. Turnover and costs fall modestly,
but not enough to offset the risk-adjusted performance gap. The tiny
$c=0.001$ candidate happens to have the best later Sharpe at 0.89; promoting it
after seeing this period would be post-hoc selection, so I do not.
{: .table-followup }

The selected Ridge portfolio becomes more net long in the later period because
its short leg carries less gross weight. Its average net stock exposure rises
from +30.0% to +46.9%, while market beta remains only 0.078. Dollar exposure and
market beta are measuring different risks. The exposure path appears later in
the portfolio diagnostics, where the daily series is more informative than
another set of table averages.

### Does the ranking improve?

The information coefficient asks a different question from portfolio Sharpe. On
each date it is the cross-sectional Spearman correlation between the predicted
score and the subsequently realized, sector-ranked target on their common stock
sample:

$$
\mathrm{IC}_t=\rho_{\mathrm S}(\widehat y_{i,t},y_{i,t}).
$$

The IC history starts with the first walk-forward predictions in September 1998
and ends on April 28, 2026, the last date for which the full 20-session outcome
is available.

Figure 5 accumulates those daily correlations. A rising path means the model has
usually ordered future outcomes correctly; a flat path means no additional
cumulative rank association, and a decline means a run of negative IC. The sum
is a prediction diagnostic, not a return series or a significance statistic.

<div class="research-figure ic-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/cumulative-ic-mobile.png?v=3">
    <img src="/assets/multiple-linear-regression/cumulative-ic.png?v=3" alt="Cumulative daily cross-sectional rank information coefficient for fixed weights, OLS, and selected Ridge with the 2022 boundary marked" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Cumulative daily cross-sectional Spearman information coefficient for the fixed score, OLS, and selected Ridge predictions; the rule marks the 2022 pseudo-holdout boundary.</p>

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
      <td data-label="Mean daily IC">0.0407</td>
      <td data-label="IC standard deviation">0.1218</td>
      <td data-label="IC IR">0.334</td>
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
      <td data-label="Mean daily IC">0.0506</td>
      <td data-label="IC standard deviation">0.1397</td>
      <td data-label="IC IR">0.363</td>
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

<p class="table-caption"><strong>Table 5:</strong> Mean and standard deviation of daily rank IC, with IC IR defined as mean divided by standard deviation, shown separately for development and later periods.</p>

During development, Ridge raises mean IC over OLS by only 0.0008 and also raises
its standard deviation, leaving IC IR fractionally lower at 0.530 versus 0.534.
In the later period its mean IC is fractionally lower than OLS and its dispersion
is higher. The cumulative paths therefore tell the same story as the table: OLS
and moderate Ridge produce almost the same ordering, and shrinkage does not add
a clear prediction-quality gain.

The fixed score has the highest later-period mean IC but also the most variable
daily IC, so its IC IR remains below OLS. That does not contradict the portfolio
results. IC measures the ordering of the entire eligible cross-section against
the normalized target; portfolio return depends only on names near the tails,
then adds position sizing, stock-level volatility scaling, execution, and
costs. The differing predictor sets also prevent fixed score versus OLS from
being a controlled estimator comparison.

### Performance through time

Portfolio performance adds selection, volatility scaling, execution, and costs
to that prediction evidence. Figure 6 shows the complete net path and the
drawdowns behind the period summaries rather than adding another performance
statistic.

<div class="research-figure performance-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/performance-and-drawdowns-mobile.png?v=3">
    <img src="/assets/multiple-linear-regression/performance-and-drawdowns.png?v=3" alt="Net growth and drawdowns for fixed weights, OLS, and selected Ridge with development and later periods separated" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 6:</strong> Net cumulative performance and drawdowns for the three ranking systems after charging 5 bp per dollar traded; the rule separates development from the later period.</p>

Figure 6 makes the learned portfolios' lower volatility and shallower
development drawdowns visible through time. Ridge remains close to OLS, and its
small development advantage disappears after 2021. The vertical rule marks the
specification boundary; earlier research reuse still makes the later period a
pseudo-holdout.

## What the portfolio is actually doing

### Turnover and cost

A useful ranking is not necessarily a portfolio I would trade. The next
diagnostics ask what the finished portfolio owns and what it costs to maintain.
Figure 7 begins with turnover: the absolute long- and short-side trading at each
rebalance, divided by equity. I charge 5 basis points per dollar traded and
compound the resulting net returns. The estimate covers stock trading but
excludes borrow, financing, market impact, and taxes. Applying the same rule to
every portfolio gives a useful first comparison of how much turnover eats into
returns.

<div class="research-figure turnover-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/turnover-and-costs-mobile.png">
    <img src="/assets/multiple-linear-regression/turnover-and-costs.png" alt="Turnover per rebalance and annual cost drag for fixed weights, OLS, and selected Ridge in development and later periods" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 7:</strong> Average two-way turnover per rebalance and annual return drag from the 5 bp trading-cost assumption, shown separately for development and the later period.</p>

The fixed score is clearly cheaper. Ridge barely changes the higher turnover
inherited from the learned monthly ranking: versus OLS, the selected penalty
saves 0.02 percentage points of annual return in development and 0.03 in the
later period. That difference is too small to motivate the penalty by itself.

### Capital and market exposure

Figure 8 shows how the selected Ridge portfolio uses capital through time. Long
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

<p class="figure-caption"><strong>Figure 8:</strong> Monthly average floating exposures for the selected Ridge portfolio; the rule marks the 2022 pseudo-holdout boundary.</p>

The long book stays near its 100% ceiling for much of the sample. Most of the
movement in net exposure comes from the short book, which contracts when the
selected high-volatility stocks receive smaller inverse-volatility weights.
Average net exposure rises from +30.0% in development to +46.9% after 2021.
Market beta remains much smaller because the short stocks carry more beta per
dollar. A portfolio risk model would control both quantities directly instead
of relying on this offset to emerge from stock-level scaling.

### Realized predictor tilts

Figure 9 asks which predictor characteristics the Ridge portfolio actually
owns. Let $x_{i,j,t}$ be stock $i$'s normalized rank on predictor $j$, and let
$w_{i,t}$ be its signed portfolio weight. I calculate

$$
T_{j,t}=\frac{\sum_i w_{i,t}x_{i,j,t}}
{\sum_i\lvert w_{i,t}\rvert}.
$$

The denominator uses the gross weight with a non-missing value for that
predictor; all ten displayed series have complete coverage. Positive values mean
that the long book owns higher ranks than the short book; negative values mean
lower ranks; zero means no directional tilt. I calculate the tilts daily and
average them by quarter. Each panel includes zero but uses its own range, rounded
outward. The panels therefore show changes through time; compare cross-panel
magnitudes using the labelled full-sample means, not apparent line height.

The feature names need a little translation. ATR is average true range relative
to price, so it captures both the daily high-low range and gaps from the previous
close. Total, upside, and downside volatility are rolling standard deviations of
all, positive, or negative daily returns; in the one-sided versions, returns on
the other side are set to zero. A trend streak such as 200/126d is the share of
the last 126 sessions that price spent above its 200-session moving average.
Price/prior high compares price with its 252-session high while skipping the
latest 21 sessions, and 252-day RSI compares average gains with average losses
over the past year. As with the other inputs, the model sees cross-sectional
ranks of these quantities rather than their raw values.

<div class="research-figure exposure-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/portfolio-feature-tilts-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/portfolio-feature-tilts-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/portfolio-feature-tilts.svg">
    <img src="/assets/multiple-linear-regression/portfolio-feature-tilts.png" alt="Quarterly portfolio-weighted predictor-rank tilts for the selected Ridge portfolio on independent zero-inclusive panel scales" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 9:</strong> Quarterly paths of the ten largest average absolute realized predictor tilts; panels use their own zero-inclusive scales and label the full-sample mean.</p>

Among its ten largest realized tilts, the portfolio is mostly defensive and
trend-following. The long book owns quieter stocks: its ranks are lower on ATR
and the volatility measures. It also owns stocks that have spent
more time above their long-run moving average and remain closer to an earlier
high.

These paths describe the holdings, rather than two independently identified
sources of alpha. The top-ten rule hides smaller tilts, several lines are close
variations of the same idea, and stock-level volatility scaling can strengthen the defensive pattern
after the ranking has already been formed. Correlated predictors can also swap
coefficient weight while continuing to identify similar stocks. Both mechanisms
can leave the final portfolio looking more stable and more concentrated by theme
than the coefficient heatmap suggests.

I keep the largest realized tilts because a hand-picked diverse set would make
the book look broader than it is. Figure 9 is a holdings x-ray, not return
attribution. The allocation rule can amplify the defensive pattern after the
ranking is formed, and it leaves the book materially net long in dollars even
when realized beta is fairly small. That points to the portfolio layer, not a
different way of selecting ten lines for the chart.

The broader limitation is feature diversification. Of the 144 inputs, 92 are
direct transformations of returns, price paths, volatility, technical state,
or market correlation; four more combine price with volume. Market
capitalization, trading volume, and publication-lagged short interest add some
breadth, but price history still dominates the deck. The penalty experiment is
consistent with several correlated inputs expressing much the same underlying
effects: at $c=0.1$, about 39 of 150 selected names change relative to OLS on a
typical rebalance, yet development Sharpe remains close at 0.99 and the largest
realized tilts are still defensive and trend-led.

That is evidence of limited diversification in the finished signal, not proof
that every changed portfolio owns the same alpha. Cross-sectional ranking
removes magnitude, broad 75-stock tails preserve substantial overlap, and
inverse-volatility sizing can pull different rankings toward similar defensive
exposures and returns. A grouped leave-one-family-out test, run both before and
after the allocation rule, would distinguish genuinely incremental information
from convergence introduced by normalization, selection, and sizing.

## Takeaways and further directions

Multiple linear regression is a practical way to turn many stock predictors
into one ranking. In this study, the learned OLS score raises development Sharpe
from 0.72 for the compact benchmark to 0.98. Annualized return stays close to the
benchmark's, while volatility and maximum drawdown fall. The comparison supports
the complete learned specification. A stricter test of learned versus fixed
weights would give both methods the same predictors and data availability.

Ridge $c=0.01$ cuts coefficient magnitude and refit movement by roughly one
third while keeping a 0.991 rank correlation with OLS. Its development Sharpe
is slightly higher, but the advantage is small and disappears in 2022–2026.
Turnover and cost savings are also minor. I would choose Ridge for a more regular
coefficient representation, while expecting almost the same ranking and
portfolio as OLS.

The main limits come from the research design and the allocation. Overlapping
targets, common shocks within each date, and repeated use of the development
history reduce the independent information in the sample. The 21-session purge
and date-blocked walk-forward design address leakage across test boundaries;
equal-date weighting and genuinely non-overlapping training dates remain useful
robustness tests. The 2022–2026 period is a pseudo-holdout, and the 5 bp trading
cost leaves borrow, financing, market impact, and taxes outside the result. The
predictor deck also remains concentrated in related price-based measures, so a
stable final ranking should not be mistaken for broad feature diversification.

The clearest next step is a better portfolio risk model. The current allocation
scales each stock by its own volatility. A covariance model would also capture
correlations between positions and size the portfolio jointly. The objective
could penalize turnover from current holdings, while constraints control gross
and net exposure, market beta, sectors, and the largest realized factor tilts.
I would test that risk model on frozen OLS and Ridge predictions, then lock the
complete prediction-and-allocation rule before opening a genuinely new period.
