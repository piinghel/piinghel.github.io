---
layout: post
title: "The Low-Volatility Factor: Portfolio Construction Matters"
date: 2024-12-15
last_modified_at: 2026-08-17
categories: [Quant]
---

Low-risk equities have historically delivered stronger returns per unit of risk than high-risk peers. [Blitz and van Vliet](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865) document the effect across the US, Europe, and Japan. One explanation is leverage constraints: investors seeking more market exposure per dollar may prefer high-beta securities to levering a higher-Sharpe, low-risk portfolio. [Frazzini and Pedersen](https://www.nber.org/papers/w16601) formalize that mechanism in betting against beta.

This article asks a narrower question: how should a simple low-minus-high volatility signal be translated into a portfolio? I hold stock selection fixed, show equal stock weights only as a reference, and use stock-level volatility scaling as the main implementation. The goal is a simple, pragmatic portfolio whose risks are deliberate and measurable.

## What exactly are we sorting?

The backtest runs from July 1995 through October 2024 using historical point-in-time Russell 1000 constituents. It applies a $5 minimum unadjusted-price filter. After common-data checks, the eligible universe contains 840–1,017 stocks per week, with a median of 971; both portfolio implementations use the same cross-section.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/eligible_universe_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/eligible_universe.png" alt="Number of eligible point-in-time Russell 1000 constituents at each weekly signal date" loading="lazy">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Number of eligible point-in-time Russell 1000 constituents at each weekly signal date after the $5 price filter and data-availability checks. The observed range is 840–1,017 stocks and the median is 971.</p>

For stock $$i$$ on signal date $$t$$, let $$\widehat{\sigma}_{i,t}^{(h)}$$ denote annualized realized volatility over the trailing $$h\in\{21,63,126\}$$ trading days. The selection signal is their average:

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

The one-, three-, and six-month horizons balance recent changes in risk against stability. I clip the average to 5%–200% before ranking so pathological observations cannot control the sort.

I divide the ranked stocks into ten deterministic, approximately equal-sized groups. Decile 1 contains the lowest-volatility stocks and decile 10 the highest. The strategy trades only those extremes; the middle deciles show the broader cross-sectional shape.

<div class="low-vol-figure decile-profile-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/decile_profile_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/decile_profile.png" alt="Geometric return, volatility, and Sharpe ratio across volatility deciles">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Long-only geometric return, realized volatility, and arithmetic-return Sharpe ratio by volatility decile, before transaction costs. Decile 1 contains the lowest-volatility stocks.</p>

Realized portfolio volatility rises steadily across the sort. Geometric returns vary across the middle deciles, while Sharpe ratios generally deteriorate as volatility rises; the weakest risk-adjusted performance sits in the highest-volatility group. That is the signal evidence. The next question is how to size the long and short extremes.

Stock P&L uses the vendor’s total-return field. Off-calendar source rows are compounded before sampling onto the Russell 1000 market calendar. Between rebalances I hold fixed quantities, and turnover is measured from the resulting drifted holdings to the next targets.

Table 1 records the implementation details.

<table class="research-table specification-table">
  <thead>
    <tr><th>Component</th><th>Specification</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Sample</th><td>July 1995–October 2024</td></tr>
    <tr><th scope="row">Universe</th><td>Point-in-time Russell 1000 constituents; unadjusted price ≥ $5</td></tr>
    <tr><th scope="row">Selection signal</th><td>Mean annualized realized volatility over 21, 63, and 126 trading days</td></tr>
    <tr><th scope="row">Cross-sectional portfolio</th><td>Ten equal-count deciles; long decile 1, short decile 10</td></tr>
    <tr><th scope="row">Stock sizing</th><td>60-day volatility floored at 5%; 20% per-stock volatility target; 4% position cap; 100% leg-gross cap</td></tr>
    <tr><th scope="row">Beta diagnostic</th><td>252-day estimate; minimum 126 observations; clipped to [−4, 4]</td></tr>
    <tr><th scope="row">Cost sensitivity</th><td>5 bps per dollar of absolute equity notional traded</td></tr>
  </tbody>
</table>

<p class="figure-caption"><strong>Table 1:</strong> Backtest specification.</p>

## A simple equal-weight reference

As a reference, I first show equal stock weights. This is deliberately naive, and its weakness is obvious by construction: the two baskets are drawn from opposite ends of the volatility distribution. The low-volatility basket realizes 12.1% volatility versus 39.8% for the high-volatility basket, and its average ex-ante stock beta is lower, 0.56 versus 1.63. Equal weighting is therefore useful as a reference but problematic as the main implementation.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/naive_leg_risk.png" alt="Realized volatility and average beta of the low- and high-volatility deciles" loading="lazy">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Annualized realized volatility and average ex-ante beta of the equal-weight low- and high-volatility baskets, before transaction costs.</p>

Those differences are exactly what the signal construction implies. The main implementation therefore allocates stock notional using each name's standalone volatility.

## The main implementation: stock-level volatility scaling

I replace equal stock weights with a simple inverse-volatility rule. The selected names do not change: the 21/63/126-day average decides *which* stocks enter, while a separate 60-day volatility estimate, floored at 5%, decides *how much* to hold. Correlations are deliberately outside this sizing rule.

For a leg $$\ell\in\{L,H\}$$, let $$\mathcal S_{\ell,t}$$ be its selected-stock set at signal date $$t$$, and let $$N_{\ell,t}=\lvert\mathcal S_{\ell,t}\rvert$$. Expressing volatility and weights as decimals, the preliminary absolute weight for stock $$i\in\mathcal S_{\ell,t}$$ is

$$
\begin{aligned}
a_{i,\ell,t}
&=\min\left(
\frac{0.20}{N_{\ell,t}\widehat{\sigma}_{i,t}^{(60)}},
\;0.04
\right).
\end{aligned}
$$

Here, 0.20 is a 20% annualized per-stock volatility target used for sizing, not a target for the realized portfolio volatility. It gives lower-volatility stocks more notional and higher-volatility stocks less, while the 4% cap limits concentration. If preliminary weights in a leg exceed 100% gross, I scale them down proportionally:

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

The 100% leg limit is a cap, not a normalization target. A volatile short basket is allowed to shrink to 30% or 40% of NAV; forcing it back to 100% would undo the risk adjustment. This is stock-level standalone-risk scaling, not covariance optimization or portfolio-level volatility targeting.

## The resulting exposure profile

The high-volatility short book naturally uses less notional because its constituents receive smaller inverse-volatility weights.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/stock_exposure_profile_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/stock_exposure_profile.png" alt="Long gross, short gross, and net stock exposure through time" loading="lazy">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Weekly target long gross, short gross, and net stock exposure after stock-level volatility scaling.</p>

Across the sample, the low-volatility long averages 97.0% gross and the high-volatility short 34.2%. Total stock gross is 131.2% and net stock exposure is +62.8%. These are consequences of the sizing rule.

Net stock exposure and market beta are different diagnostics. Let $$E_t^{\mathrm{net}}$$ be signed stock notional as a fraction of NAV, and let $$\widehat{\beta}_{i,t}$$ be stock $$i$$'s estimated market beta. Then

$$
\begin{aligned}
E_t^{\mathrm{net}} &= \sum_i w_{i,t}, \\
\widehat{\beta}_{p,t} &= \sum_i w_{i,t}\widehat{\beta}_{i,t}.
\end{aligned}
$$

The smaller short offsets much of the larger long in beta terms because its constituents carry much higher market betas. I therefore assess beta separately from the stock-level sizing rule.

## Managing market beta separately

I estimate stock beta from a rolling 252-day covariance with the Russell 1000 price-index return, requiring 126 observations and clipping estimates to [−4, 4]. A rolling return regression provides a separate realized-beta diagnostic.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/beta_diagnostic_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/beta_diagnostic.png" alt="Ex-ante and rolling realized beta of the volatility-scaled portfolio" loading="lazy">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Aggregated ex-ante stock beta and rolling 252-day realized beta for the volatility-scaled portfolio. The shaded region marks beta between −0.1 and +0.1.</p>

Average signed ex-ante beta and full-sample realized beta are both approximately −0.010. The average absolute weekly estimate is larger at 0.104, but its sign changes, so an always-on hedge is unnecessary here. In a live process I would construct the stock portfolio first, then use an index future only when residual beta leaves a predefined band:

$$
N_{\mathrm{future},t}\approx-\widehat{\beta}_{p,t}\times NAV_t.
$$

Stock selection and sizing set the equity portfolio; the overlay manages market beta as a separate decision.

## Performance, costs, and drawdowns

The tables separate performance from the exposures that produce it. I charge 5 basis points per dollar of equity notional traded, including initial formation. This is a small comparative sensitivity, not a live-performance estimate. The return columns are annualized arithmetic means; volatility, Sharpe, and drawdown use returns after that cost.

<table class="research-table comparison-table performance-table">
  <thead>
    <tr>
      <th>Performance metric</th>
      <th>Reference</th>
      <th>Volatility-scaled</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Return, 0 bp</th>
      <td data-label="Reference">2.9%</td>
      <td data-label="Volatility-scaled">7.9%</td>
    </tr>
    <tr>
      <th scope="row">Return, 5 bp</th>
      <td data-label="Reference">1.4%</td>
      <td data-label="Volatility-scaled">7.0%</td>
    </tr>
    <tr>
      <th scope="row">Volatility, 5 bp</th>
      <td data-label="Reference">34.9%</td>
      <td data-label="Volatility-scaled">9.6%</td>
    </tr>
    <tr>
      <th scope="row">Sharpe, 5 bp</th>
      <td data-label="Reference">0.04</td>
      <td data-label="Volatility-scaled">0.72</td>
    </tr>
    <tr>
      <th scope="row">Max drawdown, 5 bp</th>
      <td data-label="Reference">−89.5%</td>
      <td data-label="Volatility-scaled">−41.0%</td>
    </tr>
  </tbody>
</table>

<p class="figure-caption"><strong>Table 2:</strong> Performance from July 1995 through October 2024. Volatility uses 252 trading days and Sharpe assumes a zero risk-free rate.</p>

<table class="research-table comparison-table exposure-table">
  <thead>
    <tr>
      <th>Exposure or trading metric</th>
      <th>Reference</th>
      <th>Volatility-scaled</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Average stock gross</th>
      <td data-label="Reference">2.01</td>
      <td data-label="Volatility-scaled">1.31</td>
    </tr>
    <tr>
      <th scope="row">Average stock net</th>
      <td data-label="Reference">0.00</td>
      <td data-label="Volatility-scaled">0.63</td>
    </tr>
    <tr>
      <th scope="row">Realized beta</th>
      <td data-label="Reference">−1.18</td>
      <td data-label="Volatility-scaled">−0.01</td>
    </tr>
    <tr>
      <th scope="row">Annualized turnover</th>
      <td data-label="Reference">31.4× equity</td>
      <td data-label="Volatility-scaled">19.3× equity</td>
    </tr>
  </tbody>
</table>

<p class="figure-caption"><strong>Table 3:</strong> Daily-average stock exposures, full-sample regression beta of gross strategy returns on the Russell 1000 price-index return, and annualized turnover.</p>

The volatility-scaled implementation produces a 7.0% annualized arithmetic return after the 5 bp sensitivity, 9.6% volatility, and a 0.72 Sharpe. Its cost drag is roughly 1.0 percentage point a year.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/cumulative_performance_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/cumulative_performance.png" alt="Cumulative wealth of the equal-weight and volatility-scaled implementations" loading="lazy">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 6:</strong> Cumulative wealth under the 5 bp transaction-cost sensitivity, shown on a logarithmic scale.</p>

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/drawdowns_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/drawdowns.png" alt="Drawdowns of the equal-weight and volatility-scaled implementations" loading="lazy">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 7:</strong> Drawdowns under the 5 bp transaction-cost sensitivity for both portfolio implementations.</p>

## What broke during the 41% drawdown?

The worst drawdown is not a generic equity sell-off. The scaled portfolio peaks on 8 October 1998 and reaches its trough on 9 March 2000: a 41.0% loss over 357 trading days, during which the Russell 1000 gains 52.2%. It does not regain the earlier high until 15 August 2001.

An exact peak-NAV attribution makes the mechanism clear. The low-volatility long contributes −12.0 percentage points, the high-volatility short −28.2 points, and trading costs −0.85 points. As a separate before-cost diagnostic, the fully invested high-volatility basket gains 334.2% over the same dates while the low-volatility basket loses 16.3%. The dominant failure is therefore the short book's violent rally during the late-1990s internet-bubble regime, compounded by weakness in the long book.

Market beta does not explain it. During the drawdown, average ex-ante beta is −0.074 and realized beta is −0.064; the average stock books are 95.6% long and 23.5% short. Near-zero beta insulated the portfolio from broad market direction, not from a sustained reversal in the characteristic spread. Stock-level risk scaling limits individual standalone risk, but it cannot prevent correlated losses across both books as a regime persists. The available artifacts do not contain point-in-time sector or style labels, so they cannot establish how much of the episode was specifically technology, growth, or momentum exposure.

## How much of this is really the factor?

Figure 2 supports the signal claim: low-volatility stocks exhibit better risk-adjusted performance than high-volatility stocks. The 0.72 long/short Sharpe is a portfolio result, not newly discovered alpha. Selection is unchanged; weights, exposure, beta, turnover, and concentration of risk all change.

That distinction generalizes. When long and short selections differ structurally in risk, liquidity, or beta, portfolio construction determines which hypothesis the backtest actually tests.

## Limitations

The cost sensitivity excludes borrow fees, financing, and market impact. Missing stock returns are set to zero on 0.19% of position-days, constituent snapshots have no announcement lag, and sector, style, and liquidity exposures are unconstrained. These are research results, not a live implementation claim.

## Conclusion

The low-volatility signal is straightforward; the more interesting question is how to translate it into positions whose risks are intentional. Stock-level volatility scaling provides a simple implementation, while market beta can be managed separately with an index overlay when necessary. The 1998–2000 drawdown shows what risk scaling does not eliminate: sustained characteristic reversals can still produce severe losses.

> Start with the signal, identify the risks the initial portfolio is taking, allocate them deliberately, and only then judge the result.
