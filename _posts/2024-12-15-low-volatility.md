---
layout: post
title: "Sizing a Low-Volatility Portfolio"
description: "The same stock ranking, resized: less capital in volatile shorts and a different balance of portfolio risk."
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

<p class="article-summary">Equal capital in a stable-stock long book and a volatile-stock short book creates very unequal risk. Inverse-volatility sizing puts much less capital into the volatile shorts, changing market exposure as well as individual weights. Here portfolio volatility falls from 33% to 10% and turnover declines, but coordinated short-book losses still cause large drawdowns.</p>

One dollar in stable stocks and one dollar short in volatile stocks is an easy
starting rule. But I have deliberately chosen the two sides for different
levels of risk. Giving them equal capital lets the volatile short book
dominate the outcome. The sizing decision is already part of the strategy.

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

I changed more than individual position sizes here. The short book uses less
capital, beta shifts and turnover falls. To find out how much each change
contributes, I would need to vary them separately while matching the other
exposures and constraints.

## What improves

Table 1 shows how much the allocation change matters. Inverse-volatility sizing
reduces volatility from 33.4% to 9.8% and turns geometric return positive.
Turnover also falls. Given this choice, I would use inverse-volatility sizing.

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

The equal-weight row can look odd at first: how does a positive Sharpe go with
a negative geometric return? Sharpe uses the arithmetic mean, which is
positive here. Compounding also reflects the size of the swings. Repeated large
moves erode the equal-weight portfolio's compounded value, leaving just
35 cents per starting dollar in Figure 2. Inverse-volatility sizing reaches
7.54 dollars, although it still suffers a 38% maximum drawdown.

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
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/regime_comparison" mobile="/assets/2024-12-15-low-volatility-factor/regime_comparison_mobile" alt="Growth of one dollar in the Russell 1000 and low-volatility portfolio, with long- and short-book contributions during the dot-com rally and the April 2025 to May 2026 rally" version="15" %}
</div>

<p class="figure-caption"><strong>Figure 3: Short-book losses in two market rallies.</strong> Before-cost indexed growth above linked cumulative book contributions in percentage points. Corresponding panels share scales. The dot-com episode comes first, followed by April 2025–May 2026; the marked line identifies the dot-com portfolio trough.</p>

From 8 October 1998 to 9 March 2000, the market gains about 52% while the portfolio loses
38% after costs. The short book contributes −27.1 percentage points before
costs, versus −10.4 from the longs. The later reversal brings the portfolio
back toward its starting value.

From 3 April 2025 to 27 May 2026, the market gains about 39% while the portfolio
loses 13%. Longs contribute +4.2 points and shorts −16.3 before costs.
The shorts drive the loss again, and the portfolio hasn't recovered by the end
of the available sample. Both comparisons measure returns from the first date's close.

Positive net stock exposure does not prevent these losses. Estimated beta is
mildly negative in both episodes, but market beta alone does not describe every
risk shared by the short positions. I can see that the shorts drive the losses;
sector and style attribution would help explain what those stocks have in common.

## From individual weights to joint construction

Equal capital gave the high-volatility short book far more risk than the long
book. Inverse-volatility sizing corrected much of that imbalance, partly by
committing less capital to the shorts. But coordinated short-stock rallies
remained the main source of the two losses examined here. Getting the
individual position sizes under control did not control their shared risk.

That is where I would take the next experiment: size the holdings jointly,
using covariance and explicit portfolio limits, then check whether those
choices reduce realized drawdowns without giving away the return after costs.

This is one historical comparison on a single three-week calendar. The 5 bp
trading charge excludes borrow, financing and market impact.
