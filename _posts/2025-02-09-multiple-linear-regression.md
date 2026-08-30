---
layout: post
title: "How to Combine Stock Signals with Multiple Linear and Ridge Regression"
date: 2025-02-09
last_modified_at: 2026-08-30
categories: ["Regression"]
article_label: Factor combination · Multiple linear and Ridge regression
permalink: /quants/2025/02/09/multiple-linear-regression.html
---

<p class="article-summary"><strong>TL;DR:</strong> I compare a five-factor score whose weights are chosen in advance with multiple linear regression and Ridge regression fitted to a broader predictor set. The OLS model records a development-period Sharpe of 0.98 against 0.71 for the benchmark, but that comparison also changes the predictors and their data histories. Ridge makes the learned coefficients smaller and more stable while leaving the stock ranking almost unchanged: its rank correlation with OLS is 0.991. From January 2022 through May 2026, the selected Ridge model records a Sharpe of 0.82 against 0.87 for OLS. That four-year pseudo-holdout is too short to settle long-run performance.</p>

Once a stock model contains more than a handful of signals, finding another one
is no longer the main problem. The harder decision is how much influence each
signal should have when they are combined into a single stock ranking. A fixed
score chooses those weights in advance. Multiple linear regression can learn
them from subsequent stock outcomes, while Ridge regression can restrain that
learning when many predictors contain similar information.

I start with a score built from five factors whose directions and weights are
chosen in advance, then give multiple linear regression a broader set of 144
predictors. Ordinary least squares (OLS) is free to assign each predictor its
own coefficient. Ridge uses the same model but shrinks those coefficients. The
practical question is whether that constraint improves the ranking or merely
produces a steadier coefficient vector for the same signal.

I use two comparisons because they answer different questions. Fixed weights
versus OLS compares the five-factor score with the whole broader model. OLS
versus Ridge isolates the penalty because the predictors, target, universe, and
portfolio rules stay the same. All three rankings then pass through the same
position sizing, execution, and cost rules.

The underlying panel uses point-in-time Russell 1000 membership and daily U.S.
equity data from 3 January 1995 through 27 May 2026; the first
walk-forward portfolios begin in September 1998 after the required training
history. Every portfolio applies the same price, merger-target, duplicate-share-
class, sizing, and execution rules. OLS and Ridge also use exactly the same
eligible stock-date rows. The fixed score needs complete histories for its five
factors, so its comparison with OLS changes both the available rows and the
factor weights.

## A fixed score is the simplest way to combine signals

Fixed weights provide a useful baseline because every preference is visible. I
group familiar signals into five factors, give each factor the same influence, and
set the direction of each signal in advance. Those choices are easy to inspect,
though the factors, horizons, and signs still reflect my judgment.

The five factors describe the kind of company the benchmark prefers. The
defensive factor pairs recent volatility with the average of the three largest
daily gains over the latest month. The intention is to favour a calm return path
rather than one propped up by a few sharp jumps. Momentum looks for a trend that
has persisted beyond the latest short-term move. The remaining factors favour
lower short positioning, larger companies, and a higher share of positive-
return days.

Let $$P_t(z_{i,t})=\operatorname{rank}_t(z_{i,t})/N_t$$ denote stock $$i$$'s
within-date percentile rank, where $$N_t$$ is the number of available stocks for
that measure. Higher values are always more attractive. I write the average of
the three largest daily returns in the past 21 sessions as
$$\bar r^{(3)}_{i,t;21}$$. The five factor scores are

$$
\begin{aligned}
X_{\mathrm{def},i,t}
&=\tfrac12 P_t\!\left(-\tfrac13\sum_{h\in\{21,63,126\}}\sigma_{i,t}^{(h)}\right)\\
&\quad+\tfrac12 P_t\!\left(-\bar r^{(3)}_{i,t;21}\right),\\[0.9em]
X_{\mathrm{mom},i,t}
&=P_t\!\left(\sum_{h\in\{63,126,189,252\}}
R_{i,t}^{(h,\,\mathrm{skip}\ 21)}\right),\\[0.9em]
X_{\mathrm{short},i,t}
&=P_t\!\left(-\log\frac{SI_{i,t-21}}{ADV_{i,t}^{(63)}}\right),\\[0.9em]
X_{\mathrm{size},i,t}
&=P_t\!\left(\log MC_{i,t}\right),\\[0.9em]
X_{\mathrm{cons},i,t}
&=P_t\!\left(-\frac1{756}\sum_{u=0}^{755}
\mathbf 1\{r_{i,t-u}<0\}\right).
\end{aligned}
$$

The benchmark gives each factor 20%:

$$
X_{\mathrm{score},i,t}
=\frac15\left(
X_{\mathrm{def},i,t}
+X_{\mathrm{mom},i,t}
+X_{\mathrm{short},i,t}
+X_{\mathrm{size},i,t}
+X_{\mathrm{cons},i,t}
\right).
$$

Here $$\sigma_{i,t}^{(h)}$$ is annualised volatility over the latest $$h$$
sessions, and $$R_{i,t}^{(h,\,\mathrm{skip}\ 21)}$$ is the stock's $$h$$-session
return ending 21 sessions before date $$t$$. $$SI$$ is reported shares sold
short, lagged 21 sessions; $$ADV^{(63)}$$ is average daily share volume over 63
sessions; and $$MC$$ is market capitalisation. The indicator in
$$X_{\mathrm{cons}}$$ equals one on a negative-return day.

The defensive score combines low volatility with avoidance of unusually large
up days. Each component contributes 10% to the final score.
Momentum spans four horizons after skipping the latest month. The remaining
scores favour low short interest relative to trading volume, larger companies,
and fewer down days over three years. Ranking before aggregation prevents market
capitalisation in dollars or volatility in percentage points from dominating
through its units. Short-positioning data are lagged to when they were available,
and a stock needs enough history for every factor before it can enter the benchmark.

The five factors are meant to bring different information into the score, but
they need not be independent. Table 1 measures their same-date cross-sectional
rank correlation. I first match all five final scores on the same 6,622,873
stock-date rows, including the combined defensive score, and calculate a
Spearman correlation on each date. The table reports the equal-weight average
across 7,298 dates.

<table class="research-table comparison-table portfolio-card-table factor-correlation-table">
  <thead>
    <tr><th>Factor</th><th>Defensive</th><th>Momentum</th><th>Short pos.</th><th>Size</th><th>Return cons.</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Defensive</th><td data-label="Defensive">1.00</td><td data-label="Momentum">0.11</td><td data-label="Short positioning">−0.06</td><td data-label="Size">0.19</td><td data-label="Return consistency">0.29</td></tr>
    <tr><th scope="row">Momentum</th><td data-label="Defensive">0.11</td><td data-label="Momentum">1.00</td><td data-label="Short positioning">0.03</td><td data-label="Size">0.20</td><td data-label="Return consistency">0.27</td></tr>
    <tr><th scope="row">Short positioning</th><td data-label="Defensive">−0.06</td><td data-label="Momentum">0.03</td><td data-label="Short positioning">1.00</td><td data-label="Size">0.27</td><td data-label="Return consistency">0.03</td></tr>
    <tr><th scope="row">Size</th><td data-label="Defensive">0.19</td><td data-label="Momentum">0.20</td><td data-label="Short positioning">0.27</td><td data-label="Size">1.00</td><td data-label="Return consistency">0.10</td></tr>
    <tr><th scope="row">Return consistency</th><td data-label="Defensive">0.29</td><td data-label="Momentum">0.27</td><td data-label="Short positioning">0.03</td><td data-label="Size">0.10</td><td data-label="Return consistency">1.00</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Mean same-date Spearman rank correlation among the five final fixed factors, 21 May 1997–27 May 2026. The defensive column uses the combined defensive score, not its two ingredients.</p>

The factors overlap, but none of the average correlations exceeds 0.29 in
absolute value. Defensive and return consistency are the closest pair at 0.29;
defensive and short positioning are slightly negative at −0.06. The factors are
related, but no pair is close enough for one to stand in for another.

Table 2 asks a different question: what happens when each final factor is used
on its own? Each run uses the same eligible stock-date rows, selects 75 stocks
per side, scales positions with the same volatility rule, follows the same
three rebalance schedules, and charges 5 bp per dollar traded. The development
window ends in 2021; the later window runs from January 2022 through May 2026.

<table class="research-table comparison-table portfolio-card-table standalone-factor-table">
  <thead>
    <tr><th>Factor · period</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Sharpe</th><th>Max DD</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Defensive · Development</th><td data-label="Gross return">7.14%</td><td data-label="Net return">6.12%</td><td data-label="Net volatility">9.62%</td><td data-label="Sharpe">0.64</td><td data-label="Maximum drawdown">−37.29%</td><td data-label="Turnover per rebalance">116.85%</td></tr>
    <tr><th scope="row">Defensive · Later</th><td data-label="Gross return">1.67%</td><td data-label="Net return">0.61%</td><td data-label="Net volatility">11.98%</td><td data-label="Sharpe">0.05</td><td data-label="Maximum drawdown">−17.01%</td><td data-label="Turnover per rebalance">120.97%</td></tr>
    <tr><th scope="row">Momentum · Development</th><td data-label="Gross return">3.44%</td><td data-label="Net return">2.80%</td><td data-label="Net volatility">10.27%</td><td data-label="Sharpe">0.27</td><td data-label="Maximum drawdown">−34.46%</td><td data-label="Turnover per rebalance">74.30%</td></tr>
    <tr><th scope="row">Momentum · Later</th><td data-label="Gross return">9.26%</td><td data-label="Net return">8.70%</td><td data-label="Net volatility">11.68%</td><td data-label="Sharpe">0.74</td><td data-label="Maximum drawdown">−13.01%</td><td data-label="Turnover per rebalance">64.17%</td></tr>
    <tr><th scope="row">Short positioning · Development</th><td data-label="Gross return">1.95%</td><td data-label="Net return">1.27%</td><td data-label="Net volatility">4.88%</td><td data-label="Sharpe">0.26</td><td data-label="Maximum drawdown">−17.36%</td><td data-label="Turnover per rebalance">77.88%</td></tr>
    <tr><th scope="row">Short positioning · Later</th><td data-label="Gross return">5.74%</td><td data-label="Net return">5.07%</td><td data-label="Net volatility">5.48%</td><td data-label="Sharpe">0.93</td><td data-label="Maximum drawdown">−6.06%</td><td data-label="Turnover per rebalance">76.42%</td></tr>
    <tr><th scope="row">Size · Development</th><td data-label="Gross return">0.65%</td><td data-label="Net return">0.37%</td><td data-label="Net volatility">7.28%</td><td data-label="Sharpe">0.05</td><td data-label="Maximum drawdown">−51.64%</td><td data-label="Turnover per rebalance">32.97%</td></tr>
    <tr><th scope="row">Size · Later</th><td data-label="Gross return">5.58%</td><td data-label="Net return">5.35%</td><td data-label="Net volatility">7.30%</td><td data-label="Sharpe">0.73</td><td data-label="Maximum drawdown">−11.02%</td><td data-label="Turnover per rebalance">26.77%</td></tr>
    <tr><th scope="row">Return consistency · Development</th><td data-label="Gross return">5.64%</td><td data-label="Net return">5.22%</td><td data-label="Net volatility">8.94%</td><td data-label="Sharpe">0.58</td><td data-label="Maximum drawdown">−27.90%</td><td data-label="Turnover per rebalance">48.29%</td></tr>
    <tr><th scope="row">Return consistency · Later</th><td data-label="Gross return">1.90%</td><td data-label="Net return">1.52%</td><td data-label="Net volatility">8.94%</td><td data-label="Sharpe">0.17</td><td data-label="Maximum drawdown">−16.48%</td><td data-label="Turnover per rebalance">43.63%</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Standalone factor portfolios. Metrics are means of the three full-capital rebalance schedules. Returns and volatility are annualized; risk statistics use net returns; turnover is average executed two-way turnover per rebalance.</p>

Every factor has a positive net return in both windows, but the leaders change.
Defensive and return consistency have the strongest development Sharpe ratios,
at 0.64 and 0.58. Later, short positioning leads at 0.93, while momentum and
size rise to 0.74 and 0.73. Defensive falls to 0.05 and also trades the most,
at about 121% per rebalance. This rotation is a practical reason to combine
factors, but standalone performance does not establish incremental value. A
factor can look good alone and still add little once the other four are present.

Multiple linear regression and Ridge receive 144 ranked predictors, but these
are not 144 unrelated ideas. Price-based measures ask whether a stock has risen,
where it sits relative to a moving average or an earlier high, and how turbulent
its path has been. Other predictors describe company size, market sensitivity,
trading activity, liquidity, and lagged short positioning. Many of these ideas
appear at several horizons or through closely related definitions. That breadth
lets the model choose among short- and long-run predictors from the same factor
family, but the overlap also makes individual coefficients hard to pin down.

## Ranks put 144 unlike predictors on one scale

The 144 predictors have the same units problem as the benchmark, but here the
regression must learn both direction and weight. Let $$\widetilde X_{i,j,t}$$ be
stock $$i$$'s raw value for predictor $$j$$, let
$$R_t(\widetilde X_{i,j,t})$$ be its dense rank, and let $$K_{j,t}$$ be the
largest rank on date $$t$$. The normalised input is

$$
X_{i,j,t}
=2\frac{R_t(\widetilde X_{i,j,t})}{K_{j,t}}-1.
$$

This maps every predictor to the same $[-1,1]$ interval. Tied observations share
a rank, and a predictor with no cross-sectional variation receives zero. The
common scale stops a variable measured in dollars from receiving more influence
than one measured in percentage points merely because its numbers are larger.
It also limits the influence of extreme raw observations and makes coefficient
magnitudes more comparable across predictors.

Ranking deliberately discards distance. A stock just above another receives the
same one-rank step as a stock separated by a much larger raw gap. The model is
learning relative order, not a calibrated relationship between the raw
signal value and future return. That trade-off fits this application because the
portfolio buys and shorts only the stocks at the ends of the ranking.

Figure 1 keeps those stages separate: raw measures become comparable ranks, the
benchmark or regression combines them, and only then does the common portfolio
rule turn a stock ranking into positions.

<div class="research-figure signal-flow-figure">
  {%- include signal-combination-flow.html -%}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Signal-combination pipeline. Fixed and learned combinations feed the same stock-selection and portfolio rules.</p>

The separation in Figure 1 matters for the comparison: only the
signal-combination step changes, while stock selection and portfolio
construction remain the same.

When a predictor is unavailable, I use the latest known value or the stock's
sector average for that date. The traded universe then excludes stocks below
five dollars, announced merger targets, and duplicate share classes.

The model also needs a definition of a good future outcome. I want to reward a
gain that persists through the month rather than one produced by a single
volatile day. I divide average return over the next 20
trading days by volatility over the same period, then ranks that outcome within
each date and sector. This is a forward, Sharpe-like ranking target, not the
portfolio's Sharpe ratio. A raw-return target would express a different
preference and could produce a riskier learned score.

Writing the next 20 daily returns as $$r_{i,t+s}$$, the raw outcome and the
model target are

$$
q_{i,t}
=\sqrt{252}\,
\frac{\frac1{20}\sum_{s=1}^{20}r_{i,t+s}}
{\operatorname{sd}(r_{i,t+1},\ldots,r_{i,t+20})},
\qquad
y_{i,t}
=2\frac{\operatorname{rank}_{t,\,\mathrm{sector}}(q_{i,t})}
{K_{t,\,\mathrm{sector}}}-1.
$$

Thus $$y_{i,t}\in[-1,1]$$ is the within-date, within-sector rank of the forward
outcome; $$K_{t,\,\mathrm{sector}}$$ is that group's largest dense rank.

Predictor ranks retain cross-sector information, while the target asks which
stocks subsequently did better than their sector peers. This reduces broad
sector movement in the outcome the model is trying to learn. Portfolio
selection remains global, however, so the final holdings can still carry sector
exposures; an allocation risk model would have to constrain them explicitly.

## Multiple linear regression learns the ranking

With predictors and outcomes on comparable scales, multiple linear regression
can learn how the signals work together. I fit it with OLS. Let
$$\mathbf X_{i,t}\in[-1,1]^{144}$$ contain the normalised predictors and let
$$y_{i,t}$$ be the sector-ranked forward target. For walk-forward fold $$f$$,
the mean squared training loss is

$$
\mathcal L_f(\beta_0,\boldsymbol\beta)
=
\frac{1}{n_f}\sum_{(i,t)\in\mathcal T_f}
\left(y_{i,t}-\beta_0-\mathbf X_{i,t}^{\top}
\boldsymbol\beta\right)^2.
$$

Ordinary least squares chooses the coefficients that minimise this loss:

$$
(\widehat\beta^{\mathrm{OLS}}_{0,f},
\widehat{\boldsymbol\beta}^{\mathrm{OLS}}_f)
=\arg\min_{\beta_0,\boldsymbol\beta}
\mathcal L_f(\beta_0,\boldsymbol\beta).
$$

Here $$\mathcal T_f$$ is the training sample and $$n_f=|\mathcal T_f|$$. The
fitted score $$\widehat y_{i,t}=\widehat\beta_{0,f}
+\mathbf X_{i,t}^{\top}\widehat{\boldsymbol\beta}_f$$ becomes the learned stock
ranking. A positive coefficient rewards a high predictor rank; a negative
coefficient reverses the preference.

I refit the model as the historical sample expands and score only the next
block—a walk-forward design. Figure 2 shows the sequence. The first 900 dates
form the initial training sample, a 21-day gap separates training outcomes from
the next prediction block, and the fitted model then scores 600 new dates. I
repeat that process 12 times and average three date-thinned fits at each step to
reduce the dependence created by overlapping monthly outcomes.

For each fold, the training dates are sorted and split into three phases: the
first model keeps dates 1, 4, 7, and so on; the second keeps dates 2, 5, 8; and
the third keeps dates 3, 6, 9. Each model predicts the entire next block, and I
average the three predictions—not their coefficients—before ranking stocks.

<div class="research-figure walk-forward-figure">
  {%- include walk-forward-figure.html -%}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Expanding walk-forward estimation, with a 21-day buffer before each 600-date prediction block.</p>

The expanding windows in Figure 2 protect each prediction block from future
training data. They do not turn the full history into an untouched test. I
repeatedly inspected the 1995–2021 results while revising predictors, the target,
and the portfolio, so that entire span remains the **research and development
period**.

Every score then enters the portfolio construction developed in the earlier
[low-volatility allocation article](/quant/2024/12/15/low-volatility-factor.html).
The top and bottom 75 stocks form the long and short books, and quieter stocks
receive larger positions subject to stock-level and sleeve-level caps. Three
staggered sleeves rebalance every three weeks, and reported returns charge 5 bp
per dollar traded. Because the rule scales stocks one at a time, it leaves
correlations, net exposure, market beta, and total portfolio risk uncontrolled.

## Ridge stabilises coefficients more than rankings

Ordinary least squares becomes hard to interpret when several predictors express
the same idea. Their coefficients can move sharply between refits even when the
stocks remain in almost the same order. Ridge regression favours a more stable
division of weight by penalising large coefficients:

$$
(\widehat\beta^{(c)}_{0,f},\widehat{\boldsymbol\beta}^{(c)}_f)
=\arg\min_{\beta_0,\boldsymbol\beta}
\left\{\mathcal L_f(\beta_0,\boldsymbol\beta)
+c\lVert\boldsymbol\beta\rVert_2^2\right\}.
$$

The penalty applies to the slopes and leaves the intercept free. Setting $c=0$
gives the exact OLS baseline. Positive values shrink coefficients and encourage
correlated predictors to share influence instead of competing for a large
individual weight. Normalising the loss by the number of training rows keeps
$c$ comparable as the sample expands. Shrinkage is guaranteed by the objective;
better predictions are not.

Random row-level validation would treat strongly related observations as if they
were independent. Stocks on the same date share market and sector shocks,
predictors move slowly, and adjacent 20-day outcomes overlap. The blocked design
and 21-day gap in Figure 2 prevent the most direct leakage across prediction
boundaries, but the effective sample is still much smaller than the raw row
count. I treat the penalty grid as a sensitivity check rather than a
precise estimate of an optimal value.

All four candidates use the same predictors, target, universe, dates,
walk-forward procedure, portfolio construction, and 5 bp cost assumption. The grid
$$c\in\{0,0.001,0.01,0.1\}$$ uses data through 2021. I prefer a gentle penalty
that improves coefficient stability without depending on a large change in the
portfolio results.

I made that choice without a predeclared numerical acceptance threshold. The
development-period rule was to select the smallest tested penalty that clearly
reduced coefficient size and refit movement while leaving the portfolio results
close to OLS.

Table 3 gives the first test of the penalty choice. It compares portfolio return
and risk across the matched OLS–Ridge grid, before and after the same trading-cost
rule. Annual cost differs by only 0.03 percentage points across the candidates,
so the table is mainly comparing the rankings and the risk they produce rather
than different cost deductions.

| Estimator | Gross return | Net return | Net volatility | Net Sharpe |
| --- | ---: | ---: | ---: | ---: |
| OLS, $c=0$ | 8.49% | 7.03% | 7.15% | 0.983 |
| Ridge, $c=0.001$ | 8.51% | 7.05% | 7.19% | 0.981 |
| **Ridge, $c=0.01$** | **8.82%** | **7.38%** | **7.36%** | **1.003** |
| Ridge, $c=0.1$ | 9.26% | 7.83% | 7.92% | 0.989 |
{: .research-table .comparison-table .alpha-selection-table }

<p class="table-caption"><strong>Table 3:</strong> Development-period annualized arithmetic return across the matched OLS–Ridge penalty grid before and after 5 bp per dollar traded; volatility and Sharpe use net returns.</p>

Table 3 does not show a decisive Ridge improvement. The moderate $c=0.01$
penalty raises annualised return by 0.35 percentage points and volatility by
0.21, moving Sharpe from 0.983 to 1.003. The stronger $c=0.1$ penalty earns more
return but adds enough risk to leave Sharpe at 0.989. I carry $c=0.01$
forward as a deliberately gentle compromise, not a clear winner or an estimate
of a uniquely optimal penalty.
{: .table-followup }

Figure 3 asks what that moderate penalty actually changes. Panel A measures how
many names enter or leave the 150-stock portfolio relative to OLS. Panel B
compares the size of the coefficient vector and its movement between refits. The
two panels distinguish a different-looking model from a meaningfully different
stock selection.

<div class="research-figure alpha-sensitivity-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/alpha-sensitivity" alt="Average portfolio-membership changes and coefficient shrinkage relative to OLS across the Ridge penalty grid" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Average portfolio-membership changes and coefficient shrinkage relative to matched OLS during the development period.</p>

Figure 3 shows that coefficients change much more than the portfolio. At
$c=0.01$, their size and movement between refits fall by roughly one third, yet
only about 14 of 150 selected names change on a typical rebalance. The average
stock moves 2.71 percentile-rank points and the full ranking retains a 0.991
correlation with OLS. Even $c=0.1$ cuts the coefficient measures by about 70%
while changing only about 39 portfolio names. Ridge changes how weight is split
among predictors much more than it changes which stocks are selected.

Correlated predictors can exchange coefficient weight while keeping their
combined score close. This makes the stock ordering much more stable than the
weight assigned to each input. The 0.991 rank correlation supports that
distinction. Broad predictor themes are easier to trust than any single
coefficient.

Figure 4 follows the ten largest Ridge coefficients across refits. Positive
cells reward a high predictor rank and negative cells favour a low rank. A
stable explanation would keep the same signs and similar relative weights from
one column to the next. The 2022 and 2024 columns show what happened later; they
do not enter the penalty selection.

<div id="coefficient-heatmap" class="research-figure coefficient-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/top-coefficients" alt="Heatmap of the ten largest average absolute coefficients for the selected Ridge model across walk-forward refits" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Signed coefficients for the selected Ridge model's ten largest mean absolute weights across walk-forward refits; 2022 and 2024 show later refits.</p>

A few broad directions remain stable in Figure 4: price relative to its moving
average stays positive, while short-horizon MACD and illiquidity stay negative.
Several other coefficients weaken or change sign as the sample expands. Ridge
reduces coefficient size and concentration without producing a fixed,
predictor-by-predictor explanation. Because these predictors overlap, the broad
themes are easier to trust than any one coefficient.

## The broader model takes less risk in development

Table 4 asks whether the broader learned model improves portfolio results. It compares
the first walk-forward predictions in 1998 through the end of the
2021 development period. The fixed benchmark uses its smaller hand-built signal
set, while OLS and Ridge share the same 144 predictors and eligible rows. The
fixed score applies the same trading screens but can retain a different set of
stock-date rows because its required input histories differ.

| Development metric | Fixed | OLS | Ridge $c=0.01$ |
| --- | ---: | ---: | ---: |
| Annualized return, gross | 7.61% | 8.49% | 8.82% |
| Annualized return, net | 6.92% | 7.03% | 7.38% |
| Annualized volatility | 9.73% | 7.15% | 7.36% |
| Sharpe ratio | 0.71 | 0.98 | 1.00 |
| Maximum drawdown | −31.55% | −18.77% | −19.03% |
| Market beta | 0.093 | 0.084 | 0.091 |
| Two-way turnover per rebalance | 78.78% | 167.67% | 165.72% |
| Annual trading cost | 0.69 pp | 1.46 pp | 1.44 pp |
{: .research-table .comparison-table .period-metrics-table }

<p class="table-caption"><strong>Table 4:</strong> Development-period portfolio results. Gross return is before the stated trading cost; all risk statistics use returns after 5 bp per dollar traded.</p>

Table 4 shows where the broader OLS model differs from the benchmark.
Gross return rises by 0.88 percentage points, but the extra trading cost consumes
0.77 points of that gap, leaving only 0.11 points after costs. Its higher Sharpe
comes mainly from volatility falling from 9.73% to 7.15%, alongside a
shallower maximum drawdown. But OLS also uses more predictors and different
input histories, so the comparison cannot tell us whether learned weights
caused the lower risk. Ridge remains close to OLS: its coefficients are more
stable, but turnover falls by only 1.95
percentage points per rebalance and annual cost by 0.02 points.
{: .table-followup }

## The selected Ridge model does not beat OLS after 2021

I selected $c=0.01$ using data through 2021. Table 5 repeats the portfolio
comparison from January 2022 through May 2026. Later history had already
influenced earlier feature, target, portfolio, and presentation work, so this is
a **pseudo-holdout**, not an untouched test. Four years also cover too few
market regimes to settle long-run performance.

| Later-period metric | Fixed | OLS | Ridge $c=0.01$ |
| --- | ---: | ---: | ---: |
| Annualized return, gross | 7.85% | 8.84% | 8.68% |
| Annualized return, net | 7.24% | 7.50% | 7.37% |
| Annualized volatility | 11.33% | 8.64% | 8.95% |
| Sharpe ratio | 0.64 | 0.87 | 0.82 |
| Maximum drawdown | −10.98% | −7.59% | −8.05% |
| Market beta | 0.036 | 0.075 | 0.078 |
| Two-way turnover per rebalance | 69.70% | 152.75% | 149.61% |
| Annual trading cost | 0.61 pp | 1.34 pp | 1.31 pp |
{: .research-table .comparison-table .period-metrics-table }

<p class="table-caption"><strong>Table 5:</strong> Later-period portfolio results. Gross return is before the stated trading cost; all risk statistics use returns after 5 bp per dollar traded.</p>

In Table 5, the selected Ridge model does not beat OLS after 2021. Its
return is 0.13 percentage points below OLS, volatility is 0.31 points higher,
and Sharpe is 0.82 rather than 0.87. Turnover and costs are only slightly lower.
Changing the penalty after seeing these results would abandon the
development-period rule. I leave $c=0.01$ unchanged: the later gap counts
against Ridge and is not a reason to retune it.
{: .table-followup }

## Ridge and OLS rank stocks almost identically

The portfolio tables mix ranking quality with selection and position sizing.
Information coefficient (IC) isolates the ranking by measuring the daily
Spearman correlation between the predicted order and the subsequently realised,
sector-ranked outcome.

Figure 5 accumulates those daily correlations through time. A rising path means the
model has ordered future outcomes correctly on balance; a flat path means no new
rank association, and a decline marks a run of negative IC. The series runs from
the first walk-forward predictions in September 1998 to the last complete
20-trading-day outcome on April 28, 2026. It tests the ranking, not portfolio
returns or statistical significance.

<div class="research-figure ic-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/cumulative-ic" alt="Cumulative daily cross-sectional rank information coefficient for fixed weights, OLS, and selected Ridge with the 2022 boundary marked" version="12" %}
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Cumulative daily cross-sectional Spearman information coefficient for the fixed score, OLS, and selected Ridge predictions; the rule marks the 2022 boundary.</p>

The OLS and Ridge paths in Figure 5 are almost indistinguishable. Table 6
quantifies that overlap by separating the mean and variability of daily IC in
the development and later periods.

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

<p class="table-caption"><strong>Table 6:</strong> Mean and standard deviation of daily rank IC, with IC IR defined as mean divided by standard deviation, shown separately for development and later periods.</p>

Table 6 confirms what the overlapping paths suggest. During development, Ridge
raises mean IC over OLS by only 0.0008 and also raises its variability, leaving
IC IR fractionally lower at 0.530 versus 0.534. In the later period, Ridge has a
slightly lower mean and higher dispersion. Shrinkage adds little ranking-quality
gain in either period.

At first, the fixed score looks different: Table 6 gives it the highest
later-period mean IC, yet its IC is more variable and its IC IR remains below
OLS. This does not contradict the portfolio tables. IC evaluates the whole
eligible cross-section, while portfolio return depends on the tails and then
adds position sizing, execution, and costs. The fixed and learned models also
use different predictor sets.

## The return paths confirm the small Ridge–OLS gap

Figure 6 shows when the portfolio differences accumulated. The upper
panel tracks net growth of one dollar on a logarithmic scale; the lower panel shows the
drawdowns hidden by the period averages. The vertical rule separates the
development period from the later period.

<div class="research-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/performance-and-drawdowns" alt="Net growth on a logarithmic scale and drawdowns for fixed weights, OLS, and selected Ridge with development and later periods separated" version="14" %}
</div>

<p class="figure-caption"><strong>Figure 6:</strong> Net growth of <span class="mathjax-ignore">$1</span> and drawdowns for the three ranking systems after charging 5 bp per dollar traded. The upper panel uses a logarithmic scale; the rule separates development from the later period.</p>

Figure 6 shows that the broader learned models' development-period
Sharpe advantage comes mainly from a smoother path and shallower drawdowns, not
a dramatic return gap. Ridge tracks OLS closely throughout the sample and does
not create a visibly different return path. After 2021, OLS retains the higher
Sharpe reported in Table 5.

## Portfolio construction reshapes the learned ranking

### Learned rankings roughly double turnover

The learned rankings change more from one rebalance to the next, so their
advantage may be expensive to trade. Figure 7 compares two-way turnover and the
resulting annual drag under the same 5 bp cost rule. This estimate covers stock
trading, not borrow, financing, market impact, or taxes.

<div class="research-figure turnover-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/turnover-and-costs" alt="Turnover per rebalance and annual trading cost for fixed weights, OLS, and selected Ridge in development and later periods" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 7:</strong> Average two-way turnover per rebalance and annual trading cost under the 5 bp assumption, shown separately for development and the later period.</p>

Figure 7 shows that the fixed score trades about half as much as either learned
ranking. Ridge barely changes that burden: relative to OLS, it saves 0.02
percentage points of annual trading cost in development and 0.03 later. Smaller
coefficients do not make the portfolio much more stable.

### Inverse-volatility sizing leaves exposure uncontrolled

Stock-level volatility sizing also changes the balance between the two sides of
the portfolio. Figure 8 tracks the selected Ridge portfolio's long gross, short
gross, and their difference, the net stock exposure. A positive net line means
more capital is invested long than short.

<div class="research-figure portfolio-exposure-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/portfolio-exposures" alt="Monthly long gross, short gross, and net stock exposure of the selected Ridge portfolio" version="16" %}
</div>

<p class="figure-caption"><strong>Figure 8:</strong> Monthly average floating exposures for the selected Ridge portfolio.</p>

Figure 8 shows the long book staying near its ceiling while the short book does
most of the moving. High-volatility short candidates receive smaller positions,
so average net exposure rises from +30.0% in development to +46.9% after 2021.
Market beta remains much smaller than net exposure, which is consistent with the
short book carrying more beta per dollar. The current allocator controls neither
quantity directly.

### The portfolio remains defensive and trend-led

The realised tilts translate a long list of model inputs into a simpler
question: what kind of stocks does the finished Ridge portfolio actually own?
Each tilt is the portfolio-weighted average of a predictor's signed ranks.
Positive values mean the long book owns higher ranks than the short book;
negative values mean the reverse. Figure 9 averages these tilts by quarter.
Each panel includes zero but uses its own vertical range, so the labelled
full-sample means are the right comparison across panels.

Most of the ten largest realised tilts in Figure 9 fall into two broad groups.
ATR and the volatility measures describe how turbulent the
price path has been. Trend streak, distance from a prior high, and RSI describe
whether a trend has persisted and where the stock sits within it. The model sees
relative ranks, so the chart should be read as a directional preference rather
than a comparison of raw units.

<div class="research-figure exposure-figure">
  {% include theme-svg-figure.html base="/assets/multiple-linear-regression/portfolio-feature-tilts" alt="Quarterly portfolio-weighted predictor-rank tilts for the selected Ridge portfolio on independent zero-inclusive panel scales" version="12" %}
</div>

<p class="figure-caption"><strong>Figure 9:</strong> Quarterly paths of the ten largest average absolute realised predictor tilts; panels use their own zero-inclusive scales and label the full-sample mean.</p>

Figure 9 shows a portfolio that is mainly defensive and trend-following. The
long book owns quieter stocks, spends more time above its long-run moving
average, and remains closer to an earlier high. Several panels are variations on
those same two predictor families rather than independent sources of exposure.

The chart describes the finished portfolio; it does not tell us how much return
each predictor caused. Stock-level volatility sizing can strengthen the
defensive pattern, while correlated predictors can lead to similar stock
choices. Figure 9 cannot separate those effects.

The predictor set is not very diverse: about two thirds of
the 144 inputs come from price history or price–volume interactions. Ranking,
broad 75-stock tails, and inverse-volatility sizing can then pull different
coefficient sets toward similar portfolios. A grouped leave-one-family-out test,
run before and after allocation, would show whether each family adds information
or whether portfolio construction is creating the convergence.

## The broader model matters; Ridge adds little

The larger difference is between the five-factor benchmark and the broader
learned model, not between OLS and Ridge. During development, OLS records a Sharpe of 0.98 against
0.71 for the benchmark, with similar net return but lower volatility and a
shallower maximum drawdown. But OLS also receives a broader predictor set and
different data histories, so the comparison changes more than the model weights.

The controlled OLS–Ridge comparison gives a narrower result. At $c=0.01$,
Ridge cuts coefficient magnitude and refit movement by roughly one third, yet
its ranking retains a 0.991 correlation with OLS. Development Sharpe rises only
from 0.98 to 1.00. From January 2022 through May 2026, Ridge trails OLS, 0.82 to
0.87. The selected penalty makes the coefficients smaller and steadier; it does
not clearly improve this trading signal.

Several design choices limit how much weight I place on that result. Overlapping targets,
common shocks within each date, and repeated use of the development history all
reduce the sample's independent information. Equal-date weighting and genuinely
non-overlapping training dates remain useful robustness tests. The predictor
deck is also dominated by related price-based measures, so a stable ranking does
not imply broad feature diversification.

The model comparison and the implementation problem now need different tests. A
genuinely new period is the cleanest way to learn whether Ridge improves the
ranking. Before that evidence arrives, I would keep the OLS and Ridge predictions
frozen, stress the 5 bp cost assumption, and test the allocation layer: size
positions jointly, penalise turnover from current holdings, and constrain gross
exposure, net exposure, market beta, sectors, and the largest realised tilts.
Freezing that complete rule would make the next period more informative.
