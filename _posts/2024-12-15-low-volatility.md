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

<p class="article-summary">Inverse-volatility sizing reduces portfolio volatility from 33% to 10% in this comparison, mainly by reducing exposure to the volatile short book. Compounded returns improve and turnover falls, but common moves across the shorts still produce substantial drawdowns.</p>

The [low-volatility effect](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865)
is an appealing starting point for a stock ranking: stable stocks have tended
to earn better risk-adjusted returns than volatile stocks. Turning that ranking
into a long-short portfolio introduces an allocation problem. The stocks on
the short side are riskier by construction, so equal capital in the two books
can give the shorts much more influence over the result.

I compare equal weighting with a simple inverse-volatility sizing rule on
the same selected stocks, then follow the
change through book exposures, returns after costs and drawdowns. The starting
point is what the volatility ranking actually delivers.

## What the ranking selects

The economic case concerns returns relative to risk.
[Frazzini and Pedersen](https://www.nber.org/papers/w16601), for example, connect
low-risk stocks' performance to investors' leverage constraints. For a
long-short implementation, poor risk-adjusted performance can still come with
positive returns, which work against the short position.

Both rules use point-in-time Russell 1000 membership, a price above five dollars,
and average volatility over 21, 63 and 126 days as the ranking signal.
The lowest-volatility decile is long and the highest is short, with roughly
100 names per book. Rebalancing occurs every three weeks, execution at the
next close, and trading costs are 5 bp per dollar traded.

Figure 1 follows all ten volatility deciles, from the most stable stocks to
the most volatile. The ranking separates risk more clearly than return:
realized volatility rises from 11.9% for the stable stocks
to 37.9% for the volatile stocks, while Sharpe falls from 0.90 to 0.20.
The highest-volatility decile still earns a positive arithmetic return before
costs, but compounds at only 0.35% a year. The low Sharpe makes this group
unattractive per unit of risk, while its large price fluctuations make the
size of the short allocation consequential.

<div class="low-vol-figure decile-profile-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/decile_profile" alt="Bar plots of before-cost Sharpe ratio, annualized geometric return and annualized volatility across ten past-volatility deciles, from the most stable stocks in decile 1 to the most volatile in decile 10." version="12" %}
</div>

<p class="figure-caption"><strong>Figure 1: More volatile stocks earn less per unit of risk.</strong> Before-cost Sharpe ratio, annualized geometric return and annualized volatility, July 1995–May 2026. Decile 1 contains the most stable stocks; decile 10 contains the most volatile. Each decile is measured as a long portfolio.</p>

## Equal capital, unequal risk

To turn the two extreme deciles into a portfolio, the equal-weight rule
allocates 100% of strategy notional to each book. Figure 2 isolates the
resulting imbalance: the short book's standalone volatility is more than
three times the long book's, and its unsigned beta is almost three times as
large. Combining the two books at those sizes gives realized portfolio beta
of −1.12. The allocation adds substantial negative market exposure to the
low-volatility selection.

<div class="low-vol-figure naive-leg-risk-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/naive_leg_risk" mobile="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile" alt="Realised volatility and average beta of the low- and high-volatility deciles" version="11" %}
</div>

<p class="figure-caption"><strong>Figure 2: Equal capital gives the volatile book more risk.</strong> Annualized realized volatility and average point-in-time beta, July 1995–May 2026. The high-volatility book's beta is measured before applying the short sign.</p>

That imbalance motivates the sizing change. Scaling positions by estimated
volatility should reduce the influence of the volatile shorts while retaining
the ranking's preference for low-risk stocks.

## Sizing the two books

I scale each stock's equal-weight allocation by a reference volatility divided
by its estimated volatility. Including a position cap, the absolute allocation is

$$
a_{i,t}=\min\left(\frac{1}{N}\times
\frac{\sigma_{\mathrm{ref}}}{\widehat{\sigma}_{i,t}},\;a_{\max}\right).
$$

Here $N$ is the number of stocks in the book, $\sigma_{\mathrm{ref}}=20\%$
and $a_{\max}=4\%$. The volatility estimate uses 60 sessions with a 5% floor.
If a book exceeds 100% gross, its positions scale down proportionally.
Books below that cap retain their lower gross exposure.

This treatment of book gross is central to the comparison. Rescaling both books
to 100% would increase the allocation to the volatile shorts again. Under this rule,
the long book averages 97% gross exposure and the short book 34%, bringing
total gross exposure down from 200% to about 131%. At those sizes, each book
has standalone volatility of about 10%; equal weighting had left the short
book above 37%. Total portfolio risk also depends on covariance between them.

Changing the relative book sizes also changes market exposure. The capital
difference leaves about 63% net stock exposure, yet the smaller short book
still offsets much of the long book's market sensitivity because it contains
higher-beta stocks. Full-sample realized beta moves from −1.12 to −0.001;
holdings-based and rolling realized estimates vary through time.

The performance comparison therefore combines lower gross exposure with a
different balance between the books and a large change in beta. Most of the
reallocation is on the short side, while the long allocation stays close to
its original size.

## What improves

Table 1 shows how these changes combine at the portfolio level: volatility
falling from 33.4% to 9.8%, geometric return turning positive and turnover
declining.

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

The equal-weight portfolio's positive arithmetic return produces a positive
Sharpe, but volatility drag leaves its geometric return negative. Figure 3
shows the compounded paths: 35 cents
remain per starting dollar, compared with 7.54 dollars under inverse-volatility
sizing. The improvement is substantial, although maximum drawdown remains 38%.

<div class="low-vol-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns" mobile="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile" alt="Growth of one dollar on a logarithmic scale and drawdowns for the equal-weight and volatility-scaled long-short portfolios" version="15" %}
</div>

<p class="figure-caption"><strong>Figure 3: Sizing changes both risk and compounding.</strong> Compounded daily P&amp;L per unit of strategy notional (log scale) and drawdown, July 1995–May 2026, after the 5 bp charge. The rules retain their different exposures and volatilities; Table 1 supplies the risk comparison.</p>

## Shared losses during market rallies

The drawdown panel makes the remaining problem visible. Individual volatility
estimates guide position sizes, but the sizing rule puts no explicit limit on
the books' combined factor exposures or their sensitivity to a common move.
To see how the losses develop, Figure 4 separates the long and short
contributions during two market rallies: the dot-com episode and April
2025–May 2026.

<div class="low-vol-figure regime-comparison-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/regime_comparison" mobile="/assets/2024-12-15-low-volatility-factor/regime_comparison_mobile" alt="Growth of one dollar in the Russell 1000 and low-volatility portfolio, with long- and short-book contributions during the dot-com rally and the April 2025 to May 2026 rally" version="17" %}
</div>

<p class="figure-caption"><strong>Figure 4: Short-book losses in two market rallies.</strong> Before-cost indexed growth above linked cumulative book contributions in percentage points. The dot-com episode comes first, followed by April 2025–May 2026.</p>

From 8 October 1998 to 9 March 2000, the market gains about 52% while the portfolio loses
38% after costs. The short book contributes −27.1 percentage points before
costs, versus −10.4 from the longs. The later reversal brings the portfolio
back toward its starting value.

From 3 April 2025 to 27 May 2026, the market gains about 39% while the portfolio
loses 13%. Longs contribute +4.2 points and shorts −16.3 before costs.
The shorts drive the loss again, and the portfolio ends the sample below its
starting value. Both comparisons measure returns from the first date's close.

The two episodes differ in what the long book contributes. It adds to the
dot-com loss, whereas in the later rally it offsets about a quarter of the
short-book loss. In both cases, the smaller short allocation still drives
most of the loss. That is the portfolio-construction problem left after
the initial risk imbalance has been reduced.

## Where this leaves me
{: #from-individual-weights-to-joint-construction }

I still like inverse-volatility sizing as a simple default here. The ranking
creates an obvious risk imbalance, and this rule addresses it directly with
little additional machinery. Better compounding and lower turnover make it a
useful baseline in this comparison. In my view, that simplicity is a real
advantage.

The remaining drawdowns give the next investigation a specific purpose:
accounting for how positions move together. I'd compare this baseline with
joint construction using covariance and portfolio exposure limits, and check
whether the added complexity improves drawdowns without giving up too much
return after costs. Inverse-volatility sizing already gets us a long way;
the more elaborate approach has to earn its place.
