---
layout: post
title: "Joint Sizing with Fewer Trades"
description: "Joint sizing adds turnover. A rank buffer and trade penalty recover more of the gross return."
date: 2026-08-29
last_modified_at: 2026-09-16
categories: ["Portfolio construction"]
article_label: Portfolio construction · Ridge allocation
permalink: /quants/2026/08/29/portfolio-optimization.html
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/portfolio-optimization-study
---

In the previous articles on [low-volatility sizing](/quant/2024/12/15/low-volatility-factor.html)
and [Ridge regression](/quants/2025/02/09/multiple-linear-regression.html),
I used a simple volatility-scaling rule to size positions. Giving less weight
to more volatile stocks already worked well. Here, I want to take a closer
look at whether I can improve on that by accounting for how the stocks move
together and sizing the portfolio jointly.

There are two problems I want to tackle. The optimizer can lean too heavily
on combinations that look safer than they really are, and it can trade a lot
for small changes in the inputs. I try correlation shrinkage for the first
problem, then a rank buffer and a trading penalty for the second. The question
is whether sizing stocks together still helps after costs, and whether the
portfolio takes about as much risk as expected.

## Three allocation rules

The comparison starts in September 1998, after the signals and risk estimates
have enough history. I choose settings using data through December 2021.
I also show January 2022–May 2026 separately to see how the rules behave more
recently.

Every allocation rule starts from the same Ridge ranking and follows three rebalance
schedules, each beginning in a different week. Each schedule rebalances every three weeks,
uses the same next-close execution, and pays 5 basis points on traded notional.

- **Volatility-scaled** maps prediction scores to signal weights, scales each stock
  by its own volatility, and applies caps.
- **Optimizer** takes the same selected stocks and sizes them together under
  portfolio constraints.
- **Optimizer + trading controls** solves the same problem, but it may
  keep existing holdings from a wider rank range and adds a penalty for trading.

This baseline differs from the regression article's allocation rule. There,
selected stocks start with equal signal weights before volatility scaling;
here, stronger prediction scores receive larger signal weights.

The tables average metrics calculated separately for the three schedules. Returns are
geometric annualized returns; Sharpe uses arithmetic mean daily return and a
zero risk-free rate. Two-way turnover sums absolute executed trades relative
to strategy capital, annualized over the reporting window.

Joint sizing changes the covariance, score scaling and constraints at once, so I
compare the full rules rather than each change separately.

<h2 id="development-results">Sizing stocks together</h2>

The optimizer sizes the selected stocks together under a forecast-risk budget,
with limits on gross and net exposure, individual names, market beta, and
sectors.

The unconstrained Sharpe problem is a useful starting point. With expected
excess returns $$\alpha$$ and a positive-definite covariance matrix $$\Sigma$$,

$$
\max_{w\ne0}\frac{\alpha^\top w}{\sqrt{w^\top\Sigma w}},
\qquad w^\star\propto\Sigma^{-1}\alpha.
$$

Multiplying all positions by a positive constant scales expected return and
volatility equally, so Sharpe is unchanged. The solution fixes relative
weights but leaves portfolio size open. Setting portfolio volatility to
one—unit volatility—is a convenient normalization for the derivation.
Without other limits, I can then rescale to the volatility I want.

Portfolio limits make size and risk a joint decision. Scaling from 5% to 7%
forecast volatility turns a 4% position into 5.6%, breaching the name cap.
That's why I put the actual volatility budget inside the optimization.

My inputs are relative sizing scores, rather than calibrated expected returns.
For each stock, I multiply its Ridge prediction $$s_{i,t}$$ by estimated daily
volatility $$\widehat\sigma_{i,t}$$ to get
$$\mu_{i,t}=s_{i,t}\widehat\sigma_{i,t}$$. The target ranks forward returns
divided by volatility. Multiplying by volatility puts those scores on each
stock's risk scale, but can't recover the return magnitudes lost in ranking.
With signed portfolio weights $$w_t$$ and volatility target
$$\sigma_{\mathrm{target}}$$, I solve

$$
\begin{aligned}
\max_{w_t}\quad & \mu_t^\top w_t \\
\text{subject to}\quad
& w_t^\top\Sigma_t w_t\leq \sigma_{\mathrm{target}}^2,\\
& w_t\in\mathcal W_t.
\end{aligned}
$$

I use a 7% annual volatility target. Here $$\Sigma_t$$ is the annualized
forecast covariance matrix, so $$w_t^\top\Sigma_t w_t$$ is annual portfolio variance.
The set $$\mathcal W_t$$ contains the other portfolio limits:
200% gross, ±25% net, 4% per name, ±0.05 estimated beta, and the sector caps
in Table 4. Long candidates can receive positive or zero weights; short
candidates negative or zero weights. With these limits, maximizing the score
isn't the same as maximizing Sharpe: other limits can bind before forecast
volatility reaches 7%.

These limits apply to target weights at a rebalance. Next-close execution and
subsequent price moves can take the actual holdings outside those bounds.

In Table 1, joint sizing adds about three and a half percentage points of gross
return at similar realized risk. It also trades 42.5 times capital annually,
versus 30.3 for volatility scaling. The third rule preserves almost all that
gross return while removing much of the extra trading.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 1: Joint sizing and trading costs.</strong> September 1998–December 2021, means of three schedule-level metrics. Returns are geometric and annualized; volatility is annualized. Net results charge 5 bp on traded notional. Drawdowns are reported as positive loss magnitudes.</caption>
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Sharpe</th><th>Drawdown loss</th><th>Annual turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Volatility-scaled</th><td>10.58%</td><td>8.92%</td><td>7.92%</td><td>1.12</td><td>19.63%</td><td>30.3×</td></tr>
    <tr><th scope="row">Optimizer</th><td>14.00%</td><td>11.60%</td><td>8.41%</td><td>1.35</td><td>19.77%</td><td>42.5×</td></tr>
    <tr class="selected-rule"><th scope="row">Optimizer + trading controls</th><td>13.91%</td><td>12.32%</td><td>8.40%</td><td>1.43</td><td>18.06%</td><td>28.2×</td></tr>
  </tbody>
</table>

Figure 1 shows where the lead opens, mainly around 2000 and 2021.
Trading controls give the highest ending value and the smallest maximum drawdown.
The paths use each portfolio's actual risk level: about 8.4% annualized
volatility for the joint rules versus 7.9% for volatility scaling. Table 1
puts those gains alongside volatility and Sharpe.

<div class="research-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/performance-and-drawdowns" mobile="/assets/portfolio-optimization/performance-and-drawdowns_mobile" alt="Development-period net growth and drawdowns for the volatility-scaled rule, optimizer, and optimizer with trading controls" version="14" %}
</div>

<p class="figure-caption"><strong>Figure 1: Development-period results.</strong> Net growth index (log scale) and drawdown after trading costs, September 1998–December 2021. Paths average three separately compounded schedules at each rule's own risk level. Table 1 compares volatility and Sharpe.</p>

## Keeping existing holdings

At each rebalance, the basic optimizer starts from the newly selected stocks.
A small change in rank or covariance can trigger a replacement whose benefit is smaller
than its trading cost. A slightly better portfolio on paper can be a worse
trade in practice.

The rank buffer keeps existing holdings eligible, while the trading penalty
discourages unnecessary replacements.

Take a long stock whose rank slips from 60 to 110. The basic optimizer drops it
because only the top 75 enter the new selection. A *rank buffer* lets it stay
eligible through rank 175; the short book uses the corresponding bottom ranks.
Holdings outside that range still close, with the backtest charging for the exit.

The sizing scores and risk budget stay the same. Let $$w_t^{\mathrm{pre}}$$
be the weights just before rebalancing, after intervening price moves.
With trade coefficient $$c$$, the objective becomes

$$
\max_{w_t}\quad
\mu_t^\top w_t-c\lVert w_t-w_t^{\mathrm{pre}}\rVert_1,
$$

under the same portfolio constraints. The second term penalizes changes
from the existing weights; $$c$$ sets the penalty relative to the sizing scores.

The score scale matters once I add this penalty. Multiplying all sizing scores
by a positive constant leaves the basic optimizer's preferred weights unchanged.
With the penalty, multiplying scores by $$a$$ is equivalent to dividing $$c$$
by $$a$$. My choice of $$c=2.5\times10^{-4}$$ is a tuning coefficient in
these score units.

The L1 term counts both sides of a replacement. Selling a 1% position and buying
another 1% position changes $$\lVert w_t-w_t^{\mathrm{pre}}\rVert_1$$ by 2%.
The optimizer keeps the existing holding unless the new score-and-risk combination
clears that hurdle. Constraints can still force a trade when the old position
breaches a limit. The backtest separately charges 5 bp on executed trades.

Table 2 separates what the buffer and penalty contribute.

<table class="research-table comparison-table control-table">
  <caption><strong>Table 2: What the trading controls contribute.</strong> Development-period means across three schedules, September 1998–December 2021. Returns are geometric and annualized, with net results charging 5 bp per dollar traded. The buffer uses rank 175 and the penalty uses <i>c</i> = 2.5 × 10<sup>−4</sup>; other allocation settings are the same.</caption>
  <thead><tr><th>Trading rule</th><th>Gross return</th><th>Net return</th><th>Net Sharpe</th><th>Annual turnover</th></tr></thead>
  <tbody>
    <tr><th scope="row">Neither control</th><td>14.00%</td><td>11.60%</td><td>1.35</td><td>42.5×</td></tr>
    <tr><th scope="row">Rank buffer only</th><td>14.07%</td><td>11.84%</td><td>1.37</td><td>39.5×</td></tr>
    <tr><th scope="row">Trade penalty only</th><td>13.95%</td><td>11.95%</td><td>1.39</td><td>35.4×</td></tr>
    <tr class="selected-rule"><th scope="row">Buffer + penalty</th><td>13.91%</td><td>12.32%</td><td>1.43</td><td>28.2×</td></tr>
  </tbody>
</table>

The buffer alone saves about three times capital in annual trading; adding it
alongside the penalty saves seven. That's why I use them together: the buffer
allows more holdings to remain eligible, and the penalty favours retaining them.
Both controls change positions as well as trading costs.

Figure 2 checks nearby settings in development, varying one control at a time
around the chosen penalty and rank cutoff. The coefficient axis uses units of
$$10^{-4}$$; the plotted value 2.5 is the setting in Table 4.

<div class="research-figure parameter-sensitivity-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/parameter-sensitivity" mobile="/assets/portfolio-optimization/parameter-sensitivity_mobile" alt="Development-period net Sharpe and annualized turnover for six trade coefficients and five holding-rank cutoffs" version="8" %}
</div>

<p class="figure-caption"><strong>Figure 2: A broad return–turnover trade-off.</strong> Development-period net Sharpe and annual turnover. Points are schedule means; whiskers in the Sharpe panels span the observed schedules. Each group varies one setting while holding the other fixed; the chosen settings are highlighted.</p>

From 1 through 3, net Sharpe stays between 1.42 and 1.43 while turnover keeps
falling, from 34× to 27×. I choose 2.5 for the lower turnover within that
plateau; increasing the coefficient to 5 reduces return.

Rank cutoffs from 150 to 200 also give similar Sharpe, with modest turnover
savings. I use 175: moving to 200 saves less than another turn and worsens
mean maximum drawdown.

A 5 bp charge on 28.2 times annual turnover costs about 1.41% of strategy capital
per year on an arithmetic basis. The gap between gross and net geometric
returns includes the effect of compounding as well as these daily charges.

## Results after 2021

Table 3 starts on the first trading day of 2022. All three rules weaken relative
to their development results. The optimizer trails volatility scaling after
trading more. The trading controls change the result: net return is 8.0% versus
7.4%, Sharpe is 0.87 versus 0.78, and turnover falls below the baseline.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 3: The allocation rules in later history.</strong> January 2022–May 2026. Schedule averaging, geometric-return, drawdown, and cost conventions match Table 1.</caption>
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Sharpe</th><th>Drawdown loss</th><th>Annual turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Volatility-scaled</th><td>8.92%</td><td>7.38%</td><td>9.73%</td><td>0.78</td><td>8.65%</td><td>28.4×</td></tr>
    <tr><th scope="row">Optimizer</th><td>8.63%</td><td>6.47%</td><td>9.39%</td><td>0.71</td><td>9.41%</td><td>40.0×</td></tr>
    <tr class="selected-rule"><th scope="row">Optimizer + trading controls</th><td>9.33%</td><td>7.99%</td><td>9.32%</td><td>0.87</td><td>9.05%</td><td>24.6×</td></tr>
  </tbody>
</table>

The average hides a large calendar effect. The optimizer with trading controls has a
4.5-point spread in net return across the three schedules, compared with 1.5
points for the volatility-scaled rule. Two schedules favor the optimizer and
one is much weaker. Trading more slowly still helps on average, but the
result is much less consistent than during development.

Short-book losses remain substantial in December 2022–February 2023.
Across schedules, the long book contributes about +7.2
percentage points and the short book −16.4, measured as sums of daily
after-cost contributions. A market-only decomposition explains little of the
loss. That locates the problem in the short book, but identifying a shared
sector or style exposure requires a separate attribution study.

## Covariance and risk forecasts

The optimizer still has to work with imperfect risk estimates. I let
individual volatility react faster than correlations, repair the
pairwise correlation estimate, and shrink it toward the identity matrix:

$$
C_t(\rho)=(1-\rho)\widetilde R_t+\rho I.
$$

Here $$\widetilde R_t$$ is the repaired correlation estimate and $$I$$ has
ones on the diagonal and zeros elsewhere. At $$\rho=0$$ I retain the estimated
correlations; at $$\rho=1$$ I discard them. The value used in this comparison,
$$\rho=0.5$$, halves the off-diagonal correlations while keeping each stock's
own variance.

In [*Enhanced Portfolio Optimization*](https://doi.org/10.1080/0015198X.2020.1854543),
Pedersen, Babu, and Levine (2021, pp. 129–130) explain this through principal
components. Each component is a combination of volatility-standardized stock
returns. Its unit-length eigenvector $$q_j$$ gives the combination, and its
eigenvalue $$\lambda_j$$ measures its estimated variance. Leaving out the time
subscripts, positive shrinkage keeps the same eigenvectors and gives

$$
\begin{aligned}
\lambda_j(\rho)&=(1-\rho)\lambda_j+\rho,\\
C(\rho)^{-1}q_j&=\frac{q_j}{\lambda_j(\rho)}.
\end{aligned}
$$

Shrinkage moves the eigenvalues toward their average of one: small ones rise
and large ones fall. The second line shows why that matters: the inverse
divides each component by its estimated
variance. A favorable score in a low-variance direction can attract a large
allocation, but an underestimated variance amplifies errors in that score too.
I give up some of the strongest apparent diversification benefits to make
the allocation less sensitive to estimation error.

The shrunk correlation matrix becomes a covariance matrix through

$$
\begin{aligned}
\Sigma_t&=D_tC_t(\rho)D_t,\\
\Sigma_t^{-1}&=D_t^{-1}C_t(\rho)^{-1}D_t^{-1}.
\end{aligned}
$$

Here $$D_t$$ contains the annualized stock-volatility forecasts used in the
allocation, including their calibration. The second line
is the *precision matrix* in the unconstrained direction
$$w^\star\propto\Sigma^{-1}\alpha$$ introduced earlier: the rightmost
$$D_t^{-1}$$ divides expected returns by stock volatility, the inverse
correlation matrix adjusts their components, and the leftmost $$D_t^{-1}$$
converts back to position weights.

At full shrinkage, this gives expected return divided by stock variance.
Using my sizing scores $$\mu_{i,t}=s_{i,t}\widehat\sigma_{i,t}$$ in that same case, one volatility factor
cancels, giving weights proportional to $$s_{i,t}/\widehat\sigma_{i,t}$$.
That's the unconstrained case; portfolio limits and the trading penalty
still have to be handled together.

Factor models are another standard way to estimate covariance, combining
shared factor risk with stock-specific risk. They can also be used with
shrinkage in the same optimizer; the experiments here use empirical correlation
shrinkage. For an introduction, I particularly liked HRT's
[*Modeling Equities Returns: The Linear Case*](https://www.hudsonrivertrading.com/hrtbeat/modeling-equities-returns/).
I also recommend Giuseppe Paleologo's
[*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
especially Chapter 4 on multi-factor models.

Figure 3 shows why I keep some estimated correlation. I rebuild both joint
rules at each shrinkage value using development data. From 0.3 to 0.6,
forecast calibration, beta error, turnover, and Sharpe move relatively little.
At zero shrinkage, realized risk exceeds forecast by more. Full shrinkage
discards shared-risk information and also increases the forecast error.

<div class="research-figure rho-ladder-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/rho-ladder" mobile="/assets/portfolio-optimization/rho-ladder_mobile" alt="Four panels showing risk calibration, holding-period beta error, annual turnover, and net Sharpe across correlation shrinkage for both optimizers, with the 0.3 to 0.6 region shaded" version="14" %}
</div>

<p class="figure-caption"><strong>Figure 3: A broad middle region for correlation shrinkage.</strong> Both joint rules are rebuilt at each shrinkage value on development data. The four panels show risk calibration, mean absolute holding-period beta error, annual two-way turnover, and net Sharpe. The shaded band marks 0.3–0.6; the selected setting is 0.5. These historical comparisons informed the choice.</p>

Risk calibration takes the square root of mean realized holding-period
variance divided by mean variance forecast at execution. It uses complete
holding periods ending by December 2021; a ratio of one means realized and
forecast risk agree. At the selected shrinkage, realized volatility on this measure
is about 21% above forecast for the optimizer and 18% above for the version
with trading controls.

The full development results tell the same story: I asked for 7% forecast
volatility and got about 8.4% realized volatility. These forecasts already
include the 1.18 volatility multiplier in Table 4. Shrinkage helps, but I would
still need a new multiplier estimated on development data, then rerun the portfolios.
Changing covariance changes the
allocation decision too, including which constraints bind and how much the portfolio trades.

## Forecast beta versus realized beta

The beta limit applies to an estimate at each rebalance. Figure 4 follows
the beta of the portfolio's realized returns over a trailing year.
It reflects holdings and market moves throughout that year,
so it can stay far from zero even when new target weights satisfy the limit.

<div class="research-figure risk-beta-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/risk-calibration-and-beta" mobile="/assets/portfolio-optimization/risk-calibration-and-beta_mobile" alt="Trailing 252-day realized market beta for the volatility-scaled rule and both optimizers during development" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 4: Realized beta can persist after portfolio formation.</strong> Month-end trailing 252-day market beta, averaged across three schedules, September 1999–December 2021 after the return-window warm-up. The rebalance constraint uses a point-in-time estimate; the plotted beta measures the portfolio outcome over a trailing year.</p>

Joint sizing reduces the long departures from zero relative to volatility
scaling, but several episodes still last for months and reach roughly 0.2.
Estimation error is also present over individual holding periods.

I tested a 63-day beta window in matched portfolios. It removes the
persistent episodes, but with trading controls the later tail-error measure
remains at least as large and annualized net return falls by 0.6 percentage points,
beyond the 0.5-point tolerance I used. I keep the existing estimate.

## What joint sizing delivers

I keep joint sizing with both trading controls. In development, they preserve
almost all of the optimizer's gross return while cutting turnover by about a
third. The later advantage is smaller and depends more on the rebalance
schedule, but the combination still helps on average.

## Allocation settings

<table class="research-table settings-table">
  <caption><strong>Table 4: Allocation settings.</strong> The settings that determine selection, allocation and retention. Forecast variance is constrained jointly through the covariance matrix; long and short positions retain their respective signs.</caption>
  <thead><tr><th>Component</th><th>Setting</th></tr></thead>
  <tbody>
    <tr><th scope="row">Selection</th><td>75 long + 75 short; existing holdings eligible through rank 175 with the buffer</td></tr>
    <tr><th scope="row">Volatility-scaled baseline</th><td>Logistic signal shares with slope 2; 60-day volatility, 20% reference and 5% floor; 4% name cap; each book scales down above 100% gross</td></tr>
    <tr><th scope="row">Joint portfolio limits</th><td>7% forecast volatility; 200% gross; 4% per name; ±25% net; ±0.05 estimated beta</td></tr>
    <tr><th scope="row">Covariance estimate</th><td>21-day volatility; 756-day correlations of volatility-standardized returns (252 observations minimum); 50% shrinkage toward identity; volatility multiplied by 1.18</td></tr>
    <tr><th scope="row">Correlation preparation</th><td>Daily returns capped at ±30%; missing pairs use 0.50; matrix symmetrized, negative eigenvalues clipped and unit diagonal restored before shrinkage</td></tr>
    <tr><th scope="row">Sector limits</th><td>±20% net; 30% of either book</td></tr>
    <tr><th scope="row">Trading penalty</th><td><i>c</i> = 2.5 × 10<sup>−4</sup>, applied to the absolute change from drifted pre-trade weights</td></tr>
  </tbody>
</table>
