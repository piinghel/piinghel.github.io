---
layout: post
title: "The Low-Volatility Factor: Portfolio Construction Matters"
date: 2024-12-15
last_modified_at: 2026-08-17
categories: [Quant]
article_mark: /assets/brand/low-volatility-mark.svg
article_label: Low-volatility · portfolio construction
---

The low-volatility factor is well documented. The implementation question is how to turn its cross-sectional ranking into a sensible long/short portfolio. I keep the stock selection fixed and focus on the translation from signal to portfolio: the same stock list can produce very different results depending on how much capital each position receives.

Across the US, Europe, and Japan, low-risk equities have historically delivered more return per unit of risk than high-risk peers. [Blitz and van Vliet](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865) document the effect. One explanation is leverage constraints: investors who want more market exposure may buy high-beta securities instead of levering a higher-Sharpe, low-risk portfolio. [Frazzini and Pedersen](https://www.nber.org/papers/w16601) formalize that mechanism in betting against beta.

I keep stock selection fixed, use equal weights as a deliberately weak reference, and make stock-level volatility scaling the main implementation. The aim is a portfolio that is simple enough to understand and whose risks are visible in the results.

## The tradable universe

I start with the Russell 1000 membership recorded at each date from July 1995 through October 2024. I apply a $5 price filter based on unadjusted prices and keep stocks with enough data to estimate the signal. That leaves 840–1,017 eligible stocks per week, with a median of 971. Both portfolio implementations use the same weekly stock universe.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/eligible_universe_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/eligible_universe_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/eligible_universe.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/eligible_universe.png" alt="Number of eligible Russell 1000 stocks at each weekly signal date" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Number of eligible Russell 1000 stocks at each weekly signal date after the $5 price filter and data-availability checks. The observed range is 840–1,017 stocks and the median is 971.</p>

For each stock $$i$$ on each signal date $$t$$, I estimate annualized realized volatility over the past $$h\in\{21,63,126\}$$ trading days and take the average:

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

Each week I split the ranked stocks into ten fixed groups of roughly equal size. Deciles 1 and 10 each contain roughly 100 stocks, making them meaningful slices of the tradable universe. Decile 1 is the long leg and decile 10 is the short leg; the middle deciles show how the results change across the ranking.

<div class="low-vol-figure decile-profile-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/decile_profile_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/decile_profile_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/decile_profile.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/decile_profile.png" alt="Geometric return, volatility, and Sharpe ratio across volatility deciles" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Long-only compounded return, realized volatility, and Sharpe ratio by volatility decile, before transaction costs. Decile 1 contains the lowest-volatility stocks.</p>

Figure 2 shows the intended pattern: realized volatility rises across the ranking, while Sharpe ratios generally deteriorate. The next step is to see what that ranking produces with a deliberately simple allocation.

## A simple equal-weight reference

Before scaling positions, I use equal weighting as a control. The two baskets sit at opposite ends of the volatility distribution, so giving every stock the same dollar position leaves the high-volatility basket carrying much more risk: 39.8% realized volatility versus 12.1% for the low-volatility basket. Its average estimated stock beta is also higher, 1.63 versus 0.56. This gives us a clean comparison before changing only the sizing.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/naive_leg_risk.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/naive_leg_risk.png" alt="Realized volatility and average beta of the low- and high-volatility deciles" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Annualized realized volatility and average estimated beta of the equal-weight low- and high-volatility baskets, before transaction costs.</p>

Equal weights make the risk imbalance visible. I now keep the stock selection fixed and change only the sizing.

## The main implementation: stock-level volatility scaling

The 21/63/126-day average determines which stocks enter. Each week I split the eligible Russell 1000 stocks into ten equal-sized groups, buy the roughly 100 calmest stocks, and short the roughly 100 most volatile. The signal trades the next day. A separate 60-day volatility estimate, floored at 5%, determines how much to hold. The allocation uses each stock's own volatility and keeps correlations outside the rule, which keeps it easy to inspect.

Within each leg, the allocation starts with an explicit $1/N$ base and then adjusts each stock's position size by its inverse estimated volatility. The backtest charges 5 bps for every dollar of stock position traded.

For a leg $$\ell\in\{L,H\}$$, let $$\mathcal S_{\ell,t}$$ be its selected-stock set at signal date $$t$$, and let $$N_{\ell,t}=\lvert\mathcal S_{\ell,t}\rvert$$. Expressing volatility and weights as decimals, the uncapped and capped absolute weights for stock $$i\in\mathcal S_{\ell,t}$$ are

$$
\begin{aligned}
a_{i,\ell,t}^{\mathrm{pre}}
&=\frac{1}{N_{\ell,t}}
\times \frac{0.20}{\widehat{\sigma}_{i,t}^{(60)}}, \\
a_{i,\ell,t}
&=\min\left(a_{i,\ell,t}^{\mathrm{pre}},\;0.04\right).
\end{aligned}
$$

The 0.20 is the annualized volatility target used in the per-stock scaling step. Lower-volatility stocks receive more size and higher-volatility stocks receive less. The portfolio's realized volatility then emerges from these positions and their correlations. The 4% cap limits concentration. If the initial weights in a leg add up to more than 100% gross, I scale the whole leg down in proportion:

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

The 100% leg limit acts as a ceiling. A volatile short basket can therefore shrink to 30% or 40% of portfolio value, preserving the risk adjustment. This scales each stock by its own risk; portfolio volatility and correlations come from the resulting positions.

## The resulting exposure profile

Inverse-volatility sizing is uneven by design. The low-volatility long book receives more capital, while the high-volatility short book naturally becomes smaller.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/target_exposures_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/target_exposures_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/target_exposures.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/target_exposures.png" alt="Long gross, short gross, and net stock exposure through time" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Weekly target long gross, short gross, and net stock exposure after stock-level volatility scaling.</p>

Across the sample, the low-volatility long averages 97.0% gross and the high-volatility short 34.2%. Total stock gross is 131.2%, leaving the portfolio with +62.8% net stock exposure. This net exposure comes directly from the sizing rule.

Net stock exposure and market beta measure different things. Let $$E_t^{\mathrm{net}}$$ be signed stock exposure as a fraction of portfolio value, and let $$\widehat{\beta}_{i,t}$$ be stock $$i$$'s estimated market beta. Then

$$
\begin{aligned}
E_t^{\mathrm{net}} &= \sum_i w_{i,t}, \\
\widehat{\beta}_{p,t} &= \sum_i w_{i,t}\widehat{\beta}_{i,t}.
\end{aligned}
$$

Even with less capital, the short offsets much of the larger long in beta terms because its stocks carry much higher market betas. I therefore treat beta as a separate check and keep stock sizing focused on each stock's own volatility.

## A quick beta check

Figure 5 is a quick beta check. The estimate moves around, although its full-sample average is slightly negative. The 100% cap keeps the low-volatility long book close to fully invested while the volatile short book is smaller, so the short side does not fully offset the long side in beta terms. A small offsetting index-futures position would be a clean overlay if I wanted to tighten that exposure.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/beta_diagnostic_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/beta_diagnostic_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/beta_diagnostic.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/beta_diagnostic.png" alt="Estimated and rolling realized beta of the volatility-scaled portfolio" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Estimated stock beta and rolling 252-day realized beta for the volatility-scaled portfolio. The shaded region marks beta between −0.1 and +0.1.</p>

## Performance, costs, and drawdowns

The tables separate performance from the exposures that produce it. I charge 5 basis points per dollar of stock position traded, including the first portfolio formation. This simple cost sensitivity shows how trading costs affect the results. Returns are annualized arithmetic means; volatility, Sharpe, and drawdown use returns after that cost.

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

<p class="figure-caption"><strong>Table 1:</strong> Performance from July 1995 through October 2024. Volatility uses 252 trading days and Sharpe assumes a zero risk-free rate.</p>

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

<p class="figure-caption"><strong>Table 2:</strong> Average daily stock exposures, full-sample beta from regressing strategy returns on the Russell 1000 price-index return, and annualized turnover.</p>

With the same stock selection as the reference, the volatility-scaled implementation produces a 7.0% annualized arithmetic return after costs, 9.6% volatility, and a 0.72 Sharpe. Its cost drag is roughly 1.0 percentage point a year. Most of the improvement comes from changing the weights; stock selection is held fixed.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns.png" alt="Cumulative wealth and drawdowns of the equal-weight reference and volatility-scaled implementation" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 6:</strong> Cumulative wealth and drawdowns after the 5 bp transaction-cost sensitivity. The panels share the same time axis; the top panel uses a logarithmic wealth scale, while the shaded lower panel shows the distance from each portfolio’s previous high.</p>

## What happened during the 41% drawdown?

The most surprising part of the result is the 41.0% drawdown. The scaled portfolio peaks on 8 October 1998 and reaches its trough on 9 March 2000, a 41.0% loss over 357 trading days while the Russell 1000 price index gains 52.2%. The portfolio recovers its earlier high on 15 August 2001.

This was the dot-com boom. The strategy was long the calmer stocks and short the volatile stocks, while the volatile stocks rallied sharply. Over the same window, the low-volatility basket fell 16.3% and the high-volatility basket gained 334.2%. The long book contributed −12.0 percentage points, the short book −28.2, and trading costs another −0.85. Figure 7 puts the two legs beside the combined portfolio: the upper panel shows the portfolio result after costs, while the lower panel compounds the scaled long and short legs separately before costs. The short leg falls because the basket it sold short was one of the strongest parts of the market.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/dotcom_comparison_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/dotcom_comparison_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/dotcom_comparison.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/dotcom_comparison.png" alt="Relative wealth of the volatility-scaled portfolio, Russell 1000 price index, and its two legs from October 1998 through December 2003" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 7:</strong> Relative wealth from the 8 October 1998 peak through December 2003, with each series starting at 1. The top panel shows the combined volatility-scaled L/S portfolio after costs against the Russell 1000 price index. The bottom panel shows the same portfolio’s scaled long and short legs, compounded separately before costs.</p>

To sanity-check the aggregate result, I traced the P&L back to individual stocks over the same window. The three largest long-book losses came from New Century Energies (−0.63 percentage points), Evergy Kansas Central (−0.62), and Consolidated Edison (−0.59). On the short side, i2 Technologies (−0.91), XO Communications (−0.70), and Ciena (−0.68) were the largest losses. Across the dates they appeared in the short book, those stocks rose roughly 3,201%, 994%, and 1,691%, respectively.

The numbers in parentheses are cumulative contributions to the corresponding scaled leg, measured in percentage points across the weekly holding periods. They sit alongside the raw stock returns as a separate piece of information. In this backtest, i2 Technologies usually had a short weight of about 0.2%–0.3%, and that weight was reset each week. A 3,201% return means that the stock's total-return series grew to roughly 33 times its starting value across those dates; the strategy did not carry one fixed 0.2%–0.3% portfolio position through that entire compounding path. It realized a sequence of small weekly P&Ls instead, which is why the stock contributed −0.91 percentage points. The pattern is clear: the long book lagged, while a small group of extreme winners drove losses in the short book.

## Conclusion

The ranking is only the starting point. Equal weighting is useful as a deliberately weak reference because it makes the risk imbalance visible: the high-volatility short book carries much more risk than the low-volatility long book. Inverse-volatility sizing changes that implementation directly. With the same stock selection, it produces lower realized volatility, lower turnover, and a smaller drawdown while keeping every position easy to inspect.

The 1998–2000 episode remains the important counterexample. The Russell 1000 rallied, high-volatility stocks rallied even more, and both scaled legs lost money over the peak-to-trough window. Beta moved around but averaged slightly below zero, so I would treat it as a small separate overlay and keep the stock weights focused on the signal. My takeaway is simple: the signal tells me where to look; sizing determines what I actually own; and regime risk remains after the sizing is done. The next step I would explore is a constrained optimizer that brings correlations and explicit risk budgets into the allocation. That is where the portfolio construction becomes more interesting—and probably a separate article.
