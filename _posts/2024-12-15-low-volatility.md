---
layout: post
title: "Sizing a Low-Volatility Portfolio"
description: "Why equal capital makes a low-volatility portfolio risky, and how shrinking the shorts changes risk, market exposure and compounding."
date: 2024-12-15
last_modified_at: 2026-09-14
show_date: false
categories: ["Low volatility"]
article_label: Low-volatility · portfolio construction
permalink: /quant/2024/12/15/low-volatility-factor.html
github_repositories:
  - label: Research code on GitHub
    url: https://github.com/piinghel/low-vol-to-portfolio
---

The [low-volatility effect](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865)
is the tendency for calmer stocks to earn better returns per unit of risk
than more volatile stocks. Turning that observation into a portfolio means
deciding both which stocks to hold and how much capital to give them.

In this article, I compare equal weighting with inverse-volatility sizing
and use a market hedge to check how much market exposure matters.

## High-volatility stocks earn less per unit of risk
{: #what-the-ranking-selects }

Sharpe expresses return per unit of risk as average return divided by
volatility.
Beta measures how sensitively a stock or portfolio's returns move with the market.
[Frazzini and Pedersen](https://www.nber.org/papers/w16601) offer one explanation
for why this can persist: investors with limited access to borrowing reach
for high-beta stocks instead, bidding up their prices and accepting less
return per unit of risk.[^bab]

That matters for a long-short portfolio. A poor Sharpe differs from a
negative return: volatile stocks can still go up, with a lot of noise along
the way, and a short position pays for every up-move. Before sizing the
short positions, I want to see whether these stocks actually lose money or
simply earn little for the risk they take.

I use point-in-time Russell 1000 membership: each ranking uses the stocks
that belonged to the index at that date. I keep stocks priced above five
dollars and rank them by average volatility over one, three and six
months.[^windows] I buy the lowest-volatility decile—the calmest tenth—and
short the highest-volatility decile, the most volatile tenth. I call these long
and short groups the two books, with roughly 100 names in each.
I rebalance every three weeks, trade at the next close,
and charge 5 bp per dollar traded.

Figure 1 shows all ten volatility deciles, each an equal-weighted long
portfolio of roughly 100 stocks, from the least volatile in decile 1 to the most volatile
in decile 10. The ranking separates risk much more cleanly than return:
volatility rises from about 12% to 38%, while Sharpe falls by almost
four-fifths. The highest-volatility decile earns only about a third of a percent a
year before costs. These stocks earn little per unit of risk, yet still go up
over the sample. That makes the size of the short book matter.

<div class="low-vol-figure decile-profile-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/decile_profile" alt="Sharpe ratio, annual return and volatility across ten past-volatility deciles, from the least volatile stocks to the most volatile" version="13" %}
</div>

<p class="figure-caption"><strong>Figure 1: More volatile stocks earn less per unit of risk.</strong> Before-cost Sharpe, annual return and volatility, July 1995–May 2026. Annual return means compounded annual growth throughout this article. Each decile is an equal-weighted long portfolio of about 100 stocks, re-formed every three weeks; decile 1 is the calmest. Volatility rises from 11.9% to 37.9% and Sharpe falls from 0.90 to 0.20.</p>

## Equal capital, unequal risk

For my naive first attempt, I allocate 100% of strategy capital to each book
and divide it equally among the stocks. Gross exposure adds the absolute
sizes of all long and short positions, so this portfolio starts at 200%
gross. Figure 2 shows why equal capital gives the shorts so much influence:
their standalone volatility is more than three times the longs', and their
market sensitivity is almost three times as large. Together, the books
produce a negative beta a little larger than shorting the whole market
at the size of the strategy's capital. That is a hefty extra bet to get
from a volatility ranking.

<div class="low-vol-figure naive-leg-risk-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/naive_leg_risk" mobile="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile" alt="Realised volatility and average beta of the low- and high-volatility deciles" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 2: Equal capital gives the volatile book more risk.</strong> Annualized realized volatility and average point-in-time beta, July 1995–May 2026. The high-volatility book's beta is measured before applying the short sign. The combined portfolio's full-sample realized beta is −1.12.</p>

I can reduce the shorts' influence by putting less capital in the stocks
with the highest estimated volatility. I keep the ranking and change the sizes.

## Shrink the book, keep the ranking
{: #sizing-the-two-books }

I scale each stock's equal-weight allocation by a reference volatility divided
by its estimated volatility. Including a position cap, the absolute allocation is

$$
a_{i,t}=\min\left(\frac{1}{N}\times
\frac{\sigma_{\mathrm{ref}}}{\widehat{\sigma}_{i,t}},\;a_{\max}\right).
$$

Here $N$ is the number of stocks in the book, $\sigma_{\mathrm{ref}}=20\%$
and $a_{\max}=4\%$. I estimate volatility over about three months and apply
a 5% floor.[^windows] If a book exceeds 100% gross, I scale its positions
down proportionally. Below that cap, I keep the lower gross.

Keeping the lower gross is the step that shrinks the short book. Scaling
both books back to 100% would put the capital straight back into the high-volatility
stocks. The long book averages about 97% gross and the short book 34%,
bringing total gross down from 200% to about 131%. Each book now has
standalone volatility of about 10%; equal weighting had left the short
book above 37%. Their combined risk also depends on how they move together.

Net exposure subtracts the size of the short positions from the longs.
Here the portfolio is about 63% net long, yet its full-sample realized beta
is roughly zero: the smaller short book contains stocks with enough market
sensitivity to offset the longs. The balance varies through
time. That is why a portfolio with more dollars in longs can still lose
in a market rally, as Figure 4 will show.

## Lower risk, with a check on market exposure
{: #what-improves }

The return improvement needs more care: shrinking the shorts also removes
a large bet against the market. To check how much that matters, I hedge
each portfolio with the Russell 1000 whenever I rebalance the stocks,
using beta estimates available at the time. Equal weighting then earns
more, but still takes much more risk.[^beta-check]

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 1: Sizing with and without a beta hedge.</strong> 12 July 1995–27 May 2026, after 5 bp per dollar traded. Return, volatility and turnover are annualized; beta is measured over the full period. Hedged turnover includes index trades.</caption>
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
equal weighting and 0.005 for inverse volatility. Those are full-period
measurements of the resulting returns; the hedge itself uses trailing
estimates at each rebalance. Beta can still drift between trades.
With the hedge, equal weighting earns about 8% a year versus 6.6% for
inverse volatility, with about two and a half times the volatility.
The two rules therefore offer different return–risk trade-offs. Different
gross exposures, book sizes and stock weights remain, so this comparison
does not isolate the stock-level sizing rule.

What I do get is much lower risk: portfolio volatility falls from about 33%
to 10% without the hedge, and from about 25% to 10% with it. I also get a
higher Sharpe and a shallower worst drawdown in both comparisons.
Adding the hedge to inverse volatility barely changes its volatility or
worst drawdown. A market hedge on its own does little to improve that portfolio.

Turnover measures how much I trade relative to strategy capital, counting
both purchases and sales. Volatility-decile membership churns quickly, so
even a rebalance every three weeks produces about 12–19 times capital in
annual stock turnover. The index hedge adds about 0.63 times capital for
inverse volatility and 1.32 for equal weighting. Smaller short positions
reduce the dollars I trade and the costs I pay.

Figure 3 adds the hedged equal-weight portfolio to the original paths.
The hedge lifts its ending value from about 35 cents to almost eleven
dollars per starting dollar, compared with about seven and a half dollars
for unhedged inverse-volatility sizing. Its drawdowns remain much deeper:
about 68% at worst, versus 38%. The return gap changes substantially once
I remove the large market short; the risk gap remains.

<div class="low-vol-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns" mobile="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile" alt="Growth of one dollar and drawdowns for equal-weight, inverse-volatility and equal-weight with a point-in-time Russell 1000 beta hedge" version="16" %}
</div>

<p class="figure-caption"><strong>Figure 3: Hedging changes the return comparison; the risk gap remains.</strong> Growth of $1 (log scale) and drawdown, July 1995–May 2026, after trading costs. The dashed line adds a Russell 1000 hedge to equal weighting at each rebalance. Ending values are 0.35 for equal weighting, 7.54 for inverse volatility and 10.84 for hedged equal weighting.</p>

## Shared losses during market rallies

Figure 4 returns to the unhedged inverse-volatility portfolio to look inside
two of its losses. The portfolio has modest negative realized beta in both
market rallies, despite roughly zero beta over the full sample. That
describes its market sensitivity during those windows; explaining the
losses also requires looking at what the two books actually do.

<div class="low-vol-figure regime-comparison-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/regime_comparison" mobile="/assets/2024-12-15-low-volatility-factor/regime_comparison_mobile" alt="Growth of one dollar in the Russell 1000 and low-volatility portfolio, with long- and short-book contributions during the dot-com rally and the April 2025 to May 2026 rally" version="17" %}
</div>

<p class="figure-caption"><strong>Figure 4: Short-book losses in two market rallies.</strong> Before-cost indexed growth above linked cumulative book contributions in percentage points. Episode returns run from the first date's close: 8 October 1998–9 March 2000 and 3 April 2025–27 May 2026. Long/short gross contributions are −10.4/−27.1 points and +4.2/−16.3 points, respectively; the negative short contributions are losses. Realized portfolio betas in these windows are −0.055 and −0.106.</p>

During the dot-com rally, the market gains about 52% while the portfolio
loses about 38% after costs. The short book contributes roughly −27
percentage points before costs, versus −10 from the longs. The later
reversal brings the portfolio back toward its starting value.

In the later rally, the market gains about 39% while the portfolio
loses about 13% after costs. Longs contribute roughly +4 points and shorts −16 before costs.
The shorts drive the loss again, and the portfolio ends the sample below its
starting value.

The two episodes differ in what the long book contributes. It adds to the
dot-com loss, whereas in the later rally it offsets about a quarter of the
short-book loss. In both cases, the smaller short allocation still drives
most of the loss. Shrinking the shorts reduces their everyday risk, while
losses across those positions can still overwhelm the longs. In the dot-com
episode, both books lose together. Balancing individual stock volatility
leaves that possibility open.

## A simpler baseline
{: #from-individual-weights-to-joint-construction }

I would keep inverse-volatility sizing as the baseline for this investigation.
Hedged equal weighting earns more at the sizes tested, but inverse volatility
offers much lower volatility, shallower drawdowns and less trading. Its
advantage here is a more manageable portfolio with a better Sharpe.

The next comparison should put both hedged rules at the same risk target,
set using information available at each rebalance, with the same cost
assumptions. That would make the sizing trade-off easier to judge.
I would then test whether using covariance and portfolio exposure limits
improves on that baseline, especially when several positions lose together.
Inverse-volatility sizing already gets us a long way;
the more elaborate approach has to earn its place.

[^bab]: Andrea Frazzini and Lasse Heje Pedersen, *Betting Against Beta*, author draft dated 10 May 2013, physical PDF pages 2–3; published in the *Journal of Financial Economics* in 2014. Their mechanism concerns market beta; this article ranks total volatility. [Public author draft](https://w4.stern.nyu.edu/facdir/lpederse/papers/BettingAgainstBeta.pdf#page=2).

[^windows]: The ranking averages trailing volatility estimates over 21, 63 and 126 sessions. The separate sizing estimate uses 60 sessions, with a 5% annualized volatility floor.

[^beta-check]: At each signal close, the Russell 1000 hedge offsets the sum of stock weights times their trailing betas (252 sessions, at least 126 observations, clipped to [−4, 4]). Stocks and hedge trade at the next close and hold fixed quantities until the next three-week rebalance. Returns start after execution. The simulation charges 5 bp per dollar traded; funding, stock borrow fees and futures roll costs are excluded. Returns compound daily P&L per unit of strategy notional; annualization uses 252 sessions.
