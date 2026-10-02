---
layout: post
interactive_charts: true
title: "Performance Attribution, Part 1: What the Portfolio Is Paid For"
description: "How stock characteristics and market exposure contribute to the portfolio's return and risk, and how that has changed since 1999."
permalink: /quants/portfolio-attribution.html
toc: true
date: 2026-09-09
last_modified_at: 2026-10-03
categories: ["Risk & attribution"]
article_label: Performance attribution · Part 1 of 2
series_id: performance-attribution
series_order: 1
---

<link rel="stylesheet" href="/assets/css/attribution-article.css?v=5">

The portfolio in [From Volatility Scaling to Joint
Sizing](/quants/2026/08/29/portfolio-optimization.html) compounded at about
8.9% a year after costs from September 1998 to May 2026, with 6.6% volatility,
a Sharpe ratio of 1.32 and two-way turnover of about 21 times capital a year.
A return chart says how much it made. It doesn't say what for. After
short-term reversal, the largest fitted contribution here is the combined
low-risk position: low volatility, beta and net market exposure together
earned 2.6% a year before costs. Its
net long dollars matter to that result, even with a tight forecast-beta limit.

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
P&L, because only averages add up across themes: an annual figure is the mean
daily P&L times 252. On that basis the book averages 8.8% a year after costs
(8.6% from January 1999, where the theme returns start), against 8.9% compounded.
Theme returns are before costs, 9.6% a year in total; costs took about 1.1
points a year. Sharpe ratios use a zero cash rate.
</div>

## The longs carry the book
{: #the-book }

From 23 September 1998, the longs made **372 points**, the shorts lost **101** and trading costs took
**29.6**, leaving **242 points** net. The shorts lose money over the history
even though they made money in each of the 15 declines of 15% or more since 1999
([Part 2](/quants/short-book-rebounds.html#market-regimes)).

<div class="research-figure responsive-figure">
  {% include blog-chart.html chart="performance" source="/assets/portfolio-attribution/performance.json" base="/assets/portfolio-attribution/whole-history" mobile="/assets/portfolio-attribution/whole-history_mobile" version="8" label="Cumulative long, short and net P&L above the portfolio drawdown, September 1998–May 2026." %}
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

about 0.65 × 0.26 ≈ 0.17 of capital. This rough calculation accounts for about
two thirds of the 25%. It does not identify the remaining eight points: the
forecast returns and joint constraints also affect the holdings. The 25% net
limit binds at 82% of rebalances. The book's
forecast beta stays close to zero, a median of +0.02, but its realized
beta has been +0.08.

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
$$n$$ its net dollars, $$f^{\text{mkt}}$$ the model's market return
and $$\tilde W_s$$ its weight in sector $$s$$ beyond the net dollars.

The characteristics are built from the same 80 predictors as the ranking.
This is not a decomposition of the Ridge model's 80 coefficients.
**Short-term return** captures the book's reversal position, and **medium- and
long-term return** groups momentum and slower trend. The
[definitions](#factor-definitions) below list what each factor contains;
stock-specific P&L is the model's remainder.

I use their raw values, logged where they are skewed, clipped at four standard
deviations and standardized with a cap-weighted mean, rather than ranks. Ranks
squeeze the tails, where many of the shorts sit: the most volatile 5% of
stocks sit about 2.7 standard deviations from the mean, but only 1.6 when
ranked. Predictors that measure the same thing, such as the last week's return
and the price against its 10-day average, are averaged into one characteristic
before the regression. Estimated separately, they collide, and the regression
hands them large payoffs of opposite sign. The fitted characteristics below
are single factors; trading activity groups three of them. Net market exposure
and sector tilt come from the sector coefficients. The predictors sit in the
same seven themes as in the regression article; here volatility is signed
toward stable stocks as low volatility, and beta adds an estimated beta to
market correlation.

The two return themes are split by where a predictor's information sits, not
by its window: a predictor is short-term when more than half of its variation
across stocks comes from the last month's returns. Price against its 63-day
average therefore counts as short-term; the 10/21-session MACD, on the
boundary, does not.

<div markdown="1">
<p class="table-caption"><strong>Table 1: The attribution components.</strong> Characteristics are built from the ranking's predictors as listed; trading activity groups three factors. Net market exposure and sector tilt come from the net dollars and the sector weights.</p>

| Theme | What it measures |
| :--- | :--- |
| Short interest | Short interest relative to volume, its change, and the variability of that ratio, which mostly tracks volume |
| Short-term return | Returns over one day to one month, price against its 10-, 21- and 63-day averages, Bollinger position and recent lows, the share of losing days over a month |
| Medium- and long-term return | Returns and risk-adjusted returns over three to twelve months, slower trend, distance from 52-week highs and lows, earlier run-ups, change in market value, losing-day frequency over three months to three years |
| Size | Market value, and the illiquidity and volume variability that come with it |
| Trading activity | Turnover, volume surges and the correlation of daily returns with changes in turnover, each its own factor |
| Low volatility | Stock volatility, and the variability of market value |
| Beta | Market beta and correlation with the index |
| Net market exposure | Net dollars times the market's return |
| Sector tilt | Sector weights beyond the net dollars |
{: .research-table .settings-table .compact-table }
</div>

<details markdown="1" id="factor-definitions">
<summary>What goes into each factor</summary>

The attribution uses **the 80 ranking predictors plus a separately estimated
beta**. Related predictors are first combined into 25 groups, which together
with the estimated beta form nine fitted style factors. Standardized predictors
receive equal weight within a group; standardized groups receive equal weight
within their factor, with the signs described below. The resulting factors are
standardized again. A group with more predictors does not get more weight.
These weights describe the attribution model, not the Ridge ranking weights.
All lookbacks below are trading sessions, and characteristics precede the
return being attributed.

<details markdown="1">
<summary>Low volatility.</summary>

One group combines volatility over 10 and 252 sessions, upside volatility over
10, 21 and 63, downside volatility over 10, 21, 63 and 126, and relative average
true range over 5, 21 and 126 sessions: the high–low and previous-close ranges
expressed as ratios rather than price points. A second measures the variability
of log market value over 21, 126, 252 and 504 sessions. Both are signed so a higher factor loading
means a more stable stock. This is an individual-stock characteristic, distinct
from the market-volatility states in Part 2.

</details>

<details markdown="1">
<summary>Beta.</summary>

Two groups: the estimated stock beta, and stock–market correlations
over 252 and 504 sessions. Beta uses 756-session correlation, with
at least 252 observations, multiplied by the ratio of 21-session stock and
index volatilities, so across stocks it partly measures 21-session volatility,
which low volatility also contains. The two groups agree only weakly (median
correlation 0.22), and the payoffs of beta and low volatility correlate at
−0.31. That is one reason I read them together in the low-risk package. A higher loading means greater market sensitivity.

</details>

<details markdown="1">
<summary>Size.</summary>

Three groups: log market value; 21-session illiquidity, with its sign
reversed; and variability of log trading volume over 63, 126 and
504 sessions, also reversed. A higher loading describes larger, more liquid
stocks with more stable volume. Variability of market value belongs to low
volatility above; changes in market value belong to medium- and long-term
return below.

</details>

<details markdown="1">
<summary>Short interest.</summary>

Three groups: the current log ratio of short interest to
trading volume and its 63- and 252-session averages; changes over 21, 63, 126
and 252 sessions; and variability over 63 and 252 sessions. Short interest is
reported only about twice a month, so its variability relative to daily volume
mostly tracks the variability of volume. A higher loading
means more, rising or more variable short interest. It is a stock
characteristic, not the portfolio's short weight or a measure of borrow cost.

</details>

<details markdown="1">
<summary>Short-term return.</summary>

Six groups: 5-session return; 10- and 21-session
returns; the previous day's return; price relative to 10-, 21- and 63-session
moving averages; position within Bollinger bands over 5, 10, 21 and 126
sessions and relative to lows over 5, 10, 21 and 63 sessions; and the fraction
of losing days over 21 sessions, with its sign reversed.
A higher loading means a stronger recent price move. This portfolio's negative
exposure makes it a reversal position; the factor itself is signed toward
recent winners.

</details>

<details markdown="1">
<summary>Medium- and long-term return.</summary>

Seven groups cover returns over 90 and 252 sessions; returns
scaled by volatility over 63 and 126 sessions; slow trend measures (price
against its 252-session average, moving-average differences and trend
persistence); position relative to 252-session highs and lows;
earlier run-ups and distance from their highs over 90–252 sessions, excluding
the most recent 10 or 21 sessions; changes in log market value over 126 and 504
sessions and its position relative to past extrema; and losing-day frequency
over 63, 252 and 756 sessions, reversed. A higher loading means a stronger longer-term price trend.

</details>

<details markdown="1">
<summary>Trading activity contains three separate factors.</summary>

Turnover is the
63-session turnover-level measure. Volume surge is log volume relative to its
past maximum over 126 and 252 sessions. The factor labelled price–volume
correlation is the correlation of daily returns with changes in turnover over
21, 63 and 126 sessions. It rises with recent returns, but its daily
payoff is nearly uncorrelated with that of short-term return (−0.04).
Each enters the regression separately; their P&L is added for the displayed
trading-activity subtotal.

</details>

<details markdown="1">
<summary>The other lines.</summary>

Net market exposure and sector tilt come from the sector
part of the regression, not predictor composites. Stock-specific is the
remaining P&L of holdings with characteristics, and unloaded holdings is the
P&L of positions outside that coverage. The low-risk package adds low
volatility, beta and net market exposure; it introduces no extra predictor.

</details>

</details>

I read **low volatility, beta and net market exposure together**, as the
**low-risk package**. These are three components of the same portfolio
position: lower-risk longs, higher-risk shorts and the net long dollars that
partly offset their market exposure. The package is their sum, not another
factor. Its breakdown helps explain when the position wins or loses.

This follows the sizing logic in the [low-volatility
article](/quant/2024/12/15/low-volatility-factor.html), but measures its
contribution inside this multifactor book. The low-volatility factor here is a
conditional attribution component, not the return of that article's decile
portfolio.

A theme's **share of risk** is the covariance of its daily P&L with the book's,
divided by the book's variance:

$$
\text{share}_T=\frac{\operatorname{Cov}(C_{T},R)}{\operatorname{Var}(R)}.
$$

The non-overlapping components add to 100% of the gross book's variance;
subtotals are not added again. A negative share means that component's P&L
covaries negatively with the book. Comparing return and risk shares describes
the existing holdings; it does not establish what changing them would earn.

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
about 1% of gross, shown as its own line. Characteristics are measured at the
previous market close.

**Characteristics.** Each raw predictor is logged if it is a skewed level or
dispersion, or turned into $$\log(1+r)$$ if it is a return. Each day it is
clipped at the median ± 5 × 1.4826 × the median absolute deviation, then
standardized as $$z=(x-\bar x^{\text{cap}})/\sigma^{\text{EW}}$$, with a
cap-weighted mean, so the market portfolio has approximately zero exposure, and an
equal-weighted standard deviation, so a few mega-caps don't set the scale. The
result is clipped at ±4, standardized once more, and clipped again. Predictors
are combined into groups, then factors, with standardization at each level as
defined above. The estimated-beta input uses the optimizer's estimator;
the fitted beta factor combines it with the market-correlation group.

**Regression.** Weighted least squares with weights $$\sqrt{\text{market cap}}$$
and eleven sector indicators, so the sector coefficients absorb the market. The
market's return $$f^{\text{mkt}}$$ is the cap-weighted average of the sector
coefficients, and the sector tilt is what the sector weights earn beyond it.
Across 250 sample dates, no characteristic's variance inflation factor exceeds
3.4.

**Timing.** A theme's P&L over $$T$$ days splits into average exposure times
cumulative payoff plus timing:
$$\sum_t E_tf_t=\bar E\,\Phi_T+T\operatorname{Cov}(E_t,f_t)$$, with
$$\Phi_T=\sum_tf_t$$.

**Betas.** The slope of an OLS regression is linear in the dependent variable,
so the book's beta to the market is the sum of the themes' betas,
$$\beta_R=\sum_T\operatorname{Cov}(C_T,R^{\text{mkt}})/\operatorname{Var}(R^{\text{mkt}})$$.

</details>

## Low risk, short interest and short-term reversal pay
{: #where-the-return-comes-from }

{% include blog-chart.html chart="themes" source="/assets/portfolio-attribution/interactive-themes.json" base="/assets/portfolio-attribution/theme-pnl" mobile="/assets/portfolio-attribution/theme-pnl_mobile" label="Return and share of risk by theme" version="6" %}
<p class="figure-caption"><strong>Figure 2: What the book is paid for, in any period.</strong> Average P&amp;L, % of capital a year, and share of the gross book's daily variance, for the selected dates; January 1999–May 2026 by default. Returns are before costs, with costs shown separately. Low-risk package and trading activity are subtotals; the control reveals their components. Each subtotal replaces its components when adding up returns or risk shares. Leg shares use the whole book's variance.</p>

Over the whole period the book averaged 9.6% a year before costs. Four sources
carried it:

- **The low-risk package**, 2.6% a year on 30% of the risk. Low volatility,
  beta and net market exposure are read together: separately they mostly show
  the market's move offsetting across lines, low volatility losing when the
  market rises and the net long dollars gaining. Together, about 1.8 points a
  year of that return is not explained by the market, with a standard error of
  about 0.8.
- **Short-term return**, 3.4% a year on 8% of the risk. The book is short
  recent winners, so this is a reversal bet, and I call it short-term reversal
  below.
- **Short interest**, 1.4% a year on 5% of the risk.
- **Stock-specific returns**, 1.5% a year on 31% of the risk, a Sharpe
  ratio of 0.37 on its own.

The low-risk package supplied 27% of the return and 30% of the variance.
The short-interest and stock-specific figures, like all theme P&L here, exclude
borrow fees; they are not estimates of what remains after obtaining the shorts.
For scale, at short notional of 65% of capital, annual borrow fees of 1%, 3%
or 5% of borrowed notional would take 0.65, 1.95 or 3.25 P&L points a year.
These are cost sensitivities, not observed fee estimates; the actual cost
depends on which names were available and their fees through time.

Medium- and long-term return, which holds momentum and slower trend, earned
1.1% a year on 16% of the risk, about two standard errors from zero. Size and trading activity earned
close to nothing and took little risk. Over the attribution period, the themes'
betas add up to the book's beta of +0.08. The low-risk package accounts for
slightly more than all of it, at +0.09: +0.23 from the net long dollars, −0.12
from low volatility and −0.02 from beta; stock-specific returns take off about
0.03.

## The book earns less from reversal
{: #how-it-changed }

<div class="research-figure responsive-figure">
  {% include blog-chart.html chart="years" source="/assets/portfolio-attribution/interactive-themes.json" base="/assets/portfolio-attribution/theme-return-years" mobile="/assets/portfolio-attribution/theme-return-years_mobile" version="6" label="Non-overlapping theme groups' returns per year, 1999–2026, with block averages." %}
</div>
<p class="figure-caption"><strong>Figure 3: Short interest contributed in every block; reversal's contribution fell.</strong> Return before costs, % of capital a year, per calendar year; lines are block averages. 2026 is January–May, annualized. Bars beyond ±10 are clipped and marked.</p>

Short-term reversal made 8.1% a year in 1999–2003 and 0.3% since 2022
(0.8% from 2023). This was a long decline, alongside a smaller position:
average exposure fell from −0.36 in 2014–18 to −0.21 since 2022. The lower
contribution reflects changes in exposure, realized payoffs and their timing;
it does not by itself identify a better ranking weight.
Short interest was positive in
every block, from 0.9% to 2.0% a year. Stock-specific returns earned 2.3% a year
from 2022 to 2025 and then lost about 8 points in the first five months of 2026,
while medium- and long-term return gained; the two moved against each other day to day,
which suggests an exposure the themes don't capture.

<p class="table-caption"><strong>Table 2: What each theme earned, and the risk it took, in each period.</strong> Average return before costs and each theme’s share of the gross book’s daily variance. The low-risk package is the sum of low volatility, beta and net market exposure, rounded on its own; the themes add up to the book and the risk shares to 100, up to rounding. The standard error allows for autocorrelation up to 21 sessions. Periods are five years to 2018, then 2019–21 and 2022–May 2026.</p>

<div class="research-table-scroll">
  <table class="research-table comparison-table theme-periods">
    <thead><tr><td></td><th scope="col">1999–03</th><th scope="col">2004–08</th><th scope="col">2009–13</th><th scope="col">2014–18</th><th scope="col">2019–21</th><th scope="col">2022–26</th></tr></thead>
    <tbody>
      <tr class="section"><th scope="rowgroup" colspan="7">Return before costs, % of capital a year</th></tr>
      <tr><th scope="row">Short interest</th><td>1.6</td><td>1.4</td><td>0.9</td><td>1.2</td><td>0.9</td><td>2.0</td></tr>
      <tr><th scope="row">Short-term return</th><td>8.1</td><td>4.3</td><td>2.8</td><td>2.1</td><td>1.5</td><td>0.3</td></tr>
      <tr><th scope="row">Medium- and long-term return</th><td>1.1</td><td>0.4</td><td>0.1</td><td>1.6</td><td>0.9</td><td>2.9</td></tr>
      <tr><th scope="row">Size</th><td>−1.0</td><td>−0.5</td><td>−0.6</td><td>0.0</td><td>0.7</td><td>0.4</td></tr>
      <tr><th scope="row">Trading activity</th><td>−0.2</td><td>−0.3</td><td>−0.2</td><td>0.0</td><td>0.0</td><td>0.1</td></tr>
      <tr class="package"><th scope="row">Low-risk package</th><td>3.4</td><td>1.7</td><td>2.6</td><td>3.9</td><td>3.6</td><td>0.9</td></tr>
      <tr class="part"><th scope="row">Low volatility</th><td>2.2</td><td>1.5</td><td>−1.8</td><td>2.6</td><td>−1.8</td><td>−2.0</td></tr>
      <tr class="part"><th scope="row">Beta</th><td>0.6</td><td>0.3</td><td>−0.4</td><td>−0.4</td><td>0.3</td><td>−0.7</td></tr>
      <tr class="part"><th scope="row">Net market exposure</th><td>0.5</td><td>−0.1</td><td>4.7</td><td>1.7</td><td>5.0</td><td>3.5</td></tr>
      <tr class="se"><th scope="row">Package standard error</th><td>2.6</td><td>1.3</td><td>1.5</td><td>1.4</td><td>3.5</td><td>2.0</td></tr>
      <tr><th scope="row">Sector tilt</th><td>−1.2</td><td>−0.7</td><td>−0.1</td><td>−0.1</td><td>1.0</td><td>0.5</td></tr>
      <tr><th scope="row">Stock-specific</th><td>−1.7</td><td>2.3</td><td>3.3</td><td>2.8</td><td>2.2</td><td>0.3</td></tr>
      <tr><th scope="row">Unloaded holdings</th><td>0.6</td><td>0.0</td><td>0.1</td><td>0.0</td><td>0.1</td><td>−0.2</td></tr>
      <tr class="total"><th scope="row">Book</th><td>10.7</td><td>8.6</td><td>9.0</td><td>11.5</td><td>11.0</td><td>7.2</td></tr>
    </tbody>
    <tbody>
      <tr class="section"><th scope="rowgroup" colspan="7">Share of the book’s risk, %</th></tr>
      <tr><th scope="row">Short interest</th><td>5</td><td>7</td><td>5</td><td>5</td><td>4</td><td>6</td></tr>
      <tr><th scope="row">Short-term return</th><td>6</td><td>16</td><td>6</td><td>6</td><td>11</td><td>4</td></tr>
      <tr><th scope="row">Medium- and long-term return</th><td>10</td><td>1</td><td>8</td><td>20</td><td>23</td><td>26</td></tr>
      <tr><th scope="row">Size</th><td>3</td><td>0</td><td>1</td><td>1</td><td>0</td><td>0</td></tr>
      <tr><th scope="row">Trading activity</th><td>5</td><td>5</td><td>3</td><td>3</td><td>3</td><td>5</td></tr>
      <tr class="package"><th scope="row">Low-risk package</th><td>34</td><td>23</td><td>28</td><td>24</td><td>38</td><td>32</td></tr>
      <tr class="part"><th scope="row">Low volatility</th><td>7</td><td>−2</td><td>19</td><td>12</td><td>17</td><td>27</td></tr>
      <tr class="part"><th scope="row">Beta</th><td>0</td><td>0</td><td>4</td><td>1</td><td>3</td><td>2</td></tr>
      <tr class="part"><th scope="row">Net market exposure</th><td>26</td><td>25</td><td>6</td><td>11</td><td>18</td><td>3</td></tr>
      <tr><th scope="row">Sector tilt</th><td>9</td><td>6</td><td>5</td><td>7</td><td>1</td><td>5</td></tr>
      <tr><th scope="row">Stock-specific</th><td>29</td><td>43</td><td>45</td><td>33</td><td>20</td><td>22</td></tr>
      <tr><th scope="row">Unloaded holdings</th><td>0</td><td>−1</td><td>0</td><td>1</td><td>0</td><td>1</td></tr>
    </tbody>
  </table>
</div>

The package paid between 1.7% and 3.9% a year in every block to 2021, on roughly
a quarter to two fifths of the risk. Since 2022 it has earned 0.9% a year, more
than all of it in 2022; since 2023 it has lost about 3.4 points. The standard
error of the return since 2022 is 2.0 percentage points a year, too large to
establish deterioration. The estimate also depends on the regression weights:
with equal weights the package earns 1.4% a year since 2022, with market-cap
weights −1.1%. Its parts move much more than the package: low
volatility lost money in three of the six blocks, while the net long dollars
made up the difference.

The risk moved elsewhere too. Medium- and long-term return's share of the
risk rose from 1% in 2004–08 to 26% since 2022, while the stock-specific share
fell from 45% in 2009–13 to 20% in 2019–21 and 22% since 2022. Short interest
earned in every period on 4% to 7% of the risk.

## What the attribution supports

Over 27 years, the low-risk position, short interest and short-term reversal
account for most of the fitted contribution. The stock-specific remainder
also contributes, but can contain exposures the model misses. I judge the
low-risk position as a whole: its three components explain how it behaves,
and they are not three separate sources of return.

Reversal's contribution has fallen alongside the book's exposure to it. That makes it a
candidate for a controlled comparison, not evidence that reducing its ranking
weight would improve the portfolio. The low-risk package's recent return is
too uncertain to establish deterioration. The attribution shows where to look
in the ranking, and each change needs its own controlled test.

## References

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
2021, Chapters 3–4 and 7–8.

Giuseppe Paleologo, *The Elements of Quantitative Investing*, 2025, the chapters
on fundamental factor models and performance attribution.
