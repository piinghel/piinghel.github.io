---
layout: post
title: "From Volatility Scaling to a Constrained Optimizer"
date: 2026-08-29
last_modified_at: 2026-09-04
categories: ["Portfolio construction"]
article_label: Portfolio construction · Ridge allocation
permalink: /quants/2026/08/29/portfolio-optimization.html
---

<p class="article-summary">Volatility scaling sizes stocks one at a time, so portfolio exposures are whatever those separate decisions produce. A constrained optimizer sizes the whole book under one risk budget. Through 2021, gross return rises from 10.6% to 14.0% and Sharpe from 1.12 to 1.35, while turnover rises from 30× to 43×. The optimizer uses its risk budget to carry more gross exposure rather than lower realized volatility. Using the current book cuts turnover to 28× and lifts Sharpe to 1.43. The final evaluation is weaker, and realized beta remains the main problem.</p>

The [low-vol post](/quant/2024/12/15/low-volatility-factor.html) showed that
inverse-volatility sizing balances the two books but leaves gross, net, and beta
uncontrolled. The [Ridge post](/quants/2025/02/09/multiple-linear-regression.html)
found that learned rankings double turnover and left two tasks: size stocks
jointly and account for the positions already held. This post does both.

## Study design and the three rules

The data history begins in 1995. The common portfolio comparison starts in
September 1998, after the signals and risk estimates have enough history, and
runs through December 2021. I use September 2022 through May 2026 once, at the
end, as a final evaluation period. Earlier research has already looked at those
years, so I treat them as a short check rather than untouched evidence.

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
- The **optimizer using the current book** solves the same problem but starts
  from the positions already held and charges proposed changes in its
  objective.

Sharpe uses a zero risk-free rate. Turnover is annualized two-way weight change,
so 42× means purchases plus sales of 42 times capital per year. The development
period is also where I compare the covariance and trading settings. The final
evaluation stays outside those choices.

## Joint sizing buys more return

The volatility-scaled rule is easy to inspect. It sizes the long and short books
separately, however, and never sees covariance. Several modest positions can
therefore carry the same market or sector risk without the rule recognizing the
overlap.

The optimizer starts from the same ranking and sizes all selected stocks at
once. I first put each stock's risk-adjusted Ridge score in return units:

$$
\mu_{i,t}=s_{i,t}\widehat{\sigma}_{i,t}.
$$

It then chooses weights to maximize the portfolio score:

$$
\begin{aligned}
\max_{w_t}\quad & \mu_t^\top w_t \\
\text{subject to}\quad
& \text{forecast volatility}\leq\text{risk budget},\\
& \text{gross, net, and name weights within their limits},\\
& \text{long weights}\geq0,\quad\text{short weights}\leq0,\\
& \text{beta and sector exposures within their limits}.
\end{aligned}
$$

That compact list is the practical advantage. A volatility target, beta range,
or sector budget becomes one line in the allocation problem. Gross exposure is
then an output of the risk budget instead of a separate target that has to agree
with several other sizing rules. The exact limits are collected in Table A1.

Table 1 reports the development-period result. The optimizer raises gross
return by about three and a half percentage points and net Sharpe from 1.12 to
1.35. Realized volatility is about half a point higher and maximum drawdown is
unchanged. The optimizer used the forecast-risk budget to run more gross
exposure, rather than to make the realized portfolio safer. That is what the
constraint asked it to do.

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

The middle of Figure 2 is the useful region. From 0.3 to 0.6 shrinkage, forecast
calibration, beta error, turnover, and Sharpe move little. With no shrinkage,
realized volatility runs above forecast. Full shrinkage throws away too much
shared-risk information and misses by more. The broad middle matters more than
the exact point inside it.

<div class="research-figure rho-ladder-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/rho-ladder" alt="Development-period risk calibration, beta error, turnover, and net Sharpe across covariance-shrinkage values for both optimizers" version="5" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Development-period forecast calibration, beta error over the next holding period, annualized turnover, and net Sharpe across correlation-shrinkage values from zero to one. The shaded band marks 0.3 to 0.6; lines compare the optimizer with the version using the current book.</p>

The portfolio limits also act as guardrails. They bound how far one noisy score,
correlation, or beta estimate can move a name, sector, or the whole book. That
means the framework gives more control and asks for more care at the same time.

Realized volatility still runs about 15% above forecast. I treat that stable
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

Take a long stock whose rank slips from 60 to 110. The standard optimizer drops
it because only the top 75 enter the new selection. The version using the
current book may retain it while it remains inside the wider top 175. It begins
from the previous target weights after intervening price moves and before the
new trade.[^current-book]

If $$w_t^{\mathrm{pre}}$$ is that current book and $$c$$ is the trade
coefficient, the objective becomes

$$
\max_{w_t}\quad
\mu_t^\top w_t-c\lVert w_t-w_t^{\mathrm{pre}}\rVert_1,
$$

under the same portfolio constraints. The wider holding range gives the
optimizer more incumbents to choose from. The second term makes every change
pay for moving away from the current weights. The trade coefficient controls
that reluctance; realized P&L still uses the common cost assumption from the
study design.

Figure 3 checks both choices on the development period. The left column varies
the trade coefficient while holding the rank cutoff at 175. The right varies
the cutoff while holding the coefficient at 2.5. Points are the mean of the
three schedules and bars show their range.

<div class="research-figure parameter-sensitivity-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/parameter-sensitivity" alt="Development-period net Sharpe and annualized turnover for three trade coefficients and three holding-rank cutoffs" version="1" %}
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Local development-period sensitivity of net Sharpe (top) and annualized turnover (bottom). The selected settings are highlighted. Each column changes one setting and holds the other at its selected value; vertical bars span the three staggered schedules.</p>

The trade coefficient shows the expected trade-off. Moving from zero to 2.5
cuts turnover from about 40× to 28× while Sharpe rises from 1.37 to 1.43. A
coefficient of 5 cuts trading again but gives back some gross return. The rank
cutoff behaves similarly: 75 trades more, while 275 lowers turnover only
slightly without lifting Sharpe. I therefore use 2.5 and 175 as a local
compromise. Three points around each setting support local stability. A wider
search would be needed to claim a unique optimum.

Carryover on its own does little, which surprised me. It matters once the trade
term gives the optimizer a reason to keep an acceptable holding. Together the
two changes preserve nearly all gross return and lower turnover below the
volatility-scaled rule.

This distinction matters. Gross return barely changes. The optimizer using the
current book reaches nearly the same portfolio with fewer replacements. The
cost saving is the gain.

I read this as evidence that many marginal replacements add little at the
portfolio level. A matched study of stocks kept and replaced would tell us how
much comes from persistent Ridge ranks and how much comes from offsetting risk
changes.

## Realized beta remains the main problem

The optimizer keeps its beta estimate inside the stated range at each
rebalance. Realized beta can still drift as prices and exposures change over
the holding period. Figure 4 shows that this happens in persistent episodes.

<div class="research-figure risk-beta-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-optimization/risk-calibration-and-beta" alt="Development-period trailing realized beta for the volatility-scaled rule and both optimizers" version="9" %}
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Monthly trailing one-year realized market beta for all three rules, averaged across the staggered schedules, September 1998–December 2021. The constraint uses a point-in-time estimate at each rebalance, while this chart measures the portfolio outcome over a trailing year.</p>

The optimizer reduces the long departures from zero relative to volatility
scaling, but several episodes still last for months and reach roughly 0.3. The
chosen portfolio remains inside its point-in-time limit. This points to the beta
estimate used to choose stocks and weights.

A shorter beta window removes those persistent episodes in the saved test, but
it also reduces later net return by 0.6 percentage points. That exceeds the
0.5-point tolerance chosen before the comparison, so I leave the stock
constraint alone. The next test is a costed benchmark overlay that separates
beta management from stock selection.

Capacity is the other practical limit. Turnover falls to 28×, which is still
high once market impact, borrow, and the stocks near the edge of the universe
matter. A flat 5-basis-point charge gives a consistent comparison; a capacity
study needs trade size and liquidity.

## The final period makes the choice less clear

Table 2 moves to September 2022 through May 2026. All three rules weaken. The
optimizer trails volatility scaling. Using the current book recovers most of
that gap and cuts turnover to 25×. Its Sharpe of 0.89 is close to the
volatility-scaled rule's 0.90. The period spans less than four years, so I give
this block less weight than the development result.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Portfolio rule</th><th>Gross return</th><th>Net return</th><th>Net vol.</th><th>Net Sharpe</th><th>Max DD</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">B1 · Vol-scaled rule</th><td data-label="Gross return">10.02%</td><td data-label="Net return">8.42%</td><td data-label="Net volatility">9.46%</td><td data-label="Net Sharpe">0.90</td><td data-label="Max drawdown">8.65%</td><td data-label="Turnover">29.06×</td></tr>
    <tr><th scope="row">B2 · Optimizer</th><td data-label="Gross return">9.02%</td><td data-label="Net return">6.78%</td><td data-label="Net volatility">9.50%</td><td data-label="Net Sharpe">0.74</td><td data-label="Max drawdown">9.41%</td><td data-label="Turnover">41.18×</td></tr>
    <tr><th scope="row"><strong>B3 · Optimizer using current book</strong></th><td data-label="Gross return"><strong>9.70%</strong></td><td data-label="Net return"><strong>8.33%</strong></td><td data-label="Net volatility"><strong>9.43%</strong></td><td data-label="Net Sharpe"><strong>0.89</strong></td><td data-label="Max drawdown"><strong>9.05%</strong></td><td data-label="Turnover"><strong>24.99×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Final evaluation from September 2022 through May 2026. Metrics are means of three staggered schedules and use the same execution and cost assumptions as Table 1.</p>

I still move from volatility scaling to the constrained optimizer, and I use
the version that accounts for the current book. It sizes shared risk jointly,
makes exposure limits explicit, and avoids many marginal replacements. In
return, it demands careful covariance estimates, sensible guardrails, and a
clear separation between development choices and later evidence.

The comparison leaves three open questions. A component test could isolate
which part of joint sizing drives the development gain. A trade-level study
could explain which replacements the current-book rule avoids. A liquidity and
borrow model could test whether the remaining turnover survives at scale.

The next portfolio test is the costed benchmark overlay. Before that, I will
recalibrate the volatility multiplier on the development period and rerun the
three rules so the forecast target matches the risk the portfolio realizes.

## Appendix: parameters and two implementation notes

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Component</th><th>Setting</th><th>Why</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Initial selection</th><td data-label="Setting">75 long + 75 short</td><td data-label="Why">Anchors each rule to the same Ridge tails.</td></tr>
    <tr><th scope="row">Vol-scaled rule</th><td data-label="Setting"><span><i>γ</i> = 2; 60-day volatility; 20% target and fallback; 5% floor; 10% signal-share cap; 4% name cap; 6× multiplier cap; 100% gross per book</span></td><td data-label="Why">Preserves the sizing rule from the low-volatility study.</td></tr>
    <tr><th scope="row">Covariance</th><td data-label="Setting"><span>21-day volatility; 756-day correlation; 252-day start; 0.50 missing-pair fallback; <i>ρ</i> = 0.50; daily returns capped at ±30%</span></td><td data-label="Why">Lets volatility react faster than correlation while shrinking noisy shared-risk estimates.</td></tr>
    <tr><th scope="row">Portfolio limits</th><td data-label="Setting">7% volatility; 200% gross; 4% per name; ±25% net; ±0.05 beta</td><td data-label="Why">Expresses the intended portfolio risk and exposure bounds.</td></tr>
    <tr><th scope="row">Beta estimate</th><td data-label="Setting">756-day correlation; 252-day minimum; 21-day volatility; stock beta capped at ±4</td><td data-label="Why">Combines a stable correlation estimate with faster-moving volatility.</td></tr>
    <tr><th scope="row">Sector limits</th><td data-label="Setting">±20% net; 30% of either book</td><td data-label="Why">Keeps one sector from dominating the net portfolio or either book.</td></tr>
    <tr><th scope="row">Current-book settings</th><td data-label="Setting">2.5 bp trade coefficient; existing holdings may remain to rank 175</td><td data-label="Why">The local development sweep balances turnover, Sharpe, and drawdown.</td></tr>
    <tr><th scope="row">Realized trading cost</th><td data-label="Setting">5 bp per dollar bought or sold</td><td data-label="Why">Uses the same cost assumption as the earlier posts in the series.</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A1:</strong> Rule settings and their role in the comparison. Exact values stay here unless they carry the argument in the main text.</p>

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
uses the inherited 0.50 fallback; in a long–short book that choice can be more
or less conservative depending on the signs of the positions. I symmetrize the
pairwise matrix, clip negative eigenvalues, and restore its unit diagonal before
shrinkage. The covariance is multiplied by $$\kappa^2$$, with
$$\kappa=1.18$$ inherited from the development-period risk calibration. The
recalibration proposed above updates this number from forecast error rather than
portfolio return.

[^schedules]: The [tranching study](/quants/2025/05/10/rebalancing-luck.html) introduced these staggered schedules as a check on rebalance-date luck.
[^current-book]: The current book is the previous target portfolio after price moves and before the next rebalance. An incumbent may remain in the choice set while its rank stays inside 175.
