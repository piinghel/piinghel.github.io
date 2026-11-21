---
layout: post
interactive_charts: true
title: "Removing Style Bets from a Ridge Forecast"
description: "Where to deal with style exposure, and what happens when part of it is removed from a Ridge forecast."
permalink: /quants/ridge-style-removal.html
toc: true
date: 2026-10-26
last_modified_at: 2026-11-21
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
style removal hasn't helped. A separate test of adding short interest shows
a small negative full-period Sharpe difference, with considerable uncertainty.

**Correction, 30 October 2026.** The short-interest results below replace an
earlier comparison that overstated the benefit of removing that exposure.

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
resulting book but can restrict sizing. A factor risk model can keep the
forecast intact and account for estimated style risk in the optimizer.

Here I adjust the forecast after fitting (Figure 1), treating the share removed,
$$\lambda$$, as a dial: the removal strength. I'd like to reduce unwanted common risk without giving up too
much return. But I need to check whether that actually happens, what risk is
left, and how much turnover it adds.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/removal-diagram" mobile="/assets/ridge-style-removal/removal-diagram_mobile" alt="Flow from the Ridge forecast through a regression on sectors and styles, subtraction of a share of the style part and the portfolio optimizer to the book, whose P&L splits into a style part and a stock-specific part." version="3" %}
</div>
<p class="figure-caption"><strong>Figure 1. The removal sits between the forecast and the optimizer.</strong> A share λ of the fitted style part is subtracted from the forecast; the optimizer then selects and sizes the book exactly as before. The attribution articles read the same split in the other direction, on the book's P&L.</p>

The optimizer starts from 75 long and 75 short candidates with a 7%
forecast volatility limit and the same position, sector and beta constraints
at every removal strength. I use the risk forecast from the
[rebalancing study]({% link _posts/2026-09-05-rebalancing-luck.md %}).
The reference book realizes about 8.9% volatility against its 7% forecast limit.
All results are means over its three rebalance schedules, after 5 bp per dollar
traded, from January 1999 to April 2026. Intervals are paired 120-session
block-bootstrap 95% intervals against no removal. I compare net Sharpe ratios:
a lower return can be acceptable if volatility falls enough too.

## A fundamental factor model splits the forecast into style and the rest

The tool is the one a fundamental risk model is built on, used on the forecast
instead of on returns. On each date I build a loadings matrix $$B$$ for the
roughly 1,000 stocks in the universe: eleven sector loadings, 1 for the stock's
sector and 0 otherwise, and six
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
  <caption><strong>Table 1. The six style loadings.</strong> Raw characteristic per stock and date, before standardization.</caption>
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
<p class="figure-caption"><strong>Figure 2. The six fitted styles explain about half of the forecast.</strong> Share of each year's cross-sectional forecast variance. The three parts add to 100%: style, the residual, and a thin band for sectors plus the overlap between the sector and style parts, which are fitted together and are not perfectly independent.</p>

## The optimizer uses stock-correlation shrinkage

The factor regression changes the Ridge forecast. The optimizer sizes the
resulting book with the same stock-return covariance estimator throughout this
study.

$$
\Sigma = D\,C\,D,\qquad C=\tfrac{1}{2}\hat R+\tfrac{1}{2}I .
$$

The diagonal of $$D$$ contains each stock's volatility, estimated from its last
21 daily returns and scaled by the reference book’s fixed risk adjustment.
$$\hat R$$ is the correlation matrix of
volatility-standardized daily returns over the last 756 sessions, with at least
252 observations per pair, daily returns capped at ±30% and negative eigenvalues
set to zero. Shrinking it halfway to the identity, as in the
[joint-sizing article]({% link _posts/2026-08-29-joint-sizing.md %}#covariance-and-risk-forecasts),
reduces the optimizer's reliance on individual correlation estimates, at the
cost of pulling potentially useful correlations toward zero.

A factor risk model separates shared style risk from stock-specific risk.
Shrinking stock correlations toward zero can make shared exposures look
cheaper on one side of the portfolio and reduce the hedging credit between
the two sides. The effect on forecast risk depends on the holdings.
The [factor-risk study]({% link _posts/2026-11-20-factor-risk-sizing.md %})
holds the Ridge forecast fixed and changes the covariance estimate directly.

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
<p class="figure-caption"><strong>Figure 3. Volatility falls with removal in this backtest.</strong> Realized volatility and net Sharpe ratio, January 1999–April 2026, mean of three rebalance schedules. The dotted line is no removal.</p>

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 2. Net Sharpe ratio by removal strength and period.</strong> Net Sharpe ratio and its difference against no removal, with a 95% interval for the full period, January 1999–April 2026, mean of three rebalance schedules. The last five years run from May 2021 to April 2026.</caption>
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
<p class="figure-caption"><strong>Figure 4. Before 2019 the gains are positive from 25% to 75%; since 2019 every interval spans zero.</strong> Net Sharpe difference against no removal, mean of three schedules, with paired block-bootstrap 95% intervals. Circles are the six styles and diamonds are PCA.</p>

Figure 5 shows when the gain built up, with every variant scaled to the
full-period volatility of no removal. The 50% removal was 54 points ahead at the end of 2018 and ends at 45; 25% gained
less and kept most of it.

<div class="research-figure responsive-figure">
  {% include blog-chart.html chart="gap" source="/assets/ridge-style-removal/equal-vol-gap.json?v=5" base="/assets/ridge-style-removal/equal-vol-gap" mobile="/assets/ridge-style-removal/equal-vol-gap_mobile" version="4" label="Cumulative net return against no removal at equal volatility for style 25% and 50% and PCA 50%, 1999 to April 2026, with 2019 onward shaded." %}
</div>
<p class="figure-caption"><strong>Figure 5. The gap stopped growing after 2018, and 50% removal gave part of it back.</strong> The chart puts each strategy at the full-period volatility of the unadjusted portfolio. It accumulates the net return differences in points of capital across the three schedules. This is a retrospective comparison. Shading starts in 2019.</p>

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
penalty. The paired comparison covers 1999–2021.

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 3. Adding short interest to 25% style removal.</strong> Net Sharpe ratios, mean of three rebalance schedules. The difference is the seven-style book minus the six-style book at 25%; the full-period interval is a paired 120-session block-bootstrap 95% interval. The last five years are 2017–2021.</caption>
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

I measure short interest as the value of shares sold short relative to market
capitalization, with a one-month lag as a proxy for availability.

## PCA and portfolio-level limits do less

Replacing the styles with the first 10 principal components of trailing returns
lowers volatility about as much but adds little Sharpe (+0.04 at 50%). It falls
short of style removal before 2019 and does a bit better since. The components
start only in 2002, so I read it as a cross-check.

Limiting style exposure on the held book came in 0.13 Sharpe below 25% forecast
removal, before charging for the trades added by the limit. A cap works on the
optimizer’s existing candidate list. Removing style from the forecasts can
change which stocks make the list in the first place.

## Style removal changed the mix of risk
{: #what-i-take-from-this }

Removing part of the six-style component brought realized volatility closer to
the 7% target in this book. The full-period Sharpe gain was uncertain after
accounting for the strengths tested, and the improvement was concentrated
before 2019. The separate short-interest comparison showed different signs
over the full period and the last five years.

Changing the rankings changes which bets reach the portfolio. Taking out common
exposures can lower volatility, give up returns from styles that pay, and leave
stocks that still move together. The clearest effect here was on how the book
took risk. The return trade-off depended on the period.

## References

Giuseppe A. Paleologo, *Advanced Portfolio Management: A Quant's Guide for
Fundamental Investors*, Wiley, 2021, Chapters 6 and 8.

by256,
[*Feature Neutralization Increases Bias and Reduces Variance*](https://forum.numer.ai/t/feature-neutralization-increases-bias-and-reduces-variance/7486),
Numerai Forum, 4 June 2024.

Mark Horvath, Dominik Zvara and Mihaly Berndt,
[*Constructing Portfolios from Published Equity Research*](https://www.msci.com/research-and-insights/blog-post/constructing-portfolios-from-published-equity-research),
MSCI Research, 7 October 2026.

[^book]: Paleologo (2021), Chapter 6, Procedure 6.3; Chapter 8 uses the same factor decomposition to separate style from idiosyncratic P&L.
[^numerai]: See also Numerai's [feature-neutral correlation](https://docs.numer.ai/numerai-tournament/scoring/feature-neutral-correlation).
[^msci]: Mean post-publication information ratio across the signals; these are neutralized signals, not a model's forecast.
[^wls]: Paleologo (2021), Appendix 11.1.2; he averages market cap over about 21 days, here it is the day's value.
