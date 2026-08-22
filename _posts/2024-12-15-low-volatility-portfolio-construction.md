---
layout: post
title: "The Low-Volatility Factor: Portfolio Construction Matters"
date: 2024-12-15
last_modified_at: 2026-08-22
show_date: false
categories: [Quant]
article_mark: /assets/brand/low-volatility-mark.svg
article_label: Low-volatility · portfolio construction
permalink: /quant/2024/12/15/low-volatility-factor.html
---

The low-volatility effect is well documented. This article asks a narrower implementation question: once stocks have been ranked by volatility, how should they be weighted in a long/short portfolio? I keep the stock selection fixed and compare equal dollar weights with weights scaled by each stock's own volatility.

Across the US, Europe, and Japan, low-risk equities have historically delivered more return per unit of risk than high-risk peers. [Blitz and van Vliet](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865) document the effect. One explanation is leverage constraints: investors who want more market exposure may buy high-beta securities instead of levering a higher-Sharpe, low-risk portfolio. [Frazzini and Pedersen](https://www.nber.org/papers/w16601) formalize that mechanism in betting against beta.

The comparison is intentionally simple. Equal weighting is a transparent but subjective reference, not the strongest possible alternative. Volatility scaling is the implementation I want to study. In this sample it cuts realized volatility and drawdown substantially, but it also changes gross exposure, net exposure, beta, and turnover. The result therefore compares two complete sizing rules; it does not isolate one mechanical effect while holding every portfolio property constant.

## The tradable universe

I start with the Russell 1000 membership history and apply it point-in-time to daily prices from July 1995 through 27 May 2026. I apply a $5 price filter based on unadjusted prices and require enough return history to estimate the selection signal, sizing volatility, and beta diagnostic. The beta value does not enter the ranking or sizing rule, but its availability is part of this data screen. That leaves 857–1,015 eligible stocks at each rebalance, with a median of 973. Both implementations use that same universe.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/eligible_universe_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/eligible_universe_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/eligible_universe.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/eligible_universe.png" alt="Number of eligible Russell 1000 stocks at each rebalance date" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Eligible stocks after the price and data-availability filters.</p>

The available cross-section is broad and fairly stable. That matters because large changes in portfolio breadth could otherwise make the comparison look like a sizing effect when it is partly a universe effect.

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

The one-, three-, and six-month windows balance responsiveness and stability. Before ranking, I bound the average at 5%–200%; observations outside those limits tie at the boundary.

At each rebalance I split the ranked stocks into ten fixed groups of roughly equal size. Deciles 1 and 10 each contain roughly 100 stocks, making them meaningful slices of the tradable universe. Decile 1 is the long leg and decile 10 is the short leg; the middle deciles show how the results change across the ranking.

<div class="low-vol-figure decile-profile-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/decile_profile_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/decile_profile_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/decile_profile.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/decile_profile.png" alt="Geometric return, volatility, and Sharpe ratio across volatility deciles" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Geometric return, volatility, and Sharpe by volatility decile before costs.</p>

Figure 2 shows the basic trade-off. The plotted geometric return remains positive across all ten deciles, and the underlying arithmetic means are also positive. Realized volatility nevertheless rises sharply and Sharpe ratios deteriorate. For the highest-volatility decile, variance drag reduces a 7.6% arithmetic return to about 0.3% geometric return, with a 0.20 Sharpe. I keep that ranking fixed and change only the allocation from here.

## A simple equal-weight reference

I use equal weighting as a simple control. It exposes the problem immediately: we are long the calmest stocks and short the most volatile ones, yet every stock receives the same dollar weight. The high-volatility leg then carries roughly 38% realized volatility versus 12% for the low-volatility leg. Its average estimated stock beta is also higher, 1.63 versus 0.55. The two legs have the same capital and very different risk. That is why I use inverse-volatility sizing for the implementation.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/naive_leg_risk.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/naive_leg_risk.png" alt="Realized volatility and average beta of the low- and high-volatility deciles" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Risk of the two equal-weight legs before costs.</p>

Figure 3 is the core problem with equal dollars. The high-volatility basket carries more than three times the realized volatility and nearly three times the estimated beta of the low-volatility basket. Equal capital across the two legs therefore does not equalize their risk or market beta. This is why the next experiment changes only the sizing and keeps the stock selection fixed.

## The main implementation: stock-level volatility scaling

I rebalance every three weeks, with the signal trading on the next market day.

To size those positions, I use a separate 60-day volatility estimate, floored at 5%. I use each stock's own volatility and leave correlations out of the sizing rule. That keeps the calculation easy to inspect.

Within each leg, I start with an explicit $1/N$ allocation and then adjust each stock's position size by its inverse estimated volatility. This makes the allocation rule easy to follow: the ranking chooses the stocks, and the volatility estimate determines their relative sizes.

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

Here, 0.20 is a reference volatility, not a forecast of the stock's resulting portfolio risk. A stock estimated at 20% keeps its initial $1/N$ weight, while a stock estimated at 10% receives twice that weight before the cap. Portfolio volatility is then determined by all positions and their correlations. The 4% cap limits concentration. If the initial weights in a leg add up to more than 100% gross, I scale the whole leg down in proportion:

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

<p class="figure-caption"><strong>Figure 4:</strong> Realized long gross, short gross, and net stock exposure between rebalances.</p>

Across the sample, the low-volatility long averages 97.4% gross and the high-volatility short 34.1%. Total stock gross is 131.5%, leaving the portfolio with +63.4% net stock exposure. The daily path also shows why target exposure and realized exposure are different: prices move after each rebalance, so the weights move with them.

The resulting leg risks are much closer than under equal weighting. Realized volatility is 10.5% for the scaled long leg and 10.0% for the scaled short leg, compared with 11.9% and 37.9% under equal weights. This is an achieved outcome of the complete sizing rule, not a separately imposed portfolio-risk target.

Net stock exposure and market beta answer different questions. Let $$E_t^{\mathrm{net}}$$ be signed stock exposure as a fraction of portfolio value, and let $$\widehat{\beta}_{i,t}$$ be stock $$i$$'s estimated market beta. Then

$$
\begin{aligned}
E_t^{\mathrm{net}} &= \sum_i w_{i,t}, \\
\widehat{\beta}_{p,t} &= \sum_i w_{i,t}\widehat{\beta}_{i,t}.
\end{aligned}
$$

The short book carries less capital, but its stocks have much higher market betas, so it offsets most of the long book's beta. The full-sample average ex-ante beta is −0.014 and realized beta is −0.001. Beta is an observed outcome of the chosen weights and the beta gap between the two legs, not an input to the sizing rule. The 100% leg ceiling constrains how far either side can scale, but it does not determine the sign of beta by itself. I therefore keep beta as a separate diagnostic rather than adding it to the stock-sizing rule.

## A quick beta check

Figure 5 is the quick check I use for market exposure. Beta moves around even though the sizing rule itself does not target beta. This matters because being long in dollar terms does not guarantee positive market exposure. An offsetting index-futures position could remove that beta, but I would test it separately because it leaves the stock-selection risk unchanged.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/beta_diagnostic_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/beta_diagnostic_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/beta_diagnostic.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/beta_diagnostic.png" alt="Estimated and rolling realized beta of the volatility-scaled portfolio" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Ex-ante and rolling realized beta of the scaled portfolio.</p>

## Performance, costs, and drawdowns

I separate performance from the exposures that produce it in the tables below. I charge 5 basis points per dollar of stock position traded, including the first portfolio formation. The scaled portfolio turns over 10.4 times its equity base per year, which implies about 0.52% a year in stock-trading costs. Borrow fees, financing, market impact, and taxes are not included. Unused capacity earns zero in the simulation. Returns are annualized arithmetic means; volatility, Sharpe, and drawdown use returns after stock-trading costs. Reported Sharpe is annualized return divided by volatility with a zero cash rate.

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

<p class="figure-caption"><strong>Table 1:</strong> Full-sample performance with three-week rebalancing.</p>

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

<p class="figure-caption"><strong>Table 2:</strong> Full-sample exposure and trading diagnostics.</p>

With the same stock selection as the reference, the volatility-scaled implementation produces a 7.1% annualized arithmetic return after costs, 9.8% volatility, and a 0.73 Sharpe. Its cost drag is about 0.5 percentage points a year. Total portfolio volatility falls by 23.6 percentage points, from 33.4% to 9.8%, but this experiment cannot separate within-leg inverse-volatility weighting from the simultaneous reduction in gross exposure and changes in net exposure and beta.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns.png" alt="Growth of one dollar on a logarithmic scale and drawdowns for the equal-weight and volatility-scaled long-short portfolios" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 6:</strong> After-cost growth of $1 on a log scale, with drawdowns below.</p>

Figure 6 shows the practical difference between the implementations. The equal-weight long/short portfolio has a positive 2.4% arithmetic return after costs, yet repeated large losses leave compounded wealth at only 0.38 times its starting value. That is variance drag, not a contradiction. The volatility-scaled long/short portfolio compounds at 6.9% a year and finishes at 7.78 times its starting value. It still suffers long flat periods and a 38% maximum drawdown, so the improvement is substantial rather than complete.

There are limits to what this comparison establishes. Equal weighting is a subjective and deliberately simple reference. Volatility scaling changes gross exposure, net exposure, beta, and turnover at the same time, so the test does not attribute the result to a single channel. A stronger comparison would also match gross exposure, beta, or realized risk. The signal windows, 60-day sizing window, 20% reference volatility, 4% cap, three-week rebalance interval, and leg ceiling were held fixed rather than stress-tested.

The 5 bp cost assumption covers stock trading only; borrow fees, financing, and market impact are excluded. Beta is observed rather than constrained in both portfolios. These choices make the experiment transparent, but they also define how narrowly its result should be read.

Missing prices are carried forward, and a security that leaves the covered data closes at its last observed value rather than receiving an explicit delisting return. No adverse stale-price or delisting sensitivity is included. Persisting trailing coverage and rerunning the test with a conservative delisting convention is therefore an important data-quality check.

The recent part of the sample is less flattering. From the close on 3 April 2025 through 27 May 2026, the volatility-scaled portfolio lost 12.1% before costs and 12.6% after costs on a compounded basis, while the Russell 1000 gained 38.5%. The gross path consists of a +4.2 percentage-point long contribution and a −16.3-point short contribution; stock-trading costs account for roughly another 0.5 points of loss. The evidence shows that the high-volatility side of the universe ran far ahead of the calmer stocks; assigning that move to a particular market theme would require data not used in this test.

In beta terms, the portfolio is short the market. Its average ex-ante stock beta was −0.12 from 3 April 2025 through 27 May 2026, while average net stock exposure remained +68.6%. The distinction matters: the book is long dollars, but the smaller short leg contains stocks with sufficiently high betas to make the overall portfolio beta-negative. That exposure is not explicitly targeted by the sizing rule.

## Comparing two difficult rallies

The largest drawdown came during the dot-com boom. From its 8 October 1998 peak close to its 9 March 2000 trough close, the scaled portfolio lost 38.0% after stock-trading costs over 357 trading days while the Russell 1000 gained 52.2%. It recovered its earlier high on 3 April 2001. This makes the episode a useful comparison for the 2025–2026 rally, when the portfolio again struggled during a market advance led by high-volatility stocks.

The important detail is the market exposure. The portfolio's average ex-ante beta was −0.07 and its realized beta was −0.06, even though average net stock exposure was +72.0%. We held more dollars long than short, but the high-beta short leg made the portfolio short the market. From the peak close, the calm long basket contributed −10.4 percentage points and the volatile short basket −27.1 points before costs. Stock-trading costs account for another 0.4 points of the peak-to-trough loss. The short leg did most of the damage because the stocks we shorted were among the market's strongest winners.

Figure 7 puts this episode beside the 2025–2026 rally. Every path starts at the close of the first date shown. The left column compares gross portfolio and market wealth; the right column shows additive long- and short-leg contributions to initial capital. In the bottom row, the Russell 1000 gains 38.5% from the 3 April 2025 close through 27 May 2026 while the gross long/short portfolio loses 12.1%.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/regime_comparison_mobile.svg">
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/regime_comparison_mobile.png">
    <source type="image/svg+xml" srcset="/assets/2024-12-15-low-volatility-factor/regime_comparison.svg">
    <img src="/assets/2024-12-15-low-volatility-factor/regime_comparison.png" alt="Portfolio and market wealth beside additive long and short contributions in the 1998 to 2001 and 2025 to 2026 rallies" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 7:</strong> Gross performance and leg contributions in two difficult regimes.</p>

The comparison helps identify a recurring portfolio risk without suggesting that the markets are following the same script. The dot-com window contains a completed boom-and-bust cycle and a much larger loss. The recent window captures a rally and the factor's relative underperformance, while any later reversal remains outside the sample. In both cases, high-volatility stocks led the market while this implementation carried negative beta.

## Conclusion

What stands out in this test is how much the allocation changes the character of the signal. Equal weighting gives both legs the same capital even though their risks are very different. Inverse-volatility sizing addresses that imbalance without changing the stock selection. In this sample, after-cost geometric return changes from −3.1% to 6.9%, volatility from 33.4% to 9.8%, maximum drawdown from −87.1% to −38.0%, and turnover from 14.4× to 10.4× equity. Those differences make the scaled implementation the more practical of these two complete sizing rules. They do not isolate inverse-volatility weighting: gross exposure, net exposure, beta, and turnover all change at the same time.

The result still has an important weakness. Figure 5 shows a portfolio that is usually long dollars but can be short the market in beta terms. The high-volatility stocks in the smaller short leg carry more beta per dollar than the low-volatility long book. That positioning hurt in both episodes discussed here: the dot-com boom and the 2025–2026 rally. The two windows are clearly different—the first includes a full boom-and-bust cycle, while the second currently shows a rally and the factor's underperformance—but the recurring portfolio risk is worth taking seriously.

I would separate those effects before changing the signal. A small index-futures overlay could show how much of the recent weakness comes from market exposure. If the result remained weak after that adjustment, I would look more closely at the short leg: its concentration, correlations, and overlap with the market's strongest winners. A covariance-aware optimizer could bring those risks together, while a turnover-aware implementation could start from current holdings and trade only when the expected improvement justifies the cost. The next test should pair those matched exposure comparisons with adverse stale-price and delisting assumptions. The conclusion here is narrower: stock-level volatility scaling lowers realized risk and drawdown relative to this equal-weight reference, while the two difficult rallies show which risks the simple rule leaves unresolved.
