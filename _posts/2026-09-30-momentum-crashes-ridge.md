---
layout: post
interactive_charts: true
title: "Momentum Crashes in a Ridge Ranking"
description: "Why a linear ranking keeps its momentum bet when that bet is most dangerous, and three ways to take it out."
permalink: /quants/momentum-crashes-ridge.html
toc: true
date: 2026-09-30
categories: ["Portfolio construction"]
article_label: Portfolio construction · Momentum crashes
---


In [Part 2 of the attribution series](/quants/short-book-rebounds.html), the
Ridge book's two deepest drawdowns came mostly from its low-volatility tilt.
In March 2009 the high-volatility stocks it was short were also the past
losers, so that rebound was a momentum crash as well, and the Ridge ranking
carries a lot of momentum. Here I start from why momentum crashes happen, then
try three ways to take the exposure out of a linear ranking: adjust the scores
after prediction, let the model learn a state-dependent momentum weight, or
cap the momentum tilt in the optimizer.

The setup is the one from the [portfolio optimization
article](/quants/2026/08/29/portfolio-optimization.html): Russell 1000, the
Ridge-80 ranking, joint sizing at a 7% volatility budget with the trading
controls, 75 long and 75 short names, three rebalance schedules starting a
week apart, and 5 bp per dollar traded. Numbers cover September 1998 to
December 2021 and are means over the three schedules, with the lowest and
highest schedule in parentheses.

## Momentum crashes when the losers rebound

Momentum buys the stocks that rose most over the past year and sells those
that fell most. It earns a solid premium over long samples, but its worst
months cluster in one situation: the market has fallen for a long time and
then turns up. Daniel and Moskowitz find that 14 of the 15 worst US
winner-minus-loser (WML) months follow a negative two-year market return, and
that the losses come from the short leg: from March to May 2009 the market
rose 26% and the loser decile 163%.[^dm]

The mechanism is leverage. After a long decline the losers are the firms the
crisis hit hardest, and their equity behaves like an out-of-the-money call on
firm value: modest downside beta, huge upside beta. A book short those stocks
is short a call on the market. Barroso and Santa-Clara show a simple defence:
momentum's own recent volatility predicts its future volatility, and scaling
momentum down when that volatility is high removes most of the crash.

The Russell 1000 shows the same pattern. Figure 1 follows the momentum deciles
through the 2009 rebound: from 9 March to 29 May the losers rose 134% and the
long–short WML portfolio lost 57%.

<div class="research-figure">
  {% include blog-chart.html chart="crash" source="/assets/momentum-crashes/crash-2009.json" label="Growth of 12-1 momentum winners, losers and the long–short portfolio from 6 March to August 2009." %}
</div>

<p class="figure-caption"><strong>Figure 1: In 2009 the losers crashed up.</strong> Growth of equal-weight top-decile winners, bottom-decile losers and the long–short WML portfolio from the 6 March 2009 close, 12-1 momentum within the Russell 1000, formed at month ends. Shaded: 9 March to 29 May.</p>

## A linear ranking cannot make its momentum weight conditional

Ridge-80's momentum comes from about fifteen of its eighty predictors, trend
measures that together tilt the book toward past winners. Its tilt toward 12-1
momentum is about 0.33 in calm markets and 0.45 during the 2009 rebound.

A linear model gives each predictor one coefficient, fitted across all market
states, so the momentum weight averages a regime where momentum pays and one
where it crashes. The ranking keeps that average in exactly the state where it
is most wrong. On the 30 worst WML days the book loses 15.5 points of capital.

## Measuring momentum risk with the momentum portfolio itself

Following Barroso and Santa-Clara, I measure momentum risk with the WML
portfolio's own volatility. With $$\hat\sigma_t$$ its annualized volatility
over the last 126 sessions,

$$
g_t=\max\!\left(\frac{\hat\sigma_t}{\operatorname{median}_{s\le t}\hat\sigma_s},\,1\right),
\qquad s_t = 1-\frac{1}{g_t^2}.
$$

$$g_t$$ compares current momentum volatility with its own history.
$$s_t$$ is the share of momentum exposure a mean-variance investor would give
up if momentum's variance rose by a factor $$g_t^2$$ with its expected return
unchanged. That is variance scaling in the sense of Moreira and Muir; scaling
by volatility alone, $$1-1/g_t$$, removes less. The share uses only past
returns. It is near zero in about 40% of months, above 0.5 in about as many,
and reached 0.94 at the end of 2008.

## Three ways to take momentum out

**Score overlay.** On each date I regress the scores $$y_{i,t}$$ on the
sector-demeaned momentum rank $$m_{i,t}$$ across stocks and remove a share
$$s_t$$ of the fitted momentum component, only when the scores lean toward
winners:

$$
y'_{i,t}=y_{i,t}-s_t\,\max(\beta_t,0)\,\bigl(m_{i,t}-\bar m_t\bigr),
\qquad
\beta_t=\frac{\operatorname{cov}_i(y_{i,t},m_{i,t})}{\operatorname{var}_i(m_{i,t})}.
$$

**Learned interactions.** I refit Ridge with each trend predictor also
multiplied by a market-stress state, so the model can learn its own momentum
weight for turbulent markets. It learns to cut that weight, and already did so
before 2009 entered the training data.

**Optimizer cap.** I bound the book's gross-relative tilt toward momentum,
$$\bigl|\sum_i w_{i,t} m_{i,t} / \sum_i |w_{i,t}|\bigr| \le 0.45/g_t^2$$,
where 0.45 is the 90th percentile of the baseline's calm-market tilt. The
scores are unchanged; only the portfolio is constrained.

## The overlay improves return and risk together

Table 1: Ridge-80 by rule. Development period, net of 5 bp, mean of three
schedules (lowest–highest). Sharpe from daily net returns; geometric return;
compounded maximum drawdown. Crash days: P&L on the 30 worst WML days, points
of capital.

| Rule | Sharpe | Return | Volatility | Max drawdown | Crash days |
|---|---:|---:|---:|---:|---:|
| Baseline | 1.32 (1.26–1.36) | 9.4% | 7.0% | 15.5% | −15.5 |
| Constant shrink | 1.41 (1.34–1.45) | 9.8% | 6.8% | 13.4% | −11.1 |
| **Score overlay** | **1.54 (1.44–1.61)** | **10.6%** | **6.7%** | **11.9%** | **−1.9** |
| Learned interactions | 1.55 (1.48–1.61) | 11.5% | 7.2% | 13.3% | +2.6 |
| Optimizer cap | 1.47 (1.41–1.52) | 10.1% | 6.7% | 11.4% | −8.2 |

Table 1 shows that the overlay does what it was designed to do. On crash days
the book barely loses (1.9 points against 15.5), the maximum drawdown falls
from 15.5% to 11.9%, and Sharpe rises from 1.32 to 1.54, improving on every
schedule. In the 2009 rebound its momentum tilt is −0.12 instead of +0.45.
Turnover barely changes. Figure 2 shows the full development-period paths; under Explore you can change the window and add the other rules.

<div class="research-figure performance-figure responsive-figure">
  {% include blog-chart.html chart="performance" source="/assets/momentum-crashes/performance.json" label="Net growth and drawdown of the Ridge baseline and the score overlay, 1998–2021, with the other rules available under Explore." %}
</div>
<p class="figure-caption"><strong>Figure 2: Growth and drawdown, 1998–2021.</strong> Net growth index (log scale) and drawdown after 5 bp costs. Each path averages three separately compounded schedules, so its drawdowns are shallower than the per-schedule maxima in Table 1. The constant shrink, learned interactions and optimizer cap can be shown under Explore.</p>

Part of this is simply holding less momentum. The constant shrink removes the
overlay's average share, 0.35, on every date and gets 1.41; timing is worth
the other 0.13. Scaling down the whole book instead reaches only 1.37: the fix
works because it targets momentum.

## Timing pays in a few crashes

Figure 3 shows where the value comes from. The overlay adds 24 points over 23
years, and 2009 alone contributes 15 of them. Without 2009 and 2020 the Sharpe
gain is +0.07; leaving out any single year keeps it positive. That is what a
crash hedge should look like, but it also means the evidence rests on a
handful of episodes: the Sharpe gain has a block-bootstrap standard error of
about 0.10 per schedule, and the timing part about 0.08.

<div class="research-figure">
  {% include blog-chart.html chart="added" source="/assets/momentum-crashes/value-added.json" label="Cumulative value added against the Ridge baseline by the score overlay and a constant shrink, 1998–2021." %}
</div>

<p class="figure-caption"><strong>Figure 3: Value added against the baseline.</strong> Cumulative sum of daily net return differences, points of capital, mean of the three schedules. The constant shrink removes the overlay's average share on every date. Shaded: 2009 and 2020.</p>

A slow state also has a cost. The overlay gave up about 3.5 points in 2008,
cutting a momentum lean that was still earning. In 2020 momentum volatility
had been high since late 2019, so it cut the lean while the baseline book was
still making money (+5.3 points from the March low to 6 November), costing
about 1 point, then gained 3.5 points in the November vaccine rotation.

## The alternatives take other bets

The learned interactions match the overlay's Sharpe by a different route:
Ridge also raises its momentum weight in calm markets, so return, volatility
and drawdown are all higher, and the result depends on which state I give it.
The optimizer cap has the shallowest drawdown in Table 1 but the smaller Sharpe
gain, and adds nothing once the overlay is in place. Stacking the overlay on
the learned model reaches 1.67, but I picked that combination after seeing the
results, and it overshoots into a short-momentum bet in turbulent markets.
Among about 40 Ridge variants I tried, the best should reach about 1.52 by
selection alone; the overlay's 1.54 barely clears that, so its case rests on
having been fixed in advance.

## Remove momentum when momentum is volatile

I would keep the score overlay. It has no fitted parameter, it was fixed
before I saw its result, it can be applied to any ranking, and it improves
return and risk together: Sharpe from 1.32 to 1.54, maximum drawdown from
15.5% to 11.9%, and almost no loss when momentum crashes. Because most of the
timing gain comes from 2009 and 2020, I would expect a smaller gain in other
periods, nearer 0.1 to 0.15.

## References

Kent Daniel and Tobias J. Moskowitz,
[*Momentum Crashes*](https://doi.org/10.1016/j.jfineco.2015.12.002),
*Journal of Financial Economics* 122, 2016, 221–247.

Pedro Barroso and Pedro Santa-Clara,
[*Momentum Has Its Moments*](https://doi.org/10.1016/j.jfineco.2014.11.010),
*Journal of Financial Economics* 116, 2015, 111–120.

Alan Moreira and Tyler Muir,
[*Volatility-Managed Portfolios*](https://doi.org/10.1111/jofi.12513),
*Journal of Finance* 72, 2017, 1611–1644.

[^dm]: Daniel and Moskowitz (2016), Table 2 and Section 2.3; value-weighted CRSP deciles, 1927–2013.
