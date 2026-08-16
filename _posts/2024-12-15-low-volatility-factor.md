---
layout: post
title: "The Low-Volatility Factor: Portfolio Construction Matters"
date: 2024-12-15
last_modified_at: 2026-08-16
categories: [Quant]
---

Low-risk equities have historically delivered stronger returns per unit of risk than high-risk peers. [Blitz and van Vliet](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865) document the effect across the US, Europe, and Japan. Related evidence finds a security market line that is too flat: total volatility and market beta are distinct but overlapping equity signals.

One explanation is leverage constraints. Investors who cannot lever a high-Sharpe, low-risk portfolio may instead buy high-beta securities for more market exposure per dollar. [Frazzini and Pedersen](https://www.nber.org/papers/w16601) formalize that mechanism in betting against beta.

This article asks a narrower implementation question: how does the same low-minus-high volatility signal change when equal stock weights are replaced by stock-level risk scaling? I compare a 100%-long, 100%-short dollar-neutral portfolio with a volatility-scaled version. Dollar neutrality is a valid constraint, but it does not imply beta neutrality or balanced standalone leg risk.

The selection rule stays fixed. I change only position sizing, then compare notional, beta, turnover, drawdowns, and a small transaction-cost sensitivity. The aim is to separate the factor spread from the chosen risk budget.

## What exactly are we sorting?

The sample starts in 1995 and ends in October 2024. At every weekly signal date, I take the most recent complete Russell 1000 constituent snapshot available in the dataset and map it to the trading calendar. This point-in-time universe step matters. Using today's members throughout the history would quietly remove many companies that disappeared and would give the backtest information it could not have known at the time.

I remove stocks whose unadjusted price is below $5 and require a valid selection signal, sizing volatility, and beta estimate before ranking. After those common-data checks, the point-in-time eligible universe contains between 840 and 1,017 stocks, with a median cross-section of 971 names. Consequently, the two portfolio implementations and the exposure diagnostics all operate on the same cross-section.

<a class="low-vol-figure" href="/assets/2024-12-15-low-volatility-factor/eligible_universe.png" aria-label="Open Figure 1 at full size">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/eligible_universe_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/eligible_universe.png" alt="Number of eligible point-in-time Russell 1000 constituents at each weekly signal date" loading="lazy">
  </picture>
</a>

<p class="figure-caption"><strong>Figure 1:</strong> Number of eligible point-in-time Russell 1000 constituents at each weekly signal date after the $5 price filter and data-availability checks. The observed range is 840–1,017 stocks and the median is 971. Click or tap the figure for the full-resolution version.</p>

For stock \(i\) on signal date \(t\), let \(\widehat{\sigma}_{i,t}^{(h)}\) denote annualized realized volatility over the trailing \(h\) trading days, where \(h\in\{21,63,126\}\). The selection signal \(v_{i,t}\) is their average:

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

The one-, three-, and six-month horizons balance recent changes in risk against signal stability.

All three estimates use adjusted close-to-close price returns available through the signal close. After averaging the three horizons, I clip the resulting signal \(v_{i,t}\) to 5%–200% before ranking. This keeps pathological observations from controlling the sort while leaving ordinary cross-sectional differences untouched.

I divide the ranked stocks into ten deterministic, approximately equal-sized groups. Decile 1 contains the lowest-volatility stocks and decile 10 the highest. The strategy trades only those extremes; the middle deciles show the broader cross-sectional shape.

<a class="low-vol-figure" href="/assets/2024-12-15-low-volatility-factor/decile_profile.png" aria-label="Open Figure 2 at full size">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/decile_profile_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/decile_profile.png" alt="Geometric return, volatility, and Sharpe ratio across volatility deciles">
  </picture>
</a>

<p class="figure-caption"><strong>Figure 2:</strong> Long-only geometric return, realized volatility, and arithmetic-return Sharpe ratio by volatility decile, before transaction costs. Decile 1 contains the lowest-volatility stocks. Click or tap the figure for the full-resolution version.</p>

Figure 2 gives a more nuanced result than “low volatility wins.” Realized portfolio volatility rises steadily across the sort—an almost mechanical consequence of ranking stocks on trailing volatility. Geometric returns vary across the middle deciles, while Sharpe ratios generally deteriorate as volatility rises. The weakest risk-adjusted performance sits in the highest-volatility group.

That last group is exactly what the long/short strategy sells. It is also where the portfolio-construction problem begins.

## Keeping the timing honest

The signal is formed at the first market close of each week, the portfolio trades at the next market close, and P&L begins with the subsequent close-to-close return. A Monday signal therefore informs a Tuesday close trade whose first return runs from Tuesday to Wednesday.

Stock P&L uses the vendor's total-return field. Off-calendar source rows are compounded before sampling onto the Russell 1000 market calendar. Between rebalances I hold fixed quantities, and turnover is measured from the resulting drifted holdings to the next targets.

The complete specification is summarized below. The position-sizing and beta rows are developed in the following sections.

<table class="research-table specification-table">
  <thead>
    <tr><th>Component</th><th>Specification</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Sample</th><td>July 1995–October 2024</td></tr>
    <tr><th scope="row">Universe</th><td>Point-in-time Russell 1000 constituents; unadjusted price ≥ $5</td></tr>
    <tr><th scope="row">Selection signal</th><td>Mean annualized realized volatility over 21, 63, and 126 trading days</td></tr>
    <tr><th scope="row">Cross-sectional portfolio</th><td>Ten equal-count deciles; long decile 1, short decile 10</td></tr>
    <tr><th scope="row">Rebalance</th><td>First market close of each week</td></tr>
    <tr><th scope="row">Execution</th><td>Next market close; P&amp;L starts on the subsequent close-to-close return</td></tr>
    <tr><th scope="row">Stock sizing</th><td>60-day volatility floored at 5%; 20% reference volatility; 4% position cap; 100% leg-gross cap</td></tr>
    <tr><th scope="row">Beta diagnostic</th><td>252-day estimate; minimum 126 observations; clipped to [−4, 4]</td></tr>
    <tr><th scope="row">Cost sensitivity</th><td>5 bps per dollar of absolute equity notional traded</td></tr>
  </tbody>
</table>

<p class="figure-caption"><strong>Table 1:</strong> Backtest specification. All signal, sizing, and beta inputs are lagged consistently with the execution schedule.</p>

## First implementation: dollar-neutral, but risk-asymmetric

The equal-notional implementation is intentionally conventional:

* buy every stock in decile 1 with equal weight, for total long exposure of 100%;
* short every stock in decile 10 with equal absolute weight, for total short exposure of 100%.

Its target gross exposure is 200% and its target net exposure is zero. Let \(L\) and \(H\) denote the low- and high-volatility baskets. If \(r_{L,\tau}\) and \(r_{H,\tau}\) are their equal-weight returns during return period \(\tau\), the equal-weight portfolio return is

$$
r_{p,\tau}^{\mathrm{EW}}=r_{L,\tau}-r_{H,\tau}.
$$

The equation constrains notional only. Writing \(r_p^{\mathrm{EW}}\), \(r_L\), and \(r_H\) for the corresponding return random variables, portfolio variance still depends on both leg variances and their covariance:

$$
\begin{aligned}
\operatorname{Var}\!\left(r_p^{\mathrm{EW}}\right)
&=\operatorname{Var}(r_L)+\operatorname{Var}(r_H) \\
&\quad-2\operatorname{Cov}(r_L,r_H).
\end{aligned}
$$

Dollar neutrality constrains the sum of the signed weights. Matching the standalone volatilities or betas of the two legs requires additional constraints. Dollar neutrality, beta neutrality, and matched standalone leg risk are distinct portfolio objectives.

<a class="low-vol-figure" href="/assets/2024-12-15-low-volatility-factor/naive_leg_risk.png" aria-label="Open Figure 3 at full size">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/naive_leg_risk.png" alt="Realized volatility and average beta of the low- and high-volatility deciles" loading="lazy">
  </picture>
</a>

<p class="figure-caption"><strong>Figure 3:</strong> Annualized realized volatility and average ex-ante beta of the equal-weight low- and high-volatility baskets, before transaction costs. Click or tap the figure for the full-resolution version.</p>

The low-volatility basket realizes 12.1% volatility; the high-volatility basket realizes 39.8%. Equal notional therefore assigns the short book more than three times as much standalone volatility. Dollar neutrality remains a valid mandate, while the risk budget requires a separate design choice.

The same mismatch appears in market exposure. Average ex-ante stock beta is approximately 0.56 in the low-volatility basket and 1.63 in the high-volatility basket. Once the latter is shorted, the dollar-neutral portfolio acquires a large negative market beta. Its full-sample realized beta is −1.18.

For an investor whose mandate is dollar neutrality, this may simply be an exposure profile to manage. For my narrower research question, however, the implementation mixes the low-volatility spread with a large short-market position: a modest-risk long book is paired with a high-risk, high-beta short book. Before costs, the strategy realizes 34.9% annualized volatility, a Sharpe ratio of 0.08, and an 85.0% maximum drawdown. Under the simple cost sensitivity below, its geometric return is −4.7% per year and the maximum drawdown reaches 89.5%.

This result combines the signal with the equal-notional sizing rule. The second implementation changes the sizing rule while holding the cross-sectional selection fixed.

## Reallocating the stock-level risk budget

I now replace equal stock weights with a simple inverse-volatility sizing rule. This standalone-risk heuristic excludes correlations and leaves the selected names unchanged. Its sole input into position size is each stock's own trailing volatility.

For sizing, I use a separate 60-trading-day annualized volatility estimate, \(\widehat{\sigma}_{i,t}^{(60)}\), floored at 5%. Keeping selection and sizing conceptually separate is useful: the 21/63/126-day average decides *which* stocks belong in the extreme portfolios, while the 60-day estimate decides *how much* of each selected stock to hold.

For a leg \(\ell\in\{L,H\}\), let \(\mathcal I_{\ell,t}\) be its selected-stock set at signal date \(t\), and let \(N_{\ell,t}=|\mathcal I_{\ell,t}|\). For stock \(i\in\mathcal I_{\ell,t}\), the preliminary absolute weight is

$$
\begin{aligned}
a_{i,t}
&=\min\left(
\frac{1}{N_{\ell,t}}
\frac{20\%}{\widehat{\sigma}_{i,t}^{(60)}},
\;4\%
\right).
\end{aligned}
$$

The equation has three components:

1. \(1/N_{\ell,t}\) is the equal-weight starting point for a leg containing \(N_{\ell,t}\) stocks.
2. \(20\%/\widehat{\sigma}_{i,t}^{(60)}\) is the volatility multiplier. Before the cap, a stock with 10% estimated volatility receives twice its equal weight; a stock with 40% volatility receives half.
3. The 4% cap prevents an unusually low volatility estimate from creating a concentrated position.

There is one more step. If the preliminary weights in a leg sum to more than 100%, I scale them down proportionally. If they sum to less than 100%, I leave them alone. Writing \(s_\ell=+1\) for the long leg and \(s_\ell=-1\) for the short leg, the final signed weight is

$$
\begin{aligned}
c_{\ell,t}
&=\min\left(
1,
\frac{100\%}{\sum_{j\in\mathcal I_{\ell,t}}a_{j,t}}
\right), \\
w_{i,t}
&=s_\ell a_{i,t}c_{\ell,t}.
\end{aligned}
$$

Here \(c_{\ell,t}\) is the leg-level gross-cap multiplier, and \(j\) indexes the stocks in \(\mathcal I_{\ell,t}\); the denominator is that leg's preliminary gross weight.

The 100% leg limit acts only as a cap. If a basket contains very volatile stocks, the rule may assign 30% or 40% of NAV to that leg. Renormalizing it back to 100% would undo much of the intended reduction in high-volatility-leg notional.

The procedure is **stock-level volatility scaling**: it scales standalone stock risk and caps both concentration and leg gross. Portfolio-level volatility targeting and covariance-based marginal risk contributions sit in a separate construction layer.

### Where leverage enters

The low-volatility anomaly is fundamentally a risk-adjusted return result, which makes leverage central to implementation. An investor comparing strategies at the same ex-ante volatility would normally apply a scalar to the completed weight vector:

$$
\begin{aligned}
\widetilde{\mathbf w}_t
&= \mathbf w_t
\frac{\sigma^*}{\widehat{\sigma}_{p,t}}.
\end{aligned}
$$

Here \(\mathbf w_t\) is the completed stock-weight vector, \(\widetilde{\mathbf w}_t\) is its volatility-targeted version, \(\sigma^*\) is the portfolio volatility target, and \(\widehat{\sigma}_{p,t}\) is the portfolio-volatility forecast. I keep this scalar at one to isolate the effect of stock-level sizing. A later portfolio layer could introduce a covariance forecast and manage total leverage explicitly.

## The resulting exposure profile

Allowing the short book to shrink creates positive net notional. This experiment prioritizes a reduction in standalone-risk asymmetry over a dollar-neutral mandate. A zero-net mandate would require a different constrained construction.

<a class="low-vol-figure" href="/assets/2024-12-15-low-volatility-factor/target_exposures.png" aria-label="Open Figure 4 at full size">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/target_exposures_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/target_exposures.png" alt="Long gross, short gross, and net stock exposure through time" loading="lazy">
  </picture>
</a>

<p class="figure-caption"><strong>Figure 4:</strong> Weekly target long gross, short gross, and net stock exposure after stock-level volatility scaling. Click or tap the figure for the full-resolution version.</p>

Across the sample, the low-volatility long averages 97.0% gross and the high-volatility short 34.2%. Total stock gross is 131.2% and net stock exposure is +62.8%. The short shrinks because its constituents consume more standalone risk per dollar.

At first glance, +63% net exposure may appear inconsistent with the portfolio's near-zero average beta. Dollar exposure and beta exposure answer different questions. Let \(E_t^{\mathrm{net}}\) be signed stock notional as a fraction of NAV, and let \(\widehat{\beta}_{i,t}\) be stock \(i\)'s estimated market beta. Summing over all held stocks gives

$$
\begin{aligned}
E_t^{\mathrm{net}} &= \sum_i w_{i,t}, \\
\widehat{\beta}_{p,t} &= \sum_i w_{i,t}\widehat{\beta}_{i,t}.
\end{aligned}
$$

The first quantity is signed notional; \(\widehat{\beta}_{p,t}\) is the ex-ante portfolio beta. A smaller short book can offset a larger long book when the short constituents carry sufficiently high betas—which is exactly what happens in this cross-sectional sort.

## Does the portfolio require an always-on beta hedge?

I estimate each stock's beta from a rolling 252-trading-day covariance with the Russell 1000 price-index return, require at least 126 observations, and clip individual estimates to [−4, 4]. The ex-ante portfolio estimate is the weighted sum shown above. A rolling regression of strategy returns on market returns provides a separate realized-beta diagnostic.

<a class="low-vol-figure" href="/assets/2024-12-15-low-volatility-factor/beta_diagnostic.png" aria-label="Open Figure 5 at full size">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/beta_diagnostic_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/beta_diagnostic.png" alt="Ex-ante and rolling realized beta of the volatility-scaled portfolio" loading="lazy">
  </picture>
</a>

<p class="figure-caption"><strong>Figure 5:</strong> Aggregated ex-ante stock beta and rolling 252-day realized beta for the volatility-scaled portfolio. The shaded region marks beta between −0.1 and +0.1. Click or tap the figure for the full-resolution version.</p>

Average signed ex-ante beta and full-sample realized beta are both approximately −0.010. Weekly exposure still matters—the average absolute ex-ante estimate is 0.104—but its sign changes. I therefore omit an always-on hedge. A live process could instead use a predefined beta band for a conditional index overlay.

## A small transaction-cost sensitivity

I charge 5 basis points per dollar of absolute equity notional traded, including initial formation. Turnover is the annual sum of absolute weight changes from drifted pre-trade holdings to new targets: 31.4× for equal notional and 19.3× for volatility scaling. This is a small comparative sensitivity, not an estimate of achievable live performance.

## Comparing the two implementations

The two tables below separate performance from the exposures and trading that produce it. The 0 bp and 5 bp return columns are annualized arithmetic means; volatility, Sharpe, and drawdown use returns under the 5 bp sensitivity.

<table class="research-table comparison-table performance-table">
  <thead>
    <tr>
      <th>Implementation</th>
      <th>Return, 0 bp</th>
      <th>Return, 5 bp</th>
      <th>Volatility, 5 bp</th>
      <th>Sharpe, 5 bp</th>
      <th>Max drawdown, 5 bp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Equal-weight dollar-neutral L/S</th>
      <td data-label="Return, 0 bp">2.9%</td>
      <td data-label="Return, 5 bp">1.4%</td>
      <td data-label="Volatility, 5 bp">34.9%</td>
      <td data-label="Sharpe, 5 bp">0.04</td>
      <td data-label="Max drawdown, 5 bp">−89.5%</td>
    </tr>
    <tr>
      <th scope="row">Stock-volatility-scaled L/S</th>
      <td data-label="Return, 0 bp">7.9%</td>
      <td data-label="Return, 5 bp">7.0%</td>
      <td data-label="Volatility, 5 bp">9.6%</td>
      <td data-label="Sharpe, 5 bp">0.72</td>
      <td data-label="Max drawdown, 5 bp">−41.0%</td>
    </tr>
  </tbody>
</table>

<p class="figure-caption"><strong>Table 2:</strong> Performance from July 1995 through October 2024. Volatility uses 252 trading days and Sharpe assumes a zero risk-free rate.</p>

<table class="research-table comparison-table exposure-table">
  <thead>
    <tr>
      <th>Implementation</th>
      <th>Avg. stock gross</th>
      <th>Avg. stock net</th>
      <th>Realized beta</th>
      <th>Annualized turnover</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Equal-weight dollar-neutral L/S</th>
      <td data-label="Avg. stock gross">2.01</td>
      <td data-label="Avg. stock net">0.00</td>
      <td data-label="Realized beta">−1.18</td>
      <td data-label="Annualized turnover">31.4× equity</td>
    </tr>
    <tr>
      <th scope="row">Stock-volatility-scaled L/S</th>
      <td data-label="Avg. stock gross">1.31</td>
      <td data-label="Avg. stock net">0.63</td>
      <td data-label="Realized beta">−0.01</td>
      <td data-label="Annualized turnover">19.3× equity</td>
    </tr>
  </tbody>
</table>

<p class="figure-caption"><strong>Table 3:</strong> Daily-average stock exposures, full-sample regression beta of gross strategy returns on the Russell 1000 price-index return, and annualized turnover.</p>

The change is economically large. Annualized volatility falls from 34.9% to 9.6%. Under the 5 bp sensitivity, Sharpe rises from 0.04 to 0.72, maximum drawdown improves from 89.5% to 41.0%, and annualized arithmetic return rises from 1.4% to 7.0%.

Costs reduce annualized arithmetic return by roughly 1.6 percentage points for equal notional and 1.0 point for volatility scaling.

<a class="low-vol-figure" href="/assets/2024-12-15-low-volatility-factor/cumulative_performance.png" aria-label="Open Figure 6 at full size">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/cumulative_performance_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/cumulative_performance.png" alt="Cumulative wealth of the equal-weight and volatility-scaled implementations" loading="lazy">
  </picture>
</a>

<p class="figure-caption"><strong>Figure 6:</strong> Cumulative wealth under the 5 bp transaction-cost sensitivity, shown on a logarithmic scale. Click or tap the figure for the full-resolution version.</p>

The log-scale curves show the equal-notional portfolio failing to compound through repeated large losses, while the scaled implementation progresses more steadily.

<a class="low-vol-figure" href="/assets/2024-12-15-low-volatility-factor/drawdowns.png" aria-label="Open Figure 7 at full size">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/drawdowns_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/drawdowns.png" alt="Drawdowns of the equal-weight and volatility-scaled implementations" loading="lazy">
  </picture>
</a>

<p class="figure-caption"><strong>Figure 7:</strong> Drawdowns under the 5 bp transaction-cost sensitivity for both portfolio implementations. Click or tap the figure for the full-resolution version.</p>

An 89.5% drawdown is strategy-ending for most investors. The scaled portfolio still loses 41.0% at its worst, so risk scaling improves the path without making it benign.

## How much of this is really the factor?

Figure 2 supports the signal claim: the low-volatility decile has better risk-adjusted performance than the high-volatility decile. The jump to a 0.72 long/short Sharpe is mostly a construction result. The selected stocks do not change; their risk allocation does, along with gross, net, beta, turnover, and the return path.

This distinction generalizes beyond low volatility. Whenever the long and short selections have structurally different risk, liquidity, or beta characteristics, equal dollars can embed a large unintended exposure. Portfolio construction determines which hypothesis the backtest is actually testing.

## Limitations

The scope is a research illustration of sizing and exposure. The scaled strategy carries roughly +63% net stock exposure and therefore falls outside a dollar-neutral mandate. The cost sensitivity covers equity trading only; borrow fees, financing, and market impact sit outside it. Missing stock returns are set to zero on 0.19% of position-days, constituent snapshots are treated as effective without an announcement lag, and the portfolios carry unconstrained sector and liquidity exposures. The headline results should be read in that scope.

## Conclusion

The equal-weight low-minus-high volatility trade satisfies dollar neutrality while carrying sharply mismatched standalone leg volatility and a large negative market beta. The combined portfolio consequently realizes 34.9% volatility and an 89.5% drawdown under the 5 bp sensitivity.

Scaling positions inversely to stock volatility reduces that asymmetry. It leaves the long book close to fully invested, allows the high-risk short book to shrink, and produces near-zero average signed market beta. The trade-off is positive net notional, and its acceptability depends on the investor's mandate.

The broader lesson is the one I want to carry into later research:

> Start with the signal, identify which risks the initial portfolio is really taking, allocate those risks deliberately, and only then judge the result.
