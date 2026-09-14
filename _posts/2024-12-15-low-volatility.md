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

I rank stocks by volatility, buy the calmest and short the wildest. Then I
give each side the same capital. The catch is that the shorts are about
three times as volatile as the longs: my low-volatility portfolio becomes
a large bet against the wild stocks. I call these long and short groups
the two books. Here I try inverse-volatility sizing: give smaller positions
to stocks with higher estimated volatility, then check how risk and returns
change.

## The wild stocks earn less per unit of risk
{: #what-the-ranking-selects }

The [low-volatility effect](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865)
is the tendency for calm stocks to earn better returns per unit of risk
than wild stocks. Sharpe expresses that trade-off as average return divided
by volatility.[^sharpe] The appeal lies in risk-adjusted returns.
Beta measures how sensitively a stock or portfolio's returns move with the market.
[Frazzini and Pedersen](https://www.nber.org/papers/w16601) offer one explanation
for why this can persist: investors with limited access to borrowing reach
for high-beta stocks instead, bidding up their prices and accepting less
return per unit of risk.[^bab]

That matters for a long-short portfolio. A poor Sharpe differs from a
negative return: volatile stocks can still go up, with a lot of noise along
the way, and a short position pays for every up-move. Before sizing the
short book, I want to see whether these stocks actually lose money or
simply earn little for the risk they take.

I use point-in-time Russell 1000 membership: each ranking uses the stocks
that belonged to the index at that date. I keep stocks priced above five
dollars and rank them by average volatility over one, three and six
months.[^windows] I buy the lowest-volatility decile—the calmest tenth—and
short the highest-volatility decile, the wildest tenth, with roughly 100
names in each book. I rebalance every three weeks, trade at the next close,
and charge 5 bp per dollar traded.

Figure 1 shows all ten volatility deciles, each an equal-weighted long
portfolio of roughly 100 stocks, from the calmest in decile 1 to the wildest
in decile 10. The ranking separates risk much more cleanly than return:
volatility rises from about 12% to 38%, while Sharpe falls by almost
four-fifths. The wildest decile earns about 8% a year before costs on an
arithmetic basis—the average daily return multiplied by a trading year.
Its geometric return, which accounts for compounding, is only about a third
of a percent. Most of the arithmetic return gets eaten by the fluctuations
along the way. These stocks earn little per unit of risk, yet still go up
over the sample. That makes the size of the short book matter.

<div class="low-vol-figure decile-profile-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/decile_profile" alt="Bar plots of before-cost Sharpe ratio, annualized geometric return and annualized volatility across ten past-volatility deciles, from the most stable stocks in decile 1 to the most volatile in decile 10." version="12" %}
</div>

<p class="figure-caption"><strong>Figure 1: More volatile stocks earn less per unit of risk.</strong> Before-cost Sharpe, annualized geometric return and annualized volatility, July 1995–May 2026. Each decile is an equal-weighted long portfolio of about 100 Russell 1000 stocks, re-formed every three weeks; decile 1 is the least volatile. Volatility rises from 11.9% to 37.9% and Sharpe falls from 0.90 to 0.20. Decile 10's annual arithmetic return is 7.55%, versus a geometric return of 0.35%.</p>

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
both books back to 100% would put the capital straight back into the wild
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
a large bet against the market. Once I hedge both portfolios using beta
estimates available before each trade, the average-return advantage
disappears under my financing assumption. Table 1 puts the original
portfolios beside this check. I keep their stock positions and add an index
hedge, with trading costs and a 3% annual financing rate.[^beta-check]

<table class="research-table comparison-table portfolio-card-table">
  <caption><strong>Table 1: Sizing with and without a point-in-time beta hedge.</strong> 12 July 1995–27 May 2026. Returns, volatility and two-way turnover are annualized. Trading costs are 5 bp per dollar traded. The lower rows include index trades and 3% annual hedge financing; turnover includes stocks and the hedge. Sharpe uses a zero cash benchmark.</caption>
  <thead><tr><th>Rule</th><th>Arithmetic return</th><th>Geometric return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th><th>Turnover</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="7">Original portfolios</th></tr>
    <tr><th scope="row">Equal-weight</th><td>2.2%</td><td>−3.3%</td><td>33.4%</td><td>0.07</td><td>−87.8%</td><td>18.8×</td></tr>
    <tr><th scope="row">Inverse-volatility</th><td>7.0%</td><td>6.8%</td><td>9.8%</td><td>0.72</td><td>−38.0%</td><td>12.4×</td></tr>
    <tr class="period-heading"><th colspan="7">Point-in-time beta hedge · 3% financing</th></tr>
    <tr><th scope="row">Equal-weight</th><td>7.5%</td><td>4.6%</td><td>24.5%</td><td>0.30</td><td>−69.9%</td><td>20.1×</td></tr>
    <tr><th scope="row">Inverse-volatility</th><td>6.8%</td><td>6.6%</td><td>9.8%</td><td>0.70</td><td>−37.0%</td><td>13.0×</td></tr>
  </tbody>
</table>

The hedge brings realized beta close to zero for both rules: about 0.011
for equal weighting and 0.005 for inverse volatility. Equal weighting now
averages about 7.5% a year, versus 6.8%, but compounds at only 4.6% versus
6.6%. Financing matters because equal weighting needs a much larger long
index hedge. At zero financing, its arithmetic return is 10.7%; at 5%, it
is 5.3%. Inverse volatility stays near 6.8–6.9% across those assumptions.
The return ordering therefore depends on funding. Different gross
exposures, book sizes and stock weights also remain, so this comparison
does not isolate the stock-level sizing rule.

What I do get is much lower risk: portfolio volatility falls from about 33%
to 10%. I also get a higher Sharpe and a shallower worst drawdown, even in
the hedged comparison. Compounding explains part
of the appeal: the original equal-weight portfolio averages about 2% a year
arithmetically but compounds at roughly −3%, a gap of about five and a half
percentage points. Under inverse-volatility sizing, both
returns are about 7%, with a gap of roughly a quarter of a point.

Turnover measures how much I trade relative to strategy capital, counting
both purchases and sales. Volatility-decile membership churns quickly, so
even a rebalance every three weeks produces about 12–19 times capital in
annual turnover. Smaller short positions reduce the dollars I trade and
the costs I pay.

Figure 3 shows the original compounded paths: about 35 cents remain per
starting dollar under equal weighting, compared with about seven and a half
dollars under inverse-volatility sizing. I read that gap as the combined
effect of changing risk and market exposure. The smaller portfolio still
suffers a worst drawdown of about 38%.

<div class="low-vol-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns" mobile="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile" alt="Growth of one dollar on a logarithmic scale and drawdowns for the equal-weight and volatility-scaled long-short portfolios" version="15" %}
</div>

<p class="figure-caption"><strong>Figure 3: The raw performance gap includes the change in market exposure.</strong> Compounded daily P&amp;L per unit of strategy notional (log scale) and drawdown, July 1995–May 2026, after the 5 bp charge. Terminal indices are 0.35 and 7.54; full-sample realized gross-return betas are −1.12 and −0.001. These are the original portfolios at their different exposures and volatilities; Table 1 adds the point-in-time hedge comparison.</p>

## Shared losses during market rallies

The drawdown panel brings me back to that apparently reassuring combination:
about 63% net long and roughly zero beta over the full sample. Within both
rallies in Figure 4, the short book's market sensitivity outweighs the
longs', leaving the portfolio with negative realized beta.
I size stocks from their individual volatility, leaving their sensitivity
to shared moves free to build up. Figure 4 shows what each book contributes
during the dot-com rally and the rally from April 2025 to May 2026.

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
their shared moves can still overwhelm the longs.

## Where this leaves me
{: #from-individual-weights-to-joint-construction }

I still like inverse-volatility sizing as a simple default here. I keep
the ranking, give the wild stocks less capital, and get much lower risk
and turnover. The beta check narrows the case to those practical benefits
and better risk-adjusted returns. That is enough to make it a useful baseline.

The remaining drawdowns give the next investigation a specific purpose:
accounting for how positions move together. I'd compare this baseline with
joint construction using covariance and portfolio exposure limits, and check
whether the added complexity reduces drawdowns while keeping enough
return after costs. Inverse-volatility sizing already gets us a long way;
the more elaborate approach has to earn its place.

[^sharpe]: I calculate Sharpe using a zero cash rate. Measuring excess returns over a positive cash benchmark would lower both rules' quoted Sharpes. All annualizations use 252 trading sessions.

[^bab]: Andrea Frazzini and Lasse Heje Pedersen, *Betting Against Beta*, author draft dated 10 May 2013, physical PDF pages 2–3; published in the *Journal of Financial Economics* in 2014. Their mechanism concerns market beta; this article ranks total volatility. [Public author draft](https://w4.stern.nyu.edu/facdir/lpederse/papers/BettingAgainstBeta.pdf#page=2).

[^windows]: The ranking averages trailing volatility estimates over 21, 63 and 126 sessions. The separate sizing estimate uses 60 sessions, with a 5% annualized volatility floor.

[^beta-check]: At each signal close I sum target stock weights times their trailing market betas (252 sessions, at least 126 observations, each beta clipped to [−4, 4]). The index target is the negative of that sum. I trade at the next close, earn returns from the following session and hold quantities until the next three-week rebalance. Hedge trading costs are 5 bp per dollar traded. Financing accrues at an assumed 3% annually on signed prior-close index exposure, using calendar days/365 and daily P&L sweeps; short exposure receives the same rate. The 0% and 5% cases vary that assumption. This uses the Russell 1000 return proxy and retains the original stock accounting; historical funding rates, futures basis and roll costs are outside this comparison. The hedge targets estimated beta; realized beta can differ.
