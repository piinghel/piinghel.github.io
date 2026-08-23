---
layout: post
title: "The Low-Volatility Factor: From Stock Sorts to Portfolio Risk"
date: 2024-12-15
last_modified_at: 2026-08-23
categories: ["Low volatility"]
article_label: Low-volatility · portfolio construction
permalink: /quant/2024/12/15/low-volatility-factor.html
github_repositories:
  - label: Research code on GitHub
    url: https://github.com/piinghel/low-vol-to-portfolio
---

<p class="article-summary"><strong>TL;DR:</strong> This article holds the long and short stock selections fixed and compares equal weighting with inverse-volatility weighting. Equal weighting delivers a 2.4% after-cost arithmetic return, with 33.4% volatility and an 87.1% maximum drawdown. Inverse-volatility weighting delivers a 7.1% return, with 9.8% volatility and a 38.0% drawdown. The two rules also produce different exposure, beta, and turnover.</p>

After ranking the stocks, I compare equal-dollar and inverse-volatility position
sizes. Under equal weighting, the high-volatility stocks contribute most of the
portfolio risk.

Both methods use the same long and short baskets. Only the position sizes change.
I track return, volatility, drawdown, gross and net exposure, beta, and turnover.

The evidence for low volatility is well established. [Blitz and van
Vliet](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865) document it
across the U.S., Europe, and Japan; [Frazzini and
Pedersen](https://www.nber.org/papers/w16601) connect it to leverage constraints.
I focus on the portfolio decision that follows the ranking.

## The tradable universe

Both sizing rules use the same point-in-time Russell 1000 universe and daily
prices from July 1995 through 27 May 2026. Stocks must trade above $5 on an
unadjusted basis and have enough history for the selection signal, sizing
volatility, and beta diagnostic. I also require a beta estimate so that the beta
comparison covers the same stocks. The ranking and sizing formulas use
volatility alone. This leaves 857–1,015 eligible stocks at each rebalance, with a
median of 973.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/eligible_universe_mobile.png?v=2">
    <img src="/assets/2024-12-15-low-volatility-factor/eligible_universe.png?v=2" alt="Number of eligible Russell 1000 stocks at each rebalance date" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Eligible stocks after the price and data-availability filters.</p>

Portfolio breadth stays similar through time, so changes in the results come
mainly from position sizing.

## Measuring and ranking volatility

For each stock $$i$$ on signal date $$t$$, I average annualised realised volatility over the past 21, 63, and 126 trading days. This average is the stock's volatility score:

$$
\begin{aligned}
v_{i,t}
&= \frac{1}{3}\left(
\widehat{\sigma}_{i,t}^{(21)}
+ \widehat{\sigma}_{i,t}^{(63)}
+ \widehat{\sigma}_{i,t}^{(126)}
\right).
\end{aligned}
$$

In the equation, $$\widehat{\sigma}_{i,t}^{(h)}$$ is the annualised volatility estimated over the last $$h$$ trading days. The one-, three-, and six-month windows balance responsiveness and stability. Before ranking, I bound the score at 5%–200%; observations outside those limits tie at the boundary.

At each rebalance I split the ranked stocks into ten fixed groups of roughly
equal size. Deciles 1 and 10 each contain roughly 100 stocks. Decile 1 is the
long leg and decile 10 is the short leg; the middle deciles show how the results
change across the ranking.

<div class="low-vol-figure decile-profile-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/decile_profile_mobile.png?v=3">
    <img src="/assets/2024-12-15-low-volatility-factor/decile_profile.png?v=3" alt="Sharpe ratio, geometric return, and volatility across volatility deciles" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Sharpe ratio, geometric return, and volatility by volatility decile before costs.</p>

Geometric return stays positive across all ten deciles, while volatility rises
sharply and Sharpe deteriorates. In the highest-volatility decile, a 7.6%
arithmetic return compounds to about 0.3% a year. The gap comes from variance
drag.
The remaining tests hold the two deciles fixed and change their position sizes.

## Equal weights

The benchmark assigns the same dollar weight to every stock. The long and short
baskets each contain roughly one hundred liquid Russell 1000 names, which makes
1/N a reasonable reference without adding a size tilt. Decile 1 forms the long
leg and decile 10 the short leg. The short leg has about 38% realised volatility
and a beta of 1.63; the long leg has about 12% volatility and a beta of 0.55.

<div class="low-vol-figure naive-leg-risk-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile.png?v=2">
    <img src="/assets/2024-12-15-low-volatility-factor/naive_leg_risk.png?v=2" alt="Realized volatility and average beta of the low- and high-volatility deciles" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Risk of the two equal-weight legs before costs.</p>

The high-volatility basket carries more than three times the realised volatility
and nearly three times the estimated beta of the low-volatility basket.
Inverse-volatility sizing keeps these stocks and changes their position sizes.

## Volatility scaling

Position sizing uses a separate 60-day volatility estimate with a 5% floor.
Within each leg, every stock starts at $1/N$. Its weight is then multiplied by
20% divided by estimated volatility. A stock at 10% volatility receives twice
the preliminary weight of one at 20%. The position cap is 4%, and a leg above
100% gross exposure is scaled down proportionally. The portfolio rebalances
every three weeks and trades at the next market close.

For leg $$\ell\in\{L,H\}$$, selected-stock set $$\mathcal S_{\ell,t}$$, and stock count $$N_{\ell,t}=\lvert\mathcal S_{\ell,t}\rvert$$:

$$
\begin{aligned}
a_{i,\ell,t}^{\mathrm{pre}}
&=\frac{1}{N_{\ell,t}}
\times \frac{0.20}{\widehat{\sigma}_{i,t}^{(60)}}, \\
a_{i,\ell,t}
&=\min\left(a_{i,\ell,t}^{\mathrm{pre}},\;0.04\right).
\end{aligned}
$$

Here, 0.20 is the reference volatility. The 4% cap limits concentration. If the preliminary weights in a leg add up to more than 100% gross, I scale the whole leg down in proportion:

$$
\begin{aligned}
g_{\ell,t}^{\mathrm{pre}}
&=\sum_{j\in\mathcal S_{\ell,t}}a_{j,\ell,t}, \\
c_{\ell,t}
&=\min\left(1,\frac{1}{g_{\ell,t}^{\mathrm{pre}}}\right).
\end{aligned}
$$

The final weight is positive for a stock in the long set and negative for one in the short set:

$$
w_{i,t}
=
\begin{cases}
+a_{i,L,t}\times c_{L,t}, & i\in\mathcal S_{L,t}, \\
-a_{i,H,t}\times c_{H,t}, & i\in\mathcal S_{H,t}.
\end{cases}
$$

The 100% leg limit is a ceiling. A volatile short basket can therefore shrink to
30% or 40% of portfolio value. Portfolio risk depends on the final weights and
the realised correlations between stocks. A full risk model would estimate those
correlations and size the positions jointly.

## Resulting exposures

Inverse-volatility sizing shifts capital towards the low-volatility long book and leaves a smaller high-volatility short book.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/target_exposures_mobile.png?v=2">
    <img src="/assets/2024-12-15-low-volatility-factor/target_exposures.png?v=2" alt="Realized long gross, short gross, and net stock exposure through time" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Realized long gross, short gross, and net stock exposure between rebalances.</p>

Across the sample, the low-volatility long averages 97.2% gross and the high-volatility short 34.0%. Total stock gross is 131.1%, leaving +63.2% net stock exposure. These daily floating weights include the drift created by price moves between rebalances.

Scaling brings realised volatility to 10.5% for the long leg and 10.0% for the
short leg, compared with 11.9% and 37.9% under equal weights. This balance comes
from stock-level sizing; total portfolio risk remains free to move with the
correlations.

Net exposure measures signed capital, while beta measures market sensitivity.
Let $$E_t^{\mathrm{net}}$$ be signed stock exposure as a fraction of portfolio
value, and let $$\widehat{\beta}_{i,t}$$ be stock $$i$$'s estimated market beta.
Then

$$
\begin{aligned}
E_t^{\mathrm{net}} &= \sum_i w_{i,t}, \\
\widehat{\beta}_{p,t} &= \sum_i w_{i,t}\widehat{\beta}_{i,t}.
\end{aligned}
$$

The short book carries less capital. Its stocks have much higher market betas,
which offset most of the long book's beta. The full-sample average ex-ante beta is
−0.014 and realised beta is −0.001. Portfolio beta combines each stock's weight
with its estimated beta. The 100% leg ceiling constrains how far either side can
scale, while the stocks inside the legs determine the sign.

Stock-level volatility sizing leaves portfolio beta free to vary. Dollar exposure
and market exposure can therefore point in different directions. An index-futures
overlay could target beta while leaving the stock ranking intact; that would be a
separate allocation decision.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/beta_diagnostic_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/beta_diagnostic.png" alt="Estimated and rolling realized beta of the volatility-scaled portfolio" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Ex-ante and rolling realized beta of the scaled portfolio.</p>

## Performance, costs, and drawdowns

I charge 5 basis points per dollar traded, including the first portfolio
formation, as a rough approximation of stock-trading costs. At 10.4 times annual
turnover, that reduces the scaled portfolio's return by about 0.52 percentage
points a year.

The estimate covers stock-trading costs. A fuller implementation estimate would add borrow, financing, market impact, and taxes. Unused capacity earns zero. Returns are annualized arithmetic means. Volatility, Sharpe, and drawdown use returns after the stated trading cost. Sharpe is annualized return divided by volatility, with a zero cash rate.

<table class="research-table comparison-table performance-table">
  <thead>
    <tr>
      <th>Performance metric</th>
      <th>Equal-weight reference</th>
      <th>Volatility-scaled</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Arithmetic return, 0 bp</th>
      <td data-label="Equal-weight reference">3.2%</td>
      <td data-label="Volatility-scaled">7.6%</td>
    </tr>
    <tr>
      <th scope="row">Arithmetic return, 5 bp</th>
      <td data-label="Equal-weight reference">2.4%</td>
      <td data-label="Volatility-scaled">7.1%</td>
    </tr>
    <tr>
      <th scope="row">Geometric return, 5 bp</th>
      <td data-label="Equal-weight reference">−3.1%</td>
      <td data-label="Volatility-scaled">6.9%</td>
    </tr>
    <tr>
      <th scope="row">Volatility, 5 bp</th>
      <td data-label="Equal-weight reference">33.4%</td>
      <td data-label="Volatility-scaled">9.8%</td>
    </tr>
    <tr>
      <th scope="row">Sharpe, 5 bp</th>
      <td data-label="Equal-weight reference">0.07</td>
      <td data-label="Volatility-scaled">0.73</td>
    </tr>
    <tr>
      <th scope="row">Max drawdown, 5 bp</th>
      <td data-label="Equal-weight reference">−87.1%</td>
      <td data-label="Volatility-scaled">−38.0%</td>
    </tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Full-sample performance with three-week rebalancing.</p>

<table class="research-table comparison-table exposure-table">
  <thead>
    <tr>
      <th>Exposure or trading metric</th>
      <th>Equal-weight reference</th>
      <th>Volatility-scaled</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Average stock gross</th>
      <td data-label="Equal-weight reference">2.00</td>
      <td data-label="Volatility-scaled">1.31</td>
    </tr>
    <tr>
      <th scope="row">Average stock net</th>
      <td data-label="Equal-weight reference">0.00</td>
      <td data-label="Volatility-scaled">0.63</td>
    </tr>
    <tr>
      <th scope="row">Realized beta</th>
      <td data-label="Equal-weight reference">−1.12</td>
      <td data-label="Volatility-scaled">−0.001</td>
    </tr>
    <tr>
      <th scope="row">Annualized turnover</th>
      <td data-label="Equal-weight reference">14.4× equity</td>
      <td data-label="Volatility-scaled">10.4× equity</td>
    </tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Full-sample exposure and trading diagnostics.</p>

The volatility-scaled implementation produces a 7.1% annualised arithmetic
return after costs, 9.8% volatility, and a 0.73 Sharpe. Its cost drag is about 0.5
percentage points a year. Total portfolio volatility falls by 23.6 percentage
points, from 33.4% to 9.8%. The comparison includes the lower gross exposure,
positive net exposure, and different beta produced by inverse-volatility sizing.

<div class="low-vol-figure performance-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile.png?v=5">
    <img src="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns.png?v=5" alt="Growth of one dollar on a logarithmic scale and drawdowns for the equal-weight and volatility-scaled long-short portfolios" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 6:</strong> After-cost growth of $1 on a log scale, with drawdowns below.</p>

The equal-weight portfolio earns a positive 2.4% arithmetic return after costs,
while repeated large losses leave compounded wealth at 0.38 times its starting
value. Repeated large losses account for the gap between arithmetic and
compounded returns. The volatility-scaled portfolio compounds
at 6.9% a year and finishes at 7.78 times its starting value. Its path includes
long flat periods and a 38% maximum drawdown.

Matched tests at equal gross exposure, beta, and realised risk would show how much
of the result comes from each mechanism. I held the signal windows, 60-day sizing
window, 20% reference volatility, 4% cap, three-week rebalance interval, and leg
ceiling fixed throughout.

The 5 bp cost assumption approximates routine stock trading. Borrow fees,
financing, market impact, and taxes would lower implementable returns, especially
on the short side. Both portfolios allow beta to float. A financed,
capacity-aware implementation would include those costs and constraints.

Missing prices are carried forward, and a security that leaves the covered data closes at its last observed value. This convention can make losses look too mild when the final stale price precedes an adverse delisting. Persisting trailing coverage and rerunning the test with a conservative delisting return would show how much that data choice matters.

## When the short book rallies

The latest example runs from 3 April 2025 through 27 May 2026. The scaled
portfolio lost 12.1% before costs and 12.6% after costs, while the Russell 1000
gained 38.5%. The long book contributed +4.2 percentage points; the short book
contributed −16.3. Trading costs added roughly 0.5 points of loss. Average net
stock exposure was +68.6%, yet ex-ante beta was −0.12. The smaller short book
held stocks with much higher betas. Those stocks led the rally and drove the
loss.

The larger historical example is the dot-com boom. From 8 October 1998 to 9 March 2000, the scaled portfolio lost 38.0% after costs as the Russell 1000 gained 52.2%. Average net exposure was +72.0%, while ex-ante beta was −0.07 and realised beta −0.06. Before costs, the long book contributed −10.4 percentage points and the short book −27.1. Trading costs added 0.4 points.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/regime_comparison_mobile.png?v=3">
    <img src="/assets/2024-12-15-low-volatility-factor/regime_comparison.png?v=3" alt="Grouped bars compare long- and short-book contributions during the dot-com and recent high-volatility rallies" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 7:</strong> Gross long- and short-book contributions during two high-volatility rallies. Values are percentage points on the strategy capital base.</p>

Both episodes show the same mechanism: the short book accounts for most of the
loss. The dot-com episode is larger; the recent episode ends with the sample in
May 2026.

## Conclusion

Equal dollars allow volatile names to dominate the portfolio; inverse-volatility
sizing brings the leg risks closer while holding stock selection constant. In
this sample, after-cost geometric return moves from −3.1% to 6.9%, volatility
from 33.4% to 9.8%, maximum drawdown from −87.1% to −38.0%, and turnover from
14.4× to 10.4× equity. These figures describe the complete scaled implementation
and its combined exposure changes.

The portfolio can be long dollars and short the market in beta terms. That
exposure hurt during the dot-com boom and the 2025–2026 rally.

A covariance estimate would model how positions move together and size the
portfolio as a whole. Explicit constraints could control beta, net exposure,
gross exposure, and concentration. A turnover penalty could start from current
holdings and trade only when the expected risk improvement justifies the cost. I
would test that model against matched versions of the present rule at equal gross
exposure, beta, and realised risk, then repeat the comparison with conservative
stale-price and delisting assumptions.
