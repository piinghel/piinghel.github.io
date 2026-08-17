---
layout: post
title: "The Low-Volatility Factor: Portfolio Construction Matters"
date: 2024-12-15
last_modified_at: 2026-08-17
categories: [Quant]
---

Low-volatility stocks are quiet by design. That is part of their appeal—and part of the implementation problem. The factor is easy to describe: rank stocks by volatility, buy the calmest, and short the most volatile. The harder question is what positions that ranking should produce.

Across the US, Europe, and Japan, low-risk equities have historically delivered more return per unit of risk than high-risk peers. [Blitz and van Vliet](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865) document the effect. One explanation is leverage constraints: investors who want more market exposure may buy high-beta securities instead of levering a higher-Sharpe, low-risk portfolio. [Frazzini and Pedersen](https://www.nber.org/papers/w16601) formalize that mechanism in betting against beta.

Here I keep stock selection fixed, use equal weights only as a deliberately weak reference, and make stock-level volatility scaling the main implementation. The aim is modest: a portfolio that is simple enough to understand and whose risks are visible in the results.

## The tradable universe

I start with historical point-in-time Russell 1000 constituents from July 1995 through October 2024. I apply a $5 minimum unadjusted-price filter and keep names with the data needed to estimate the signal. That leaves 840–1,017 eligible stocks per week, with a median of 971. Both portfolio implementations use exactly the same weekly cross-section.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/eligible_universe_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/eligible_universe.png" alt="Number of eligible point-in-time Russell 1000 constituents at each weekly signal date" loading="lazy">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Number of eligible point-in-time Russell 1000 constituents at each weekly signal date after the $5 price filter and data-availability checks. The observed range is 840–1,017 stocks and the median is 971.</p>

For each stock $$i$$ on signal date $$t$$, I estimate annualized realized volatility over the trailing $$h\in\{21,63,126\}$$ trading days and take the average:

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

The one-, three-, and six-month windows balance responsiveness and stability. Before ranking, I clip the average to 5%–200% to keep extreme observations from dominating the sort.

Each week I split the ranked stocks into ten deterministic, approximately equal-sized groups. Deciles 1 and 10 each contain roughly 100 stocks, making them meaningful slices of the tradable universe. Decile 1 is the long leg and decile 10 is the short leg; the middle deciles help show the shape of the cross-section.

<div class="low-vol-figure decile-profile-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/decile_profile_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/decile_profile.png" alt="Geometric return, volatility, and Sharpe ratio across volatility deciles">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Long-only geometric return, realized volatility, and arithmetic-return Sharpe ratio by volatility decile, before transaction costs. Decile 1 contains the lowest-volatility stocks.</p>

Figure 2 confirms the intended cross-sectional pattern: realized volatility rises across the sort, while Sharpe ratios generally deteriorate. That is the easy part. The allocation determines the portfolio, so the full specification is below.

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

Before scaling positions, I use equal weighting as a control. The two baskets sit at opposite ends of the volatility distribution, so equal notional leaves the high-volatility basket carrying much more risk: 39.8% realized volatility versus 12.1% for the low-volatility basket. Its average ex-ante stock beta is also higher, 1.63 versus 0.56. This gives us a clean comparison before changing only the sizing.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/naive_leg_risk.png" alt="Realized volatility and average beta of the low- and high-volatility deciles" loading="lazy">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Annualized realized volatility and average ex-ante beta of the equal-weight low- and high-volatility baskets, before transaction costs.</p>

Equal weights do exactly what we would expect: they leave the riskier basket carrying much more risk. The main implementation changes only the allocation and uses each name's standalone volatility to decide how much notional to hold.

## The main implementation: stock-level volatility scaling

At this point I change one thing: position sizing. Stock selection remains fixed. The 21/63/126-day average decides *which* stocks enter, while a separate 60-day volatility estimate, floored at 5%, decides *how much* to hold. I leave correlations out of the rule to keep the construction transparent.

Within each leg, the allocation starts with an explicit $1/N$ base and then adjusts each stock's notional by inverse estimated volatility.

For a leg $$\ell\in\{L,H\}$$, let $$\mathcal S_{\ell,t}$$ be its selected-stock set at signal date $$t$$, and let $$N_{\ell,t}=\lvert\mathcal S_{\ell,t}\rvert$$. Expressing volatility and weights as decimals, the uncapped and capped absolute weights for stock $$i\in\mathcal S_{\ell,t}$$ are

$$
\begin{aligned}
a_{i,\ell,t}^{\mathrm{pre}}
&=\frac{1}{N_{\ell,t}}
\frac{0.20}{\widehat{\sigma}_{i,t}^{(60)}}, \\
a_{i,\ell,t}
&=\min\left(a_{i,\ell,t}^{\mathrm{pre}},\;0.04\right).
\end{aligned}
$$

The 0.20 sets a 20% annualized volatility target for each stock. Portfolio volatility emerges from the resulting positions. Lower-volatility stocks receive more notional and higher-volatility stocks receive less. The 4% cap limits concentration. If the preliminary weights in a leg add up to more than 100% gross, I scale the whole leg down proportionally:

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

The 100% leg limit acts as a ceiling. A volatile short basket can therefore shrink to 30% or 40% of NAV, preserving the risk adjustment. This is standalone stock-risk scaling; portfolio volatility and correlations are properties of the resulting positions.

## The resulting exposure profile

Inverse-volatility sizing is asymmetric here. The low-volatility long book receives more notional, while the high-volatility short book naturally becomes smaller.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/stock_exposure_profile_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/stock_exposure_profile.png" alt="Long gross, short gross, and net stock exposure through time" loading="lazy">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Weekly target long gross, short gross, and net stock exposure after stock-level volatility scaling.</p>

Across the sample, the low-volatility long averages 97.0% gross and the high-volatility short 34.2%. Total stock gross is 131.2%, leaving the portfolio with +62.8% net stock exposure. This net exposure comes directly from the sizing rule.

Net stock notional and market beta are different things. Let $$E_t^{\mathrm{net}}$$ be signed stock notional as a fraction of NAV, and let $$\widehat{\beta}_{i,t}$$ be stock $$i$$'s estimated market beta. Then

$$
\begin{aligned}
E_t^{\mathrm{net}} &= \sum_i w_{i,t}, \\
\widehat{\beta}_{p,t} &= \sum_i w_{i,t}\widehat{\beta}_{i,t}.
\end{aligned}
$$

Even with less notional, the short offsets much of the larger long in beta terms because its constituents carry much higher market betas. I therefore treat beta as a separate diagnostic and keep stock sizing focused on standalone volatility.

## Managing market beta separately

Beta sits outside the stock allocation. Figure 5 shows the practical reason: the average beta is close to zero, but it moves around quite a bit. A small offsetting index-futures position could reduce that residual exposure. I would keep it as a separate overlay and leave the stock weights focused on the volatility signal.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/beta_diagnostic_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/beta_diagnostic.png" alt="Ex-ante and rolling realized beta of the volatility-scaled portfolio" loading="lazy">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Aggregated ex-ante stock beta and rolling 252-day realized beta for the volatility-scaled portfolio. The shaded region marks beta between −0.1 and +0.1.</p>

The small negative average is incidental: the high-volatility short leg is allowed to shrink under the 100% leg cap, leaving more notional in low-volatility stocks.

## Performance, costs, and drawdowns

The tables separate performance from the exposures that produce it. I charge 5 basis points per dollar of equity notional traded, including initial formation. This comparative sensitivity shows how trading costs affect the results. Returns are annualized arithmetic means; volatility, Sharpe, and drawdown use returns after that cost.

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

With the same stock selection as the reference, the volatility-scaled implementation produces a 7.0% annualized arithmetic return after costs, 9.6% volatility, and a 0.72 Sharpe. Its cost drag is roughly 1.0 percentage point a year. Most of the improvement comes from changing the weights; stock selection is held fixed.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns.png" alt="Cumulative wealth and drawdowns of the equal-weight reference and volatility-scaled implementation" loading="lazy">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 6:</strong> Cumulative wealth and drawdowns after the 5 bp transaction-cost sensitivity. The panels share the same time axis; the top panel uses a logarithmic wealth scale, while the shaded lower panel shows the distance from each portfolio’s previous high.</p>

## What happened during the 41% drawdown?

The uncomfortable part of the result is the 41.0% drawdown. The scaled portfolio peaks on 8 October 1998 and reaches its trough on 9 March 2000, a loss over 357 trading days while the Russell 1000 price index gains 52.2%. The portfolio recovers its earlier high on 15 August 2001.

This was the dot-com boom. The strategy was long the calmer stocks and short the volatile stocks, but the latter rallied sharply. Over the peak-to-trough window, the Russell 1000 price index gained 52.2%, while the standalone scaled low-volatility long fell 15.5% and the standalone signed high-volatility short fell 29.6%, both before costs. Figure 7 makes the accounting explicit: the top line is the combined L/S portfolio built from the signed target weights. Its daily dollar P&L equals the sum of the long-book and short-book P&L, normalized by portfolio NAV and compounded after costs. The two lower lines are standalone leg paths, compounded separately before costs, so the signed short leg falls when the high-volatility basket rallies.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/dotcom_comparison_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/dotcom_comparison.png" alt="Relative wealth of the volatility-scaled portfolio, Russell 1000 price index, and its two legs from October 1998 through December 2003" loading="lazy">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 7:</strong> Relative wealth from the 8 October 1998 peak through December 2003, with each series rebased to 1. The top panel shows the combined volatility-scaled L/S portfolio after costs against the Russell 1000 price index. The bottom panel shows standalone signed long and short legs, compounded separately before costs.</p>

## Conclusion

The signal is simple; the portfolio is where the real work begins. Equal weighting is useful as a deliberately weak reference because it exposes the basic problem: the high-volatility short book carries much more risk than the low-volatility long book. Stock-level volatility scaling addresses that asymmetry directly. With the same stock selection, it produces lower realized volatility, lower turnover, and a much smaller drawdown while keeping the allocation rule easy to inspect.

That is the implementation I would take forward, with the factor's risks in view. The 1998–2000 episode is the important counterexample: the Russell 1000 rallied, high-volatility stocks rallied even more, and both standalone scaled legs lost money over the peak-to-trough window. Beta moved around but averaged close to zero, so I would treat it as a small separate overlay and keep the stock weights focused on the signal. My takeaway is that the signal tells me where to look; sizing determines what I actually own, and regime risk remains after the sizing is done. A natural next step is to let correlations and explicit risk budgets enter the allocation through a constrained optimizer. That is a separate portfolio-construction question—and probably a separate article.
