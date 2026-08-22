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

I want the reference to be useful even if we never fit a regression. So I start
with a small set of familiar, economically motivated signals with fixed signs
and equal theme weights. Every choice is visible, the score still works with
uneven data histories, and I know in advance how much influence one strong theme
can have. That makes it a useful hurdle for the learned ranking. The trade-off is
that the factor choices, lookbacks, and signs all embed judgment.

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
date, mapped to a score from −1 to +1, and signed so that a higher value is more
attractive. For each stock and date, I first average the low-volatility and
tail-avoidance scores. I then give that defensive score and each of the other
four themes an equal 20% weight. Measuring the defensive idea twice therefore
does not give it twice the influence.

The result is one stock ranking, not an average of five portfolio returns. This
is **signal-level aggregation**. That ranking passes through the same long-short
portfolio machinery as the regression, so benchmark and model share the
selection, weighting, execution, and cost rules. A stock must have the required
component ranks; missing themes do not cause the available themes to be silently
reweighted.

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

<p class="table-caption"><strong>Table 1:</strong> Net annualized return, annualized volatility, and Sharpe for each standalone component on the common May 1997–May 2026 sample; every portfolio uses the common 75-by-75 construction and 5 bp trading cost.</p>

The defensive measurements and fewer-loss-days signal have the strongest
standalone Sharpes. That is consistent with a broad defensive effect, but it is
not three independent confirmations of one. Low volatility and tail avoidance
are close variants, and loss frequency also describes the return path. Grouping
the first two prevents the benchmark from rewarding the same idea twice merely
because it was measured twice.

The weaker components still clarify the hurdle. Low short interest has a modest
return but also low volatility; large capitalization has a positive return and
the lowest Sharpe. Upper-tail avoidance loses 1.51 percentage points a year to
the stated cost assumption. These histories justify including plausible themes,
not assuming that each contributes after the others are controlled for.
Standalone success can disappear when signals overlap or when a model assigns
conditional weights.
{: .table-followup }

The table also shows why equal signal weights should not be read as equal risk
contributions. The defensive components produce much higher standalone
volatility than low short interest, and their realized portfolios overlap more.
The fixed score is equal-weighted before stock selection; the portfolio process
can still concentrate the resulting risk in a smaller set of related themes.

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

<p class="figure-caption"><strong>Figure 1:</strong> Same-date rank correlations between component signals (left) and subsequent daily-return correlations between their standalone portfolios (right), on the common sample.</p>

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
controlling for the remaining factors. The regression also receives a broader
predictor deck, so benchmark versus OLS compares two complete ranking systems,
not just fixed versus learned weights on identical inputs. It is a transparent
reference, not a neutral definition of multifactor investing or a claim that
these are the uniquely correct economic factors.

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
{\sigma(r_{i,t+1:t+20})}.
$$

I use this forward Sharpe-like outcome rather than raw forward return to prefer
a return distributed through the month over the same return produced by a few
volatile days. It is still only a ranking target, not a direct optimization of
portfolio Sharpe, and the annualization factor does not change the ordering. A
raw-return target is a plausible alternative and could produce a riskier learned
score.

I rank the outcome within its date and sector. Targets are never imputed.
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

<p class="figure-caption"><strong>Figure 2:</strong> Expanding walk-forward estimation, with each training history separated from its next 600-date prediction block by a 21-session purge.</p>

Those predictions are mechanically out of sample at each refit, but 1995–2021
is still the **research and development period**. I repeatedly inspected that
history while revising predictors, normalization, targets, and portfolio rules.
Walk-forward mechanics do not undo research reuse.

Every score then enters the same portfolio construction. The top and bottom 75
stocks form the long and short books. Each starts at $1/75$, is scaled by 20%
divided by trailing 60-session volatility, and is capped at 4% of sleeve capital;
volatility is floored at 5% and the multiplier at four. Each side is scaled down
if gross exposure exceeds 100%, but a smaller side is not levered up. Three
equal-capital sleeves rebalance on offset third Fridays, execute at the next
close, and hold for three weeks. Reported returns charge 5 bp per dollar traded.

## Ridge as a stability extension

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

The intercept is not penalized. Setting $c=0$ gives the exact OLS
baseline. Positive values shrink coefficients and can make correlated inputs
share weight more evenly. Shrinkage is guaranteed; stronger predictions are not.

Here $c$ is the penalty relative to **mean** squared error. The estimator API
uses summed squared error, so the implementation passes the equivalent raw
value $\alpha_t=c\,n_t$ in each fold. Dividing that complete objective by $n_t$
recovers the equation above. The conversion keeps the reported penalty fixed as
the expanding window grows; it does not treat the row count as a measure of
independent information.

They are not independent. Stocks on one date share market and sector effects;
predictors move gradually; 20-session forward targets overlap; and expanding
windows reuse related observations. I therefore compare
$c\in\{0,0.001,0.01,0.1\}$ on the same 600-date walk-forward blocks, with a
21-session purge and three complementary every-third-date fits. This is
date-blocked evaluation, not random row-level cross-validation. Full-period,
final-ten-year, and final-five-year development results test whether the choice
depends on one span of history; no precise effective sample size is invented.

Rows within a training date have equal weight. The eligible cross-section is
quite stable—955 stocks at the fifth percentile, 984 at the median, and 1,022
at the 95th percentile—so dates receive comparable but not identical aggregate
influence. Exact equal-date weighting remains a useful robustness test. I do not
introduce it after seeing the results because that would change the matched
experiment rather than clarify its existing penalty convention.

## Choosing the penalty

All four models use the same predictors, target, universe, dates, walk-forward
procedure, portfolio construction, and 5 bp cost assumption. The selection rule
uses only evidence through 2021 and prefers consistency across development
windows rather than the highest Sharpe in any single slice.

To judge Ridge, I separate the model from the trading layer. Rank IC, prediction
changes, and coefficient behavior ask what shrinkage changes before costs. The
portfolio table stays net because the final choice still has to work as an
implementation. Annual cost drag ranges only from 1.43 to 1.46 percentage points
across the grid, so the penalty choice is not coming from one candidate receiving
a meaningfully easier cost deduction. A gross table would isolate the portfolio
effect more cleanly, but it would not replace the net implementation check.

| Estimator | Return | Volatility | Sharpe |
| --- | ---: | ---: | ---: |
| OLS, $c=0$ | 7.03% | 7.15% | 0.983 |
| Ridge, $c=0.001$ | 7.05% | 7.19% | 0.981 |
| **Ridge, $c=0.01$** | **7.38%** | **7.36%** | **1.003** |
| Ridge, $c=0.1$ | 7.83% | 7.92% | 0.989 |
{: .research-table .comparison-table .alpha-selection-table }

<p class="table-caption"><strong>Table 2:</strong> Development-period annualized return, annualized volatility, and Sharpe across the matched OLS–Ridge penalty grid, net of 5 bp per dollar traded.</p>

The moderate $c=0.01$ specification is the most balanced choice. Relative to
OLS, annualized return rises by 0.35 percentage points and volatility by 0.21,
leaving a 0.020 Sharpe improvement. The final-ten-year Sharpe is nearly
unchanged, while the final-five-year gain is only 0.008 and slightly trails the
$c=0.001$ result. These are small differences, not an economically decisive
victory. The stronger $c=0.1$ model earns more return and takes more risk; its
weaker shorter-window Sharpes argue against selecting it on full-period return
or mean IC alone. Across the final ten and five development years, respectively,
Sharpe is 1.118/0.975 for OLS, 1.119/0.987 for $c=0.001$, 1.120/0.983 for the
selected $c=0.01$, and 1.060/0.941 for $c=0.1$.
{: .table-followup }

Figure 3 translates the penalty into two practical changes relative to OLS.
Portfolio membership counts how many of the 75 longs and 75 shorts differ from
the OLS portfolio on an average rebalance. Coefficient shrinkage reports the
percentage reduction in the mean coefficient L2 norm and in the mean absolute
coefficient change between adjacent refits. Higher values in either panel mean
that Ridge has moved further away from OLS; they do not mean that predictions
have become more accurate.

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
therefore material before the portfolio becomes radically different, but
Figure 3 does not show that the changed ranking is more accurate.

Other development-only coefficient diagnostics change less. Adjacent
coefficient-vector correlation is 0.932 for $c=0.01$ versus 0.934 for OLS, sign
agreement rises from 89.4% to 90.0%, and the top 20 coefficients' share of total
absolute weight falls from 41.4% to 38.6%. Ridge makes the weights smaller and a
little less concentrated; it does not turn an unstable model into a stable one.

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
combinations. That is useful numerical regularity, but it is not evidence that
the shrunken coefficient on one horizon is the economically “true” effect.

A narrower alternative is that rank stability comes only from the 75-stock
selection cutoff: scores may move without enough names crossing the boundary.
That explains some portfolio overlap, but not the 0.991 rank correlation
measured across the whole stock universe. The broader evidence therefore points
more strongly to substitution among correlated predictors than to a cutoff
artifact alone.

This distinction changes how I read the diagnostics. The 0.991 prediction-rank
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
average stays positive, while short-horizon MACD and illiquidity stay negative.
Other weights weaken or change sign as the sample expands. Combined with the
summary statistics above, this suggests Ridge mainly reduces coefficient scale
and concentration; it does not eliminate time variation in which correlated
predictor receives the weight.

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

<p class="table-caption"><strong>Table 3:</strong> Net development-period portfolio results; OLS and Ridge share the full predictor deck, while the fixed benchmark uses its smaller hand-built signal set.</p>

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

<p class="table-caption"><strong>Table 4:</strong> Net portfolio results from January 2022 through May 2026; this pseudo-holdout did not enter the Ridge-penalty selection rule.</p>

The main later-period observation is not dramatic but it is unfavorable to the
selected penalty. Ridge return is 0.13 percentage points lower than OLS,
volatility is 0.30 points higher, and Sharpe falls from 0.87 to 0.82. Its maximum
drawdown and beta are also slightly worse. Turnover and costs fall modestly,
but not enough to offset the risk-adjusted performance gap. The tiny
$c=0.001$ candidate happens to have the best later Sharpe at 0.89; promoting it
after seeing this period would be post-hoc selection, so I do not.
{: .table-followup }

The information coefficient asks a different question from portfolio Sharpe. On
each date it is the cross-sectional Spearman correlation between the predicted
score and the subsequently realized, sector-ranked target on their common stock
sample:

$$
\mathrm{IC}_t=\rho_{\mathrm S}(\widehat y_{i,t},y_{i,t}).
$$

Figure 5 accumulates those daily correlations. A rising path means the model has
usually ordered future outcomes correctly; a flat path means no additional
cumulative rank association, and a decline means a run of negative IC. The sum
is a prediction diagnostic, not a return series or a significance statistic.

<div class="research-figure ic-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/cumulative-ic-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/cumulative-ic-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/cumulative-ic.svg">
    <img src="/assets/multiple-linear-regression/cumulative-ic.png" alt="Cumulative daily cross-sectional rank information coefficient for fixed weights, OLS, and selected Ridge with the 2022 boundary marked" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Cumulative daily cross-sectional Spearman information coefficient for the fixed score, OLS, and selected Ridge predictions; the rule marks the 2022 pseudo-holdout boundary.</p>

OLS and moderate Ridge follow almost the same path. Both remain ahead of the
fixed score, although the differing signal decks prevent a clean estimator
claim from that comparison. More importantly for the penalty decision, Ridge
does not separate from OLS after the 2022 boundary.

Portfolio performance adds selection, volatility scaling, execution, and costs
to that prediction evidence. Figure 6 shows the complete net path and the
drawdowns behind the period summaries rather than adding another performance
statistic.

<div class="research-figure performance-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/performance-and-drawdowns-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/performance-and-drawdowns-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/performance-and-drawdowns.svg">
    <img src="/assets/multiple-linear-regression/performance-and-drawdowns.png" alt="Net growth and drawdowns for fixed weights, OLS, and selected Ridge with development and later periods separated" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 6:</strong> Net cumulative performance and drawdowns for the three ranking systems after charging 5 bp per dollar traded; the rule separates development from the later period.</p>

The learned portfolios' lower volatility and shallower development drawdowns
are visible through time, not only in Table 3. Ridge remains close to OLS and
does not produce a distinct later-period improvement. The vertical rule marks
the specification boundary; it does not imply that the later data were wholly
untouched by prior research.

## What the portfolio is actually doing

Returns alone do not tell me whether the ranking is practical or what the final
portfolio actually owns. Figure 7 starts with the practical part. Two-way
turnover is the sum of absolute long- and short-side trading divided by equity
on each rebalance. I charge 5 bp per dollar traded as a simple cost
approximation and compound the resulting net returns. It is definitely
imperfect: borrow, financing, market impact, and taxes are not included. Still,
applying the same rule to every portfolio gives a useful first comparison of how
much turnover eats into returns.

<div class="research-figure turnover-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/multiple-linear-regression/turnover-and-costs-mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/multiple-linear-regression/turnover-and-costs-mobile.png">
    <source type="image/svg+xml" srcset="/assets/multiple-linear-regression/turnover-and-costs.svg">
    <img src="/assets/multiple-linear-regression/turnover-and-costs.png" alt="Turnover per rebalance and annual cost drag for fixed weights, OLS, and selected Ridge in development and later periods" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 7:</strong> Average two-way turnover per rebalance and annual return drag from the 5 bp trading-cost assumption, shown separately for development and the later period.</p>

The fixed score is clearly cheaper. Ridge barely changes the higher turnover
inherited from the learned monthly ranking: versus OLS, the selected penalty
saves 0.02 percentage points of annual return in development and 0.03 in the
later period. That difference is too small to motivate the penalty by itself.

Figure 8 then asks what the Ridge portfolio actually owns. Let $x_{i,j,t}$ be
stock $i$'s normalized rank on predictor $j$ and $w_{i,t}$ its signed held
weight, positive for longs and negative for shorts. I calculate

$$
T_{j,t}=\frac{\sum_i w_{i,t}x_{i,j,t}}
{\sum_i\lvert w_{i,t}\rvert}.
$$

The denominator uses the gross weight with a non-missing value for that
predictor; all ten displayed series have complete coverage. Positive means the
long book owns higher ranks than the short book, negative means lower ranks,
and zero means no directional tilt. Tilts are calculated from held positions on
every trading date and averaged by quarter for Figure 8. Each panel includes
zero and rounds its limits outward to its own observed quarterly range. The
axes therefore reveal changes through time without reserving space for values
that never occur. Compare absolute magnitudes using the labeled full-sample
means, not the apparent height of the independently scaled lines.

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

<p class="figure-caption"><strong>Figure 8:</strong> Quarterly paths of the ten largest average absolute realized predictor tilts; panels use their own zero-inclusive scales and label the full-sample mean.</p>

The pattern is fairly simple. The long book owns quieter stocks: its ranks are
lower on ATR and the volatility measures. It also owns stocks that have spent
more time above their long-run moving average and remain closer to an earlier
high. Among the largest realized characteristics, the portfolio therefore looks
mostly like defensive plus trend.

That is not the same as discovering two independent sources of alpha. The
top-ten rule hides smaller tilts, several lines are close variations of the same
idea, and stock-level volatility scaling can strengthen the defensive pattern
after the ranking has already been formed. Correlated predictors can also swap
coefficient weight while continuing to identify similar stocks. Both mechanisms
can leave the final portfolio looking more stable and more concentrated by theme
than the coefficient heatmap suggests.

I keep the largest realized tilts because a hand-picked diverse set would make
the book look broader than it is. But Figure 8 is a holdings x-ray, not return
attribution. A grouped theme summary would show how much exposure is duplicated.
Running the same rankings without stock-level volatility scaling would separate
the model's defensive preference from the weighting rule. Neutralizing the
defensive and trend themes would then test whether performance survives without
them. Those two experiments matter more than which line happens to look largest
in the chart.

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

The next tests should target the remaining design risks rather than add another
model family. I would first repeat the same grid with exactly equal aggregate
weight per date, then vary the date thinning, blocked-window length, and target
horizon to see whether overlapping outcomes drive the apparent stability.
Leave-one-theme-out or residualized tests would address incremental value in the
correlated predictor deck. Most importantly, the next genuine holdout must begin
with the full specification locked in advance. Until then, the later result is
evidence that the learned ranking remains useful, but also a warning against
claiming that Ridge won.
