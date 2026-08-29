---
layout: post
title: "Technical Note: Portfolio Optimization Implementation"
last_modified_at: 2026-08-29
categories: ["Portfolio construction"]
article_label: Technical note · Ridge allocation
permalink: /quants/portfolio-optimization-technical-note.html
---

<p class="article-summary">This note records the implementation and supporting evidence behind <a href="/quants/portfolio-optimization-preview.html">From Volatility Scaling to State-Aware Portfolio Optimization</a>. It covers the baseline weighting rule, covariance and beta estimates, risk diagnostics, portfolio constraints, state-aware eligibility, robustness tests, and reporting conventions.</p>

## Volatility-scaled baseline

At rebalance date $t$, let $\mathcal L_t$ and $\mathcal S_t$ be the fresh
long and short candidate sets. For stock $i$, $G_{i,t}$ identifies its
sleeve and $d_{i,t}$ its direction:

$$
G_{i,t}=\begin{cases}\mathcal L_t,&i\in\mathcal L_t,\\
\mathcal S_t,&i\in\mathcal S_t,\end{cases}
\qquad
d_{i,t}=\begin{cases}+1,&i\in\mathcal L_t,\\
-1,&i\in\mathcal S_t.\end{cases}
$$

The allocator standardizes the Ridge score $p_{i,t}$ within each sleeve and
maps it through a logistic function:

$$
z_{i,t}=d_{i,t}\frac{p_{i,t}-\bar p_{G_{i,t},t}}
{s_{p,G_{i,t},t}},
\qquad
q_{i,t}=\frac{1}{1+\exp(-\gamma z_{i,t})}.
$$

The logistic scores are normalized within each sleeve and scaled by trailing
volatility. Before the final name cap and sleeve budget, the absolute weight is

$$
\widetilde a_{i,t}
=\min\left(\frac{q_{i,t}}{\sum_{j\in G_{i,t}}q_{j,t}},c\right)
\min\left(\frac{v}{\widehat\sigma_{i,t}^{(\mathrm{ann},L)}},m\right).
$$

The final signed weight is

$$
\begin{aligned}
b_{i,t}&=\min(\widetilde a_{i,t},h),\\
\eta_{G,t}&=\min\left(1,\frac{B_G}{\sum_{j\in G}b_{j,t}}\right),\\
w_{i,t}&=d_{i,t}\eta_{G_{i,t},t}b_{i,t}.
\end{aligned}
$$

The implementation uses $\gamma=2$, a 60-session volatility window, a 10%
pre-volatility score cap, a 20% volatility target, a maximum scaling multiple
of 6, a 4% final name cap, and a 100% budget for each sleeve. The volatility
estimate has a 5% floor and a 20% fallback.

## Return scores and covariance construction

The optimizer uses the fresh top and bottom 75 Ridge ranks. It converts each
Sharpe-like Ridge score into a daily return score by multiplying it by the
stock's 21-session daily volatility forecast:

$$
\mu_{i,t}^{(\mathrm d)}
=p_{i,t}\widehat\sigma_{i,t}^{(\mathrm d,21)}.
$$

For each date $\tau$ in the trailing correlation window, daily returns are
clipped and divided by contemporaneous forecast volatility:

$$
\widetilde r_{i,\tau}
=\frac{\operatorname{clip}(r_{i,\tau},-r_c,r_c)}
{\widehat\sigma_{i,\tau}^{(\mathrm d,21)}}.
$$

Pairwise correlations can contain missing entries or fail to be positive
semidefinite because stocks have different return histories. Missing entries
are filled, negative eigenvalues are clipped, the diagonal is renormalized,
and the repaired correlation matrix is shrunk toward identity:

$$
\begin{aligned}
\widehat C_t&=\operatorname{Corr}(\widetilde{\boldsymbol r}_{\tau}),\\
\overline C_t&=\mathcal P_{\mathrm{corr}}
  \left(\mathcal F_f(\widehat C_t)\right),\\
C_t&=(1-\rho)\overline C_t+\rho I.
\end{aligned}
$$

With $D_t$ denoting the diagonal matrix of daily volatility forecasts, the
annual covariance estimate is

$$
\Sigma_t^{\mathrm{ann}}
=252\,\mathcal P_{\mathrm{PSD}}
\left(\kappa^2D_tC_tD_t\right).
$$

The implementation clips returns at ±30%, fills missing correlations with 0.50,
uses 50% identity shrinkage, and applies the existing scale adjustment
$\kappa=1.18$. That adjustment does not close the forecast gap in the audit
below. Correlations use at most 756 dates and are estimated once 252 dates are
available. A pair can have as few as two overlapping finite returns.

## Risk-calibration audit

Forecast risk is evaluated over each execution-to-execution holding window,
which averages 13.46 trading days. Predicted and realised variances are compared
with QLIKE,

$$
\operatorname{QLIKE}_t
=\frac{v_t}{\widehat v_t}
-\log\left(\frac{v_t}{\widehat v_t}\right)-1.
$$

Lower is better and zero denotes a perfect variance forecast. Non-positive or
non-finite variances fail the audit rather than being silently floored.

The 7% limit applies only to predicted volatility of the target portfolio. The
audit therefore distinguishes four events: a target violation when target-
weight predicted volatility exceeds the limit; an execution overshoot after
rounding and execution; a drift overshoot immediately before the next
rebalance; and a realised overshoot when subsequent volatility exceeds 7%.
Only the first is a solver or constraint failure. The others measure
implementation and calibration.

Across 1,444 rebalance events, mean predicted volatility is 7.00% for B2 and
6.99% for B3, while mean subsequently realised volatility is 8.06% and 8.04%.
Root-mean-square realised volatility is roughly 8.6%, about 20% above the
budget-scale forecasts. Neither optimizer has a target violation. Realised
overshoots occur at roughly 60% of events, which is evidence of underprediction,
not evidence that the optimizer disobeyed its ex-ante constraint. Mean QLIKE is
0.339 for B2 and 0.344 for B3; their calibration is economically similar.

## Market-beta estimation and evaluation windows

The optimizer estimates each stock's market beta as a long-window correlation
multiplied by a short-window volatility ratio:

$$
\widehat\beta_{i,t}
=\widehat{\operatorname{Corr}}_{756}
  (r_{i},r_m)
\frac{\widehat\sigma_{i,t}^{(21)}}
{\widehat\sigma_{m,t}^{(21)}}.
$$

The correlation requires at least 252 finite paired observations; both
volatility estimates require 21. The portfolio constraint applies
$\widehat{\boldsymbol\beta}_t^\top\boldsymbol w_t$ to target weights on the
signal date.

The realized-beta diagnostics answer different questions. The
execution-to-execution diagnostic uses the next 10–14 trading days, a separate
forward diagnostic uses the next 21 trading days, and the main article's time
series uses the trailing 252 trading days. The 252-day series is therefore a
slow outcome measure rather than a direct validation of the point-in-time
constraint.

The predeclared comparison evaluated the current hybrid against coherent 63-day
and 252-day regression betas and a fixed equal blend of coherent 252-day and
756-day estimates. Selection used pre-2022 mean absolute 21-day beta error and
its 90th percentile, with the later period reserved for the frozen comparison.
Portfolio Sharpe did not select the estimator.

The coherent 63-day estimate was the only candidate that improved both
development metrics and retained the improvement later for both allocators. In
the combined fixed-book diagnostic, later mean absolute error fell from 0.153
to 0.143 and 90th-percentile error from 0.329 to 0.301. Matching the 252-day
outcome window was not the solution: both the coherent 252-day estimate and the
252/756 blend deteriorated in the later period.

The 63-day implementation was then rerun inside matched B2 and B3 allocators.
For B2, later holding-window beta error fell from 0.1760 to 0.1592 and all four
persistent episodes disappeared. For B3, error fell from 0.1788 to 0.1647 and
its persistent episodes also disappeared. B3 nevertheless missed two frozen
gates: 90th-percentile error moved from 0.38557 to 0.38596, and later net return
fell from 7.99% to 7.39%, beyond the 0.50-percentage-point tolerance. A universal
63-day replacement was therefore rejected; using different beta estimators for
B2 and B3 after seeing the results would add an unplanned degree of freedom.

The next beta-management experiment will keep the stock book fixed. At each
existing rebalance, the coherent 63-day estimate will size only enough opposite
benchmark exposure to bring forecast beta to the nearest edge of the current
±0.05 band. This tests whether the exposure improvement can be retained without
paying the opportunity cost of changing individual stocks. Hedge turnover,
cost, gross exposure, beta error, persistent episodes, return, and Sharpe must
all be reported; the result will remain exploratory because the later period
has already informed its design.

Before the experiment runs, its implementation contract is frozen: beta is
measured on executed stock weights; the hedge uses the same benchmark return
series as the beta audit; signal formation and execution occur on the existing
rebalance schedule; the hedge is held until the next scheduled rebalance;
financing, dividends, margin, and one-way transaction costs are included;
absolute hedge notional counts toward gross exposure; and hedge returns enter
both holding-window and trailing 252-day realised beta. A directly tradeable
proxy is required—the return index cannot be treated as a costless instrument.

## Complete constraint set

Let $\boldsymbol 1$ be a vector of ones, $\boldsymbol\beta_t$ the estimated
market-beta vector, and $\boldsymbol x_{k,t}$ the indicator for sector $k$.
The optimizer applies these constraints:

$$
\begin{aligned}
0\leq w_i\leq h&\quad(i\in\mathcal L_t),
&-h\leq w_i\leq0&\quad(i\in\mathcal S_t),\\
\lVert\boldsymbol w\rVert_1&\leq g,
&e_{\min}\leq\boldsymbol 1^\top\boldsymbol w&\leq e_{\max},\\
\beta_{\min}\leq\boldsymbol\beta_t^\top\boldsymbol w&\leq\beta_{\max},
&s_{\min}\leq\boldsymbol x_{k,t}^\top\boldsymbol w&\leq s_{\max}.
\end{aligned}
$$

Each sector's share of either side also obeys

$$
\begin{aligned}
\boldsymbol x_{k,t,\mathcal L}^\top\boldsymbol w_{\mathcal L}
&\leq c_{\mathrm{sec}}\boldsymbol 1^\top\boldsymbol w_{\mathcal L},\\
\boldsymbol x_{k,t,\mathcal S}^\top(-\boldsymbol w_{\mathcal S})
&\leq c_{\mathrm{sec}}\boldsymbol 1^\top(-\boldsymbol w_{\mathcal S}).
\end{aligned}
$$

<table class="research-table methodology-table">
  <thead>
    <tr><th>Constraint</th><th>Value</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Sleeve sign</th><td data-label="Value">Long ≥ 0; short ≤ 0</td></tr>
    <tr><th scope="row">Name weight</th><td data-label="Value">4% maximum absolute</td></tr>
    <tr><th scope="row">Gross exposure</th><td data-label="Value">200% maximum</td></tr>
    <tr><th scope="row">Net exposure</th><td data-label="Value">−25% to +25%</td></tr>
    <tr><th scope="row">Russell 1000 beta</th><td data-label="Value">−0.05 to +0.05</td></tr>
    <tr><th scope="row">BICS sector net</th><td data-label="Value">−20% to +20%</td></tr>
    <tr><th scope="row">Sector share per side</th><td data-label="Value">30% maximum</td></tr>
    <tr><th scope="row">Ex-ante volatility</th><td data-label="Value">7% annual maximum</td></tr>
  </tbody>
</table>

## State-aware eligibility and first rebalance

Let $\mathcal K_{\mathcal L,t}$ and $\mathcal K_{\mathcal S,t}$ contain
qualifying incumbent positions on their held side. The state-aware candidate
sets are

$$
\begin{aligned}
\mathcal L_t^{\mathrm{state}}&=\mathcal L_t\cup\mathcal K_{\mathcal L,t},\\
\mathcal S_t^{\mathrm{state}}&=\mathcal S_t\cup\mathcal K_{\mathcal S,t},\\
\mathcal U_t^{\mathrm{state}}&=\mathcal L_t^{\mathrm{state}}
\cup\mathcal S_t^{\mathrm{state}}.
\end{aligned}
$$

Fresh positions enter through the top or bottom 75. Existing holdings remain
eligible through rank 175. Holdings outside that carryover range exit before
the optimizer's voluntary-trade calculation.

For the first solve date $t_0$, the effective trading penalty is zero because
the portfolio begins from cash. Later dates use the configured penalty:

$$
\lambda_t=\begin{cases}0,&t=t_0,\\
\lambda,&t>t_0.\end{cases}
$$

The state-aware objective is

$$
\max_{\boldsymbol w}
\left(\boldsymbol\mu_t^{(\mathrm d)}\right)^\top\boldsymbol w
-\lambda_t\lVert\boldsymbol w-\boldsymbol w_t^-\rVert_1,
$$

subject to the same 7% risk budget and exposure constraints. The configured
penalty coefficient is $\lambda=0.00025$. It is a hyperparameter that controls
the optimizer's aversion to turnover, not a transaction-cost estimate, and it
has no basis-point interpretation. The backtest separately charges a realized
cost of 5 basis points per dollar traded.

## Reporting across rebalance schedules

Each of the three staggered schedules produces a full-capital portfolio. For
allocator $a$, period $P$, metric $M$, and schedule set $\mathcal O$,
the headline value is the mean of the three schedule-level metrics and the
timing spread is their maximum minus minimum:

$$
\begin{aligned}
\overline M_{a,P}
&=\frac{1}{|\mathcal O|}\sum_{o\in\mathcal O}M_{a,o,P},\\
\Delta M_{a,P}
&=\max_{o\in\mathcal O}M_{a,o,P}
-\min_{o\in\mathcal O}M_{a,o,P}.
\end{aligned}
$$

Geometric return, Sharpe, and drawdown are calculated for each schedule before
the three values are averaged. The cumulative-wealth figure in the main article
uses an equal-weight blend of the three return series from their common start;
it is a path reference rather than the headline estimate.

## Robustness tests

The robustness work separates three questions that are easy to conflate:
whether the covariance-shrinkage setting lies in a stable region, whether the
result survives different deterministic rank cutoffs, and whether it survives
different stock identities at a fixed breadth.

### Covariance shrinkage

The predeclared ladder rebuilds B2 and B3 at 11 values of $\rho$ from zero to
one. The Ridge forecasts, selected names, constraints, execution, transaction
costs, and three rebalance schedules remain fixed. The purpose is to locate a
stable region, not to choose the best historical Sharpe cell.

Risk calibration, QLIKE, and holding-window beta error are U-shaped, with a
marginal minimum at $\rho=0.4$. The existing $\rho=0.5$ setting is nearly
identical. For B2, the realised-to-predicted volatility ratio is 1.221 at 0.4
and 1.227 at 0.5; beta mean absolute error is 0.178 and 0.179. For B3, the
corresponding values are 1.191 versus 1.198 and 0.177 versus 0.178. Net Sharpe
is also stable from 0.3 through 0.6. Both endpoints materially degrade the risk
model, so the analysis retains 0.5 instead of retuning to the small in-sample
minimum.

### Deterministic breadth

The breadth test uses the top and bottom 50, 75, 100, or 150 Ridge ranks. This
changes both book size and the score cutoff; it does not randomize stock
identity. B2's 50/50 cell is infeasible under the frozen sector constraints,
whereas B3 completes, so that cell is recorded but excluded from paired
differences.

Across the matched 75/75, 100/100, and 150/150 cells, B3's mean net-Sharpe
advantage is 0.05–0.08 through 2021 and 0.16–0.29 from 2022 onward. Mean
executed turnover is 33.7%–34.0% lower in development and 38.4%–42.9% lower
later. The risk evidence is mixed: later holding-window beta mean absolute
error is 0.010–0.015 worse for B3 at every matched breadth, while volatility
calibration and QLIKE improve. The supported claim is therefore that the
implementation advantage is robust to deterministic breadth, not that every
risk metric improves.

### Random composition

The stock-identity test first forms the top and bottom 200 Ridge candidates.
For each of 20 fixed seeds, a persistent BLAKE2 priority based on seed, asset,
and side selects either 50 or 100 names. The priority persists through time so
the experiment does not create artificial turnover by redrawing the whole book
at every rebalance. B2 and B3 receive the same fresh selections. B3 retains a
100-rank carryover buffer, making these breadth-adjusted variants rather than
literal reruns of the baseline 75/75, rank-175 book.

Only matched feasible B2/B3 seed pairs enter the paired distributions. The
reported result must include every terminal failure, the feasible count at each
breadth, every seed-level point, and the B3-minus-B2 differences in net Sharpe
and executed turnover. Realised volatility and beta error remain supporting
acceptance metrics. These seeds are sensitivity draws from one market history,
not independent return samples.
