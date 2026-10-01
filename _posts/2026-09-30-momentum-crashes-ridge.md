---
layout: post
interactive_charts: true
title: "Managing Momentum Crashes: A Comparison of Different Approaches"
description: "Three ways to make a Ridge strategy's momentum exposure depend on market conditions: change the scores, let the regression learn, or cap the portfolio. Development results and the 2022–May 2026 test period."
permalink: /quants/momentum-crashes-ridge.html
toc: true
date: 2026-09-30
last_modified_at: 2026-10-01
categories: ["Portfolio construction"]
article_label: Portfolio construction · Momentum crashes
github_repositories:
  - label: Research materials
    url: https://github.com/piinghel/momentum-crash-study
---

In the previous articles I built a long-short Russell 1000 strategy: a
[Ridge regression on 80 predictors](/quants/2025/02/09/multiple-linear-regression.html)
ranks the stocks, and the
[joint optimizer with its trading controls](/quants/2026/08/29/portfolio-optimization.html)
sizes them, for a Sharpe ratio of 1.32 over 1998–2021. About fifteen of those
predictors are trend measures, so the book leans toward past winners. I measure
that lean as the book's momentum tilt: the position-weighted average of the
stocks' momentum ranks (from −1 to 1 within each sector) per unit of gross
exposure. It's about 0.33 in calm markets and 0.36 in volatile ones, so it
doesn't back off when momentum gets risky. I wanted to see what it costs when momentum
turns dangerous.

So I split the trading days by how volatile the momentum portfolio had been
going in, measured up to the previous day. Up to about twice its usual
volatility the strategy hardly notices, with a Sharpe ratio around 1.5–1.6.
Above that, which is a quarter of the days, the Sharpe drops to 0.69 and the
strategy earns about half its usual return (the grey bars in Figure 1).

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/momentum-crashes/sharpe-by-state" mobile="/assets/momentum-crashes/sharpe-by-state_mobile" alt="Net Sharpe ratio of the baseline and the score overlay by level of lagged momentum volatility: similar below twice normal volatility, much lower for the baseline above it." version="1" %}
</div>
<p class="figure-caption"><strong>Figure 1: The strategy earns much less once momentum has been volatile.</strong> Net Sharpe ratio by level of the momentum-risk state g: the 12-1 winner-minus-loser portfolio's volatility over the last 126 sessions relative to its expanding median, floored at one and known the day before. Sharpe is computed within each bucket for each of the three rebalance schedules, then averaged; September 1998–December 2021, net of 5 bp. Labels give the share of trading days. The blue bars are the score overlay described below.</p>

The strategy still makes money in that top bucket, and much of the gap comes
from 2009, when the book lost about 5 points of capital on those days; without
2009 the bucket's Sharpe is 0.93. Because the state only uses returns up to the previous
day, the figure shows what happened once momentum had visibly become risky,
which is information a fix can act on in time.

I tried three ways to take momentum out when it's risky, each at a different
point between the predictions and the portfolio. A score overlay removes part
of the scores' momentum lean after prediction. Learned interactions let the
regression set its own momentum weight for turbulent markets. An optimizer cap
limits the book's momentum tilt and leaves the scores alone. The overlay, in
blue in Figure 1, lifts the top bucket to 1.39 and changes little below it.
Table 1 sums up the trade-offs.

<table class="research-table settings-table approach-table">
  <caption><strong>Table 1: Three ways to take momentum out.</strong> Where each approach acts, and what it trades off.</caption>
  <thead><tr><th>Approach</th><th>Strengths</th><th>Weaknesses</th></tr></thead>
  <tbody>
    <tr><th scope="row">Score overlay<br><small>between the predictions and the optimizer</small></th><td>No tuned strength coefficient; transparent; applies to any score; removes the scores' positive linear momentum lean</td><td>Relies on a slow, backward-looking state; also removes momentum when it still pays after a volatility spike</td></tr>
    <tr><th scope="row">Learned interactions<br><small>inside the regression</small></th><td>The model decides how much to cut, predictor by predictor</td><td>Learns from a handful of crashes; depends on the chosen state; also raises momentum in calm markets, a second bet</td></tr>
    <tr><th scope="row">Optimizer cap<br><small>inside the joint optimizer</small></th><td>A hard limit on the book's exposure; scores untouched; steady</td><td>Limits the size of the tilt, not which stocks carry it; bound calibrated on the baseline; smaller gain</td></tr>
  </tbody>
</table>

Everything else stays as in the portfolio optimization article: the same
predictions (only the learned model refits them), a 7% volatility budget with
the rank buffer and trade penalty, 75 long and 75 short names, three rebalance
schedules a week apart, next-close execution and 5 bp per dollar traded. I
separate the September 1998–December 2021 development period from the
January 2022–May 2026 test period, averaging each statistic over the three
schedules. The comparison focuses on these three approaches, each used on its own.

## Why momentum crashes when the losers rebound

A momentum crash is what happens when a market that has fallen for a long time
turns sharply up. By momentum I mean the 12-1 return (the past year, skipping
the last month), and the winner-minus-loser (WML) portfolio is long the top
decile and short the bottom one. It earns a solid premium over long samples,
but with a nasty left tail. Daniel and Moskowitz measure a monthly skewness of
−4.7 for US WML deciles over 1927–2013, and the bad months aren't random: 14 of
the 15 worst follow a negative two-year market return, and all 15 come in
months when the market went up.[^dm]

The damage comes from the short leg. In July and August 1932 the market rose
82% and the loser decile 232%; from March to May 2009 the market rose 26% and
the losers 163%. The reason is leverage. After a long decline the losers are
the firms the crisis hit hardest (in March 2009 they were down 84% from their
peak on average), and their equity behaves like an out-of-the-money call on
firm value: modest downside beta, very large upside beta. Being short them
means being short a call on the market. You gain a little if the market keeps
falling and lose a lot when it turns.

The literature has two answers. Daniel and Moskowitz time the *premium*: they
forecast momentum's mean with a bear-market indicator and market variance, and
scale momentum by its conditional mean over its conditional variance. Barroso
and Santa-Clara time the *risk*: momentum's own recent volatility predicts its
future volatility much better than its mean, and scaling momentum to a
constant volatility removes most of the crash. Moreira and Muir extend that
idea to scaling any factor by the inverse of its recent variance.

The Russell 1000 is even less forgiving. An equal-weight 12-1 decile WML
portfolio has a Sharpe ratio of only 0.21 over 1998–2021, with daily skewness
of −1.1. Figure 2 puts 2009 in context. Through the 2008 sell-off momentum was
volatile but still up 8% by the March low; from 9 March to 29 May it then lost
57% while the losers rose 134%. In the vaccine-rotation week of 9 November 2020
it lost another 24%.

<div class="research-figure">
  {% include blog-chart.html chart="crash" source="/assets/momentum-crashes/crash-2009.json?v=5" label="Growth of 12-1 momentum winners, losers and the long–short portfolio, 1998–2021, opening on July 2007 to June 2010." %}
</div>
<p class="figure-caption"><strong>Figure 2: In 2009 the losers crashed up.</strong> Growth of equal-weight top-decile winners, bottom-decile losers and the long–short WML portfolio, 12-1 momentum within the Russell 1000, formed at month ends, indexed to 100 at the start of the window. It opens on July 2007–June 2010: momentum rises through the sell-off, then collapses when the losers rally from March 2009 (shaded). Drag across the chart to zoom into a period, double-click to reset, or pick another crash under Periods.</p>

## A linear ranking can't make its momentum weight conditional

Nothing in the model asks for momentum. It comes from about fifteen trend
predictors (past returns over several horizons, distance to highs,
moving-average gaps), which together tilt the book toward past winners. In the
months after the March 2009 low that tilt reached 0.45.

A linear model gives each predictor one coefficient across all market states,
so the momentum weight is an average of a regime where momentum pays and one
where it crashes. The ranking keeps that average exactly where it's most wrong,
and the book even leans a bit harder into momentum there, because the losers
are volatile and the winners defensive. On momentum's 30 worst days since 1998
the book lost 15.5 points of capital. The tilt is the obvious suspect, but
exposure alone doesn't put all of that on momentum: in the
[attribution series](/quants/short-book-rebounds.html) the deepest drawdowns
came mostly from the low-volatility tilt, and in March 2009 the
high-volatility stocks the book was short were also the past losers. Either
way, if I want the momentum weight to depend on the market state, I have to
build that in.

## Measuring momentum risk with the momentum portfolio itself

Each fix needs a signal that says when momentum is dangerous. The overlay and
the cap use the state from Figure 1, following Barroso and Santa-Clara: the WML
portfolio's own realized volatility. The learned model uses a composite state,
described with it below. With $$\hat\sigma_t$$ the annualized WML volatility
over the last 126 sessions,

$$
g_t=\max\!\left(\frac{\hat\sigma_t}{\operatorname{median}_{s\le t}\hat\sigma_s},\,1\right)
$$

compares current momentum volatility with its own history, floored at one.
I lag it one session and smooth it over five sessions, so the ranking on day $$t$$ only
uses WML returns up to $$t-1$$. At the end of 2008, $$g_t$$ was 4.0.

If momentum's variance has risen by a factor $$g_t^2$$ and its expected return
hasn't changed, a mean-variance investor would hold $$1/g_t^2$$ of the
calm-market exposure. So the share of momentum to remove is

$$
s_t = 1-\frac{1}{g_t^2}.
$$

That's variance scaling in the sense of Moreira and Muir; scaling by
volatility alone, $$1-1/g_t$$, removes less. There's no tuned strength
coefficient, and I fixed the formula before running it, although the
126-session window, the momentum definition and the expanding-median
normalization are still choices I made. The share is near zero in about 40% of
months, above 0.5 in about as many, and reached 0.94 at the end of 2008.
Because of the floor it only ever removes momentum: unlike Barroso and
Santa-Clara, I never lever it up in calm markets.

## How each approach works

**Score overlay.** After prediction, on each date I regress the scores
$$y_{i,t}$$ on the sector-demeaned momentum rank $$m_{i,t}$$ across stocks and
take out a share $$s_t$$ of the fitted momentum component:

$$
y'_{i,t}=y_{i,t}-s_t\,\max(\beta_t,0)\,\bigl(m_{i,t}-\bar m_t\bigr),
\qquad
\beta_t=\frac{\operatorname{cov}_i(y_{i,t},m_{i,t})}{\operatorname{var}_i(m_{i,t})}.
$$

It's one-sided. When the scores lean toward winners ($$\beta_t>0$$),
$$s_t=1$$ removes that linear lean completely; a lean toward losers is left
alone. I leave the remaining score component unchanged, and the optimizer sizes
the adjusted scores exactly as before.

**Learned interactions.** Here I refit the regression with the same target,
predictors, penalty and walk-forward folds as the baseline, plus fifteen extra
terms: each trend predictor times a state $$s_t$$. Each trend weight then
becomes $$\beta_k+\gamma_k(s_t-\bar s)$$, so the model can learn its own
momentum weight for turbulent markets. This state is a composite
rather than momentum volatility alone: the average of three scores between 0
and 1. Two measure how high volatility is, for the market over 21 sessions and
for the WML portfolio over 126: 0 when it's at or below its historical median,
1 at its 90th percentile or above, and in between otherwise. The third is 1 in
a bear market, when the two-year market return is negative. All three use past
data only, lagged and smoothed like $$g_t$$. Two details matter. I centre the
state on its training mean $$\bar s$$, and I rescale each interaction to the
spread of its base predictor, fold by fold on training data only. Without that,
the common penalty shrinks the interactions far harder than the predictors.
With it, the model does learn to cut momentum: per unit of the state, the trend
weights fall by about 0.2 times their calm-market size in the first
walk-forward fold and by 1.6 times in the fold that predicts 2008–2010, before
2009 is in the training data.

**Optimizer cap.** Inside the optimizer I bound the book's momentum tilt:

$$
\left|\frac{\sum_i w_{i,t}\,m_{i,t}}{\sum_i |w_{i,t}|}\right|\le\frac{B}{g_t^2},
$$

with $$B=0.45$$, the 90th percentile of the baseline's calm-market tilt. Since
both sleeves are sign-constrained, the absolute value turns into two linear
inequalities. The cap uses the same $$g_t$$ as the overlay but applies it
differently: the overlay changes the scores the optimizer sizes, while the cap
leaves the scores alone and only limits the portfolio's momentum exposure.

## The development period favours all three approaches

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 2: Development-period performance.</strong> September 1998–December 2021, after costs of 5 bp per dollar traded. Means of metrics calculated separately for the three schedules. Returns are geometric and annualized; volatility is annualized; maximum drawdown is compounded.</caption>
  <thead>
    <tr><th>Rule</th><th>Net Sharpe</th><th>Net return</th><th>Net vol.</th><th>Max drawdown</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Baseline</th><td>1.32</td><td>9.4%</td><td>7.0%</td><td>−15.5%</td></tr>
    <tr><th scope="row">Score overlay</th><td>1.54</td><td>10.6%</td><td>6.7%</td><td>−11.9%</td></tr>
    <tr><th scope="row">Learned interactions</th><td>1.55</td><td>11.5%</td><td>7.2%</td><td>−13.3%</td></tr>
    <tr><th scope="row">Optimizer cap</th><td>1.47</td><td>10.1%</td><td>6.7%</td><td>−11.4%</td></tr>
  </tbody>
</table>

In the development period, the overlay raises returns and reduces drawdowns on every
schedule. On momentum's worst days the book now barely loses, and its daily
returns are about half as negatively skewed. The overlay only takes out the
scores' positive linear momentum lean, though; selection and joint sizing can
still push the portfolio's tilt negative, as in the 2009 rebound (−0.12,
against +0.45 for the baseline). Turnover barely changes, so the gain holds at
10 and 20 bp.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/momentum-crashes/sharpe-by-rule" mobile="/assets/momentum-crashes/sharpe-by-rule_mobile" alt="Development-period Sharpe ratio and maximum drawdown for the baseline, score overlay, learned interactions and optimizer cap, with ranges across schedules." version="3" %}
</div>
<p class="figure-caption"><strong>Figure 3: The development gains hold across schedules.</strong> September 1998–December 2021. Points are means of the three rebalance schedules; lines span the lowest and highest schedule, an observed range rather than a confidence interval. After 5 bp trading costs; drawdowns compounded per schedule, with shallower drawdowns to the right. Dotted lines mark the baseline.</p>

## The approaches earn their gains differently

The overlay adds 24 points of capital over the development period, and 2009
alone accounts for 15 of them; 2009 and 2020 together make up 85%. A slow state
also has a cost. In 2008 the overlay gave up about 3.5 points by cutting a
momentum lean that was still earning. In 2020 it cut the lean before the
vaccine news and paid for that protection until the reversal arrived.

The learned model gets to about the same Sharpe by a different route.
Because the state is centred, $$s_t-\bar s$$ is negative in calm markets, so
the model can raise its momentum weight there while cutting it in turbulent
ones. The book's calm-market momentum tilt rises from 0.33 to 0.45. It earns
more than the overlay, with higher volatility and a deeper drawdown. Its worst
drawdown moves to autumn 2008, when the composite state cut momentum while it
was still earning. I chose this composite after comparing five states in the
development period, so the learned specification also reflects that selection.

The optimizer cap gives the smallest Sharpe gain and the shallowest maximum
drawdown. It limits the exposure the optimizer can take, whereas the overlay
changes the scores used to select and size stocks. Those are different
interventions, even though they use the same momentum-volatility state.

## The test period shows the cost of reducing exposure

I kept the three specifications fixed for the January 2022–May 2026
comparison, continuing the original walk-forward estimation and trading rules.
The portfolios continue across the boundary with their existing holdings.
Figure 4 shows the accumulated difference against the baseline throughout the
history; the shaded region marks the test period.

<div class="research-figure responsive-figure">
  {% include blog-chart.html chart="added" source="/assets/momentum-crashes/value-added.json?v=6" base="/assets/momentum-crashes/value-added" mobile="/assets/momentum-crashes/value-added_mobile" version="2" label="Cumulative net P&L added by the score overlay, learned interactions and optimizer cap against Ridge, through May 2026, with the test period shaded from 2022." %}
</div>
<p class="figure-caption"><strong>Figure 4: Value added against the Ridge baseline.</strong> Cumulative daily net return differences, in points of capital, averaged across three schedules after 5 bp trading costs. Zero is the baseline. Training precedes the first trades in September 1998; all subsequent P&amp;L is retained. Shading marks January 2022–27 May 2026. Under Explore, choose the test period to rebase the comparison at the end of 2021.</p>

<table class="research-table comparison-table compact-table">
  <caption><strong>Table 3: Test-period performance.</strong> 3 January 2022–27 May 2026, after costs of 5 bp per dollar traded. Means of metrics calculated separately for the three schedules. Returns are geometric and annualized; maximum drawdown is compounded. Added P&amp;L sums daily net return differences against the baseline over this period, in points of capital.</caption>
  <thead><tr><th>Rule</th><th>Net Sharpe</th><th>Net return</th><th>Max drawdown</th><th>Added P&amp;L</th></tr></thead>
  <tbody>
    <tr><th scope="row">Baseline</th><td>0.87</td><td>6.37%</td><td>−7.31%</td><td>0.00</td></tr>
    <tr><th scope="row">Score overlay</th><td>0.71</td><td>4.85%</td><td>−6.89%</td><td>−6.50</td></tr>
    <tr><th scope="row">Learned interactions</th><td>1.07</td><td>8.19%</td><td>−6.21%</td><td>+7.42</td></tr>
    <tr><th scope="row">Optimizer cap</th><td>0.71</td><td>4.86%</td><td>−6.30%</td><td>−6.40</td></tr>
  </tbody>
</table>

The overlay and cap underperform the baseline in this period. Both give up
about 6.5 points and lower Sharpe, despite smaller average maximum drawdowns.
The learned interactions improve Sharpe
on all three schedules and maximum drawdown on two, adding 7.42 points on
average. Much of that gain comes from 2023: 6.67 points, while 2022 and 2025
detract. These are four and a half years, and the three schedules share the
same market history. That is a short basis for judging protection against
infrequent momentum crashes, or for declaring the learned specification a
reliable replacement.

Momentum also performed strongly in this later sample. The same Russell 1000
12–1 winner-minus-loser portfolio earned about 16.1% a year before costs,
against 2.1% in the development period. Cutting momentum exposure therefore
had an opportunity cost. That is consistent with the overlay's underperformance,
although the factor return alone cannot explain every change in the optimized
portfolio.

## Momentum protection has a return cost

The development period made the overlay look attractive: higher Sharpe and
smaller drawdowns, with much of its benefit concentrated in 2009 and 2020.
It has since underperformed. Reducing exposure also gives up returns when
momentum continues to pay, and a volatility signal cannot know when a reversal
will arrive. The later losses make that trade-off visible; the short sample
does not settle its value over a full cycle.

I would keep both results in view. The learned interactions have performed
better in the later period, but their gain is concentrated in 2023.
Momentum protection has to earn its cost across both reversals and prolonged
trends; four and a half years cannot settle that judgement.

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

[^dm]: Daniel and Moskowitz (2016), Tables 1–2 and Section 2.3; value-weighted CRSP deciles, 1927–2013.
