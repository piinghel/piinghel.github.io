---
layout: post
title: "Performance Attribution, Part 1: What the Portfolio Is Paid For"
description: "Which of the ranking's themes earn their share of the portfolio's risk, and how that has changed since 1999."
permalink: /quants/portfolio-attribution.html
toc: true
date: 2026-09-09
last_modified_at: 2026-09-28
categories: ["Risk & attribution"]
article_label: Performance attribution · Part 1 of 2
series_id: performance-attribution
series_order: 1
---

<link rel="stylesheet" href="/assets/css/attribution-article.css?v=3">

The portfolio from my [optimizer
article](/quants/2026/08/29/portfolio-optimization.html) compounded at about
9.0% a year after costs from September 1998 to May 2026, with 6.6% volatility,
a Sharpe ratio of 1.32 and two-way turnover of about 21 times capital a year.
A return chart says how much it made. It doesn't say what for.

The ranking behind it combines the 80 predictors of the [regression
article](/quants/2025/02/09/multiple-linear-regression.html). So the question I
want to answer is which of the ranking's themes the portfolio is actually paid
for, which take risk without paying for it, and whether that has changed.

The book is the optimizer article's final portfolio, joint sizing with trading
controls, with its three rebalance schedules held together at equal notional.

<div id="pnl-conventions" markdown="1">
Capital is held fixed, and one **P&L point** is 1% of it. Trading costs are
5 basis points per dollar traded, excluding borrow, financing and market impact.
With fixed capital, P&L over any stretch of days is the plain sum of daily P&L,
so no linking across periods is needed. The attribution works with average daily
P&L, because only averages add up across themes: the same book averages 8.8% a
year after costs (8.6% from January 1999, where the theme returns start). Theme returns are
before costs and start in January 1999; costs took about 1.1 points a year.
</div>

## The longs carry the book
{: #the-book }

The longs made **372 points**, the shorts lost **101** and trading costs took
**29.6**, leaving **242 points** net. The shorts lose money over the history
even though they made money in each of the 15 declines of 15% or more since 1999
([Part 2](/quants/short-book-rebounds.html#market-regimes)).

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/whole-history" mobile="/assets/portfolio-attribution/whole-history_mobile" version="6" alt="Cumulative long, short and net P&L above the portfolio drawdown, September 1998–May 2026." %}
</div>
<p class="figure-caption"><strong>Figure 1: The longs carried the accumulated result.</strong> Cumulative P&amp;L and drawdown, in points; longs and shorts before costs, net after. Shading marks the two deepest drawdowns, February 2020–January 2021 and July 2008–September 2009.</p>

The book is also net long, by about 25% of capital, and most of that follows
from its tilt towards low-risk stocks. At the median, the longs have a forecast beta of
0.85 and the shorts 1.07. The optimizer keeps the book's forecast beta within
±0.05, so long dollars times their beta roughly equal short dollars times
theirs, $$L\beta_L = S\beta_S$$, which leaves the book net long by

$$
L-S = S\,(\beta_S/\beta_L-1),
$$

about 0.65 × 0.26 ≈ 0.17 of capital. That is two thirds of the 25%. The rest, I
think, comes from the 7% volatility target: low-risk longs use less of it per dollar
than the shorts, so the optimizer would hold even more of them, and its limit of
25% on net dollars binds at more than four in five rebalances. The book's
forecast beta stays close to zero, a median of +0.02, but its realized
beta has been +0.07.

## Attributing P&L to the ranking's themes
{: #follow-exposure-and-payoff-together }

To see what each part of the book is paid for, I split its daily P&L with a
cross-sectional factor model. Each day, stock returns are regressed on the
stocks' characteristics measured the evening before and on sector indicators,
weighting each stock by the square root of its market capitalization. The
coefficients are the day's payoffs: what one unit of each characteristic earned,
holding the others fixed. The book's return then splits exactly into its
exposure to each characteristic times that payoff, its net dollars times the
market's return, its sector weights beyond that, and a remainder specific to the
stocks it holds:

$$
R_t=\sum_k E_{k,t-1}\,f_{k,t}+n_{t-1}\,f^{\text{mkt}}_t+\sum_s \tilde W_{s,t-1}\,g_{s,t}+\sum_i w_{i,t-1}\,\epsilon_{i,t}.
$$

Here $$E_{k}=\sum_i w_i z_{ik}$$ is the book's exposure to characteristic $$k$$,
$$n$$ its net dollars, $$f^{\text{mkt}}$$ the return of the cap-weighted market
and $$\tilde W_s$$ its weight in sector $$s$$ beyond the net dollars.

The characteristics are the ranking's predictors, grouped by what they measure.
I use their raw values, logged where they are skewed, clipped at four standard
deviations and standardized with a cap-weighted mean, rather than ranks. Ranks
squeeze the tails, where many of the shorts sit: the most volatile 5% of
stocks sit about 2.7 standard deviations from the mean, but only 1.6 when
ranked. Predictors that measure the same thing, such as the last week's return
and the price against its 10-day average, are averaged into one characteristic
before the regression. Estimated separately, they collide, and the regression
hands them large payoffs of opposite sign. So each theme below is exactly one
factor, except trading activity, which shows three small ones together.

<div markdown="1">
<p class="table-caption"><strong>Table 1: The themes.</strong> Each theme is one characteristic built from the predictors listed; net market exposure and sector tilt come from the net dollars and the sector weights.</p>

| Theme | What it measures |
| :--- | :--- |
| Short interest | Short interest relative to volume, its change and its variability |
| Short-term return | Returns over one day to one month, price against 10- and 21-day averages and recent highs and lows, the share of losing days |
| Long-term return | Returns over one to twelve months, trend over three months to two years, price against 52-week highs and lows, change in market value |
| Size | Market value, and the illiquidity and volume variability that come with it |
| Trading activity | Turnover, volume surges and the correlation of price and volume, each its own factor |
| Low volatility | Stock volatility, and the variability of market value |
| Beta | Market beta and correlation with the index |
| Net market exposure | Net dollars times the market's return |
| Sector tilt | Sector weights beyond the net dollars |
{: .research-table .comparison-table .compact-table }
</div>

A theme's **share of risk** is the covariance of its daily P&L with the book's,
divided by the book's variance:

$$
\text{share}_T=\frac{\operatorname{Cov}(C_{T},R)}{\operatorname{Var}(R)}.
$$

The shares add to 100%; a theme that offsets the rest of the book gets a
negative one, and a theme pays its way when its share of the return exceeds its
share of risk.

<details markdown="1">
<summary>How I compute the attribution</summary>

**Daily identity.** For holdings $$H$$ with characteristics at the previous
close, signed weights $$w_{i,t-1}$$ (fraction of capital), long gross
$$L=\sum_{w>0}w$$, short gross $$S=-\sum_{w<0}w$$ and net $$n=L-S$$, the book's
net P&L on day $$t$$ is

$$
P_t=\sum_k E_{k,t-1}f_{k,t}+n_{t-1}f^{\text{mkt}}_t+\sum_s \tilde W_{s,t-1}g_{s,t}+\sum_{i\in H}w_{i,t-1}\epsilon_{i,t}+\sum_{i\notin H}w_{i,t-1}r_{i,t}-\kappa_t ,
$$

with $$\kappa_t=0.0005\sum_i|\Delta w_{i,t}|$$ the trading cost on the day's
traded notional; two-way turnover is $$\sum_i|\Delta w_{i,t}|$$ summed over a
year. The fifth term is the P&L of the few holdings without characteristics,
about 1% of gross, shown as its own line.

**Characteristics.** Each raw descriptor is logged if it is a skewed level or
dispersion, or turned into $$\log(1+r)$$ if it is a return. Each day it is
clipped at the median ± 5 × 1.4826 × the median absolute deviation, then
standardized as $$z=(x-\bar x^{\text{cap}})/\sigma^{\text{EW}}$$, with a
cap-weighted mean, so the market portfolio has zero exposure, and an
equal-weighted standard deviation, so a few mega-caps don't set the scale. The
result is clipped at ±4 and standardized once more. A theme's characteristic is
the mean of its signed descriptors, standardized the same way. Beta is the
optimizer's own: 756-day correlation with the Russell 1000 times the ratio of
21-day volatilities.

**Regression.** Weighted least squares with weights $$\sqrt{\text{market cap}}$$
and eleven sector indicators, so the sector coefficients absorb the market. The
market's return $$f^{\text{mkt}}$$ is the cap-weighted average of the sector
coefficients, and the sector tilt is what the sector weights earn beyond it.
Across 250 sample dates, no characteristic's variance inflation factor exceeds
3.3.

**Timing.** A theme's P&L over $$T$$ days splits into average exposure times
cumulative payoff plus timing:
$$\sum_t E_tf_t=\bar E\,\Phi_T+T\operatorname{Cov}(E_t,f_t)$$, with
$$\Phi_T=\sum_tf_t$$.

**Betas.** The slope of an OLS regression is linear in the dependent variable,
so the book's beta to the market is the sum of the themes' betas,
$$\beta_R=\sum_T\operatorname{Cov}(C_T,R^{\text{mkt}})/\operatorname{Var}(R^{\text{mkt}})$$.

</details>

I checked the method against known answers. On returns simulated from known
payoffs and this book's actual weights, it recovers each theme's P&L to within
about half a point a year; random long–short books with the same gross get
theme returns near zero; and a cap-weighted market portfolio lands all of its
return and risk on net market exposure.

## Low risk, short interest and short-term reversal pay
{: #where-the-return-comes-from }

{% include attribution-explorer.html %}
<p class="figure-caption"><strong>Figure 2: What the book is paid for, in any period.</strong> Return before costs, % of capital a year, and share of the book's daily variance, for the chosen months; January 1999–May 2026 by default. The themes add up to the book, or to the chosen leg; the low-risk package and trading activity are subtotals of the themes below them.</p>

Over the whole period the book earned 9.7% a year before costs. Four sources
carried it:

- **The low-risk package**, 3.1% a year on 32% of the risk. Low volatility,
  beta and net market exposure are read together: separately they mostly show
  the market's move offsetting across lines, low volatility losing when the
  market rises and the net long dollars gaining. Together, about 2 points a
  year of that return is not explained by the market, with a standard error of
  about 0.9. With the predictors kept as separate factors the package earns
  5–5.5% a year, so its level depends on the model.
- **Short-term return**, 2.7% a year on 7% of the risk. The book is short
  recent winners, so this is a reversal bet, and I call it short-term reversal
  below.
- **Short interest**, 1.6% a year on 6% of the risk.
- **Stock-specific returns**, 1.8% a year on a third of the risk, a Sharpe
  ratio of 0.44 on its own.

Long-term return, which holds momentum and trend, earned 0.7% a year on 10% of
the risk, about two standard errors from zero. Size and trading activity earned
nothing and took little risk. The themes' betas add up to the book's beta of
+0.07, and the low-risk package accounts for more than all of it, +0.08: +0.23
from the net long dollars, −0.13 from low volatility and −0.02 from beta;
stock-specific returns take off about 0.03.

## Short-term reversal stopped paying
{: #how-it-changed }

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/theme-return-years" mobile="/assets/portfolio-attribution/theme-return-years_mobile" version="3" alt="Each theme's return per year, 1999–2026, with block averages." %}
</div>
<p class="figure-caption"><strong>Figure 3: Short interest paid in every block; short-term reversal faded.</strong> Return before costs, % of capital a year, per calendar year; lines are block averages. 2026 is January–May, annualized. Bars beyond ±10 are clipped and marked.</p>

Short-term reversal made 6.1% a year in 1999–2003 and about nothing since 2022
(0.2%); the fall is more than five standard errors. Short interest was positive in
every block, from 1.2% to 2.3% a year. Stock-specific returns earned 2.5% a year
from 2022 to 2025 and then lost about 8 points in the first five months of 2026,
while long-term return gained; the two moved against each other day to day,
which suggests an exposure the themes don't capture.

<div markdown="1">
<p class="table-caption"><strong>Table 2: The low-risk package by block.</strong> Return before costs, % of capital a year, and share of the book's daily variance, %. Standard errors allow for autocorrelation up to 21 sessions. Blocks are five years to 2018, then 2019–21 and 2022–May 2026.</p>

| | 1999–03 | 2004–08 | 2009–13 | 2014–18 | 2019–21 | 2022–26 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Return, % a year** | | | | | | |
| Low volatility | 3.6 | 1.9 | −1.4 | 3.0 | −2.0 | −1.7 |
| Beta | 0.5 | 0.1 | −0.4 | −0.5 | 0.3 | −0.6 |
| Net market exposure | 0.8 | 0.0 | 4.8 | 1.7 | 5.0 | 3.5 |
| Low-risk package | 4.8 | 2.0 | 2.9 | 4.2 | 3.4 | 1.2 |
| Standard error | 2.7 | 1.3 | 1.6 | 1.5 | 3.8 | 2.1 |
| **Share of risk, %** | | | | | | |
| Low volatility | 8 | −2 | 21 | 14 | 20 | 30 |
| Beta | 1 | 1 | 4 | 2 | 4 | 2 |
| Net market exposure | 26 | 25 | 6 | 11 | 18 | 3 |
| Low-risk package | 35 | 24 | 31 | 26 | 41 | 35 |
| **Book return, % a year** | 11.1 | 8.6 | 9.0 | 11.5 | 11.0 | 7.2 |
{: .research-table .comparison-table .compact-table }
</div>

The package paid between 2% and 5% a year in every block to 2021, on a quarter
to two fifths of the risk. Since 2022 it has earned 1.2% a year, more than all of it
in 2022; since 2023 it has lost about 2 points. The uncertainty, about ±2% a year, is too wide to say
whether it has weakened, and so is the choice of regression weights: with equal
weights the package earns 2.0% a year since 2022, with market-cap weights −1.3%. Its parts move much more than the package: low
volatility lost money in three of the six blocks, while the net long dollars
made up the difference.

## What I'd change

Over 27 years the book is paid for its tilt to low-risk stocks, for short
interest and, until recently, for short-term reversal, plus stock selection that
the themes don't explain. Size, trading activity and the individual lines of the
low-risk package are not where the money is. The clearest change is short-term
reversal: it paid 6% a year early on and nothing since 2022, so I would give it
less weight in the ranking. The low-risk package is too uncertain over four years
to cut on this evidence, so it stays.

## References

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
2021, Chapters 3–4 and 7–8.

Giuseppe Paleologo, *The Elements of Quantitative Investing*, 2025, the chapters
on fundamental factor models and performance attribution.
