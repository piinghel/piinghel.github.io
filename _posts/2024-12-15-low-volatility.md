---
layout: post
title: "Sizing a Low-Volatility Portfolio"
description: "The same stock ranking, resized: less capital in volatile shorts and a different balance of portfolio risk."
date: 2024-12-15
last_modified_at: 2026-09-06
show_date: false
categories: ["Low volatility"]
article_label: Low-volatility · portfolio construction
permalink: /quant/2024/12/15/low-volatility-factor.html
github_repositories:
  - label: Research code on GitHub
    url: https://github.com/piinghel/low-vol-to-portfolio
---

<p class="article-summary">Equal capital in a stable-stock long book and a volatile-stock short book creates very unequal risk. Inverse-volatility sizing puts much less capital into the volatile shorts, changing market exposure as well as individual weights. Here portfolio volatility falls from 33% to 10% and turnover declines, but coordinated short-book losses still cause large drawdowns.</p>

The strategy buys stable stocks and shorts volatile ones. I then have to decide
how much capital to put behind each side. Equal dollar amounts seem like a
reasonable place to start, but I've chosen the two books for very different
levels of risk. The volatile shorts can dominate the portfolio even when I
give them no more capital than the longs.

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

In this sample, the ranking separates risk more clearly than return. Across
the ten deciles, realized volatility rises from 11.9% for the stable stocks
to 37.9% for the volatile stocks, while Sharpe falls from 0.90 to 0.20.
The highest-volatility decile still earns a positive arithmetic return before
costs, but compounds at only 0.35% a year. Poor risk-adjusted returns don't
make these stocks an easy short: their large swings are precisely what the
portfolio has to absorb.

## Equal capital, unequal risk

The equal-weight rule puts one dollar into each book for every dollar of
strategy capital. Figure 1 shows the consequence: the high-volatility stocks
have more than three times the long book's standalone volatility and almost
three times its beta. Shorting them reverses that market exposure, leaving
the combined portfolio with realized beta of −1.12.

<div class="low-vol-figure naive-leg-risk-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/naive_leg_risk" mobile="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile" alt="Realised volatility and average beta of the low- and high-volatility deciles" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 1: Equal capital gives the volatile book more risk.</strong> Annualized realized volatility and average point-in-time beta, July 1995–May 2026. The high-volatility book's beta is measured before applying the short sign.</p>

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

Volatility now has two separate jobs. The ranking selects which stocks enter
each book; the 60-session estimate determines how much capital each selected
stock receives. The selected names are the same under both sizing rules, so
the comparison shows what changes when I alter their allocations.

Leaving the smaller book alone does a lot of the work here. Scaling it back up
would put capital straight back into the volatile shorts. With the rule above,
the stable long book averages 97% gross exposure,
while the volatile short book averages 34%. At those actual book sizes, each
has standalone volatility of about 10%; equal weighting had left the short
book above 37%. Similar standalone volatilities do not imply equal contributions
to total portfolio risk, which also depend on covariance.

The capital difference leaves about 63% net stock exposure. Because the smaller
short book contains higher-beta stocks, it still offsets much of the long
book's market sensitivity. Full-sample realized beta moves from −1.12 to
−0.001, but holdings-based and rolling realized estimates vary through time.
I haven't asked the sizing rule to target that beta. It is an outcome of these
weights, and the near-zero average hides variation through time.

The amount of capital committed changes too. Equal weighting commits 200% of
strategy capital across the two books. Inverse-volatility sizing averages about
131%: 97% long and 34% short. Most of the reduction comes from the volatile short
book, while the long allocation remains close to its original size. The result
therefore reflects both smaller individual positions and a different balance
between the two books.

## What improves

Table 1 shows how much the allocation change matters. Inverse-volatility sizing
reduces volatility from 33.4% to 9.8% and turns geometric return positive.
Turnover also falls.

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 1: Risk and return under the two sizing rules.</strong> Results for 12 July 1995–27 May 2026. Net return is geometric; returns, volatility and two-way turnover are annualized. Net results charge 5 bp on traded notional; turnover sums absolute executed trades relative to strategy capital. Sharpe uses a zero cash rate.</caption>
  <thead>
    <tr><th>Rule</th><th>Net geometric return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Annual turnover</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Equal-weight</th><td>−3.3%</td><td>33.4%</td><td>0.07</td><td>−87.8%</td><td>18.8×</td></tr>
    <tr><th scope="row"><strong>Inverse-volatility</strong></th><td><strong>6.8%</strong></td><td><strong>9.8%</strong></td><td><strong>0.72</strong></td><td><strong>−38.0%</strong></td><td><strong>12.4×</strong></td></tr>
  </tbody>
</table>

The equal-weight portfolio has a positive Sharpe because its average daily
return is positive. But those returns come with large swings, which hurt
compounding. Figure 2 shows what this means over the full period: 35 cents
remain per starting dollar, compared with 7.54 dollars under inverse-volatility
sizing. The change in sizing makes a large difference, although a 38% maximum
drawdown still leaves plenty to improve.

<div class="low-vol-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns" mobile="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile" alt="Growth of one dollar on a logarithmic scale and drawdowns for the equal-weight and volatility-scaled long-short portfolios" version="15" %}
</div>

<p class="figure-caption"><strong>Figure 2: Sizing changes both risk and compounding.</strong> Compounded daily P&amp;L per unit of strategy notional (log scale) and drawdown, July 1995–May 2026, after the 5 bp charge. The rules retain their different exposures and volatilities; Table 1 supplies the risk comparison.</p>

## What individual sizing misses

The remaining drawdowns show the limit of treating positions individually.
Figure 3 examines two market rallies when the short book lost heavily:
the dot-com episode and April 2025–May 2026. The contribution panels locate
the return in the long and short books.

<div class="low-vol-figure regime-comparison-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/regime_comparison" mobile="/assets/2024-12-15-low-volatility-factor/regime_comparison_mobile" alt="Growth of one dollar in the Russell 1000 and low-volatility portfolio, with long- and short-book contributions during the dot-com rally and the April 2025 to May 2026 rally" version="17" %}
</div>

<p class="figure-caption"><strong>Figure 3: Short-book losses in two market rallies.</strong> Before-cost indexed growth above linked cumulative book contributions in percentage points. Corresponding panels share scales. The dot-com episode comes first, followed by April 2025–May 2026.</p>

From 8 October 1998 to 9 March 2000, the market gains about 52% while the portfolio loses
38% after costs. The short book contributes −27.1 percentage points before
costs, versus −10.4 from the longs. The later reversal brings the portfolio
back toward its starting value.

From 3 April 2025 to 27 May 2026, the market gains about 39% while the portfolio
loses 13%. Longs contribute +4.2 points and shorts −16.3 before costs.
The shorts drive the loss again, and the portfolio hasn't recovered by the end
of the available sample. Both comparisons measure returns from the first date's close.

The two episodes show what individual sizing misses. During the dot-com rally,
both books lose money, so the longs provide no offset to the short-book losses.
In the later rally, the longs gain 4.2 points but offset only about a quarter
of the shorts' 16.3-point loss. Inverse-volatility sizing reduces the capital
behind each volatile position; it does not account for how several positions
can move together. Positive net stock exposure does not prevent that shared
risk from dominating the portfolio.

## From individual weights to joint construction

I would use inverse-volatility sizing as the starting point. It keeps the stock
selection intact and puts less capital behind the positions taking the most
risk. Here that reduces portfolio volatility from 33.4% to 9.8%, with much better
compounded returns and lower turnover.

The two rallies show where I would go next. Smaller positions help, but the
short book can still overwhelm the longs when its holdings rise together.
Sizing the holdings jointly, using covariance and explicit portfolio limits,
would let me account for those relationships. The next test is whether that
reduces drawdowns without giving away the return after costs.
