---
layout: post
interactive_charts: true
title: "Momentum Crashes in a Ridge Ranking"
description: "The Ridge-regression strategy from the previous articles leans toward past winners. Why that hurts in momentum crashes, and three ways to take the exposure out."
permalink: /quants/momentum-crashes-ridge.html
toc: true
date: 2026-09-30
categories: ["Portfolio construction"]
article_label: Portfolio construction · Momentum crashes
---

In the previous articles I built a long-short Russell 1000 strategy: a
[Ridge regression on 80 predictors](/quants/2025/02/09/multiple-linear-regression.html)
ranks the stocks, and the
[joint optimizer with its trading controls](/quants/2026/08/29/portfolio-optimization.html)
sizes them, for a Sharpe ratio of 1.32 over 1998–2021. About fifteen of those
predictors are trend measures, so the book ends up leaning toward past
winners. Most of the time that's fine, but it leaves the strategy exposed to
momentum crashes, and that's what this article is about.

A momentum crash happens when a market that has fallen for a long time turns
sharply up. The stocks that fell most, the past losers, rally hardest, and a
book that is short them gives back a lot in a few weeks. Spring 2009 is the
textbook case: from 9 March to 29 May, a 12-1 winner-minus-loser portfolio in
the Russell 1000 lost 57% while its losers rose 134%. In the
[attribution series](/quants/short-book-rebounds.html) the strategy's deepest
drawdowns came mostly from its low-volatility tilt, but in March 2009 the
high-volatility stocks it was short were also the past losers. On the 30 worst
days for momentum since 1998, the book lost 15.5 points of capital.

I try three ways to take that exposure out, each at a different point between
the predictions and the portfolio. A score overlay removes part of the scores'
momentum lean after prediction. Learned interactions let the regression set
its own momentum weight for turbulent markets. An optimizer cap limits the
book's momentum tilt and leaves the scores alone. Table 1 sums up the
trade-offs; the rest of the article shows the evidence behind them.

<table class="research-table settings-table approach-table">
  <caption><strong>Table 1: Three ways to take momentum out.</strong> Where each approach acts, and what it trades off.</caption>
  <thead><tr><th>Approach</th><th>Strengths</th><th>Weaknesses</th></tr></thead>
  <tbody>
    <tr><th scope="row">Score overlay<br><small>between the predictions and the optimizer</small></th><td>No tuned strength coefficient; transparent; applies to any score; removes the scores' positive linear momentum lean</td><td>Relies on a slow, backward-looking state; also removes momentum when it still pays after a volatility spike</td></tr>
    <tr><th scope="row">Learned interactions<br><small>inside the Ridge regression</small></th><td>The model decides how much to cut, predictor by predictor, and can raise momentum in calm markets</td><td>Learns from a handful of crashes; needs careful scaling; depends on the chosen state; changes the bet</td></tr>
    <tr><th scope="row">Optimizer cap<br><small>inside the joint optimizer</small></th><td>A hard limit on the book's exposure; scores untouched; steady</td><td>Limits the size of the tilt, not which stocks carry it; bound calibrated on the baseline; smaller gain</td></tr>
  </tbody>
</table>

Everything else stays as in the portfolio optimization article: the same
predictions (only the learned model refits them), a 7% volatility budget with
the rank buffer and trade penalty, 75 long and 75 short names, three rebalance
schedules a week apart, next-close execution and 5 bp per dollar traded. I
report September 1998 to December 2021, averaging each statistic over the three
schedules and showing the lowest and highest schedule in parentheses.

## Why momentum crashes when the losers rebound

Momentum here is the 12-1 return: the past year, skipping the last month. It
earns a solid premium over long samples, but with a nasty left tail. Daniel and
Moskowitz measure a monthly skewness of −4.7 for US winner-minus-loser (WML)
deciles over 1927–2013, and the bad months aren't random: 14 of the 15 worst
follow a negative two-year market return, and all 15 come in months when the
market went up.[^dm]

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
of −1.1. Figure 1 puts 2009 in context: through the 2008 sell-off momentum was
volatile but still up 8% by the March low, then lost more than half its value
once the market turned. In the vaccine-rotation week of 9 November 2020 it lost
another 24%.

<div class="research-figure">
  {% include blog-chart.html chart="crash" source="/assets/momentum-crashes/crash-2009.json?v=5" label="Growth of 12-1 momentum winners, losers and the long–short portfolio, 1998–2021, opening on July 2007 to June 2010." %}
</div>
<p class="figure-caption"><strong>Figure 1: In 2009 the losers crashed up.</strong> Growth of equal-weight top-decile winners, bottom-decile losers and the long–short WML portfolio, 12-1 momentum within the Russell 1000, formed at month ends, indexed to 100 at the start of the window. It opens on July 2007–June 2010: momentum rises through the sell-off, then collapses when the losers rally from March 2009 (shaded). Drag across the chart to zoom into a period, double-click to reset, or pick another crash under Periods.</p>

## A linear ranking cannot make its momentum weight conditional

Nothing in the model asks for momentum. It comes from about fifteen trend
predictors (past returns over several horizons, distance to highs,
moving-average gaps), which together tilt the book toward past winners.
Measured as the book's gross-relative tilt toward the sector-demeaned 12-1
momentum rank, that tilt is about 0.33 in calm markets, 0.36 in volatile ones
and 0.45 in the months after the March 2009 low.

A linear model gives each predictor a single coefficient across all market
states, so the momentum weight is an average of a regime where momentum pays
and one where it crashes. The ranking keeps that average in exactly the state
where it's most wrong, and the book even leans a bit harder into momentum
there, because the losers are volatile and the winners defensive. That's where
the 15.5-point loss on momentum's worst days comes from. If I want the weight
to depend on the market state, I have to build that in.

## Measuring momentum risk with the momentum portfolio itself

Each fix needs a signal that says when momentum is dangerous. For the overlay
and the cap I follow Barroso and Santa-Clara and use the WML portfolio's own
realized volatility; the learned model uses a composite state, described
below. With $$\hat\sigma_t$$ its annualized volatility over the last 126
sessions,

$$
g_t=\max\!\left(\frac{\hat\sigma_t}{\operatorname{median}_{s\le t}\hat\sigma_s},\,1\right)
$$

compares current momentum volatility with its own history, floored at one.
The state is lagged one session and smoothed over five, so the ranking on day
$$t$$ only uses WML returns up to $$t-1$$. At the end of 2008, $$g_t$$ was 4.0.

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
alone. Everything else in the ranking stays as it was, and the optimizer sizes
the adjusted scores exactly as before.

**Learned interactions.** Here I refit the regression with fifteen extra
terms, each trend predictor times a market-stress state, so the model can learn
its own momentum weight for turbulent markets. Two details matter. I centre the
state on its training mean, and I rescale each interaction to the spread of its
base predictor, fold by fold on training data only. Without that, the common
penalty shrinks the interactions far harder than the predictors. With it, the
model does learn to cut momentum: the implied reduction of the trend weights
per unit of state goes from about 0.2 in the first walk-forward fold to 1.6 in
the fold that predicts 2008–2010, before 2009 is in the training data. The
state is a composite: the average of a market-volatility ramp, a bear-market
indicator (negative two-year market return) and a momentum-volatility ramp.

**Optimizer cap.** Inside the optimizer I bound the book's gross-relative tilt
toward momentum:

$$
\left|\frac{\sum_i w_{i,t}\,m_{i,t}}{\sum_i |w_{i,t}|}\right|\le\frac{B}{g_t^2},
$$

with $$B=0.45$$, the 90th percentile of the baseline's calm-market tilt. Since
both sleeves are sign-constrained, the absolute value turns into two linear
inequalities. The scores don't change; only the portfolio is constrained.

## The overlay improves return and risk together

Table 2 also includes one control, a constant shrink: it removes the overlay's
average share of the momentum lean, 0.35, on every date, with no timing.

<table class="research-table comparison-table">
  <caption><strong>Table 2: The Ridge strategy by rule.</strong> Development period, September 1998–December 2021, net of 5 bp. Means of metrics calculated separately for the three schedules, with min–max Sharpe in parentheses. Returns are geometric and annualized; maximum drawdown is compounded; skewness is of daily net returns. Crash days: P&amp;L on the 30 worst WML days, points of capital.</caption>
  <thead>
    <tr><th>Rule</th><th>Net Sharpe</th><th>Net return</th><th>Net vol.</th><th>Max drawdown</th><th>Skewness</th><th>Crash days</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Baseline</th><td>1.32<br><small>(1.26–1.36)</small></td><td>9.4%</td><td>7.0%</td><td>−15.5%</td><td>−0.46</td><td>−15.5</td></tr>
    <tr><th scope="row">Constant shrink</th><td>1.41<br><small>(1.34–1.45)</small></td><td>9.8%</td><td>6.8%</td><td>−13.4%</td><td>−0.36</td><td>−11.1</td></tr>
    <tr><th scope="row">Optimizer cap</th><td>1.47<br><small>(1.41–1.52)</small></td><td>10.1%</td><td>6.7%</td><td>−11.4%</td><td>−0.21</td><td>−8.2</td></tr>
    <tr class="selected-rule"><th scope="row">Score overlay</th><td>1.54<br><small>(1.44–1.61)</small></td><td>10.6%</td><td>6.7%</td><td>−11.9%</td><td>−0.23</td><td>−1.9</td></tr>
    <tr><th scope="row">Learned interactions</th><td>1.55<br><small>(1.48–1.61)</small></td><td>11.5%</td><td>7.2%</td><td>−13.3%</td><td>−0.27</td><td>+2.6</td></tr>
    <tr><th scope="row">Learned + overlay</th><td>1.67<br><small>(1.57–1.74)</small></td><td>12.3%</td><td>7.1%</td><td>−13.5%</td><td>−0.26</td><td>+9.9</td></tr>
  </tbody>
</table>

The overlay does what it was built for. On momentum's worst days the book now
barely loses, it earns more with a smaller drawdown on every schedule, and its
daily returns are about half as negatively skewed. The overlay only reduces
the scores' positive linear exposure to momentum, though; selection and joint
sizing can still push the portfolio's tilt negative, as in the 2009 rebound
(−0.12, against +0.45 for the baseline). Turnover barely changes, so the gain
holds at 10 and 20 bp.

<div class="research-figure">
  {% include theme-svg-figure.html base="/assets/momentum-crashes/sharpe-by-rule" mobile="/assets/momentum-crashes/sharpe-by-rule_mobile" alt="Net Sharpe ratio and maximum drawdown of the Ridge strategy by rule, schedule means with lowest-to-highest schedule ranges." version="2" %}
</div>
<p class="figure-caption"><strong>Figure 2: Sharpe ratio and maximum drawdown by rule.</strong> Points are means of the three rebalance schedules; lines span the lowest and highest schedule, an observed range rather than a confidence interval. Net of 5 bp; drawdowns compounded per schedule, with shallower drawdowns to the right. Dotted lines mark the baseline. Marker shapes group the approaches: optimizer caps, score overlay, learned interactions and combinations.</p>

Part of the gain is just holding less momentum: the constant shrink reaches
1.41, so less momentum helped in this backtest. Timing adds the other 0.13,
between 0.10 and 0.17 depending on the schedule. The overlay also beats the
whole-book controls I tried. Scaling the entire baseline book by $$1-s_t$$,
targeting its own volatility, or hedging it with the WML portfolio all stop at
1.36–1.38, so targeting momentum in the scores did better than de-risking
everything.

Figure 3 covers the whole period. It opens on the baseline and the overlay;
under Explore you can change the window and add the other rules.

<div class="research-figure performance-figure responsive-figure">
  {% include blog-chart.html chart="performance" source="/assets/momentum-crashes/performance.json?v=4" label="Net growth and drawdown of the Ridge baseline and the score overlay, 1998–2021, with the other rules available under Explore." %}
</div>
<p class="figure-caption"><strong>Figure 3: Growth and drawdown, 1998–2021.</strong> Net growth index (log scale) and drawdown after 5 bp costs. Each path averages three separately compounded schedules, so its drawdowns are shallower than the per-schedule maxima in Table 2. The rules run at slightly different volatilities; Table 2 compares Sharpe.</p>

## Timing pays in a few crashes

The overlay adds 24 points of capital over 23 years, and 2009 alone accounts
for 15 of them; 2009 and 2020 together make up 85%. Drop any single year and
the Sharpe gain stays positive (the smallest, +0.13, is without 2009). Drop
both 2009 and 2020 and it's +0.07. By five-year block it helps in 1998–2002,
2008–2012, 2013–2017 and 2018–2021 and is flat in 2003–2007, when the state was
mostly off.

<div class="research-figure">
  {% include blog-chart.html chart="added" source="/assets/momentum-crashes/value-added.json?v=4" label="Cumulative value added against the Ridge baseline by each rule, 1998–2021." %}
</div>
<p class="figure-caption"><strong>Figure 4: Value added against the baseline.</strong> Cumulative sum of daily net return differences, points of capital, mean of the three schedules. The constant shrink removes the overlay's average share on every date. Shaded: 2009 and 2020.</p>

That's what a crash hedge should look like: it costs little in normal years
and pays in the few episodes that matter. It also means the evidence rests on
a handful of crashes. The Sharpe gain has a block-bootstrap standard error of
about 0.10 per schedule, and the timing part about 0.08.

A slow state has a cost too. The overlay gave up about 3.5 points in 2008 by
cutting a momentum lean that was still earning. In 2020 momentum volatility
had been high since late 2019, so it cut the lean while the baseline book was
still making money (+5.3 points from the March low to 6 November), which cost
about 1 point, and then made 3.5 points in the vaccine week.

The details don't matter much. A 63-session window, a rolling three-year median
instead of the expanding one, and 12-0 instead of 12-1 momentum all give 1.53,
and using the market-volatility ramp as the state gives 1.54. Two versions are
weaker: volatility scaling (1.48), because it removes less, and measuring the
lean against 6-1 momentum (1.43), because 6-1 overlaps much less with what the
ranking actually holds.

## The learned model buys return with a different bet

The learned model gets to the same Sharpe as the overlay, 1.55, by a different
route. Because the state is centred, the model can raise its momentum weight in
calm markets while cutting it in turbulent ones, and the score's calm-market
momentum lean goes up from about 0.36 to 0.50. Return is higher (11.5% against
10.6%), but so are volatility and drawdown (13.3%). The worst drawdown moves to
autumn 2008, when the composite state cut momentum while it was still earning,
and 2007 and 2009 account for 72% of the gain.

It also depends a lot on the state. With market volatility alone it reaches
1.42, with momentum volatility 1.45, with the Daniel–Moskowitz bear ×
volatility state 1.39, and I picked the composite after comparing the four. A
single momentum × state term instead of fifteen trend terms doesn't work here
(1.30–1.35).

Stacking the overlay on the learned scores gives the best Sharpe in Table 2,
1.67. I wouldn't take that at face value. I tried this combination after
seeing the single-layer results, and among about 40 variants the best will
look good partly by selection. It also makes 9.9 points on crash days, but its
measured momentum tilt there is close to the overlay's (−0.13 in the 2009
rebound and −0.18 in the vaccine week, against −0.12 and −0.14). So a larger
short-momentum position doesn't seem to explain the extra gain, and I wouldn't
count on it.

## The optimizer cap is the steadiest and the smallest

The cap works on the portfolio instead of the scores. It only binds when the
tilt would exceed the bound, it has the shallowest maximum drawdown in Table 2
(11.4%), and its gain is even across schedules (+0.14 to +0.17). But it adds
only 0.13 to 0.15 in Sharpe, cuts crash-day losses only to 8 points, and adds
nothing once the overlay is in place (1.54 with both). The cap and the overlay
use the same state; what differs is how they use it. The overlay changes the
scores the optimizer sizes, while the cap only limits the portfolio's momentum
exposure. Here that makes the cap a guardrail more than a fix.

Two ideas from the literature didn't help. A Daniel–Moskowitz state, bear market
times market volatility, adds only 0.04 as an overlay: the two-year market
return was negative on about a fifth of the days (in 2001–2003 and 2008–2010),
and the state was off throughout 2020. Neutralizing only the loser leg adds
0.08, less than the symmetric version at the same strength (+0.10).

<details class="research-details" markdown="0">
<summary>Other variants I tried (Table 3)</summary>

<table class="research-table comparison-table">
  <caption><strong>Table 3: Other Ridge variants.</strong> Variants not shown in Figure 2. Development period, net of 5 bp, mean Sharpe over the three schedules; the baseline is 1.32. The first three overlays use half strength.</caption>
  <thead><tr><th>Variant</th><th>Net Sharpe</th></tr></thead>
  <tbody>
    <tr><th scope="row">Overlay, bear market × market volatility</th><td>1.35</td></tr>
    <tr><th scope="row">Overlay, loser leg only</th><td>1.40</td></tr>
    <tr><th scope="row">Overlay on all 17 trend characteristics</th><td>1.41</td></tr>
    <tr><th scope="row">Learned, market-volatility state</th><td>1.42</td></tr>
    <tr><th scope="row">Learned, momentum-volatility state</th><td>1.45</td></tr>
    <tr><th scope="row">Overlay, volatility scaling</th><td>1.48</td></tr>
    <tr><th scope="row">Hand-set shrink of the fifteen trend bets</th><td>1.48</td></tr>
  </tbody>
</table>
</details>

## Remove momentum when momentum is volatile

The score overlay is my preferred specification here. It has no tuned strength
coefficient, I fixed its formula before running it, it sits between the
predictions and the optimizer without touching either, and it improves return
and risk together: Sharpe from 1.32 to 1.54, maximum drawdown from 15.5% to
11.9%, and almost no loss when momentum crashes. About 0.09 of the gain comes
from holding less momentum and 0.13 from timing, mostly in 2009 and 2020, so my
guess is that 0.1 to 0.15 is a more realistic gain outside this sample than
0.22. The preference itself came out of comparing many rules, and those
comparisons change both where each rule acts and which state it uses. The
learned model and the combination earn more return by taking a different, more
concentrated bet, and the cap is a useful guardrail.

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
