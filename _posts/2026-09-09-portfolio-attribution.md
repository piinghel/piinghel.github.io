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

The portfolio from my [optimizer
article](/quants/2026/08/29/portfolio-optimization.html) earned about 8.8% a
year after costs at 6.6% volatility from September 1998 to May 2026. A return
chart says how much it made. It doesn't say what for.

The ranking behind it combines the 80 predictors of the [regression
article](/quants/2025/02/09/multiple-linear-regression.html). So the question I
want to answer is which of the ranking's themes the portfolio is actually paid
for, which take risk without paying for it, and whether that has changed.

The book is the optimizer article's final portfolio, joint sizing with trading
controls, with its three rebalance schedules held together at equal notional.

<div id="pnl-conventions" markdown="1">
Capital is held fixed, and one **P&L point** is 1% of it. Trading costs are
5 basis points per dollar traded, excluding borrow, financing and market impact.
Annual figures average daily P&L points, so they sit slightly below the
compounded returns in the optimizer article. Theme returns are before costs and
start in January 1999; the book's costs were about 1.1 points a year.
</div>

## The longs carry the book
{: #the-book }

The longs made **372 points**, the shorts lost **101** and trading costs took
**29.6**, leaving **242 points** net. Because the longs hold lower-beta stocks
than the shorts, keeping forecast beta near zero leaves the book about 24% net
long in dollars. The shorts lose money over the history even though they made
money in every market decline.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/whole-history" mobile="/assets/portfolio-attribution/whole-history_mobile" version="6" alt="Cumulative long, short and net P&L above the portfolio drawdown, September 1998–May 2026." %}
</div>
<p class="figure-caption"><strong>Figure 1: The longs carried the accumulated result.</strong> Cumulative P&amp;L and drawdown, in points; longs and shorts before costs, net after. Shading marks the two deepest drawdowns, February 2020–January 2021 and July 2008–September 2009.</p>

## Attributing P&L to the ranking's themes
{: #follow-exposure-and-payoff-together }

First, each characteristic is ranked across stocks every day, the ranks in a
theme group are averaged, and the average is standardized to mean zero and
unit standard deviation:

$$
\begin{aligned}
s_{ik,t}&=\frac{1}{|G_k|}\sum_{j\in G_k}\frac{\operatorname{rank}_t(x_{ij,t})}{N_t},\\
z_{ik,t}&=\frac{s_{ik,t}-\bar s_{k,t}}{\operatorname{sd}_t(s_k)}.
\end{aligned}
$$

Market beta is the exception and enters unranked. Next, each day's stock
returns are regressed on the previous day's loadings and industry indicators,
weighting each stock by the square root of its market capitalization:

$$
r_{i,t+1}=\sum_k z_{ik,t}\,f_{k,t+1}+g_{\operatorname{ind}(i),t+1}+\epsilon_{i,t+1}.
$$

The coefficients $$f_{k,t+1}$$ are the day's payoffs: what one unit of each
characteristic earned, holding the others fixed. The book's return then splits
exactly into exposure times payoff for each characteristic, the net long
dollars times the average industry return, the industry weights beyond that,
and a stock-specific remainder:[^model]

$$
\begin{aligned}
R_{t+1}={}&\sum_k\Big(\sum_i w_{i,t}z_{ik,t}\Big)f_{k,t+1}+n_t\,\bar g_{t+1}\\
&+\sum_g\big(W_{g,t}-n_t\pi_{g,t}\big)g_{g,t+1}\\
&+\sum_i w_{i,t}\hat\epsilon_{i,t+1}.
\end{aligned}
$$

Here $$w_{i,t}$$ are the signed weights, $$n_t$$ the net dollars, $$W_{g,t}$$
the book's weight in industry $$g$$ and $$\pi_{g,t}$$ that industry's share of
the stocks in the regression. A theme's P&L is the sum of its characteristics'
terms: what the book's exposure earned, whether the ranking chose the exposure
or the optimizer's limits created it, as with the net long dollars.

<div markdown="1">
<p class="table-caption"><strong>Table 1: The themes.</strong> The regression article's momentum &amp; trend theme is split into four; net market exposure and sector tilt are exposures the portfolio carries without the ranking aiming for them.</p>

| Theme | What it measures |
| :--- | :--- |
| Short interest | Short interest relative to volume, and its changes |
| Momentum | Returns and risk-adjusted returns over one to twelve months |
| Trend | Price relative to moving averages, and how long it has stayed above them |
| Short-term reversal | Returns over the last one to 21 sessions |
| Price position | Price relative to recent highs and lows |
| Loss frequency | The share of losing days over windows up to three years |
| Low volatility | Stock volatility |
| Net market exposure | Net dollars times the market's move |
| Size | Market capitalization, its variability and its change |
| Liquidity &amp; volume | Turnover, illiquidity and the behaviour of trading volume |
| Beta &amp; market correlation | Market beta and correlation with the index |
| Sector tilt | Industry exposure beyond the net dollars |
{: .research-table .comparison-table .compact-table }
</div>

A theme's **share of risk** is the covariance of its daily P&L with the book's,
divided by the book's variance:

$$
\text{share}_T=\frac{\operatorname{Cov}(C_{T},R)}{\operatorname{Var}(R)}.
$$

Because the themes add up to the book, the shares add to 100%; a theme that
offsets the rest of the book gets a negative one, and a theme pays its way when
its share of the return exceeds its share of risk.

I checked the method against known answers. On simulated returns built from
known payoffs and this book's actual weights, it recovers each theme's P&L
without bias; random long–short books get theme returns near zero; and a
cap-weighted market portfolio lands 99% of its variance on net market
exposure.

## Short interest pays most reliably
{: #where-the-return-comes-from }

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/theme-pnl" mobile="/assets/portfolio-attribution/theme-pnl_mobile" version="3" alt="Return and share of risk of each theme, 1999–May 2026, grouped into signal themes, the defensive package and the rest." %}
</div>
<p class="figure-caption"><strong>Figure 2: Short interest is the most reliable earner.</strong> Return before costs, % of capital a year, and share of the book's daily variance, January 1999–May 2026. Rows group the signal themes, the defensive package and the rest.</p>

The steadiest earner is **short interest**: 2.2% a year, 23% of the book's 9.7%
gross return on 9% of the risk, and positive in every block. **Net market
exposure** earns more, 3.2% a year, mostly the market's return on the net long
dollars the beta limit forces on the book. Low volatility adds 1.7%,
stock-specific returns 1.3%, and price position, reversal, loss frequency,
liquidity and momentum 0.7–1.4% each.

Momentum, trend and price position are built from the same price paths, so
their loadings overlap heavily and offset each other: trend shows −2.1% a year
and price position +1.4%, but the three together earned about nothing. I read
them as one price-path signal rather than three. **Size** lost 1.9% a year on
18% of the risk, but almost all of that came in 1999–2003; since 2014 it has
been close to flat.

## The defensive package stopped paying
{: #how-it-changed }

Low volatility and the net long dollars are one position seen twice: the beta
limit adds net long dollars because the longs are low-beta, so the two offset
each other. Size and liquidity overlap in the same way. I read the four
together as the **defensive package**.

<div markdown="1">
<p class="table-caption"><strong>Table 2: The defensive package stopped paying after 2021.</strong> Return before costs, % of capital a year, and share of the book's daily variance, %. Blocks are five years to 2018, then 2019–21 and 2022–May 2026.</p>

| Block | Book | Package | Package risk | Low volatility | Low vol. risk |
| :--- | ---: | ---: | ---: | ---: | ---: |
| 1999–2003 | 11.1 | 3.4 | 42 | 4.4 | −2 |
| 2004–08 | 8.6 | 4.2 | 26 | 1.4 | 0 |
| 2009–13 | 9.0 | 4.8 | 37 | 2.5 | 19 |
| 2014–18 | 11.5 | 4.3 | 34 | 2.7 | 9 |
| 2019–21 | 11.0 | 8.4 | 49 | 2.0 | 27 |
| 2022–May 2026 | 7.2 | −0.2 | 44 | −3.5 | 30 |
{: .research-table .comparison-table .compact-table }
</div>

The package paid in every block to 2021, best in 2019–21, while its share of
risk rose to 49%. How much of the early return it gets depends on how market
beta is measured; the change after 2021 does not. Since 2022 it has earned −0.2% a year,
with a standard error of about 3 points, on 44% of the risk; low volatility
alone lost 3.5% a year on 30%. Figures 3 and 4 show every theme year by year.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/theme-return-years" mobile="/assets/portfolio-attribution/theme-return-years_mobile" version="2" alt="Each theme's return per year, 1999–2026, with block averages." %}
</div>
<p class="figure-caption"><strong>Figure 3: Short interest paid in every block.</strong> Return before costs, % of capital a year, per calendar year; lines are block averages. 2026 is January–May, annualized. Bars beyond ±10 are clipped and marked.</p>

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/portfolio-attribution/theme-risk-years" mobile="/assets/portfolio-attribution/theme-risk-years_mobile" version="2" alt="Each theme's share of the book's risk per year, 1999–2026, with block averages." %}
</div>
<p class="figure-caption"><strong>Figure 4: Low volatility's share of risk tripled after 2018, while stock-specific risk shrank.</strong> Share of the book's daily variance, %, per calendar year; lines are block averages. Bars beyond ±40 are clipped and marked.</p>

Stock-specific returns faded too, from positive in every block to 2018 to
−1.2% in 2019–21 and about zero since, and their share of risk fell from
about 19% to 8%. Short interest held up, with its best block since 2022 at 3.2%
a year, and momentum and loss frequency earned 2.2–2.3%, two to three times
their long-run average.

## What I'd change

Over 27 years the book is paid for short interest, the smaller signal themes
and, until 2019, stock selection; the price-path themes together earned about
nothing. The problem is the defensive package, which paid in every block to
2021 and has since carried 44% of the risk for nothing. Four years is a short
record after its best block, but I would change the ranking's mix first: a
low-volatility tilt sized for what it earns now.

## References

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
2021, Chapters 3–4 and 7–8.

[^model]: Weighted by the square root of market capitalization, with 20 industries. Holdings without theme data, about 1% of gross, are shown separately.
