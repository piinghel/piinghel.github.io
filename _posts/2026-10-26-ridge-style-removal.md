---
layout: post
interactive_charts: true
title: "Removing Style Bets from a Ridge Forecast"
description: "Half of the Ridge forecast is style. Removing part of it before the portfolio is built lowers risk and helps on the early history; after 2019 every strength loses, and statistical factors do not make a better substitute."
permalink: /quants/ridge-style-removal.html
toc: true
date: 2026-10-26
categories: ["Portfolio construction"]
article_label: Portfolio construction · Style removal
---

The attribution articles split the Ridge portfolio's return by what it is paid
for, and style characteristics turned up on both sides of the ledger. They earn
return, and in
[Part 2]({% link _posts/2026-09-09-short-book-rebounds.md %}) the deepest
drawdowns came mostly from the low-risk package, chiefly low volatility. That split is made after the
fact, on the book. Here I make the same split earlier, on the forecast the book
is built from, and ask whether part of the style content should come out before
the portfolio is formed.

The question is not free of cost. Style characteristics explain 50% of the
[Ridge forecast's]({% link _posts/2025-02-09-combining-predictors.md %})
cross-sectional variance, and 58% after 2019. Removing some of that lowers risk
and leaves more of the risk budget for stock-specific bets. It also throws away
a component that was paid on average, and the price of that shows up when styles
keep winning. Over the full history light-to-moderate removal raises the Sharpe
ratio; almost all of the gain sits before 2019, and after 2019 every strength I
tried loses to no removal. A statistical alternative (principal components) and
controls on the finished portfolio do worse.

Figure 1 shows where the removal sits. The forecast is split on each date into a
sector part, a style part and a stock-specific remainder, a share of the style
part is subtracted, and the adjusted scores go through selection and sizing as
before. The attribution articles read the same split in the other direction, on
the book's P&L and variance.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/removal-diagram" mobile="/assets/ridge-style-removal/removal-diagram_mobile" alt="Flow from the Ridge forecast through a split into sector, style and stock-specific parts, subtraction of a share of the style part, selection of 75 long and 75 short names and sizing, ending in book weights, whose P&L and variance split into a style part and a stock-specific part." version="1" %}
</div>
<p class="figure-caption"><strong>Figure 1: Removal acts on the forecast, and attribution reads the result in the book.</strong> The dial $$\lambda$$ is the share of the fitted style part subtracted from the forecast. The book's exposure to the styles, $$X'w$$, is inherited from the forecast's style loadings; the stock-specific part, $$w'e$$, is what remains.</p>

I am not the first to remove a fitted exposure from predictions. Giuseppe
Paleologo's *Advanced Portfolio Management* does it for a fundamental
investor's alpha vector, regressing it on factor loadings and sizing from the
residual.[^book] Numerai's tournament does the same to machine-learning
predictions with a tunable proportion, and a forum study there finds bias
rising and variance falling as the proportion grows, with about one half a
good trade-off for that model.[^numerai] MSCI neutralizes published equity
signals to market beta or to eight style factors before evaluating them, and
the average post-publication information ratio of a signal rises from 0.17 raw
to 0.28 style-neutral.[^msci] That is a different object from this article: MSCI
neutralizes the signals it evaluates, and does not remove style from a model's
forecast before sizing or from its training target. Their results are also
signal-level, without an optimizer that prices risk. The question here is how
much of such a gain survives one, and since a Ridge forecast is learned from
returns and part of its style content is what the model found, I treat the
removed share as a dial to measure and not as a switch.

The book is the joint-sizing optimizer with 75 long and 75 short names, a 7%
forecast volatility target and its position, sector and beta limits. Every number
below is the mean of three rebalance schedules a week apart, as in
[Reducing Rebalancing Luck]({% link _posts/2026-09-05-rebalancing-luck.md %}),
after costs of 5 bp per dollar traded, from 26 January 1999 to 28 April 2026.
Turnover is two-way: purchases plus sales, as a multiple of capital per year.
Intervals are paired 120-session block-bootstrap 95% intervals against no
removal.

## Half of the forecast is style

On each date I split the forecast's cross-sectional variance into a sector part,
a style part (beta, residual volatility, momentum, size, liquidity and
short-term reversal) and a stock-specific remainder. Style carries 50% of the
variance on average and 58% after 2019 (Figure 2). For a LightGBM forecast on
the same data it is 28%, so the Ridge forecast is the more style-driven of the
two.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/forecast-style-share" mobile="/assets/ridge-style-removal/forecast-style-share_mobile" alt="Stacked shares of the Ridge forecast's cross-sectional variance by year: style between 40% and 65%, stock-specific most of the rest." version="1" %}
</div>
<p class="figure-caption"><strong>Figure 2: Style is half of the Ridge forecast and has grown since 2019.</strong> Share of each year's cross-sectional forecast variance explained by the six style exposures (blue), left to the stock-specific remainder (grey), or assigned to sectors and cross terms (light grey, top). Sector dummies and styles are fitted jointly with square-root-of-market-cap weights.</p>

## The style part earns its return with half the consistency

The style part of the forecast is not worthless. Its rank correlation with
subsequent returns (the IC) is 0.034, the same as the stock-specific part's.
The difference is in how steadily it pays: the information ratio of the daily
IC is 0.31 for the style part and 0.60 for the stock-specific part. Built into
portfolios on their own, the style part earns a Sharpe ratio of 0.07 and the
stock-specific part 1.09.

My reading is that a style bet pays on average but pays unevenly, and every
position shares it at once, while stock-specific bets diversify each other. If
that is right, a forecast that devotes half of its variance to style is
spending its risk on the part that earns least per unit of risk. Whether that
matters for the portfolio depends on how the optimizer prices risk.

## The risk model prices common risk at a discount

The optimizer sees risk through a covariance matrix $$\Sigma_t=D_tC_tD_t$$.
Each stock's volatility in $$D_t$$ is its 21-session realized volatility times a
multiplier. The correlation matrix $$C_t$$ is estimated from 756 sessions of
volatility-standardized returns, with at least 252 observations, and shrunk
halfway to the identity, $$C_t=0.5\,\widetilde R_t+0.5\,I$$. The
[joint-sizing article]({% link _posts/2026-08-29-joint-sizing.md %}#covariance-and-risk-forecasts)
explains why: the optimizer puts its largest bets where estimated risk is
lowest, and shrinkage makes those estimates less fragile.

Two consequences matter here. First, halving every correlation halves their
average, so the model understates common risk by construction, and the
multiplier is a patch for that. The joint-sizing article calibrates it at 1.55
on development data; as in the rebalancing article, the books here keep the
earlier 1.18, so they take more risk at the same 7% forecast target. The
realized volatility of 8.9% against the 7% target, a ratio of 1.27, is the usual
mark of shrunk correlations and a low multiplier. I do not treat it as evidence
that style risk is mispriced. A constant multiplier rescales every book alike,
which is why I compare Sharpe ratios; rescaling each book to a constant
trailing realized volatility leaves the ordering below unchanged.[^vt]

Second, a multiplier cannot change the mix. The common risk that shrinkage
discounts is the same common risk a style bet carries, so style positions in the
forecast get through the optimizer at a discount compared with stock-specific
ones. That is the channel through which removal could help, and it is specific to
this covariance model. A model with explicit style factors, or less
shrinkage, would price the bets directly and might capture part of the gain
below. I have not tested one, so the results describe this risk model.

## Removal should help where style earns less than it risks

The attribution articles write the book's return as exposure times payoff. For
returns $$R_i=x_i'f+e_i$$, with style exposures $$x_i$$, factor returns $$f$$ and
stock-specific returns $$e_i$$, the book's return and variance split as

$$
w'R=(X'w)'f+w'e,\qquad
\operatorname{Var}=(X'w)'\Sigma_f(X'w)+\sum_i w_i^2\sigma_i^2 .
$$

The weights come from a forecast $$y_i=x_i'b+r_i$$ with a style part and a
remainder, so the book's style exposure $$X'w$$ is inherited from the forecast's
style loadings $$b$$. The two variance terms behave differently. Style variance
is common to every position and does not fall as names are added; stock-specific
variance does. At a fixed risk budget, each unit of variance spent on style is
unavailable for stock-specific bets.

In a linear portfolio, let $$S$$ be the return from the style part and $$P$$ the
whole book, and scale the style part by $$a=1-\lambda$$. Then $$d\ln\mathrm{SR}/da=\mu_S/\mu_P-\operatorname{Cov}(S,P)/\operatorname{Var}(P)$$,
so a small removal raises the Sharpe ratio if and only if

$$
\underbrace{\frac{\mu_S}{\mu_P}}_{\text{return share of style}}\;<\;\underbrace{\frac{\operatorname{Cov}(S,P)}{\operatorname{Var}(P)}}_{\text{risk share of style}}.
$$

Style has to earn a smaller share of the book's return than it contributes to
its risk. Selection and the optimizer change this picture, which is why the full
book is tested below. Table 1 lists what that statement assumes and where I look for each
assumption failing.

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 1: The argument fails in four ways, and each has a test.</strong> What removal needs to be true and the evidence in the sections below.</caption>
  <thead><tr><th>Assumption</th><th>If it fails</th><th>Where it is tested</th></tr></thead>
  <tbody>
    <tr><th scope="row">Style's return share is below its risk share</th><td>Removal lowers return as much as risk</td><td>Stand-alone Sharpe above; Table 2</td></tr>
    <tr><th scope="row">Style premia are stable enough for a historical return share to carry forward</th><td>The share flips and removal costs return</td><td>Split at 2019; Table 3, Figure 4</td></tr>
    <tr><th scope="row">The style projection separates style from stock-specific information</th><td>Removal also takes out stock-specific return</td><td>Return change by removal step</td></tr>
    <tr><th scope="row">The risk model does not already price the style risk</th><td>Little is left to remove</td><td>PCA variant; controls on the book</td></tr>
  </tbody>
</table>

The first assumption is estimated on the same history the result is judged on,
which is the main reason to read the strengths below as a trade-off and not as an
optimum.

## Removal takes out a share of the fitted style part

Each date I regress the forecast on sector dummies and the six style exposures,
subtract a share $$\lambda$$ of the fitted style part, keep the sector part and
leave the remainder as it is:

$$
y'_i=y_i-\lambda\sum_{k\in\text{styles}}\hat\beta_k\,x_{ik}.
$$

The adjusted scores then go through selection and the optimizer exactly as
before; I don't re-rank. This removes the style part from the forecast, after
prediction; removing it from the training target is a different intervention, and
for LightGBM it gave a smaller gain than removing it from the forecast, +0.03
against +0.07 at 25%. The Numerai and Paleologo rule is $$\lambda=1$$. I run
$$\lambda=0.25,\,0.5,\,0.75$$ and $$1$$ and compare each with no removal.

$$\lambda$$ is a bias–variance dial. Subtracting the style part gives up
whatever information it carries, which is the bias. In exchange the forecast's
cross-sectional variance falls by about $$\lambda(2-\lambda)$$ times the style
share, up to a covariance term with the sector part: 22% of the total at 25%
removal and 38% at 50%, with a style share of 50%. What I can measure is the
mean and the dispersion of the daily IC, not the training-sample variance in
Numerai's study, so I use the framing to organize the trade-off and do not claim
a measured decomposition.

## Light removal helps and heavy removal gives it back

Removal takes factor variance out of the book first. From no removal to 100%,
the book's factor variance falls from 24 to 7 %² a year, while the non-factor
variance falls from 55 to 46, and realized volatility falls from 8.9% to 7.3%
(Figure 3).

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/variance-split" mobile="/assets/ridge-style-removal/variance-split_mobile" alt="Realized variance of the book by share of style removed, split into factor and non-factor parts: factor variance falls from 24 to 7 and non-factor variance from 55 to 46." version="1" %}
</div>
<p class="figure-caption"><strong>Figure 3: Most of the variance that removal takes out is factor variance.</strong> Annualized variance of the book's daily gross return in %², split by a time-series regression on same-day market, sector and style factor returns, 1999–April 2026. Blue is factor variance and grey the rest; the label above each bar is realized net volatility.</p>

Table 2 reports the full history. Sharpe rises to 1.38 at 50% and 1.41 at 75%,
then falls back to 1.20 at 100%, where volatility is lowest but the return has
dropped to 8.7%. Only the 50% gain has an interval clear of zero, +0.19
[+0.02, +0.36]. The 25% gain of +0.07 [−0.01, +0.16] and the 75% gain of +0.22
[−0.06, +0.47] do not, and the 100% result is zero with an interval of ±0.4.

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 2: Removing style raises Sharpe at moderate strength and costs drawdown and turnover.</strong> Ridge forecast, 1999-01-26 to 2026-04-28, mean of three rebalance schedules, after 5 bp per dollar traded. Δ is the paired Sharpe difference against no removal with a block-bootstrap 95% interval; the last column gives it by schedule. Returns are geometric and annualized; turnover is two-way as a multiple of capital a year.</caption>
  <thead>
    <tr><th>Removal</th><th>Net Sharpe</th><th>Δ [95%]</th><th>Return</th><th>Vol.</th><th>Max DD</th><th>Turnover</th><th>Δ by schedule</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">None</th><td>1.20</td><td>—</td><td>10.6%</td><td>8.89%</td><td>−19.9%</td><td>24.7x</td><td>—</td></tr>
    <tr><th scope="row">Style 25%</th><td>1.27</td><td>+0.07 [−0.01, +0.16]</td><td>11.1%</td><td>8.70%</td><td>−20.9%</td><td>25.7x</td><td>+0.04 / +0.04 / +0.14</td></tr>
    <tr><th scope="row">Style 50%</th><td>1.38</td><td>+0.19 [+0.02, +0.36]</td><td>11.6%</td><td>8.36%</td><td>−18.5%</td><td>27.2x</td><td>+0.13 / +0.11 / +0.32</td></tr>
    <tr><th scope="row">Style 75%</th><td>1.41</td><td>+0.22 [−0.06, +0.47]</td><td>11.0%</td><td>7.76%</td><td>−16.4%</td><td>28.9x</td><td>+0.18 / +0.15 / +0.32</td></tr>
    <tr><th scope="row">Style 100%</th><td>1.20</td><td>0.00 [−0.39, +0.40]</td><td>8.7%</td><td>7.30%</td><td>−16.5%</td><td>30.2x</td><td>+0.03 / −0.19 / +0.15</td></tr>
    <tr><th scope="row">PCA, 10 factors, 25%</th><td>1.19</td><td>−0.01 [−0.08, +0.07]</td><td>10.3%</td><td>8.67%</td><td>−23.3%</td><td>25.6x</td><td></td></tr>
    <tr><th scope="row">PCA, 10 factors, 50%</th><td>1.23</td><td>+0.04 [−0.12, +0.19]</td><td>10.3%</td><td>8.38%</td><td>−21.5%</td><td>26.4x</td><td></td></tr>
  </tbody>
</table>

The table also shows what the Sharpe ratio hides. At 25% the maximum drawdown
is worse than with no removal (−20.9% against −19.9%). Turnover rises with every
step, from 24.7x to 30.2x, so part of what is saved in risk is spent on
costs. From 50% to 75% the return falls from 11.6% to 11.0% while volatility
keeps falling, so a good share of the Sharpe improvement at 75% is a lower
denominator.

Holdings-based attribution, the same exposure-times-payoff split as in the
attribution articles, shows where the return comes from. Each additional 25
points of removal changes the book's style return by −0.55, −1.02, −1.56 and
−2.28 points a year, and its stock-specific return by +0.97, +1.63, +1.17 and
+0.41. The first two steps pay: the style return given up is smaller than the
stock-specific return that gets through. By the third step the style return
given up is larger, and the book's style exposures cross zero somewhere
between 50% and 75% removal. At 100% they overshoot to the opposite sign, which
replaces one set of style bets with another.

The signal level shows the same trade. At 25% the mean daily IC barely moves,
from 0.0468 to 0.0463, while its standard deviation falls from 0.0958 to 0.0899,
so the information ratio of the IC (ICIR) rises from 0.489 to 0.515. The ICIR
keeps rising with strength (0.546 at 50%, 0.594 at 100%) while the mean IC falls,
so a steadier signal is not the same thing as a more profitable one: at 100% the
ICIR is highest and the Sharpe ratio no better than doing nothing.

## The gain belongs to the early history

Table 2 averages two different regimes. Figure 4 splits the Sharpe ratio at
2019: before it, every strength up to 100% beats no removal, with the peak at
75% (1.73 against 1.34). From 2019 onward the ordering reverses, and the loss
grows with strength, down to 0.39 at 100% against 0.93 with no removal.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/strength-curve" mobile="/assets/ridge-style-removal/strength-curve_mobile" alt="Net Sharpe ratio by share of style removed, 1999–2018 rising to a peak at 75% and 2019–2026 falling with strength; PCA points sit below the style line before 2019 and above it after." version="1" %}
</div>
<p class="figure-caption"><strong>Figure 4: The best strength depends on the period.</strong> Net Sharpe ratio by share of style removed, mean of three schedules, split at 2019. Diamonds are the PCA variants at 25% and 50%, with the same split.</p>

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 3: Removal up to 75% helps in every subperiod before 2019 and hurts from 2019.</strong> Difference in net Sharpe ratio against no removal by subperiod, mean of three schedules.</caption>
  <thead>
    <tr><th>Removal</th><th>1999–2003</th><th>2004–2008</th><th>2009–2013</th><th>2014–2018</th><th>2019–2026</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Style 25%</th><td>+0.13</td><td>+0.16</td><td>+0.08</td><td>+0.11</td><td>−0.02</td></tr>
    <tr><th scope="row">Style 50%</th><td>+0.23</td><td>+0.23</td><td>+0.50</td><td>+0.35</td><td>−0.11</td></tr>
    <tr><th scope="row">Style 75%</th><td>+0.35</td><td>+0.26</td><td>+0.49</td><td>+0.47</td><td>−0.18</td></tr>
    <tr><th scope="row">Style 100%</th><td>+0.38</td><td>−0.03</td><td>+0.34</td><td>+0.16</td><td>−0.54</td></tr>
  </tbody>
</table>

The change is in the stock-specific return. Style 50% earns 1.93 points a year
more than no removal before 2019 and 1.72 points a year less afterwards, and
almost all of that swing is stock-specific return rather than style return. In
the recent bull market the style component of the forecast carried
stock-specific return that the adjusted scores no longer hold, which is what the
third assumption in Table 1 failing would look like. The attribution describes
the books and does not prove the mechanism: in the LightGBM books, the sign of
such stock-specific return differences changed when trailing instead of
full-sample betas were used.

One result does not fit that story neatly. A plain score-weighted portfolio of
the forecast, with no optimizer and a 15-session hold, improves at every
strength up to 100% in both periods; its Sharpe ratio goes from 0.22 to 0.63
across 2019–2026. That resembles the signal-level gains in the MSCI and Numerai
studies. The fade appears only once the adjusted scores are turned into 75 long
and 75 short names and sized by the optimizer, and I have not separated which of
those two steps produces it.

<div class="research-figure responsive-figure">
  {% include blog-chart.html chart="gap" source="/assets/ridge-style-removal/cumulative-gap.json?v=1" base="/assets/ridge-style-removal/cumulative-gap" mobile="/assets/ridge-style-removal/cumulative-gap_mobile" version="1" label="Cumulative net return of style 25% and style 50% against no removal, 1999 to April 2026, with 2019 onward shaded." %}
</div>
<p class="figure-caption"><strong>Figure 5: Most of the accumulated gain was in by 2019, and part of it was given back.</strong> Cumulative daily net return difference against no removal, mean of three schedules, in points of capital. Shaded: 2019 onward.</p>

Figure 5 makes the cost of choosing a strength concrete. A 50% removal was ahead
by about 40 points of capital at the end of 2018 and by about 25 at the end of
the sample. The 25% removal peaks lower, at about 14 points, and gives back
less. It is also the only strength whose 2019–2026 shortfall is as small as two
hundredths of a Sharpe point.

## Statistical factors are a weaker substitute

Named styles require choosing a factor model, and a reasonable objection is
that the statistical alternative makes no such choice. I replaced the styles
with the first 10 principal components of the trailing 252 days of stock
returns, refit every 21 days, and removed 25% and 50% of their fitted part
the same way.

The result is a weaker version of the same thing (Table 2). The PCA variants
lower volatility by about as much, but they do not shorten the drawdowns
(−23.3% and −21.5% against −19.9%), and the Sharpe differences of −0.01
[−0.08, +0.07] and +0.04 [−0.12, +0.19] both have intervals that include zero.
Against the style variant at the same strength, PCA is behind by 0.08
[−0.17, −0.003] at 25% and by 0.15 [−0.31, +0.004] at 50%.

Almost all of that gap is before 2019, where PCA at 50% gains nothing (0.00)
against style 50%'s +0.33 average. The optimizer's covariance is already
estimated from the same statistical co-movement, even at half its strength after
shrinkage, so removing it from the forecast frees little that the optimizer was
not already pricing. After 2019 PCA is ahead: +0.09 against no removal where
style 50% is at −0.11, a lead of 0.20 (Figure 4). Statistical removal does less
good before 2019 and less harm after it. It agrees with the named-style result on
volatility and not on Sharpe, so I treat it as a partial cross-check and not as a
replacement.

## Controls on the finished portfolio do not recover the gain

The same exposure can be limited later. Two of those later controls lose to
removing it from the forecast.

**Overlays on the finished book.** Limiting the book's style beta after the
fact, even without costs, is behind 25% forecast removal: a 75% style-beta limit
against style 25% is −0.13 [−0.24, −0.04]. The two act at different points:
removal changes which names are chosen, the overlay only how much of them is held.

**Hard caps inside the optimizer.** With style bounds set to 75% of the
unadjusted book's typical tilt, the optimizer had a feasible solution on
2009-04-24 only for the empty book. The 75 long and 75 short names are chosen
from the forecast before the optimizer weights them, so if the forecast picks
names that share a style, no weighting satisfies the cap.

What forecast removal does is change the held book's tilts directly. Averaged
over time, the mean absolute tilt on the optimizer's rank scale falls from 0.40
to 0.35 and 0.28 for momentum, from 0.27 to 0.23 and 0.16 for size, and from
0.26 to 0.21 and 0.14 for residual volatility, as removal goes from none to 25%
and 50%.

## Light removal is a low-regret default, not a measured optimum

For a style-heavy linear forecast I would remove a quarter of the style part and
stop there. At 25% the Sharpe ratio improves in every one of the first four
subperiods, the 2019–2026 shortfall is 0.02 and the extra turnover is one turn
(25.7x against 24.7x). The costs are a maximum drawdown that is a point worse
and a full-history gain whose interval includes zero. It is also the steadiest
setting partly by construction: it is the smallest change, so its paired
difference from no removal has the least room to swing.

Stronger removal buys more Sharpe, but it is an early-history result. The 50%
gain is significant on its own and I still discount it, for two reasons. I
compared 15–19 variants on this one history, so a significant interval on the
best of them overstates what to expect. And the gain reverses after 2019 for
the same reason it appeared before: the removed style component paid in some
regimes and not in others, and no rule in this study can tell me which regime
comes next. I do not read the peak at 75% as an optimum. Full removal, the first
rule in the book and in Numerai's scoring, adds no Sharpe at all here: at 100%
it is 1.20, the same as no removal.

Two limits come with that choice. The results describe a risk model that
shrinks correlations; a model that priced style risk directly could close part
of the gap that removal closes here. And the direction, not the size, is what
carries over: the LightGBM forecast on the same data points the same way, with a
lower best strength because only 28% of its variance is style. The more of a
forecast is style, the more there is to remove and the more of it was earning.

## References

Giuseppe A. Paleologo, *Advanced Portfolio Management: A Quant's Guide for
Fundamental Investors*, Wiley, 2021, Chapters 6 and 8.

bobyfisch,
[*An introduction to feature neutralization / exposure*](https://forum.numer.ai/t/an-introduction-to-feature-neutralization-exposure/4955),
Numerai Forum, 15 February 2022.

by256,
[*Feature Neutralization Increases Bias and Reduces Variance*](https://forum.numer.ai/t/feature-neutralization-increases-bias-and-reduces-variance/7486),
Numerai Forum, 4 June 2024.

Numerai,
[*Feature Neutral Correlation (FNC)*](https://docs.numer.ai/numerai-tournament/scoring/feature-neutral-correlation),
Numerai Docs.

Mark Horvath, Dominik Zvara and Mihaly Berndt,
[*Constructing Portfolios from Published Equity Research*](https://www.msci.com/research-and-insights/blog-post/constructing-portfolios-from-published-equity-research),
MSCI Research, 7 October 2026.

[^book]: Paleologo (2021), Chapter 6, Procedure 6.3; Chapter 8 uses the same factor decomposition to separate style from idiosyncratic P&L.
[^numerai]: Numerai's scoring documentation defines feature-neutral correlation with full removal; the forum posts describe a tunable proportion.
[^msci]: Mean post-publication information ratio across the signals in the MSCI study; the style-neutral version orthogonalizes eight style factors, with no strength given.
[^vt]: With each book scaled to a constant trailing realized volatility, the Sharpe ratios for none, 25% and 50% are 1.34, 1.47 and 1.69 before 2019 and 0.98, 0.95 and 0.81 from 2019.
