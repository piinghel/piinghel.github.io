---
layout: post
title: "Sizing a Low-Volatility Portfolio"
description: "The same stock ranking, resized: less short capital, lower risk, and positive compounding."
date: 2024-12-15
last_modified_at: 2026-09-05
show_date: false
categories: ["Low volatility"]
article_label: Low-volatility · portfolio construction
permalink: /quant/2024/12/15/low-volatility-factor.html
github_repositories:
  - label: Research code on GitHub
    url: https://github.com/piinghel/low-vol-to-portfolio
---

<p class="article-summary">Equal capital in a stable-stock long book and a volatile-stock short book creates very unequal risk. Inverse-volatility sizing corrects much of that imbalance here, cutting portfolio volatility from 33% to 10% and turning compounding positive after trading costs. It leaves shared risk uncontrolled, however, and coordinated short-book losses still cause large drawdowns.</p>

Buying stable stocks and shorting volatile ones creates a position-sizing
problem before any portfolio is formed: the two sides were deliberately
selected for different levels of risk. Giving them equal capital allows the
volatile short book to dominate the outcome.

The ranking comes from the [low-volatility
effect](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865): stable stocks
have tended to earn better risk-adjusted returns than volatile stocks.
[Frazzini and Pedersen](https://www.nber.org/papers/w16601) connect this pattern
to investors' leverage constraints. The allocation question is how much
capital to put behind each side.

I compare equal weighting and inverse-volatility sizing on the same stocks.
Both use point-in-time Russell 1000 membership, a price above five dollars,
and average volatility over 21, 63 and 126 days as the ranking signal.
The lowest-volatility decile is long and the highest is short, with roughly
100 names per book. Rebalancing occurs every three weeks, execution at the
next close, and trading costs are 5 bp per dollar traded.

## Equal capital, unequal risk

The equal-weight rule puts one dollar into each book for every dollar of
strategy capital. Figure 1 shows the consequence: the high-volatility stocks
have more than three times the long book's standalone volatility and almost
three times its beta. Shorting them reverses that market exposure, leaving
the combined portfolio with realized beta of −1.12.

<div class="low-vol-figure naive-leg-risk-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/naive_leg_risk" alt="Realised volatility and average beta of the low- and high-volatility deciles" version="10" %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Annualized realized volatility (left) and average point-in-time beta (right) for the equal-weight stable-stock long book and volatile-stock short book, July 1995–May 2026.</p>

Total portfolio risk also depends on covariance between the books. Even before
that joint calculation, the standalone figures identify a clear imbalance:
equal capital gives the deliberately volatile tail far more risk.

## Sizing the two books

Inverse-volatility sizing reduces a stock's allocation as its recent
volatility rises. Before the cap, a stock at 40% annualized volatility receives
half its equal share; a stock at the 20% reference retains its equal share:

$$
a_{i,t}=\min\left(\frac{1}{N}\times
\frac{0.20}{\widehat{\sigma}_{i,t}^{(60)}},\;0.04\right).
$$

Here $N$ is the number of stocks in the book. Volatility is estimated over
60 sessions with a 5% floor, and the position cap is 4%. If a book exceeds
100% gross, its positions scale down proportionally. A smaller book keeps its
lower capital allocation.

This last choice matters. The stable long book averages 97% gross exposure,
while the volatile short book averages 34%. At those actual book sizes, each
has standalone volatility of about 10%; equal weighting had left the short
book above 37%. Similar standalone volatilities do not imply equal contributions
to total portfolio risk, which also depend on covariance.

The capital difference leaves about 63% net stock exposure. Because the smaller
short book contains higher-beta stocks, it still offsets much of the long
book's market sensitivity. Full-sample realized beta moves from −1.12 to
−0.001, but holdings-based and rolling realized estimates vary through time.
That average is an incidental outcome of the weights, not an explicit beta
control.

## What improves

Table 1 shows how much the allocation change matters. Inverse-volatility sizing
reduces volatility from 33.4% to 9.8% and turns geometric return positive.
Turnover also falls. The result makes the sizing decision clear under these
backtest assumptions.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Rule</th><th>Arithmetic return, after costs</th><th>Geometric return, after costs</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Equal-weight</th><td>2.4%</td><td>−3.1%</td><td>33.4%</td><td>0.07</td><td>−87.1%</td><td>14.4×</td></tr>
    <tr><th scope="row"><strong>Inverse-volatility</strong></th><td><strong>7.1%</strong></td><td><strong>6.9%</strong></td><td><strong>9.8%</strong></td><td><strong>0.73</strong></td><td><strong>−38.0%</strong></td><td><strong>10.4×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Results for 12 July 1995–27 May 2026. Returns, volatility, Sharpe and two-way turnover are annualized. Net results charge 5 bp on traded notional; turnover sums absolute executed trades relative to strategy capital. Sharpe uses a zero cash rate.</p>

Figure 2 shows the paths behind those averages. Equal weighting ends at
38 cents per starting dollar despite its positive arithmetic return.
Inverse-volatility sizing reaches 7.78 dollars, although it still suffers
a 38% maximum drawdown. Repeated large moves erode the equal-weight portfolio's
compounded value.

<div class="low-vol-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns" alt="Growth of one dollar on a logarithmic scale and drawdowns for the equal-weight and volatility-scaled long-short portfolios" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Compounded daily P&amp;L per unit of strategy notional (top, log scale) and drawdown (bottom), July 1995–May 2026, after the 5 bp trading charge.</p>

The comparison captures a complete sizing change: individual weights, book
capital, beta and turnover move together. It establishes the benefit of this
allocation rule here; isolating each component would require matched exposure
and constraint comparisons.

## What individual sizing misses

The remaining drawdowns show the limit of treating positions individually.
Figure 3 examines two market rallies when the short book lost heavily:
the dot-com episode and April 2025–May 2026. Each column uses its own scale;
the lower panels locate the return in the long and short books.

<div class="low-vol-figure regime-comparison-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/regime_comparison" alt="Growth of one dollar in the Russell 1000 and low-volatility portfolio, with long- and short-book contributions during the dot-com rally and the April 2025 to May 2026 rally" version="14" %}
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Before-cost indexed growth for the inverse-volatility portfolio and Russell 1000 (top), with linked long- and short-book contributions in percentage points (bottom). The left column covers the dot-com rally and reversal; the right covers April 2025–May 2026. The vertical line marks the dot-com portfolio trough.</p>

During the dot-com rally, the market gains about 52% while the portfolio loses
38% after costs. The short book contributes −27.1 percentage points before
costs, versus −10.4 from the longs. The later reversal brings the portfolio
back toward its starting value.

The recent episode has the same loss direction without a reversal in the
available sample. The market gains about 39%, while the portfolio loses 13%.
Longs contribute +4.2 points and shorts −16.3 before costs. Table A2 gives
the exact windows and contributions.

Positive net stock exposure does not prevent these losses. Estimated beta is
mildly negative in both episodes, but market beta alone does not describe every
risk shared by the short positions. The book contributions establish where
the losses occur. Sector and style attribution would be needed to explain
what those positions have in common.

## From individual weights to joint construction

Inverse-volatility sizing corrects much of the imbalance created by allocating
equal capital to books selected for opposite volatility characteristics.
It is the clear choice in this comparison. The research lesson is what remains:
scaling each stock separately does not explicitly control shared exposures,
market beta or the losses caused when short positions rally together.

The next allocation decision is therefore how to size the holdings jointly,
using covariance and explicit portfolio limits. That addresses a risk the
individual sizing rule never measures. It would still need to be judged by
realized risk, drawdowns and returns after trading costs.

## Research notes

This is one historical comparison on a single three-week calendar. The flat
trading charge omits borrow fees, financing and market impact; expensive or
unavailable borrow could materially change short-book implementation.

The simulator holds quantities fixed between trades and measures daily P&L
against fixed strategy notional. Compounding that series produces the displayed
performance index. A funded account replay would also need reinvestment and
financing assumptions; unallocated cash earns no interest here.

Signal volatility and strategy P&L use vendor-adjusted price changes. The beta
diagnostic uses the vendor's separate total-return series, aligned to the market
calendar. Requiring beta estimates keeps that comparison on the same stocks.

Missing prices are carried forward, and an exit from the data closes at the
last observed price. Missing terminal losses or buyout proceeds can bias either
book's result, depending on the event. An event-specific terminal-return check
would address this limitation.

<table class="research-table settings-table">
  <thead>
    <tr><th>Component</th><th>Exact setting</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Ranking</th><td>21-, 63-, and 126-day annualized volatility; score bounded at 5%–200%</td></tr>
    <tr><th scope="row">Selection</th><td>Decile 1 long; decile 10 short</td></tr>
    <tr><th scope="row">Sizing volatility</th><td>60 days; 5% floor; 20% reference</td></tr>
    <tr><th scope="row">Position and book caps</th><td>4% per stock; 100% gross per book</td></tr>
    <tr><th scope="row">Beta</th><td>252-day window; 126 observations required; stock beta clipped to [−4, 4]</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A1:</strong> Signal, sizing and beta settings. Ranking and sizing use different volatility windows.</p>

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Episode metric</th><th>Dot-com rally</th><th>2025–2026 rally</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Window</th><td>8 Oct 1998–9 Mar 2000</td><td>3 Apr 2025–27 May 2026</td></tr>
    <tr><th scope="row">Russell 1000 return</th><td>52.2%</td><td>38.5%</td></tr>
    <tr><th scope="row">Portfolio return, after costs</th><td>−38.0%</td><td>−12.6%</td></tr>
    <tr><th scope="row">Average net stock exposure</th><td>72.0%</td><td>68.6%</td></tr>
    <tr><th scope="row">Average estimated beta</th><td>−0.07</td><td>−0.12</td></tr>
    <tr><th scope="row">Realized beta</th><td>−0.06</td><td>−0.11</td></tr>
    <tr><th scope="row">Long-book contribution, before costs</th><td>−10.4 pp</td><td>+4.2 pp</td></tr>
    <tr><th scope="row">Short-book contribution, before costs</th><td>−27.1 pp</td><td>−16.3 pp</td></tr>
    <tr><th scope="row">Compounded trading-cost drag</th><td>−0.4 pp</td><td>−0.5 pp</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A2:</strong> Exact rally windows and book contributions for Figure 3. Each window starts at the close of its first date. Before-cost contributions sum to gross compounded return; the trading-cost row bridges gross and net return.</p>
