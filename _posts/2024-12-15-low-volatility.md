---
layout: post
title: "Sizing a Low-Volatility Portfolio"
description: "How equal weighting and inverse-volatility sizing compare in risk, market exposure and performance."
date: 2024-12-15
last_modified_at: 2026-09-27
categories: ["Signals"]
article_label: Signals · Low volatility
permalink: /quant/2024/12/15/low-volatility-factor.html
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/low-vol-to-portfolio
---

The [low-volatility effect](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865)
is the tendency of low-volatility stocks to earn about as much as volatile ones
with far less risk. Frazzini and Pedersen offer one explanation: investors who
cannot easily borrow bid up stocks with more market exposure, lowering their
expected returns.[^bab]

The ranking is the easy part. To turn it into a long–short portfolio I also
have to decide how to size the two books, and the obvious choice, equal weights
and equal capital, turns out to be a large bet on the market. In this article I
compare equal weighting with inverse-volatility sizing, and use a market hedge
to separate the sizing from the market exposure it creates.

## Returns and risk across volatility deciles
{: #what-the-ranking-selects }

I rank point-in-time Russell 1000 constituents priced above $5, a liquid and
shortable universe, by their average one-, three- and six-month volatility;
blending horizons gives a steadier ranking and less turnover than any single
window.[^windows] I go long the lowest-volatility decile and short the highest,
roughly 100 names each, which keeps the contrast sharp while leaving each book
diversified. I rebalance every three weeks and trade at the next close, so
every trade uses only information available at the signal.

Figure 1 shows the ten equal-weighted decile portfolios. Compounded returns are
almost flat across the seven least volatile deciles, 10.5–11.6% a year, while
volatility nearly doubles. Beyond that, returns fall: the most volatile decile
compounds at only about a third of a percent a year before costs, and Sharpe
falls from 0.90 in decile 1 to 0.20 in decile 10.

<div class="low-vol-figure decile-profile-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/decile_profile" mobile="/assets/2024-12-15-low-volatility-factor/decile_profile_mobile" alt="Sharpe ratio, annual return and volatility across ten past-volatility deciles, from the least volatile stocks to the most volatile" version="15" %}
</div>


<p class="figure-caption"><strong>Figure 1: More volatile stocks earn less per unit of risk.</strong> Before-cost Sharpe, annual return and volatility, July 1995–May 2026. Each decile is an equal-weighted long portfolio of about 100 stocks, re-formed every three weeks; decile 1 has the lowest volatility. Annual return is compounded throughout this article; Sharpe uses the arithmetic mean daily return and a zero cash rate, which is why decile 10 keeps a Sharpe of 0.20 with a compounded return near zero.</p>

## Equal capital, unequal risk

I start with equal weights within each book and 100% of strategy capital on
each side, for 200% gross exposure. As Figure 2 shows, the short book has more
than three times the long book's standalone volatility and almost three times
its ex-ante beta. The portfolio's realized beta is −1.12: equal capital makes
it a large short position in the market.

<div class="low-vol-figure naive-leg-risk-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/naive_leg_risk" mobile="/assets/2024-12-15-low-volatility-factor/naive_leg_risk_mobile" alt="Realized volatility and average beta of the low- and high-volatility deciles" version="11" %}
</div>


<p class="figure-caption"><strong>Figure 2: The short book dominates risk under equal weighting.</strong> Annualized realized volatility and average ex-ante beta, July 1995–May 2026. The high-volatility book's beta is measured before applying the short sign.</p>

## Inverse-volatility sizing
{: #sizing-the-two-books }

I scale each stock's equal-weight allocation by a reference volatility divided
by its estimated volatility. Including a position cap, the absolute allocation is

$$
a_{i,t}=\min\left(\frac{1}{N}\times
\frac{\sigma_{\mathrm{ref}}}{\widehat{\sigma}_{i,t}},\;a_{\max}\right).
$$

Here $N$ is the number of stocks in the book, $\sigma_{\mathrm{ref}}=20\%$
and $a_{\max}=4\%$. I estimate volatility over about three months, shorter than
the ranking windows so that sizing reacts faster, with a 5% floor.[^windows] If
a book's gross exceeds 100%, I scale it down proportionally; otherwise I leave
it as calculated.

With a 20% reference, the calm long book sits near its 100% cap, at about 97%
gross, while the short book shrinks to 34%. Total gross falls from 200% to about
131%, and the portfolio is about 63% net long in dollars. Both books now have
standalone volatility of about 10%, and because they move against each other,
with a correlation of about −0.55 once the short sign is applied, the portfolio's
volatility is about 10% too.

Realized beta is roughly zero, which is close to a coincidence of the numbers:
the short decile is about 3.2 times as volatile as the long decile and has about
3.0 times its beta, so sizing by volatility almost offsets beta. The two rules
differ in book sizes as well as in the weights within each book, and these
results don't separate the two.

## Comparing the portfolios with a beta hedge
{: #what-improves }

Because the two rules take such different market exposures, I also hedge each
portfolio's beta with the Russell 1000 at every rebalance, using trailing
ex-ante betas.[^beta-check] Table 1 compares all four.

<table class="research-table comparison-table attribution-table">
  <caption><strong>Table 1: Sizing with and without a beta hedge.</strong> 12 July 1995–27 May 2026, after 5 bp trading costs. Annual return is compounded and volatility annualized; the hedge is financed at no cost.</caption>
  <thead><tr><th>Rule</th><th>Annual return</th><th>Volatility</th><th>Sharpe</th><th>Max drawdown</th></tr></thead>
  <tbody>
    <tr class="period-heading"><th colspan="5">Unhedged</th></tr>
    <tr><th scope="row">Equal-weight</th><td>−3.3%</td><td>33.4%</td><td>0.07</td><td>−87.8%</td></tr>
    <tr><th scope="row">Inverse-volatility</th><td>6.8%</td><td>9.8%</td><td>0.72</td><td>−38.0%</td></tr>
    <tr class="period-heading"><th colspan="5">Beta hedged at each rebalance</th></tr>
    <tr><th scope="row">Equal-weight</th><td>8.0%</td><td>24.5%</td><td>0.44</td><td>−68.2%</td></tr>
    <tr><th scope="row">Inverse-volatility</th><td>6.6%</td><td>9.8%</td><td>0.70</td><td>−36.8%</td></tr>
  </tbody>
</table>

Hedging lifts equal weighting's Sharpe from 0.07 to 0.44, so its short market
exposure explains much of its weakness, but inverse volatility still reaches
0.70, with a third of the volatility and about half the drawdown. The hedge
brings realized beta close to zero for both rules (0.011 and 0.005); for
inverse volatility, already near zero at −0.001, it changes little.

Hedged equal weighting does compound faster, 8.0% a year against 6.6%, but at
two and a half times the volatility and only because its large long index
hedge is financed for free. Charging 3% a year on the hedge cuts it to 4.6%, and
5% to 2.3%, while inverse volatility's small hedge barely moves. Neither rule
earns interest on its net long dollars either, so the absolute returns flatter
a funded portfolio; the Sharpe ranking is the robust comparison.

Two-way stock turnover is about 12 times capital a year for inverse volatility
and 19 for equal weighting, which at 5 bp costs about 0.6 and 0.9 points a year;
the hedge adds 0.6 and 1.3 times capital.

Figure 3 shows the paths. Equal weighting ends at 0.35 unhedged and 10.84
hedged, against 7.54 for inverse volatility, but each keeps its own risk:
hedged equal weighting still falls 68% at its worst, against 38%.

<div class="low-vol-figure performance-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns" mobile="/assets/2024-12-15-low-volatility-factor/performance_and_drawdowns_mobile" alt="Growth of one dollar and drawdowns for equal-weight, inverse-volatility and equal-weight with a point-in-time Russell 1000 beta hedge" version="18" %}
</div>


<p class="figure-caption"><strong>Figure 3: Hedging changes the return comparison; the risk gap remains.</strong> Growth of $1 (log scale) and drawdown, July 1995–May 2026, after trading costs. The dashed line adds a Russell 1000 hedge to equal weighting at each rebalance.</p>

## Losses in strong rallies

The inverse-volatility portfolio's worst periods came in strong rallies.
Figure 4 follows it from its high before two of them. The first window, October
1998 to March 2000, is also its deepest drawdown: the portfolio lost about 38%
before costs while the market rose about 52%. In the second, April 2025 to May
2026, it lost about 12% while the market rose about 39%.

On gross contributions the short book looks responsible: roughly −27 points
against −10 for the longs in the dot-com rally, and −16 against +4 in the later
one. But the short book is sized to carry more market beta per dollar, so in any
rally it loses more. Net of each book's own beta the picture changes. In the
dot-com rally both books lagged what their betas implied, the longs by more:
about 24 points against 20. In the later rally the short book did roughly what
its beta implied, and the shortfall of about 6 points came from the calm
longs.[^rally-beta] Net market beta explains only 2 to 7 points of either loss,
depending on how beta is measured, so the beta hedge wouldn't have prevented
them.

<div class="low-vol-figure regime-comparison-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/2024-12-15-low-volatility-factor/regime_comparison" mobile="/assets/2024-12-15-low-volatility-factor/regime_comparison_mobile" alt="Growth of one dollar in the Russell 1000 and low-volatility portfolio, with long- and short-book contributions during the dot-com rally and the April 2025 to May 2026 rally" version="19" %}
</div>


<p class="figure-caption"><strong>Figure 4: Two rallies from the portfolio's high.</strong> Before-cost indexed growth above linked cumulative book contributions in percentage points. Panel A continues to 3 April 2001; episode returns use 8 October 1998–9 March 2000 and 3 April 2025–27 May 2026. Linked long/short contributions are −10.4/−27.1 and +4.2/−16.3 points, and realized portfolio betas in the windows are −0.055 and −0.106.</p>

The dot-com loss was temporary: by April 2001 the portfolio was back to roughly
where it started. The later window ends the sample below its start.

## Which sizing I'd keep
{: #from-individual-weights-to-joint-construction }

Inverse-volatility sizing. At about 131% gross it has a Sharpe of 0.70–0.72
against 0.44 for equal weighting even after hedging, a third of the volatility,
half the drawdown and less turnover, and it stays close to beta-neutral without
a hedge. Funding the hedge and the missing cash return change the absolute
returns, not that ranking.

Two questions stay open. The near-zero beta here is partly a coincidence of the
volatility and beta ratios, and the comparison doesn't separate book sizes from
stock weights: would sizing the books for equal beta do as well, or better? And
why did the calm long book lag its beta in the 2025–26 rally? The optimizer's
portfolio showed the same weakness in [strong
rallies](/quants/short-book-rebounds.html), and whether it's one mechanism is
worth knowing.

[^bab]: Andrea Frazzini and Lasse Heje Pedersen, *Betting Against Beta*, author draft dated 10 May 2013, pages 2–3; published in the *Journal of Financial Economics* in 2014. Their mechanism concerns market beta; this article ranks total volatility. [Public author draft](https://w4.stern.nyu.edu/facdir/lpederse/papers/BettingAgainstBeta.pdf#page=2).

[^windows]: The ranking averages trailing volatility estimates over 21, 63 and 126 sessions. The separate sizing estimate uses 60 sessions, with a 5% annualized volatility floor. Ex-ante beta is each stock's trailing 252-session beta (at least 126 observations) at the signal; realized beta is the full-sample regression of daily portfolio returns on the Russell 1000.

[^beta-check]: At each signal close, the Russell 1000 hedge offsets the sum of stock weights times their ex-ante betas, clipped to [−4, 4]. Stocks and hedge trade at the next close and hold fixed quantities until the next three-week rebalance. Returns start after execution. The simulation applies transaction costs of 5 bp of traded notional; funding, stock borrow fees, futures roll costs and delisting returns are excluded, the last mattering most for the high-volatility short book. Returns compound daily P&L per unit of strategy notional; annualization uses 252 sessions.

[^rally-beta]: Summing each book's daily before-cost P&L and removing its in-window market beta; using the books' ex-ante betas instead gives the same split. The figure's linked contributions differ slightly because they compound.
