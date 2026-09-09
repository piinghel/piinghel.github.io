---
layout: post
title: "Understanding Your P&L"
description: "Understanding a strategy through its changing exposures, sources of return, drawdowns and individual positions."
permalink: /quants/portfolio-attribution.html
toc: true
show_date: false
published: false
navigation: false
---


<p class="article-summary">I work through my strategy's P&L, from the long and short books down to individual stocks, then take a closer look at its two worst drawdowns.</p>

A profitable backtest leaves me with plenty of questions. Which positions
made the money? What were the shorts doing? And when the strategy struggled,
were its usual bets letting it down?

I'll use the long–short equity strategy from my
[optimizer article](/quants/2026/08/29/portfolio-optimization.html).
It ranks stocks with a prediction model and sizes positions within risk limits.
The history runs from **23 September 1998 to 27 May 2026**. One **P&L point**
means 1% of the same fixed strategy notional throughout.

<details>
<summary>Backtest assumptions</summary>
<div markdown="1">

The backtest uses real market data and history already used to help choose
the model. It charges five basis points on traded notional and excludes
borrow, financing and market impact. Long and short contributions use the same
notional, with costs recorded separately for the portfolio.

</div>
</details>

## Start with the long and short books

Let's start with something simple: add up the P&L from each side. Across the
full history, longs earned **444.27 points**, shorts lost **93.17**, and trading
costs took another **38.18**. That leaves **312.92 points net**.

The gap between the long and net lines in Figure 1 is hard to miss. The long
book made more than the portfolio kept after short losses and costs.


<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/whole-history" mobile="/_draft_assets/portfolio-attribution/whole-history_mobile" version="3" alt="Full-history cumulative long, short and net contributions above the daily net drawdown, with the 2008–09 and 2020–21 declines shaded." %}
</div>
<p class="figure-caption"><strong>Figure 1: The longs carried the accumulated result.</strong> Cumulative fixed-notional P&amp;L and its drawdown, September 1998–May 2026. Longs and shorts are gross; net includes trading costs. Shading marks the two deepest peak-to-trough declines.</p>


Was the short book losing money all along? Table 1 gives a more mixed picture:
shorts added 5.12 points in 2000–04, but lost 54.89 in 2010–14.


<div markdown="1">
<p class="table-caption"><strong>Table 1: How the two books contributed over time.</strong> P&amp;L points. ¹Partial blocks at the beginning and end of the sample; totals are not annualized.</p>

| Period | Longs | Shorts | Costs | Net |
| :--- | ---: | ---: | ---: | ---: |
| 1998–99¹ | +31.84 | −8.45 | −1.74 | +21.66 |
| 2000–04 | +67.61 | +5.12 | −7.77 | +64.97 |
| 2005–09 | +57.41 | −14.98 | −7.54 | +34.88 |
| 2010–14 | +112.99 | −54.89 | −7.03 | +51.08 |
| 2015–19 | +87.54 | −5.35 | −6.36 | +75.83 |
| 2020–24 | +69.39 | −13.74 | −6.15 | +49.51 |
| 2025–26¹ | +17.48 | −0.87 | −1.61 | +15.00 |
{: .research-table .comparison-table .attribution-table }

</div>


I'd want to understand that drag before changing the strategy. The shorts also
change its exposures and can help when markets fall. I'll look at what that
protection amounted to during the drawdowns.

<details>
<summary>How a position becomes P&L</summary>
<div markdown="1">

For a stock held over a return interval, its contribution is

$$
c_{i,t}=w_{i,t^-}r_{i,t},
$$

where $$w_{i,t^-}$$ is its signed starting dollar exposure divided by strategy
notional. A short has a negative weight, so a rising stock produces a loss.
Adding contributions across stocks and subtracting costs gives that day's
portfolio P&L. I then add the daily values across the period.

Holdings and returns must cover the same interval, with consistent treatment
of corporate actions. Trading within an interval needs its own accounting;
a final position multiplied by the whole period's return won't reconstruct
what the portfolio earned along the way.

</div>
</details>

## Which sectors made money?

Now let's group the stocks by sector and add up their P&L across both books
(Figure 2). No model is needed for this step.

**Every sector contributed positively before costs over the full history.**
Technology led with **63.45 points**, followed by Consumer Discretionary
(**55.08**) and Industrials (**49.34**). Energy contributed the least at
**2.32 points**, followed by Materials at **5.19**.


<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/sector-pnl" mobile="/_draft_assets/portfolio-attribution/sector-pnl_mobile" version="3" alt="All eleven full-history sector contributions, ranked from Technology at plus 63.45 points to Energy at plus 2.32 points." %}
</div>
<p class="figure-caption"><strong>Figure 2: Where the stock P&L came from.</strong> Gross contributions across both books, September 1998–May 2026, on the same fixed notional. Costs remain at portfolio level.</p>


The totals are positive largely because long gains outweighed short losses.
In Energy, for example, longs earned **17.64 points** and shorts lost **15.33**.
Only Communications and Consumer Staples had positive short-book contributions
over the full history.

Position size and time held both affect these totals. A sector can contribute
more simply because I held more of it. I'm also using retrospective
classifications to group the history; the labels may differ from those used
at the time.

## Which stocks stand out?

Let's put names to those totals. Table 2 lists the five biggest winners
and losers across the full history.


<div markdown="1">
<p class="table-caption"><strong>Table 2: The five best and five worst stock contributions.</strong> Gross P&amp;L points across both books. Names identify the securities in the reference data and may reflect later corporate changes.</p>

| Stock | Sector | P&L |
| :--- | :--- | ---: |
| Apple | Technology | +5.59 |
| Computer Sciences | Technology | +4.34 |
| Amazon.com | Consumer Discretionary | +3.48 |
| Microsoft | Technology | +3.27 |
| VMware | Technology | +3.02 |
| United States Steel | Materials | −3.99 |
| Continental Resources | Energy | −3.21 |
| Tesla | Consumer Discretionary | −2.95 |
| Match Group (old listing) | Communications | −2.85 |
| Brocade Communications Systems | Technology | −2.66 |
{: .research-table .comparison-table .attribution-table  .stock-table }

</div>


Apple contributed **5.59 points**, almost entirely from the long side.
For VMware, **2.68 of its 3.02 points** came from shorts.
Among the losers, Tesla's **−2.95 points** also came almost entirely from
short positions.

Four of the five largest winners were Technology stocks. So was Brocade,
one of the biggest losers. The stock table exposes weak spots inside an
otherwise profitable sector.

## What did the shared exposures contribute?

Several stocks can lose money for similar reasons. Were my positions tilted
towards larger companies, recent winners or lower-volatility stocks, and what
did those tilts earn? This is where I bring in a **factor model**.

Here's how I calculate the split:

1. Describe each stock using its prior-day characteristics, or **loadings**.
2. Fit that day's stock returns across the eligible universe, with all factors
   in the regression together. The fitted coefficients are the day's
   **factor returns**; what remains for each covered stock is its **residual**.
3. Multiply each stock's signed starting weight by its loading and the factor
   return, then add across stocks and days.

$$
c_{i,k,t}=w_{i,t^-}b_{i,k,t^-}\widehat f_{k,t},
\qquad
C_k=\sum_t\sum_i c_{i,k,t}.
$$

Figure 3 applies this to the full history. Momentum contributed **23.10 points**,
volatility **20.26** and reversal **17.94**. Beta (**−15.13**) and size
(**−5.99**) detracted. The largest component was the **residual, +198.82 points**:
the part of covered stocks' returns left after fitting the model.


<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/factor-pnl" mobile="/_draft_assets/portfolio-attribution/factor-pnl_mobile" version="3" alt="Full-history attribution with common intercept, five style factors, sector effects, residual, uncovered holdings, reconciliation and trading costs." %}
</div>
<p class="figure-caption"><strong>Figure 3: A factor view of the same full-history P&L.</strong> All contributions sum to +312.92 points net. Sector effects are the model terms, distinct from grouping complete stock P&amp;L by sector. Uncovered holdings and costs remain explicit.</p>


The model's common intercept contributed **84.09 points**. Every covered stock
has a loading of one on that term, so its portfolio exposure is the net dollar
weight of those stocks. A positive net dollar weight gives positive intercept
*exposure*; the sign of its P&L still depends on the fitted daily return.

This is where I need to be careful with the labels. Intercept exposure, a
standardized beta tilt and beta to a market index describe different things.
The other factor components can offset the intercept's market sensitivity.
I keep the intercept in the factor split and assess the portfolio's benchmark
sensitivity separately.

The large residual is encouraging, but I'd want to know what the model missed
before crediting it to stock picking. The model covered about **93.1%** of gross
exposure on average; holdings outside that coverage earned another **22.49
points**, shown separately. I'll come back to how much confidence I can put in
the split after looking at the losses.

<details>
<summary>How the pieces add back to the portfolio</summary>
<div markdown="1">

For a covered stock, the fitted decomposition is
$$r_{i,t}=\sum_k b_{i,k,t^-}\widehat f_{k,t}+\widehat\varepsilon_{i,t}$$.
Multiplying by its signed weight gives

$$
w_{i,t^-}r_{i,t}
=\sum_k c_{i,k,t}+w_{i,t^-}\widehat\varepsilon_{i,t}.
$$

Think of a grid with one row per stock, one column per factor, and a final
residual column. Adding across a row gives that stock's contribution. Adding
down a factor column gives that factor's portfolio contribution. Grouping rows
by sector gives another view of the same money; adding the sector totals to
the factor totals would count it twice.

For the whole portfolio I also retain uncovered stocks, costs and any difference
between the model's return basis and the accounting P&L. The reconciliation
difference here is negligible. Keeping it visible prevents a price or timing
mismatch from being mistaken for a stock-selection result.

</div>
</details>

<details>
<summary>What is fitted, and where does the risk model enter?</summary>
<div markdown="1">

For one day, stack stock returns in $$r$$ and prior-day loadings in $$B$$.
The fitted decomposition is

$$
\begin{aligned}
r&=B\widehat f+\widehat\varepsilon,\\
\widehat f&=\arg\min_{f\in\mathcal F}(r-Bf)^\top W(r-Bf).
\end{aligned}
$$

Here $$W$$ controls how much each stock matters in the fit. This example uses
square-root market-cap weights. The fit includes a common intercept and sector
effects constrained to have a weighted mean of zero; $$\mathcal F$$ denotes
that constraint. Without it, the intercept and the full set of sector indicators
would not give a unique set of coefficients. The intercept is the model's common
baseline; it is not the return
of a traded market index. Different universes, regression weights or factor
definitions can change the attribution.

Because each covered stock has intercept loading one, portfolio intercept
exposure is $$\sum_i w_i$$ on that covered set. Raw holdings beta instead is
$$\sum_i w_i\beta_i$$, using stock betas to the same named benchmark. Unequal
long and short dollars can therefore offset in beta. The standardized beta
loading used in this fit is different again. I keep the intercept contribution
in the factor split: moving it into residuals would change what "residual"
means, without improving the explanation of market sensitivity.

The factor returns are estimated **after** observing that day's stock returns.
Using today's return as the outcome is appropriate for explaining today's P&L;
using it to build yesterday's exposure or risk forecast would introduce look-ahead.
This is a cross-sectional fit across stocks each day, rather than a regression
of the portfolio's return history on factor returns.

To forecast portfolio risk, I also need a factor covariance matrix $$\Omega_f$$
and a residual covariance matrix $$D$$. Under the model's assumption that factor
and residual shocks are uncorrelated,

$$
\begin{aligned}
\Sigma&=B\Omega_f B^\top+D,\\
\sigma_p&=\sqrt{w^\top\Sigma w}.
\end{aligned}
$$

The covariance estimates give more weight to recent returns and use return
history through the previous session. But the sector classifications are
retrospective, so this is not a fully point-in-time test of risk forecasts.
The model assumes $$D$$ is diagonal: residual shocks in different stocks are uncorrelated.
That assumption can miss risk if the model leaves a shared driver unexplained.
The ordinary P&L split above uses realized factor returns; the covariance
estimates answer the additional question of how risky the positions were.

*Elements*, §14.1, also stresses that holdings must match the return interval.
If the portfolio trades within it, a single snapshot cannot explain all P&L.
The difference can include trading gains and losses as well as costs.

</div>
</details>


<details>
<summary>Net dollars and historical market sensitivity</summary>
<div markdown="1">

Over September 1998–May 2026, beginning net dollar exposure averaged **+22.0%**
of notional. Regressing daily net fixed-notional P&L on the Russell 1000
price-return benchmark, with a constant, gives a slope of **+0.068**.
The intercept component's slope is **+0.249**, offset by **−0.181** from the
remaining components. The regressions use the same 6,962 dates and denominator,
so those slopes add up.

The five-year blocks from 2000 through 2024 have net slopes between **+0.039
and +0.078**. This is low historical sensitivity for changing holdings; it
doesn't establish the beta of each day's positions before trading.

</div>
</details>

## How have the exposures changed?

Before looking at the losses, I want to see how much of each bet I was taking.
Figure 4 tracks monthly average standardized exposures across the full history.


<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/whole-exposures" mobile="/_draft_assets/portfolio-attribution/whole-exposures_mobile" version="3" alt="Four full-history panels for standardized size, momentum, volatility and beta exposures." %}
</div>
<p class="figure-caption"><strong>Figure 4: The portfolio has persistent tilts, with changing sizes.</strong> Monthly mean signed exposures, September 1998–May 2026, on fitted holdings without rescaling missing positions. Zero means no net loading on that characteristic; each panel has its own vertical scale.</p>


The strategy usually favours larger stocks and takes a negative volatility
tilt. During a drawdown, I want to know whether those bets became larger or
their returns turned against me. Figure 4 gives me the exposure side of that
comparison; the factor P&L tells me what those exposures earned.

<details>
<summary>Comparing P&L with contribution to risk</summary>
<div markdown="1">

A component can earn money over a period while making day-to-day portfolio
P&L more variable. To measure its contribution to realized volatility, I use

$$
RC_k=\sqrt{252}\,
\frac{\widehat{\operatorname{Cov}}(c_k,r_p)}{\widehat\sigma(r_p)}.
$$

The covariance measures how its daily contribution moves with total daily
P&L. Signed contributions sum to annualized portfolio volatility when all
components, including costs, use the same dates. A negative contribution
means the component offset some observed variation. The expression is
undefined when portfolio volatility is zero.

This describes the realized path with changing holdings. Forecast risk applies
the covariance model available at a decision date to the holdings then in
place, using $$\sqrt{w^\top\Sigma w}$$.

</div>
</details>

<details>
<summary>What changes when factors move together?</summary>
<div markdown="1">

For a fixed portfolio with factor exposures $$e$$ and factor covariance
$$\Omega_f$$, its factor-P&L sensitivity to factor $$k$$ is

$$
\beta_{p,k}^{\mathrm{factor}}
=\frac{(\Omega_f e)_k}{(\Omega_f)_{kk}}.
$$

When that factor has positive variance, this can be nonzero even if $$e_k=0$$.
The other exposures enter through their covariance with it. It is a linear
sensitivity, not evidence that the factor caused every associated move.

The chapter's **maximal attribution** uses these correlations to collect the
modeled P&L associated with a chosen factor or group, including the part carried
through other factors. It offers another way to examine the same loss; the
figures here use ordinary attribution. Individual factor totals can also change
when the model's factors are re-expressed, even while total modeled P&L and
forecast risk stay the same. That is why a factor label alone cannot settle
what economic bet was responsible.

</div>
</details>


## Now look at the two deepest drawdowns

Where did things go most wrong? I take the two deepest declines from a P&L
peak to the lowest point before recovery: **2008–09** and **2020–21**, both
just over **16 P&L points**.

The first starts after the peak on **30 July 2008** and reaches its trough on
**16 September 2009**. The second starts after **21 February 2020** and bottoms
on **27 January 2021**. But those dates don't tell me whether the damage
happened while the market was falling or after it started recovering.

To check that, I split each window at the low of the Russell 1000 price-return
benchmark: **9 March 2009** and **23 March 2020**. Table 3 shows the P&L up to
that low, then from the following session to the strategy's own trough.


<div markdown="1">
<p class="table-caption"><strong>Table 3: Did the losses come during the decline or the rebound?</strong> Portfolio P&amp;L points on fixed notional. Longs and shorts are gross; net includes costs. Sessions show the different lengths of the phases.</p>

| Phase | Sessions | Longs | Shorts | Net |
| :--- | ---: | ---: | ---: | ---: |
| 2008–09 decline | 152 | −36.28 | +30.63 | −6.18 |
| 2009 rebound | 133 | +39.59 | −49.14 | −10.14 |
| 2020 decline | 21 | −39.95 | +30.74 | −9.32 |
| 2020–21 rebound | 214 | +38.41 | −44.19 | −6.74 |
{: .research-table .comparison-table .attribution-table }

</div>


**The strategy lost in both phases, in both episodes.** Shorts helped during
the declines, but didn't fully offset the long losses. During the rebounds,
short losses exceeded the long gains. Figure 5 lines up the market path and
portfolio contributions so I can see when that change happened.


<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/market-phases" mobile="/_draft_assets/portfolio-attribution/market-phases_mobile" version="2" alt="Benchmark levels above cumulative long, short and net P&L, split at the March 2009 and March 2020 market lows. The strategy continues losing during the rebounds." %}
</div>
<p class="figure-caption"><strong>Figure 5: The market rebounded while the strategy lost further ground.</strong> Each window runs from the strategy's peak to its trough. Shading ends at the benchmark low. Benchmark price indices start at 100; portfolio contributions use fixed-notional P&amp;L points on separate axes. Corresponding panels share scales.</p>


<details>
<summary>How I choose and measure the drawdowns</summary>
<div markdown="1">

Let $$r_{p,t}$$ be daily net P&L divided by fixed notional. Its cumulative
path and drawdown are

$$
A_t=\sum_{s\le t}r_{p,s},
\qquad
D_t=A_t-\max(0,A_1,\ldots,A_t).
$$

An episode ends when the prior peak is regained. I rank those distinct episodes
by their deepest $$D_t$$, so several bad days in the same decline don't occupy
both places. The loss attribution starts after the peak and ends at the trough.
The strategy eventually regained its prior P&L peak on 22 September 2010 and
30 April 2021, respectively.

These are additive P&L drawdowns on fixed notional. Compounding the daily
series selects the same two episodes but reverses their order. I keep the
additive convention so the book, stock and factor contributions add directly
to the loss being explained.

Within each window, the market low is the minimum compounded benchmark level.
The decline includes that session; the rebound starts on the next one. These
dates are selected with hindsight. The window starts at the strategy's peak,
which need not be the market's peak, and a rebound need not regain the market's
previous high.

Moving the split five sessions earlier or later leaves both phases negative
in both episodes. The 2008–09 rebound still loses more. In 2020–21, which phase
has the larger total loss changes with that boundary, so I wouldn't make much
of that ranking. These are two selected episodes, not a tested market-timing rule.

</div>
</details>

### 2008–09: more damage during the rebound

The benchmark fell **47.73%** from the strategy's July peak to 9 March 2009,
then rose **59.69%** through 16 September. The shorts cushioned the fall,
but gave back more than the longs earned during the rebound. The strategy
lost **6.18 points before the market low and another 10.14 afterwards**.
Here, more of the damage accumulated after the market had bottomed.

Over the whole peak-to-trough window, **Industrials lost 7.66 points**, followed by Communications
(**2.47**) and Materials (**1.93**). Industrial losses came from both books:
**−1.93 from longs** and **−5.73 from shorts**. TE Connectivity (**−0.78**),
RR Donnelley (**−0.75**) and CSX (**−0.60**) were its three largest losing
stock contributions.

Technology, which led the full-history gains, also helped over this window
with **+2.03 points**. Industrials did the opposite: a large long-run contributor
became the biggest losing sector in this episode.

### 2020–21: a sharp decline, followed by further losses

The benchmark fell **33.79%** through 23 March 2020. The strategy lost **9.32
points in just 21 sessions**: the short gains weren't enough to offset the
long losses.

The market then rose **73.03%** through 27 January 2021, while the strategy
lost another **6.74 points over 214 sessions**. The initial decline was much
sharper; the rebound added a slower, prolonged loss. So I can't explain this
episode simply as shorts getting caught by a recovery.

Across the full 2020–21 window, **Financials lost 9.83 points**, with almost equal losses
from longs (**−4.93**) and shorts (**−4.89**). Real Estate lost **3.16** and
Consumer Discretionary **2.20**. Within Financials, Rithm Capital (**−1.16**),
KeyCorp (**−1.08**) and State Street (**−0.81**) were the largest losers,
all from long positions.

Caesars was the largest individual stock loss in the whole episode at
**−2.36 points**, also almost entirely from longs. So the fact that shorts
lost more in aggregate doesn't mean the worst individual positions were shorts.

## Was I just holding on to the old shorts?

One explanation would be that the stocks I shorted during the decline bounced
back and I stayed short too long. I can test part of that story by separating
rebound P&L into names that were short at the market low and names that weren't
(Table 4).

<div markdown="1">
<p class="table-caption"><strong>Table 4: Where the rebound's short losses came from.</strong> Gross short P&amp;L points after the market low through the strategy trough. Each group includes subsequent changes in size, exits and reentries.</p>

| Short-book names | 2009 rebound | 2020–21 rebound |
| :--- | ---: | ---: |
| Short at the market low | −20.90 | −23.12 |
| Not short at the market low | −28.24 | −21.08 |
| **Total** | **−49.14** | **−44.19** |
{: .research-table .comparison-table .attribution-table }

</div>

Names absent from the short book at the low accounted for **57.5%** of its
2009 rebound loss and **47.7%** in 2020–21. Holding on to the original shorts
therefore can't explain the whole loss. I also need to understand the positions
the strategy entered or reentered during the rebound.

Was it just a handful of bad stocks? The five worst short contributors explain
only **12.4%** and **8.8%** of the respective aggregate short-book losses, before costs. The damage
was spread much more broadly. That makes shared exposures worth examining.

## Did the same factors hurt in both periods?

On average, the strategy tilted away from higher-beta and more volatile stocks.
Those tilts helped while the market fell, then hurt as it rebounded in both
episodes. But they don't explain the whole loss. Figure 6 adds up each factor
over the complete drawdown, including the residual left by the model.


<div class="research-figure responsive-figure">
  {% include theme-svg-figure.html base="/_draft_assets/portfolio-attribution/drawdown-factors" mobile="/_draft_assets/portfolio-attribution/drawdown-factors_mobile" version="3" alt="The 2008–09 and 2020–21 attribution side by side: beta and residual lead the first loss; residual and volatility lead the second." %}
</div>
<p class="figure-caption"><strong>Figure 6: Similar total losses, different factor contributions.</strong> Peak-to-trough P&amp;L points on equal scales. Each panel includes all factor terms, residual, uncovered holdings and costs, and reconciles to its net loss.</p>


In **2008–09**, beta was the largest losing style at **−6.55 points**, followed
by size (**−3.66**). The residual lost **6.14**. In **2020–21**, volatility was
the main losing style (**−8.10**), beta lost **4.53**, and the residual was
larger still at **−11.41**. Positive contributions from other terms partly
offset these losses.

To see the reversal inside those totals, take beta: its contribution went
from **+3.32 during the decline to −9.87 points during the rebound** in 2008–09,
and from **+1.27 to −5.80** in 2020–21.

Volatility tells a similar story in 2020–21. Its contribution swung from
**+0.61 to −8.71 points**, while average exposure became more negative,
from **−0.75 to −0.99**. The fitted factor return also changed sign.
Both the size of the bet and its payoff changed. A tilt that helped over the
full history could still be painful during a recovery. These are contributions
under the joint factor model; they don't establish that an exposure limit
would have improved the strategy.

The stock and factor views can also disagree within a single position.
Table 5 shows two examples. Protective Life lost through beta and overall.
Annaly lost through the volatility factor but made money overall, because
its other components more than offset that loss.


<div markdown="1">
<p class="table-caption"><strong>Table 5: A stock can lose through one factor and still contribute positively.</strong> P&amp;L points over the indicated drawdown. Stock totals are gross.</p>

| Stock / episode | Factor P&L | Stock P&L |
| :--- | ---: | ---: |
| Protective Life / 2008–09 | Beta: −0.40 | −1.29 |
| Annaly / 2020–21 | Volatility: −0.20 | +0.85 |
{: .research-table .comparison-table .attribution-table }

</div>



## How much should I trust that split?

I can add up what a stock earned from the portfolio accounting. Deciding how
much came from common factors is harder: I have to estimate that split.
*Elements*, §14.2, explains why even a sensible model leaves uncertainty here.

Think about how we estimated momentum's return. Stocks with high momentum can
also move on earnings announcements, company news and other individual events.
Across a finite set of stocks, those effects won't cancel perfectly. Some can
be picked up by the regression as momentum return. **Even a correctly specified
factor model has estimation noise.**

Here is the math for one day. Let $$r$$ be the vector of stock returns and
$$B$$ the matrix of loadings. Within the assumed model, $$f$$ is the underlying
factor return and $$\varepsilon$$ the stock-specific return. A hat marks an
estimate, and $$\eta$$ is the factor-return estimation error:

$$
\begin{aligned}
r&=Bf+\varepsilon,\\
\widehat f&=f+\eta.
\end{aligned}
$$

The estimated residual is whatever remains after subtracting the fitted factor
effects. Substituting the second equation into that subtraction gives

$$
\begin{aligned}
\widehat\varepsilon
&=r-B\widehat f\\
&=(Bf+\varepsilon)-B(f+\eta)\\
&=\varepsilon-B\eta.
\end{aligned}
$$

That last term is the important one: the error picked up by the factors is
removed from the residual. To translate it into portfolio P&L, multiply by
the signed position weights $$w$$. Call this attribution error $$\delta$$:

$$
\delta=w^\top B\eta=e^\top\eta,
\qquad e=B^\top w.
$$

For the covered positions, call the underlying factor contribution $$F=w^\top Bf$$
and the stock-specific contribution $$I=w^\top\varepsilon$$. Figure 7 shows what estimation does to
them. The same error appears twice, with opposite signs; these are **not two
independent errors**.

<div class="research-figure">
  {% include attribution-error-diagram.html %}
</div>
<p class="figure-caption"><strong>Figure 7: The split moves; its sum stays fixed.</strong> Within the assumed model, estimation adds the same amount to factor P&amp;L that it subtracts from residual P&amp;L. The error can have either sign.</p>

Getting the attribution to add up therefore cannot tell me whether either
piece is precise. If the factor-return error has covariance $$V_\eta$$, the
standard error of each portfolio attribution is

$$
s=\sqrt{e^\top V_\eta e}.
$$

This measures uncertainty in the **explanation of the P&L**. It is different
from the volatility of the portfolio's returns. Factor errors can move together,
so the off-diagonal entries of $$V_\eta$$ matter too.

The residual losses of **6.14 points in 2008–09** and **11.41 in 2020–21**
therefore need an uncertainty estimate before I judge how precisely the
model has separated them from common factors.

For the whole period, write the residual estimate as $$\widehat I_T$$ and its
attribution standard error as $$s_T$$. With zero-mean Gaussian estimation errors
and known error variance, a 95% interval takes the form

$$
\widehat I_T\;\pm\;1.96\,s_T.
$$

The same width applies to the total factor attribution under these assumptions.
The figures here show point estimates; $$s_T$$ has not been calculated for
these episodes. I can describe how the model allocates each loss, but I can't
say whether its residual estimate is distinguishable from estimation noise.
An interval entirely below zero would support a negative stock-specific
contribution under that model. A claim about persistent stock-selection skill
would need evidence across periods too.

There is a second uncertainty: **did I choose a suitable model?** Mine omits
value, quality and finer industry effects, so some common returns can end up
in the residual. An interval for estimation noise within this model would not
automatically cover those omissions. To attribute the residual loss to stock
selection, the interpretation would also have to survive a reasonable change
in factor specification. Otherwise the conclusion concerns this particular
model's unexplained return.

<details>
<summary>Computing the standard error, including across days</summary>
<div markdown="1">

The remaining ingredient is $$V_\eta$$. For weighted least squares in an
identified, full-rank factor basis, write the estimator as

$$
\begin{aligned}
A&=(B^\top WB)^{-1}B^\top W,\\
\widehat f&=Ar=f+A\varepsilon.
\end{aligned}
$$

Since $$\eta=A\varepsilon$$, residual-noise covariance $$D$$ implies

$$
V_\eta=ADA^\top.
$$

*Elements*, §14.2.2, uses generalized least squares with known $$D$$.
Setting $$W=D^{-1}$$ simplifies this to

$$
V_\eta=(B^\top D^{-1}B)^{-1}.
$$

My market-cap weighting requires the more general expression. The sector
constraint also requires working in an independent factor basis, with matching
portfolio exposures. And $$D$$ describes the underlying stock-specific noise;
it cannot simply be assumed equal to the covariance of fitted residuals, from
which the regression has already removed some noise.

One practical estimate is the **HC3 sandwich covariance**. With regression
leverage $$h_i=(BA)_{ii}$$, it uses

$$
\widehat V_{\eta,\mathrm{HC3}}
=A\,\operatorname{diag}\!\left(
\frac{\widehat\varepsilon_i^2}{(1-h_i)^2}
\right)A^\top.
$$

The leverage adjustment allows for the way fitting reduces residuals,
especially for influential observations. It permits different noise variances
across stocks, but assumes their errors are uncorrelated. Correlated omitted
drivers can still make the interval too narrow. Because this covariance is
estimated, normal intervals based on it are approximate; the exact
known-variance calculation above is a reference case. The interval also says
nothing by itself about persistent stock-selection skill. HC3 needs residual
degrees of freedom and $$h_i<1$$; otherwise the interval is unavailable.

Across days, the attribution error is $$\Delta_T=\sum_t\delta_t$$. Treating
the loadings and portfolio weights as fixed, its variance is

$$
s_T^2=\sum_t\operatorname{Var}(\delta_t)
+2\sum_{t<u}\operatorname{Cov}(\delta_t,\delta_u).
$$

If the daily estimation errors are uncorrelated, the cross-day terms vanish:

$$
s_T^2=\sum_t e_t^\top V_{\eta,t}e_t.
$$

So I add daily **error variances**, then take the square root. I don't add
standard errors or annualize the result: the interval concerns this particular
period's P&L. Dependence across days, estimated residual risks and changing
model parameters require more care. Even a well-calculated interval remains
conditional on the model and does not cover every omitted factor or mistaken
loading.

</div>
</details>



## What would I investigate next?

I'd start with two questions. First, **did changing short sizes amplify the
rebound losses?**
When a shorted stock rises, its dollar exposure grows in magnitude even without
another trade.
I'd separate that price drift from changes in effective share quantities,
then measure the P&L associated with the quantity changes. That calculation
hasn't been done here; the name-level split doesn't answer it.

Second, **were new predictions repeatedly selecting the exposures that were
hurting?** I'd inspect the predictions and ranks when those losing shorts
entered the book, then compare their factor and residual P&L with the existing
shorts. That would help me decide whether to work on the predictions, position
sizes or trading rules.

The residual deserves the same care. Once I've checked model coverage and
uncertainty, I can ask whether the stock choices were poor or I put too much
risk on the losers. The calculation below separates those two effects.

<details>
<summary>The calculation behind selection and sizing</summary>
<div markdown="1">

This is the selection/sizing identity from *Elements*, §14.4. I have not
evaluated it for these episodes.
For one date, let $$\varepsilon_i$$ be a stock's idiosyncratic return,
$$\sigma_i>0$$ its matching idiosyncratic volatility, and $$w_i$$ its signed
position weight. Define

$$
u_i=\frac{\varepsilon_i}{\sigma_i}\operatorname{sign}(w_i),
\qquad a_i=\sigma_i|w_i|.
$$

The first quantity measures the signed outcome in volatility units; the second
measures the size of the risk taken. Their product is exactly
$$u_i a_i=w_i\varepsilon_i$$. Averaging across the $$n$$ included positions,
with cross-sectional covariance defined using divisor $$n$$, gives

$$
\sum_i w_i\varepsilon_i
=\overline u\sum_i a_i
+n\operatorname{Cov}_{i}(u_i,a_i).
$$

This identity makes the question concrete. The first term uses the average
signed outcome. The second is positive when larger risk positions coincide
with better signed outcomes on that date. A hit rate discards the magnitude
of those standardized outcomes, so it answers a different question.

If idiosyncratic returns are uncorrelated under the model, the corresponding
portfolio volatility is $$\sqrt{\sum_i a_i^2}$$. Dividing the identity by it
gives a selection term multiplied by diversification,
$$\sum_i a_i/\sqrt{\sum_i a_i^2}$$, plus a sizing term. This is a
single-period risk-normalized result; a reported time-series information
ratio requires its own aggregation convention. See *The Elements of
Quantitative Investing*, §14.4.

</div>
</details>

The test of a proposed change would include other declines, rebounds and
ordinary periods, with costs. Knowing the turning points after the fact is
useful for diagnosing a loss; it doesn't tell me when I could have traded differently.

## References

Giuseppe Paleologo, [*Advanced Portfolio Management*](https://www.wiley-vch.de/en/areas-interest/finance-economics-law/advanced-portfolio-management-978-1-119-78979-6),
Chapter 8; [*The Elements of Quantitative Investing*](https://linktr.ee/paleologo),
Chapter 14.

The [dashboard source code](https://github.com/piinghel/portfolio-pnl-dashboard)
is available if you'd like to explore your own portfolio.
