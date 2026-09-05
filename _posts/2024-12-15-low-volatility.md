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

<p class="article-summary">Buying stable stocks and shorting volatile ones can leave most of the portfolio's risk on the short side. In this backtest, inverse-volatility sizing cuts portfolio volatility from 33% to 10% and turns compounding positive after trading costs. It does so with much less capital in the short book, though rallies in those stocks still cause large drawdowns.</p>

I compare two ways of sizing the same stocks. The first puts equal dollars
behind each position. The second gives smaller positions to stocks with higher
volatility. When the volatile stocks are on the short side, this difference
can determine whether a rally overwhelms the longs.

The ranking comes from the [low-volatility
effect](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865): stable stocks
have tended to earn better risk-adjusted returns than volatile stocks.
[Frazzini and Pedersen](https://www.nber.org/papers/w16601) connect this pattern
to investors' leverage constraints. Neither observation tells me how much
capital to put behind each side of the trade.

Both rules use point-in-time Russell 1000 membership, rebalance every three
weeks, and charge five basis points per dollar traded. Equal weighting gives
each selected stock the same capital within its book. Inverse-volatility sizing
reduces the allocation to stocks whose prices have moved more. Table 1 shows
how much that choice changes the portfolio.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Rule</th><th>Arithmetic return, after costs</th><th>Geometric return, after costs</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Equal-weight</th><td>2.4%</td><td>−3.1%</td><td>33.4%</td><td>0.07</td><td>−87.1%</td><td>14.4×</td></tr>
    <tr><th scope="row"><strong>Inverse-volatility</strong></th><td><strong>7.1%</strong></td><td><strong>6.9%</strong></td><td><strong>9.8%</strong></td><td><strong>0.73</strong></td><td><strong>−38.0%</strong></td><td><strong>10.4×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Key results, 12 July 1995–27 May 2026. Returns, volatility, Sharpe, and two-way turnover are annualized; net results charge 5 bp on traded notional. Turnover sums absolute executed trades relative to strategy capital; Sharpe uses a zero cash rate.</p>

## Portfolio setup

Both portfolios use the same point-in-time universe[^beta-universe]. Signal
volatility and P&L use changes in the vendor-adjusted closing price; the
unadjusted close is used only for the price screen. The beta diagnostic uses
the vendor's separate total-return series, compounded onto the market calendar.
That series also enters data-quality checks; strategy P&L uses adjusted-price changes.

<table class="research-table settings-table">
  <thead>
    <tr><th>Component</th><th>Fixed setting</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Performance window</th><td>12 July 1995–27 May 2026</td></tr>
    <tr><th scope="row">Universe</th><td>Point-in-time Russell 1000; price above $5</td></tr>
    <tr><th scope="row">Ranking signal</th><td>Average volatility over 21, 63, and 126 days</td></tr>
    <tr><th scope="row">Selection</th><td>Lowest decile long; highest decile short</td></tr>
    <tr><th scope="row">Rebalancing</th><td>Every three weeks; execute at the next close</td></tr>
    <tr><th scope="row">Trading cost</th><td>5 bp on traded notional</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Shared setup for both portfolios. Table A1 gives the sizing and risk-estimation parameters.</p>

## Risk and return by decile

At each rebalance, I split the ranking
into ten groups of roughly equal size; each book holds about 100 stocks. The
middle groups show whether the relation between the signal and outcomes changes
smoothly rather than only at the two tails. Figure 1 plots Sharpe, geometric
return, and annualized volatility from the most stable stocks to the most
volatile. Volatility rises and Sharpe falls across the deciles. The
highest-volatility group still has a positive arithmetic return, but it
barely compounds.

<div class="low-vol-figure decile-profile-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/decile_profile" alt="Sharpe ratio, geometric return, and volatility across volatility deciles" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Before-cost Sharpe, annualized geometric return, and annualized volatility by past-volatility decile, July 1995–May 2026. Decile 1 contains the most stable stocks; decile 10 contains the most volatile.</p>

## Equal dollar weights

The reference rule puts one dollar into each book for every dollar of strategy
capital. Because the short stocks were selected for high volatility, the same
dollar allocation produces a much more volatile short book.

<div class="low-vol-figure naive-leg-risk-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/naive_leg_risk" alt="Realised volatility and average beta of the low- and high-volatility deciles" version="10" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Annualized realized volatility (left) and average point-in-time beta (right) for the equal-weight stable-stock long book and volatile-stock short book.</p>

In Figure 2, the high-volatility stocks have more than three times the long
book's standalone volatility and almost three times its beta. Selling them
short reverses the sign of that market exposure. The combined portfolio has a
realized beta of −1.12: equal capital has left a large negative market exposure.

Portfolio volatility depends on the covariance between the books as well as
their standalone risk. Figure 2 shows the sizing problem: the rule
allocates as much capital to its volatile tail as to its stable tail without
accounting for that difference in risk.

## Inverse-volatility weights

The alternative rule makes a stock's position smaller as its
recent volatility rises. A stock with 40% annualized volatility gets half its
equal share before the cap; a stock at the 20% reference keeps its equal share.
The weight is

$$a_{i,t}=\min\left(\frac{1}{N}\times\frac{0.20}{\widehat{\sigma}_{i,t}^{(60)}},\;0.04\right).$$

Here, $N$ is the number of stocks in the book and
$\widehat{\sigma}_{i,t}^{(60)}$ is stock $i$'s annualized volatility over
the past 60 trading days. The 0.20 term is the 20% reference volatility, and
0.04 caps a stock at 4%. The volatility estimate has a 5% floor. If the weights
exceed the 100% book ceiling, the book scales down proportionally. Table A1
gives the remaining parameters.

The rule allows each book to use up to the ceiling. The stable long book stays
near it, while the volatile short book needs less capital to carry similar
risk. Sizing each stock separately leaves portfolio risk, net exposure, and
beta to depend on the resulting combination of holdings.

The target weights drift with prices between rebalances. Figure 3 shows the
resulting capital in each book and the net allocation.

<div class="low-vol-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/target_exposures" alt="Realised long gross, short gross, and net stock exposure through time" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Daily floating long gross, short gross, and net stock exposure for the inverse-volatility portfolio, July 1995–May 2026. The weights include price moves between rebalances.</p>

The long book averages 97% gross exposure and the short book 34%. Their
difference leaves about 63% net stock exposure. Book
volatility is now similar on the two sides: about 10% each. Equal weighting had
left the short book above 37%. These are standalone volatilities at the actual
book sizes. Allocating total portfolio risk between them would also require
their covariance.

Net dollar exposure and market beta measure different things. The smaller
short book contains higher-beta stocks, so it can still offset most of the
larger long book's market exposure. Here a 63% net dollar allocation coexists
with realized market beta close to zero.

Figure 4 compares the beta estimated from current holdings with beta realized
over the trailing year. The holdings estimate can move first; the realized
line reacts slowly because it uses a long return window.

<div class="low-vol-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/beta_diagnostic" alt="Estimated and rolling realised beta of the volatility-scaled portfolio" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Point-in-time beta estimated from current holdings and trailing one-year realized beta for the inverse-volatility portfolio, July 1995–May 2026.</p>

Inverse-volatility sizing also moves realized beta from −1.12 under equal
weights to −0.001. Both full-sample averages in Figure 4 sit near zero, but
neither line stays there. I read this as accidental balance between long and
short market sensitivity. A different period or stock mix can
move the exposure again.

## Portfolio performance

The return path explains the gap between arithmetic and geometric return in
Table 1.[^cash-rate]

The simulator holds quantities fixed between trades and measures daily P&L
against a fixed strategy notional. Figure 5 compounds that normalized daily
series as a performance index. A funded account simulation would also need to
model reinvestment, financing, and borrow payments.

<div class="low-vol-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns" alt="Growth of one dollar on a logarithmic scale and drawdowns for the equal-weight and volatility-scaled long-short portfolios" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Compounded daily P&L per unit of strategy notional (top, logarithmic scale) and drawdown (bottom), July 1995–May 2026, after the 5 bp trading charge.</p>

Equal weighting leaves 38 cents per starting dollar in Figure 5.
Inverse-volatility sizing grows it to 7.78 dollars, although the path still
suffers a 38% maximum drawdown. The arithmetic return of the equal-weight
portfolio is positive, but repeated large moves erode its compounded value.
The sign of the average daily return misses that loss of compounded value.

Several things change together: smaller positions reduce gross exposure,
change the balance of the books, move beta toward zero, and lower turnover.
To isolate the benefit of weighting individual stocks, I would also
compare the rules at matched gross exposure and with the same explicit beta
constraint. Scaling an existing return series to equal volatility would check
the effect of leverage. Evaluating a risk-targeted portfolio would require
replaying its trades.

## Rallies in the short book

Figure 6 examines two periods when the short book lost money during a market
rally: the dot-com episode on the left and April 2025–May 2026 on the right.
The upper panels compare the
portfolio with the Russell 1000; the lower panels split the result into long and
short book contributions. Each column has its own vertical scale. The
vertical line in the dot-com column marks the portfolio trough.

<div class="low-vol-figure regime-comparison-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/regime_comparison" alt="Growth of one dollar in the Russell 1000 and low-volatility portfolio, with long- and short-book contributions during the dot-com rally and the April 2025 to May 2026 rally" version="14" %}
</div>

<p class="figure-caption"><strong>Figure 6:</strong> Before-cost indexed growth for the inverse-volatility portfolio and Russell 1000 (top), with linked long- and short-book contributions in percentage points (bottom). The left column covers the dot-com rally and reversal; the right covers April 2025–May 2026. Scales differ by column.</p>

The dot-com panel is the clearest failure. The market gains about 52% while the
portfolio loses 38%. Most of the loss comes from the short book. The later
reversal brings the portfolio back toward its starting value.

The later episode has the same sign but no reversal in the available sample.
The market gains about 39% while the portfolio loses 13%. Table A2 carries the
exact dates, exposures, beta, and book contributions for both episodes.

The portfolio loses money despite its positive net stock exposure. Estimated
beta is mildly negative in both episodes, while the book contributions locate
most of the damage on the short side. Sector and style attribution would help
explain what those losing short positions have in common.

## Backtest limitations

This is a historical sizing comparison on one three-week calendar. The
[tranching study](/quants/2025/05/10/rebalancing-luck.html) examines calendar
sensitivity in the later, broader Ridge strategy. This low-volatility comparison
uses a single calendar. The five-basis-point charge covers a
proportional trading cost; it omits borrow fees, financing, and market impact.
An expensive or unavailable borrow could make the short book materially harder
to implement than the backtest suggests.

Missing prices are carried forward and a stock that leaves the data is closed
at its last observed price. Missing a subsequent collapse overstates a long
position's return and understates a short position's gain; a buyout above the
last price has the opposite effect. The direction of bias therefore depends on
which book holds the stock and why its data ends. A useful sensitivity test
would identify those exits and apply event-specific terminal returns.

## Where sizing helps

I prefer inverse-volatility sizing here because the equal-weight portfolio
lets the most volatile stocks determine too much of the outcome. Reducing their
capital produces a more balanced pair of books and a better compounded result
under the stated costs. The remaining drawdowns show why that stock-by-stock
rule is only a starting point for portfolio construction.

The next question is how to size the portfolio jointly under explicit risk and
turnover constraints. The [portfolio-optimization
study](/quants/2026/08/29/portfolio-optimization.html) takes up joint sizing
using a broader learned ranking and multiple rebalance schedules. Its return
levels also reflect that different signal and calendar setup.

[^beta-universe]: Requiring a beta estimate keeps the later beta comparison on the same stocks.
[^cash-rate]: The calculations use a zero cash rate, so cash outside stock positions earns no interest.

## Appendix

### Signal formula and parameters

The ranking score averages annualized volatility over three horizons:

$$
v_{i,t}
= \frac{1}{3}\left(
\widehat{\sigma}_{i,t}^{(21)}
+ \widehat{\sigma}_{i,t}^{(63)}
+ \widehat{\sigma}_{i,t}^{(126)}
\right).
$$

Here, $\widehat{\sigma}_{i,t}^{(h)}$ is stock $i$'s annualized volatility
over the last $h$ trading days. I bound the score before ranking so extreme
observations tie at the nearest limit.

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

<p class="table-caption"><strong>Table A1:</strong> Exact signal, selection, sizing, and beta settings. The ranking and sizing volatility estimates use different windows.</p>

### Beta formula

Relative to Russell 1000 return $r_m$, and using the calendar-aligned vendor
total return $r_i$ for each stock, the point-in-time beta estimates are

$$
\widehat{\beta}_{i,t}
=
\frac{\widehat{\operatorname{Cov}}_{252}
\!\left(r_i,r_m\right)}
{\widehat{\operatorname{Var}}_{252}\!\left(r_m\right)},
\qquad
\widehat{\beta}_{p,t}=\sum_i w_{i,t}\widehat{\beta}_{i,t}.
$$

### Rally episodes

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

<p class="table-caption"><strong>Table A2:</strong> Market return, portfolio result, exposure, beta, and book contributions during the two rallies highlighted in Figure 6. Each window starts at the close of the first date. Before-cost book contributions add to the gross portfolio return; the cost row bridges gross and net compounded returns.</p>
