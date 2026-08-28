---
layout: post
title: "The Low-Volatility Factor: Why Position Sizing Matters"
date: 2024-12-15
last_modified_at: 2026-08-28
show_date: false
categories: ["Low volatility"]
article_label: Low-volatility · portfolio construction
permalink: /quant/2024/12/15/low-volatility-factor.html
github_repositories:
  - label: Research code on GitHub
    url: https://github.com/piinghel/low-vol-to-portfolio
---

<p class="article-summary"><strong>TL;DR:</strong> A low-volatility strategy buys the least volatile stocks and shorts the most volatile ones. With equal weights, the volatile short book dominates risk. Holding the stocks fixed, inverse-volatility sizing raises the after-cost arithmetic return from 2.4% to 7.1%, lowers volatility from 33.4% to 9.8%, and reduces the maximum drawdown from 87.1% to 38.0%. Scaling also changes gross, net, and beta exposure, so the comparison supports the complete sizing rule rather than one isolated effect.</p>

The low-volatility effect is an empirical pattern: stocks with smaller price
swings have often delivered better risk-adjusted returns than stocks with larger
swings. [Blitz and van
Vliet](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865) document this
pattern across the U.S., Europe, and Japan. [Frazzini and
Pedersen](https://www.nber.org/papers/w16601) offer one explanation based on
investors' leverage constraints.

A common implementation ranks stocks by past volatility, buys the least volatile
group, and shorts the most volatile group. The first group is the *long book*:
it gains when those stocks rise. The second is the *short book*: it gains when
those stocks fall.

The ranking says which stocks belong in each book, but not how large their
positions should be. Giving every stock the same dollar weight is easy to
implement, yet one dollar in a volatile stock carries more risk than one dollar
in a stable stock. The high-volatility short book can therefore drive the entire
portfolio.

I compare equal weights with an inverse-volatility rule, which gives smaller
positions to stocks whose prices move more. Both versions hold the same stocks
and rebalance on the same dates. The comparison therefore stays focused on what
changes when the position sizes change.

## The stock ranking stays fixed

Both portfolios use point-in-time Russell 1000 membership and daily prices from
July 1995 through 27 May 2026. A stock must trade above \$5 on an unadjusted
basis and have enough history to estimate the selection signal, sizing
volatility, and beta.
Requiring a beta estimate keeps the later beta comparison on the same set of
stocks; beta does not enter the ranking or sizing rule. Each rebalance retains
857–1,015 stocks, with a median of 973.

On each signal date, I rank stocks by their average annualised volatility over
the past 21, 63, and 126 trading days:

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

Here, $$\widehat{\sigma}_{i,t}^{(h)}$$ is stock $$i$$'s annualised volatility
over the last $$h$$ trading days. The three windows keep the score responsive
without making it depend on one short lookback. I bound the score at 5%–200%
before ranking, so observations outside that range tie at the nearest boundary.

At each rebalance, I split the ranking into ten groups of roughly equal size.
The portfolio buys decile 1, the lowest-volatility group, and shorts decile 10,
the highest-volatility group. Each book holds about 100 stocks. The middle
deciles show whether the pattern changes smoothly across the ranking.

The decile results in Figure 1 show that the ranking separates risk more clearly
than return. Volatility rises steadily from the lowest- to the
highest-volatility stocks, while Sharpe falls.

<div class="low-vol-figure decile-profile-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/decile_profile" alt="Sharpe ratio, geometric return, and volatility across volatility deciles" version="10" mobile=false %}
</div>

<p class="figure-caption"><strong>Figure 1:</strong> Risk and return by volatility decile, before costs. Decile 1 contains the least volatile stocks; decile 10 the most volatile.</p>

Geometric return remains positive, but the highest-volatility decile turns a
7.6% arithmetic return into only 0.3% annual compounding. Large swings create
that gap. The remaining comparison holds deciles 1 and 10 fixed and changes only
their position sizes.

## Equal weights leave the short book in control

With the stocks fixed, equal weighting is the simplest place to start. The
reference portfolio gives every stock the same dollar weight, but equal capital
does not produce equal risk. The high-volatility short book has 37.9% realised
volatility; the low-volatility long book has 11.9%.

Beta measures how strongly a stock tends to move with the market. A beta near 1
moves roughly with the market, while a beta near zero has little average market
sensitivity. The short book's estimated beta is 1.63, compared with 0.55 for the
long book.

The imbalance is large (Figure 2). Equal capital gives the short book more than
three times the volatility and nearly three times the beta of the long book.

<div class="low-vol-figure naive-leg-risk-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/naive_leg_risk" alt="Realised volatility and average beta of the low- and high-volatility deciles" version="10" mobile=false %}
</div>

<p class="figure-caption"><strong>Figure 2:</strong> Realised volatility and beta of the equal-weight long and short books.</p>

## Scaling each stock by its own volatility

Inverse-volatility sizing responds directly to the imbalance: a position becomes
smaller as its volatility rises. I use a separate 60-day volatility estimate
with a 5% floor. Each stock starts at $1/N$, then its weight is multiplied by
20% divided by its estimated volatility. A stock with 10% volatility therefore
receives twice the preliminary weight of one with 20% volatility. I cap each
position at 4% and each book at 100% gross exposure. The portfolio rebalances
every three weeks and trades at the next market close.

For stock $$i$$ in a book with $$N$$ positions, the preliminary weight is

$$
\begin{aligned}
a_{i,t}^{\mathrm{pre}}
&=\frac{1}{N}
\times \frac{0.20}{\widehat{\sigma}_{i,t}^{(60)}}, \\
a_{i,t}
&=\min\left(a_{i,t}^{\mathrm{pre}},\;0.04\right).
\end{aligned}
$$

The 20% reference volatility sets the scale, and the 4% cap prevents one stock
from becoming too large. If the weights add up to more than 100% within either
book, I scale that whole book back to 100%.

The 100% limit is a ceiling, not a target. Because its stocks are more volatile,
the short book can shrink to 30% or 40% of portfolio value. This rule scales each
stock on its own; it does not target total portfolio risk, gross exposure, net
exposure, or beta. Those outcomes still depend on the final weights and on how
the stocks move together.

## Scaling balances book risk, not capital

Inverse-volatility sizing reduces the risk imbalance in Figure 2, but it also
changes how much capital sits on each side. The low-volatility long book stays
near its 100% ceiling, while the high-volatility short book becomes much smaller.

Figure 3 traces long, short, and net exposure through time. Net exposure stays
positive because the portfolio has more capital in long positions than in short
positions.

<div class="low-vol-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/target_exposures" alt="Realised long gross, short gross, and net stock exposure through time" version="10" mobile=false %}
</div>

<p class="figure-caption"><strong>Figure 3:</strong> Daily long, short, and net stock exposure after volatility scaling.</p>

Gross exposure adds the capital on both sides. Net exposure subtracts the short
book from the long book: a portfolio that is 100% long and 40% short has 140%
gross exposure and +60% net exposure.

Across the sample, the long book averages 97.2% gross exposure and the short
book 34.0%. Total gross exposure is 131.1%, and net stock exposure is +63.2%.
These are daily floating weights, so they include price moves between
rebalances.

The capital becomes less balanced, but the risk becomes more balanced. Long-
and short-book volatility is 10.5% and 10.0%, compared with 11.9% and 37.9%
under equal weights. The rule achieves its immediate goal at the book level;
total portfolio risk still depends on correlations.

Net exposure does not tell us how the portfolio moves with the market. Beta
does. Portfolio beta weights each stock's beta by its position, with negative
weights for short positions.

The short book uses less capital, but its stocks have much higher betas. Their
market sensitivity offsets most of the larger long book's beta. The full-sample
average beta estimated from the holdings is −0.014, and realised beta is −0.001.

Stock-level volatility sizing leaves beta free to move. The portfolio can
therefore have positive net stock exposure while carrying little, or even
negative, market beta. Targeting beta would require a separate constraint or an
index-futures overlay.

Estimated and realised beta both move over time (Figure 4), but their full-sample
averages remain close to zero.

<div class="low-vol-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/beta_diagnostic" alt="Estimated and rolling realised beta of the volatility-scaled portfolio" version="10" mobile=false %}
</div>

<p class="figure-caption"><strong>Figure 4:</strong> Estimated and rolling realised beta of the volatility-scaled portfolio.</p>

## The scaled portfolio takes less risk and compounds better

Both portfolios rebalance every three weeks. I deduct 5 basis points for every
dollar bought or sold, including the opening trades. Because the scaled
portfolio trades 10.4 times its equity each year, this assumption reduces its
annual return by about 0.52 percentage points. Cash held outside the stock
positions earns no interest.

Arithmetic return measures average yearly performance; geometric return measures
the rate at which wealth compounds. A volatile portfolio can have a positive
arithmetic return and still lose money over time. Sharpe divides arithmetic
return by volatility, using a zero cash rate. All risk, Sharpe, and drawdown
figures below include the 5 basis-point trading cost.

Tables 1 and 2 put the performance difference beside the exposure and turnover
that come with each sizing rule.

<table class="research-table comparison-table performance-table desktop-layout-table">
  <thead>
    <tr>
      <th>Performance metric</th>
      <th>Equal-weight reference</th>
      <th>Volatility-scaled</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Arithmetic return, before costs</th>
      <td data-label="Equal-weight reference">3.2%</td>
      <td data-label="Volatility-scaled">7.6%</td>
    </tr>
    <tr>
      <th scope="row">Arithmetic return, after costs</th>
      <td data-label="Equal-weight reference">2.4%</td>
      <td data-label="Volatility-scaled">7.1%</td>
    </tr>
    <tr>
      <th scope="row">Geometric return, after costs</th>
      <td data-label="Equal-weight reference">−3.1%</td>
      <td data-label="Volatility-scaled">6.9%</td>
    </tr>
    <tr>
      <th scope="row">Volatility, after costs</th>
      <td data-label="Equal-weight reference">33.4%</td>
      <td data-label="Volatility-scaled">9.8%</td>
    </tr>
    <tr>
      <th scope="row">Sharpe, after costs</th>
      <td data-label="Equal-weight reference">0.07</td>
      <td data-label="Volatility-scaled">0.73</td>
    </tr>
    <tr>
      <th scope="row">Max drawdown, after costs</th>
      <td data-label="Equal-weight reference">−87.1%</td>
      <td data-label="Volatility-scaled">−38.0%</td>
    </tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 1:</strong> Full-sample performance with three-week rebalancing.</p>

<table class="research-table comparison-table exposure-table desktop-layout-table">
  <thead>
    <tr>
      <th>Exposure or trading metric</th>
      <th>Equal-weight reference</th>
      <th>Volatility-scaled</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Average gross exposure</th>
      <td data-label="Equal-weight reference">200%</td>
      <td data-label="Volatility-scaled">131%</td>
    </tr>
    <tr>
      <th scope="row">Average net exposure</th>
      <td data-label="Equal-weight reference">0%</td>
      <td data-label="Volatility-scaled">63%</td>
    </tr>
    <tr>
      <th scope="row">Realised beta</th>
      <td data-label="Equal-weight reference">−1.12</td>
      <td data-label="Volatility-scaled">−0.001</td>
    </tr>
    <tr>
      <th scope="row">Annualised turnover</th>
      <td data-label="Equal-weight reference">14.4× equity</td>
      <td data-label="Volatility-scaled">10.4× equity</td>
    </tr>
  </tbody>
</table>

<p class="table-caption"><strong>Table 2:</strong> Full-sample exposure and turnover.</p>

The scaled portfolio earns a 7.1% arithmetic return after costs with 9.8%
volatility. The equal-weight portfolio earns 2.4% with 33.4% volatility. Sharpe
therefore rises from 0.07 to 0.73, while maximum drawdown falls from 87.1% to
38.0%.

The return and risk gaps lead to very different wealth paths (Figure 5). The
upper panel tracks the growth of one dollar; the lower panel shows each
portfolio's decline from its previous peak.

<div class="low-vol-figure performance-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns" alt="Growth of one dollar on a logarithmic scale and drawdowns for the equal-weight and volatility-scaled long-short portfolios" version="10" mobile=false %}
</div>

<p class="figure-caption"><strong>Figure 5:</strong> After-cost growth of \$1 and drawdowns. Wealth is shown on a log scale.</p>

The equal-weight portfolio's positive arithmetic return hides poor compounding:
repeated large losses leave only 38 cents from each starting dollar. The scaled
portfolio compounds at 6.9% a year and turns each starting dollar into \$7.78.
Its path still includes long flat periods and a 38% maximum drawdown.

This is a comparison of two complete sizing rules, not a clean estimate of one
mechanism. Volatility scaling also lowers gross exposure, creates positive net
exposure, changes beta, and reduces turnover. Matched tests at the same gross
exposure, beta, or realised risk would show which of those changes explains the
performance gap. The stock selections, signal windows, sizing window, position
cap, book ceiling, and rebalance interval are held fixed.

The price data add another limitation. I carry missing prices forward and close
a stock that leaves the data at its last observed price. If that price is stale
before a bad delisting, the backtest understates the loss. A conservative
delisting return is the most useful test of this assumption. Full-sample
averages can also hide the periods in which the strategy is most vulnerable.

## The short book drives losses when volatile stocks rally

The dot-com boom makes the remaining risk easy to see because the sample
contains both the rally and the reversal. From 8 October 1998 to 9 March 2000,
the Russell 1000 gained 52.2% while the scaled long–short portfolio lost 38.0%
after costs. Its average net stock exposure was +72.0%, but its estimated beta
was −0.07 and its realised beta was −0.06. The portfolio held more dollars long
than short, yet the smaller short book contained stocks with much higher market
sensitivity.

Before costs, the long book lost 10.4 percentage points and the short book lost
27.1. The two panels on the left of Figure 6 trace the episode. The upper panel
compares the portfolio's before-cost wealth with the market; the lower panel
separates the long- and short-book contributions. The dotted line marks the
portfolio trough on 9 March 2000. Both books recover after that point, and the
portfolio returns to roughly its starting value by 3 April 2001.

The two panels on the right show the 2025–2026 AI rally. From 3 April 2025
through 27 May 2026, the Russell 1000 gained 38.5% and the scaled long–short
portfolio lost 12.6% after costs. Its average net stock exposure was +68.6%,
while its estimated beta was −0.12. Before costs, the long book added 4.2
percentage points and the short book lost 16.3; trading costs removed another
0.5 points.

<div class="low-vol-figure regime-comparison-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/regime_comparison" alt="Russell 1000 and low-volatility portfolio wealth with long- and short-book contributions during the dot-com rally and the 2025 to 2026 AI rally" version="10" mobile=false %}
</div>

<p class="figure-caption"><strong>Figure 6:</strong> Dot-com rally and reversal (left) and the 2025–2026 AI rally (right). Top: portfolio wealth before trading costs and Russell 1000 wealth. Bottom: long- and short-book contributions. Each episode has its own vertical scale.</p>

Both episodes expose the same weakness. Volatility scaling reduces the capital
in the short book, but it does not remove the risk of a sharp rally in those
stocks. The negative long–short beta shows why positive net exposure offered no
protection: the market rose while the portfolio's market sensitivity was
negative. The recent sample ends during the rally, so it contains no recovery
comparable with the dot-com reversal.

## Inverse-volatility sizing fixes the first problem

Equal weighting is not a sensible way to build this portfolio. It gives the
volatile short book most of the risk and produces much worse compounding and
drawdowns, even though the stock selection is unchanged. I would replace it
with inverse-volatility sizing.

That decision solves only the first construction problem. The scaled portfolio
still leaves gross exposure, net exposure, beta, correlations, and the risk of
a violent high-volatility rally uncontrolled. The dot-com and AI episodes show
that these are not minor details.

The next step is to size the portfolio as a whole, using a covariance model and
explicit constraints on exposure, beta, and turnover. I would compare that
portfolio with the current rule at matched gross exposure, beta, and realised
risk, then repeat the test with conservative stale-price and delisting
assumptions. Those are the problems I would take up in the next post.
