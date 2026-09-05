---
layout: post
title: "Inverse-Volatility Sizing Stops the Short Book Taking Over"
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

<p class="article-summary">A low-volatility stock ranking can produce a very volatile portfolio when its short positions receive the same capital as its longs. Holding the selected stocks and rebalance dates fixed, inverse-volatility sizing cuts portfolio volatility from 33% to 10% and turns compounding positive after the stated trading costs. Most of the change comes with a much smaller short book. That is a useful sizing improvement, but the remaining drawdowns still begin with rallies in the stocks sold short.</p>

The [low-volatility effect](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865)
is the empirical tendency for stable stocks to earn better risk-adjusted returns
than volatile stocks. [Frazzini and
Pedersen](https://www.nber.org/papers/w16601) link the pattern to investors'
leverage constraints. Their explanation motivates the trade; it does not
determine how much capital to put behind it. I start with the lowest-volatility
stocks long and the highest-volatility stocks short, then ask whether equal
weights are a sensible way to express that ranking.

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

<p class="table-caption"><strong>Table 1:</strong> Key results, 12 July 1995–27 May 2026. Returns, volatility, Sharpe, and turnover are annualized; net results charge 5 basis points for every dollar bought or sold. Turnover is purchases plus sales; Sharpe uses a zero cash rate.</p>

## The stock ranking stays fixed

Both portfolios use the same point-in-time universe[^beta-universe]. Signal
volatility and P&L use changes in the vendor-adjusted closing price; the
unadjusted close is used only for the price screen. The beta diagnostic uses
the vendor's separate total-return series, compounded onto the market calendar.
That series also enters data-quality checks, but not the strategy's P&L.

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
    <tr><th scope="row">Trading cost</th><td>5 bp per dollar bought or sold</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Universe, ranking, selection, timing, and cost held fixed across the two sizing rules. Table A1 gives the exact parameter values.</p>

## The ranking separates risk more than return

At each rebalance, I split the ranking
into ten groups of roughly equal size; each book holds about 100 stocks. The
middle groups show whether the relation between the signal and outcomes changes
smoothly rather than only at the two tails. Figure 1 plots Sharpe, geometric
return, and annualized volatility from the most stable stocks to the most
volatile. Volatility rises and Sharpe falls across the deciles. The
highest-volatility group still has a positive arithmetic return, but it
barely compounds. That is enough to keep the ranking fixed while I change the
weights.

<div class="low-vol-figure decile-profile-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/decile_profile" alt="Sharpe ratio, geometric return, and volatility across volatility deciles" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Before-cost Sharpe, annualized geometric return, and annualized volatility by past-volatility decile, July 1995–May 2026. Decile 1 contains the most stable stocks; decile 10 contains the most volatile.</p>

## Equal weights make the short book control risk

The reference rule puts one dollar into each book for every dollar of strategy
capital. Because the short stocks were selected for high volatility, the same
dollar allocation produces a much more volatile short book.

Figure 2 compares realized volatility and beta for the stable-stock long book
and the volatile-stock short book.

<div class="low-vol-figure naive-leg-risk-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/naive_leg_risk" alt="Realised volatility and average beta of the low- and high-volatility deciles" version="10" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Annualized realized volatility (left) and average point-in-time beta (right) for the equal-weight stable-stock long book and volatile-stock short book.</p>

In Figure 2, the high-volatility stocks have more than three times the long
book's standalone volatility and almost three times its beta. Selling them
short reverses the sign of that market exposure. The combined portfolio has a
realized beta of −1.12: equal capital has left a large negative market exposure.

Standalone book volatilities do not add up to portfolio volatility; their
covariance matters too. They nevertheless expose the sizing problem. The rule
allocates as much capital to its volatile tail as to its stable tail without
accounting for that difference in risk.

## Inverse-volatility sizing balances book risk by using less short capital

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

The ceiling is not a target. The stable long book stays near it, while the
volatile short book needs less capital to carry similar risk. This rule sizes
each stock separately; it does not target total portfolio risk, net exposure,
beta, or correlation.

Figure 3 traces daily floating exposure: the target weights move with prices
between rebalances. The long and short panels show capital in each book; the
last panel subtracts short capital from long capital.

<div class="low-vol-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/target_exposures" alt="Realised long gross, short gross, and net stock exposure through time" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Daily floating long gross, short gross, and net stock exposure for the inverse-volatility portfolio, July 1995–May 2026. The weights include price moves between rebalances.</p>

The long book averages 97% gross exposure and the short book 34%. Their
difference leaves about 63% net stock exposure. Book
volatility is now similar on the two sides: about 10% each. Equal weighting had
left the short book above 37%. These are standalone volatilities at the actual
book sizes, rather than an allocation of total portfolio risk to each book.

The smaller short book contains higher-beta stocks, so it can still offset most
of the larger long book's market exposure.

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
short market sensitivity, not beta control. A different period or stock mix can
move the exposure again.

## Sizing cuts risk and restores positive compounding

Table 1 gives the full-sample portfolio comparison. Inverse-volatility sizing
earns more after costs, takes less risk, and trades less.[^cash-rate]

The simulator holds quantities fixed between trades and measures daily P&L
against a fixed strategy notional. Figure 5 compounds that normalized daily
series as a performance index. It is not a cash-account reconstruction with
daily reinvestment, financing, and borrow payments.

Figure 5 plots after-cost growth on a logarithmic scale above drawdown from the
previous peak. Color distinguishes equal-weight and inverse-volatility sizing.

<div class="low-vol-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns" alt="Growth of one dollar on a logarithmic scale and drawdowns for the equal-weight and volatility-scaled long-short portfolios" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 5:</strong> Compounded daily P&L per unit of strategy notional (top, logarithmic scale) and drawdown (bottom), July 1995–May 2026, after the 5 bp trading charge.</p>

Equal weighting leaves 38 cents per starting dollar in Figure 5.
Inverse-volatility sizing grows it to 7.78 dollars, although the path still
suffers a 38% maximum drawdown. The arithmetic return of the equal-weight
portfolio is positive, but repeated large moves erode its compounded value.
That gap is economically more consequential than the sign of its average
daily return.

The result supports the complete sizing rule. It reduces gross exposure,
changes the balance of the books, moves beta toward zero, and lowers turnover
together. To isolate the benefit of weighting individual stocks, I would also
compare the rules at matched gross exposure and with the same explicit beta
constraint. Scaling an existing return series to equal volatility would check
the effect of leverage, but would not reproduce the trades of a risk-targeted
portfolio.

## Volatile-stock rallies remain the failure mode

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

Positive net stock exposure was not enough to offset these losses. Estimated
beta is mildly negative in both episodes, but that alone does not explain their
size. The book contributions locate most of the damage on the short side.
Sector and style attribution would be needed before blaming a particular
growth exposure or treating the later period as evidence of an AI-specific bet.

## What the backtest leaves unresolved

This is a historical sizing comparison on one three-week calendar. The
[tranching study](/quants/2025/05/10/rebalancing-luck.html) examines calendar
sensitivity in the later, broader Ridge strategy; it is not a robustness test
of this low-volatility ranking. The five-basis-point charge covers a
proportional trading cost; it omits borrow fees, financing, and market impact.
An expensive or unavailable borrow could make the short book materially harder
to implement than the backtest suggests.

Missing prices are carried forward and a stock that leaves the data is closed
at its last observed price. Missing a subsequent collapse overstates a long
position's return and understates a short position's gain; a buyout above the
last price has the opposite effect. The direction of bias therefore depends on
which book holds the stock and why its data ends. A useful sensitivity test
would identify those exits and apply event-specific terminal returns.

## The sizing rule I carry forward

I carry inverse-volatility sizing forward because the equal-weight portfolio
lets the most volatile stocks determine too much of the outcome. Reducing their
capital produces a more balanced pair of books and a better compounded result
under the stated costs. The remaining drawdowns show why that stock-by-stock
rule is only a starting point for portfolio construction.

The next question is how to size the portfolio jointly under explicit risk and
turnover constraints. The [portfolio-optimization
study](/quants/2026/08/29/portfolio-optimization.html) takes up joint sizing
using a broader learned ranking and multiple rebalance schedules. Its return
levels should not be compared directly with this single-signal experiment.

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
