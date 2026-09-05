---
layout: post
title: "Joint Sizing with Fewer Trades"
description: "Joint sizing adds turnover. A rank buffer and trade penalty recover more of the gross return."
date: 2026-08-29
last_modified_at: 2026-09-05
categories: ["Portfolio construction"]
article_label: Portfolio construction · Ridge allocation
permalink: /quants/2026/08/29/portfolio-optimization.html
series_previous: /quants/2025/02/09/multiple-linear-regression.html
series_next: /quants/2025/05/10/rebalancing-luck.html
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/systematic-equity-research
---

<p class="article-summary">Joint sizing raises this Ridge portfolio's development-period Sharpe from 1.12 to 1.35, but adds turnover. Letting the optimizer keep acceptable holdings and penalizing replacements cuts turnover by about a third while preserving gross return. I use both controls, though the advantage is smaller and less consistent after 2021. Risk forecasts also understate realized volatility.</p>

The [low-vol post](/quant/2024/12/15/low-volatility-factor.html) showed that
inverse-volatility sizing balances the long and short books. It sizes each
stock separately. Joint sizing adds the covariance between positions to that
decision. In the
[Ridge post](/quants/2025/02/09/multiple-linear-regression.html), I replaced the
fixed score with a learned ranking. Sharpe improved, but turnover doubled. Here
I feed those predictions into an optimizer that sizes stocks
jointly, and the trading controls make it less eager to replace positions that
still rank well.

## Three allocation rules

The comparison starts in September 1998, after the signals and risk estimates
have enough history. I choose settings using data through December 2021.
January 2022–May 2026 provides the later comparison, but that history has since
informed feature, allocation, and beta-estimator choices. It is reused evidence.

Every rule starts from the same Ridge ranking and trades the same three
staggered schedules.[^schedules] A staggered schedule runs the full strategy
from a different starting week. Each schedule rebalances every three weeks,
uses the same next-close execution, and pays 5 basis points on traded notional.

- The **volatility-scaled rule** maps rank to a signal weight, scales each stock
  by its own volatility, and applies caps.
- The **optimizer** takes the same selected stocks and sizes them together under
  portfolio constraints.
- The **optimizer with trading controls** solves the same problem, but it may
  keep existing holdings from a wider rank range and penalizes changes in its
  objective.

The tables average metrics calculated separately for the three schedules. Returns are
geometric annualized returns; Sharpe uses arithmetic mean daily return and a
zero risk-free rate. Two-way turnover sums absolute executed trades relative
to strategy capital, annualized over the reporting window.

There is also a change from the preceding regression article: this baseline
uses score-dependent weights before volatility scaling, whereas that article
uses equal signal weights within each selected book. I compare allocators
within the present study; comparing performance levels across the two posts
would also pick up that sizing change.

## Development results

The volatility-scaled rule is easy to inspect. But it sizes the long and short
books separately and never sees covariance. Several modest positions can
therefore carry the same market or sector risk without the rule recognizing the
overlap.

The optimizer sizes the selected stocks together under a forecast-risk budget,
with limits on gross and net exposure, individual names, market beta, and
sectors. The appendix writes out that allocation problem. Here I first compare
what the whole rule delivers and what it costs to trade.

In Table 1, joint sizing adds about three and a half percentage points of gross
return at similar realized risk. It also trades 42.5 times capital annually,
versus 30.3 for volatility scaling. The third rule preserves almost all that
gross return while removing much of the extra trading.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Net Sharpe</th><th>Max drawdown loss</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">B1 · Vol-scaled rule</th><td>10.58%</td><td>8.92%</td><td>7.92%</td><td>1.12</td><td>19.63%</td><td>30.27×</td></tr>
    <tr><th scope="row">B2 · Optimizer</th><td>14.00%</td><td>11.60%</td><td>8.41%</td><td>1.35</td><td>19.77%</td><td>42.52×</td></tr>
    <tr><th scope="row"><strong>B3 · Optimizer + trading controls</strong></th><td><strong>13.91%</strong></td><td><strong>12.32%</strong></td><td><strong>8.40%</strong></td><td><strong>1.43</strong></td><td><strong>18.06%</strong></td><td><strong>28.19×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> September 1998–December 2021, means of three schedule-level metrics. Returns are geometric and annualized; volatility is annualized. Net results charge 5 bp on traded notional. Drawdowns are reported as positive loss magnitudes.</p>

Covariance, the score used for sizing, and the constraints change together, so
isolating covariance's contribution would require a separate comparison. The forecast risk target is 7%; realized volatility
exceeds it for both optimizers. I return to that calibration miss below.

Figure 1 gives the path behind the averages. The optimizer finishes above the
volatility-scaled rule. Adding the trading controls finishes highest and loses
less in its worst drawdown. Its lead opens mainly around 2000 and 2021 rather
than building at a steady rate.

<div class="research-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/performance-and-drawdowns" alt="Development-period net growth and drawdowns for the volatility-scaled rule, optimizer, and optimizer with trading controls" version="12" %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Net growth of <span class="mathjax-ignore">$1</span> on a logarithmic scale (top) and drawdown in percent (bottom) after trading costs, September 1998–December 2021. Each path averages three separately compounded staggered schedules.</p>

## Keeping existing holdings

The optimizer starts from the newly selected stocks at every rebalance,
without a preference for retaining a position already held. A small change in
rank or covariance can then trigger a replacement whose benefit is smaller
than its trading cost. I want the allocation decision to include that cost of
changing direction.

Take a long stock whose rank slips from 60 to 110. The optimizer drops it
because only the top 75 enter the new selection. The optimizer with trading
controls may retain it while it remains inside the wider top 175. It starts from
the existing weights after intervening price moves.

Let $$w_t$$ be the signed portfolio weights and $$\mu_t$$ the sizing scores:
Ridge predictions multiplied by each stock's daily volatility. Their scale is
used for relative allocation. Calibrating them to expected returns would
require another estimation step. If
$$w_t^{\mathrm{pre}}$$ contains the weights just before rebalancing and
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
enter executed turnover as mandatory trades.

Table 2 separates the two controls. A *rank buffer* lets an existing long
remain eligible down to rank 175, while new positions still enter through the
top 75; the short book uses the corresponding bottom ranks. The buffer alone
saves little turnover. With a penalty on changing weights, it becomes much
more useful: the optimizer can retain an acceptable incumbent instead of
paying to replace it.

<table class="research-table comparison-table control-table">
  <thead><tr><th>Trading rule</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Annual turnover</th></tr></thead>
  <tbody>
    <tr><th scope="row">Neither control</th><td>14.00%</td><td>11.60%</td><td>1.35</td><td>42.52×</td></tr>
    <tr><th scope="row">Rank buffer only</th><td>14.07%</td><td>11.84%</td><td>1.37</td><td>39.54×</td></tr>
    <tr><th scope="row">Trade penalty only</th><td>13.95%</td><td>11.95%</td><td>1.39</td><td>35.35×</td></tr>
    <tr><th scope="row"><strong>Buffer + penalty</strong></th><td><strong>13.91%</strong></td><td><strong>12.32%</strong></td><td><strong>1.43</strong></td><td><strong>28.19×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Development-period means across three schedules, September 1998–December 2021. Returns are annualized geometric returns. The buffer uses rank 175 and the penalty uses <i>c</i> = 2.5 × 10<sup>−4</sup>. Other allocation settings are the same. <a href="/assets/portfolio-optimization/parameter-sensitivity.csv">Control results</a> · <a href="/assets/portfolio-optimization/period-comparison.csv">Baseline results</a>.</p>

The buffer reduces turnover by about 3× without the penalty, and 7× with it.
That is why I use the two controls together. They change which stocks remain
eligible and how much I hold, so the difference includes changes in positions
as well as trading costs.

Figure 2 checks both choices on the development period. The left column varies
the trade coefficient while holding the rank cutoff at 175. The right varies
the cutoff while holding $$c=2.5\times10^{-4}$$. The coefficient axis is in
units of $$10^{-4}$$, so the plotted value 2.5 denotes that setting. Points are the mean of the
three schedules and vertical lines show their range.

<div class="research-figure parameter-sensitivity-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/parameter-sensitivity" alt="Development-period net Sharpe and annualized turnover for six trade coefficients and five holding-rank cutoffs" version="6" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Local development-period sensitivity of net Sharpe (top) and annualized turnover (bottom). The selected settings are highlighted. Each column changes one setting and holds the other at its selected value; vertical bars span the three staggered schedules.</p>

From 1 through 3, net Sharpe stays between 1.42 and 1.43 while turnover keeps
falling, from 34× to 27×. The data therefore identify a broad trade-off rather
than one best coefficient. I use 2.5 because it sits toward the lower-turnover
end of that plateau; pushing to 5 gives back some return.

The rank cutoff is also locally stable. Moving from 150 to 175 raises Sharpe
from 1.41 to 1.43 and lowers turnover by about one turn. Moving on to 200 saves
less than another turn, leaves Sharpe at 1.42, and raises mean maximum drawdown
from 18.1% to 19.2%. I use 175 as a practical balance.

A 5 bp charge on 28.2 times annual turnover costs about 1.41% of strategy capital
per year on an arithmetic basis. The gap between gross and net geometric
returns includes the effect of compounding as well as these daily charges.

## Results after 2021

Table 3 starts on the first trading day of 2022. All three rules weaken relative
to their development results. The optimizer trails volatility scaling after
trading more. The trading controls change the result: net return is 8.0% versus
7.4%, Sharpe is 0.87 versus 0.78, and turnover falls below the baseline.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Net Sharpe</th><th>Max drawdown loss</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">B1 · Vol-scaled rule</th><td>8.92%</td><td>7.38%</td><td>9.73%</td><td>0.78</td><td>8.65%</td><td>28.35×</td></tr>
    <tr><th scope="row">B2 · Optimizer</th><td>8.63%</td><td>6.47%</td><td>9.39%</td><td>0.71</td><td>9.41%</td><td>39.97×</td></tr>
    <tr><th scope="row"><strong>B3 · Optimizer + trading controls</strong></th><td><strong>9.33%</strong></td><td><strong>7.99%</strong></td><td><strong>9.32%</strong></td><td><strong>0.87</strong></td><td><strong>9.05%</strong></td><td><strong>24.62×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 3:</strong> January 2022–May 2026, a later period revisited during research. Schedule averaging, geometric-return, drawdown, and cost conventions match Table 1.</p>

The average hides a large calendar effect. The optimizer with trading controls has a
4.5-point spread in net return across the three schedules, compared with 1.5
points for the volatility-scaled rule. Two schedules favor the optimizer and
one is much weaker. Trading more slowly still helps on average, but the
result is much less consistent than during development.

Could market exposure explain the weaker result? Only partly. The optimizer
with trading controls has beta of 0.01 over the evaluation period. Its beta is
mildly negative in 2022 and 2023, then turns positive. In the first five months
of 2026, the portfolio loses money with beta around 0.22. The positive beta
has a positive fitted market component during that episode, but the remaining
return is still negative. The residual from this ex-post market regression
includes all return variation left unexplained by the market factor.

Beta does fall around the largest drawdown. Across the three schedules, trailing
63-day beta ranges from −0.02 to +0.02 at the December 2022 peak. By the February
2023 trough it ranges from −0.10 to −0.02. The beta estimate used by the
optimizer also turns negative and reaches its −0.05 limit in every schedule.

The drop is real, but it explains little of the loss. The schedule with beta of
−0.08 loses 9.2%; its fitted market component is about −0.9 percentage points.
Another schedule loses 9.1% over the same dates with positive beta. Averaged
across schedules over 29 December 2022–2 February 2023, the long book adds
7.2 points while the short book costs 16.4. These are sums of daily after-cost
book contributions; linking them through compounding gives a different measure.

The short book also drove the difficult episodes in the [low-vol
post](/quant/2024/12/15/low-volatility-factor.html). Whether the two portfolios
share a style exposure remains an attribution question. Here the market-only
decomposition leaves most of the loss unexplained.

## Covariance and risk forecasts

Both optimizers realize more volatility than they forecast. Correlation error
can make a group of positions appear safer than it is. I let stock
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
from the predecessor allocator.
Volatility uses 21 days and correlation 756 days, so the model can respond to a
change in risk level without re-estimating every stock relationship on a short
window.

Figure 3 shows why I keep some estimated correlation in the risk model. From 0.3 to 0.6 shrinkage, forecast
calibration, beta error, turnover, and Sharpe move little. With no shrinkage,
realized volatility runs above forecast. Full shrinkage throws away too much
shared-risk information and misses by more. The broad middle matters more than
the exact point inside it.

The calibration panel takes the square root of mean realized holding-period
variance divided by mean forecast variance; one would indicate agreement in
level. The averaging takes place in variance units before the square root.

<div class="research-figure rho-ladder-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/rho-ladder" alt="Development-period risk calibration, beta error, turnover, and net Sharpe across correlation-shrinkage values for both optimizers" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 3:</strong> The horizontal axis in every panel is correlation shrinkage, from zero to one. The panels show development-period forecast calibration, beta error over the next holding period, annualized turnover, and net Sharpe. The shaded band marks 0.3 to 0.6; lines compare the optimizer with and without trading controls.</p>

At the implemented shrinkage, root-mean realized volatility is about 21% above
forecast for the optimizer and 18% above for the version with trading controls.
The existing multiplier therefore needs another calibration
check on development data. That would be a model change: changing covariance
alters the weights, constraints that bind, turnover, and realized risk. I would
rerun the matched portfolios with the recalibrated covariance.

## Forecast beta versus realized beta

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
it reflects portfolios held throughout that year. The
holding-period diagnostics also show estimation error beyond ordinary
execution and weight drift. Both the measurement window and the stock-beta
estimate matter.

I tested a 63-day beta window in matched portfolios. It removes the flagged
persistent episodes, but B3 fails the later tail-error check and loses 0.6
percentage points of annualized net return, beyond the 0.5-point tolerance.
I therefore keep the existing estimate. That rejection also means the later
period has participated in model selection.

## My allocation choice

I use the constrained optimizer with both trading controls. It lets me set
portfolio limits jointly and earns nearly the same
development gross return as the optimizer without controls, with fewer trades. The weaker,
less consistent later results keep me from treating that choice as settled.

Before adding another constraint, I want to know where the risk and P&L sit.
The drawdown evidence identifies the short book. Separating a shared style
exposure from stock-specific losses comes
before a new style limit or a market hedge. Matched counterfactual portfolios
would then be needed to decide whether the ranking, retention rule, or a
constraint caused the exposure.

Risk recalibration remains a concrete implementation test. Borrow,
financing, liquidity, and market impact also remain outside the flat trading
charge. They would have to enter the portfolio replay before using these
results to judge capacity.

## Appendix

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
    <tr><th scope="row">Realized trading cost</th><td>5 bp on traded notional</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A1:</strong> Rule settings used throughout the comparison.</p>

### Joint-sizing objective

The optimizer starts from the same ranking and sizes all selected stocks at
once. The score orders stocks by predicted target rank. Its
training target divides forward return by volatility, so I map the score into
return units using each stock's volatility:

$$
\mu_{i,t}=s_{i,t}\widehat{\sigma}_{i,t}.
$$

Here $$s_{i,t}$$ is the Ridge score and $$\widehat\sigma_{i,t}$$ is the daily
stock-volatility estimate supplied to the objective. Their product is a daily
return proxy for sizing. Ranking the
training target discarded its magnitude. I use the product as a relative allocation score;
its scale also determines the strength of the trading penalty used in the trading controls.

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
$$p$$ sum to one before the signal-share cap $$p_{\max}$$. Weight above the cap
is left unallocated. The remaining caps limit the volatility multiplier,
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
