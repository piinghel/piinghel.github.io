---
layout: post
title: "Sizing a Low-Volatility Portfolio"
description: "How equal weighting and inverse-volatility sizing compare in risk, market exposure and performance."
date: 2024-12-15
last_modified_at: 2026-09-16
show_date: false
categories: ["Signals"]
article_label: Low-volatility · portfolio construction
permalink: /quant/2024/12/15/low-volatility-factor.html
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/low-vol-to-portfolio
---

The [low-volatility effect](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865)
is the tendency for low-volatility stocks to earn better returns per unit of risk
than more volatile stocks. Building a portfolio around it also requires a
choice about position sizing.

In this article, I compare equal weighting with inverse-volatility sizing
and use a market hedge to check how much market exposure matters.

## High-volatility stocks earn less per unit of risk
{: #what-the-ranking-selects }

Let’s start by looking at returns, volatility and Sharpe ratios across
volatility deciles. This gives us a first look at the low-volatility effect
before we move on to building a portfolio.

The low-volatility effect has been studied extensively.
[Blitz and van Vliet](https://repub.eur.nl/pub/10460) document the strong
risk-adjusted returns of low-volatility stocks.
[Frazzini and Pedersen](https://w4.stern.nyu.edu/facdir/lpederse/papers/BettingAgainstBeta.pdf)
offer a related explanation: investors who cannot easily borrow may favour
stocks with more market exposure, bidding up their prices and reducing
their expected returns.[^bab]

I rank point-in-time Russell 1000 constituents priced above $5 by their
average one-, three- and six-month volatility.[^windows] I go long the
lowest-volatility decile and short the highest, with roughly 100 names per
book. I rebalance every three weeks and execute at the next close.

Figure 1 shows the ten equal-weighted decile portfolios, ordered from lowest
to highest volatility. Volatility rises from about 12% to 38%, while Sharpe
falls by almost four-fifths. The highest-volatility decile earns only about
a third of a percent a year before costs. Its return is low relative to its
risk, but still positive over the sample.

<div class="low-vol-figure decile-profile-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/decile_profile" alt="Sharpe ratio, annual return and volatility across ten past-volatility deciles, from the least volatile stocks to the most volatile" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 1: More volatile stocks earn less per unit of risk.</strong> Before-cost Sharpe, annual return and volatility, July 1995–May 2026. Annual return means compounded annual growth throughout this article. Each decile is an equal-weighted long portfolio of about 100 stocks, re-formed every three weeks; decile 1 has the lowest volatility. Volatility rises from 11.9% to 37.9% and Sharpe falls from 0.90 to 0.20.</p>

## Equal capital, unequal risk

I start with equal weights within each book and allocate 100% of strategy
capital to each side, for 200% gross exposure. As Figure 2 shows, the short
book has more than three times the standalone volatility of the long book.
The high-volatility stocks also have almost three times the average beta
of the low-volatility stocks. The resulting portfolio has a realized beta
of −1.12: equal capital produces substantial short market exposure.

<div class="low-vol-figure naive-leg-risk-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/naive_leg_risk" mobile="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile" alt="Realised volatility and average beta of the low- and high-volatility deciles" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 2: The short book dominates risk under equal weighting.</strong> Annualized realized volatility and average point-in-time beta, July 1995–May 2026. The high-volatility book's beta is measured before applying the short sign. The combined portfolio's full-sample realized beta is −1.12.</p>

## Inverse-volatility sizing
{: #sizing-the-two-books }

I scale each stock's equal-weight allocation by a reference volatility divided
by its estimated volatility. Including a position cap, the absolute allocation is

$$
a_{i,t}=\min\left(\frac{1}{N}\times
\frac{\sigma_{\mathrm{ref}}}{\widehat{\sigma}_{i,t}},\;a_{\max}\right).
$$

Here $N$ is the number of stocks in the book, $\sigma_{\mathrm{ref}}=20\%$
and $a_{\max}=4\%$. I estimate volatility over about three months and apply
a 5% floor.[^windows] I cap each book at 100% gross by scaling down its
positions proportionally when needed. Books below the cap retain their
calculated weights.

Without renormalizing each book to 100%, inverse-volatility sizing reduces
the short allocation substantially. The long book averages about 97% gross
and the short book 34%, bringing total gross exposure down from 200% to
about 131%. Both books now have standalone volatility of about 10%, compared
with more than 37% for the equal-weighted short book. Portfolio volatility
also depends on the correlation between the books.

Average net exposure is about 63% long, while full-sample realized beta is
roughly zero. The higher-beta stocks in the smaller short book offset the
long book's market exposure on average, though the offset varies over time.

## Comparing the portfolios with a beta hedge
{: #what-improves }

The two sizing rules also produce very different market exposures. To
assess how much this affects the comparison, I add a Russell 1000 beta hedge
to each portfolio at every rebalance, using trailing beta estimates.
Hedged equal weighting earns more, but remains much more volatile.[^beta-check]

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 1: Sizing with and without a beta hedge.</strong> 12 July 1995–27 May 2026, after trading costs. Return, volatility and turnover are annualized; beta is measured over the full period. Hedged turnover includes index trades.</caption>
  <thead><tr><th>Rule</th><th>Annual return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Beta</th><th>Turnover</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="7">Unhedged portfolios</th></tr>
    <tr><th scope="row">Equal-weight</th><td>−3.3%</td><td>33.4%</td><td>0.07</td><td>−87.8%</td><td>−1.121</td><td>18.78×</td></tr>
    <tr><th scope="row">Inverse-volatility</th><td>6.8%</td><td>9.8%</td><td>0.72</td><td>−38.0%</td><td>−0.001</td><td>12.39×</td></tr>
    <tr class="period-heading"><th colspan="7">Beta hedged at each rebalance</th></tr>
    <tr><th scope="row">Equal-weight</th><td>8.0%</td><td>24.5%</td><td>0.44</td><td>−68.2%</td><td>0.011</td><td>20.10×</td></tr>
    <tr><th scope="row">Inverse-volatility</th><td>6.6%</td><td>9.8%</td><td>0.70</td><td>−36.8%</td><td>0.005</td><td>13.02×</td></tr>
  </tbody>
</table>

The hedge brings realized beta close to zero for both rules: 0.011 for
equal weighting and 0.005 for inverse volatility over the full sample.
Beta can still drift between rebalances.
With the hedge, equal weighting earns about 8% a year versus 6.6% for
inverse volatility, with about two and a half times the volatility.
The comparison includes changes in gross exposure and book allocation as
well as stock weights.

Inverse-volatility sizing reduces portfolio volatility from about 33% to
10% without the hedge, and from about 25% to 10% with it. Sharpe is higher
and maximum drawdown is smaller in both comparisons. Adding a hedge to the
inverse-volatility portfolio makes little difference to either its
volatility or maximum drawdown.

Annual two-way stock turnover is about 12–19 times strategy capital,
counting purchases and sales. The index hedge adds about 0.63 times capital
for inverse volatility and 1.32 for equal weighting. The smaller short
allocation reduces traded notional and transaction costs.

Figure 3 compares the cumulative returns and drawdowns. Hedging raises the
equal-weighted portfolio's terminal index value from 0.35 to 10.84,
compared with 7.54 for unhedged inverse-volatility sizing.
Its maximum drawdown remains much larger: about 68%, versus 38%.
Removing the short market exposure changes the return comparison
substantially, while the difference in risk persists.

<div class="low-vol-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns" mobile="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile" alt="Growth of one dollar and drawdowns for equal-weight, inverse-volatility and equal-weight with a point-in-time Russell 1000 beta hedge" version="16" %}
</div>

<p class="figure-caption"><strong>Figure 3: Hedging changes the return comparison; the risk gap remains.</strong> Growth of $1 (log scale) and drawdown, July 1995–May 2026, after trading costs. The dashed line adds a Russell 1000 hedge to equal weighting at each rebalance. Ending values are 0.35 for equal weighting, 7.54 for inverse volatility and 10.84 for hedged equal weighting.</p>

## Shared losses during market rallies

Figure 4 decomposes the unhedged inverse-volatility portfolio's returns
during two market rallies. Realized beta is modestly negative in both
windows, despite being roughly zero over the full sample. The book-level
contributions show where the losses occur.

<div class="low-vol-figure regime-comparison-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/regime_comparison" mobile="/assets/2024-12-15-low-volatility-factor/regime_comparison_mobile" alt="Growth of one dollar in the Russell 1000 and low-volatility portfolio, with long- and short-book contributions during the dot-com rally and the April 2025 to May 2026 rally" version="17" %}
</div>

<p class="figure-caption"><strong>Figure 4: Short-book losses in two market rallies.</strong> Before-cost indexed growth above linked cumulative book contributions in percentage points. Episode returns run from the first date's close: 8 October 1998–9 March 2000 and 3 April 2025–27 May 2026. Long/short gross contributions are −10.4/−27.1 points and +4.2/−16.3 points, respectively. Realized portfolio betas in these windows are −0.055 and −0.106.</p>

During the dot-com rally, the market gains about 52% while the portfolio
loses about 38% after costs. The short book contributes roughly −27
percentage points before costs, versus −10 from the longs. The later
reversal brings the portfolio back toward its starting value.

In the later rally, the market gains about 39% while the portfolio
loses about 13% after costs. The long book contributes roughly +4 percentage
points and the short book −16 before costs. The short book again accounts
for most of the loss, and the portfolio ends the sample below its
value at the start of the rally.

The long book adds to the dot-com loss but offsets about a quarter of the
short-book loss in the later rally. In both episodes, the short book
dominates losses despite its smaller allocation.

## A simpler baseline
{: #from-individual-weights-to-joint-construction }

Hedged equal weighting earns more at the allocations tested, but inverse
volatility offers a higher Sharpe, lower volatility, smaller drawdowns and
less turnover. Inverse-volatility sizing already seems like a good starting point.

[^bab]: Andrea Frazzini and Lasse Heje Pedersen, *Betting Against Beta*, author draft dated 10 May 2013, physical PDF pages 2–3; published in the *Journal of Financial Economics* in 2014. Their mechanism concerns market beta; this article ranks total volatility. [Public author draft](https://w4.stern.nyu.edu/facdir/lpederse/papers/BettingAgainstBeta.pdf#page=2).

[^windows]: The ranking averages trailing volatility estimates over 21, 63 and 126 sessions. The separate sizing estimate uses 60 sessions, with a 5% annualized volatility floor.

[^beta-check]: At each signal close, the Russell 1000 hedge offsets the sum of stock weights times their trailing betas (252 sessions, at least 126 observations, clipped to [−4, 4]). Stocks and hedge trade at the next close and hold fixed quantities until the next three-week rebalance. Returns start after execution. The simulation applies transaction costs of 5 bp of traded notional; funding, stock borrow fees and futures roll costs are excluded. Returns compound daily P&L per unit of strategy notional; annualization uses 252 sessions.
