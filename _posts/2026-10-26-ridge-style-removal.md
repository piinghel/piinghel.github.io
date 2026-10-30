---
layout: post
interactive_charts: true
title: "Removing Style Bets from a Ridge Forecast"
description: "Where to deal with style exposure, and what happens when part of it is removed from a Ridge forecast."
permalink: /quants/ridge-style-removal.html
toc: true
date: 2026-10-26
last_modified_at: 2026-10-30
categories: ["Portfolio construction"]
article_label: Portfolio construction · Style removal
---

In the attribution articles I split the Ridge portfolio's return by its
estimated sources. Style kept showing up on both sides: it accounts for a good
part of the return, and in
[Part 2]({% link _posts/2026-09-09-short-book-rebounds.md %}) it was also
behind the deepest drawdowns. That made me wonder what happens if I take some
style out earlier, from the forecast the portfolio is built on.

About half of the [Ridge forecast]({% link _posts/2025-02-09-combining-predictors.md %})
is explained by the styles I use here. Taking some of that out lowers the
book's volatility in this backtest, and improves the full-period Sharpe ratio at
some strengths. But the gains were earned before 2019, and in the last five years
style removal hasn't helped at all. A separate test of adding short interest
shows a small negative full-period Sharpe difference, with considerable
uncertainty. And even if the results had been stronger, momentum or low volatility
might still be bets I want to keep.

**Correction, 30 October 2026:** An earlier version overstated the benefit of
removing short interest because the input mixed split-adjusted shares with
unadjusted prices. The short-interest results below use a corrected input in a
different test; the six-style results are unaffected.

## Style bets and stock-specific bets behave differently

A stock-ranking forecast mixes two kinds of bets. Some are on characteristics
that many stocks share: low volatility, momentum, size. Others are on what is
specific to a company. Both can pay, but they behave very differently in a
portfolio. When momentum turns, stocks with similar momentum exposure can move
together, so adding more stocks with the same exposure may offer little
protection against that shared move.
Company-specific bets can diversify, but 150 positions do not guarantee it:
their returns can still be correlated, including through exposures the factor
model misses. And a shared style bet can earn enough to justify its risk.

One way to understand and adjust those exposures is to separate the style part
of the forecast. Giuseppe Paleologo's
*Advanced Portfolio Management* regresses a fundamental investor's alphas on
factor loadings and sizes positions from the residual.[^book] Numerai subtracts
part of the fitted feature exposure from machine-learning predictions; a forum
study there finds a bias–variance trade-off in its setting.[^numerai]
MSCI evaluates published equity signals after neutralizing them to eight style
factors, and the average signal's information ratio rises from 0.17 to 0.28.[^msci]

There are a few places to make that choice. I could remove style from the
predictors or the training target, adjust the forecast after fitting, or limit
exposures when building the portfolio. Each changes a different part of the
problem: cleaning the target changes what the model learns; adjusting the
forecast can change which stocks are selected; portfolio limits control the
resulting book but can restrict sizing. A factor risk model offers another route:
keep the forecast and let the optimizer account for estimated style risk.

Here I adjust the forecast after fitting (Figure 1), treating the share removed,
$$\lambda$$, as a dial: the removal strength. I'd like to reduce unwanted common risk without giving up too
much return. But I need to check whether that actually happens, what risk is
left, and how much turnover it adds.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/removal-diagram" mobile="/assets/ridge-style-removal/removal-diagram_mobile" alt="Flow from the Ridge forecast through a regression on sectors and styles, subtraction of a share of the style part and the portfolio optimizer to the book, whose P&L splits into a style part and a stock-specific part." version="3" %}
</div>
<p class="figure-caption"><strong>Figure 1: The removal sits between the forecast and the optimizer.</strong> A share λ of the fitted style part is subtracted from the forecast; the optimizer then selects and sizes the book exactly as before. The attribution articles read the same split in the other direction, on the book's P&L.</p>

The book is the joint-sizing optimizer: 75 long and 75 short names, a 7%
forecast volatility target, and its position, sector and beta limits, with the
1.18 volatility multiplier of
[Reducing Rebalancing Luck]({% link _posts/2026-09-05-rebalancing-luck.md %}).
It takes more risk than the books in
[joint sizing]({% link _posts/2026-08-29-joint-sizing.md %}) and
[momentum crashes]({% link _posts/2026-09-30-momentum-crashes-ridge.md %}): it realizes
about 8.9% volatility instead of 7%, so its returns and drawdowns are about 25%
larger, while its Sharpe ratio over the same dates is close to theirs, 1.20 against 1.23.
All results are means over its three rebalance schedules, after 5 bp per dollar
traded, from January 1999 to April 2026. Intervals are paired 120-session
block-bootstrap 95% intervals against no removal. I compare net Sharpe ratios:
a lower return can be acceptable if volatility falls enough too.

## A fundamental factor model splits the forecast into style and the rest

The tool is the one a fundamental risk model is built on, used on the forecast
instead of on returns. On each date I build a loadings matrix $$B$$ for the
roughly 1,000 stocks in the universe: eleven sector loadings, 1 for the stock's
sector and 0 otherwise (with the sector classification held fixed), and six
style loadings (Table 1). Then I regress the forecast on it:

$$
y = Bx + \epsilon .
$$

This is Paleologo's Procedure 6.3 with the forecast in place of the alpha
vector. $$x$$ holds the fitted coefficient for each sector and style that day,
and $$\epsilon$$ is the part these loadings don't explain. A risk model runs the same
regression with returns on the left, and then $$x$$ is the day's factor returns;
the attribution articles do exactly that for the book's P&L.

How the loadings are estimated matters. Each raw characteristic in Table 1 uses
data up to that day's close. Then, on every date and across all stocks, each of
the six styles is put on a common scale in four steps:

1. Winsorize at five median absolute deviations from the median (the MAD scaled by 1.4826, so it matches a standard deviation for normal data).
2. Fill a missing value of beta, residual volatility, momentum, size or liquidity with the capitalization-weighted average.
3. Centre it so that the capitalization-weighted average is zero, which means the cap-weighted market has no style exposure.
4. Scale it to an equal-weighted standard deviation of one, so one unit is one cross-sectional standard deviation for every style.

Residual volatility gets one more step: it is regressed on beta and size and only
the residual is kept, because volatile stocks also tend to be small and high-beta,
and without this it would partly duplicate those two.

<table class="research-table settings-table">
  <caption><strong>Table 1: The six style loadings.</strong> Raw characteristic per stock and date, before standardization.</caption>
  <thead><tr><th>Style</th><th>Raw characteristic</th><th>Window</th></tr></thead>
  <tbody>
    <tr><th scope="row">Beta</th><td>Slope of the stock's daily returns on the Russell 1000, shrunk toward 1 in proportion to its sampling variance (prior variance 0.25), clipped at ±4</td><td>252 sessions, at least 126</td></tr>
    <tr><th scope="row">Residual volatility</th><td>Log standard deviation of that regression's residuals</td><td>252 sessions</td></tr>
    <tr><th scope="row">Momentum</th><td>Sum of daily log returns, leaving out the latest 21 sessions</td><td>252 sessions</td></tr>
    <tr><th scope="row">Size</th><td>Log market capitalization</td><td>That day</td></tr>
    <tr><th scope="row">Liquidity</th><td>Log of the median daily dollar volume divided by market capitalization</td><td>63 sessions</td></tr>
    <tr><th scope="row">Short-term reversal</th><td>Minus the stock's return</td><td>21 sessions</td></tr>
  </tbody>
</table>

The regression is weighted least squares with square-root market-cap weights, the
usual practical stand-in for inverse idiosyncratic variance in a return
regression;[^wls] with a forecast on the left-hand side the weighting is a choice.
Every stock has exactly one sector loading of 1, so the sector columns act as
the intercept.

Removal subtracts a share $$\lambda$$ of the fitted style part and keeps the
sector part and the residual:

$$
y'_i=y_i-\lambda\sum_{k\in\text{styles}}B_{ik}\,\hat x_k .
$$

The adjusted forecasts go into the optimizer as they are, without re-ranking. I
tried $$\lambda$$ = 25%, 50%, 75% and 100%. At 25%, the forecast's variance falls
by about a fifth. Momentum matters in this comparison: leaving it out of the
removal at 50% lowers Sharpe by 0.10 and adds half a point of volatility.

The six styles don't directly measure short interest. Heavily shorted stocks can
share crowding risk, especially in a squeeze, which makes short interest worth
looking at separately. That doesn't mean removing it will improve a forecast or
portfolio; I'll come back to the corrected comparison below.

## Half of the Ridge forecast is style

The same regression splits the forecast's cross-sectional variance into three
parts. The six styles carry 50% of it on average and 58% since 2019 (Figure 2). One
possible contributor is the target: the model predicts a forward 20-session
Sharpe ratio, which can favour low-volatility stocks, depending on their returns.

That split depends on the predictors, the styles and how they are estimated.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/forecast-style-share" mobile="/assets/ridge-style-removal/forecast-style-share_mobile" alt="Stacked shares of the Ridge forecast's cross-sectional variance by year, adding to 100%: style between 40% and 65%, residual most of the rest, and a thin band for sectors and overlap." version="3" %}
</div>
<p class="figure-caption"><strong>Figure 2: The six fitted styles explain about half of the forecast.</strong> Share of each year's cross-sectional forecast variance. The three parts add to 100%: style, the residual, and a thin band for sectors plus the overlap between the sector and style parts, which are fitted together and are not perfectly independent.</p>

## The optimizer's risk model is a shrunk covariance, not a factor model

The optimizer needs a covariance matrix to size positions, and it does not use a
factor model for it. It uses a sample covariance estimated directly from stock
returns:

$$
\Sigma = D\,C\,D,\qquad C=\tfrac{1}{2}\hat R+\tfrac{1}{2}I .
$$

$$D$$ holds each stock's volatility: the sample standard deviation of its last 21
daily returns, floored at 5% a year (20% when there isn't enough history), times
a multiplier of 1.18. $$\hat R$$ is the correlation matrix of
volatility-standardized daily returns over the last 756 sessions, with at least
252 observations per pair, daily returns capped at ±30% and negative eigenvalues
set to zero. Shrinking it halfway to the identity, as in the
[joint-sizing article]({% link _posts/2026-08-29-joint-sizing.md %}#covariance-and-risk-forecasts),
reduces the optimizer's reliance on individual correlation estimates, at the
cost of pulling potentially useful correlations toward zero.

A factor risk model would write the covariance as
$$B\Omega_fB'+\Omega_\epsilon$$, separating the factor covariance
$$\Omega_f$$ from the residual covariance $$\Omega_\epsilon$$. A shrunk
sample covariance has no such separation: halving every correlation also halves
those that come from shared styles, which can make concentrated style exposure
look too cheap and may help explain why the book overshoots its 7% target.
Removing style from the forecast is not the same as changing the covariance used
for sizing.

The attribution puts the trade-off in perspective. In the unadjusted book the
style P&L has a Sharpe ratio of 0.93, against 0.49 for the
stock-specific P&L. Removal changes which stocks are held. The unadjusted book's
names carrying the 50%-removal book's style exposures would have earned a Sharpe
ratio of 1.19, the same as doing nothing, while the actual 50% book earned 1.38;
about a third of its weight sits in different names. That comparison suggests
selection matters here, though it does not establish a general mechanism.

## Removal lowers volatility at every strength and raises the Sharpe ratio up to 75%

Figure 3 shows the two numbers that matter side by side. Volatility falls at
every step, from 8.9% with no removal to 7.3% with full removal. Up to 75% the
return doesn't fall with it, so the Sharpe ratio rises, from 1.20 to 1.38 at 50%
and 1.41 at 75%. At full removal the return gives way and the Sharpe ratio is back
at 1.20.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/risk-return" mobile="/assets/ridge-style-removal/risk-return_mobile" alt="Volatility and net Sharpe ratio for each variant: volatility falls with every step of style removal, and the Sharpe ratio rises to 1.38 at 50% and 1.41 at 75% before falling back to 1.20 at full removal." version="4" %}
</div>
<p class="figure-caption"><strong>Figure 3: Volatility falls with removal in this backtest.</strong> Realized volatility and net Sharpe ratio, January 1999–April 2026, mean of three rebalance schedules. The dotted line is no removal.</p>

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 2: Net Sharpe ratio by removal strength and period.</strong> Net Sharpe ratio and its difference against no removal, with a 95% interval for the full period, January 1999–April 2026, mean of three rebalance schedules. The last five years run from May 2021 to April 2026.</caption>
  <thead>
    <tr><th>Removal</th><th>Net Sharpe</th><th>Δ full [95%]</th><th>Δ 1999–2018</th><th>Δ 2019–2026</th><th>Δ last five years</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">No removal</th><td>1.20</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
    <tr><th scope="row">Style 25%</th><td>1.27</td><td>+0.07 [−0.01, +0.16]</td><td>+0.12</td><td>−0.02</td><td>−0.02</td></tr>
    <tr><th scope="row">Style 50%</th><td>1.38</td><td>+0.19 [+0.03, +0.34]</td><td>+0.32</td><td>−0.11</td><td>−0.22</td></tr>
    <tr><th scope="row">Style 75%</th><td>1.41</td><td>+0.22 [−0.04, +0.49]</td><td>+0.39</td><td>−0.18</td><td>−0.35</td></tr>
    <tr><th scope="row">Style 100%</th><td>1.20</td><td>0.00 [−0.39, +0.40]</td><td>+0.21</td><td>−0.54</td><td>−0.88</td></tr>
    <tr><th scope="row">PCA 25%</th><td>1.19</td><td>−0.01 [−0.10, +0.06]</td><td>−0.01</td><td>−0.01</td><td>+0.03</td></tr>
    <tr><th scope="row">PCA 50%</th><td>1.23</td><td>+0.04 [−0.13, +0.18]</td><td>0.00</td><td>+0.09</td><td>+0.13</td></tr>
  </tbody>
</table>

The 50% gain has an interval clear of zero, but I tried roughly 28 removal
variants on this history, and none of these settings has an independent test.
Turnover rises from 24.7 to 27.2 times capital
a year at 50%, and the net figures already pay 5 bp per dollar traded for it.

## The Sharpe gain was earned before 2019

Before 2019 the gains at 25% to 75% were positive (Figure 4). Since 2019 the estimates are close to zero or negative, and every
interval spans zero. The difference between the two periods is clear at 50% and
above. Over the last five years every
strength above 25% trails no removal, and 25%
is about level (Table 2). The weak stretch is mostly
2021 and 2024–2025; 2019–2023 on its own is about flat. I picked 2019 as the
split after looking at the data, and with a split at 2016 the later period is
slightly positive, so the boundary is soft.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/delta-sharpe" mobile="/assets/ridge-style-removal/delta-sharpe_mobile" alt="Net Sharpe difference against no removal by strength with 95% intervals: positive for 25 to 75 percent before 2019, and intervals spanning zero from 2019." version="5" %}
</div>
<p class="figure-caption"><strong>Figure 4: Before 2019 the gains are positive from 25% to 75%; since 2019 every interval spans zero.</strong> Net Sharpe difference against no removal, mean of three schedules, with paired block-bootstrap 95% intervals. Circles are the six styles and diamonds are PCA.</p>

Figure 5 shows when the gain built up, with every variant scaled to the
full-period volatility of no removal. The 50% removal was 54 points ahead at the end of 2018 and ends at 45; 25% gained
less and kept most of it.

<div class="research-figure responsive-figure">
  {% include blog-chart.html chart="gap" source="/assets/ridge-style-removal/equal-vol-gap.json?v=5" base="/assets/ridge-style-removal/equal-vol-gap" mobile="/assets/ridge-style-removal/equal-vol-gap_mobile" version="4" label="Cumulative net return against no removal at equal volatility for style 25% and 50% and PCA 50%, 1999 to April 2026, with 2019 onward shaded." %}
</div>
<p class="figure-caption"><strong>Figure 5: The gap stopped growing after 2018, and 50% removal gave part of it back.</strong> Cumulative daily net return difference against no removal, in points of capital, with each variant scaled to the full-period volatility of no removal; mean of three schedules. Shaded: 2019 onward.</p>

One possibility is that the trade-off changed: since 2019 the book's
stock-specific P&L has paid much less (a Sharpe ratio of 0.10, against 0.63
before) while the style P&L kept paying. That is consistent with the fade, but
doesn't tell me how much it caused. A plain
score-weighted portfolio of the adjusted forecast, with no optimizer, still
improves at every strength after 2019. The comparison points toward selection or
sizing as part of the difference, though both portfolios change in other ways too.

## Short interest is a separate trade-off

Short interest is worth looking at because heavily shorted stocks can share
crowding risk. I compared 25% removal of the six styles with 25% removal of
those styles and short interest together. I did this for Ridge and LightGBM,
using both the original forecasts and forecasts trained with a style-exposure
penalty. This is a separate portfolio test covering 1999–2021, with a different
engine from the 1999–April 2026 book above.

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 3: Adding short interest to 25% style removal.</strong> Net Sharpe ratios, mean of three rebalance schedules. The difference is the seven-style book minus the six-style book at 25%; the full-period interval is a paired 120-session block-bootstrap 95% interval. The last five years are 2017–2021.</caption>
  <thead><tr><th>Forecast</th><th>Six styles</th><th>Six + short interest</th><th>Δ 1999–2021 [95%]</th><th>Δ 2017–2021</th></tr></thead>
  <tbody>
    <tr><th scope="row">LightGBM, original</th><td>2.321</td><td>2.300</td><td>−0.021 [−0.067, +0.019]</td><td>+0.024</td></tr>
    <tr><th scope="row">LightGBM, penalized</th><td>2.443</td><td>2.409</td><td>−0.033 [−0.086, +0.015]</td><td>+0.032</td></tr>
    <tr><th scope="row">Ridge, original</th><td>1.356</td><td>1.305</td><td>−0.052 [−0.117, +0.010]</td><td>+0.053</td></tr>
    <tr><th scope="row">Ridge, penalized</th><td>1.493</td><td>1.428</td><td>−0.065 [−0.141, +0.005]</td><td>+0.010</td></tr>
  </tbody>
</table>

Adding short interest reduced measured forecast dependence on the included
factors, but increased information-coefficient volatility. The full-period
Sharpe differences are negative in all four comparisons, though their intervals
include zero. The last five years are mildly positive. Short interest may be
useful to control a particular exposure, but this test doesn't establish a
return or signal-stability improvement.

For this comparison, I converted short-interest shares to the historical share
basis using unadjusted volume divided by split-adjusted volume, then multiplied
by unadjusted price and divided by market capitalization. I lagged the whole
ratio by 21 trading sessions and kept reported zero separate from unknown.
The lag is a proxy for availability: publication and data vintage timing
haven't been verified.

## PCA and portfolio-level limits do less

Replacing the styles with the first 10 principal components of trailing returns
lowers volatility about as much but adds little Sharpe (+0.04 at 50%). It falls
short of style removal before 2019 and does a bit better since. The components
start only in 2002, so I read it as a cross-check.

Limiting style on the finished portfolio did worse. A cost-free style-beta limit
on the book was 0.13 Sharpe behind 25% forecast removal, and hard style caps in the
optimizer had no feasible solution on 24 April 2009 other than the empty book. The
150 names are chosen from the forecast before the optimizer weights them. A
limit can change their weights, but it can't choose different names to offset an
exposure. That fits Clarke,
de Silva and Thorley's point that constraints limit how much of a signal reaches
the weights.[^clarke] Another alternative is to hedge part of
the risk with covariance-based portfolios, as Daniel, Mota, Rottke and Santos do
for characteristic portfolios.[^daniel]

## What I take from this

For this book, removing style from the forecast changes the mix of bets. Volatility
fell at every strength tested and moved closer to the 7% target, but that alone
doesn't establish better risk forecasts in other periods or portfolios. For the
six styles the full-period Sharpe gain is uncertain once the variants are
accounted for, and the recent results don't show the earlier improvement.
The corrected short-interest evidence is mixed and comes from a different test.

I would start with 25% removal of the six styles if reducing this book's style
exposure were the goal: it is a modest adjustment, not a proven optimal setting.
I'd keep no removal as a serious
alternative. A style bet may be deliberate and well rewarded; removing it may
also leave correlated residual bets or discard useful stock selection.

A factor risk model in the optimizer, separate decisions for each style (short
interest included) and a style-adjusted training target would each handle this
risk differently. For now, the result argues for measuring the bets and their
costs at matched risk, not for treating style removal as the default.

## References

Giuseppe A. Paleologo, *Advanced Portfolio Management: A Quant's Guide for
Fundamental Investors*, Wiley, 2021, Chapters 6 and 8.

by256,
[*Feature Neutralization Increases Bias and Reduces Variance*](https://forum.numer.ai/t/feature-neutralization-increases-bias-and-reduces-variance/7486),
Numerai Forum, 4 June 2024.

Mark Horvath, Dominik Zvara and Mihaly Berndt,
[*Constructing Portfolios from Published Equity Research*](https://www.msci.com/research-and-insights/blog-post/constructing-portfolios-from-published-equity-research),
MSCI Research, 7 October 2026.

Roger Clarke, Harindra de Silva and Steven Thorley,
*Portfolio Constraints and the Fundamental Law of Active Management*, Financial
Analysts Journal 58(5), 2002, 48–66.

Kent Daniel, Lira Mota, Simon Rottke and Tano Santos,
[*The Cross-Section of Risk and Returns*](https://doi.org/10.1093/rfs/hhaa021),
Review of Financial Studies 33(5), 2020, 1927–1979.

[^book]: Paleologo (2021), Chapter 6, Procedure 6.3; Chapter 8 uses the same factor decomposition to separate style from idiosyncratic P&L.
[^numerai]: See also Numerai's [feature-neutral correlation](https://docs.numer.ai/numerai-tournament/scoring/feature-neutral-correlation).
[^msci]: Mean post-publication information ratio across the signals; these are neutralized signals, not a model's forecast.
[^wls]: Paleologo (2021), Appendix 11.1.2; he averages market cap over about 21 days, here it is the day's value.
[^clarke]: Their transfer coefficient is 1 when the signal reaches the weights unconstrained; constrained managers typically sit between 0.3 and 0.8.
[^daniel]: The squared Sharpe ratio of their five characteristic portfolios rises from 1.16 to 2.16, per the authors' abstract.
