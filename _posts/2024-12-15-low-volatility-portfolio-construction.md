---
layout: post
title: "The Low-Volatility Factor: Portfolio Construction Matters"
date: 2024-12-15
last_modified_at: 2026-08-18
show_date: false
categories: [Quant]
article_mark: /assets/brand/low-volatility-mark.svg
article_label: Low-volatility · portfolio construction
permalink: /quant/2024/12/15/low-volatility-factor.html
---

The low-volatility factor is well documented. The implementation question is how to turn its cross-sectional ranking into a sensible long/short portfolio. I keep the stock selection fixed and focus on the translation from signal to portfolio: the same stock list can produce very different results depending on how much capital each position receives.

Across the US, Europe, and Japan, low-risk equities have historically delivered more return per unit of risk than high-risk peers. [Blitz and van Vliet](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865) document the effect. One explanation is leverage constraints: investors who want more market exposure may buy high-beta securities instead of levering a higher-Sharpe, low-risk portfolio. [Frazzini and Pedersen](https://www.nber.org/papers/w16601) formalize that mechanism in betting against beta.

I compare two allocations with the same stock selection: equal weighting as a deliberately weak reference, and stock-level volatility scaling as the main implementation. The aim is a portfolio that is simple enough to understand and whose risks are visible in the results.

## The tradable universe

I start with the Russell 1000 membership history and apply it point-in-time to daily prices from July 1995 through 27 May 2026. I apply a $5 price filter based on unadjusted prices and keep stocks with enough data to estimate the signal. That leaves 857–1,015 eligible stocks at each rebalance, with a median of 973. Both implementations use that same universe.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/eligible_universe_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/eligible_universe_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/eligible_universe.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/eligible_universe.png" alt="Number of eligible Russell 1000 stocks at each rebalance date" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Eligible Russell 1000 stocks at each rebalance after the $5 price filter and availability checks. Range: 857–1,015; median: 973.</p>

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

At each rebalance I split the ranked stocks into ten fixed groups of roughly equal size. Deciles 1 and 10 each contain roughly 100 stocks, making them meaningful slices of the tradable universe. Decile 1 is the long leg and decile 10 is the short leg; the middle deciles show how the results change across the ranking.

<div class="low-vol-figure decile-profile-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/decile_profile_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/decile_profile_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/decile_profile.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/decile_profile.png" alt="Geometric return, volatility, and Sharpe ratio across volatility deciles" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Compounded return, realized volatility, and Sharpe ratio by volatility decile before costs. Decile 1 is the lowest-volatility group.</p>

Figure 2 shows the intended pattern: realized volatility rises across the ranking, while Sharpe ratios generally deteriorate. The next step is to see what that ranking produces with a deliberately simple allocation.

## A simple equal-weight reference

Equal weighting is a useful control because it exposes the problem immediately. We are long the calmest stocks and short the most volatile ones. Giving every stock the same dollar weight leaves the high-volatility leg carrying much more risk: 53.8% realized volatility versus 4.9% for the low-volatility leg. It also has the higher average estimated stock beta, 1.63 versus 0.55. Equal weighting gives the two legs the same capital, with very different risk. For the actual portfolio, I move to inverse-volatility sizing.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/naive_leg_risk.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/naive_leg_risk.png" alt="Realized volatility and average beta of the low- and high-volatility deciles" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Realized volatility and average beta for equal-weight low- and high-volatility baskets before costs.</p>

That imbalance motivates the next step: keep the stock selection fixed and change only the sizing.

## The main implementation: stock-level volatility scaling

I rebalance every three weeks, with the signal trading on the next market day.

To size those positions, I use a separate 60-day volatility estimate, floored at 5%. The allocation uses each stock's own volatility and leaves correlations outside the rule, so the sizing stays easy to inspect.

Within each leg, the allocation starts with an explicit $1/N$ base and then adjusts each stock's position size by its inverse estimated volatility.

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

The 0.20 sets the annualized volatility target in this per-stock scaling step. Lower-volatility stocks receive more size and higher-volatility stocks receive less. The portfolio's realized volatility then emerges from these positions and their correlations. The 4% cap limits concentration. If the initial weights in a leg add up to more than 100% gross, I scale the whole leg down in proportion:

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
    <img src="/assets/2024-12-15-low-volatility-factor/target_exposures.png" alt="Realized long gross, short gross, and net stock exposure through time" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Long gross, short gross, and net stock exposure between three-week rebalances. The variation is floating-position drift.</p>

Across the sample, the low-volatility long averages 97.4% gross and the high-volatility short 34.1%. Total stock gross is 131.5%, leaving the portfolio with +63.4% net stock exposure. The daily path also shows why target exposure and realized exposure are different: prices move after each rebalance, so the weights move with them.

Net stock exposure and market beta answer different questions. Let $$E_t^{\mathrm{net}}$$ be signed stock exposure as a fraction of portfolio value, and let $$\widehat{\beta}_{i,t}$$ be stock $$i$$'s estimated market beta. Then

$$
\begin{aligned}
E_t^{\mathrm{net}} &= \sum_i w_{i,t}, \\
\widehat{\beta}_{p,t} &= \sum_i w_{i,t}\widehat{\beta}_{i,t}.
\end{aligned}
$$

The short book carries less capital, but its stocks have higher market betas, so it offsets much of the long book's beta. The full-sample average ex-ante beta is −0.014 and realized beta is −0.001. The small negative beta is a consequence of the 100% leg ceiling: the long book is close to fully invested, while the short book often cannot provide enough leverage to offset it. I keep beta as a separate diagnostic rather than adding it to the stock-sizing rule.

## A quick beta check

Figure 5 is the quick check I use for market exposure. Beta moves around, but it is slightly negative on average and more negative in the recent window. That matters for the recent result: the Russell 1000 rose sharply while this portfolio was modestly short the market and short the high-volatility end of the universe. The beta mismatch is one source of drag alongside the characteristic loss. An offsetting index-futures position could remove some of that market exposure; I would test it separately because it leaves the characteristic risk unchanged.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/beta_diagnostic_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/beta_diagnostic_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/beta_diagnostic.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/beta_diagnostic.png" alt="Estimated and rolling realized beta of the volatility-scaled portfolio" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Estimated stock beta and rolling 252-day realized beta for the scaled portfolio. Shading marks −0.1 to +0.1.</p>

## Performance, costs, and drawdowns

The tables separate performance from the exposures that produce it. I charge 5 basis points per dollar of stock position traded, including the first portfolio formation. The scaled portfolio turns over 10.4 times its equity base per year, which implies about 0.52% a year in stock-trading costs. Borrow and financing are separate inputs. Returns are annualized arithmetic means; volatility, Sharpe, and drawdown use returns after stock-trading costs.

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
      <td data-label="Reference">3.2%</td>
      <td data-label="Volatility-scaled">7.6%</td>
    </tr>
    <tr>
      <th scope="row">Return, 5 bp</th>
      <td data-label="Reference">2.4%</td>
      <td data-label="Volatility-scaled">7.1%</td>
    </tr>
    <tr>
      <th scope="row">Volatility, 5 bp</th>
      <td data-label="Reference">33.4%</td>
      <td data-label="Volatility-scaled">9.8%</td>
    </tr>
    <tr>
      <th scope="row">Sharpe, 5 bp</th>
      <td data-label="Reference">0.07</td>
      <td data-label="Volatility-scaled">0.73</td>
    </tr>
    <tr>
      <th scope="row">Max drawdown, 5 bp</th>
      <td data-label="Reference">−87.1%</td>
      <td data-label="Volatility-scaled">−38.0%</td>
    </tr>
  </tbody>
</table>

<p class="figure-caption"><strong>Table 1:</strong> Performance from July 1995 to 27 May 2026 with three-week rebalances. Volatility uses 252 trading days; Sharpe assumes zero cash return.</p>

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
      <td data-label="Reference">2.00</td>
      <td data-label="Volatility-scaled">1.31</td>
    </tr>
    <tr>
      <th scope="row">Average stock net</th>
      <td data-label="Reference">0.00</td>
      <td data-label="Volatility-scaled">0.63</td>
    </tr>
    <tr>
      <th scope="row">Realized beta</th>
      <td data-label="Reference">−1.12</td>
      <td data-label="Volatility-scaled">−0.00</td>
    </tr>
    <tr>
      <th scope="row">Annualized turnover</th>
      <td data-label="Reference">14.4× equity</td>
      <td data-label="Volatility-scaled">10.4× equity</td>
    </tr>
  </tbody>
</table>

<p class="figure-caption"><strong>Table 2:</strong> Average daily exposures, full-sample beta versus the Russell 1000, and annualized turnover.</p>

With the same stock selection as the reference, the volatility-scaled implementation produces a 7.1% annualized arithmetic return after costs, 9.8% volatility, and a 0.73 Sharpe. Its cost drag is about 0.5 percentage points a year. Most of the risk reduction comes from changing the weights; stock selection is held fixed.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns.png" alt="Cumulative wealth and drawdowns of the equal-weight reference and volatility-scaled implementation" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 6:</strong> Cumulative wealth and drawdown after 5 bp trading costs, through 27 May 2026. Wealth is above; drawdown is below.</p>

The recent part of the sample is less flattering. From 3 April 2025 through 27 May 2026, the volatility-scaled portfolio lost 10.3% before costs and 10.8% after costs on a compounded basis, while the Russell 1000 gained 31.6%. The long contribution was +3.2 percentage points and the short contribution was −13.5 points. The period overlaps with the AI-led rally, and the mechanism is familiar: the high-volatility side of the universe ran far ahead of the calmer stocks.

In beta terms, the portfolio is short the market. Its average ex-ante stock beta was −0.12 from 3 April 2025 through 27 May 2026, while average net stock exposure remained +68.6%. The distinction matters: the book is long dollars, while the high-beta short leg makes it beta-short. The small negative beta also reflects the 100% upper bound on each leg: the long book is close to fully invested, while the short leg often cannot provide enough leverage to offset all of the long book's market exposure.

## What happened during the largest drawdown?

The most surprising part of the result is the drawdown during the dot-com boom. The scaled portfolio peaks on 8 October 1998 and reaches its trough on 9 March 2000, a 38.0% loss after stock-trading costs over 357 trading days while the Russell 1000 price index gains 50.2%. It recovers its earlier high on 3 April 2001.

This was the dot-com boom. We were long the calmer stocks and short the volatile stocks, while the volatile stocks rallied sharply. On the compounded strategy wealth path, the low-volatility long basket contributed −10.6 percentage points, the high-volatility short basket −26.6 points, and stock-trading costs were another 0.70 points on the initial capital base.

Figure 7 puts both episodes into one view. The left column compares the gross vol-scaled L/S with the Russell 1000; the right column shows the long- and short-leg contributions. The long leg holds the low-volatility basket, and the short leg holds the high-volatility basket. The top row includes both the late-1990s rally and the subsequent unwind. The bottom row ends on 27 May 2026: it shows the strategy lagging during the AI-led rally, before any comparable market sell-off. In both windows, the short leg loses ground because it contains some of the market's strongest winners.

So far, the recent episode shows only one side of the comparison: a rising market, a falling low-volatility portfolio, and a large relative win for the volatile end of the universe. Whether the strategy would behave like it did during the 2000–2001 unwind remains an open question.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/regime_comparison_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/regime_comparison_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/regime_comparison.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/regime_comparison.png" alt="Relative wealth and long and short contributions of the volatility-scaled portfolio in the dot-com and AI-led periods" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 7:</strong> Dot-com and AI-led episodes. Left: vol-scaled L/S versus the Russell 1000. Right: long- and short-leg contributions.</p>

As a quick stock-level check, I traced the P&L back to individual positions over the same window. The three largest long-book losses were New Century Energies (−0.67 percentage points), Evergy Kansas Central (−0.60), and WEC Energy Group (−0.56). On the short side, i2 Technologies (−0.95), Avantax (−0.73), and Ciena (−0.71) hurt most. These numbers are cumulative signed contributions to the strategy's initial capital base, measured in percentage points. For example, i2 Technologies compounded to about 39 times its starting value while it was held, but its largest floating short weight was only about 0.47%, resulting in a −0.95-point contribution.

The pattern is clear: the long book lagged, while a small group of explosive winners drove losses in the short book. The changing, floating weights matter here. A stock can rise several thousand percent during the dates it appears in the basket without producing the same loss as a fixed-size short held from the beginning; the actual contribution depends on the position held each day.

The same check is useful for the recent AI-led window. From 3 April 2025 through 27 May 2026, the largest negative long-book contributions came from Marsh & McLennan (−0.34 percentage points), Roper Technologies (−0.33), and Broadridge Financial Solutions (−0.30). On the short side, Sandisk (−1.14), Lumentum (−0.67), and Micron (−0.59) hurt most. Sandisk compounded by about 829% over the dates it was held, while its largest floating short weight was about 0.83%, so its strategy-level contribution was −1.14 percentage points. This is the same mechanism as in 1998–2000, at a smaller scale: the volatile short basket contained some of the market's strongest winners.

## Conclusion

The ranking is simple. The portfolio is where the important choices enter. Equal weighting makes the risk imbalance visible, while inverse-volatility sizing changes the size of each position without changing the stock selection. In this sample, that produces 9.8% volatility after costs instead of 33.4%, with lower turnover and a less severe drawdown.

The 1998–2000 episode remains the important counterexample. The Russell 1000 rallied, high-volatility stocks rallied even more, and both scaled legs lost money before the subsequent unwind. Figure 7 shows the first part of a similar setup in the recent AI-led rally: a rising market, a beta-short portfolio, and a volatile short leg that ran ahead of the calmer stocks. The sample ends before a comparable crash, so it does not yet tell us whether the factor would recover in the same way. A small futures overlay could offset some market-beta exposure, but it would leave the characteristic risk in place. I would test that separately. The next step I would explore is a constrained optimizer that brings correlations and explicit risk budgets into the allocation. But the immediate question is more basic: if the AI-led winners eventually reverse, will this portfolio recover as it did after 2000, or will the construction create a different problem? That is the next test I would run.
