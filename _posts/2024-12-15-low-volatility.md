---
layout: post
title: "Inverse-Volatility Sizing Stops the Short Book Taking Over"
date: 2024-12-15
last_modified_at: 2026-09-02
show_date: false
categories: ["Low volatility"]
article_label: Low-volatility · portfolio construction
permalink: /quant/2024/12/15/low-volatility-factor.html
github_repositories:
  - label: Research code on GitHub
    url: https://github.com/piinghel/low-vol-to-portfolio
---

<p class="article-summary">Equal dollars do not mean equal risk in a portfolio with a long book (stocks bought) and a short book (stocks sold short). The short book takes over an equal-weight strategy. I hold the stocks and rebalance dates fixed, then size each position inversely to its recent volatility. Portfolio volatility falls from 33% to 10%, and compounding turns positive.</p>

The [low-volatility effect](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865)
is the empirical tendency for stable stocks to earn better risk-adjusted returns
than volatile stocks. [Frazzini and
Pedersen](https://www.nber.org/papers/w16601) link the pattern to investors'
leverage constraints. This article starts the portfolio-construction series by
asking a narrower question: once the ranking is fixed, how should I size the
stocks?

The state of the strategy is simple: point-in-time Russell 1000 stocks, a
past-volatility ranking, the lowest decile long, the highest decile short, three-week
rebalancing, and a five-basis-point trading cost. Only position size changes.

Table 1 puts the implementable comparison at the top. The equal-weight rule
allocates the same dollars to every selected stock. The inverse-volatility rule
allocates less to stocks whose prices have moved more.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Rule</th><th>Arithmetic return, before costs</th><th>Arithmetic return, after costs</th><th>Geometric return, after costs</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Equal-weight</th><td data-label="Arithmetic return, before costs">3.2%</td><td data-label="Arithmetic return, after costs">2.4%</td><td data-label="Geometric return, after costs">−3.1%</td><td data-label="Net volatility">33.4%</td><td data-label="Net Sharpe">0.07</td><td data-label="Maximum drawdown">−87.1%</td><td data-label="Turnover">14.4×</td></tr>
    <tr><th scope="row"><strong>Inverse-volatility</strong></th><td data-label="Arithmetic return, before costs"><strong>7.6%</strong></td><td data-label="Arithmetic return, after costs"><strong>7.1%</strong></td><td data-label="Geometric return, after costs"><strong>6.9%</strong></td><td data-label="Net volatility"><strong>9.8%</strong></td><td data-label="Net Sharpe"><strong>0.73</strong></td><td data-label="Maximum drawdown"><strong>−38.0%</strong></td><td data-label="Turnover"><strong>10.4×</strong></td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Key results, September 1998–May 2026. Returns, volatility, Sharpe, and turnover are annualized; net results charge 5 basis points for every dollar bought or sold. Turnover is purchases plus sales.</p>

## The stock ranking stays fixed

Both portfolios use the same point-in-time universe[^beta-universe] and adjusted
closing prices. Vendor total returns, including distributions, drive P&L. The
unadjusted close is used only for the price screen.

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Component</th><th>Fixed setting</th><th>Role in the test</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Data window</th><td data-label="Fixed setting">July 1995–27 May 2026</td><td data-label="Role in the test">Provides signal history and the investable sample.</td></tr>
    <tr><th scope="row">Universe</th><td data-label="Fixed setting">Point-in-time Russell 1000; price above $5</td><td data-label="Role in the test">Uses the membership and information available on each date.</td></tr>
    <tr><th scope="row">Ranking signal</th><td data-label="Fixed setting">Average volatility over 21, 63, and 126 days</td><td data-label="Role in the test">Orders stocks from stable to volatile.</td></tr>
    <tr><th scope="row">Selection</th><td data-label="Fixed setting">Lowest decile long; highest decile short</td><td data-label="Role in the test">Holds the same stocks under both sizing rules.</td></tr>
    <tr><th scope="row">Rebalancing</th><td data-label="Fixed setting">Every three weeks; execute at the next close</td><td data-label="Role in the test">Keeps the portfolio calendar and execution lag fixed.</td></tr>
    <tr><th scope="row">Trading cost</th><td data-label="Fixed setting">5 bp per dollar bought or sold</td><td data-label="Role in the test">Turns executed trades into the net result.</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Universe, ranking, selection, timing, and cost held fixed across the two sizing rules. Table A1 gives the exact parameter values.</p>

## The ranking separates risk more than return

Does the ranking separate anything worth trading? At each rebalance, I split it
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

<p class="figure-caption"><strong>Figure 1:</strong> Before-cost Sharpe, annualized geometric return, and annualized volatility by past-volatility decile. Decile 1 contains the most stable stocks; decile 10 contains the most volatile.</p>

## Equal weights make the short book control risk

Why does one dollar long for each dollar short create unequal risk? The
reference rule gives every selected stock the same dollar weight and sets both
books to the same capital. The short book was selected for high volatility, so
equal capital loads more risk into that book.

Figure 2 compares realized volatility and beta for the stable-stock long book
and the volatile-stock short book.

<div class="low-vol-figure naive-leg-risk-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/naive_leg_risk" alt="Realised volatility and average beta of the low- and high-volatility deciles" version="10" %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Annualized realized volatility (left) and average point-in-time beta (right) for the equal-weight stable-stock long book and volatile-stock short book.</p>

The short book carries more than three times the long book's volatility and
almost three times its beta. Equal weighting therefore turns a stock-ranking
idea into a large short-book risk position. Its long and short books average
11.9% and 37.9% volatility. Both books average 100.0% gross exposure, leaving
the portfolio at 200.0% gross, 0.0% net exposure, and −1.12 realized beta. I
don't want one book to make most of the portfolio's risk decision.

## Inverse-volatility sizing balances book risk by using less short capital

How much capital does the short book need once each stock carries comparable
stand-alone risk? The alternative rule makes a stock's position smaller as its
recent volatility rises. A stock with 40% annualized volatility gets half its
equal share before the cap; a stock at the 20% reference keeps its equal share.
The weight is

$$a_{i,t}=\min\left(\frac{1}{N}\times\frac{0.20}{\widehat{\sigma}_{i,t}^{(60)}},\;0.04\right).$$

Here, \(N\) is the number of stocks in the book and
\(\widehat{\sigma}_{i,t}^{(60)}\) is stock \(i\)'s annualized volatility over
the past 60 trading days. The 0.20 term is the 20% reference volatility, and
0.04 caps a stock at 4%. If the weights exceed the 100% book ceiling, I scale
the book down proportionally. Table A1 gives the other exact parameters.

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

<p class="figure-caption"><strong>Figure 3:</strong> Daily floating long gross, short gross, and net stock exposure for the inverse-volatility portfolio, September 1998–May 2026. The weights include price moves between rebalances.</p>

The long book averages 97.2% gross exposure, while the short book averages
34.0%. That leaves the portfolio at 131.1% gross and +63.2% net exposure. Book
volatility is almost balanced at 10.5% long and 10.0% short, compared with
11.9% and 37.9% under equal weights. That is the book-level fix I wanted.

The smaller short book contains higher-beta stocks, so it can still offset most
of the larger long book's market exposure.

Figure 4 compares the beta estimated from current holdings with beta realized
over the trailing year. The holdings estimate can move first; the realized
line reacts slowly because it uses a long return window.

<div class="low-vol-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/beta_diagnostic" alt="Estimated and rolling realised beta of the volatility-scaled portfolio" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Point-in-time beta estimated from current holdings and trailing one-year realized beta for the inverse-volatility portfolio, September 1998–May 2026.</p>

Inverse-volatility sizing also moves realized beta from −1.12 under equal
weights to −0.001. Both full-sample averages in Figure 4 sit near zero, but
neither line stays there. I read this as accidental balance between long and
short market sensitivity, not beta control. A different period or stock mix can
move the exposure again.

## Sizing cuts risk and restores positive compounding

Does the book-level balance improve the whole portfolio? Table 1 gives the
full-sample comparison. Inverse-volatility sizing earns more after costs, takes
less risk, and trades less. The calculations use a zero cash rate, so cash
outside stock positions earns no interest.

Figure 5 plots after-cost growth on a logarithmic scale above drawdown from the
previous peak. Color distinguishes equal-weight and inverse-volatility sizing.

<div class="low-vol-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns" alt="Growth of one dollar on a logarithmic scale and drawdowns for the equal-weight and volatility-scaled long-short portfolios" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 5:</strong> After-cost growth of $1 on a logarithmic scale (top) and drawdown in percent (bottom) for equal-weight and inverse-volatility sizing, September 1998–May 2026.</p>

Look at the endpoints and the deepest losses. Equal weighting leaves 38 cents
per starting dollar; that is enough to reject it as the baseline.
Inverse-volatility sizing grows the dollar to $7.78, though the path still
suffers a 38% maximum drawdown. Volatility drag explains the gap between
arithmetic return and compounding. In the decile check, a 33%-volatility
portfolio with a 7.6% arithmetic return compounds at only 0.3% a year.

Sizing changes four things at once, so I can't say which one drives the gain.
It reduces gross exposure, makes net exposure positive, moves beta toward zero,
and lowers turnover. Less negative beta or simple deleveraging could explain
part of the gain. I would need matched tests at the same gross exposure, beta,
and realized volatility to tell.

## Volatile-stock rallies remain the failure mode

Where does the rule still break? Figure 6 compares two rallies in volatile
growth stocks. The dot-com episode is
on the left and the recent AI rally on the right. The upper panels compare the
portfolio with the Russell 1000; the lower panels split the result into long and
short book contributions. Each column has its own vertical scale. The
vertical line in the dot-com column marks the portfolio trough.

<div class="low-vol-figure regime-comparison-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/regime_comparison" alt="Growth of one dollar in the Russell 1000 and low-volatility portfolio, with long- and short-book contributions during the dot-com rally and the 2025 to 2026 AI rally" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 6:</strong> Before-cost growth of $1 for the inverse-volatility portfolio and Russell 1000 (top), with long- and short-book return contributions in percentage points (bottom). The left column covers the dot-com rally and reversal; the right covers the April 2025–May 2026 AI rally. Scales differ by column.</p>

The dot-com panel is the clearest failure. The market gains about 52% while the
portfolio loses 38%. Most of the loss comes from the short book. The later
reversal brings the portfolio back toward its starting value.

The recent episode has the same sign but no reversal in the available sample.
The market gains about 39% while the portfolio loses 13%. Table A4 carries the
exact dates, exposures, beta, and book contributions for both episodes.

Positive net stock exposure offers no protection because the portfolio's beta
is negative in both rallies. Sector or growth-style concentration inside the
volatile short book could explain the losses. The book contributions put the
loss in the short book, but I can't tell which of those exposures drove it.

## The rule fixes book risk, not the full portfolio

Inverse-volatility sizing does what it was designed to do: it balances
long- and short-book volatility. It leaves gross exposure, net exposure, beta, and
correlation uncontrolled.

The backtest also uses one three-week calendar. The later
[tranching study](/quants/2025/05/10/rebalancing-luck.html) found that three
staggered sleeves left mean return almost unchanged while narrowing dispersion
across starting weeks. A five-basis-point cost omits market impact and borrow,
which matter most in the volatile short book.

Finally, missing prices are carried forward and a stock that leaves the data is
closed at its last observed price. A stale price before a bad delisting would
understate the loss. I would rerun the backtest with a conservative delisting
return to see how much that matters.

## Conclusion

I use inverse-volatility sizing as the next baseline. It keeps the same stocks,
stops the volatile short book dominating risk, and compounds better after the
stated costs.

What this does not show: gross exposure, net exposure, beta, correlation,
turnover, and total risk all change together. I can't say which one drives the
gain. The test also uses one rebalance calendar and simplified trading and
delisting costs. Those limitations could change the size of the advantage.

The next question is how to size the portfolio jointly under explicit risk and
turnover constraints. The [portfolio-optimization
study](/quants/2026/08/29/portfolio-optimization.html) runs that test using the
same ranking discipline and multiple rebalance schedules.

[^beta-universe]: Requiring a beta estimate keeps the later beta comparison on the same stocks.

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

Here, \(\widehat{\sigma}_{i,t}^{(h)}\) is stock \(i\)'s annualized volatility
over the last \(h\) trading days. I bound the score before ranking so extreme
observations tie at the nearest limit.

[NEEDS INPUT: Why were the ranking horizons and bounds, sizing window and
floor, reference volatility, caps, and beta settings chosen? The current
article explains what they do but not why these exact values were used.]

<table class="research-table comparison-table portfolio-card-table">
  <thead>
    <tr><th>Component</th><th>Exact setting</th><th>Why</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Ranking</th><td data-label="Exact setting">21-, 63-, and 126-day annualized volatility; score bounded at 5%–200%</td><td data-label="Why">Orders the universe while limiting isolated extremes.</td></tr>
    <tr><th scope="row">Selection</th><td data-label="Exact setting">Decile 1 long; decile 10 short</td><td data-label="Why">Keeps the most stable and volatile tails.</td></tr>
    <tr><th scope="row">Sizing volatility</th><td data-label="Exact setting">60 days; 5% floor; 20% reference</td><td data-label="Why">Scales each stock inversely to recent volatility.</td></tr>
    <tr><th scope="row">Position and book caps</th><td data-label="Exact setting">4% per stock; 100% gross per book</td><td data-label="Why">Limits concentration and capital on either side.</td></tr>
    <tr><th scope="row">Beta</th><td data-label="Exact setting">252-day window; 126 observations required; stock beta clipped to [−4, 4]</td><td data-label="Why">Measures market sensitivity using information available on each date.</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A1:</strong> Exact signal, selection, sizing, and beta settings. The ranking and sizing volatility estimates use different windows.</p>

### Beta formula

Relative to Russell 1000 return \(r_m\), the point-in-time stock and portfolio
beta estimates are

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
    <tr><th>Episode metric</th><th>Dot-com rally</th><th>AI rally</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Window</th><td data-label="Dot-com rally">8 Oct 1998–9 Mar 2000</td><td data-label="AI rally">3 Apr 2025–27 May 2026</td></tr>
    <tr><th scope="row">Russell 1000 return</th><td data-label="Dot-com rally">52.2%</td><td data-label="AI rally">38.5%</td></tr>
    <tr><th scope="row">Portfolio return, after costs</th><td data-label="Dot-com rally">−38.0%</td><td data-label="AI rally">−12.6%</td></tr>
    <tr><th scope="row">Average net stock exposure</th><td data-label="Dot-com rally">72.0%</td><td data-label="AI rally">68.6%</td></tr>
    <tr><th scope="row">Average estimated beta</th><td data-label="Dot-com rally">−0.07</td><td data-label="AI rally">−0.12</td></tr>
    <tr><th scope="row">Realized beta</th><td data-label="Dot-com rally">−0.06</td><td data-label="AI rally">—</td></tr>
    <tr><th scope="row">Long-book contribution, before costs</th><td data-label="Dot-com rally">−10.4 pp</td><td data-label="AI rally">+4.2 pp</td></tr>
    <tr><th scope="row">Short-book contribution, before costs</th><td data-label="Dot-com rally">−27.1 pp</td><td data-label="AI rally">−16.3 pp</td></tr>
    <tr><th scope="row">Trading-cost drag</th><td data-label="Dot-com rally">—</td><td data-label="AI rally">−0.5 pp</td></tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table A4:</strong> Market return, portfolio result, exposure, beta, and book contributions during the two volatile-stock rallies highlighted in Figure 6. A dash means the article evidence does not report that value.</p>
