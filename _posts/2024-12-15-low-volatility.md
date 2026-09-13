---
layout: post
title: "Sizing a Low-Volatility Portfolio"
description: "The same stock ranking, resized: less capital in volatile shorts and a different balance of portfolio risk."
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

<p class="article-summary">Giving volatile stocks smaller positions brings portfolio volatility down from 33% to 10% in this comparison. Most of the change comes from reducing the short book. That helps a lot, but the shorts can still lose together during market rallies.</p>

Buying stable stocks and shorting volatile ones sounds straightforward enough.
The awkward part is deciding how much to put behind each side. Equal dollar
amounts are a simple starting point, but the two books have very different
levels of risk. The shorts can end up driving the whole portfolio.

I want to see how much a simple sizing rule can fix. I'll keep the same stocks
and compare equal weighting with inverse-volatility sizing, giving smaller
positions to stocks that move around more. Then I'll look at the drawdowns
to see where that rule still falls short.

The ranking comes from the [low-volatility
effect](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865): stable stocks
have tended to earn better risk-adjusted returns than volatile stocks.
[Frazzini and Pedersen](https://www.nber.org/papers/w16601) connect this pattern
to investors' leverage constraints.

Both rules use point-in-time Russell 1000 membership, a price above five dollars,
and average volatility over 21, 63 and 126 days as the ranking signal.
The lowest-volatility decile is long and the highest is short, with roughly
100 names per book. Rebalancing occurs every three weeks, execution at the
next close, and trading costs are 5 bp per dollar traded.

In this sample, the ranking separates risk more clearly than return. Across
the ten deciles, realized volatility rises from 11.9% for the stable stocks
to 37.9% for the volatile stocks, while Sharpe falls from 0.90 to 0.20.
The highest-volatility decile still earns a positive arithmetic return before
costs, but compounds at only 0.35% a year. Shorting these stocks means absorbing
their large price swings.

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

Equal weighting is easy to explain, but I find it a poor starting point for
this particular ranking: it gives the deliberately volatile stocks too much
influence. The next step is to reduce their allocations.

## Sizing the two books

Inverse-volatility sizing makes the allocation proportional to the inverse of
estimated volatility. With a 20% reference level, a stock at 40% annualized
volatility receives half its equal share. Including a position cap, the rule is

$$
a_{i,t}=\min\left(\frac{1}{N}\times
\frac{\sigma_{\mathrm{ref}}}{\widehat{\sigma}_{i,t}},\;a_{\max}\right).
$$

Here $N$ is the number of stocks in the book, $\sigma_{\mathrm{ref}}=20\%$
and $a_{\max}=4\%$. The volatility estimate uses 60 sessions with a 5% floor.
If a book exceeds
100% gross, its positions scale down proportionally. A smaller book keeps its
lower capital allocation.

Leaving the smaller book alone does a lot of the work here. Scaling it back up
would put capital straight back into the volatile shorts. With the rule above,
the long book averages 97% gross exposure and the short book 34%, bringing
total gross exposure down from 200% to about 131%. At those sizes, each book
has standalone volatility of about 10%; equal weighting had left the short
book above 37%. Total portfolio risk also depends on covariance between them.

The capital difference leaves about 63% net stock exposure. Because the smaller
short book contains higher-beta stocks, it still offsets much of the long
book's market sensitivity. Full-sample realized beta moves from −1.12 to
−0.001, but holdings-based and rolling realized estimates vary through time.
Most of the sizing change is therefore a smaller short book, with the long
allocation close to its original size. That matters when interpreting the
performance comparison below.

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

## Shared losses during market rallies

The remaining drawdowns show the limit of treating positions individually.
Figure 3 examines two market rallies when the short book lost heavily:
the dot-com episode and April 2025–May 2026. The contribution panels locate
the return in the long and short books.

<div class="low-vol-figure regime-comparison-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/regime_comparison" mobile="/assets/2024-12-15-low-volatility-factor/regime_comparison_mobile" alt="Growth of one dollar in the Russell 1000 and low-volatility portfolio, with long- and short-book contributions during the dot-com rally and the April 2025 to May 2026 rally" version="17" %}
</div>

<p class="figure-caption"><strong>Figure 3: Short-book losses in two market rallies.</strong> Before-cost indexed growth above linked cumulative book contributions in percentage points. The dot-com episode comes first, followed by April 2025–May 2026.</p>

From 8 October 1998 to 9 March 2000, the market gains about 52% while the portfolio loses
38% after costs. The short book contributes −27.1 percentage points before
costs, versus −10.4 from the longs. The later reversal brings the portfolio
back toward its starting value.

From 3 April 2025 to 27 May 2026, the market gains about 39% while the portfolio
loses 13%. Longs contribute +4.2 points and shorts −16.3 before costs.
The shorts drive the loss again, and the portfolio ends the sample below its
starting value. Both comparisons measure returns from the first date's close.

In the dot-com rally, both books lose. In the later rally, the longs help,
but cover only about a quarter of the short-book loss. Smaller positions
reduce the damage from each volatile stock; they still leave the portfolio
exposed when those stocks rise together.

## From individual weights to joint construction

I prefer inverse-volatility sizing for this comparison. Putting less capital
behind the volatile shorts makes sense to me, and here it improves both risk
and compounded returns while reducing turnover. A 38% maximum drawdown still
leaves a problem worth working on.

The two rallies show where I would go next. Smaller positions help, but the
short book can still overwhelm the longs when its holdings rise together.
Sizing the holdings jointly, using covariance and explicit portfolio limits,
would let me account for those relationships. The next test is whether that
reduces drawdowns while preserving the return after costs.
