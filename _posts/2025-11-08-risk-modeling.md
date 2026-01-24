---
layout: post
title: "Forecasting Volatility with Panel Regressions"
date: 2025-11-08
categories: [Quants]
---

## Introduction



I have been forecasting volatility with simple rolling averages, and honestly, they work surprisingly well. I was pretty convinced that anything more sophisticated wouldn't be worth the complexity.

Then a colleague challenged me. He'd been working on volatility forecasting for futures and found real improvements over rolling averages. It got me thinking: could the same be true for equities?

Here's why this matters to me. I use volatility forecasts for position sizing: smaller positions in volatile stocks, larger positions in stable ones. Get it wrong and the errors compound directly into portfolio risk. Underestimate volatility and your positions run too large; overestimate and you leave returns on the table.

The thing is, simple rolling averages ignore structure that should be predictable. Volatility clusters, so high-vol days tend to follow high-vol days. It mean-reverts, so spikes decay back toward a long-run level. It responds asymmetrically to returns: down moves increase vol more than equivalent up moves (that's the leverage effect). And it varies systematically by sector, with Utilities calmer than Energy. A model that captures this structure should, in theory, forecast better.

So this post tries to answer two questions I've been curious about: **(1) Can we actually improve volatility forecasts with more sophisticated methods? (2) Do better forecasts translate to better portfolio performance?**

To get a sense of the upper bound, I run a perfect-foresight experiment. Using Russell 1000 stocks from 1995-2024 (~7 million observations), perfect volatility knowledge on the long leg would lift the Sharpe ratio from 1.77 to 2.41, a 36% improvement. Obviously unattainable, but it tells me the ceiling is high enough to be worth chasing.

### How I Use Volatility Forecasts

To give some context, this volatility forecast is part of a long-short equity strategy I run (see [previous post on the low-volatility factor]({% post_url 2024-12-15-low-volatility-factor %})).

The allocation works in two stages. First, I use ML scores to select positions, say the top 50 or 75 stocks for the long leg (the exact number is somewhat arbitrary). Higher-scoring stocks get higher weights, lower-scoring stocks go to the short leg with the logic reversed. These initial weights $\alpha_i$ are normalized to sum to 1 per leg, and I cap individual positions so no single stock dominates. You could also just use equal weights here; the ML weighting isn't the focus of this post.

Second, each position gets scaled by its predicted volatility:

$$w_i = \alpha_i \cdot \min\left(\frac{\sigma_{\text{target}}}{\hat{\sigma}_i}, \lambda_{\max}\right)$$

where:
- \\(\hat{\sigma}_i\\) = volatility forecast for stock \\(i\\)
- \\(\sigma_{\text{target}}\\) = target volatility (20% annualized)
- \\(\lambda_{\max} = 3\\) = leverage cap

Note that while the initial weights \\(\alpha\_i\\) sum to 1, the final weights \\(w\_i\\) do not. They're capped at 1, but in high-volatility environments (when most stocks have \\(\hat{\sigma}\_i > \sigma\_{\text{target}}\\)) the total exposure shrinks below 1. The portfolio naturally de-levers when volatility is elevated.

I also enforce a 5% max per stock. Currently, I estimate volatility with simple moving averages: 20-day rolling vol for longs, 60-day for shorts.

### The Perfect Foresight Experiment

Before diving into models, I wanted to know: how much could better volatility forecasts actually help? To find out, I run a backtest where I cheat, using the actual realized volatility that we'd only know in hindsight.

I test three scenarios:
- **Current:** Rolling volatility estimates (my baseline)
- **Perfect Long:** Perfect foresight on the long leg only
- **Perfect:** Perfect foresight on both legs

Here's something that might seem counterintuitive: **Perfect Long actually outperforms Perfect (both)**. Why? Think about how a long-short portfolio works. Your combined return is long leg minus short leg. You're subtracting the short leg's return, so you actually *want* the short leg to do poorly.

When you give the short leg better volatility forecasts, it performs better: positions are sized more accurately, it captures more return. But that "improvement" is now being subtracted from your total. In the results below, the short leg return jumps from 0.07% to 2.77% with perfect foresight. That's 2.7% you're now losing on the combined portfolio. The long leg is where better forecasts genuinely help you.

### Results

Here's what the equity curves look like:

![Figure 1](/assets/vol_impact/vol_impact_comparison.png)  
<p class="figure-caption"><strong>Figure 1:</strong> Long-short portfolio performance with different volatility estimation methods.</p>

And breaking it down by leg:

![Figure 2](/assets/vol_impact/long_short_legs_comparison.png)  
<p class="figure-caption"><strong>Figure 2:</strong> Long and short legs separately. Where does the improvement come from?</p>

### Performance Breakdown

Let's look at the actual performance. First, the combined long-short portfolio:

<div style="overflow-x: auto;">
<table style="width: 100%; border-collapse: collapse; margin: 0.5em 0;">
<thead>
<tr>
<th style="padding: 0.6em; text-align: left; border-bottom: 2px solid #333;">Scenario</th>
<th style="padding: 0.6em; text-align: center; border-bottom: 2px solid #333;">Return</th>
<th style="padding: 0.6em; text-align: center; border-bottom: 2px solid #333;">Sharpe</th>
<th style="padding: 0.6em; text-align: center; border-bottom: 2px solid #333;">Max DD</th>
</tr>
</thead>
<tbody>
<tr style="background: #fafafa;">
<td style="padding: 0.6em; border-bottom: 1px solid #eee;">Current</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">12.15%</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.77</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; color: #b00;">-11.06%</td>
</tr>
<tr style="background: #e8f5e9;">
<td style="padding: 0.6em; font-weight: bold; border-bottom: 1px solid #eee;">Perfect Long</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; color: #2e7d32; font-weight: bold;">14.91%</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; color: #2e7d32; font-weight: bold;">2.41</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; color: #2e7d32;">-8.93%</td>
</tr>
<tr style="background: #f5f5f5;">
<td style="padding: 0.6em;">Perfect</td>
<td style="padding: 0.6em; text-align: center;">11.86%</td>
<td style="padding: 0.6em; text-align: center;">1.90</td>
<td style="padding: 0.6em; text-align: center; color: #2e7d32;">-8.27%</td>
</tr>
</tbody>
</table>
</div>
<p class="table-caption"><strong>Table 1:</strong> Long-short portfolio performance (with fees). Perfect Long = perfect foresight on long leg only.</p>

The numbers confirm what I mentioned earlier: Perfect Long beats Perfect. You can see the short leg effect at work. When the short leg "improves," that return gets subtracted from your total.

Here's the leg-by-leg breakdown:

<div style="overflow-x: auto;">
<table style="width: 100%; border-collapse: collapse; margin: 1em 0;">
<thead>
<tr>
<th style="padding: 0.6em; text-align: left; border-bottom: 2px solid #333;"></th>
<th colspan="3" style="padding: 0.6em; text-align: center; border-bottom: 2px solid #333; background: #f8f8f8;">Current</th>
<th colspan="3" style="padding: 0.6em; text-align: center; border-bottom: 2px solid #333; background: #e8f5e9;">Perfect Foresight</th>
</tr>
<tr style="font-size: 0.8em; color: #666;">
<th style="padding: 0.4em; border-bottom: 1px solid #ddd;"></th>
<th style="padding: 0.4em; text-align: center; border-bottom: 1px solid #ddd; background: #f8f8f8;">Return</th>
<th style="padding: 0.4em; text-align: center; border-bottom: 1px solid #ddd; background: #f8f8f8;">Sharpe</th>
<th style="padding: 0.4em; text-align: center; border-bottom: 1px solid #ddd; background: #f8f8f8;">Max DD</th>
<th style="padding: 0.4em; text-align: center; border-bottom: 1px solid #ddd; background: #e8f5e9;">Return</th>
<th style="padding: 0.4em; text-align: center; border-bottom: 1px solid #ddd; background: #e8f5e9;">Sharpe</th>
<th style="padding: 0.4em; text-align: center; border-bottom: 1px solid #ddd; background: #e8f5e9;">Max DD</th>
</tr>
</thead>
<tbody>
<tr>
<td style="padding: 0.6em; font-weight: bold; border-bottom: 1px solid #eee;">Long</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; background: #fafafa;">12.34%</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; background: #fafafa;">1.19</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; background: #fafafa; color: #b00;">-30.11%</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; background: #e8f5e9; color: #2e7d32; font-weight: bold;">15.24%</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; background: #e8f5e9; color: #2e7d32; font-weight: bold;">1.76</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; background: #e8f5e9; color: #2e7d32;">-15.14%</td>
</tr>
<tr>
<td style="padding: 0.6em; font-weight: bold;">Short</td>
<td style="padding: 0.6em; text-align: center; background: #fafafa;">0.07%</td>
<td style="padding: 0.6em; text-align: center; background: #fafafa;">0.01</td>
<td style="padding: 0.6em; text-align: center; background: #fafafa; color: #b00;">-32.09%</td>
<td style="padding: 0.6em; text-align: center; background: #e8f5e9;">2.77%</td>
<td style="padding: 0.6em; text-align: center; background: #e8f5e9;">0.30</td>
<td style="padding: 0.6em; text-align: center; background: #e8f5e9;">-27.34%</td>
</tr>
</tbody>
</table>
</div>
<p class="table-caption"><strong>Table 2:</strong> Individual leg performance with Current vs Perfect volatility forecasts.</p>

The long leg is where the magic happens: about 3% more return, the Sharpe nearly doubles from 1.19 to 1.76, and drawdowns get cut in half. The short leg improves too, but it runs at lower leverage so the effect is smaller. And as I mentioned, that improvement actually hurts you on the combined portfolio.

### What This Tells Us

So perfect foresight on the long leg would take the Sharpe from 1.77 to 2.41, a 36% improvement. Obviously we can't achieve perfect foresight, but this tells me the ceiling is high enough to justify spending time on better forecasting methods.

The rest of this post explores whether I can get any closer to that ceiling. I'll compare:
- **Baselines:** simple moving averages (what I currently use)
- **Per-asset regressions:** fitting a separate model for each stock
- **Global + sector dummies:** pooling across stocks, with sector-level adjustments
- **LightGBM:** a tree-based model on the same features

## Data & Exploration

### Data

I use historical point-in-time data for Russell 1000 constituents from 1995 to 2024. This gives me roughly 7 million date × asset observations, with about 1,000 stocks in the universe at any point in time.

Importantly, the dataset includes stocks that later went bankrupt or got delisted. Using point-in-time constituent lists avoids survivorship bias, so I'm seeing the universe as it actually looked back then.

### Data Exploration

Before diving into features, it's worth looking at what we're actually trying to predict. Figure 3 shows the distribution of 21-day realized volatility across sectors.

![Figure 3](/assets/vol_forecasting/sector_distribution.png)  
<p class="figure-caption"><strong>Figure 3:</strong> Distribution of 21-day realized volatility by sector (box plots + density curves).</p>

A couple of things stand out. First, the shape of the distributions is similar across sectors, but the levels differ. Median vol ranges from about 15% for Utilities to 30% for Energy, a 2x spread. This suggests sector dummies could capture these level differences while the model learns shared dynamics.

Second, all sectors show the same right-skewed pattern. Most observations sit in the 10-25% range, but there's a long tail stretching past 100%. Predicting in log-space could help here, since it compresses the tail and makes the target more symmetric.

With that context, let me walk through the features I use.

## Feature Engineering

The features are straightforward. For each stock, I compute:

**Rolling volatility** at multiple horizons (5, 21, 63, 126 days):

$$
\hat{\sigma}_{i,t}^{(w)} = \sqrt{\frac{252}{w} \sum_{k=0}^{w-1} r_{i,t-k}^2}
$$

Volatility clusters, so recent vol is the strongest predictor of near-term vol. The mid-horizon measures (21-63d) turn out to be most informative; 5-day is notably weaker.

**Upside and downside volatility** over 21 days, to capture the leverage effect (down moves increase vol more than equivalent up moves):

$$
\hat{\sigma}_{i,t}^{\text{down}} = \sqrt{\frac{252}{21} \sum_{k=0}^{20} r_{i,t-k}^2 \cdot \mathbf{1}_{r_{i,t-k} < 0}}
$$

$$
\hat{\sigma}_{i,t}^{\text{up}} = \sqrt{\frac{252}{21} \sum_{k=0}^{20} r_{i,t-k}^2 \cdot \mathbf{1}_{r_{i,t-k} \geq 0}}
$$

Could have computed this for multiple windows like the regular vol, but kept it simple for now.

**Sector dummies** to capture level differences across sectors.

**Log market cap** since smaller firms tend to be more volatile.

For preprocessing, I clip features and target to [2.5%, 200%] to limit outlier impact, and create log-transformed versions to test whether log-space modeling helps.

## Methodology

With features in place, the next question is how to estimate the model. The target is 21-day realized volatility (annualized). I filter to Russell 1000 constituents, drop rows with >75% missing features, and impute the rest using sector means.

The key design choice is strict walk-forward testing. For each date, I estimate coefficients using only the past 504 days (2 years), then predict on today's features. No lookahead. For global models, I refit every 25 days to keep computation time and memory manageable.

I use Ridge regression rather than OLS because the volatility features are highly correlated (~0.8+), which makes OLS coefficients unstable. Ridge adds an L2 penalty that keeps things well-behaved. I set \\(\alpha = 1\\); other values don't change the conclusions much.

### Implementation with polars-ols

For the actual computation, I use [polars-ols](https://github.com/azmyrajab/polars_ols), a Rust-based linear regression plugin for Polars. It's incredibly fast: on my laptop (no GPU), the per-asset rolling regressions over 7 million observations take around 40 seconds, and the global panel model around 2 minutes. For this kind of workload, that's remarkable. Highly recommend it.

Here's a toy example showing both per-asset and global models. First, define your features once:

```python
import polars as pl

FEATURES = [
    pl.col("vol_5"), pl.col("vol_21"), pl.col("vol_63"), 
    pl.col("vol_126"), pl.col("log_mktcap")
]
```

For per-asset models, use `rolling_ols` with `.over("asset_id")`:

```python
df = df.with_columns(
    pl.col("target")
    .least_squares.rolling_ols(
        *FEATURES,
        window_size=504, alpha=1.0, add_intercept=True
    )
    .over("asset_id", order_by="date")
    .alias("coefficients")
)
```

For global/panel models where you pool across assets, use `group_by_dynamic`:

```python
# Build regression expression
reg_expr = pl.col("target").least_squares.ridge(
    *FEATURES, alpha=1.0, add_intercept=True
)

# Rolling coefficients, refit every 25 days
df_coef = (
    df.sort("time_idx")
    .group_by_dynamic("time_idx", every="25i", period="504i")
    .agg(reg_expr.alias("coefficients"))
)

# Join back and predict
df = df.join(df_coef, on="time_idx", how="left")
df = df.with_columns(
    pl.col("coefficients")
    .forward_fill()
    .shift(25)  # out-of-sample
    .least_squares.predict(*FEATURES)
    .alias("prediction")
)
```

The `.shift(25)` ensures predictions are out-of-sample.

## Results

Now for the part I was most curious about: do these methods actually improve forecasts?

### Baselines

I start with the simple approaches I'd reach for if I wanted something fast and robust: 5-day, 21-day, and 63-day rolling volatility, plus a composite average and a weighted blend. The 21-day and 63-day measures are what I currently use in production, so they're the benchmarks to beat. They reach correlations around 0.67-0.69.

![Figure 4](/assets/vol_forecasting/residuals_baseline.png)  
<p class="figure-caption"><strong>Figure 4:</strong> Predicted vs actual volatility for the weighted blend baseline.</p>

Predictions follow the diagonal but with significant scatter. Can we do better by learning the weights from data?

### Per-Asset vs Pooled Models

My first attempt was to fit a separate model for each stock, estimating coefficients on its own 2-year history. Surprisingly, this underperforms the simple composite baseline (0.661 vs 0.697 correlation).

This is the bias-variance tradeoff at work. Per-asset models have low bias: they fit each stock's own history well. But with only ~500 observations per stock, they have higher variance: the coefficients are noisier, which can hurt out-of-sample performance.

Pooling across assets flips this tradeoff. Global models have slightly higher bias (they assume all stocks share the same dynamics), but much lower variance (millions of observations to estimate a handful of coefficients). The variance reduction dominates. Correlations jump to ~0.715.

Interestingly, per-sector and global pooling perform almost identically. Even sector-level dynamics aren't different enough to justify separate estimation. Volatility behavior is remarkably universal.

![Figure 5](/assets/vol_forecasting/residuals_best.png)  
<p class="figure-caption"><strong>Figure 5:</strong> Predicted vs actual volatility for the global pooled model.</p>

Predictions cluster closer to the diagonal, but there's still a pattern: the model underpredicts when actual volatility is high. Linear models trained on mostly normal observations systematically undershoot extremes. This is exactly when accurate forecasts matter most for position sizing.

### Log-Space and Macro Factors

Since the target is right-skewed, I tested log-transforming both features and target. This gives a small but consistent edge (correlation up to 0.720). I also tried adding market-level volatility factors, but they contribute only marginally. For simplicity, I stick with log-space + sector dummies.

### Summary

Here's the full progression:

![Figure 6](/assets/vol_forecasting/metrics_comparison.png)  
<p class="figure-caption"><strong>Figure 6:</strong> Comparison of all model variants (correlation and RMSE).</p>

The pattern is clear: fitting a model per asset doesn't work because the coefficients are too noisy. Pooling across assets is where the gains come from (0.70 → 0.72). Log-space adds a small edge, macro factors barely move the needle.

### Robustness Checks

Before settling on a final model, I wanted to sanity-check how sensitive these results are to my choices.

On window size: I swept from 6 months to 10 years. Longer windows help slightly (correlation rises from 0.712 to 0.728), but I use 504 days as a balance between stability and responsiveness.

![Figure 7](/assets/vol_forecasting/window_trends.png)  
<p class="figure-caption"><strong>Figure 7:</strong> Model performance across different rolling window sizes (252 to 2520 days).</p>

On regime robustness: do models hold up when volatility spikes? Interestingly, all models improve in high-vol regimes. When vol is elevated, it's more persistent and easier to predict. During calm periods, everything compresses and becomes harder to differentiate. The pooled model maintains its edge across all regimes.

![Figure 8](/assets/vol_forecasting/regime_analysis.png)  
<p class="figure-caption"><strong>Figure 8:</strong> Correlation by market volatility regime: low (&lt;20%), neutral (20-30%), high (&gt;30%).</p>

### What the Coefficients Tell Us

One nice thing about linear models is you can actually see what they're doing. The heatmap below shows how the coefficients evolve over time:

<iframe src="/assets/vol_forecasting/coefficient_heatmap.html" title="Figure 9" style="width: 100%; max-width: 1100px; height: 520px; border: 0; display: block; margin: 2rem auto;"></iframe>
<p class="figure-caption"><strong>Figure 9:</strong> Rolling regression coefficients over time. Red = predicts higher vol, blue = predicts lower vol.</p>

Long-horizon vol (126d, 63d) carries most of the weight, which makes sense since it acts as the mean-reversion anchor. The 5-day vol coefficient is often negative, which surprised me at first, but it's mean-reversion in action: when short-term vol spikes above long-term, the model predicts it will come down. Log market cap is negative as expected (smaller firms are more volatile).

The sector dummies tell their own story. Energy shows a huge spike in 2020 (COVID oil crash, negative prices) and elevated coefficients during 2008 and 2014-2016. Financials spike in 2008-2009 during the GFC. Technology was elevated in the early 2000s (dot-com bust) but moderate since. Utilities stay consistently low: defensive stocks live up to their reputation.

The asymmetric features (downside/upside vol) have small coefficients. The leverage effect is present but subtle. Most of the asymmetry seems already captured by the level dynamics.

## Conclusion

So what did I end up with? A global Ridge regression in log space with sector dummies and a 2-year rolling window. It's a pragmatic choice: simple, stable, and close to the best forecasting performance I found.

| Component | Choice |
|-----------|--------|
| Target | log 21-day realized vol (converted back for evaluation) |
| Features | Rolling vol (5/21/63/126d), downside/upside vol, log market cap, sector dummies (log-transformed) |
| Model | Ridge regression (α=1) |
| Estimation | 2-year rolling window |
| Pooling | Global (all assets) |
| Implementation | polars-ols for fast rolling regressions |

<p class="table-caption"><strong>Table 7:</strong> Final model specification.</p>

The key insight is about the bias-variance tradeoff. Per-asset models overfit: low bias, high variance. They fit their own history well but don't generalize. Global models flip this: slightly higher bias (assuming shared dynamics), but much lower variance. With volatility, the variance reduction dominates because the underlying dynamics really are universal across stocks.

This aligns with [How Global is Predictability?](https://ssrn.com/abstract=4620157) and AQR's [Risk Everywhere](https://www.aqr.com/Insights/Research/Working-Paper/Risk-Everywhere-Modeling-and-Managing-Volatility), both emphasizing shared structure and panel-style forecasting.

The best pooled models lift forecast correlation from ~0.70 to ~0.72. That's real signal, though the question remains whether it translates to better portfolio performance.

With a simple linear model, we've likely squeezed out most of what we can from these features. To go further, we probably need more complexity: richer feature sets that capture non-linearities, event-driven dynamics, or regime shifts. The pooling insight tells us we have enough data to support more complex models without overfitting. The question is whether the additional signal is there to find.

## What's Next

The next step is to test these forecasts inside the position-sizing pipeline and measure the actual impact on portfolio performance. That's the experiment that really matters.

Beyond that, the bias-variance analysis points the way forward. We have enough data to support more complex models. The question is what features to add. Event-timing (days to earnings) seems promising since these are known volatility catalysts that simple rolling measures miss. Regime features might help the model adapt its predictions to different market environments. And non-linear models could capture the fat tails that linear regression systematically undershoots.

## References

- [How Global is Predictability? The Power of Financial Transfer Learning](https://ssrn.com/abstract=4620157) - O. Hellum, L.H. Pedersen, A. Rønn-Nielsen
- [Risk Everywhere: Modeling and Managing Volatility](https://www.aqr.com/Insights/Research/Working-Paper/Risk-Everywhere-Modeling-and-Managing-Volatility) - T. Bollerslev, B. Hood, J. Huss, L.H. Pedersen

