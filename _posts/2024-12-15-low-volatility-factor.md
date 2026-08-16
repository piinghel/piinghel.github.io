---
layout: post
title: "The Low-Volatility Factor: Portfolio Construction Matters"
date: 2024-12-15
last_modified_at: 2026-08-16
categories: [Quant]
---

The low-volatility effect is one of the most persistent results in the empirical asset-pricing literature. Low-risk equities have historically delivered much stronger returns per unit of risk than their high-risk peers. The evidence is well established: [Blitz and van Vliet](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865) documented the effect across the US, Europe, and Japan, and a large literature on defensive equities has followed.

The anomaly is striking because higher total volatility has historically come with little additional average return, leaving low-volatility stocks with unusually strong Sharpe ratios. Closely related evidence shows that the empirical security market line is too flat. Total volatility and market beta are distinct signals with substantial overlap in equity cross-sections. The resulting high Sharpe can still correspond to modest unlevered returns. An investor targeting a higher absolute return or volatility level must then apply leverage.

That observation motivates one influential economic explanation. Many institutional and retail investors are leverage constrained. Instead of levering a high-Sharpe, low-risk portfolio, they reach for high-beta securities that provide more market exposure per dollar of capital. [Frazzini and Pedersen](https://www.nber.org/papers/w16601) formalize this mechanism and construct a betting-against-beta factor that leverages low-beta assets and shorts high-beta assets.

So the low-volatility factor is easy to state but less trivial to capture. Suppose we run a cross-sectional volatility sort, buy the lowest-volatility decile, and short the highest. How should we allocate notional across the two legs? How much gross leverage do we want? And should the portfolio target dollar neutrality, beta neutrality, or matched leg risk?

A natural first implementation is 100% long the low-volatility basket and 100% short the high-volatility basket. This portfolio satisfies dollar neutrality, a non-negotiable constraint for some mandates. Its standalone leg risks remain sharply asymmetric: in my sample, the long leg realizes 12.1% annualized volatility while the short leg realizes 39.8%.

This exercise uses a well-known factor to study a focused implementation question: how does the same cross-sectional signal behave when equal stock weights are replaced by explicit stock-level risk scaling?

The analysis proceeds in two stages. I first run a conventional equal-weight, dollar-neutral long/short portfolio and decompose its risk. I then hold the selection rule fixed and change only the position sizing. I track gross and net notional, ex-ante and realized beta, turnover, drawdowns, and a small transaction-cost sensitivity. The question is: **what comes from the factor spread, and what comes from the chosen risk budget?**

## What exactly are we sorting?

The sample starts in 1995 and ends in October 2024. At every weekly signal date, I take the most recent complete Russell 1000 constituent snapshot available in the dataset and map it to the trading calendar. This point-in-time universe step matters. Using today's members throughout the history would quietly remove many companies that disappeared and would give the backtest information it could not have known at the time.

I remove stocks whose unadjusted price is below $5. Depending on the date, this leaves between 840 and 1,017 eligible stocks, with a median cross-section of 971 names. I also require every stock to have a valid selection signal, sizing volatility, and beta estimate before it can enter the ranking. Consequently, the two portfolio implementations and the exposure diagnostics all operate on the same cross-section.

For stock \(i\) on signal date \(t\), the selection signal is the average of three annualized realized-volatility estimates:

$$
v_{i,t}
= \frac{1}{3}\left(
\hat\sigma^{21}_{i,t}
+ \hat\sigma^{63}_{i,t}
+ \hat\sigma^{126}_{i,t}
\right).
$$

The horizons correspond roughly to one, three, and six trading months. They give a weekly strategy a more stable signal than 5- or 10-day estimates, while the 21-day component retains some responsiveness to recent changes in stock risk. The average is a deliberately simple compromise between responsiveness and stability.

All three estimates use adjusted close-to-close price returns available through the signal close. After averaging the three horizons, I clip the resulting signal \(v_{i,t}\) to 5%–200% before ranking. This keeps pathological observations from controlling the sort while leaving ordinary cross-sectional differences untouched.

I rank the eligible stocks and divide them into ten deterministic, approximately equal-sized groups. Decile 1 contains the lowest-volatility stocks and decile 10 the highest. Deciles are useful here because they keep the number of positions reasonably stable through time and avoid pretending that there is an economically meaningful absolute boundary between, say, a 24% and a 25% volatility stock. The strategy trades only the two extremes; the middle deciles are shown to understand whether the signal has a broader cross-sectional shape.

![Volatility-decile performance](/assets/2024-12-15-low-volatility-factor/decile_profile.png)

**Figure 1:** Long-only geometric return, realized volatility, and arithmetic-return Sharpe ratio by volatility decile, before transaction costs. Decile 1 contains the lowest-volatility stocks.

Figure 1 gives a more nuanced result than “low volatility wins.” Realized portfolio volatility rises steadily across the sort—an almost mechanical consequence of ranking stocks on trailing volatility. Geometric returns vary across the middle deciles, while Sharpe ratios generally deteriorate as volatility rises. The weakest risk-adjusted performance sits in the highest-volatility group.

That last group is exactly what the long/short strategy sells. It is also where the portfolio-construction problem begins.

## Keeping the timing honest

Before looking at weights, it is worth being explicit about when information enters the strategy. The signal is formed at the first market close of each week—normally Monday, or the first trading day after a Monday holiday. The portfolio trades at the following market close. Its first attributed return is the next close-to-close return after execution.

A Monday close can therefore inform a Tuesday close trade, with P&L beginning on the Tuesday-to-Wednesday return. The one-day delay puts signal formation, execution, and P&L in a transparent causal order.

Stock P&L uses the vendor's total-return field rather than adjusted-price returns. Source rows that fall outside the Russell 1000 market calendar are compounded before the data are sampled onto that calendar. Between weekly rebalances I hold fixed quantities, so the portfolio weights drift naturally with stock prices. That drift also matters when turnover is calculated later: the next trade is measured against the holdings the strategy actually arrives with, not against last week's target weights.

The complete specification is summarized below. The position-sizing and beta rows are developed in the following sections.

| Component | Specification |
|---|---|
| Sample | July 1995–October 2024 |
| Universe | Point-in-time Russell 1000 constituents; unadjusted price ≥ $5 |
| Selection signal | Mean annualized realized volatility over 21, 63, and 126 trading days |
| Cross-sectional portfolio | Ten equal-count deciles; long decile 1, short decile 10 |
| Rebalance | First market close of each week |
| Execution | Next market close; P&L starts on the subsequent close-to-close return |
| Stock sizing | 60-day volatility floored at 5%; 20% reference volatility; 4% position cap; 100% leg-gross cap |
| Beta diagnostic | 252-day estimate; minimum 126 observations; clipped to [−4, 4] |
| Cost sensitivity | 5 bps per dollar of absolute equity notional traded |

**Table 1:** Backtest specification. All signal, sizing, and beta inputs are lagged consistently with the execution schedule.

## First implementation: dollar-neutral, but risk-asymmetric

The equal-notional implementation is intentionally conventional:

* buy every stock in decile 1 with equal weight, for total long exposure of 100%;
* short every stock in decile 10 with equal absolute weight, for total short exposure of 100%.

Its target gross exposure is 200% and its target net exposure is zero. If \(r_{L,t}\) and \(r_{H,t}\) are the equal-weight returns of the low- and high-volatility baskets, the strategy return is simply

$$
r^{\text{EW}}_{p,t}=r_{L,t}-r_{H,t}.
$$

The equation constrains notional only. Portfolio variance still depends on both leg variances and their covariance:

$$
\sigma_p^2
=\sigma_L^2+\sigma_H^2-2\operatorname{Cov}(r_L,r_H).
$$

Dollar neutrality constrains the sum of the signed weights. Matching \(\sigma_L\) and \(\sigma_H\), or matching the betas of the two legs, requires additional constraints. Dollar neutrality, beta neutrality, and matched standalone leg risk are distinct portfolio objectives.

![Equal-weight long and short leg risk](/assets/2024-12-15-low-volatility-factor/naive_leg_risk.png)

**Figure 2:** Annualized realized volatility and average ex-ante beta of the equal-weight low- and high-volatility baskets, before transaction costs.

The low-volatility basket realizes 12.1% volatility; the high-volatility basket realizes 39.8%. Equal notional therefore assigns the short book more than three times as much standalone volatility. Dollar neutrality remains a valid mandate, while the risk budget requires a separate design choice.

The same mismatch appears in market exposure. Average ex-ante stock beta is approximately 0.56 in the low-volatility basket and 1.63 in the high-volatility basket. Once the latter is shorted, the dollar-neutral portfolio acquires a large negative market beta. Its full-sample realized beta is −1.18.

For an investor whose mandate is dollar neutrality, this may simply be an exposure profile to manage. For my narrower research question, however, the implementation mixes the low-volatility spread with a large short-market position: a modest-risk long book is paired with a high-risk, high-beta short book. Before costs, the strategy realizes 34.9% annualized volatility, a Sharpe ratio of 0.08, and an 85.0% maximum drawdown. Under the simple cost sensitivity below, its geometric return is −4.7% per year and the maximum drawdown reaches 89.5%.

This result combines the signal with the equal-notional sizing rule. The second implementation changes the sizing rule while holding the cross-sectional selection fixed.

## Reallocating the stock-level risk budget

I now replace equal stock weights with a simple inverse-volatility sizing rule. This standalone-risk heuristic excludes correlations and leaves the selected names unchanged. Its sole input into position size is each stock's own trailing volatility.

For sizing, I use a separate 60-trading-day annualized volatility estimate, \(\hat\sigma^{60}_{i,t}\), floored at 5%. Keeping selection and sizing conceptually separate is useful: the 21/63/126-day average decides *which* stocks belong in the extreme portfolios, while the 60-day estimate decides *how much* of each selected stock to hold.

For stock \(i\) in leg \(\ell\), the preliminary absolute weight is

$$
a_{i,t}
=\min\left(
\frac{1}{N_{\ell,t}}
\frac{20\%}{\hat\sigma^{60}_{i,t}},
\;4\%
\right).
$$

The equation has three components:

1. \(1/N_{\ell,t}\) is the equal-weight starting point for a leg containing \(N_{\ell,t}\) stocks.
2. \(20\%/\hat\sigma^{60}_{i,t}\) is the volatility multiplier. Before the cap, a stock with 10% estimated volatility receives twice its equal weight; a stock with 40% volatility receives half.
3. The 4% cap prevents an unusually low volatility estimate from creating a concentrated position.

This transparent heuristic uses the 20% reference volatility to determine the notional multiplier and the position cap to limit concentration from a low or noisy denominator.

There is one more step. If the preliminary weights in a leg sum to more than 100%, I scale them down proportionally. If they sum to less than 100%, I leave them alone. Writing \(s_\ell=+1\) for the long leg and \(s_\ell=-1\) for the short leg, the final signed weight is

$$
w_{i,t}
=s_\ell a_{i,t}
\min\left(
1,
\frac{100\%}{\sum_{j\in\ell}a_{j,t}}
\right).
$$

The 100% leg limit acts only as a cap. If a basket contains very volatile stocks, the rule may assign 30% or 40% of NAV to that leg. Renormalizing it back to 100% would undo much of the intended reduction in high-volatility-leg notional.

The procedure is **stock-level volatility scaling**: it scales standalone stock risk and caps both concentration and leg gross. Portfolio-level volatility targeting and covariance-based marginal risk contributions sit in a separate construction layer.

### Where leverage enters

The low-volatility anomaly is fundamentally a risk-adjusted return result, which makes leverage central to implementation. An investor comparing strategies at the same ex-ante volatility would normally apply a scalar to the completed weight vector:

$$
\tilde{\mathbf w}_t
= \mathbf w_t
\frac{\sigma^*}{\hat\sigma_{p,t}},
$$

where \(\sigma^*\) is the portfolio volatility target and \(\hat\sigma_{p,t}\) is a forecast of portfolio volatility. I keep this scalar at one to isolate the effect of stock-level sizing. A later portfolio layer could introduce a covariance forecast and manage total leverage explicitly.

The long and short books still create gross notional above NAV. Each stock leg is capped at 100%, and the resulting relative risk allocation remains unscaled. A broader portfolio process could then scale the full vector to a risk target subject to margin, financing, and mandate constraints.

## The resulting exposure profile

Allowing the short book to shrink creates positive net notional. This experiment prioritizes a reduction in standalone-risk asymmetry over a dollar-neutral mandate. A zero-net mandate would require a different constrained construction.

![Volatility-scaled target exposures](/assets/2024-12-15-low-volatility-factor/target_exposures.png)

**Figure 3:** Weekly target long gross, short gross, and net stock exposure after stock-level volatility scaling.

Across the sample, the low-volatility long leg averages 97.0% gross exposure. The high-volatility short averages only 34.2%. Total stock gross exposure is therefore 131.2%, while net stock exposure averages +62.8%.

Figure 3 makes that change in notional explicit. The high-volatility leg runs less gross because its constituents consume more standalone risk per dollar, producing a different allocation from the original 200% gross book.

At first glance, +63% net exposure may appear inconsistent with beta neutrality. Dollar exposure and beta exposure answer different questions:

$$
\text{Net exposure}_t=\sum_i w_{i,t},
\qquad
\hat\beta_{p,t}=\sum_i w_{i,t}\hat\beta_{i,t}.
$$

The first quantity is signed notional; the second is the weighted beta exposure. A smaller short book can offset a larger long book when the short constituents carry sufficiently high betas—which is exactly what happens in this cross-sectional sort.

## Does the portfolio require an always-on beta hedge?

I estimate each stock's beta from a rolling 252-trading-day covariance with the Russell 1000 price-index return, require at least 126 observations, and clip individual estimates to [−4, 4]. The ex-ante portfolio estimate is the weighted sum shown above. A rolling regression of strategy returns on market returns provides a separate realized-beta diagnostic.

![Beta diagnostic for the volatility-scaled portfolio](/assets/2024-12-15-low-volatility-factor/beta_diagnostic.png)

**Figure 4:** Aggregated ex-ante stock beta and rolling 252-day realized beta for the volatility-scaled portfolio. The shaded region marks beta between −0.1 and +0.1.

The average signed ex-ante beta is −0.010, and the full-sample realized beta is also approximately −0.010. Weekly exposure remains time varying: the average absolute ex-ante estimate is 0.104, and the rolling realized series moves visibly through time. Its sign changes, leaving little persistent signed market exposure over the full sample.

I leave the portfolio unhedged because the residual beta changes sign and averages close to zero. This design choice concerns an **always-on** overlay; weekly beta exposure can still be economically relevant.

A live process could activate an index overlay whenever estimated beta breaches a predefined tolerance band. That conditional rule addresses time-varying exposure more directly than a permanent hedge motivated by a near-zero full-sample average.

## A small transaction-cost sensitivity

Transaction costs remain a secondary sensitivity in this research exercise. The two implementations trade different amounts of gross notional, so a cost-free comparison would favor the higher-turnover portfolio. I charge 5 basis points for each dollar of absolute equity notional traded and include initial portfolio formation.

Turnover is measured against drifted pre-trade holdings. If a stock appreciates between rebalances, the strategy arrives with a larger weight; the next trade runs from that realized holding to the new target.

I report annual turnover as the sum of absolute weight changes. Under that convention, the equal-notional strategy turns over 31.4 times per year, compared with 19.3 times for the volatility-scaled strategy. These figures provide a relative implementation check; the 5 bps assumption is a sensitivity parameter rather than an estimate of achievable live performance.

## Comparing the two implementations

The table below puts the full comparison in one place. The 0 bp and 5 bp return columns are annualized arithmetic means; volatility, Sharpe, and drawdown use returns under the 5 bp sensitivity.

| Implementation | Return, 0 bp | Return, 5 bp | Volatility, 5 bp | Sharpe, 5 bp | Max drawdown, 5 bp | Avg. stock gross | Avg. stock net | Realized beta | Annualized turnover |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Equal-weight dollar-neutral L/S | 2.9% | 1.4% | 34.9% | 0.04 | −89.5% | 2.01 | 0.00 | −1.18 | 31.4× equity |
| Stock-volatility-scaled L/S | 7.9% | 7.0% | 9.6% | 0.72 | −41.0% | 1.31 | 0.63 | −0.01 | 19.3× equity |

**Table 2:** Daily results from July 1995 through October 2024. Volatility uses 252 trading days and Sharpe assumes a zero risk-free rate. Exposure statistics are daily averages. Realized beta is the full-sample regression beta of gross strategy returns on the Russell 1000 price-index return.

The change is economically large. Annualized volatility falls from 34.9% to 9.6%. Under the 5 bp sensitivity, Sharpe rises from 0.04 to 0.72, maximum drawdown improves from 89.5% to 41.0%, and annualized arithmetic return rises from 1.4% to 7.0%.

Costs reduce annualized arithmetic return by roughly 1.6 percentage points for the equal-notional portfolio and 1.0 point for the scaled portfolio. That gap reflects both lower turnover and the smaller gross trading requirement after volatile short positions are reduced.

![Cumulative performance by implementation stage](/assets/2024-12-15-low-volatility-factor/cumulative_performance.png)

**Figure 5:** Cumulative wealth under the 5 bp transaction-cost sensitivity, shown on a logarithmic scale.

The log-scale wealth curves show how hard it is for the equal-notional portfolio to compound through repeated large losses. Its weakness persists across the sample, while the scaled implementation compounds more steadily.

![Drawdown by implementation stage](/assets/2024-12-15-low-volatility-factor/drawdowns.png)

**Figure 6:** Drawdowns under the 5 bp transaction-cost sensitivity for both portfolio implementations.

The drawdown chart provides the clearest practical summary. An 89.5% drawdown is strategy-ending for almost any investor. The scaled portfolio still reaches a severe 41.0% drawdown, but its capital path has a very different degree of survivability.

## How much of this is really the factor?

There are two distinct empirical observations here.

First, the low-volatility decile has better risk-adjusted performance than the high-volatility decile in this sample. Figure 1 contains the evidence for that statement. The signal is simple, but the difference between the extremes is meaningful.

Second, most of the dramatic improvement between the two long/short portfolios is a construction result. The selected stocks do not change. What changes is the amount of risk allocated to them. That adjustment simultaneously alters gross exposure, net exposure, beta, turnover, costs, and the path of returns.

The 0.72 Sharpe combines the low-volatility spread with a material change in portfolio construction. The equal-weight portfolio cleanly tests an equal-dollar implementation; the scaled portfolio tests a standalone-risk-aware implementation. Comparing them isolates the importance of sizing, while Figure 1 provides the direct evidence on the underlying cross-sectional signal.

This distinction generalizes beyond low volatility. Whenever the long and short selections have structurally different risk, liquidity, or beta characteristics, equal dollars can embed a large unintended exposure. Portfolio construction determines which hypothesis the backtest is actually testing.

## Limitations

The scope is a research illustration of sizing and exposure. The scaled strategy carries roughly +63% net stock exposure and therefore falls outside a dollar-neutral mandate. The cost sensitivity covers equity trading only; borrow fees, financing, and market impact sit outside it. Missing stock returns are set to zero on 0.19% of position-days, constituent snapshots are treated as effective without an announcement lag, and the portfolios carry unconstrained sector and liquidity exposures. The headline results should be read in that scope.

## Conclusion

The equal-weight low-minus-high volatility trade satisfies dollar neutrality while carrying sharply mismatched standalone leg volatility and a large negative market beta. The combined portfolio consequently realizes 34.9% volatility and an 89.5% drawdown under the 5 bp sensitivity.

Scaling positions inversely to stock volatility reduces that asymmetry. It leaves the long book close to fully invested, allows the high-risk short book to shrink, and produces near-zero average signed market beta. The trade-off is positive net notional, and its acceptability depends on the investor's mandate.

The broader lesson is the one I want to carry into later research:

> Start with the signal, identify which risks the initial portfolio is really taking, allocate those risks deliberately, and only then judge the result.
