---
layout: post
interactive_charts: true
title: "Momentum Crashes in a Ridge Ranking"
description: "Why the Ridge ranking keeps its momentum bet when that bet is most dangerous, and three ways to take it out: a score overlay, learned state interactions and an optimizer cap."
permalink: /quants/momentum-crashes-ridge.html
toc: true
date: 2026-09-30
categories: ["Portfolio construction"]
article_label: Portfolio construction · Momentum crashes
---

The Ridge strategy of the earlier articles ranks the Russell 1000 with a
[Ridge regression on 80 predictors](/quants/2025/02/09/multiple-linear-regression.html)
and sizes the ranking with the
[joint optimizer and its trading controls](/quants/2026/08/29/portfolio-optimization.html),
for a development-period Sharpe ratio of 1.32: the last row of
[Table 2 in that article](/quants/2026/08/29/portfolio-optimization.html#development-results). The
[attribution series](/quants/short-book-rebounds.html) showed where that book
loses: its two deepest drawdowns came mostly from the low-volatility tilt, and
in March 2009 the high-volatility stocks it was short were also the past
losers. That rebound was a momentum crash, and the ranking carries a lot of
momentum.

In this article I start from why momentum crashes happen and why a linear
ranking is exposed to them, then try three ways to take the exposure out of
the same Ridge strategy. Each acts at a different point between the Ridge
predictions and the portfolio.

- **Score overlay.** After prediction, remove part of the scores' momentum
  lean when momentum's own volatility is high.
- **Learned interactions.** Refit the Ridge regression with trend × state
  terms, so the model learns its own momentum weight for turbulent markets.
- **Optimizer cap.** Leave the scores alone and bound the book's momentum
  tilt in the optimizer, more tightly when momentum is volatile.

<table class="research-table settings-table approach-table">
  <caption><strong>Table 1: Three ways to take momentum out.</strong> Where each approach acts, and what it trades off.</caption>
  <thead><tr><th>Approach</th><th>Strengths</th><th>Weaknesses</th></tr></thead>
  <tbody>
    <tr><th scope="row">Score overlay<br><small>between the predictions and the optimizer</small></th><td>No fitted parameter; transparent; works on any score; removes exactly the momentum lean</td><td>Relies on a slow, backward-looking state; also removes momentum when it still pays after a volatility spike</td></tr>
    <tr><th scope="row">Learned interactions<br><small>inside the Ridge regression</small></th><td>The model decides how much to cut, predictor by predictor, and can raise momentum in calm markets</td><td>Learns from a handful of crashes; needs careful scaling; depends on the chosen state; changes the bet</td></tr>
    <tr><th scope="row">Optimizer cap<br><small>inside the joint optimizer</small></th><td>A hard limit on the book's exposure; scores untouched; steady</td><td>Limits the size of the tilt, not which stocks carry it; bound calibrated on the baseline; smaller gain</td></tr>
  </tbody>
</table>

Everything else is the book from the portfolio optimization article,
unchanged: the Ridge-80 predictions, joint sizing at a 7% volatility budget
with the rank buffer and trade penalty, 75 long and 75 short names, three
rebalance schedules starting a week apart, next-close execution and 5 bp per
dollar traded. Numbers cover September 1998 to December 2021 and are means
over the three schedules, with the lowest and highest schedule in parentheses.

## Momentum crashes when the losers rebound

Momentum buys the stocks that rose most over the past year, skipping the last
month, and sells those that fell most. It earns a solid premium over long
samples, but its return distribution has a long left tail: Daniel and
Moskowitz measure a monthly skewness of −4.7 for US winner-minus-loser (WML)
deciles over 1927–2013. The worst months are not random. Fourteen of the 15
worst WML months follow a negative two-year market return, and all 15 come in
months when the market rose.[^dm]

The damage comes from the short leg. In July and August 1932 the market rose
82% and the loser decile 232%; from March to May 2009 the market rose 26% and
the losers 163%. The mechanism is leverage. After a long decline the losers
are the firms the crisis hit hardest (in March 2009 they were down 84% from
their peak on average), and their equity behaves like an out-of-the-money call
on firm value: modest downside beta, very large upside beta. A book that is
short them is short a call on the market. It gains a little if the market
keeps falling and loses a lot when it turns.

The literature offers two answers. Daniel and Moskowitz time the *premium*:
they forecast momentum's mean with a bear-market indicator and market
variance, and weight momentum by its conditional mean over its conditional
variance. Barroso and Santa-Clara time the *risk*: momentum's own recent
volatility predicts its future volatility much better than it predicts its
mean, and scaling momentum to a constant volatility removes most of the
crash. Moreira and Muir generalize the second idea to scaling a factor by the
inverse of its recent variance.

The Russell 1000 shows the same pattern, just less forgivingly. An
equal-weight 12-1 decile WML portfolio inside the index has a Sharpe ratio of
only 0.21 over 1998–2021, with daily skewness of −1.1. Figure 1 follows it
through the 2009 rebound: from 9 March to 29 May the losers rose 134% and the
long–short portfolio lost 57%. In the week of 9 November 2020, the vaccine
rotation, it lost another 24%.

<div class="research-figure">
  {% include blog-chart.html chart="crash" source="/assets/momentum-crashes/crash-2009.json?v=2" label="Growth of 12-1 momentum winners, losers and the long–short portfolio from 6 March to August 2009." %}
</div>
<p class="figure-caption"><strong>Figure 1: In 2009 the losers crashed up.</strong> Growth of equal-weight top-decile winners, bottom-decile losers and the long–short WML portfolio from the 6 March 2009 close, 12-1 momentum within the Russell 1000, formed at month ends. Shaded: 9 March to 29 May.</p>

## A linear ranking cannot make its momentum weight conditional

The Ridge ranking holds no momentum factor on purpose. About fifteen of its
eighty predictors are trend measures (past returns over several horizons,
distance to highs, moving-average gaps), and together they tilt the book
toward past winners. I measure that as the book's gross-relative tilt toward
the sector-demeaned 12-1 momentum rank: about 0.33 in calm markets, 0.36 in
volatile ones and 0.45 in the months after the March 2009 low.

A linear model gives each predictor one coefficient, fitted across all market
states, so the momentum weight averages a regime where momentum pays and one
where it crashes. The ranking keeps that average in exactly the state where it
is most wrong, and the book leans slightly harder into momentum, because the
losers are volatile and the winners defensive. On the 30 worst WML days in the
sample the baseline book loses 15.5 points of capital.

A LightGBM ranking on the same predictors loses only 1.8 points on those days;
its splits can already let the trend effect depend on volatility. For Ridge
the state dependence has to be added explicitly.

## Measuring momentum risk with the momentum portfolio itself

All three fixes need a state that says when momentum is dangerous. Following
Barroso and Santa-Clara, I use the WML portfolio's own realized volatility.
With $$\hat\sigma_t$$ its annualized volatility over the last 126 sessions,

$$
g_t=\max\!\left(\frac{\hat\sigma_t}{\operatorname{median}_{s\le t}\hat\sigma_s},\,1\right)
$$

compares current momentum volatility with its own expanding median, floored at
one. The state is lagged one session and smoothed over five sessions, so the
ranking on day $$t$$ only uses WML returns up to $$t-1$$. At the end of 2008,
$$g_t$$ was 4.0.

A mean-variance investor who treats momentum as a risk factor whose variance
has risen by a factor $$g_t^2$$, with its expected return unchanged, would
hold $$1/g_t^2$$ of the calm-market exposure. So I define the share of
momentum to remove as

$$
s_t = 1-\frac{1}{g_t^2}.
$$

This is variance scaling in the sense of Moreira and Muir; scaling by
volatility alone, $$1-1/g_t$$, removes less. The share has no free parameter,
and I fixed it before running it. It is near zero in about 40% of months,
above 0.5 in about as many, and reached 0.94 at the end of 2008. The floor
makes the rule shrink-only: unlike Barroso and Santa-Clara, I never lever
momentum up in calm markets.

## How each approach works

**Score overlay.** After prediction, on each date I regress the Ridge scores
$$y_{i,t}$$ on the sector-demeaned momentum rank $$m_{i,t}$$ across stocks and
remove a share $$s_t$$ of the fitted momentum component:

$$
y'_{i,t}=y_{i,t}-s_t\,\max(\beta_t,0)\,\bigl(m_{i,t}-\bar m_t\bigr),
\qquad
\beta_t=\frac{\operatorname{cov}_i(y_{i,t},m_{i,t})}{\operatorname{var}_i(m_{i,t})}.
$$

It is one-sided: it only removes a lean toward winners. At $$s_t=1$$ the
scores are fully momentum-neutral, and the rest of the ranking is untouched.
The optimizer then sizes the adjusted scores exactly as before.

**Learned interactions.** I refit the Ridge regression with fifteen extra
terms, each trend predictor times a market-stress state, so the model can
learn its own momentum weight for turbulent markets. Two details matter. I
centre the state on its training mean, and I rescale each interaction to the
spread of its base predictor, fold by fold on training data only; otherwise
the common penalty shrinks the interactions much harder than the predictors.
With the rescaling, Ridge learns a shrink: the implied reduction of the trend
weights per unit of state rises from about 0.2 in the first walk-forward fold
to 1.6 in the fold that predicts 2008–2010, before 2009 was in the training
data. The state here is a composite: the average of a market-volatility ramp,
a bear-market indicator (negative two-year market return) and a
momentum-volatility ramp.

**Optimizer cap.** Inside the joint optimizer I bound the book's
gross-relative tilt toward momentum:

$$
\left|\frac{\sum_i w_{i,t}\,m_{i,t}}{\sum_i |w_{i,t}|}\right|\le\frac{B}{g_t^2},
$$

with $$B=0.45$$, the 90th percentile of the baseline's calm-market tilt.
Because both sleeves are sign-constrained, this is one linear constraint. The
scores stay as they are; only the portfolio is constrained.

## The overlay improves return and risk together

<table class="research-table comparison-table">
  <caption><strong>Table 2: The Ridge strategy by rule.</strong> Development period, September 1998–December 2021, net of 5 bp. Means of metrics calculated separately for the three schedules, with min–max Sharpe in parentheses. Returns are geometric and annualized; maximum drawdown is compounded. Crash days: P&amp;L on the 30 worst WML days, points of capital.</caption>
  <thead>
    <tr><th>Rule</th><th>Net Sharpe</th><th>Net return</th><th>Net vol.</th><th>Max drawdown</th><th>Crash days</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Baseline</th><td>1.32<br><small>(1.26–1.36)</small></td><td>9.4%</td><td>7.0%</td><td>−15.5%</td><td>−15.5</td></tr>
    <tr><th scope="row">Constant shrink</th><td>1.41<br><small>(1.34–1.45)</small></td><td>9.8%</td><td>6.8%</td><td>−13.4%</td><td>−11.1</td></tr>
    <tr><th scope="row">Optimizer cap</th><td>1.47<br><small>(1.41–1.52)</small></td><td>10.1%</td><td>6.7%</td><td>−11.4%</td><td>−8.2</td></tr>
    <tr class="selected-rule"><th scope="row">Score overlay</th><td>1.54<br><small>(1.44–1.61)</small></td><td>10.6%</td><td>6.7%</td><td>−11.9%</td><td>−1.9</td></tr>
    <tr><th scope="row">Learned interactions</th><td>1.55<br><small>(1.48–1.61)</small></td><td>11.5%</td><td>7.2%</td><td>−13.3%</td><td>+2.6</td></tr>
    <tr><th scope="row">Learned + overlay</th><td>1.67<br><small>(1.57–1.74)</small></td><td>12.3%</td><td>7.1%</td><td>−13.5%</td><td>+9.9</td></tr>
  </tbody>
</table>

Table 2 shows that the overlay does what it was designed to do. On crash days
the book barely loses (1.9 points against 15.5), the 2009 rebound turns from a
6.1-point loss into a 3.5-point gain, and the book's momentum tilt in the
months after the March 2009 low is −0.12 instead of +0.45. The maximum
drawdown falls from 15.5% to 11.9%, the worst month from −6.8% to −5.4%, and
daily skewness from −0.46 to −0.23. Sharpe rises from 1.32 to 1.54, by 0.19
to 0.25 on each schedule. Turnover barely changes, so the gain survives higher
costs: 1.36 against 1.15 at 10 bp, and 1.00 against 0.82 at 20 bp.

<div class="research-figure">
  {% include theme-svg-figure.html base="/assets/momentum-crashes/sharpe-by-rule" mobile="/assets/momentum-crashes/sharpe-by-rule_mobile" alt="Net Sharpe ratio of the Ridge strategy by rule, schedule means with lowest-to-highest schedule ranges." version="1" %}
</div>
<p class="figure-caption"><strong>Figure 2: Sharpe ratio by rule.</strong> Points are means of the three rebalance schedules; lines span the lowest and highest schedule, an observed range rather than a confidence interval. Net of 5 bp. The dotted line marks the baseline. Marker shapes group the approaches: optimizer caps, score overlay, learned interactions and combinations.</p>

Part of the gain is simply holding less momentum. The constant shrink removes
the overlay's average share, 0.35, on every date and reaches 1.41, so the
ranking carries more momentum than it should on average. Timing is worth the
other 0.13, between 0.10 and 0.17 on each schedule. The overlay also beats
simpler ways of de-risking the whole book: scaling the entire baseline book by
$$1-s_t$$, targeting its own volatility, or hedging it with the WML portfolio
reach only 1.36–1.38. The problem is specific to momentum, and the fix works
best in the scores, before the optimizer sizes the positions.

Figure 3 shows the whole development period. By default it compares the
baseline with the score overlay; under Explore you can change the window and
add the other rules.

<div class="research-figure performance-figure responsive-figure">
  {% include blog-chart.html chart="performance" source="/assets/momentum-crashes/performance.json?v=2" label="Net growth and drawdown of the Ridge baseline and the score overlay, 1998–2021, with the other rules available under Explore." %}
</div>
<p class="figure-caption"><strong>Figure 3: Growth and drawdown, 1998–2021.</strong> Net growth index (log scale) and drawdown after 5 bp costs. Each path averages three separately compounded schedules, so its drawdowns are shallower than the per-schedule maxima in Table 2. The rules run at slightly different volatilities; Table 2 compares Sharpe.</p>

## Timing pays in a few crashes

The overlay adds 24 points of capital over 23 years, and 2009 alone
contributes 15 of them; 2009 and 2020 together contribute 85%. Leaving out any
single year keeps the Sharpe gain positive, with the smallest gain, +0.13,
when 2009 is left out. Leaving out both 2009 and 2020 the gain is +0.07. By
five-year block it improves 1998–2002, 2008–2012, 2013–2017 and 2018–2021 and
is flat in 2003–2007, when the state was mostly off.

<div class="research-figure">
  {% include blog-chart.html chart="added" source="/assets/momentum-crashes/value-added.json?v=2" label="Cumulative value added against the Ridge baseline by each rule, 1998–2021." %}
</div>
<p class="figure-caption"><strong>Figure 4: Value added against the baseline.</strong> Cumulative sum of daily net return differences, points of capital, mean of the three schedules. The constant shrink removes the overlay's average share on every date. Shaded: 2009 and 2020.</p>

That concentration is what a crash hedge should look like: the rule costs
little in normal years and pays in the few episodes that matter. It also means
the evidence rests on a handful of crashes. The Sharpe gain has a
block-bootstrap standard error of about 0.10 per schedule, and the timing part
about 0.08.

A slow state has a cost as well. The overlay gave up about 3.5 points in 2008,
cutting a momentum lean that was still earning. In 2020 momentum volatility
had been high since late 2019, so the overlay cut the lean while the baseline
book was still making money (+5.3 points from the March low to 6 November),
costing about 1 point, and then gained 3.5 points in the vaccine week.

The rule is not sensitive to its details. A 63-session volatility window, a
rolling three-year median instead of the expanding one, and 12-0 momentum
instead of 12-1 all give 1.53; using the market-volatility ramp as the state
gives 1.54. Two versions are weaker. Volatility scaling gives 1.48 because it
removes less, and measuring the lean against 6-1 momentum gives 1.43, because
6-1 overlaps much less with what the ranking actually holds.

## The learned model buys return with a different bet

The learned interactions reach the same Sharpe as the overlay, 1.55, by a
different route. Centring the state lets the model raise its momentum weight
in calm markets while it cuts it in turbulent ones, so the score's calm-market
momentum lean rises from about 0.36 to 0.50. Return is higher (11.5% against
10.6%), but so are volatility and drawdown (13.3%). The worst drawdown moves
to autumn 2008, when the composite state cut momentum while it was still
earning, and 2007 and 2009 contribute 72% of the gain.

It also depends on the state. With market volatility alone it reaches 1.42,
with momentum volatility 1.45, with the Daniel–Moskowitz bear × volatility
state 1.39, and I chose the composite after comparing four. A single momentum
× state term instead of fifteen trend terms does not work for Ridge (1.30–1.35).

Putting the overlay on top of the learned scores gives the best Sharpe in
Table 2, 1.67. I would not take that number at face value: I tried this
combination after seeing the single-layer results, and among about 40 Ridge
variants the best should look good by selection alone. The expected maximum of
40 variants with this spread is about 1.52. The combination also overshoots:
on crash days the book now makes 9.9 points, which means it is net short
momentum when momentum is volatile. That is a new bet, not the removal of an
old one.

## The optimizer cap is the steadiest and the smallest

The cap works on the portfolio rather than the scores. It only binds when the
tilt would exceed the bound, it has the shallowest maximum drawdown in Table 2
(11.4%), and its gain is even across schedules (+0.14 to +0.17). But it adds
0.13 to 0.15 in Sharpe, cuts crash-day losses only to 8 points, and adds
nothing once the overlay is in place (1.54 with both). It works as a guardrail
on the portfolio; the fix itself belongs in the scores.

Two ideas from the literature did not help here. A Daniel–Moskowitz state,
bear market times market volatility, adds only 0.04 as an overlay: the
two-year market return was negative on about a fifth of the days, in
2001–2003 and 2008–2010, and the state was off through 2020. Neutralizing only
the loser leg adds 0.08, less than the symmetric version at the same strength
(+0.10).

<table class="research-table comparison-table">
  <caption><strong>Table 3: The main Ridge variants.</strong> Development period, net of 5 bp, mean Sharpe over the three schedules; the baseline is 1.32. λ scales the state; ramp states rise from 0 to 1 between the 50th and 90th expanding percentile of the underlying volatility.</caption>
  <thead><tr><th>Variant</th><th>Net Sharpe</th></tr></thead>
  <tbody>
    <tr><th scope="row">Constant shrink 0.16 / 0.35 (no timing)</th><td>1.35 / 1.41</td></tr>
    <tr><th scope="row">Overlay, bear market × market volatility, λ 0.5</th><td>1.35</td></tr>
    <tr><th scope="row">Overlay, loser leg only, λ 0.5</th><td>1.40</td></tr>
    <tr><th scope="row">Overlay on all 17 trend characteristics, λ 0.5</th><td>1.41</td></tr>
    <tr><th scope="row">Overlay, market / momentum volatility ramp, λ 0.5</th><td>1.42 / 1.43</td></tr>
    <tr><th scope="row">Overlay, volatility scaling \(1-1/g_t\)</th><td>1.48</td></tr>
    <tr><th scope="row">Overlay, market / momentum volatility ramp, λ 1</th><td>1.54 / 1.55</td></tr>
    <tr class="selected-rule"><th scope="row">Overlay, variance scaling \(1-1/g_t^2\)</th><td>1.54</td></tr>
    <tr><th scope="row">Hand-set shrink of the fifteen trend bets</th><td>1.48</td></tr>
    <tr><th scope="row">Learned, bear × volatility / market volatility / momentum volatility</th><td>1.39 / 1.42 / 1.45</td></tr>
    <tr><th scope="row">Learned, composite state</th><td>1.55</td></tr>
    <tr><th scope="row">Optimizer cap \(0.45/g_t\) / \(0.45/g_t^2\)</th><td>1.45 / 1.47</td></tr>
    <tr><th scope="row">Overlay + cap</th><td>1.54</td></tr>
    <tr><th scope="row">Learned + cap / learned + overlay</th><td>1.60 / 1.67</td></tr>
  </tbody>
</table>

## Remove momentum when momentum is volatile

For the Ridge strategy I would keep the score overlay. It has no fitted
parameter, it was fixed before I saw its result, it sits between the Ridge
predictions and the optimizer without touching either, and it improves return
and risk together: Sharpe from 1.32 to 1.54, maximum drawdown from 15.5% to
11.9%, and almost no loss when momentum crashes. About 0.09 of the gain comes
from holding less momentum and 0.13 from timing, most of it in 2009 and 2020,
so I would plan on a gain nearer 0.1 to 0.15 than 0.22. The learned model and
the combination earn more return by taking a different, more concentrated bet,
and the optimizer cap is a guardrail.

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
