---
layout: post
title: "From Volatility Scaling to a Constrained Optimizer"
date: 2026-08-29
last_modified_at: 2026-09-02
categories: ["Portfolio construction"]
article_label: Portfolio construction · Ridge allocation
permalink: /quants/2026/08/29/portfolio-optimization.html
---

<p class="article-summary">Volatility scaling sizes stocks one at a time and leaves market, sector, and net exposure uncontrolled. A constrained mean-variance optimizer sizes the book jointly under explicit limits. Gross return rises from 10.3% to 13.1%, and Sharpe from 1.05 to 1.24, although realized volatility and drawdown do not improve. The price is dependence on covariance estimates and turnover that rises from 30× to 42×. Accounting for current holdings cuts turnover to 28×, raises Sharpe to 1.33, and lowers maximum drawdown to 18.1%. Realized beta remains the main open problem.</p>

The [low-volatility study](/quant/2024/12/15/low-volatility-factor.html) showed
that inverse-volatility sizing improves balance between the long and short books,
but leaves gross, net, beta, and shared risk uncontrolled. The
[Ridge study](/quants/2025/02/09/multiple-linear-regression.html) then showed that
learned rankings roughly double turnover and ended with two tasks: size stocks
jointly and charge proposed changes against the current book.

This article does both. It uses three staggered schedules[^schedules] from the
[tranching study](/quants/2025/05/10/rebalancing-luck.html), so the result does
not rest on one arbitrary starting week.

Table 1 gives the full-period comparison. The vol-scaled rule sizes each stock
separately. The optimizer sizes the selected stocks jointly but starts over at
each rebalance.[^fresh-book] The optimizer with memory starts from the current
holdings and charges for changing them.[^transition-aware]

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Net Sharpe</th><th>Max DD</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">B1 · Vol-scaled rule</th><td data-label="Gross return">10.31%</td><td data-label="Net return">8.67%</td><td data-label="Net volatility">8.24%</td><td data-label="Net Sharpe">1.05</td><td data-label="Max drawdown">19.63%</td><td data-label="Turnover">29.94×</td></tr>
    <tr><th scope="row">B2 · Optimizer</th><td data-label="Gross return">13.13%</td><td data-label="Net return">10.77%</td><td data-label="Net volatility">8.57%</td><td data-label="Net Sharpe">1.24</td><td data-label="Max drawdown">19.77%</td><td data-label="Turnover">42.08×</td></tr>
    <tr><th scope="row"><strong>B3 · Optimizer with memory</strong></th><td data-label="Gross return"><strong>13.17%</strong></td><td data-label="Net return"><strong>11.62%</strong></td><td data-label="Net volatility"><strong>8.55%</strong></td><td data-label="Net Sharpe"><strong>1.33</strong></td><td data-label="Max drawdown"><strong>18.06%</strong></td><td data-label="Turnover"><strong>27.61×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Return, realized risk, and trading, September 1998–May 2026. Metrics are means of three full-capital rebalance schedules. Returns and volatility are annualized; net results charge 5 basis points for every dollar bought or sold. Turnover is annualized purchases plus sales.</p>

The optimizer adds about three percentage points of gross return and
lifts net Sharpe from 1.05 to 1.24. That is a performance gain, not a
realized-risk gain: volatility is a third of a point higher and drawdown remains
about 20%.

Giving the optimizer memory keeps the gross return, cuts trading below the
volatility-scaled rule, and lowers drawdown. Its schedule-level Sharpe gain over
the optimizer ranges from 0.05 to 0.16; Table 3 tests the mechanism.

## What stays the same in every test

The data, ranking, schedules, execution, and costs stay the same. Only the rule
that turns a Ridge score into portfolio weights changes. I fixed every parameter
before running these tests.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Component</th><th>Shared setting</th><th>Why it stays the same</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Investable sample</th><td data-label="Shared setting">22 September 1998–27 May 2026</td><td data-label="Why it stays the same">Uses the same point-in-time universe and warm-up for every rule.</td></tr>
    <tr><th scope="row">Ranking</th><td data-label="Shared setting">Walk-forward Ridge; 144 predictors</td><td data-label="Why it stays the same">Gives every rule the same stocks and scores.</td></tr>
    <tr><th scope="row">Fresh selection</th><td data-label="Shared setting">75 long + 75 short</td><td data-label="Why it stays the same">Defines the reference portfolio.</td></tr>
    <tr><th scope="row">Rebalancing</th><td data-label="Shared setting">Three staggered schedules; every three weeks</td><td data-label="Why it stays the same">Separates the allocation result from one lucky start date.</td></tr>
    <tr><th scope="row">Execution</th><td data-label="Shared setting">Signal at one close; trade at the next close</td><td data-label="Why it stays the same">Prevents same-close look-ahead.</td></tr>
    <tr><th scope="row">Realized trading cost</th><td data-label="Shared setting">5 bp per dollar bought or sold</td><td data-label="Why it stays the same">Turns executed trades into the net result.</td></tr>
    <tr><th scope="row">Evaluation</th><td data-label="Shared setting">Development through 2021; later period from 2022</td><td data-label="Why it stays the same">Shows whether the result continued after the development window.</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Inputs, sample, timing, and evaluation held fixed across all three portfolio rules. Table A1 gives the rule-specific parameters.</p>

Sharpe uses a zero risk-free rate. Turnover is annualized two-way weight change,
so 42× means purchases plus sales of 42 times capital per year.

## 1. Volatility scaling cannot see shared risk

Why not keep the simpler rule? The volatility-scaled rule maps the ranking into
weights in four steps: rank,
logistic weight, inverse-volatility scaling, and caps. It sizes the long and
short books separately and caps each at 100% gross. The rule is transparent,
and each stock's own volatility affects its weight.

The rule never sees covariance. It cannot tell when several modest positions
carry the same market or sector risk, and it has no portfolio-level volatility,
beta, sector, or net-exposure constraint. Those exposures are whatever the
separate stock weights produce. This is the unresolved problem left by the
[low-volatility study](/quant/2024/12/15/low-volatility-factor.html).

## 2. Constraints turn portfolio intentions into one allocation problem

So how does the optimizer express the controls the vol-scaled rule is missing?
It starts from the same ranking but sizes every selected
stock jointly. Because the Ridge output is a risk-adjusted score rather than a
return forecast, I put it in daily return units using recent volatility:

$$
\mu_{i,t}=s_{i,t}\widehat{\sigma}_{i,t}.
$$

The optimizer then chooses the weight vector $$w_t$$ against covariance matrix
$$\Sigma_t$$. Let $$L_t$$ and $$S_t$$ be the stocks selected for the long and
short books, and let $$g_{k,t}$$ identify sector $$k$$. The problem is

$$
\begin{aligned}
\max_{w_t}\quad & \mu_t^\top w_t \\
\text{subject to}\quad
& w_t^\top\Sigma_t w_t\leq 0.07^2, \\
& \lVert w_t\rVert_1\leq 2.00,\qquad |w_{i,t}|\leq 0.04, \\
& -0.25\leq\mathbf{1}^\top w_t\leq 0.25, \\
& w_{i,t}\geq0\ \forall i\in L_t,\qquad
  w_{i,t}\leq0\ \forall i\in S_t, \\
& -0.05\leq\beta_t^\top w_t\leq0.05, \\
& -0.20\leq g_{k,t}^\top w_t\leq0.20, \\
& \sum_{i\in L_{k,t}}w_{i,t}
  \leq0.30\sum_{i\in L_t}w_{i,t}, \\
& \sum_{i\in S_{k,t}}|w_{i,t}|
  \leq0.30\sum_{i\in S_t}|w_{i,t}|.
\end{aligned}
$$

Each line states an intention: forecast volatility at most 7%, beta within
±0.05, and net exposure within ±25%. The remaining lines keep gross exposure,
single names, and sector concentration inside their limits. There is no required
gross target, so gross exposure becomes whatever the risk budget and other
constraints permit.

That is the engineering advantage. Adding beta or sector control to the
volatility-scaled rule would require another sizing rule and a way to reconcile
it with the existing caps. Here the risk intentions live in the same problem as
the return-unit score. The price is that the solution inherits every error in
that score and covariance matrix.

The two optimizers record zero portfolio-constraint breaches across
1,447 rebalance dates. Mean gross exposure rises from 136% under volatility
scaling to 176% and 183% for the two optimizers; the risk budget, rather than a
fixed book size, allows that expansion.

Maximum absolute net exposure falls from 66% to the 25% optimizer limit. A
matched sector history for all three rules was not saved, so sector control is
shown by the saved rebalance records rather than a baseline time series.

## 3. Joint sizing improves return, not realized risk by itself

Does explicit risk control also lower realized risk? Not by itself.

Table 1 separates the gain from the claim I cannot make. Moving from the
volatility-scaled rule to the optimizer raises gross and net return,
but realized volatility is slightly higher and drawdown is essentially
unchanged. The improvement is return per unit of realized risk, alongside more
explicit point-in-time risk control.

Because the ranking, stocks, and execution are fixed, the extra gross return
enters after the forecast. I read it as evidence that joint sizing removes some
shared-risk drag that the separate rule carries, including the risk of letting
one side of the book dominate. But the comparison bundles return-unit scaling,
covariance, and constraints. A component test between the two rules would
be needed to assign the gain to one of them.

The optimizer with memory improves the realized-risk evidence as well as the
net result: maximum drawdown falls from about 20% to 18%. That improvement is
useful, but it is not proof that the risk forecast is calibrated.

Figure 1 plots net growth on a logarithmic scale above drawdown. The optimizer
finishes above the volatility-scaled rule, and the optimizer-with-memory
path finishes highest. Its largest separations from the optimizer path open in
2000 and 2021 rather than accumulating smoothly. The vertical line starts the
later period.[^later-period]

<div class="research-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/performance-and-drawdowns" alt="Net growth of one dollar on a logarithmic scale and transparent drawdown areas for the vol-scaled rule, optimizer, and optimizer with memory, with the later period beginning in 2022" version="8" %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Net growth of <span class="mathjax-ignore">$1</span> on a logarithmic scale (top) and drawdown in percent (bottom) for the vol-scaled rule, optimizer, and optimizer with memory after trading costs, September 1998–May 2026. The paths average the three rebalance schedules; the vertical rule marks the start of the later period.</p>

The main drawdowns are similar for the first two rules, while the
optimizer-with-memory path loses less in its worst episode. The plot averages the
three schedule paths; Table 1 reports the mean of metrics calculated inside each
schedule, so their endpoint and drawdown values need not match exactly.

## 4. Better inputs are the cost of a more expressive optimizer

What does the cleaner framework demand in return? Better inputs. An optimizer
takes every number literally, and the covariance matrix is the
input it trusts most. Noisy correlations become positions. An unstable or
overconfident matrix can make a portfolio look diversified while understating
its risk.

Volatility changes faster than correlation, so I estimate stock volatility over
21 sessions and correlation over 756. After repairing the pairwise estimate to
a valid correlation matrix $$\widetilde R_t$$, I shrink it toward identity:

$$
C_t(\rho)=(1-\rho)\widetilde R_t+\rho I,
\qquad 0\leq\rho\leq1.
$$

With diagonal volatility matrix $$D_t$$, annualization factor $$A$$, and a
calibration factor $$\kappa$$ that corrects forecast bias,[^calibration]
the covariance input is

$$
\Sigma_t=A\kappa^2D_tC_t(\rho)D_t.
$$

Figure 2 asks how much the risk forecast and portfolio result depend on
shrinkage. The horizontal axis runs from the raw repaired correlation estimate
to full identity. The panels compare forecast calibration, beta forecast error
over the next holding period, turnover, and net Sharpe for the optimizer with
and without memory.

<div class="research-figure rho-ladder-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/rho-ladder" alt="Risk calibration, beta forecast error, turnover, and mean schedule-level net Sharpe for the optimizer with and without memory across covariance-shrinkage values from zero to one" version="4" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> How the risk forecast and result depend on correlation shrinkage. Panels show realized-to-forecast volatility, beta forecast error over the next holding period, annualized turnover, and net Sharpe for the optimizer with and without memory, September 1998–May 2026. The shaded region marks shrinkage from 0.3 to 0.6.</p>

The useful region is the shaded middle. The curves change little from 0.3 to
0.6, and the implemented value is 0.5. Moving shrinkage from 0.4 to 0.5 changes
net return by 0.03 percentage points; Sharpe is unchanged.

The extremes show why the input needs care. With no shrinkage, realized
volatility is about 1.3 times forecast. Full shrinkage discards useful
correlation and makes the miss roughly 1.7 times. The sensitivity sweep supports
a stable middle, not one exact shrinkage value.

The constraints are guardrails against the remaining estimation error. They
stop the optimizer from turning one noisy input into an unbounded name, sector,
beta, or gross position. They do not make the inputs correct: realized
volatility still averages about 15% above forecast, and Section 8 shows that the
beta estimate misses persistent exposure.

That volatility miss looks like a configuration problem, not a failure of the
framework. The model is systematically underpredicting risk, so I can adjust
$$\kappa$$ until forecast and realized volatility line up better. I would then
rerun the comparison because the change also affects weights, feasibility,
turnover, and returns.

## 5. The optimizer trades more because it has no memory

So where does the extra turnover come from? The return gain comes with a trading
problem. Annualized purchases plus sales
rise from about 30 times capital under volatility scaling to 42 times under the
optimizer. At each rebalance, it solves only over the new selection;
an existing holding receives no credit for already being in the book.

Small changes in scores or covariance can therefore replace a stock even when
the proposed substitute adds little at the portfolio level. Can the optimizer
keep the allocation gain if every change has to pay for itself?

## 6. The current book turns marginal replacements into a decision

What happens to a stock the optimizer already owns? Suppose a current long falls
from rank 60 to rank 110. An optimizer that starts over must replace it because
it is outside the fresh 75. The optimizer with memory may keep it because it is
still inside the wider top-175 rank tail.[^carryover]

It now asks whether the proposed replacement improves the score-risk objective
enough to cover the trade. The comparison starts from the price-drifted book:
the previous target weights after market moves and before this rebalance.[^drifted]
If $$w_t^{\mathrm{pre}}$$ is that current book and $$c$$ is the penalty, the
objective becomes

$$
\max_{w_t}\quad
\mu_t^\top w_t-c\lVert w_t-w_t^{\mathrm{pre}}\rVert_1,
$$

subject to the same constraints as the optimizer without memory. In words,
carryover widens the eligible set for existing holdings, while the penalty
charges any move away from the current weights. A new stock still has to enter
through the fresh 75.

The objective uses a 2.5 bp penalty, while realized P&L is charged 5 bp for each
dollar bought or sold. The penalty is a configuration value, not a cost
estimate: it controls how reluctant the optimizer is to trade. The saved
evidence does not record why it was set at half the realized cost.

This distinction matters. The optimizer with memory does not win because its
gross backtest compounds faster. It reaches nearly the same portfolio with
fewer replacements. The cost saving is the gain.

Table 3 removes one piece at a time. The top row uses neither mechanism, the
middle rows add one at a time, and the bottom row combines them.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Variant</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Optimizer · neither mechanism</th><td data-label="Gross return">13.13%</td><td data-label="Net return">10.77%</td><td data-label="Net Sharpe">1.24</td><td data-label="Turnover">42.08×</td></tr>
    <tr><th scope="row">Carryover only · rank 175</th><td data-label="Gross return">13.16%</td><td data-label="Net return">10.96%</td><td data-label="Net Sharpe">1.25</td><td data-label="Turnover">39.00×</td></tr>
    <tr><th scope="row">Trade penalty only · 2.5 bp</th><td data-label="Gross return">13.02%</td><td data-label="Net return">11.07%</td><td data-label="Net Sharpe">1.27</td><td data-label="Turnover">34.83×</td></tr>
    <tr><th scope="row"><strong>Optimizer with memory · both</strong></th><td data-label="Gross return"><strong>13.17%</strong></td><td data-label="Net return"><strong>11.62%</strong></td><td data-label="Net Sharpe"><strong>1.33</strong></td><td data-label="Turnover"><strong>27.61×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 3:</strong> Carryover and trade-penalty mechanism comparison using the reference portfolios. The penalty guides the optimizer; the backtest still charges the same realized cost. The mechanisms interact, so their combined effect is not the sum of the two middle rows.</p>

Carryover alone does almost nothing, which surprised me. It only pays once the
penalty gives the optimizer a reason to use it. Together they cut turnover by
another 7× and raise mean Sharpe by 0.06. That Sharpe increment is
close to the 0.05 schedule spread, so the case for carryover rests more on
trading than on a precisely estimated performance gain.

Gross return barely changes across the four rows. I read this as evidence that
many marginal replacements add little at the portfolio level. It is not a
trade-level alpha test: changes in risk and exposure could offset the returns of
the skipped trades. A matched analysis of replaced versus retained stocks, with
the Ridge score's rank persistence, would separate those explanations.

The mechanisms reinforce each other. Carryover makes acceptable incumbents
eligible; the trade penalty gives the optimizer a reason to keep them. Either
mechanism alone leaves one half of that decision missing, so their combined
turnover reduction is larger than the sum of the two isolated reductions.

Trading does not disappear. Forced exits—sales required because a stock leaves
the eligible universe—still account for 36% of modeled turnover.[^trading]
Target changes sum to 1.59 times capital per rebalance, and the average interval
between executions is 13.46 trading days. The design reduces discretionary
replacements; it does not remove implementation risk.

## 7. The trading gain survives wider portfolios

Does the trading gain depend on choosing exactly 75 stocks? Figure 3 tests
selection breadth from 50 to 150 stocks on each side. Net Sharpe
is in the top row and annualized turnover in the bottom row; columns separate
the development and later periods.

<div class="research-figure deterministic-breadth-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/deterministic-breadth" alt="Grouped bars comparing actual net Sharpe and annualized turnover for the vol-scaled rule, optimizer, and optimizer with memory from 50 to 150 selected names per side before and after 2022" version="7" %}
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Net Sharpe (top) and annualized purchases plus sales (bottom) for the three portfolio rules by selected stocks per side. The left panels end in 2021; the right panels cover January 2022–May 2026. The narrowest optimizer pair uses a looser sector-share cap because one selected tail contains only three sectors.</p>

The optimizer with memory has the highest mean Sharpe at every tested
breadth. During development, its gaps over the optimizer without memory range from
0.05 to 0.08, while schedule spread reaches 0.14. The ordering is stable, but
the differences are small relative to rebalance timing.

Turnover remains below the optimizer without memory throughout. It also falls below
the volatility-scaled rule at the middle breadths, but not at the widest book.
Wider books also change which stocks are selected, so the figure cannot isolate
breadth from stock identity.

The later-period panels are more dispersed. I treat them as the short check in
Section 9, not as a second headline result.

## 8. Realized beta is the main open problem

What still goes wrong after the optimizer satisfies its constraints? Realized
beta. The optimizer enforces a point-in-time beta limit when it chooses weights.
Realized beta can still change as prices and beta estimates move over the
holding period.

Figure 4 plots monthly trailing one-year realized beta for all three rules. The
volatility-scaled rule supplies the baseline; the two optimizer lines show what
joint sizing changes. I omit the optimizer's band because it applies to a
different, point-in-time estimate.

<div class="research-figure risk-beta-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/risk-calibration-and-beta" alt="Trailing 252-day realized market beta for the vol-scaled rule, optimizer, and optimizer with memory, sampled monthly, with a zero reference line" version="8" %}
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Monthly trailing one-year realized market beta for the volatility-scaled rule and both optimizers, averaged across the three schedules, September 1998–May 2026. The point-in-time optimizer constraint uses a different estimate and clock, so its target band is not overlaid.</p>

Look at the long departures from zero rather than one-month peaks. The
optimizers reduce persistent beta relative to volatility scaling, but they do
not remove it. The optimizer without memory has four episodes above 0.20 that
last at least 63 trading days, covering 600 days in total. Its peak absolute
beta is 0.309.

The optimizer with memory has five such episodes covering 339 days. Its peak
absolute beta is 0.251. The chart does not attribute returns to beta.

Constraint compliance is not the problem. The beta limit binds on nearly half
of the optimizer-with-memory rebalance dates. The chosen portfolio remains inside the
limit, and execution drift adds only a few thousandths. This points to the beta
estimate used to choose stocks and weights.

I tested a shorter beta window. It
removes the persistent beta episodes, but later net return falls by 0.60
percentage points. I reject it because that is larger than the 0.50-point loss I
was willing to accept.

That missing attribution matters. Some of the return difference between rules
may come from market exposure rather than stock selection. The saved evidence
has no beta-residual return decomposition, so I do not treat a mean return lead
as proof of stronger selection.

Volatility calibration is more tractable. Realized volatility averages about
15% above the optimizer's forecast, and the covariance model already has
an explicit multiplier for that gap. I treat this as a development-period
configuration update, not as a new source of edge.

Turnover also remains high after the improvement. At roughly 28× purchases plus
sales per year, capacity depends on market impact, borrow, and the stocks at the
edge of the universe. A flat five-basis-point cost is useful for a matched
comparison, but it is not a capacity model.

The cleaner next test is a costed benchmark overlay that leaves the stock
portfolio untouched. It would separate beta management from stock selection.
Tightening the stock constraint first would mix them again.

## 9. The later period is a short check

All three rules weaken in the later period, with annualized net
returns of 7.38%, 6.47%, and 7.99% for the vol-scaled rule, optimizer, and
optimizer with memory. The optimizer trails volatility scaling in this block.
The optimizer-with-memory lead over it remains inside schedule spread,
and five years is not enough to promote this check into the headline result.

## Conclusion

I move from volatility scaling to the constrained optimizer, and I use the
version that accounts for its current book.

Joint sizing improves the allocation and turns exposure intentions into explicit
constraints. That cleaner framework demands more careful covariance estimation,
guardrails that keep bad inputs from becoming extreme positions, and a trading
objective that starts from what the portfolio already owns.

I treat the volatility miss as calibration work: adjust the multiplier until
forecast and realized volatility match better, then rerun the comparison. The
separate research problem is beta, because its point-in-time estimate can
satisfy the constraint while realized exposure still drifts.

What this does not show: the later period is not a clean out-of-sample test,
the breadth check changes rank cutoffs rather than stock identity, skipped
trades have no direct alpha attribution, and returns have not been decomposed
into beta and residual components. Market impact and borrow could also narrow
the estimated net edge.

The next test is a costed benchmark overlay. It isolates beta management from
stock selection and can show whether the remaining risk drift is worth hedging.

## Appendix: parameters and safeguards

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Component</th><th>Setting</th><th>Why</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Fresh selection</th><td data-label="Setting">75 long + 75 short</td><td data-label="Why">Keeps the comparison on the same selected stocks.</td></tr>
    <tr><th scope="row">Vol-scaled rule</th><td data-label="Setting"><span><i>γ</i> = 2; 60-day volatility; 20% target and fallback; 5% floor; 10% signal-share cap; 4% name cap; 6× multiplier cap; 100% gross per book</span></td><td data-label="Why">Preserves the sizing rule from the low-volatility study.</td></tr>
    <tr><th scope="row">Covariance</th><td data-label="Setting"><span>21-day volatility; 756-day correlation; 252-day start; 0.50 missing-pair fallback; <i>ρ</i> = 0.50; <i>κ</i> = 1.18; daily returns capped at ±30%</span></td><td data-label="Why">Lets volatility react faster than correlation while shrinking noisy shared-risk estimates.</td></tr>
    <tr><th scope="row">Portfolio limits</th><td data-label="Setting">7% volatility; 200% gross; 4% per name; ±25% net; ±0.05 beta</td><td data-label="Why">Turns the intended risk and exposure limits into guardrails.</td></tr>
    <tr><th scope="row">Beta estimate</th><td data-label="Setting">756-day correlation; 252-day minimum; 21-day volatility; stock beta capped at ±4</td><td data-label="Why">Combines a stable correlation estimate with faster-moving volatility.</td></tr>
    <tr><th scope="row">Sector limits</th><td data-label="Setting">±20% net; 30% of either book</td><td data-label="Why">Stops one sector from dominating the net portfolio or either book.</td></tr>
    <tr><th scope="row">Memory</th><td data-label="Setting">2.5 bp trade penalty; existing holdings may remain to rank 175</td><td data-label="Why">Makes marginal replacements pay for changing the current book.</td></tr>
    <tr><th scope="row">Realized trading cost</th><td data-label="Setting">5 bp per dollar bought or sold</td><td data-label="Why">Converts executed turnover into net return using the series-wide cost assumption.</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A1:</strong> Rule-specific parameters and the reason each is in the comparison. The trade penalty enters the objective; the realized trading cost enters portfolio P&L.</p>

### The vol-scaled sizing chain

Within each book, the rule turns rank into logistic signal share $$p$$, applies
inverse-volatility multiplier $$\lambda$$, caps the weight, and scales the book
down only when its gross exposure exceeds $$G_\ell$$:

$$
\begin{aligned}
p_{i,t}
&=\frac{\Lambda(\gamma d_\ell z_{i,t})}
{\sum_{j\in\mathcal I_{\ell,t}}\Lambda(\gamma d_\ell z_{j,t})},
&\Lambda(x)&=(1+e^{-x})^{-1},\\
\lambda_{i,t}
&=\min\!\left\{\lambda_{\max},
\frac{\sigma_{\mathrm{target}}}{\widehat\sigma_{i,t}}\right\},\\
\widetilde w_{i,t}
&=d_\ell\min\!\left\{w_{\max},
\min(p_{i,t},p_{\max})\lambda_{i,t}\right\},\\
w_{i,t}
&=\eta_{\ell,t}\widetilde w_{i,t},
&\eta_{\ell,t}&=\min\!\left\{1,
\frac{G_\ell}{\sum_{j\in\mathcal I_{\ell,t}}|\widetilde w_{j,t}|}\right\}.
\end{aligned}
$$

### Covariance safeguards

Daily returns are capped at ±30% before correlation estimation. A missing pair
gets the inherited 0.50 fallback, which is not always conservative in a
long–short portfolio. I symmetrize the pairwise matrix, clip negative
eigenvalues, and restore its unit diagonal before applying the shrinkage shown
in Section 4. The calibration multiplier is $$\kappa=1.18$$, inherited from the
original development configuration; it is the setting to adjust when forecast
and realized volatility do not line up.

[^schedules]: A staggered schedule runs the same rule from a different starting week. Each is a full-capital portfolio, not one slice of a combined portfolio. The [tranching study](/quants/2025/05/10/rebalancing-luck.html) introduced this calendar design.
[^fresh-book]: Starting over means that the optimizer uses the current top and bottom 75 stocks at every rebalance and does not account for existing holdings.
[^transition-aware]: Memory means that the optimizer starts from its price-drifted holdings, keeps eligible incumbents through carryover, and penalizes proposed trades.
[^carryover]: Carryover lets an existing holding remain eligible outside the fresh 75 while it stays in the wider top or bottom 175.
[^drifted]: The price-drifted book is the previous target portfolio after intervening price moves and before the next rebalance.
[^calibration]: The calibration factor $$\kappa$$ rescales the covariance model so forecast portfolio volatility better matches realized volatility.
[^trading]: Modeled turnover is the target-weight change seen by the optimizer. A forced exit is required by loss of eligibility; a discretionary replacement is chosen among otherwise eligible stocks.
[^later-period]: The later period runs from January 2022 through May 2026. Schedule spread is the difference between the best and worst of the three staggered schedules for a metric.
