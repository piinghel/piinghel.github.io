---
layout: post
title: "From Volatility Scaling to a Constrained Optimizer"
date: 2026-08-29
last_modified_at: 2026-09-04
categories: ["Portfolio construction"]
article_label: Portfolio construction · Ridge allocation
permalink: /quants/2026/08/29/portfolio-optimization.html
---

<p class="article-summary">The Ridge model ranks stocks, but the volatility-scaled rule still sizes each stock separately. I replace it with an optimizer that sizes the whole book under one risk budget. Through 2021, Sharpe rises from 1.12 to 1.35, while turnover rises from 30× to 43×. Accounting for the current book brings turnover back to 28× and lifts Sharpe to 1.43. From January 2022 onward, the optimizer using the current book still edges the volatility-scaled rule, although the result varies more across rebalance schedules. Estimated beta is constrained at each rebalance, but realized beta still drifts; beta control is the next portfolio problem.</p>

The [low-vol post](/quant/2024/12/15/low-volatility-factor.html) showed that
inverse-volatility sizing balances the two books but leaves gross, net, and beta
uncontrolled. The [Ridge post](/quants/2025/02/09/multiple-linear-regression.html)
found that learned rankings double turnover and left two tasks: size stocks
jointly and account for the positions already held. This post does both.

## Study design and the three rules

The data history begins in 1995. The portfolio comparison starts in September
1998, once the signals and risk estimates have enough history. I use the period
through December 2021 to choose the settings. The final evaluation runs from
the first trading day of January 2022 through May 2026, with the first forecast
built from data already available at the end of 2021.

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
- The **optimizer using the current book**[^current-book] solves the same problem but starts
  from the positions already held and charges proposed changes in its
  objective.

Sharpe uses a zero risk-free rate. Turnover is annualized two-way weight change,
so 42× means purchases plus sales of 42 times capital per year. The development
period is also where I compare the covariance and trading settings. I fixed
those choices before calculating the final evaluation.

## Joint sizing buys more return

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

Here $$s_{i,t}$$ is the Ridge score and $$\widehat\sigma_{i,t}$$ is the stock's
volatility estimate. Their product is a return proxy for sizing. I treat it as
a relative input to the optimizer.

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
are the gross, net, name, beta, and sector limits. A portfolio intention becomes
one line in the same problem. Gross exposure is then an output of those choices
instead of a separate target that has to agree with several other sizing rules.
The exact limits are collected in Table A1.

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
    <tr><th scope="row">B1 · Vol-scaled rule</th><td data-label="Gross return">10.58%</td><td data-label="Net return">8.92%</td><td data-label="Net volatility">7.92%</td><td data-label="Net Sharpe">1.12</td><td data-label="Max drawdown">19.63%</td><td data-label="Turnover">30.27×</td></tr>
    <tr><th scope="row">B2 · Optimizer</th><td data-label="Gross return">14.00%</td><td data-label="Net return">11.60%</td><td data-label="Net volatility">8.41%</td><td data-label="Net Sharpe">1.35</td><td data-label="Max drawdown">19.77%</td><td data-label="Turnover">42.52×</td></tr>
    <tr><th scope="row"><strong>B3 · Optimizer using current book</strong></th><td data-label="Gross return"><strong>13.91%</strong></td><td data-label="Net return"><strong>12.32%</strong></td><td data-label="Net volatility"><strong>8.40%</strong></td><td data-label="Net Sharpe"><strong>1.43</strong></td><td data-label="Max drawdown"><strong>18.06%</strong></td><td data-label="Turnover"><strong>28.19×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Development-period return, realized risk, and trading, September 1998–December 2021. Metrics are means of three staggered schedules. Returns and volatility are annualized; net results charge 5 basis points for every dollar bought or sold.</p>

The comparison changes the whole allocation rule. Covariance, return-unit
scaling, and the constraints all move together. I read the result as evidence
that joint sizing uses the ranking better than separate stock-by-stock sizing.
A component-by-component comparison would isolate the source.

Figure 1 gives the path behind the averages. The optimizer finishes above the
volatility-scaled rule. Using the current book finishes highest and loses less
in its worst drawdown. Its lead opens mainly around 2000 and 2021 rather than
building at a steady rate.

<div class="research-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/performance-and-drawdowns" alt="Development-period net growth and drawdowns for the volatility-scaled rule, optimizer, and optimizer using the current book" version="9" %}
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

The shrunk correlation matrix becomes a covariance matrix through

$$
\Sigma_t=\kappa^2D_tC_t(\rho)D_t,
$$

where $$D_t$$ contains the stock-volatility estimates and $$\kappa$$ corrects
their average level. This split lets volatility react quickly while correlation
uses more history. Shrinkage controls how much of the estimated cross-stock
structure reaches the optimizer.

The middle of Figure 2 is the useful region. From 0.3 to 0.6 shrinkage, forecast
calibration, beta error, turnover, and Sharpe move little. With no shrinkage,
realized volatility runs above forecast. Full shrinkage throws away too much
shared-risk information and misses by more. The broad middle matters more than
the exact point inside it.

<div class="research-figure rho-ladder-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/rho-ladder" alt="Development-period risk calibration, beta error, turnover, and net Sharpe across covariance-shrinkage values for both optimizers" version="5" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Development-period forecast calibration, beta error over the next holding period, annualized turnover, and net Sharpe across correlation-shrinkage values from zero to one. The shaded band marks 0.3 to 0.6; lines compare the optimizer with the optimizer using the current book.</p>

The two ends fail for different reasons. At zero, the optimizer can chase every
estimated correlation. At one, it behaves as if stock returns are uncorrelated.
Several nearby settings in the middle produce similar allocations and results.
Shared-risk structure matters, while the exact shrinkage value matters less
inside the middle range.

The portfolio limits also act as guardrails. They bound how far one noisy score,
correlation, or beta estimate can move a name, sector, or the whole book. That
means the framework gives more control and asks for more care at the same time.

Realized volatility still runs about 18% above forecast. I treat that stable
gap as a configuration issue. The covariance input already includes one
calibration multiplier, so the next version can estimate it from the
development-period forecast error and rerun every portfolio. Recalibration
changes the weights and turnover as well as the risk forecast, so the full
comparison has to be repeated.

## Making the optimizer pay for each trade

Where does the extra turnover come from? At every rebalance, the optimizer sees
the newly selected stocks but gives no value to a position already in the book.
A small change in rank or covariance can replace a holding even when the new
stock adds little at the portfolio level.

Take a long stock whose rank slips from 60 to 110. The optimizer drops it
because only the top 75 enter the new selection. The optimizer using the current
book may retain it while it remains inside the wider top 175. It begins from the
previous target weights after intervening price moves and before the new trade.

If $$w_t^{\mathrm{pre}}$$ is that current book and $$c$$ is the trade
coefficient, the objective becomes

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
objective.

Figure 3 checks both choices on the development period. The left column varies
the trade coefficient while holding the rank cutoff at 175. The right varies
the cutoff while holding the coefficient at 2.5. Points are the mean of the
three schedules and vertical lines show their range.

<div class="research-figure parameter-sensitivity-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/parameter-sensitivity" alt="Development-period net Sharpe and annualized turnover for five trade coefficients and five holding-rank cutoffs" version="2" %}
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Local development-period sensitivity of net Sharpe (top) and annualized turnover (bottom). The selected settings are highlighted. Each column changes one setting and holds the other at its selected value; vertical bars span the three staggered schedules.</p>

The nearby coefficients show a smooth trade-off. At 2.0, 2.5, and 3.0, net
Sharpe is 1.43, 1.43, and 1.42. Turnover falls more steadily, from 30× to 28×
and then 27×. The wider endpoints show what happens outside that neighborhood:
removing the trade term raises turnover to about 40×, while doubling the
coefficient gives back some return.

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

Gross return barely changes. The optimizer using the current book reaches
nearly the same portfolio with fewer replacements. The cost saving is the gain.
I read this as evidence that many marginal replacements add little at the
portfolio level.

## Realized beta remains the main problem

The optimizer keeps its beta estimate inside the stated range at each
rebalance. Realized beta can still drift as prices and exposures change over
the holding period. Figure 4 shows that this happens in persistent episodes.

<div class="research-figure risk-beta-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/risk-calibration-and-beta" alt="Development-period trailing realized beta for the volatility-scaled rule and both optimizers" version="9" %}
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Monthly trailing one-year realized market beta for all three rules, averaged across the staggered schedules, September 1998–December 2021. The constraint uses a point-in-time estimate at each rebalance, while this chart measures the portfolio outcome over a trailing year.</p>

The optimizer reduces the long departures from zero relative to volatility
scaling, but several episodes still last for months and reach roughly 0.3. At
each rebalance the estimated exposure is within its limit; the realized path
shows that the estimate is too slow or too noisy. This points to the beta
estimate used to choose stocks and weights.

I tested a shorter beta window. It removes those persistent episodes, but it
also reduces later net return by 0.6 percentage points. I required a replacement
to stay within 0.5 points of later net return, so I keep the current stock-level
estimate. A costed benchmark overlay is the next way to separate beta
management from stock selection.

Capacity is the other practical limit. Turnover falls to 28×, which is still
high once market impact, borrow, and the stocks near the edge of the universe
matter. A flat 5-basis-point charge gives a consistent comparison; a capacity
study needs trade size and liquidity.

## The current book still helps after 2021, but timing matters

Table 2 starts on the first trading day of 2022. All three rules weaken relative
to their development results. The optimizer trails volatility scaling after
trading more. Using the current book changes the result: net return is 8.0%
versus 7.4%, Sharpe is 0.87 versus 0.78, and turnover falls below the baseline.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Net Sharpe</th><th>Max DD</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">B1 · Vol-scaled rule</th><td data-label="Gross return">8.92%</td><td data-label="Net return">7.38%</td><td data-label="Net volatility">9.73%</td><td data-label="Net Sharpe">0.78</td><td data-label="Max drawdown">8.65%</td><td data-label="Turnover">28.35×</td></tr>
    <tr><th scope="row">B2 · Optimizer</th><td data-label="Gross return">8.63%</td><td data-label="Net return">6.47%</td><td data-label="Net volatility">9.39%</td><td data-label="Net Sharpe">0.71</td><td data-label="Max drawdown">9.41%</td><td data-label="Turnover">39.97×</td></tr>
    <tr><th scope="row"><strong>B3 · Optimizer using current book</strong></th><td data-label="Gross return"><strong>9.33%</strong></td><td data-label="Net return"><strong>7.99%</strong></td><td data-label="Net volatility"><strong>9.32%</strong></td><td data-label="Net Sharpe"><strong>0.87</strong></td><td data-label="Max drawdown"><strong>9.05%</strong></td><td data-label="Turnover"><strong>24.62×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Final evaluation from January 2022 through May 2026. Metrics are means of three staggered schedules and use the same execution and cost assumptions as Table 1.</p>

That average needs one qualification. The optimizer using the current book has
a 4.5-point spread in net return across the three schedules, compared with 1.5
points for the volatility-scaled rule. Two schedules favor the optimizer and one
is much weaker. The short final period therefore supports the value of trading
more slowly, but with less confidence than the longer development result.

Market exposure explains only part of the weaker result. The optimizer using the
current book has beta of 0.01 over the evaluation period. It is mildly negative
in 2022 and 2023, then turns positive. The loss in the first five months of 2026
occurs with beta around 0.22 and weak return after accounting for the market.
The optimizer carries less of the market than the volatility-scaled rule
throughout a market-positive period, which accounts for part of its return gap.
Its higher trading cost widens that gap. Using the current book overcomes both
effects through a stronger residual return and fewer trades.

The worst drawdown is a useful check on that interpretation. In one schedule,
the optimizer using the current book fell 9.2% from its 28 December 2022 peak to
2 February 2023. Its beta during the decline was −0.08, which accounts for about
0.9 percentage points while the market rose 11.1%. Another schedule fell 9.1%
over the same dates with positive beta. Negative beta made the first loss worse.
The similar loss with positive beta points to positions shared across the
schedules.

Splitting the drawdown into the two books points to the shorts. Averaged across
the three schedules, the long book added 7.2 percentage points while the short
book cost 16.4. The next question is why the shorted stocks rallied together.

The rolling extremes tell the same story. The worst three-month period ended on
2 February 2023 and lost 6.8%; its beta was −0.07. The best three-month period
ended on 3 April 2024 and gained 11.3% with beta of 0.04. Market exposure was a
small part of both moves.

Even with wider timing variation, the final period leaves the implementation
choice intact. I move from volatility scaling to the constrained optimizer, and
I use the version that accounts for the current book. It sizes shared risk
jointly, makes exposure limits explicit, and avoids many marginal replacements.
In return, it demands careful covariance estimates, constraints that keep noisy
estimates from dominating the book, and separate beta control.

The first follow-up is mechanical. I will recalibrate the volatility multiplier
from the development-period forecast error and rerun all three rules. That will
show whether matching the intended risk more closely changes the comparison or
only its scale.

The drawdown points to the next research question. I want to trace the common
sector, style, and stock exposures in the short book across schedules. That
will tell me whether the residual loss came from the Ridge ranking, a shared
constraint, or a small set of overlapping positions. A matched trade study can
then ask whether the optimizer using the current book avoids weak replacements
or merely delays necessary exits.

The next portfolio change to test is the costed benchmark overlay. After that,
a liquidity and borrow model should replace the flat trading charge before I
make a capacity claim.

## Appendix: parameters and two implementation notes

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Component</th><th>Setting</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Initial selection</th><td data-label="Setting">75 long + 75 short</td></tr>
    <tr><th scope="row">Vol-scaled rule</th><td data-label="Setting"><span><i>γ</i> = 2; 60-day volatility; 20% target and fallback; 5% floor; 10% signal-share cap; 4% name cap; 6× multiplier cap; 100% gross per book</span></td></tr>
    <tr><th scope="row">Covariance</th><td data-label="Setting"><span>21-day volatility; 756-day correlation; 252-day start; 0.50 missing-pair fallback; <i>ρ</i> = 0.50; daily returns capped at ±30%</span></td></tr>
    <tr><th scope="row">Portfolio limits</th><td data-label="Setting">7% volatility; 200% gross; 4% per name; ±25% net; ±0.05 beta</td></tr>
    <tr><th scope="row">Beta estimate</th><td data-label="Setting">756-day correlation; 252-day minimum; 21-day volatility; stock beta capped at ±4</td></tr>
    <tr><th scope="row">Sector limits</th><td data-label="Setting">±20% net; 30% of either book</td></tr>
    <tr><th scope="row">Current-book settings</th><td data-label="Setting"><span><i>c</i> = 2.5 × 10<sup>−4</sup>; existing holdings may remain to rank 175</span></td></tr>
    <tr><th scope="row">Realized trading cost</th><td data-label="Setting">5 bp per dollar bought or sold</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A1:</strong> Rule settings used throughout the comparison.</p>

### Volatility-scaled sizing

Within each book, the rule turns rank into logistic signal share $$p$$, applies
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

### Covariance safeguards

Daily returns are capped at ±30% before correlation estimation. A missing pair
uses a 0.50 fallback; in a long–short book that choice can be more
or less conservative depending on the signs of the positions. I symmetrize the
pairwise matrix, clip negative eigenvalues, and restore its unit diagonal before
shrinkage. The covariance is multiplied by $$\kappa^2$$, with $$\kappa=1.18$$
set from the development-period risk calibration. The next calibration will
estimate this number directly from development-period forecast error.

[^schedules]: The [tranching study](/quants/2025/05/10/rebalancing-luck.html) introduced these staggered schedules as a check on rebalance-date luck.
[^current-book]: The current book is the previous target portfolio after price moves and before the next rebalance. An incumbent may remain in the choice set while its rank stays inside 175.
