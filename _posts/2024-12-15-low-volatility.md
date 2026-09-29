---
layout: post
title: "Sizing a Low-Volatility Portfolio"
description: "How equal weighting and inverse-volatility sizing compare in risk, market exposure and performance."
date: 2024-12-15
last_modified_at: 2026-09-28
interactive_charts: true
categories: ["Signals"]
article_label: Signals · Low volatility
permalink: /quant/2024/12/15/low-volatility-factor.html
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/low-vol-to-portfolio
---

Ranking stocks by volatility is the easy part of a
[low-volatility](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865)
long–short portfolio. I also have to decide how to size the two books, and the
obvious choice, equal weights and equal capital, turns out to be a large bet on
the market. In this article I compare equal weighting with inverse-volatility
sizing, and use a market hedge to separate the sizing from the market exposure
it creates.

The low-volatility effect is the tendency of low-volatility stocks to earn
about as much as volatile ones with far less risk. Frazzini and Pedersen offer
one explanation: investors who cannot easily borrow bid up stocks with more
market exposure, lowering their expected returns.[^bab]

## Returns and risk across volatility deciles
{: #what-the-ranking-selects }

I rank point-in-time Russell 1000 constituents priced above $5 by their
average one-, three- and six-month volatility;
blending horizons gives a steadier ranking and less turnover than any single
window.[^windows] I re-form the deciles every three weeks and trade at the next
close, so every trade uses only information available at the signal. The
backtest assumes the selected shorts can be borrowed.

Figure 1 shows the ten equal-weighted decile portfolios. Compounded returns are
almost flat across the seven least volatile deciles, 10.5–11.6% a year, while
volatility nearly doubles. Beyond that, returns fall: the most volatile decile
compounds at only about a third of a percent a year before costs, and Sharpe
falls from 0.90 in decile 1 to 0.20 in decile 10.

<div class="low-vol-figure decile-profile-figure responsive-figure">
  {% include blog-chart.html chart="deciles" source="/assets/2024-12-15-low-volatility-factor/deciles.json" base="/assets/2024-12-15-low-volatility-factor/decile_profile" mobile="/assets/2024-12-15-low-volatility-factor/decile_profile_mobile" label="Sharpe ratio, annual return and volatility across ten past-volatility deciles, from the least volatile stocks to the most volatile" version="18" %}
</div>


<p class="figure-caption"><strong>Figure 1: More volatile stocks earn less per unit of risk.</strong> Before-cost Sharpe, annual return and volatility, July 1995–May 2026. Each decile is an equal-weighted long portfolio of about 100 stocks; decile 1 has the lowest volatility. Sharpe uses the arithmetic mean daily return and a zero cash rate, so decile 10 keeps a Sharpe of 0.20 with a compounded return near zero.</p>

## Equal capital, unequal risk

The portfolio buys the lowest-volatility decile and shorts the highest, roughly
100 names each. I start with equal weights within each book and 100% of capital
on each side, for 200% gross exposure. As Figure 2 shows, the short book has more
than three times the long book's standalone volatility and almost three times
its ex-ante beta. The portfolio's realized beta is −1.12: equal capital makes
it a large short position in the market.

<div class="low-vol-figure naive-leg-risk-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/naive_leg_risk" mobile="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile" alt="Realized volatility and average beta of the low- and high-volatility deciles" version="13" %}
</div>


<p class="figure-caption"><strong>Figure 2: The short book dominates risk under equal weighting.</strong> Annualized realized volatility and average ex-ante beta, July 1995–May 2026. The high-volatility book's beta is measured before applying the short sign.</p>

## Inverse-volatility sizing
{: #sizing-the-two-books }

I scale each stock's equal-weight allocation by a reference volatility divided
by its estimated volatility. Including a position cap, the absolute allocation is

$$
a_{i,t}=\min\left(\frac{1}{N}\times
\frac{\sigma_{\mathrm{ref}}}{\widehat{\sigma}_{i,t}},\;a_{\max}\right).
$$

Here $N$ is the number of stocks in the book, $\sigma_{\mathrm{ref}}=20\%$
and $a_{\max}=4\%$. I estimate each stock's volatility over about three months,
with a 5% floor.[^windows] If
a book's gross exceeds 100%, I scale it down proportionally; otherwise I leave
it as calculated.

With a 20% reference, the long book comes in at about 97% gross, just under the
100% limit, while the short book shrinks to 34%. Total gross falls from 200% to about
131%, and the portfolio is about 63% net long in dollars. Each book's
standalone volatility is about 10%. Their daily P&L partly offsets, and the
combined portfolio's volatility is also about 10%.

Realized beta is nonetheless roughly zero, largely by coincidence: the
volatility ratio between the two deciles is close to their beta ratio, so sizing
by volatility almost offsets beta.

## Comparing the portfolios with a beta hedge
{: #what-improves }

Because the two rules take such different market exposures, I also hedge each
portfolio's beta with the Russell 1000 at every rebalance, using trailing
ex-ante betas.[^beta-check] Table 1 compares all four.

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 1: Sizing with and without a beta hedge.</strong> 12 July 1995–27 May 2026, after trading costs of 5 bp per dollar traded. Annual return is compounded and volatility annualized; the hedge is financed at no cost. Two-way stock turnover is about 19 times capital a year for equal weighting and 12 for inverse volatility; the hedge adds 1.3 and 0.6.</caption>
  <thead><tr><th>Rule</th><th>Annual return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="5">Unhedged</th></tr>
    <tr><th scope="row">Equal-weight</th><td>−3.3%</td><td>33.4%</td><td>0.07</td><td>−87.8%</td></tr>
    <tr><th scope="row">Inverse-volatility</th><td>6.8%</td><td>9.8%</td><td>0.72</td><td>−38.0%</td></tr>
    <tr class="period-heading"><th colspan="5">Beta hedged at each rebalance</th></tr>
    <tr><th scope="row">Equal-weight</th><td>8.0%</td><td>24.5%</td><td>0.44</td><td>−68.2%</td></tr>
    <tr><th scope="row">Inverse-volatility</th><td>6.6%</td><td>9.8%</td><td>0.70</td><td>−36.8%</td></tr>
  </tbody>
</table>

Hedging lifts equal weighting's Sharpe from 0.07 to 0.44, so its short market
exposure explains much of its weakness, but inverse volatility still reaches
0.70, with 40% of the volatility and about half the drawdown. The hedge
brings realized beta close to zero for both rules.

Hedged equal weighting compounds faster, 8.0% a year against 6.6%, only because
its large long index hedge is financed for free; charging 3% a year on it cuts
that to 4.6%, while inverse volatility, with its small hedge, barely changes.

Figure 3 shows the paths. The hedge removes equal weighting's market bet but not
its deep drawdowns.

<div class="low-vol-figure performance-figure responsive-figure">
  {% include blog-chart.html chart="performance" source="/assets/2024-12-15-low-volatility-factor/performance.json" base="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns" mobile="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile" label="Growth and drawdowns for equal-weight, inverse-volatility and equal-weight with a point-in-time Russell 1000 beta hedge" version="20" %}
</div>


<p class="figure-caption"><strong>Figure 3: Hedging changes the return comparison; the risk gap remains.</strong> Compounded growth (log scale) and drawdown, July 1995–May 2026, after trading costs. The dashed line adds a Russell 1000 hedge to equal weighting at each rebalance; the inverse-volatility line is unhedged, and hedging it changes little (Table 1).</p>

## Losses in strong rallies

The inverse-volatility portfolio's worst periods came in strong rallies.
Figure 4 follows it from its high before two of them. The first window, October
1998 to March 2000, is also its deepest drawdown: the portfolio lost about 38%
before costs while the market rose about 52%. In the second, April 2025 to May
2026, it lost about 12% while the market rose about 39%.

Net market beta explains only 2 to 7 points of either loss, depending on how
beta is measured, so the beta hedge wouldn't have prevented them. Gross
contributions point at the short book: roughly −27 points against −10 for the
longs in the dot-com rally, and −16 against +4 in the later one. But they
include each book's market exposure: a short book's negative market exposure
loses when the market rises. Net
of each book's own beta,[^rally-beta] both books did worse than their betas
implied in the dot-com rally: the longs by about 24 points and the shorts by
about 20.
In the later rally the short book did roughly what its beta implied, and the
shortfall of about 6 points came from the long book.

<div class="low-vol-figure regime-comparison-figure responsive-figure">
  {% include blog-chart.html chart="rally-a" source="/assets/2024-12-15-low-volatility-factor/episodes.json" base="/assets/2024-12-15-low-volatility-factor/regime_comparison" mobile="/assets/2024-12-15-low-volatility-factor/regime_comparison_mobile" label="Panel A: dot-com rally and reversal, with linked book contributions" version="22" %}
  <section class="blog-chart" data-source="{{ '/assets/2024-12-15-low-volatility-factor/episodes.json' | relative_url }}" data-chart="rally-b" aria-label="Panel B: April 2025–May 2026 rally, with linked book contributions">
    <div class="blog-chart-ui" hidden></div>
    <p class="blog-chart-status" role="status"></p>
    <div class="blog-chart-fallback"></div>
  </section>
</div>


<p class="figure-caption"><strong>Figure 4: The portfolio lost in both rallies while the market rose.</strong> Before-cost compounded growth above linked cumulative book contributions in percentage points, gross of each book's market exposure. Episodes run 8 October 1998–9 March 2000 (Panel A continues to 3 April 2001) and 3 April 2025–27 May 2026; realized portfolio betas in the windows are −0.055 and −0.106.</p>

The dot-com loss was temporary: by April 2001 the portfolio was back to roughly
where it started.

## Inverse-volatility sizing is the better rule
{: #from-individual-weights-to-joint-construction }

I'd keep inverse-volatility sizing. Its Sharpe is about 0.7 with or without the
hedge, against 0.44 for equal weighting even after hedging, with less than half
the volatility, about half the drawdown and less turnover. At about 131% gross,
its realized beta also stays near zero without a hedge. Free hedge financing and
the zero cash rate change the absolute returns, not that ranking. Its weak spot
is strong rallies, where the long book lagged its beta both times, and a beta
hedge doesn't fix that.

[^bab]: Andrea Frazzini and Lasse Heje Pedersen, *Betting Against Beta*, *Journal of Financial Economics*, 2014 ([author draft](https://w4.stern.nyu.edu/facdir/lpederse/papers/BettingAgainstBeta.pdf#page=2)). Their mechanism concerns market beta; this article ranks total volatility.

[^windows]: The ranking averages 21-, 63- and 126-session volatility; sizing uses 60 sessions. Ex-ante beta is a stock's trailing 252-session beta; realized beta regresses daily portfolio returns on the Russell 1000.

[^beta-check]: The hedge trades with the stocks at the next close. Costs are 5 bp per dollar traded; funding, borrow fees and delisting returns are excluded.

[^rally-beta]: Summed daily before-cost P&L of each book net of its in-window market beta, so not directly comparable with the linked contributions in Figure 4; ex-ante betas give the same split.
