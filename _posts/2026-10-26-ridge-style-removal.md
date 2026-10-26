---
layout: post
interactive_charts: true
title: "Removing Style Bets from a Ridge Forecast"
description: "Half of the Ridge forecast is style. Removing part of it before the portfolio is built lowers risk and helps on the early history; the gain disappears after 2019, and statistical factors do not make a better substitute."
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
and moves the book towards stock-specific bets that earn more, and it gives up a
component that was paid. Over the full history light-to-moderate removal raises
the Sharpe ratio, but the gain is an early-history result: from 2019 the point
estimates turn negative at every strength, mostly in 2021 and 2024–2026, and no
later difference is distinguishable from zero. A statistical alternative
(principal components) is weaker, and a portfolio-level limit I tried was behind
forecast removal.

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
forecast volatility target and its position, sector and beta limits. It keeps the
1.18 volatility multiplier of the rebalancing article, so it takes more risk than
the book in the attribution articles. Book results are means of three rebalance
schedules a week apart, as in
[Reducing Rebalancing Luck]({% link _posts/2026-09-05-rebalancing-luck.md %}),
after costs of 5 bp per dollar traded, from 26 January 1999 to 28 April 2026.
Turnover is two-way: purchases plus sales, as a multiple of capital per year.
Intervals are paired 120-session block-bootstrap 95% intervals against no
removal. Forecast-level statistics (variance shares, IC, stand-alone Sharpe) are
daily, gross and use all stocks.

## Half of the forecast is style

On each date I split the forecast's cross-sectional variance into a sector part,
a style part (beta, residual volatility, momentum, size, liquidity and
short-term reversal) and a stock-specific remainder. Style carries 50% of the
variance on average and 58% after 2019 (Figure 2).

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/forecast-style-share" mobile="/assets/ridge-style-removal/forecast-style-share_mobile" alt="Stacked shares of the Ridge forecast's cross-sectional variance by year: style between 40% and 65%, stock-specific most of the rest." version="1" %}
</div>
<p class="figure-caption"><strong>Figure 2: Style is half of the Ridge forecast and a larger share since 2019.</strong> Share of each year's cross-sectional forecast variance explained by the six style exposures (blue), left to the stock-specific remainder (grey), or assigned to sectors and cross terms (light grey, top). Sector dummies and styles are fitted jointly with square-root-of-market-cap weights.</p>

## The style part is less consistent in the forecast and pays more in the book

At the forecast level the style part looks like the weaker half. Its rank
correlation with subsequent returns (the IC) is 0.034, the same as the
stock-specific part's, but the information ratio of the daily IC is 0.31 against
0.60. As stand-alone gross portfolios of all stocks, the style part earns a
Sharpe ratio of 0.07 and the stock-specific part 1.09.

Inside the optimized book the picture reverses. In the unadjusted book the style
P&L earns a Sharpe ratio of 0.93 on 6.9% volatility, against 0.49 for the
stock-specific P&L, and supplies 56% of the return for 49% of the variance. So
the argument that removal drops the half that earns least per unit of risk does
not describe this book.

The ranking also changes over time. Before 2019 the style P&L earned a Sharpe
ratio of 1.15 against 0.63 for the stock-specific P&L; since 2019 it is 0.57
against 0.10. The stock-specific part stopped paying: its IC fell from 0.037 to
0.027 while the style part's rose from 0.028 to 0.048, and the ICIR gap narrowed
from 0.32 against 0.71 to 0.32 against 0.40. The lower consistency of style is a
fact about the years before 2019.

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
Most of the excess over the 49 %² budget is factor variance, 24 of the 30, which
is what shrunk correlations would leave out. That is consistent with the
discount and does not prove it, since the split depends on how factors are
measured: a holdings-based split puts factor variance at 33.

Second, a multiplier cannot change the mix. The common risk that shrinkage
discounts is the same common risk a style bet carries, so style positions in the
forecast get through the optimizer at a discount compared with stock-specific
ones. That is the channel through which removal could help, and it is specific to
this covariance model. A model with explicit style factors, or less
shrinkage, would price the bets directly and might capture part of the gain
below. I have not tested one, so the results describe this risk model.

## Removal works through the names it selects, not by scaling style down

The attribution articles write the book's return as exposure times payoff. For
returns $$R_i=x_i'f+e_i$$, with style exposures $$x_i$$, factor returns $$f$$ and
stock-specific returns $$e_i$$, the book's return and variance split as

$$
w'R=(X'w)'f+w'e,\qquad
\operatorname{Var}=(X'w)'\Sigma_f(X'w)+\sum_i w_i^2\sigma_i^2 .
$$

The weights come from a forecast $$y_i=x_i'b+r_i$$ with a style part and a
remainder, so the book's style exposure $$X'w$$ is inherited from the forecast's
style loadings $$b$$. Style variance is common to every position and does not
fall as names are added; stock-specific variance does. At a fixed risk budget,
each unit of variance spent on style is unavailable for stock-specific bets.

If removal only scaled the style part by $$a=1-\lambda$$ in a linear portfolio,
with $$S$$ the style return and $$P$$ the whole book, then
$$d\ln\mathrm{SR}/da=\mu_S/\mu_P-\operatorname{Cov}(S,P)/\operatorname{Var}(P)$$,
and a small removal would raise the Sharpe ratio if and only if

$$
\underbrace{\frac{\mu_S}{\mu_P}}_{\text{return share of style}}\;<\;\underbrace{\frac{\operatorname{Cov}(S,P)}{\operatorname{Var}(P)}}_{\text{risk share of style}}.
$$

In the unadjusted book that is false: style earns 56% of the return for 49% of
the variance over the full history, and 58% for 42% before 2019, where removal
helped most. Plain scaling would have lowered the Sharpe ratio.

What removal does instead is change the stocks. The unadjusted book's stocks
carrying the 50%-removal book's style exposures earn a Sharpe ratio of 1.19,
no better than the unadjusted book's 1.20, while the 50% book earns 1.38. The 50%
book keeps about two thirds of the unadjusted book's weight, so about a third of
it is different. The gain comes from which stocks carry the exposure, and more of
the return comes from stock-specific bets. Table 2 lists what that explanation
needs and where each part is tested.

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 2: The explanation needs three things, and each has a test.</strong> What must be true for removal to help and the evidence in the sections below.</caption>
  <thead><tr><th>Requirement</th><th>If it fails</th><th>Where it is tested</th></tr></thead>
  <tbody>
    <tr><th scope="row">Removal changes which names are held, and the added names earn more stock-specific return</th><td>Removal only rescales the style bet, which lowers Sharpe in this book</td><td>Synthetic book above; return change by removal step</td></tr>
    <tr><th scope="row">Style bets get through the optimizer at a discount</th><td>Little is left to remove</td><td>Risk-model section; PCA variant; portfolio-level controls</td></tr>
    <tr><th scope="row">The stock-specific part keeps paying</th><td>The reallocation earns less and removal costs return</td><td>Split at 2019; Table 4, Figures 4 and 5</td></tr>
  </tbody>
</table>

The strengths below are judged on the same history that sets how much each part
paid, so I read them as a trade-off and not as an optimum.

## Removal takes out a share of the fitted style part

Each date I regress the forecast on sector dummies and the six style exposures,
subtract a share $$\lambda$$ of the fitted style part, keep the sector part and
leave the remainder as it is:

$$
y'_i=y_i-\lambda\sum_{k\in\text{styles}}\hat\beta_k\,x_{ik}.
$$

The adjusted scores then go through selection and the optimizer exactly as
before; I don't re-rank. This removes the style part from the forecast, after
prediction; removing it from the training target is a different intervention.
The Numerai and Paleologo rule is $$\lambda=1$$. I run
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
(Figure 3). A holdings-based split gives 33 to 8 for factor variance and a flat
46 for the rest.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/variance-split" mobile="/assets/ridge-style-removal/variance-split_mobile" alt="Realized variance of the book by share of style removed, split into factor and non-factor parts: factor variance falls from 24 to 7 and non-factor variance from 55 to 46." version="1" %}
</div>
<p class="figure-caption"><strong>Figure 3: Most of the variance that removal takes out is factor variance.</strong> Annualized variance of the book's daily gross return in %², split by a time-series regression on same-day market, sector and style factor returns, 1999–April 2026. Blue is factor variance and grey the rest; the label above each bar is realized net volatility.</p>

Table 3 reports the full history. Sharpe rises to 1.38 at 50% and 1.41 at 75%,
then falls back to 1.20 at 100%, where volatility is lowest but the return has
dropped to 8.8%. Only the 50% gain has an interval clear of zero, +0.19
[+0.02, +0.36], and it is the best of the strengths and PCA variants compared;
adjusting for those with a max-t bootstrap gives a p-value of about 0.05–0.1,
depending on which variants count. The 25% gain of +0.07 [−0.01, +0.16] and the 75% gain of +0.22
[−0.06, +0.47] do not, and the 100% result is zero with an interval of ±0.4.

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 3: Removing style raises Sharpe at moderate strength and costs turnover.</strong> Ridge forecast, 1999-01-26 to 2026-04-28, mean of three rebalance schedules, after 5 bp per dollar traded. Δ is the paired Sharpe difference against no removal with a block-bootstrap 95% interval; the last column gives it by schedule. Return is the geometric annual return, volatility is annualized and maximum drawdown is compounded; turnover is two-way as a multiple of capital a year.</caption>
  <thead>
    <tr><th>Removal</th><th>Net Sharpe</th><th>Δ [95%]</th><th>Return</th><th>Vol.</th><th>Max DD</th><th>Turnover</th><th>Δ by schedule</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">None</th><td>1.20</td><td>—</td><td>10.8%</td><td>8.89%</td><td>−18.7%</td><td>24.7x</td><td>—</td></tr>
    <tr><th scope="row">Style 25%</th><td>1.27</td><td>+0.07 [−0.01, +0.16]</td><td>11.3%</td><td>8.70%</td><td>−19.5%</td><td>25.7x</td><td>+0.04 / +0.04 / +0.14</td></tr>
    <tr><th scope="row">Style 50%</th><td>1.38</td><td>+0.19 [+0.02, +0.36]</td><td>11.9%</td><td>8.36%</td><td>−17.5%</td><td>27.2x</td><td>+0.13 / +0.11 / +0.32</td></tr>
    <tr><th scope="row">Style 75%</th><td>1.41</td><td>+0.22 [−0.06, +0.47]</td><td>11.2%</td><td>7.76%</td><td>−15.6%</td><td>28.9x</td><td>+0.18 / +0.15 / +0.32</td></tr>
    <tr><th scope="row">Style 100%</th><td>1.20</td><td>0.00 [−0.39, +0.40]</td><td>8.8%</td><td>7.29%</td><td>−15.5%</td><td>30.2x</td><td>+0.03 / −0.19 / +0.15</td></tr>
    <tr><th scope="row">PCA, 10 factors, 25%</th><td>1.19</td><td>−0.01 [−0.08, +0.07]</td><td>10.4%</td><td>8.67%</td><td>−21.5%</td><td>25.6x</td><td>+0.03 / −0.04 / −0.01</td></tr>
    <tr><th scope="row">PCA, 10 factors, 50%</th><td>1.23</td><td>+0.04 [−0.12, +0.19]</td><td>10.5%</td><td>8.38%</td><td>−19.9%</td><td>26.4x</td><td>+0.03 / −0.01 / +0.08</td></tr>
  </tbody>
</table>

The table also shows what the Sharpe ratio hides. At 25% the maximum drawdown
is worse than with no removal (−19.5% against −18.7%); it improves from 50%.
Turnover rises with every
step, from 24.7x to 30.2x, so part of what is saved in risk is spent on
costs. From 50% to 75% the return falls from 11.9% to 11.2% while volatility
keeps falling, so a good share of the Sharpe improvement at 75% is a lower
denominator.

The gains are not even across schedules. The baseline's third schedule is its
weakest (Sharpe 1.10 against 1.23 and 1.26) and carries the largest gain, +0.32
at 50% against +0.13 and +0.11, so without it the 50% gain is about +0.12.

Holdings-based attribution, the same exposure-times-payoff split as in the
attribution articles, shows where the return comes from. Each additional 25
points of removal changes the book's gross style return by −0.55, −1.02, −1.56
and −2.28 points a year, and its stock-specific return by +0.97, +1.63, +1.17
and +0.41. The first two steps pay: the style return given up is smaller than
the stock-specific return that gets through. By the third step the style return
given up is larger. The book's mean exposure to size changes sign between 50%
and 75% removal, and to momentum, residual volatility and beta between 75% and
100%; reversal and liquidity never change sign. At 100% the book has
replaced some style bets with opposite ones.

The signal level shows the same trade. At 25% the mean daily IC barely moves,
from 0.0468 to 0.0463, while its standard deviation falls from 0.0958 to 0.0899,
so the information ratio of the IC (ICIR) rises from 0.49 to 0.52. The ICIR
keeps rising with strength (0.55 at 50%, 0.59 at 100%) while the mean IC falls,
so a steadier signal is not the same thing as a more profitable one: at 100% the
ICIR is highest and the Sharpe ratio no better than doing nothing.

## The gain belongs to the early history

Table 3 averages two periods. Figure 4 splits the Sharpe ratio at 2019, a date I
chose after seeing the weak recent years. Before it, every strength up to 75% has
an interval clear of zero: +0.12 [+0.02, +0.23] at 25%, +0.32 [+0.13, +0.53] at
50% and +0.39 [+0.09, +0.72] at 75%. From 2019 the point estimates are negative,
−0.02, −0.11, −0.18 and −0.54 at 100%, and none is distinguishable from zero. The
change from the early period is clear at 50% (−0.43 [−0.78, −0.15]) and 75%
(−0.57 [−1.18, −0.06]) and not at 25% (−0.14 [−0.33, +0.01]).

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/ridge-style-removal/delta-sharpe" mobile="/assets/ridge-style-removal/delta-sharpe_mobile" alt="Net Sharpe difference against no removal by strength with 95% intervals: clearly positive for 25 to 75 percent before 2019, and intervals spanning zero with negative point estimates from 2019." version="1" %}
</div>
<p class="figure-caption"><strong>Figure 4: Before 2019 the gain is clear for 25–75%; from 2019 no difference is.</strong> Net Sharpe difference against no removal, mean of three schedules, with paired 120-session block-bootstrap 95% intervals. Diamonds are the PCA variants at 25% and 50%.</p>

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 4: Removal up to 75% helps in every subperiod before 2019 and is lower from 2019.</strong> Difference in net Sharpe ratio against no removal by subperiod, mean of three schedules.</caption>
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

The shortfall is concentrated. For 50%, the annual return difference is positive
in 16 of 20 years before 2019 and in 3 of 8 since, with the losses in 2021, 2024
and 2025. The years 2019–2023 are about flat at 25–75% (+0.02, −0.04, +0.01
in Sharpe) and the loss is in 2024–2026 (−0.11, −0.28, −0.63). The split date
matters too: with a split at 2016 the later period is slightly positive for
25–75%, and it turns negative only for splits from 2017.

The book-level numbers say why. Since 2019 the unadjusted book's stock-specific
P&L has earned 0.55 points a year, against 3.46 before, while its style P&L has
kept paying. Removal moves risk towards the part that stopped paying, which is the
third requirement in Table 2 failing. Style 50% earns about 1.9 points a year more
than no removal before 2019 and 1.7 less afterwards, almost all of it
stock-specific return. The attribution describes the books and does not prove the
mechanism.

One result does not fit that story neatly. A plain score-weighted portfolio of
the forecast, with no optimizer and a 15-session hold, improves at every
strength up to 100% in both periods; its Sharpe ratio goes from 0.22 to 0.63
across 2019–2026. That resembles the signal-level gains in the MSCI and Numerai
studies. The fade appears only once the adjusted scores are turned into 75 long
and 75 short names and sized by the optimizer, and I have not separated which of
those two steps produces it.

<div class="research-figure responsive-figure">
  {% include blog-chart.html chart="gap" source="/assets/ridge-style-removal/cumulative-gap.json?v=2" base="/assets/ridge-style-removal/cumulative-gap" mobile="/assets/ridge-style-removal/cumulative-gap_mobile" version="2" label="Cumulative net return of style 25%, 50% and 75% against no removal, 1999 to April 2026, with 2019 onward shaded." %}
</div>
<p class="figure-caption"><strong>Figure 5: Most of the accumulated gain was in by 2019, and part of it was given back.</strong> Cumulative daily net return difference against no removal, mean of three schedules, in points of capital. Shaded: 2019 onward.</p>

Figure 5 shows what the choice of strength cost. A 50% removal was ahead by about
38 points of capital at the end of 2018, peaked near 40 in February 2019 and ends
the sample at 25. The 25% removal was ahead by 14 at the end of 2018, peaked at 16
in February 2020 and ends at 11; the 75% removal peaked at 37 in June 2011 and
ends at 9. By hit rate no strength is more consistent: 25% gains in 17 of 28
calendar years, 50% in 19 and 75% in 15. What differs is the shape of the regret.
25% earns 37% of the 50% gain before 2019 and takes 16% of its loss since.

## Statistical factors are a weaker substitute

Named styles require choosing a factor model, and a reasonable objection is
that the statistical alternative makes no such choice. I replaced the styles
with the first 10 principal components of the trailing 252 days of stock
returns, refit every 21 days, and removed 25% and 50% of their fitted part
the same way. The components only start in early 2002, so before then the PCA
books equal no removal, and equal $$\lambda$$ removes different amounts of
forecast variance, so the comparison is between settings and not between matched
removals.

The result is a weaker version of the same thing (Table 3). The PCA variants
lower volatility by about as much, but they do not shorten the drawdowns
(−21.5% and −19.9% against −18.7%), and the Sharpe differences of −0.01
[−0.08, +0.07] and +0.04 [−0.12, +0.19] both have intervals that include zero.
Against the style variant at the same strength, PCA is behind by 0.08
[−0.17, −0.003] at 25% and by 0.15 [−0.31, +0.004] at 50%.

Almost all of that gap is before 2019, where PCA at 50% gains nothing (0.00)
against style 50%'s +0.32. A plausible reason is that the covariance is already
estimated from the same statistical co-movement, but PCA lowers realized
volatility as much as style removal does (8.67% and 8.38% against 8.70% and
8.36%), which suggests the optimizer does not fully price those components either,
so I leave the reason open. After 2019 PCA is ahead of style 50%: +0.09
[−0.19, +0.43] against no removal, where style 50% is at −0.11, a lead of 0.20
that is a point comparison (Figure 4). Statistical removal agrees with the
named-style result on volatility and not on Sharpe, so I treat it as a partial
cross-check and not as a replacement.

## Portfolio-level controls did not recover the gain

The same exposure can be limited later, and the two controls I tried lost to
removing it from the forecast.

**Overlay on the finished book.** A portfolio-level style-beta limit, even
without costs, was behind 25% forecast removal: a 75% limit against style 25% is
−0.13 [−0.24, −0.04]. It is one of several overlay variants and is exploratory,
and it is volatility-targeted, so it is not on the same basis as Table 3. The two
act at different points: removal changes which names are chosen, the overlay only
how much of them is held.

**Hard caps inside the optimizer.** With style bounds set to 75% of the
unadjusted book's typical tilt, the optimizer had a feasible solution on
2009-04-24 only for the empty book, so I could not compare it. The 75 long and 75
short names are chosen from the forecast before the optimizer weights them, so if
the forecast picks names that share a style, no weighting satisfies the cap.
Softer designs, such as a penalty, are untested.

What forecast removal does is change the held book's tilts directly. Averaged
over time, the mean absolute tilt on the optimizer's rank scale falls from 0.40
to 0.35 and 0.28 for momentum, from 0.27 to 0.23 and 0.16 for size, and from
0.26 to 0.21 and 0.14 for residual volatility, as removal goes from none to 25%
and 50%.

## Light removal costs little, and the case for more is early history

If I removed anything from a style-heavy linear forecast it would be a quarter of
the style part, and no removal is also defensible. At 25% the Sharpe gain is +0.07
with an interval that includes zero, the maximum drawdown is 0.8 points worse and
turnover rises by one turn (25.7x against 24.7x). It is the least regret: it earns
about a third of the 50% gain before 2019 and takes about a sixth of its loss
since. It is also the steadiest setting partly by construction, being the smallest
change, so its paired difference has the least room to swing.

Stronger removal buys more Sharpe, but it is an early-history result. The 50%
gain has an interval clear of zero on its own, and it is the best of the strengths
and PCA variants compared, so adjusting for them leaves a p-value of about
0.05–0.1. It also reverses: the change from before 2019 is clear at 50% and 75%,
the losses sit mostly in 2021 and 2024–2026, and nothing in this study says which
regime comes next. I do not read the peak at 75% as an optimum. Full removal, the
first rule in the book and in Numerai's scoring, adds no Sharpe at all here: at
100% it is 1.20, the same as no removal.

Three limits come with that choice. The results describe a risk model that
shrinks correlations and a 1.18 volatility multiplier; I have not repeated them at
the 1.55 calibration of the joint-sizing article, and a model that priced style
risk directly could close part of the gap that removal closes here. The strengths
and the 2019 split were chosen on the same history. And the right strength
depends on the forecast: the more of it is style, the more there is to remove and
the more of it was earning.

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
[^vt]: With each book scaled to constant trailing realized volatility, the Sharpe ordering of none, 25% and 50% is unchanged in both periods (1.34, 1.47 and 1.69 before 2019).
