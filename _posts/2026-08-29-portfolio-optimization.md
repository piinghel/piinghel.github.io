---
layout: post
title: "From Volatility Scaling to a Constrained Optimizer"
date: 2026-08-29
last_modified_at: 2026-09-02
categories: ["Portfolio construction"]
article_label: Portfolio construction · Ridge allocation
permalink: /quants/2026/08/29/portfolio-optimization.html
---

<p class="article-summary">Volatility scaling sizes stocks one at a time and leaves portfolio exposures uncontrolled. A constrained optimizer sizes the whole book under explicit risk limits. Gross return rises from about 10% to 13%, but the framework depends on a covariance estimate and trades more. Making it account for current holdings removes that extra trading without giving back gross return. Realized beta remains the main open problem.</p>

The [Ridge study](/quants/2025/02/09/multiple-linear-regression.html) found that
learned rankings raised turnover and ended with two open tasks: size stocks
jointly and penalize changes from the current portfolio. The earlier
[low-volatility study](/quant/2024/12/15/low-volatility-factor.html) reached the same
joint-sizing question from a different direction. This article runs that test
using the staggered schedules from the
[tranching study](/quants/2025/05/10/rebalancing-luck.html).

The state of the strategy is fixed: Russell 1000 stocks, a walk-forward Ridge
score, three-week staggered rebalancing, and a five-basis-point trading cost.
Only the rule that turns scores into weights changes.

Table 1 reports gross return, net return, net Sharpe, and turnover for the three
rules. Higher is better in the return and Sharpe columns; lower is better for
turnover. The two optimizer rows are the central comparison.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">B1 · Signal-weighted</th><td data-label="Gross return">10.31%</td><td data-label="Net return">8.67%</td><td data-label="Net Sharpe">1.05</td><td data-label="Turnover">29.94×</td></tr>
    <tr><th scope="row">B2 · Fresh-book optimizer</th><td data-label="Gross return">13.13%</td><td data-label="Net return">10.77%</td><td data-label="Net Sharpe">1.24</td><td data-label="Turnover">42.08×</td></tr>
    <tr><th scope="row"><strong>B3 · Transition-aware optimizer</strong></th><td data-label="Gross return"><strong>13.17%</strong></td><td data-label="Net return"><strong>11.62%</strong></td><td data-label="Net Sharpe"><strong>1.33</strong></td><td data-label="Turnover"><strong>27.61×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Key results, September 1998–May 2026. Metrics are means of three full-capital rebalance schedules. Returns are annualized; net results charge 5 basis points for every dollar bought or sold. Turnover is annualized purchases plus sales.</p>

The rule that accounts for current holdings raises net Sharpe in every matched
schedule. The schedule-level gain ranges from 0.05 to 0.16. Table 1 does not
identify the mechanism; the ablation in Table 3 does.

## What stays the same in every test

I use a frozen research snapshot with daily prices, point-in-time Russell 1000
membership, the Russell 1000 benchmark, and sector classifications. Adjusted
closing prices drive both signals and P&L.

At each rebalance, a fixed walk-forward Ridge model ranks eligible stocks using
mostly price-based predictors. Its output is a risk-adjusted score, not a
calibrated return forecast. Eligibility requires sufficient signal and risk
history, as well as a price of at least five dollars. I exclude announced
merger targets and duplicate share classes. The strongest and weakest scores
form the new long and short lists. The [Ridge article](/quants/2025/02/09/multiple-linear-regression.html)
describes the model and predictors.

I freeze those scores so portfolio construction is the only moving part. Every
rule receives the same stocks, rebalance dates, execution rules, and costs. A
target formed at one close executes at the next close. The new portfolio first
earns the following close-to-close return, which prevents same-close look-ahead.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Component</th><th>Frozen setting</th><th>Why it is fixed</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Investable sample</th><td data-label="Frozen setting">22 September 1998–27 May 2026</td><td data-label="Why it is fixed">Uses the same point-in-time universe and warm-up for every rule.</td></tr>
    <tr><th scope="row">Ranking</th><td data-label="Frozen setting">Walk-forward Ridge; 144 predictors</td><td data-label="Why it is fixed">Gives every rule the same stocks and scores.</td></tr>
    <tr><th scope="row">Fresh selection</th><td data-label="Frozen setting">75 long + 75 short</td><td data-label="Why it is fixed">Defines the reference portfolio.</td></tr>
    <tr><th scope="row">Rebalancing</th><td data-label="Frozen setting">Three staggered schedules; every three weeks</td><td data-label="Why it is fixed">Separates the allocation result from one lucky start date.</td></tr>
    <tr><th scope="row">Execution</th><td data-label="Frozen setting">Signal at one close; trade at the next close</td><td data-label="Why it is fixed">Prevents same-close look-ahead.</td></tr>
    <tr><th scope="row">Realized trading cost</th><td data-label="Frozen setting">5 bp per dollar bought or sold</td><td data-label="Why it is fixed">Turns executed trades into the net result.</td></tr>
    <tr><th scope="row">Evaluation</th><td data-label="Frozen setting">Development through 2021; later period from 2022</td><td data-label="Why it is fixed">Shows whether the result continued after the development window.</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Inputs, sample, timing, and evaluation held fixed across all three portfolio rules. Table A1 gives the rule-specific parameters.</p>

The middle column states the shared setting; the last explains why it cannot
drive a difference between rules. The ranking, schedule, and cost rows matter
most for interpretation. The table does not test whether those fixed choices
are optimal.

Each schedule is a separate full-capital portfolio. I calculate its return,
Sharpe, drawdown, and turnover, then report the mean across schedules. I do not
blend their return streams before calculating the headline metrics. The
[tranching study](/quants/2025/05/10/rebalancing-luck.html) explains why the
three starting schedules matter.

The development period ends in 2021. The later chronological check starts in
2022.

## Transition awareness changes the current portfolio, not the forecast

The **signal-weighted rule** sizes each stock from its score and its own recent
volatility. Stronger scores receive more weight, while more volatile stocks
receive less. The long and short books are scaled separately. This makes the
rule easy to inspect, but it treats stocks one at a time. It cannot recognize
that several modest positions may carry the same market or sector risk.

The **fresh-book optimizer** starts with the same ranking. It converts each
score to return units using recent stock volatility, then chooses all weights
together. A covariance model captures common risk, while constraints limit
forecast volatility, beta, gross and net exposure, sector exposure, and
single-stock concentration. This allows the optimizer to reduce a high-scoring stock
when another holding already carries similar risk.

Volatility changes faster than correlation, so I estimate them on different
windows. I then repair the pairwise correlation matrix and shrink its noisy
off-diagonal estimates toward zero. A frozen calibration factor rescales the
resulting portfolio-volatility forecast. These choices affect feasibility and
weights, not just a diagnostic, which is why the shrinkage check later varies
the full portfolio rather than rescaling a chart.

The fresh-book optimizer still has no memory. At each rebalance it solves for
the best portfolio among the newly selected stocks. An existing holding gets no
credit for already being in the book, even when its replacement offers only a
small improvement.

The **transition-aware optimizer** keeps the same score, covariance model, and
constraints. It changes two things. First, an existing stock may remain
eligible after its rank slips outside the fresh selection, provided it stays in
a wider rank tail. Second, the objective subtracts a penalty for changing the
price-drifted portfolio. Together, these rules create a buffer around marginal
replacements.

There is no hard turnover cap. A strong enough improvement still leads to a
trade, and an ineligible stock must still leave. The objective's trade penalty
is also separate from the realized transaction cost in the backtest. One guides
the optimizer; the other reduces net return for every dollar actually bought or
sold. The full equations and safeguards are in the appendix.

## Trading less is the whole gain after costs

The fresh-book optimizer raises gross return, but turnover increases from about
30× to 42×. Transition awareness matches that gross return and cuts turnover to
28×. Table 1 shows the resulting improvement in net return and Sharpe.

This distinction matters. The transition-aware rule does not win because its
gross backtest compounds faster. It reaches nearly the same portfolio with
fewer replacements. The cost saving is the gain.

Figure 1 plots net growth on a logarithmic scale in the upper panel and
drawdown in the lower panel. Each color is one portfolio rule. The vertical
line starts the later period. A better path finishes higher in the top panel
without spending more time deep in the bottom panel.

<div class="research-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/performance-and-drawdowns" alt="Net growth of one dollar on a logarithmic scale and transparent drawdown areas for the signal-weighted baseline, fresh-book optimizer, and transition-aware optimizer, with the later period beginning in 2022" version="7" %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Net growth of <span class="mathjax-ignore">$1</span> on a logarithmic scale (top) and drawdown in percent (bottom) for the signal-weighted, fresh-book, and transition-aware rules after trading costs, September 1998–May 2026. The paths average the three rebalance schedules; the vertical rule marks the start of the later period.</p>

Look first at the endpoints, then the major drawdowns. The transition-aware
path finishes highest without a larger major loss, but the lead develops
unevenly. The plot averages schedule paths; Table 1 reports schedule-level
metrics instead.

The later-period mean return edge over the fresh-book optimizer is about 1.5
percentage points. The transition-aware schedules span 4.5 points. The mean
gap therefore sits inside rebalance-timing dispersion.

All three rules weaken after the boundary. One explanation is decay in the
shared price-based ranking rather than a change in portfolio construction.
Crowding, the rate regime, and universe drift are plausible mechanisms, but the
current evidence does not distinguish them.

## The trade penalty does most of the work; carryover adds to it

Carryover lets an acceptable holding remain in the eligible set. The trade
penalty makes a replacement compete with the cost of changing the book. In
Table 3, the top row uses neither mechanism, the middle rows add one at a time,
and the bottom row uses both. Read the return and Sharpe columns upward and the
turnover column downward.

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

<p class="table-caption"><strong>Table 3:</strong> Carryover and trade-penalty ablation using the reference portfolios. The penalty guides the optimizer; the backtest still charges the same realized cost. The mechanisms interact, so their combined effect is not the sum of the two middle rows.</p>

The penalty-only row captures most of the improvement. Adding carryover cuts
turnover by another 7× and raises mean Sharpe by 0.06. That Sharpe increment is
close to the 0.05 schedule range, so the case for carryover rests more on
trading than on a precisely estimated performance gain.

Gross return barely changes across the four rows. I read this as evidence that
many marginal replacements add little at the portfolio level. It is not a
trade-level alpha test: changes in risk and exposure could offset the returns of
the skipped trades. A matched analysis of replaced versus retained stocks, with
the Ridge score's rank persistence, would separate those explanations.

Trading does not disappear. Forced exits still account for 36% of modeled
transition-aware turnover. The design reduces discretionary replacements; it
cannot retain a stock that leaves the eligible universe.

## The covariance choice is not carrying the result

Covariance shrinkage pulls noisy stock-correlation estimates toward zero. In
Figure 2, the horizontal axis moves from the empirical matrix to treating every
stock pair as uncorrelated. The panels show how much realized volatility
exceeded forecast, beta error, annualized turnover, and net Sharpe. The two
colors are the fresh-book and transition-aware optimizers over the full sample.

For the risk panels, lower is better and a volatility ratio near one is ideal.
Lower turnover and higher Sharpe are better in the bottom row. A flat line
means that the conclusion does not depend on one exact covariance setting.

<div class="research-figure rho-ladder-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/rho-ladder" alt="Risk calibration, beta error, turnover, and mean schedule-level net Sharpe for the fresh-book and transition-aware optimizers across covariance-shrinkage values from zero to one" version="4" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Full-sample volatility calibration (top left), holding-period beta error (top right), annualized turnover (bottom left), and net Sharpe (bottom right) as correlation shrinkage moves from none to full identity. Slate is the fresh-book optimizer; orange is the transition-aware optimizer. The shaded region marks the stable middle of the range.</p>

Look at the shaded middle. The curves change little from 0.3 to 0.6, and the
implemented choice is 0.5. A nearby setting has slightly lower risk errors, but
Table A3 shows no meaningful performance difference. I keep the frozen value
rather than tune to the in-sample minimum.

The extremes are more informative. With no shrinkage, noisy empirical
correlations understate realized volatility. Treating every pair as
uncorrelated makes the miss larger and beta error worse. Turnover declines as
shrinkage rises, but that saving does not offset the loss in risk control and
Sharpe. The transition-aware advantage survives throughout the useful middle
of the range. This is a historical sensitivity check, not an independent
estimate of the best shrinkage value.

## The advantage survives wider portfolios

Figure 3 puts net Sharpe in the top row and annualized turnover in the bottom
row. The horizontal axis is the number of selected stocks on each side. The
left column is the development period; the right is the later period. Within
each breadth, color identifies the rule. Higher is better for Sharpe and lower
is better for turnover.

<div class="research-figure deterministic-breadth-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/deterministic-breadth" alt="Grouped bars comparing actual net Sharpe and annualized turnover for the signal-weighted baseline, fresh-book optimizer, and transition-aware optimizer from 50 to 150 selected names per side before and after 2022" version="7" %}
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Net Sharpe (top) and annualized purchases plus sales (bottom) for the three portfolio rules by selected stocks per side. The left panels end in 2021; the right panels cover January 2022–May 2026. The narrowest optimizer pair uses a looser sector-share cap because one selected tail contains only three sectors.</p>

The transition-aware optimizer has the highest mean Sharpe at every tested
breadth in both periods. In development, the gaps over the fresh-book optimizer
run from 0.05 to 0.08 while schedule ranges reach 0.14. The ordering is stable,
but those early-period differences are small.

The later gaps are larger. At the narrowest book, mean Sharpe is 0.96 versus
0.71. Schedule dispersion also widens, so the mean bars should not be read as
precise rankings.

Turnover tells a slightly different story. Transition awareness remains well
below the fresh-book optimizer throughout. It also trades less than the
signal-weighted rule at the middle breadths. At the widest book, the simpler rule
trades slightly less. That is the one turnover comparison the transition-aware
optimizer loses.

The horizontal axis changes the rank cutoff. The transition-aware rule keeps a
fixed 100-rank buffer as the book widens, but Figure 3 does not test different
stock identities at a fixed breadth.

The risk evidence is mixed. Transition awareness improves volatility forecasts
at most breadths, but its later-period beta error is a few thousandths higher
than the fresh-book optimizer's throughout. That does not change the trading
result, but it rules out a claim that transition awareness improves every part
of the risk model.

## Risk forecasts and capacity remain the weak links

The volatility target and beta limit answer different questions. The first is
a point-in-time portfolio forecast. Realized volatility averages about 15%
above it for the transition-aware portfolio. The beta limit is also enforced
when weights are chosen, but exposure can change as prices and beta estimates
move during the holding period.

Figure 4 plots monthly trailing one-year realized beta for all three rules. The
volatility-scaled rule supplies the baseline; the two optimizer lines show what
joint sizing changes. I omit the optimizer's band because it applies to a
different, point-in-time estimate.

<div class="research-figure risk-beta-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/risk-calibration-and-beta" alt="Trailing 252-day realized market beta for the volatility-scaled rule, fresh-book optimizer, and transition-aware optimizer, sampled monthly, with a zero reference line" version="8" %}
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Monthly trailing one-year realized market beta for the volatility-scaled rule and both optimizers, averaged across the three schedules, September 1998–May 2026. The point-in-time optimizer constraint uses a different estimate and clock, so its target band is not overlaid.</p>

Look at the long departures from zero rather than one-month peaks. The
optimizers reduce persistent beta relative to volatility scaling, but they do
not remove it. Table A4 gives episode counts and magnitudes for the two
optimizers; the chart does not attribute returns to beta.

Constraint compliance is not the problem. The beta limit binds on nearly half
of transition-aware rebalance dates. The chosen portfolio remains inside the
limit, and execution drift adds only a few thousandths. This points to the beta
estimate used to choose stocks and weights.

I tested a shorter-window estimate selected on the development period. It
removes the persistent beta episodes, but later net return falls by 0.60
percentage points. That exceeds the 0.50-point tolerance I fixed before
checking the later period, so I reject it.

That missing attribution matters. Some of the return difference between rules
or periods may come from market exposure rather than stock selection. The saved
evidence has no beta-residual return decomposition, so I do not treat the later
mean return lead as proof of stronger selection.

Turnover also remains high after the improvement. At roughly 28× purchases plus
sales per year, capacity depends on market impact, borrow, and the stocks at the
edge of the universe. A flat five-basis-point cost is useful for a matched
comparison, but it is not a capacity model.

The cleaner next test is a costed benchmark overlay that leaves the stock
portfolio untouched. It would separate beta management from stock selection.
Tightening the stock constraint first would mix them again.

## Conclusion

I carry the transition-aware optimizer forward. It keeps the fresh-book
optimizer's allocation gain and makes each change pay for itself. The ablation
shows that carryover and the trade penalty work best together.

What this does not show: the later period is not a clean out-of-sample test,
the breadth check changes rank cutoffs rather than stock identity, skipped
trades have no direct alpha attribution, and returns have not been decomposed
into beta and residual components. Market impact and borrow could also narrow
the estimated net edge.

The next test is a costed benchmark overlay. It isolates beta management from
stock selection and can show whether the remaining risk drift is worth hedging.

## Appendix: implementation details

### The frozen parameters define the comparison

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Component</th><th>Frozen setting</th><th>Role</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Fresh selection</th><td data-label="Frozen setting">75 long + 75 short</td><td data-label="Role">Defines the stocks that may enter the reference portfolio.</td></tr>
    <tr><th scope="row">Signal-weighted rule</th><td data-label="Frozen setting"><span><i>γ</i> = 2; 60-day volatility; 20% target and fallback; 5% floor; 10% signal-share cap; 4% name cap; 6× multiplier cap; 100% gross per book</span></td><td data-label="Role">Maps each score and stock volatility into a standalone weight.</td></tr>
    <tr><th scope="row">Covariance</th><td data-label="Frozen setting"><span>21-day volatility; 756-day correlation; 252-day start; 0.50 missing-pair fallback; <i>ρ</i> = 0.50; calibration 1.18; daily returns capped at ±30%</span></td><td data-label="Role">Combines faster volatility with slower, repaired, and shrunk correlation estimates.</td></tr>
    <tr><th scope="row">Portfolio limits</th><td data-label="Frozen setting">7% volatility; 200% gross; 4% per name; ±25% net; ±0.05 beta</td><td data-label="Role">Constrains total risk, concentration, direction, and forecast market exposure.</td></tr>
    <tr><th scope="row">Beta estimate</th><td data-label="Frozen setting">756-day correlation; 252-day minimum; 21-day volatility; stock beta capped at ±4</td><td data-label="Role">Supplies the point-in-time beta used by the portfolio constraint.</td></tr>
    <tr><th scope="row">Sector limits</th><td data-label="Frozen setting">±20% net; 30% of either book</td><td data-label="Role">Controls net sector bets and one-sided concentration.</td></tr>
    <tr><th scope="row">Transition rule</th><td data-label="Frozen setting">2.5 bp trade penalty; existing holdings may remain to rank 175</td><td data-label="Role">Makes a replacement improve the objective enough to justify changing the portfolio.</td></tr>
    <tr><th scope="row">Realized trading cost</th><td data-label="Frozen setting">5 bp per dollar bought or sold</td><td data-label="Role">Converts executed turnover into net return.</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A1:</strong> Rule-specific parameters for the reference comparison. The trade penalty enters the objective; the realized trading cost enters portfolio P&L.</p>

### Returns and turnover are calculated within each schedule

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
-0.0005\lVert\Delta w_t\rVert_1$$. Annualized two-way turnover is
$$Y^{-1}\sum_t\lVert\Delta w_t\rVert_1$$, where $$Y$$ is elapsed calendar
years. A turnover value of 42.08× therefore means that purchases plus sales
total 42.08 times portfolio capital per year.

The interval between executions averages 13.46 trading days. Results through
2021 form the development period.

January 2022 through May 2026 is a later evaluation period that was separated
in advance. Subsequent research used knowledge of it, so it is informative
rather than a clean out-of-sample test.

The P&L engine carries a missing adjusted price forward until the position
closes. It does not append a separate delisting-return series.

### Signal weighting sizes each stock separately

Let \(s_{i,t}\) be stock \(i\)'s Ridge score, \(\mathcal I_{\ell,t}\) the
stocks in book \(\ell\), and \(z_{i,t}\) the score's cross-sectional z-score
within that book. Set \(d_\ell=+1\) for long and \(d_\ell=-1\) for short. The
normalized signal share is

$$
p_{i,t}
=
\frac{\Lambda(\gamma d_\ell z_{i,t})}
{\sum_{j\in\mathcal I_{\ell,t}}\Lambda(\gamma d_\ell z_{j,t})},
$$

where \(\Lambda(x)=(1+e^{-x})^{-1}\). The inverse-volatility multiplier is

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

The rule scales a book down only when its provisional gross exposure exceeds
the ceiling:

$$
w^{\mathrm{B1}}_{i,t}=\eta_{\ell,t}\widetilde{w}_{i,t},
\qquad
\eta_{\ell,t}
=
\min\!\left\{
1,
\frac{G_\ell}
{\sum_{j\in\mathcal I_{\ell,t}}|\widetilde{w}_{j,t}|}
\right\}.
$$

Table A1 gives the volatility window, missing-value rule, floors, and weight
caps used in this mapping.

### Covariance combines fast volatility with slow correlation

The Ridge output is a Sharpe-like score rather than a return forecast. I put it
in daily return units using recent volatility:

$$
\mu_{i,t}=s_{i,t}\widehat{\sigma}_{i,t}^{(h_\sigma)}.
$$

The result remains a return-unit score, not a calibrated expected return. I
estimate volatility faster than correlation, following Open Source Quant's
[covariance construction](https://osquant.com/papers/a-quants-guide-to-covariance-matrix-estimation/).
Table A1 gives the windows and safeguards.

For the correlation estimate,

$$
x_{i,\tau}
=\frac{r_{i,\tau}}
{\widehat{\sigma}_{i,\tau}^{(h_\sigma)}},
\qquad
\widehat{R}_{ij,t}
=\operatorname{Corr}_{\tau\in\mathcal T_{ij,t}}
\!\left(x_{i,\tau},x_{j,\tau}\right),
$$

where \(\mathcal T_{ij,t}\) contains the dates on which both standardized
returns are finite. The estimator starts after 252 days. A pair needs two
common finite observations and positive sample variance. A missing pair gets
the inherited fallback correlation \(r_{\mathrm{fill}}=0.50\). This need not
be conservative for a long–short portfolio.

Pairwise estimates may not form a valid correlation matrix. I symmetrize the
filled matrix, set its negative eigenvalues to zero, and rescale it to restore a
unit diagonal. If the resulting matrix is \(\widetilde R_t\), shrinkage gives

$$
C_t(\rho)=(1-\rho)\widetilde R_t+\rho I,
\qquad 0\leq\rho\leq1.
$$

With diagonal daily volatility matrix \(D_t\), annualization factor \(A\), and
frozen calibration correction \(\kappa\), the risk model is

$$
\Sigma_t=A\kappa^2D_tC_t(\rho)D_t.
$$

The calibration correction enters as \(\kappa^2\) because it rescales the
portfolio-volatility forecast. It was frozen before the performance checks in
this article.

### The fresh-book optimizer constrains joint risk

The beta estimate combines a long-window stock–market correlation with a
short-window volatility ratio:

$$
\widehat{\beta}_{i,t}
=
\widehat{\operatorname{Corr}}^{(\beta)}_{i,m,t}
\frac{\widehat{\sigma}^{(\beta)}_{i,t}}
{\widehat{\sigma}^{(\beta)}_{m,t}}.
$$

Table A1 gives the beta windows, observation minimum, and cap. I use zero when
beta cannot be estimated.

Let \(L_t\) and \(S_t\) be the long and short candidate sets. With risk budget
\(\sigma_\star\), gross limit \(G_{\max}\), name limit \(w_{\max}\), net
bounds \(n_{\min},n_{\max}\), and beta limit \(b_{\max}\), the fresh-book
optimizer solves

$$
\begin{aligned}
\max_{w_t}\quad & \mu_t^\top w_t \\
\text{subject to}\quad
& w_t^\top\Sigma_t w_t\leq \sigma_\star^2, \\
& \lVert w_t\rVert_1\leq G_{\max},\qquad
  |w_{i,t}|\leq w_{\max}\quad\forall i, \\
& n_{\min}\leq\mathbf{1}^\top w_t\leq n_{\max}, \\
& w_{i,t}\geq0\quad\forall i\in L_t,\qquad
  w_{i,t}\leq0\quad\forall i\in S_t, \\
& -b_{\max}\leq\beta_t^\top w_t\leq b_{\max}.
\end{aligned}
$$

For sector indicator vector \(g_{k,t}\), sector-net limit
\(q_{\mathrm{net}}\), and sector-book share \(q_{\mathrm{leg}}\), it also
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

The volatility budget is a forecast, not a promise about realized risk. The
sector-net constraint controls direction; the separate sector-book constraint
stops one sector from dominating either side. There is no required gross target,
so the score objective expands the portfolio only until a risk or exposure
limit binds.

### Transition awareness penalizes changes to drifted holdings

Let \(F_t^{(N)}\) be the fresh top-\(N\) and bottom-\(N\) candidates,
\(H_t^{\mathrm{pre}}\) the drifted holdings before rebalancing, and
\(T_t^{(K)}\) the current top-\(K\) and bottom-\(K\) ranks. The transition-aware
optimizer may hold

$$
E_t=F_t^{(N)}\cup\left(H_t^{\mathrm{pre}}\cap T_t^{(K)}\right).
$$

A new stock enters only through the fresh selection. An existing stock may
remain while it stays inside the wider rank tails, but it stays on its current
side. A move from long to short, or short to long, requires re-entry through the
fresh selection.

If \(w_{t,E_t}^{\mathrm{pre}}\) is the price-drifted portfolio before the
rebalance, restricted to \(E_t\), the optimizer solves

$$
\max_{w_t\in\mathbb R^{|E_t|}}\quad
\mu_{t,E_t}^\top w_t
-c\lVert w_t-w_{t,E_t}^{\mathrm{pre}}\rVert_1,
$$

subject to the fresh-book optimizer's constraints. The coefficient \(c\) is
the trade penalty in the objective. It is distinct from the realized trading
cost charged by the backtest. The first build has no old holdings, and an
ineligible stock must still be sold.

### Supporting diagnostics preserve the exact comparisons

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Portfolio rule</th><th>Net return through 2021</th><th>Net return from 2022</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">B1 · Signal-weighted</th><td data-label="Net return through 2021">8.92%</td><td data-label="Net return from 2022">7.38%</td></tr>
    <tr><th scope="row">B2 · Fresh-book optimizer</th><td data-label="Net return through 2021">11.60%</td><td data-label="Net return from 2022">6.47%</td></tr>
    <tr><th scope="row">B3 · Transition-aware optimizer</th><td data-label="Net return through 2021">12.32%</td><td data-label="Net return from 2022">7.99%</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A2:</strong> Annualized net return in the development and later periods, averaged across the three schedules.</p>

Compare each row across the two period columns. Every rule weakens, while the
transition-aware rule keeps the highest mean return. The main text explains why
the later gap does not clear schedule dispersion.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Shrinkage</th><th>Net return</th><th>Net Sharpe</th><th>Realized / forecast volatility</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">0.40 · lowest risk error</th><td data-label="Net return">11.59%</td><td data-label="Net Sharpe">1.33</td><td data-label="Realized / forecast volatility">1.191</td></tr>
    <tr><th scope="row">0.50 · implemented</th><td data-label="Net return">11.62%</td><td data-label="Net Sharpe">1.33</td><td data-label="Realized / forecast volatility">1.198</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A3:</strong> The transition-aware optimizer at the nearby and implemented covariance-shrinkage settings.</p>

The first row minimizes the risk error; the second is the frozen choice. Return
and Sharpe are effectively unchanged, which is why I do not retune the model.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Risk diagnostic</th><th>Fresh-book optimizer</th><th>Transition-aware optimizer</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Persistent beta episodes</th><td data-label="Fresh-book optimizer">4</td><td data-label="Transition-aware optimizer">5</td></tr>
    <tr><th scope="row">Days in those episodes</th><td data-label="Fresh-book optimizer">600</td><td data-label="Transition-aware optimizer">339</td></tr>
    <tr><th scope="row">Peak absolute beta</th><td data-label="Fresh-book optimizer">0.309</td><td data-label="Transition-aware optimizer">0.251</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A4:</strong> Episodes with absolute trailing one-year beta above 0.20 for at least 63 trading days. The cutoff summarizes Figure 4; the optimizer does not use it.</p>

The transition-aware rule has one more episode, but fewer days in breach and a
lower peak. This table summarizes persistence; it does not explain the source
of the exposure.

For the transition-aware portfolio, mean realized volatility is about 15%
above forecast. The root-mean-square ratio is about 1.2.

Since 2022, monthly absolute beta averages about 0.04 and peaks near 0.08.

The rejected beta candidate changes both estimation windows to 63 days and
uses a 42-observation minimum.

Its later net return falls by 0.60 percentage
points and Sharpe by 0.05, while turnover is almost unchanged.
