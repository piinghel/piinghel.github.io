---
layout: post
title: "From Volatility Scaling to a Constrained Optimizer"
date: 2026-08-29
last_modified_at: 2026-09-05
categories: ["Portfolio construction"]
article_label: Portfolio construction · Ridge allocation
permalink: /quants/2026/08/29/portfolio-optimization.html
---

<p class="article-summary">I want the allocation to account for risks shared across stocks and for the positions already held. A constrained optimizer does the first job: it raises development-period Sharpe from 1.12 to 1.35, but trades more. Allowing it to retain acceptable holdings and penalizing replacements cuts turnover by about a third while preserving gross return. That is the version I carry forward. Its advantage is smaller and more sensitive to rebalance dates after 2021, and its risk forecasts still understate realized volatility.</p>

The [low-vol post](/quant/2024/12/15/low-volatility-factor.html) showed that
inverse-volatility sizing balances the long and short books. But the rule still
treats every stock on its own; it cannot see when several positions carry the
same risk. In the
[Ridge post](/quants/2025/02/09/multiple-linear-regression.html), I replaced the
fixed score with a learned ranking. Sharpe improved, but turnover doubled. Here
I keep that ranking fixed and change the allocation: the optimizer sizes stocks
jointly, and the trading controls make it less eager to replace positions that
still rank well.

## Study design and the three rules

The data history begins in 1995. The portfolio comparison starts in September
1998, once the signals and risk estimates have enough history. I use the period
through December 2021 to choose the settings. The later comparison runs from
the first trading day of January 2022 through May 2026, with the first forecast
built from data already available at the end of 2021. This later history has
since informed feature, allocation, and beta-estimator decisions. It is a
pseudo-holdout: chronologically later, but no longer untouched evidence.

Every rule starts from the same Ridge ranking and trades the same three
staggered schedules.[^schedules] A staggered schedule runs the full strategy
from a different starting week. Each schedule rebalances every three weeks,
uses the same next-close execution, and pays 5 basis points for every dollar
bought or sold. This holds the ranking, timing, and cost assumption constant.

The comparison has three rules:

- The **volatility-scaled rule** maps rank to a signal weight, scales each stock
  by its own volatility, and applies caps.
- The **optimizer** takes the same selected stocks and sizes them together under
  portfolio constraints.
- The **optimizer with trading controls** solves the same problem, but it may
  keep existing holdings from a wider rank range and penalizes changes in its
  objective.

The tables average metrics calculated separately for the three schedules.
They do not report the Sharpe of a combined three-sleeve portfolio. Returns are
geometric annualized returns; Sharpe uses arithmetic mean daily return and a
zero risk-free rate. Turnover is executed purchases plus sales divided by
strategy capital, annualized over the reporting window.

There is also a change from the preceding regression article: this baseline
uses score-dependent weights before volatility scaling, whereas that article
uses equal signal weights within each selected book. I compare allocators
within the present study; the baseline performance levels across the two posts
are not interchangeable.

## Joint sizing raises development returns at similar realized risk

The volatility-scaled rule is easy to inspect. But it sizes the long and short
books separately and never sees covariance. Several modest positions can
therefore carry the same market or sector risk without the rule recognizing the
overlap.

The optimizer starts from the same ranking and sizes all selected stocks at
once. That score orders stocks rather than forecasting expected returns. Its
training target divides forward return by volatility, so I map the score into
return units using each stock's volatility:

$$
\mu_{i,t}=s_{i,t}\widehat{\sigma}_{i,t}.
$$

Here $$s_{i,t}$$ is the Ridge score and $$\widehat\sigma_{i,t}$$ is the daily
stock-volatility estimate supplied to the objective. Their product is a daily
return proxy for sizing. Ranking the
training target discarded its magnitude, so this multiplication does not
recover a calibrated expected return. I use it as a relative allocation score;
its scale also determines the strength of the trading penalty introduced below.

The optimizer then chooses weights to maximize the portfolio score:

$$
\begin{aligned}
\max_{w_t}\quad & \mu_t^\top w_t \\
\text{subject to}\quad
& w_t^\top\Sigma_t w_t\leq\sigma_*^2,\\
& \lVert w_t\rVert_1\leq G,\quad
  |\mathbf 1^\top w_t|\leq N,\\
& |w_{i,t}|\leq M,\\
& w_{i,t}\geq0\ \text{for longs},\quad
  w_{i,t}\leq0\ \text{for shorts},\\
& |\beta_t^\top w_t|\leq B,\\
& |\mathbf 1_s^\top w_t|\leq S_s
  \quad\text{for each sector }s.
\end{aligned}
$$

The first constraint says that forecast portfolio variance must fit inside the
risk budget $$\sigma_*^2$$. The symbols $$G$$, $$N$$, $$M$$, $$B$$, and $$S_s$$
are the gross, net, name, beta, and sector-net limits. The implementation also
caps each sector at 30% of either book's gross exposure. These constraints let
me state the exposures I am prepared to hold in one allocation problem. Gross
exposure becomes an outcome within its ceiling. Table A1 collects the limits.

Table 1 reports the development-period result. The optimizer raises gross
return by about three and a half percentage points and net Sharpe from 1.12 to
1.35. Realized volatility is about half a point higher and maximum drawdown is
unchanged. The 7% forecast target sets the amount of risk the optimizer may
use. Within that budget, it chooses more gross exposure and ends with similar
realized risk.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Net Sharpe</th><th>Max DD</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">B1 · Vol-scaled rule</th><td>10.58%</td><td>8.92%</td><td>7.92%</td><td>1.12</td><td>19.63%</td><td>30.27×</td></tr>
    <tr><th scope="row">B2 · Optimizer</th><td>14.00%</td><td>11.60%</td><td>8.41%</td><td>1.35</td><td>19.77%</td><td>42.52×</td></tr>
    <tr><th scope="row"><strong>B3 · Optimizer + trading controls</strong></th><td><strong>13.91%</strong></td><td><strong>12.32%</strong></td><td><strong>8.40%</strong></td><td><strong>1.43</strong></td><td><strong>18.06%</strong></td><td><strong>28.19×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> September 1998–December 2021, means of three schedule-level metrics. Returns are geometric and annualized; volatility is annualized. Net results charge 5 bp per dollar bought or sold. Drawdowns are reported as positive loss magnitudes.</p>

The comparison changes the whole allocation rule. Covariance, return-unit
scaling, and the constraints all move together. I read the result as evidence
that joint sizing uses the ranking better than separate stock-by-stock sizing.
A component-by-component comparison would isolate the source.

Figure 1 gives the path behind the averages. The optimizer finishes above the
volatility-scaled rule. Adding the trading controls finishes highest and loses
less in its worst drawdown. Its lead opens mainly around 2000 and 2021 rather
than building at a steady rate.

<div class="research-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/performance-and-drawdowns" alt="Development-period net growth and drawdowns for the volatility-scaled rule, optimizer, and optimizer with trading controls" version="12" %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Net growth of <span class="mathjax-ignore">$1</span> on a logarithmic scale (top) and drawdown in percent (bottom) after trading costs, September 1998–December 2021. Each path averages three separately compounded staggered schedules.</p>

## The optimizer is only as good as its covariance matrix

The optimizer takes its covariance estimate literally. Noisy correlations can
become concentrated positions or an overconfident risk forecast. I let stock
volatility react on a shorter window than correlation, repair the pairwise
correlation estimate, and shrink it toward a matrix with zero correlations:

$$
C_t(\rho)=(1-\rho)\widetilde R_t+\rho I.
$$

In [*Enhanced Portfolio Optimization*](https://doi.org/10.1080/0015198X.2020.1854543),
Pedersen, Babu, and Levine (2021) show why this helps: noise can make some
combinations of stocks look safer than they are, so mean-variance optimization
gives them too much weight. Shrinking correlations toward zero keeps useful
shared-risk information without trusting every estimated relationship equally.

The shrunk correlation matrix becomes a covariance matrix through

$$
\Sigma_t=\kappa^2D_tC_t(\rho)D_t,
$$

Here $$\widetilde R_t$$ is the repaired correlation estimate, $$I$$ is the
identity matrix, and $$D_t$$ contains annualized stock-volatility estimates,
so $$\Sigma_t$$ and the risk budget use annual units. The
multiplier $$\kappa$$ scales their level. I retain the existing value of 1.18
from the predecessor allocator; it was not freshly fitted to this comparison.
Volatility uses 21 days and correlation 756 days, so the model can respond to a
change in risk level without re-estimating every stock relationship on a short
window.

The middle of Figure 2 is the useful region. From 0.3 to 0.6 shrinkage, forecast
calibration, beta error, turnover, and Sharpe move little. With no shrinkage,
realized volatility runs above forecast. Full shrinkage throws away too much
shared-risk information and misses by more. The broad middle matters more than
the exact point inside it.

The calibration panel takes the square root of mean realized holding-period
variance divided by mean forecast variance; one would indicate agreement in
level. It is not an average of individual realized-to-forecast volatility ratios.

<div class="research-figure rho-ladder-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/rho-ladder" alt="Development-period risk calibration, beta error, turnover, and net Sharpe across correlation-shrinkage values for both optimizers" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> The horizontal axis in every panel is correlation shrinkage, from zero to one. The panels show development-period forecast calibration, beta error over the next holding period, annualized turnover, and net Sharpe. The shaded band marks 0.3 to 0.6; lines compare the optimizer with and without trading controls.</p>

The portfolio limits reduce how far the optimizer can exploit an apparently
attractive but poorly estimated combination. They complement shrinkage: one
restrains the positions, the other restrains the estimated relationships used
to choose them.

At the implemented shrinkage, root-mean realized volatility is about 21% above
forecast for the optimizer and 18% above for the version with trading controls.
The existing multiplier therefore needs another calibration
check on development data. That would be a model change: changing covariance
alters the weights, constraints that bind, turnover, and realized risk. I would
rerun the matched portfolios rather than multiply the reported volatility by a
correction after the fact.

## Making the optimizer pay for each trade

The fresh optimizer receives the newly selected stocks at every rebalance,
without a preference for retaining a position already held. A small change in
rank or covariance can then trigger a replacement whose benefit is smaller
than its trading cost. I want the allocation decision to include that cost of
changing direction.

Take a long stock whose rank slips from 60 to 110. The optimizer drops it
because only the top 75 enter the new selection. The optimizer with trading
controls may retain it while it remains inside the wider top 175. It starts from
the existing weights after intervening price moves.

If $$w_t^{\mathrm{pre}}$$ contains the weights just before rebalancing and
$$c$$ is the trade coefficient, the objective becomes

$$
\max_{w_t}\quad
\mu_t^\top w_t-c\lVert w_t-w_t^{\mathrm{pre}}\rVert_1,
$$

under the same portfolio constraints. The wider holding range gives the
optimizer more incumbents to choose from. The second term makes every change
pay for moving away from the current weights. The trade coefficient controls
that reluctance.

The L1 term counts both sides of a replacement. Selling a 1% position and buying
another 1% position changes $$\lVert w_t-w_t^{\mathrm{pre}}\rVert_1$$ by 2%.
The optimizer keeps the incumbent unless the new score-and-risk combination
clears that hurdle. Constraints can still force a trade when the old position
no longer fits. The coefficient is a tuning parameter inside the score
objective, distinct from the 5 bp fee charged to realized trades. A holding
that leaves the wider eligible set must also be closed; those forced exits
enter executed turnover even though the optimizer cannot choose to avoid them.

Figure 3 checks both choices on the development period. The left column varies
the trade coefficient while holding the rank cutoff at 175. The right varies
the cutoff while holding $$c=2.5\times10^{-4}$$. The coefficient axis is in
units of $$10^{-4}$$, so the plotted value 2.5 denotes that setting. Points are the mean of the
three schedules and vertical lines show their range.

<div class="research-figure parameter-sensitivity-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/parameter-sensitivity" alt="Development-period net Sharpe and annualized turnover for six trade coefficients and five holding-rank cutoffs" version="6" %}
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Local development-period sensitivity of net Sharpe (top) and annualized turnover (bottom). The selected settings are highlighted. Each column changes one setting and holds the other at its selected value; vertical bars span the three staggered schedules.</p>

Moving from 0 to 1 on the coefficient axis raises net
Sharpe from 1.37 to 1.43 and cuts turnover from about 40× to 34×. Most of the
gain from discouraging marginal trades arrives early.

From 1 through 3, net Sharpe stays between 1.42 and 1.43 while turnover keeps
falling, from 34× to 27×. The data therefore identify a broad trade-off rather
than one best coefficient. I use 2.5 because it sits toward the lower-turnover
end of that plateau; pushing to 5 gives back some return.

The rank cutoff is also locally stable. Moving from 150 to 175 raises Sharpe
from 1.41 to 1.43 and lowers turnover by about one turn. Moving on to 200 saves
less than another turn, leaves Sharpe at 1.42, and raises mean maximum drawdown
from 18.1% to 19.2%. I use 175 as a practical balance. The figure supports a
broad region of reasonable choices around it.

The two mechanisms reinforce each other. Widening the holding set on its own
cuts turnover from 43× to 40×. The trade term on its own brings it to 35×. Used
together, they reach 28×. That interaction surprised me: the wider set matters
most once the objective gives the optimizer a reason to keep an acceptable
holding.

Gross return barely changes between B2 and B3 during development, while fewer
replacements leave more of it after costs. Similar aggregate returns do not
imply similar holdings: the wider retention set also changes which stocks can
remain. I read the result as evidence that many marginal replacements add
little at the portfolio level under this signal and cost assumption.

The cost arithmetic needs a separate convention from the return table. A
5 bp charge on 28.2 times annual turnover costs about 1.41% of strategy capital
per year on an arithmetic basis. The gap between gross and net geometric
returns also reflects compounding, so it need not equal that simple product.

## Estimated beta limits do not guarantee realized beta control

The optimizer keeps its beta estimate inside the stated range at each
rebalance. Realized beta can still drift as prices and exposures change over
the holding period. Figure 4 shows that this happens in persistent episodes.

<div class="research-figure risk-beta-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/risk-calibration-and-beta" alt="Development-period trailing realized beta for the volatility-scaled rule and both optimizers" version="12" %}
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Month-end trailing one-year realized market beta for all three rules, averaged across the staggered schedules, September 1999–December 2021 after the return-window warm-up. The constraint uses a point-in-time estimate at each rebalance, while this chart measures the portfolio outcome over a trailing year.</p>

The optimizer reduces the long departures from zero relative to volatility
scaling, but several episodes still last for months and reach roughly 0.2.
A trailing one-year estimate remembers earlier holdings and market moves, so
it is not a direct test of today's constrained portfolio. The saved
holding-period diagnostics also show estimation error beyond ordinary
execution and weight drift. Both the measurement window and the stock-beta
estimate matter.

I tested a 63-day beta window in matched portfolios. It removes the flagged
persistent episodes, but B3 fails the later tail-error check and loses 0.6
percentage points of annualized net return, beyond the 0.5-point tolerance.
I therefore keep the existing estimate. That rejection also means the later
period has participated in model selection; it cannot serve as a fresh
validation of the surviving rule.

## The advantage narrows after 2021

Table 2 starts on the first trading day of 2022. All three rules weaken relative
to their development results. The optimizer trails volatility scaling after
trading more. The trading controls change the result: net return is 8.0% versus
7.4%, Sharpe is 0.87 versus 0.78, and turnover falls below the baseline.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Net Sharpe</th><th>Max DD</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">B1 · Vol-scaled rule</th><td>8.92%</td><td>7.38%</td><td>9.73%</td><td>0.78</td><td>8.65%</td><td>28.35×</td></tr>
    <tr><th scope="row">B2 · Optimizer</th><td>8.63%</td><td>6.47%</td><td>9.39%</td><td>0.71</td><td>9.41%</td><td>39.97×</td></tr>
    <tr><th scope="row"><strong>B3 · Optimizer + trading controls</strong></th><td><strong>9.33%</strong></td><td><strong>7.99%</strong></td><td><strong>9.32%</strong></td><td><strong>0.87</strong></td><td><strong>9.05%</strong></td><td><strong>24.62×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> January 2022–May 2026, a later period revisited during research. Schedule averaging, geometric-return, drawdown, and cost conventions match Table 1.</p>

That average needs one qualification. The optimizer with trading controls has a
4.5-point spread in net return across the three schedules, compared with 1.5
points for the volatility-scaled rule. Two schedules favor the optimizer and
one is much weaker. The shorter later period therefore supports the value of
trading more slowly, but with less confidence than the longer development
result.

Could market exposure explain the weaker result? Only partly. The optimizer
with trading controls has beta of 0.01 over the evaluation period. Its beta is
mildly negative in 2022 and 2023, then turns positive. In the first five months
of 2026, the portfolio loses money with beta around 0.22. The positive beta
has a positive fitted market component during that episode, but the remaining
return is still negative. This is an ex-post regression decomposition; its
residual is not evidence of stock-selection alpha.

Beta does fall around the largest drawdown. Across the three schedules, trailing
63-day beta ranges from −0.02 to +0.02 at the December 2022 peak. By the February
2023 trough it ranges from −0.10 to −0.02. The beta estimate used by the
optimizer also turns negative and reaches its −0.05 limit in every schedule.

The drop is real, but it explains little of the loss. The schedule with beta of
−0.08 loses 9.2%; its fitted market component is about −0.9 percentage points.
Another schedule loses 9.1% over the same dates with positive beta. Averaged
across schedules over 29 December 2022–2 February 2023, the long book adds
7.2 points while the short book costs 16.4. These are sums of daily after-cost
book contributions, not contributions linked to the compounded drawdown.

The short book also drove the difficult episodes in the [low-vol
post](/quant/2024/12/15/low-volatility-factor.html), but that shared sign does
not establish a common style exposure. Here the market-only decomposition
leaves most of the loss unexplained. Sector, style, and stock contributions are
needed to understand what the short book was exposed to.

## The allocator I carry forward

I carry the constrained optimizer with trading controls into the next research
stage. It lets me express portfolio limits jointly and earns nearly the same
development gross return as the fresh optimizer with fewer trades. The weaker,
less consistent later results keep me from treating that choice as settled.

Before adding another constraint, I want to know where the risk and P&L sit.
The drawdown evidence identifies the short book, but does not distinguish a
shared style exposure from stock-specific losses. That attribution comes
before a new style limit or a market hedge. Matched counterfactual portfolios
would then be needed to decide whether the ranking, retention rule, or a
constraint caused the exposure.

Risk recalibration remains a concrete implementation test. Borrow,
financing, liquidity, and market impact also remain outside the flat trading
charge. They would have to enter the portfolio replay before using these
results to judge capacity.

## Appendix: parameters and two implementation notes

<table class="research-table settings-table">
  <thead>
    <tr><th>Component</th><th>Setting</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Initial selection</th><td>75 long + 75 short</td></tr>
    <tr><th scope="row">Vol-scaled rule</th><td><span><i>γ</i> = 2; 60-day volatility; 20% target and fallback; 5% floor; 10% signal-share cap; 4% name cap; 6× multiplier cap; 100% gross per book</span></td></tr>
    <tr><th scope="row">Covariance</th><td><span>21-day volatility; 756-day correlation; 252-day start; 0.50 missing-pair fallback; <i>ρ</i> = 0.50; daily returns capped at ±30%</span></td></tr>
    <tr><th scope="row">Portfolio limits</th><td>7% volatility; 200% gross; 4% per name; ±25% net; ±0.05 beta</td></tr>
    <tr><th scope="row">Beta estimate</th><td>756-day correlation; 252-day minimum; 21-day volatility; stock beta capped at ±4</td></tr>
    <tr><th scope="row">Sector limits</th><td>±20% net; 30% of either book</td></tr>
    <tr><th scope="row">Trading controls</th><td><span><i>c</i> = 2.5 × 10<sup>−4</sup>; existing holdings may remain to rank 175</span></td></tr>
    <tr><th scope="row">Realized trading cost</th><td>5 bp per dollar bought or sold</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A1:</strong> Rule settings used throughout the comparison.</p>

### Volatility-scaled sizing

Within each book, the rule turns the standardized prediction into logistic
signal share $$p$$, applies
an inverse-volatility multiplier $$\lambda$$, caps the weight, and scales the
book down when gross exposure exceeds $$G_\ell$$:

$$
\begin{aligned}
p_{i,t}&\propto\left(1+e^{-\gamma d_\ell z_{i,t}}\right)^{-1},\\
\lambda_{i,t}&=\min\!\left\{\lambda_{\max},
\frac{\sigma_{\mathrm{target}}}{\widehat\sigma_{i,t}}\right\},\\
\widetilde w_{i,t}&=d_\ell\min\!\left\{w_{\max},
\min(p_{i,t},p_{\max})\lambda_{i,t}\right\},\\
w_{i,t}&=\widetilde w_{i,t}
\min\!\left\{1,\frac{G_\ell}{\sum_j|\widetilde w_{j,t}|}\right\}.
\end{aligned}
$$

Here $$z_{i,t}$$ is the prediction minus its book mean, divided by its book
standard deviation; $$d_\ell$$ is +1 for longs and −1 for shorts. The shares
$$p$$ sum to one before the signal-share cap $$p_{\max}$$. Capped weight is
not redistributed. The remaining caps limit the volatility multiplier,
individual position, and gross exposure of book $$\ell$$. Volatility is floored
at 5% annually, with a 20% fallback when its estimate is unavailable.

### Covariance safeguards

Daily returns are capped at ±30% before correlation estimation. A missing pair
uses a 0.50 fallback; in a long–short book that choice can be more
or less conservative depending on the signs of the positions. I symmetrize the
pairwise matrix, clip negative eigenvalues, and restore its unit diagonal before
shrinkage. The covariance retains $$\kappa=1.18$$ from the predecessor
allocator. A new calibration would estimate its replacement from the present
development-period forecast errors and repeat the allocation comparison.

[^schedules]: The [tranching study](/quants/2025/05/10/rebalancing-luck.html) introduced these staggered schedules as a check on rebalance-date luck.
