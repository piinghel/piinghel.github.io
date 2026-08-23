---
layout: post
title: "The Low-Volatility Factor: From Stock Sorts to Portfolio Risk"
date: 2024-12-15
last_modified_at: 2026-08-23
categories: [Quant]
article_label: Low-volatility · portfolio construction
permalink: /quant/2024/12/15/low-volatility-factor.html
github_repositories:
  - label: Research code on GitHub
    url: https://github.com/piinghel/low-vol-to-portfolio
---

<p class="article-summary"><strong>TL;DR:</strong> I buy the calmest volatility decile and short the most volatile. Equal weights produce a 2.4% after-cost arithmetic return, 33.4% volatility, and an 87.1% maximum drawdown. With the same stocks, inverse-volatility weights produce 7.1%, 9.8%, and 38.0%, respectively. Exposure, beta, and turnover also change.</p>

Selection and allocation are separate decisions. The volatility rank chooses the low- and high-volatility baskets; the sizing rule sets each position's capital. Even within those baskets, the stocks have markedly different risk. Equal weighting assigns identical dollars across those different risks, allowing volatile names to dominate portfolio risk. The 4% cap limits concentration while preserving the simple 1/N benchmark.

I therefore test another rule: start from the same 1/N weights and scale each stock by the inverse of its own volatility. Holding stock selection fixed keeps the comparison focused on the sizing rule. The question is how volatility-based sizing changes the resulting portfolio—its return, risk, drawdown, gross and net exposure, beta, and turnover.

The signal has a long history. Low-volatility stocks have earned more return per unit of risk than their more volatile peers across the U.S., Europe, and Japan, as [Blitz and van Vliet](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865) document. The finding runs against the intuition that higher risk should bring higher expected return. Leverage constraints offer one explanation. Investors seeking more market exposure may use high-beta stocks as a substitute for leverage on a higher-Sharpe, low-risk portfolio. [Frazzini and Pedersen](https://www.nber.org/papers/w16601) formalize that mechanism in betting against beta. Here, I take the ranking as given and examine how its stocks should be sized.

## The tradable universe

I start with point-in-time Russell 1000 membership and daily prices from July 1995 through 27 May 2026. Stocks must trade above $5 on an unadjusted basis and have enough history for the selection signal, sizing volatility, and beta diagnostic. The screen requires a beta estimate for consistent diagnostic coverage; the ranking and sizing formulas use volatility alone. The result is 857–1,015 eligible stocks at each rebalance, with a median of 973. Both implementations see exactly the same universe.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/eligible_universe_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/eligible_universe.png" alt="Number of eligible Russell 1000 stocks at each rebalance date" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Eligible stocks after the price and data-availability filters.</p>

The available cross-section is broad and fairly stable. That matters because large changes in portfolio breadth could otherwise make the comparison look like a sizing effect when it is partly a universe effect.

## Measuring and ranking volatility

The ranking is simple: for each stock $$i$$ on signal date $$t$$, I average its annualised realised volatility over the past 21, 63, and 126 trading days. I call that average the stock's volatility score:

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

At each rebalance I split the ranked stocks into ten fixed groups of roughly equal size. Deciles 1 and 10 each contain roughly 100 stocks, making them meaningful slices of the tradable universe. Decile 1 is the long leg and decile 10 is the short leg; the middle deciles show how the results change across the ranking.

<div class="low-vol-figure decile-profile-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/decile_profile_mobile.png?v=2">
    <img src="/assets/2024-12-15-low-volatility-factor/decile_profile.png?v=2" alt="Geometric return, volatility, and Sharpe ratio across volatility deciles" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Sharpe ratio, geometric return, and volatility by volatility decile before costs.</p>

Figure 2 shows why the signal is interesting. Geometric return stays positive across the ten deciles. Volatility rises sharply, and Sharpe deteriorates. In the highest-volatility decile, a 7.6% arithmetic return compounds to only about 0.3% a year. The gap is the cost of compounding volatile returns—variance drag. From here on I leave this ranking alone and change only the allocation.

## Equal-weight benchmark

Equal weighting makes a useful control precisely because its flaw is visible. The screened Russell 1000 names are liquid enough for a simple 1/N allocation, and equal weights keep the benchmark from quietly becoming a large-cap portfolio. I am long the calmest stocks and short the most volatile ones, while giving every stock the same dollar weight. The high-volatility leg then carries roughly 38% realized volatility versus 12% for the low-volatility leg; its average estimated beta is 1.63 versus 0.55. The capital is equal; the risk differs sharply. That is the imbalance inverse-volatility sizing is meant to address.

<div class="low-vol-figure naive-leg-risk-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/naive_leg_risk.png" alt="Realized volatility and average beta of the low- and high-volatility deciles" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Risk of the two equal-weight legs before costs.</p>

Figure 3 puts numbers on that imbalance. Equal capital leaves the high-volatility basket with more than three times the realized volatility and nearly three times the estimated beta of the calm basket. The next experiment keeps the selected stocks fixed and changes their sizes.

## Volatility scaling

To size those positions, I use a separate 60-day volatility estimate and treat any estimate below 5% as 5%. The rule handles each stock independently, which keeps the calculation easy to inspect. A full portfolio risk model would also estimate correlations and size the positions jointly.

I rebalance every three weeks and trade the signal at the next market close.

Within each leg, I start with an explicit $1/N$ allocation and then adjust each stock's position size by its inverse estimated volatility. This makes the allocation rule easy to follow: the ranking chooses the stocks, and the volatility estimate determines their relative sizes.

The sizing rule follows the same logic. Each leg starts with equal dollar weights. I then multiply each stock's weight by 20% divided by its own 60-day volatility: a stock estimated at 10% volatility receives twice the preliminary weight of one estimated at 20%. The position cap is 4%, and a leg above 100% gross exposure is scaled down proportionally. In notation, for leg $$\ell\in\{L,H\}$$, selected-stock set $$\mathcal S_{\ell,t}$$, and stock count $$N_{\ell,t}=\lvert\mathcal S_{\ell,t}\rvert$$:

$$
\begin{aligned}
a_{i,\ell,t}^{\mathrm{pre}}
&=\frac{1}{N_{\ell,t}}
\times \frac{0.20}{\widehat{\sigma}_{i,t}^{(60)}}, \\
a_{i,\ell,t}
&=\min\left(a_{i,\ell,t}^{\mathrm{pre}},\;0.04\right).
\end{aligned}
$$

Here, 0.20 is the reference volatility used to scale individual positions. A stock estimated at 20% keeps its initial $1/N$ weight, while a stock estimated at 10% receives twice that weight before the cap. The portfolio's realized risk still depends on every position and the correlations between them. The 4% cap limits concentration. If the initial weights in a leg add up to more than 100% gross, I scale the whole leg down in proportion:

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

The 100% leg limit is a ceiling. A volatile short basket can therefore shrink to 30% or 40% of portfolio value, preserving the risk adjustment. The final portfolio risk emerges from these stock-level weights and their realized correlations.

## Resulting exposures

Inverse-volatility sizing is uneven by design. The low-volatility long book receives more capital, while the high-volatility short book naturally becomes smaller.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/target_exposures_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/target_exposures.png" alt="Realized long gross, short gross, and net stock exposure through time" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Realized long gross, short gross, and net stock exposure between rebalances.</p>

Across the sample, the low-volatility long averages 97.2% gross and the high-volatility short 34.0%. Total stock gross is 131.1%, leaving +63.2% net stock exposure. These daily floating weights include the drift created by price moves between rebalances.

The resulting leg risks are much closer than under equal weighting. Realized volatility is 10.5% for the scaled long leg and 10.0% for the scaled short leg, compared with 11.9% and 37.9% under equal weights. The sizing rule produces this balance indirectly through individual stock volatilities; portfolio-level risk remains unconstrained.

Net stock exposure and market beta answer different questions. Let $$E_t^{\mathrm{net}}$$ be signed stock exposure as a fraction of portfolio value, and let $$\widehat{\beta}_{i,t}$$ be stock $$i$$'s estimated market beta. Then

$$
\begin{aligned}
E_t^{\mathrm{net}} &= \sum_i w_{i,t}, \\
\widehat{\beta}_{p,t} &= \sum_i w_{i,t}\widehat{\beta}_{i,t}.
\end{aligned}
$$

The short book carries less capital. Its stocks have much higher market betas, which offset most of the long book's beta. The full-sample average ex-ante beta is −0.014 and realized beta is −0.001. Beta emerges from the chosen weights and the beta gap between the legs. The 100% leg ceiling constrains how far either side can scale. The stocks inside the legs determine the sign. I therefore track beta as a separate portfolio diagnostic.

Figure 5 is my quick check on market exposure. The sizing rule controls individual volatility. Portfolio beta remains free. Dollar exposure and market exposure can therefore point in different directions. An index-futures overlay could target beta directly while leaving the stock ranking intact. I would evaluate that as a separate allocation decision.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/beta_diagnostic_mobile.png">
    <img src="/assets/2024-12-15-low-volatility-factor/beta_diagnostic.png" alt="Estimated and rolling realized beta of the volatility-scaled portfolio" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Ex-ante and rolling realized beta of the scaled portfolio.</p>

## Performance, costs, and drawdowns

The tables separate performance from the exposures that produce it. I charge 5 basis points per dollar traded, including the first portfolio formation, as a rough approximation of stock-trading costs. At 10.4 times annual turnover, that reduces the scaled portfolio's return by about 0.52 percentage points a year.

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
      <td data-label="Volatility-scaled">1.23</td>
    </tr>
    <tr>
      <th scope="row">Average stock net</th>
      <td data-label="Equal-weight reference">0.00</td>
      <td data-label="Volatility-scaled">0.58</td>
    </tr>
    <tr>
      <th scope="row">Realized beta</th>
      <td data-label="Equal-weight reference">−1.12</td>
      <td data-label="Volatility-scaled">−0.022</td>
    </tr>
    <tr>
      <th scope="row">Annualized turnover</th>
      <td data-label="Equal-weight reference">14.4× equity</td>
      <td data-label="Volatility-scaled">11.5× equity</td>
    </tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Full-sample exposure and trading diagnostics.</p>

Against the equal-dollar diagnostic, the volatility-scaled implementation produces a 7.1% annualized arithmetic return after costs, 9.8% volatility, and a 0.73 Sharpe. Its cost drag is about 0.5 percentage points a year. Total portfolio volatility falls by 23.6 percentage points, from 33.4% to 9.8%. The improvement reflects the full sizing change: lower gross exposure, positive net exposure, and a different beta arrive together with the inverse-volatility weights.

<div class="low-vol-figure performance-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile.png?v=5">
    <img src="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns.png?v=5" alt="Growth of one dollar on a logarithmic scale and drawdowns for the equal-weight and volatility-scaled long-short portfolios" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 6:</strong> After-cost growth of $1 on a log scale, with drawdowns below.</p>

Figure 6 shows the practical difference between the implementations. The equal-weight long/short portfolio has a positive 2.4% arithmetic return after costs. Repeated large losses leave compounded wealth at only 0.38 times its starting value. That gap is variance drag. The volatility-scaled long/short portfolio compounds at 6.9% a year and finishes at 7.78 times its starting value. Long flat periods and a 38% maximum drawdown remain. The improvement is substantial and incomplete.

The benchmark makes the first point plainly: large differences in stock-level volatility produce an incoherent risk allocation when every name receives the same dollars. The scaled portfolio's improvement reflects several linked mechanisms. Volatility scaling changes gross exposure, net exposure, beta, and turnover at the same time. Matched tests at equal gross exposure, beta, and realized risk would separate those mechanisms. I held the signal windows, 60-day sizing window, 20% reference volatility, 4% cap, three-week rebalance interval, and leg ceiling fixed throughout.

The 5 bp cost assumption approximates routine stock trading. Borrow fees, financing, market impact, and taxes would lower implementable returns, especially on the short side. Both portfolios also allow beta to float. The result describes a transparent test of inverse-volatility sizing against a naïve diagnostic; a fully financed, capacity-aware strategy would require those additional costs and constraints.

Missing prices are carried forward, and a security that leaves the covered data closes at its last observed value. This convention can make losses look too mild when the final stale price precedes an adverse delisting. Persisting trailing coverage and rerunning the test with a conservative delisting return would show how much that data choice matters.

## When the short book rallies

From 3 April 2025 through 27 May 2026, the scaled portfolio lost 12.1% before costs and 12.6% after costs. The Russell 1000 gained 38.5%. The long book contributed +4.2 percentage points, and the short book −16.3 points. Trading costs added roughly 0.5 points of loss. Average net stock exposure was +68.6%, while ex-ante beta was −0.12. The smaller short book held stocks with much higher betas. Those stocks led the rally and drove the loss.

The largest drawdown came during the dot-com boom. From 8 October 1998 to 9 March 2000, the scaled portfolio lost 38.0% after costs. The Russell 1000 gained 52.2%. Average net exposure was +72.0%. Ex-ante beta was −0.07, and realized beta −0.06. The long book contributed −10.4 points and the short book −27.1 points before costs. Trading costs added 0.4 points. The portfolio recovered its earlier high on 3 April 2001.

Figure 7 places the two periods side by side. Each path starts at the first close shown. The left column compares gross portfolio and market wealth. The right column shows long- and short-book contributions.

<div class="low-vol-figure">
  <picture>
    <source media="(max-width: 768px)" srcset="/assets/2024-12-15-low-volatility-factor/regime_comparison_mobile.png?v=2">
    <img src="/assets/2024-12-15-low-volatility-factor/regime_comparison.png?v=2" alt="Portfolio and market wealth beside additive long and short contributions in the 1998 to 2001 and 2025 to 2026 rallies" loading="lazy" decoding="async">
  </picture>
</div>

<p class="figure-caption"><strong>Figure 7:</strong> Gross performance in two difficult regimes. Combined wealth starts at 1×; additive long and short contributions start at 0× and sum to the strategy's gross wealth change.</p>

The comparison identifies a recurring portfolio risk across two different markets. The dot-com window contains a completed boom-and-bust cycle and a much larger loss. The recent window captures a rally and the factor's relative underperformance through May 2026. In both cases, high-volatility stocks led the market while this implementation carried negative beta. The shared exposure is informative; the surrounding market narratives remain different.

## Conclusion

The main lesson is that stock-level risk deserves an explicit allocation rule after ranking. Equal dollars allow volatile names to dominate the portfolio; inverse-volatility sizing addresses that imbalance while holding stock selection constant. In this sample, after-cost geometric return moves from −3.1% to 6.9%, volatility from 33.4% to 9.8%, maximum drawdown from −87.1% to −38.0%, and turnover from 14.4× to 10.4× equity. The intentionally naïve benchmark shows how badly equal dollars can misrepresent a volatility signal. These figures describe the complete scaled implementation and its combined exposure changes.

The chief remaining risk is clear. The portfolio can be long dollars and short the market in beta terms. That exposure hurt during the dot-com boom and the 2025–2026 rally.

The next step is a better risk model. A covariance estimate would model how positions move together and size the portfolio as a whole. Explicit constraints could control beta, net exposure, gross exposure, and concentration. A turnover penalty could start from current holdings and trade only when the expected risk improvement justifies the cost. I would test that model against matched versions of the present rule at equal gross exposure, beta, and realized risk, then repeat the comparison with conservative stale-price and delisting assumptions.

This study provides the baseline for that work. Stock-level volatility scaling lowers realized risk and drawdown relative to equal weighting, while the two difficult rallies expose the risks it leaves unmanaged: correlations inside the short book, time-varying beta, financing and borrow costs, and imperfect exit data.
