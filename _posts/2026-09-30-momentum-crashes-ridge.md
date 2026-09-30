---
layout: post
interactive_charts: true
title: "Managing Momentum Crashes: A Comparison of Different Approaches"
description: "The regression strategy from the previous articles leans toward past winners and earns much less once momentum turns volatile. Three ways to take that exposure out, and what each one costs."
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
report September 1998 to December 2021, averaging each statistic over the three
schedules and showing the lowest and highest schedule in parentheses.

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

## The overlay earns more with smaller drawdowns

Before comparing the rules I added one control. The constant shrink removes the
overlay's average share of the momentum lean, 0.35, on every date, with no
timing. It separates holding less momentum from holding less of it at the right
time.

<table class="research-table comparison-table">
  <caption><strong>Table 2: The strategy by rule.</strong> Development period, September 1998–December 2021, net of 5 bp. Means of metrics calculated separately for the three schedules, with min–max Sharpe in parentheses. Returns are geometric and annualized; maximum drawdown is compounded; skewness is of daily net returns. Crash days: P&amp;L on the 30 worst WML days, points of capital.</caption>
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

With the overlay, returns rise a little and drawdowns get smaller, on every
schedule. On momentum's worst days the book now barely loses, and its daily
returns are about half as negatively skewed. The overlay only takes out the
scores' positive linear momentum lean, though; selection and joint sizing can
still push the portfolio's tilt negative, as in the 2009 rebound (−0.12,
against +0.45 for the baseline). Turnover barely changes, so the gain holds at
10 and 20 bp.

<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/assets/momentum-crashes/sharpe-by-rule" mobile="/assets/momentum-crashes/sharpe-by-rule_mobile" alt="Net Sharpe ratio and maximum drawdown by rule, schedule means with lowest-to-highest schedule ranges." version="2" %}
</div>
<p class="figure-caption"><strong>Figure 3: Sharpe ratio and maximum drawdown by rule.</strong> Points are means of the three rebalance schedules; lines span the lowest and highest schedule, an observed range rather than a confidence interval. Net of 5 bp; drawdowns compounded per schedule, with shallower drawdowns to the right. Dotted lines mark the baseline. Marker shapes group the approaches: optimizer caps, score overlay, learned interactions and combinations.</p>

Part of the gain is just holding less momentum: the constant shrink reaches
1.41, so less momentum helped in this backtest. Timing adds the other 0.13,
between 0.10 and 0.17 depending on the schedule. It shows up where you'd
expect: in the top bucket of Figure 1 the constant shrink only gets to 0.95,
against 1.39 for the overlay. The overlay also beat the whole-book controls I
tried. Scaling the entire baseline book by $$1-s_t$$, targeting its own
volatility, or hedging it with the WML portfolio all stop at 1.36–1.38. Among
those controls, adjusting the scores' momentum lean did better than de-risking
the whole book.

Figure 4 covers the whole period. It opens on the baseline and the overlay;
under Explore you can change the window and add the other rules.

<div class="research-figure performance-figure responsive-figure">
  {% include blog-chart.html chart="performance" source="/assets/momentum-crashes/performance.json?v=5" label="Net growth and drawdown of the baseline and the score overlay, 1998–2021, with the other rules available under Explore." %}
</div>
<p class="figure-caption"><strong>Figure 4: Growth and drawdown, 1998–2021.</strong> Net growth index (log scale) and drawdown after 5 bp costs. Each path averages three separately compounded schedules, so its drawdowns are shallower than the per-schedule maxima in Table 2. The rules run at slightly different volatilities; Table 2 compares Sharpe.</p>

## Timing pays in a few crashes

The overlay adds 24 points of capital over 23 years, and 2009 alone accounts
for 15 of them; 2009 and 2020 together make up 85%. Drop any single year and
the Sharpe gain stays positive (the smallest, +0.13, is without 2009). Drop
both 2009 and 2020 and it's +0.07. By five-year block it helps in 1998–2002,
2008–2012, 2013–2017 and 2018–2021 and is flat in 2003–2007, when the state was
mostly off.

<div class="research-figure">
  {% include blog-chart.html chart="added" source="/assets/momentum-crashes/value-added.json?v=4" label="Cumulative value added against the baseline by each rule, 1998–2021." %}
</div>
<p class="figure-caption"><strong>Figure 5: Value added against the baseline.</strong> Cumulative sum of daily net return differences, points of capital, mean of the three schedules. The constant shrink removes the overlay's average share on every date. Shaded: 2009 and 2020.</p>

That's what a crash hedge should look like: it costs little in normal years
and pays in the few episodes that matter. It also means the evidence rests on
a handful of crashes. The Sharpe gain has a block-bootstrap standard error of
about 0.10 per schedule, and the timing part about 0.08.

A slow state has a cost too. The overlay gave up about 3.5 points in 2008 by
cutting a momentum lean that was still earning. In 2020 momentum volatility
had been high since late 2019, so it cut the lean while the baseline book was
still making money (+5.3 points from the March low to 6 November), which cost
about 1 point, and then made 3.5 points in the vaccine week.

Most of the details don't matter much. A 63-session window, a rolling
three-year median instead of the expanding one, and 12-0 instead of 12-1
momentum all give 1.53, and using the market-volatility score as the state gives
1.54. Two versions are weaker: volatility scaling (1.48), because it removes
less, and measuring the lean against 6-1 momentum (1.43), because 6-1 overlaps
much less with what the ranking actually holds.

## The learned model buys return with a different bet

The learned model gets to the same Sharpe as the overlay by a different route.
Because the state is centred, $$s_t-\bar s$$ is negative in calm markets, so
the model can raise its momentum weight there while cutting it in turbulent
ones, and the book's calm-market momentum
tilt goes up from 0.33 to 0.45. It earns more than the overlay, but with higher
volatility and a deeper drawdown. The worst drawdown moves to autumn 2008, when
the composite state cut momentum while it was still earning.

What made me hesitate is that it adds value more steadily. In Figure 5 the
learned model and the combination beat the baseline in 15 and 16 of the 24
calendar years, against 12 for the overlay, whose gain sits mostly in 2009 and
2020. So I looked at what the learned model does with each state I tried.
Every row in Table 3 is the same model; only the state it's given changes. The
composite is the average of the three scores described above. The other rows
use a single ingredient: the momentum-volatility score, the market-volatility
score, the bear-market indicator times the market-volatility score (the
Daniel–Moskowitz state), or the share the overlay removes, 1 − 1/g².

<table class="research-table comparison-table">
  <caption><strong>Table 3: Learned interactions by state.</strong> Development period, net of 5 bp, schedule means with min–max Sharpe in parentheses. Momentum tilt as defined in the introduction, averaged over calm days (market-volatility score at zero) and over the 2009 rebound (10 March–16 September).</caption>
  <thead><tr><th>Rule</th><th>Net Sharpe</th><th>Tilt, calm days</th><th>Tilt, 2009 rebound</th></tr></thead>
  <tbody>
    <tr><th scope="row">Baseline</th><td>1.32<br><small>(1.26–1.36)</small></td><td>0.33</td><td>0.45</td></tr>
    <tr class="selected-rule"><th scope="row">Score overlay</th><td>1.54<br><small>(1.44–1.61)</small></td><td>0.26</td><td>−0.12</td></tr>
    <tr><th scope="row">Learned, composite state</th><td>1.55<br><small>(1.48–1.61)</small></td><td>0.45</td><td>0.08</td></tr>
    <tr><th scope="row">Learned, momentum volatility</th><td>1.45<br><small>(1.38–1.53)</small></td><td>0.37</td><td>0.41</td></tr>
    <tr><th scope="row">Learned, market volatility</th><td>1.42<br><small>(1.39–1.48)</small></td><td>0.46</td><td>0.31</td></tr>
    <tr><th scope="row">Learned, bear × volatility</th><td>1.39<br><small>(1.29–1.45)</small></td><td>0.42</td><td>−0.10</td></tr>
    <tr><th scope="row">Learned, momentum variance</th><td>1.35<br><small>(1.31–1.37)</small></td><td>0.33</td><td>0.37</td></tr>
  </tbody>
</table>

Two things stand out. Every learned version raises the calm-market tilt or
keeps it, whatever the state: once the interaction terms can explain the crash
losses, the ordinary trend weights drift up. That's a second bet, more momentum
when markets are quiet, on top of the crash fix. And most versions don't cut
momentum much in the 2009 rebound at all; only the composite and the bear ×
volatility state do. The typical learned model lands around 1.42, below the
overlay, and the 1.55 is the best of five states, with the composite picked
after I'd seen the results. A single momentum × state term instead of fifteen
trend terms doesn't work either (1.30–1.35).

If I wanted a learned version I'd trust, I'd take that freedom away. Keep the
baseline weights fixed, use momentum volatility as the state, and let the model
learn only how much to cut each trend weight as the state rises, never to add.
It then answers the same question as the overlay, how much momentum to remove
and when, rather than adding a bet on calm markets.

Stacking the overlay on the learned scores gives the best Sharpe in Table 2,
1.67. I wouldn't take that at face value. I tried this combination after
seeing the single-layer results, and among about 40 variants the best will
look good partly by selection. It also makes 9.9 points on crash days, yet its
average momentum tilt there is close to the overlay's (−0.13 in the 2009
rebound and −0.18 after the vaccine news, against −0.12 and −0.14). That suggests
a bigger short-momentum position isn't what earns the extra, but it doesn't
tell me what does, so I wouldn't count on it.

## The optimizer cap is the steadiest and the smallest

The cap only binds when the tilt would exceed the bound. It has the shallowest
maximum drawdown in Table 2, and its gain is even across schedules (+0.14 to
+0.17). But it adds less Sharpe than the overlay, still loses about 8 points on
crash days, and adds nothing once the overlay is in place (1.54 with both).
Limiting how much momentum the book holds isn't the same as removing the
momentum lean from the scores the optimizer ranks on. Still, going from 1.32 to
1.47 with the shallowest drawdown is a real improvement; the cap just works
better as a guardrail next to the overlay than as the main fix.

Two other ideas helped less. A Daniel–Moskowitz state, bear market
times market volatility, adds only 0.04 as an overlay: the two-year market
return was negative on about a fifth of the days (in 2001–2003 and 2008–2010),
and the state was off throughout 2020. Neutralizing only the loser leg adds
0.08, less than the symmetric version at the same strength (+0.10).

<details class="research-details" markdown="0">
<summary>Other variants I tried (Table 4)</summary>

<table class="research-table comparison-table">
  <caption><strong>Table 4: Other variants.</strong> Variants not shown in Figure 3 or Table 3. Development period, net of 5 bp, mean Sharpe over the three schedules; the baseline is 1.32. The first three overlays use half strength.</caption>
  <thead><tr><th>Variant</th><th>Net Sharpe</th></tr></thead>
  <tbody>
    <tr><th scope="row">Overlay, bear market × market volatility</th><td>1.35</td></tr>
    <tr><th scope="row">Overlay, loser leg only</th><td>1.40</td></tr>
    <tr><th scope="row">Overlay on all 17 trend characteristics</th><td>1.41</td></tr>
    <tr><th scope="row">Overlay, volatility scaling</th><td>1.48</td></tr>
    <tr><th scope="row">Hand-set shrink of the fifteen trend bets</th><td>1.48</td></tr>
  </tbody>
</table>
</details>

## Remove momentum when momentum is volatile

The score overlay is the version I'd keep. It has no tuned strength
coefficient, I fixed its formula before running it, and it sits between the
predictions and the optimizer without touching either. With it, returns rise a
little, drawdowns get smaller and the book barely loses when momentum crashes.
About 0.09 of the Sharpe gain comes from holding less momentum and 0.13 from
timing, mostly in 2009 and 2020, so I'd expect something like 0.1 to 0.15
outside this sample rather than the full 0.22. That preference also came out of
comparing many rules, which differ both in where they act and in which state
they use. The learned model and the combination add value more steadily and
earn more, but they do it with a second bet, more momentum in calm markets, and
their results depend on a state I picked after comparing several. I'd rather
keep the rule I fixed in advance. The cap gives a smaller but steady
improvement that works well as a guardrail.

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
