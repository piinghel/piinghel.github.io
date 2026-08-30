---
layout: post
title: "From Signal Weighting to Transition-Aware Portfolio Optimization"
date: 2026-08-29
last_modified_at: 2026-08-30
categories: ["Portfolio construction"]
article_label: Portfolio construction · Ridge allocation
permalink: /quants/2026/08/29/portfolio-optimization.html
---

<p class="article-summary">I compare three ways to turn the same Ridge ranking into a long–short portfolio. A fresh-book optimizer improves return but trades heavily. A transition-aware optimizer preserves its gross return while reducing annualized turnover from 42.08× to 27.61×; net return rises from 10.77% to 11.62%. That benefit remains when the portfolio gets wider and the covariance assumptions change, but realized market beta can still drift away from zero.</p>

A standard optimizer sees today's best portfolio, not the cost of getting there
from yesterday's holdings. This can lead it to replace a still-useful holding
for a small score gain. I wanted to know whether making each change pay for
itself could reduce trading without giving back the allocation improvement.

## What stays the same in every test

I use a frozen research snapshot containing daily prices, point-in-time Russell
1000 membership, the Russell 1000 benchmark, and sector classifications.
Returns and portfolio P&L use corporate-action-adjusted daily closing prices.
The P&L engine forward-fills
a missing adjusted price until the position closes; it does not append a
separate delisting-return series. The snapshot begins in 1995; model warm-up
leaves an investable sample from September 1998 through 27 May 2026.

At each rebalance, a fixed walk-forward Ridge model ranks the eligible stocks
using 144 mostly price-based predictors. Its output is a forward Sharpe-like
score: a ranking of risk-adjusted opportunity, not a calibrated return forecast.
Eligibility requires a price of at least five dollars and sufficient signal and risk
history; announced merger targets and duplicate share classes are excluded.
The strongest and weakest scores form the new long and short lists. Table 1
shows how many stocks each list contains. The [Ridge article](/quants/2025/02/09/multiple-linear-regression.html)
describes the predictors and walk-forward model.

I freeze those forecasts so allocation is the only moving part. Every allocator
receives the same stocks, scores, rebalance dates, execution rules, and costs.
A target formed at one close executes at the next trading day's close; the new
book first earns the following close-to-close move. There are three separate
staggered full-capital schedules, each rebalancing every three weeks with a
different weekly starting offset. The interval between consecutive executions
averages 13.46 trading days. B3 can keep a useful holding across several such
intervals. I calculate return, Sharpe, drawdown, and turnover within each
schedule and report their mean; I do not compute the headline metrics from a
blended return stream. Net performance charges 5 basis points for every dollar
bought or sold. The [tranching study](/quants/2025/05/10/rebalancing-luck.html)
explains why all three starting schedules matter.

For a schedule with $$T$$ daily returns, annualized geometric return and net
Sharpe are

$$
g=\left[\prod_{t=1}^{T}(1+r_t)\right]^{252/T}-1,
\qquad
\operatorname{SR}_{\mathrm{net}}
=\sqrt{252}\,\frac{\overline r_{\mathrm{net}}}
{\operatorname{sd}(r_{\mathrm{net}})},
$$

using a zero risk-free rate. If $$\Delta w_t$$ is the executed weight change,
daily net return is $$r_{\mathrm{net},t}=r_{\mathrm{gross},t}
-0.0005\lVert\Delta w_t\rVert_1$$, and annualized two-way turnover is
$$Y^{-1}\sum_t\lVert\Delta w_t\rVert_1$$, where $$Y$$ is the elapsed number of
calendar years. Thus 42.08× means that purchases plus sales total about 42.08
times portfolio capital per year.

Results through 2021 form the development period. January 2022 through May 2026
is a pseudo-holdout: it was separated in advance, but later research decisions
eventually used knowledge of it. It is still useful, but it is not a clean
out-of-sample test.

## Three ways to use the same ranking

I compare three allocation rules:

- **B1, signal-weighted baseline:** weights each stock from its score and its
  own volatility.
- **B2, fresh-book optimizer:** chooses one constrained portfolio from the
  selected stocks, without considering the current holdings.
- **B3, transition-aware optimizer:** solves the same portfolio problem, but
  replaces an existing holding only when the new trade is good enough to justify it.

### B1: signal-weighted baseline

B1 treats the long and short sleeves separately. Let \\(s_{i,t}\\) denote stock
\\(i\\)'s Ridge score at date \\(t\\), \\(\mathcal I_{\ell,t}\\) the stocks in
sleeve \\(\ell\\), and \\(z_{i,t}\\) the cross-sectional z-score of
\\(s_{i,t}\\) within that sleeve. I set \\(d_\ell=+1\\) for long and
\\(d_\ell=-1\\) for short. The normalized signal share is

$$
p_{i,t}
=
\frac{\Lambda(\gamma d_\ell z_{i,t})}
{\sum_{j\in\mathcal I_{\ell,t}}
\Lambda(\gamma d_\ell z_{j,t})}.
$$

Here \\(\Lambda(x)=(1+e^{-x})^{-1}\\) is the logistic function. The
estimate \\(\widehat{\sigma}^{\mathrm{B1}}&#95;{i,t}\\) is annualized stock
volatility over the final \\(h&#95;{\mathrm{B1}}\\) trading sessions. It is
bounded below by \\(\sigma&#95;{\min}^{\mathrm{B1}}\\) and replaced by
\\(\sigma&#95;{\mathrm{fallback}}^{\mathrm{B1}}\\) when unavailable. Its
inverse-volatility multiplier is

$$
\lambda_{i,t}
=
\min\!\left\{
\lambda_{\max},
\frac{\sigma_{\mathrm{target}}}
{\widehat{\sigma}^{\mathrm{B1}}_{i,t}}
\right\}.
$$

The provisional weight caps the signal share before applying the volatility
multiplier, then applies the final name limit:

$$
\widetilde{w}_{i,t}
=
d_\ell
\min\!\left\{
w_{\max},
\min(p_{i,t},p_{\max})\lambda_{i,t}
\right\}.
$$

Finally, B1 scales a sleeve down only when its provisional gross exposure
exceeds the sleeve ceiling:

$$
w^{\mathrm{B1}}_{i,t}
=\eta_{\ell,t}\widetilde{w}_{i,t},
\qquad
\eta_{\ell,t}
=
\min\!\left\{
1,
\frac{G_\ell}
{\sum_{j\in\mathcal I_{\ell,t}}|\widetilde{w}_{j,t}|}
\right\}.
$$

The logistic slope \\(\gamma\\) controls how strongly standardized scores
separate without depending on the Ridge score's raw scale. I set \\(\gamma=2\\),
use a 60-session volatility window, cap the provisional signal share at 10%,
and cap each final stock weight at 4%. The stock-volatility target and the
missing-estimate fallback are both 20%, the floor is 5%, the inverse-volatility
multiplier cannot exceed six, and each sleeve is capped at 100% gross.

This rule is transparent, but it treats each stock separately. It cannot see
that several modest positions may carry the same market or sector risk.

### B2: fresh-book optimizer under a risk budget

B2 needs a return-unit score and a model of joint risk. The Ridge output is a
Sharpe-like score rather than a return forecast, so I convert it to daily
return units using a short-horizon daily volatility estimate:

$$
\mu_{i,t}=s_{i,t}\widehat{\sigma}_{i,t}^{(h_\sigma)}.
$$

For a long candidate with a positive score, or a short candidate with a
negative score, the contribution to \\(\mu_t^\top w_t\\) is positive. The
vector \\(\mu_t\\) is still a return-unit *score*, not a calibrated expected
return forecast.

#### Estimating covariance

Volatility changes faster than correlation, so I estimate them on different
clocks. This separation follows the construction described in Open Source
Quant's [guide to covariance-matrix estimation](https://osquant.com/papers/a-quants-guide-to-covariance-matrix-estimation/):
estimate volatilities and correlations independently, then put them back
together. For each stock,
\\(\widehat{\sigma}&#95;{i,t}^{(h&#95;\sigma)}\\) is the sample standard deviation
of the previous \\(h&#95;\sigma\\) daily returns. It is bounded
below by \\(\sigma&#95;{\min}\\) and replaced by
\\(\sigma&#95;{\mathrm{fallback}}\\) when unavailable. I use a 21-session
window, a 5% annualized floor, and a 20% fallback. These annualized safeguards
are converted to daily units before they enter \\(\mu_t\\) or \\(D_t\\).

Before standardizing, I cap daily returns at ±30% to limit the influence of an
isolated data error; \\(r_{i,\tau}\\) denotes that bounded return below. I then
divide each return by its contemporaneous rolling volatility and estimate each
pairwise correlation on dates valid for both stocks. Let
\\(\mathcal W_t^{(h_R)}\\) be the final \\(h_R\\) trading sessions. Then

$$
x_{i,\tau}
=\frac{r_{i,\tau}}
{\widehat{\sigma}_{i,\tau}^{(h_\sigma)}}.
$$

$$
\mathcal T_{ij,t}
=
\left\{
\tau\in\mathcal W_t^{(h_R)}:
x_{i,\tau},x_{j,\tau}\in\mathbb{R}
\right\}.
$$

$$
\widehat{R}_{ij,t}
=\operatorname{Corr}_{\tau\in\mathcal T_{ij,t}}
\!\left(x_{i,\tau},x_{j,\tau}\right).
$$

The set \\(\mathcal T&#95;{ij,t}\\) keeps the dates on which both standardized
returns are finite. I use a 756-session correlation window and require 252
sessions before the estimator starts. Within that window, a pair needs at
least two common finite observations and positive sample variances.
The very small pairwise minimum can still produce noisy estimates for new
stocks. That is why the next repair and shrinkage steps matter.
A pair that still cannot be estimated receives the fallback correlation
\\(r_{\mathrm{fill}}=0.50\\) before the matrix is repaired. That fallback is an
inherited assumption, not a value tested here. Because long and short weights
have opposite signs, filling every missing correlation with a positive value
can either raise or lower estimated portfolio risk. It is not always the
cautious choice.

$$
R^{\mathrm{fill}}_{ij,t}
=
\begin{cases}
1, & i=j,\\
\widehat{R}_{ij,t}, & i\neq j\ \text{and}\ \widehat{R}_{ij,t}\ \text{is finite},\\
r_{\mathrm{fill}}, & \text{otherwise}.
\end{cases}
$$

The completed matrix is then symmetrized. Write

$$
R_t^{\mathrm{sym}}
=\tfrac12\left(R_t^{\mathrm{fill}}+(R_t^{\mathrm{fill}})^\top\right)
=Q_t\operatorname{diag}(\lambda_{1,t},\ldots,\lambda_{n_t,t})Q_t^\top,
$$

set $$\lambda_{k,t}^{+}=\max(\lambda_{k,t},0)$$, and define

$$
P_t=Q_t\operatorname{diag}(\lambda_{1,t}^{+},\ldots,\lambda_{n_t,t}^{+})Q_t^\top,
\qquad
S_t=\operatorname{diag}\!\left(\sqrt{P_{11,t}},\ldots,\sqrt{P_{n_tn_t,t}}\right),
$$

$$
\widetilde R_t=S_t^{-1}P_tS_t^{-1}.
$$

This sets negative eigenvalues to zero, making the matrix positive
semidefinite, and then restores a unit diagonal. The repair matters because
pairwise estimates based on different overlapping histories need not jointly
form a valid correlation matrix.

The empirical matrix is still noisy, so I shrink it toward the identity:

$$
C_t(\rho)=(1-\rho)\widetilde{R}_t+\rho I,
\qquad 0\leq\rho\leq1.
$$

At \\(\rho=0\\), the model keeps the empirical correlations in full. At
\\(\rho=1\\), every off-diagonal correlation is set to zero. The implemented
setting in Table 1 sits between those extremes; Figure 2 tests it rather than
choosing the best value after seeing portfolio returns.

Finally, let \\(A\\) be the annualization factor and \\(n_t\\) the number of
eligible assets at date \\(t\\). Define the diagonal volatility matrix as

$$
D_t=\operatorname{diag}\!\left(
\widehat{\sigma}_{1,t}^{(h_\sigma)},\ldots,
\widehat{\sigma}_{n_t,t}^{(h_\sigma)}
\right).
$$

The annualized covariance matrix used in the risk constraint is

$$
\Sigma_t=A\kappa^2 D_t C_t(\rho)D_t.
$$

The diagonal matrix \\(D_t\\) sets each stock's risk scale; \\(C_t(\rho)\\)
determines how those risks move together. The factor \\(\kappa\\) rescales the
portfolio-volatility forecast and therefore enters covariance as
\\(\kappa^2\\). It is a frozen calibration correction, not a parameter selected
from the performance results below.

#### The constrained portfolio

The optimizer chooses signed weights \\(w_t\\), positive for the eligible long
set \\(L_t\\) and negative for the eligible short set \\(S_t\\). The vector
\\(\beta_t\\) contains each stock's estimated Russell 1000 beta. It combines a
756-session return correlation, requiring at least 252 observations, with a
21-session stock-to-market volatility ratio. With \\(r_m\\) denoting the
Russell 1000 return,

$$
\widehat{\beta}_{i,t}
=
\widehat{\operatorname{Corr}}^{(\beta)}_{i,m,t}
\frac{\widehat{\sigma}^{(\beta)}_{i,t}}
{\widehat{\sigma}^{(\beta)}_{m,t}}.
$$

I cap the resulting stock beta between −4 and +4 and use zero when it cannot be
estimated. The superscript \\((\beta)\\) distinguishes this volatility ratio
from the covariance diagonal estimate. Stock-level beta enters the portfolio
only through \\(\beta_t^\top w_t\\), its predicted market beta.

Let \\(g_{k,i,t}=\mathbf{1}\{i\text{ belongs to sector }k\}\\), with
\\(g_{k,t}\\) collecting those indicators. With annual risk budget
\\(\sigma_{\star}\\), gross limit \\(G_{\max}\\), name limit \\(w_{\max}\\), net
bounds \\(n_{\min},n_{\max}\\), and portfolio-beta limit \\(b_{\max}\\), B2
solves

$$
\begin{aligned}
\max_{w_t}\quad & \mu_t^\top w_t \\
\text{subject to}\quad
& w_t^\top\Sigma_t w_t\leq \sigma_{\star}^{2}, \\
& \lVert w_t\rVert_1\leq G_{\max},\qquad
  |w_{i,t}|\leq w_{\max}\quad\forall i, \\
& n_{\min}\leq\mathbf{1}^\top w_t\leq n_{\max}, \\
& w_{i,t}\geq0\quad\forall i\in L_t,\qquad
  w_{i,t}\leq0\quad\forall i\in S_t, \\
& -b_{\max}\leq\beta_t^\top w_t\leq b_{\max}.
\end{aligned}
$$

For each sector \\(k\\), define
\\(L_{k,t}=\{i\in L_t:g_{k,i,t}=1\}\\) and
\\(S_{k,t}=\{i\in S_t:g_{k,i,t}=1\}\\). With sector-net limit
\\(q_{\mathrm{net}}\\) and sector-sleeve share \\(q_{\mathrm{leg}}\\), B2 also
imposes

$$
\begin{aligned}
-q_{\mathrm{net}}
&\leq g_{k,t}^\top w_t\leq q_{\mathrm{net}}, \\
\sum_{i\in L_{k,t}}w_{i,t}
&\leq q_{\mathrm{leg}}\sum_{i\in L_t}w_{i,t}, \\
\sum_{i\in S_{k,t}}|w_{i,t}|
&\leq q_{\mathrm{leg}}\sum_{i\in S_t}|w_{i,t}|.
\end{aligned}
$$

The \\(\sigma_{\star}\\) bound is an ex-ante annual volatility budget, not a
promise about realized volatility. The \\(q_{\mathrm{net}}\\) constraint
controls a sector's net exposure as a share of portfolio capital; the separate
\\(q_{\mathrm{leg}}\\) constraint stops one sector from dominating either
sleeve. These are frozen risk limits, not values fitted to the results shown
later. Unlike B1, B2 can reduce a high-scoring stock when another holding
already carries similar risk. Because there is no required gross-exposure
target, the score objective expands the book only until one or more risk or
exposure limits bind.

### B3: transition-aware optimizer

B3 changes the objective and the set of stocks it may hold, but not the risk
model or constraints. A stock already in the portfolio gets some room to stay
when its rank slips just outside the fresh selection. Let \\(F_t^{(N)}\\) be the
fresh top-\\(N\\) and bottom-\\(N\\) candidates, \\(H_t^{\mathrm{pre}}\\) the stocks in
the drifted book immediately
before rebalancing, and \\(T_t^{(K)}\\) the union of the current top-\\(K\\) and
bottom-\\(K\\) ranks. B3 may optimize over

$$
E_t=F_t^{(N)}\cup\left(H_t^{\mathrm{pre}}\cap T_t^{(K)}\right).
$$

A new position can enter only through the strongest or weakest \\(N\\)
scores. An existing holding may stay while it remains in either rank tail out
to \\(K\\), but it stays on its current side of the book. Moving from long to
short, or short to long, requires re-entry through the fresh selection. The carryover
buffer \\(K-N\\) is fixed in advance rather than chosen to maximize the reported
result. The breadth test keeps that buffer unchanged as the new stock lists grow.

Let \\(w_{t,E_t}^{\mathrm{pre}}\\) be the actual price-drifted portfolio
immediately before the rebalance, restricted to \\(E_t\\). B3 solves

$$
\max_{w_t\in\mathbb{R}^{|E_t|}}\quad
\mu_{t,E_t}^\top w_t
-c\lVert w_t-w_{t,E_t}^{\mathrm{pre}}\rVert_1,
$$

subject to the same constraints as B2. The coefficient \\(c\\) lowers the score
of a proposed portfolio when it changes more weight; its value is in Table 1.
There is no hard turnover cap. The backtest separately charges the realized trading
cost \\(c_{\mathrm{exec}}\\) for every dollar actually bought or sold, whether
or not the optimizer anticipated the trade. There are no old holdings on the
first build, so no trade penalty applies. A stock that becomes ineligible must
still be sold; the backtest charges that trade even though the optimizer cannot
choose to keep it.

Table 1 summarizes the settings that define the three allocators. I leave the
narrower estimation safeguards in the text so the table stays readable.
Figures 2 and 3 then test shrinkage and breadth.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Component</th><th>Frozen setting</th><th>Role in the design</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Fresh selection</th><td data-label="Frozen setting">75 long + 75 short</td><td data-label="Role in the design">Defines the stocks that may enter the reference book.</td></tr>
    <tr><th scope="row">B1 sizing</th><td data-label="Frozen setting"><span><i>γ</i> = 2; 60-day volatility; 20% volatility target; 4% per name</span></td><td data-label="Role in the design">Maps each score and stock volatility into a standalone weight; each sleeve is capped at 100%.</td></tr>
    <tr><th scope="row">B2/B3 risk model</th><td data-label="Frozen setting"><span>21-day volatility; 756-day correlation; <i>ρ</i> = 0.50; calibration 1.18</span></td><td data-label="Role in the design">Builds covariance from faster volatility and slower correlation estimates.</td></tr>
    <tr><th scope="row">Portfolio limits</th><td data-label="Frozen setting">7% volatility; 200% gross; 4% per name; ±25% net; ±0.05 beta</td><td data-label="Role in the design">Constrains total risk, concentration, direction, and estimated market exposure.</td></tr>
    <tr><th scope="row">Sector limits</th><td data-label="Frozen setting">±20% net; 30% of either leg</td><td data-label="Role in the design">Controls net sector bets and one-sided concentration.</td></tr>
    <tr><th scope="row">B3 transition</th><td data-label="Frozen setting">2.5 bp trade penalty; carryover to rank 175</td><td data-label="Role in the design">Keeps useful existing holdings unless a replacement offers enough improvement.</td></tr>
    <tr><th scope="row">Realized trading cost</th><td data-label="Frozen setting">5 bp per dollar bought or sold</td><td data-label="Role in the design">Converts executed turnover into the net return used in evaluation.</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Settings used for the reference 75-name portfolios. Estimation safeguards are defined in the surrounding methodology.</p>

I keep these values unchanged for the comparison, but that does not make them
independently tested. The B1 settings, risk budget, and calibration factor come
from earlier work. I chose B3's trade penalty and carryover rank during
development from fixed ladders. The headline comparison keeps them in place;
Figures 2 and 3 then vary shrinkage and breadth.

## The main gain comes from trading less

Across September 1998 through May 2026, the fresh-book optimizer raises gross
return from the baseline's 10.31% to 13.13%, but annualized turnover rises from
29.94× to 42.08×. The transition-aware optimizer earns nearly the same gross
return and trades much less. Table 2 shows how that lower cost drag raises net
return by 0.85 percentage points and net Sharpe from 1.24 to 1.33.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Allocator</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">B1 · Signal-weighted baseline</th><td data-label="Gross return">10.31%</td><td data-label="Net return">8.67%</td><td data-label="Net Sharpe">1.05</td><td data-label="Turnover">29.94×</td></tr>
    <tr><th scope="row">B2 · Fresh-book optimizer</th><td data-label="Gross return">13.13%</td><td data-label="Net return">10.77%</td><td data-label="Net Sharpe">1.24</td><td data-label="Turnover">42.08×</td></tr>
    <tr><th scope="row"><strong>B3 · Transition-aware optimizer</strong></th><td data-label="Gross return"><strong>13.17%</strong></td><td data-label="Net return"><strong>11.62%</strong></td><td data-label="Net Sharpe"><strong>1.33</strong></td><td data-label="Turnover"><strong>27.61×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Portfolio construction and full-period implementation. Metrics are means of the three full-capital rebalance schedules. Returns are annualized; net results charge 5 basis points for every dollar bought or sold. Turnover is annualized executed two-sided L1.</p>

In this backtest, B3 keeps B2's gross return while trading much less. That
directly improves the result after costs. The risk forecasts still need a
separate test.

## The improvement remains, but timing matters

Through 2021, the baseline, fresh-book, and transition-aware portfolios earn
annualized net returns of 8.92%, 11.60%, and 12.32%. From January 2022 through
May 2026, they earn 7.38%, 6.47%, and 7.99%. Figure 1 shows
when those differences accumulated and how much capital each path lost from its
previous peak.

<div class="research-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/performance-and-drawdowns" alt="Net growth of one dollar on a logarithmic scale and transparent drawdown areas for the signal-weighted baseline, fresh-book optimizer, and transition-aware optimizer, with the later period beginning in 2022" version="7" %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Net growth of <span class="mathjax-ignore">$1</span> and drawdown for the average of the three rebalance-schedule paths after trading costs, 22 September 1998–27 May 2026. The vertical rule marks January 2022, the start of the later pseudo-holdout. The plotted average shows when gains and losses occurred; Table 2 reports the mean of the three schedules' metrics.</p>

The upper panel shows the transition-aware portfolio finishing above the
fresh-book optimizer without a visibly larger major drawdown in the lower
panel. The path is not smooth, however, and the later advantage is not
monotonic.

The three transition-aware schedules differ by 4.49 percentage points in
later-period net return and by 0.43 in Sharpe. Over this relatively short later
period, the choice of rebalance dates still matters.

## Why transition awareness trades less

The design has two moving parts. Carryover keeps acceptable existing
positions; the trade penalty gives the optimizer a reason not to replace them for a
small forecast gain. Table 3 separates the two mechanisms before combining
them.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Variant</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Fresh book · neither mechanism</th><td data-label="Gross return">13.13%</td><td data-label="Net return">10.77%</td><td data-label="Net Sharpe">1.24</td><td data-label="Turnover">42.08×</td></tr>
    <tr><th scope="row">Carryover only · rank 175</th><td data-label="Gross return">13.16%</td><td data-label="Net return">10.96%</td><td data-label="Net Sharpe">1.25</td><td data-label="Turnover">39.00×</td></tr>
    <tr><th scope="row">Trade penalty only · 2.5 bp</th><td data-label="Gross return">13.02%</td><td data-label="Net return">11.07%</td><td data-label="Net Sharpe">1.27</td><td data-label="Turnover">34.83×</td></tr>
    <tr><th scope="row"><strong>Transition-aware · both</strong></th><td data-label="Gross return"><strong>13.17%</strong></td><td data-label="Net return"><strong>11.62%</strong></td><td data-label="Net Sharpe"><strong>1.33</strong></td><td data-label="Turnover"><strong>27.61×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 3:</strong> Comparison of carryover and the trade penalty using 75 stocks per side. The penalty guides the optimizer; realized trading costs remain 5 basis points for every dollar bought or sold. The two choices work together, so the gain from using both is not the simple sum of the two one-at-a-time rows.</p>

Carryover alone trims turnover modestly. The trade penalty does more, and using
both produces the largest reduction and the highest net Sharpe.

Forced exits still account for 36% of modeled transition-aware turnover. The
design reduces discretionary replacement; it does not make trading disappear.

## The covariance setting lies in a stable region

The covariance model pulls noisy estimated correlations toward zero. Figure 2
varies that adjustment from none to treating all stock pairs as uncorrelated.
The Ridge forecasts, selected stocks, constraints, costs, and execution stay
fixed. If
the result disappears outside one exact setting, it is too fragile to trust.

The top-left panel of Figure 2 divides realized volatility by forecast
volatility; a value of one is ideal. The beta panel measures the average
absolute gap between forecast and realized beta; lower is better.

<div class="research-figure rho-ladder-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/rho-ladder" alt="Risk calibration, beta error, turnover, and mean schedule-level net Sharpe for the fresh-book and transition-aware optimizers across covariance-shrinkage values from zero to one" version="4" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Results as covariance shrinkage changes over the full September 1998–May 2026 sample. The shaded 0.3–0.6 region changes little across risk calibration, beta error, turnover, and mean schedule-level net Sharpe. The risk measures are slightly best at 0.4; the portfolios used elsewhere in the article keep the original 0.5 setting.</p>

The center of each panel is nearly flat. The 0.4 setting has the lowest risk
errors in this sample, but moving the transition-aware
optimizer from 0.4 to the implemented 0.5 changes net return from 11.59% to
11.62%, leaves net Sharpe at 1.33, and changes the
realized-to-predicted-volatility ratio from 1.191 to 1.198. I keep 0.5 rather
than change the reference portfolio for differences this small.

At zero shrinkage, realized volatility is about 1.3 times forecast. At full
identity it rises to about 1.7 times forecast, beta error increases, and net
Sharpe falls. Turnover declines gradually as shrinkage increases, but the lower
trading at the high-shrinkage extreme does not compensate for worse risk
forecasts and Sharpe.

## The advantage survives larger portfolios

I next widen the long and short books while leaving the ranking rule unchanged.
This changes the rank cutoff, so Figure 3 tests portfolio breadth—not whether
the result survives a different stock sample. The transition-aware optimizer keeps the same 100-rank
carryover band as the book grows: fresh 50, 75, 100, and 150-name sleeves use
carryover limits of 150, 175, 200, and 250. Figure 3 shows Sharpe and turnover
for each allocator rather than only the differences between them.

<div class="research-figure deterministic-breadth-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/deterministic-breadth" alt="Grouped bars comparing actual net Sharpe and annualized turnover for the signal-weighted baseline, fresh-book optimizer, and transition-aware optimizer from 50 to 150 selected names per side before and after 2022" version="7" %}
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Mean net Sharpe and annualized executed turnover across the three full-capital schedules. The matched 50-name optimizer pair uses a 35% per-leg sector cap; the 75-, 100-, and 150-name cells retain the reference 30% cap.</p>

At 50 names, both optimizer cells use a 35% rather than 30% sector-share cap:
one selected tail contains only three sectors, so a non-empty leg requires
slightly more than one-third. The wider cells retain 30%.

At 50 names per side, B1 earns mean net Sharpe of 1.13 before 2022 and 0.73
afterward, with annualized turnover of 30.93× and 29.57×. B2 records 1.35 and
0.71 Sharpe with turnover of 40.05× and 34.53×, while B3 records 1.40 and 0.96
with turnover of 26.47× and 22.16×.

The upper panel shows B3 with the highest net Sharpe at every displayed
breadth. Before 2022, B1 moves from 1.13 at 50 names to 1.07 at 150, B2 moves
from 1.35 to 1.30 across the 50–150 range, and B3 stays between 1.35 and
1.43. Later, B1 rises from 0.73 at 50 to roughly 0.78–0.80 at the wider books,
B2 falls from 0.71 to 0.64, and B3 ranges from 0.87 to 0.96. B3 still leads when
the simpler B1 rule is included.

Gross and net returns tell the same economic story. At 75 names, B3 earns
13.91% gross and 12.32% net before 2022, versus 10.58% and 8.92% for B1 and
14.00% and 11.60% for B2. At 150 names, B3 earns 13.19% gross and 11.54% net,
versus 8.96% and 7.47% for B1 and 13.58% and 11.09% for B2. In the later period,
B3's gross/net return is 9.33%/7.99% at 75 names and 9.76%/8.37% at 150; both
endpoints remain above B1 and B2 after costs.

The 50-name portfolios show the same pattern in returns. Before 2022,
B1, B2, and B3 earn 11.33%/9.62%, 13.76%/11.50%, and 13.48%/11.99% gross/net.
Later, the three values are 8.85%/7.24%, 8.21%/6.35%, and
10.06%/8.84%.

The lower panel shows the same comparison in trading rather than performance.
Transition-aware turnover ranges from 26.47× to 29.37× before 2022 and from
22.16× to 25.41× afterward; fresh-book turnover lies around 40–45× before 2022
and 35–45× afterward. B1 turns over 30× at 75 names and falls to roughly 25–27×
at 150. B3 remains far below B2 throughout and below B1 at 75 and 100 names,
but B1 is slightly lower at 150. B3 keeps its turnover advantage over
B2 as the book widens, although B1 trades slightly less at 150 names.

The risk results are less consistent. From 2022 onward, B3's holding-window beta
error is only 0.001–0.005 higher than B2's, but the difference persists at all
four breadths. Volatility calibration and QLIKE—a variance-forecast loss where
lower is better—improve at 75, 100, and 150 names and worsen slightly at 50.
There are no target-risk violations. The gaps are small, but their consistency
means I would not claim that B3 forecasts risk better than B2. They do not
change the clear reduction in trading.

The test also changes the rank cutoff. A separate test is still needed to learn
whether the result holds for different groups of stocks at the same breadth.

## The beta forecast still needs work

The volatility target and the beta limit answer different questions. The 7%
target is a point-in-time forecast. Across B3 rebalance windows, mean predicted
and realized volatility are 6.99% and 8.04%, so the average outcome is about
15% higher. Figure 2 uses a more tail-sensitive root-mean-square comparison:
7.16% predicted versus 8.58% realized, a ratio of 1.198. The beta limit is also
enforced when the portfolio is chosen, but the exposure can change as prices
and beta estimates evolve.

Figure 4 shows how realized beta can move away from zero after the portfolio is
formed. It compares the fresh-book and transition-aware optimizers using
trailing 252-day realized beta, sampled monthly. I do not draw the optimizer's
±0.05 target band on this chart: that
band applies to a different, point-in-time beta estimate, whereas the plotted
measure deliberately moves slowly.

<div class="research-figure risk-beta-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/risk-calibration-and-beta" alt="Trailing 252-day realized market beta for the fresh-book and transition-aware optimizers, sampled monthly, with a zero reference line" version="7" %}
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Trailing 252-day realized market beta, sampled monthly and averaged across the three rebalance schedules, September 1998–May 2026. The zero line is a neutral reference. I omit the point-in-time optimizer band because it is not directly comparable.</p>

The chart shows that both optimized books have spent extended periods away from
zero. Using the same cutoff throughout—absolute beta above 0.20 for at least 63
trading days—the transition-aware portfolio has five such episodes covering 339
days, with a 0.251 peak. The fresh-book optimizer has four episodes covering 600
days, with a 0.309 peak. Since 2022, B3 is much calmer: monthly absolute beta
averages 0.035, reaches 0.064 at the 90th percentile, and peaks at 0.081.

B3's point-in-time beta constraint binds on 48.3% of optimizer dates, and
execution drift adds only about 0.001 mean absolute beta. At each rebalance, B3
stays within the beta limit. This points to the beta estimate used to choose the
portfolio, not a failure by the optimizer to obey its constraint.

A shorter beta estimate makes the trade-off visible. The baseline combines a
756-day stock–market correlation (minimum 252 observations) with 21-day stock
and market volatilities (minimum 21). The candidate changes both components to
63-day windows with a 42-observation minimum and leaves the allocator otherwise
fixed. I selected it using forward beta error through 2021, then assessed that
frozen choice in the later period. It removes the persistent episodes, but from
2022 onward B3's net return falls from 7.99% to 7.39%—a 0.60 percentage-point
decline against the predeclared 0.50-point tolerance—and Sharpe falls from 0.87
to 0.82, while turnover barely changes. The candidate fails the return tolerance,
so I reject it.

The episode cutoff—absolute trailing realized beta above 0.20 for at least 63
trading sessions—only summarizes the chart. The optimizer never sees it.

The cleaner next test is a costed benchmark overlay that leaves the B3 stock
weights untouched. That separates beta management from stock selection;
tightening the stock constraint first would mix them again.

## Conclusion

In this backtest, B3 keeps what worked in B2 while removing much of the extra
trading. It cuts annualized turnover from 42.08× to 27.61× without giving up
gross return, which raises net return and Sharpe after the stated costs. At the
reference 75-name breadth, B3 also has
the strongest later-period result: 7.99% net return and a 0.87 Sharpe from
January 2022 through May 2026. I would carry B3 forward as the portfolio rule.

All three rules weakened after 2021, so the decline is not unique to B3. That
later period covers only about four years and five months, and the three B3
schedules still differ enough to matter. Beta error and volatility
underprediction show that the risk forecasts still need work; they do not erase
the improvement in turnover and net performance shown here. The 5 bp
cost rule also omits market impact and borrow. A costed benchmark overlay is the
next useful beta test. More data are needed to tell whether the later result
holds up.
