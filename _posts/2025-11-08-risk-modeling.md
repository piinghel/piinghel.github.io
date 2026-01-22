---
layout: post
title: "Forecasting Volatility with Panel Regressions"
date: 2025-11-08
categories: [Quants]
---

## Introduction

I've been using simple rolling averages to forecast volatility for a while now. They work fine, but I always wondered if I was leaving money on the table.

I scale positions by predicted volatility: smaller positions in volatile stocks, larger positions in stable ones. This keeps portfolio risk roughly constant. The key word is *predicted*—I need to forecast volatility, not just measure it after the fact.

Simple heuristics are common: rolling averages of recent realized volatility, often with fixed weights across horizons. They're easy to implement, but they ignore structure in volatility dynamics. Mean reversion, clustering, sector effects, and the leverage effect all contain predictive signal that simple averages discard.

This post tries to answer two questions I've been curious about: (1) can we actually improve volatility forecasts with more sophisticated methods? And (2) do better forecasts translate to better portfolio performance?

To quantify the potential, I start with the upper bound: what if we had perfect foresight of future realized volatility? Using Russell 1000 constituents from 1995-2024—approximately 7 million date × asset observations covering roughly 1,000 stocks at any point in time—I backtest a long-short equity strategy and find that perfect volatility forecasts on the long leg alone would increase Sharpe ratio from 1.76 to 2.65—a 50% improvement. The full potential improvement is 3-4% annualized return. While perfect foresight is unattainable, this shows that better volatility forecasting could matter.

The remainder of this post evaluates both questions by comparing forecasting models, from simple moving averages to dynamic panel regressions. Spoiler: panel regression methods do improve forecast correlation compared to simple moving averages. But—and this was a bit disappointing—those improvements don't translate to better portfolio performance in this strategy.

### Application Context

The volatility forecast sits directly inside position sizing for the long-short equity strategy (see [previous post on the low-volatility factor]({% post_url 2024-12-15-low-volatility-factor %})). This is not an academic exercise for me—these forecasts feed the weights I trade.

The allocation proceeds in two stages. First, ML scores are converted into initial weights $\alpha_i$. Better predictions receive more capital on the long side; worse predictions receive more capital on the short side (weights are always positive, assigned to different legs).

Second, each position is scaled by volatility to target a fixed risk level:

$$w_i = \alpha_i \cdot \min\left(\frac{\sigma_{\text{target}}}{\hat{\sigma}_i}, \lambda_{\max}\right)$$

where:
- \\(\hat{\sigma}_i\\) = volatility forecast for stock \\(i\\)
- \\(\sigma_{\text{target}}\\) = target volatility (20% annualized)
- \\(\lambda_{\max} = 3\\) = leverage cap

If a stock has half the target volatility, its position size doubles (up to the cap). Additional constraints apply: 5% maximum per stock, total exposure ≤ 100%.

The volatility forecast $\hat{\sigma}_i$ is currently estimated with simple moving averages—20-day rolling volatility for longs, 60-day for shorts. Forecast errors directly impact position sizing:

- **Underestimated volatility** → positions too large → deeper drawdowns
- **Overestimated volatility** → positions too small → missed returns

### The Perfect Foresight Experiment

To quantify the potential value of better volatility forecasts, I run a backtest with perfect foresight. It is a thought experiment—impossible in practice—but it tells me how much is on the table.

Three scenarios are tested:
- **Current:** Rolling volatility estimates (baseline method)
- **Perfect Long:** Perfect foresight on the long leg only
- **Perfect:** Perfect foresight on both legs

**A note on the short leg:** In a long-short portfolio, combined return = long return − short return. This means you *want* the short leg return to be as low as possible—you're subtracting it. Better vol forecasts on the short leg improve its return, but since you're subtracting a bigger number, your combined return goes down. That's why "Perfect Long" can outperform "Perfect (both)".

### Long-Short Performance

![Figure 1](/assets/vol_impact/vol_impact_comparison.png)  
<p class="figure-caption"><strong>Figure 1:</strong> Long-short portfolio performance with different volatility estimation methods.</p>

### Individual Legs

![Figure 2](/assets/vol_impact/long_short_legs_comparison.png)  
<p class="figure-caption"><strong>Figure 2:</strong> Long and short legs separately—where does the improvement come from?</p>

### The Numbers

Long-short portfolio performance:

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

Perfect Long outperforms Perfect because of the short leg. With perfect vol forecasts, the short leg return improves from 0.07% to 2.77%. Since combined return = long − short, you're now subtracting 2.77% instead of 0.07%—that "improvement" costs you ~2.7% on the combined portfolio. The long leg is where better volatility forecasts actually help.

The leg-by-leg breakdown:

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

The long leg improves dramatically: +4% return, nearly double the Sharpe, half the drawdown. The short leg improves too, but it's a smaller effect—it runs at lower leverage and benefits less from accurate position sizing.

### Implications

Perfect volatility forecasts on the long leg alone would increase Sharpe ratio from 1.76 to 2.65—a substantial improvement. While perfect foresight is unattainable, this shows the economic significance of better volatility forecasting.

The remainder of this post evaluates whether panel regression methods can approach this upper bound. The analysis compares:
- Baselines: simple moving averages
- Per-asset regressions: one model per stock
- Global + sector dummies: shared dynamics, sector-specific levels
- LightGBM baseline: tree model on the same features

## Data & Exploration

### Data

I use historical point-in-time data for Russell 1000 constituents from 1995 to 2024. This gives me approximately 7 million date × asset observations, with roughly 1,000 stocks in the universe at any point in time. The point-in-time aspect is important—I only use information that would have been available at each historical date, avoiding survivorship bias.

### Data Exploration

Before building models, I want to be clear about what we are predicting. Figure 3 shows the distribution of the target variable—21-day forward realized volatility—across sectors.

![Figure 3](/assets/vol_forecasting/sector_distribution.png)  
<p class="figure-caption"><strong>Figure 3:</strong> Distribution of 21-day forward realized volatility by sector (box plots + density curves).</p>

**Sector-level differences are large.** Median volatility ranges from ~15% (Utilities) to ~30% (Energy)—a 2x spread. The distributions have similar shape across sectors (right-skewed with long tails) but differ primarily in their mean levels. Utilities and Consumer Staples cluster tightly at low volatility; Energy and Technology show wider dispersion with visible outliers. The "Unknown" sector (stocks without sector classification, a small subset) also exhibits high volatility and outliers.

**The distribution is right-skewed.** Most observations cluster at low-to-moderate volatility (10-25%), with a long tail extending to 100%+. This suggests:
1. **Sector structure matters:** Different sectors have structurally different volatility levels, motivating sector dummies in the model.
2. **Log transformation may help:** Right-skewed distributions often benefit from log-space modeling, though we test both raw and log-space specifications.

With this context in place, here are the features used in the models.

## Feature Engineering

Each feature is motivated by well‑known patterns in volatility behavior.

### Rolling Volatility

Volatility clusters—high-vol days tend to follow high-vol days. Recent realized volatility is the strongest single predictor of near-term volatility.

For each stock, I compute rolling volatility at multiple horizons:

$$
\hat{\sigma}_{i,t}^{(w)} = \sqrt{\frac{252}{w} \sum_{k=0}^{w-1} r_{i,t-k}^2}
$$

with windows $w \in \{5, 21, 63, 126\}$ days:
- **5-day:** Captures very recent shocks (earnings, news)
- **21-day:** Standard monthly volatility, balances noise and signal
- **63-day:** Quarterly horizon, smooths out short-term noise
- **126-day:** Semi-annual, provides mean-reversion anchor

In this dataset, mid‑horizon measures (21–63d) and EWM volatility are the strongest single predictors; the 5‑day window is notably weaker. Downside volatility is slightly more informative than upside volatility, which aligns with leverage‑effect intuition.

### Asymmetric Features

Volatility responds asymmetrically to returns. Bad news increases volatility more than good news reduces it—the leverage effect. I capture this with downside and upside volatility features computed over a 21-day window:

$$
\hat{\sigma}_{i,t}^{\text{down}} = \sqrt{\frac{252}{21} \sum_{k=0}^{20} r_{i,t-k}^2 \cdot \mathbf{1}_{r_{i,t-k} < 0}}
$$

$$
\hat{\sigma}_{i,t}^{\text{up}} = \sqrt{\frac{252}{21} \sum_{k=0}^{20} r_{i,t-k}^2 \cdot \mathbf{1}_{r_{i,t-k} \geq 0}}
$$

Downside volatility counts only negative return days; upside counts only positive days. If the leverage effect is present, the regression should load more heavily on downside volatility—and that is what the coefficient heatmap shows.

### Sector Dummies

Different sectors have structurally different vol levels. Utilities are stable. Energy is volatile. Tech sits somewhere in between. I add sector dummies so the model can learn these level differences while sharing the dynamics across all assets.

### Log Market Cap

Small firms are more volatile than large firms: less diversified revenue, higher leverage, lower liquidity, more idiosyncratic risk.

I include log market cap as a feature:

$$
\text{LogMktCap}_{i,t} = \log(\text{MarketCap}_{i,t})
$$

The log transformation handles the skewed distribution of market caps (a few mega-caps, many small-caps) and makes the relationship with volatility more linear.

### Data Transformations

**Clipping:** Volatility features and the target are clipped to [2.5%, 200%] during feature creation to prevent outliers from heavily impacting the model. The raw (unclipped) target is saved separately for evaluation.

**Log transformations:** We test both raw-space and log-space models. Log-transformed features (`{feature}_log`) are created for all volatility features, market cap, and the target. We never use both raw and log versions of the same feature simultaneously.

## Methodology

Here is the precise target and the modeling setup used to forecast it.

The target is 21‑day forward realized volatility, defined as:

$$
\sigma_{i,t}^{\text{fwd}} = \sqrt{\frac{252}{21} \sum_{k=1}^{21} r_{i,t+k}^2}
$$

where $r_{i,t}$ is the daily return of stock $i$ on day $t$. The factor $\sqrt{252}$ annualizes the volatility. This target is observable and directly measurable—I can compute it from realized returns. All reported metrics (RMSE, MAE, and Spearman rank correlation) are computed against the raw, unclipped target.

After feature creation, I filter to Russell 1000 constituents at each point in time, drop rows where more than 75% of features are missing, then impute missing values using a cascade: sector mean → forward fill by asset → fixed value of 0.20 as a last resort (volatility features only). Market cap uses sector mean and forward fill, with no fixed fallback. Clipping, log transformations, and saving raw targets happen during feature creation, not here.

The core of the methodology is strict walk-forward testing. For each date, I estimate coefficients on the past 504 days (2 years), then apply them to today's features. No lookahead bias—yesterday's coefficients predict today.

```
Training:    Day t-504 ──────────────────── Day t-1
Prediction:                                          Day t
```

For global models that pool all assets, I refit coefficients every 25 days rather than daily. Volatility dynamics change slowly, so daily refitting adds little benefit while dramatically increasing computation time. A ~monthly interval balances model freshness with computational efficiency.

For each date $t$, I fit a cross-sectional Ridge regression:

$$
\sigma_{i,t}^{\text{fwd}} = \beta_0 + \sum_{j=1}^{J} \beta_j X_{i,t}^{(j)} + \sum_{s=1}^{S} \gamma_s D_{i,s} + \varepsilon_{i,t}
$$

where $X_{i,t}^{(j)}$ are volatility features (5d, 21d, 63d, 126d, downside, upside) and log market cap, $D_{i,s}$ are sector dummies, and $\varepsilon_{i,t}$ is the error term.

Volatility features at different horizons are highly correlated (~0.8+), so OLS estimates become unstable when features are collinear. Ridge regression stabilizes them by adding an L2 penalty:

$$
\hat{\boldsymbol{\beta}} = \arg\min_{\boldsymbol{\beta}} \left\{ \sum_{i} \left( y_i - \mathbf{X}_i \boldsymbol{\beta} \right)^2 + \alpha \|\boldsymbol{\beta}\|_2^2 \right\}
$$

I use $\alpha = 1$. Different alpha values don't meaningfully change the conclusions, so I stick with this standard choice.

I use [polars-ols](https://github.com/azmyrajab/polars_ols)—a fast, Rust-based OLS implementation for Polars—to compute rolling regressions. The implementation differs for per-asset vs panel models:

**Per-asset regression** (simpler, faster):
```python
import polars as pl
import polars_ols

# Rolling OLS per asset - much faster, already aligned
df = df.with_columns(
    pl.col("y_target_vol_21")
    .least_squares.rolling_ols(
        pl.col("X_feature_vol_5"),
        pl.col("X_feature_vol_21"),
        window_size=504,
        alpha=1.0,
        add_intercept=True
    )
    .over("asset_id_bb_global", order_by="date")
    .alias("coefficients")
)
```

For per-asset models, `rolling_ols` with `.over("asset_id")` works because each asset is processed independently—one time series per asset. This is much faster and the coefficients are already aligned with the original DataFrame.

**Panel/global regression** (more complex, slower, especially for long windows):

For sector-level or global models, we need to pool data across multiple assets. `rolling_ols` with `.over()` cannot do this—it processes each group independently. Instead, we use `group_by_dynamic`, which pools all assets (or all assets within a sector) into each rolling window:
```python
# Build regression expression
regression_expr = pl.col("y_target_vol_21").least_squares.ridge(
    pl.col("X_feature_vol_5"),
    pl.col("X_feature_vol_21"),
    alpha=1.0,
    add_intercept=True
)

# Create time index
df = df.with_columns(
    pl.int_range(pl.len()).over("date").alias("time_idx")
)

# Compute rolling coefficients (global model, refit every 25 days)
df_coef = (
    df.sort("time_idx")
    .group_by_dynamic(
        index_column="time_idx",
        group_by=None,  # None = global (pool all assets)
        period="504i",   # 2-year window
        every="25i"     # Refit every 25 days
    )
    .agg(regression_expr.alias("coefficients"))
)

# Join, forward-fill, shift, then predict
df = df.join(df_coef, on="time_idx", how="left")
df = df.with_columns(
    pl.col("coefficients")
    .forward_fill()
    .over("asset_id_bb_global", order_by="time_idx")
    .shift(25)  # Use most recent refit coefficients (out-of-sample)
    .least_squares.predict(
        pl.col("X_feature_vol_5"),
        pl.col("X_feature_vol_21")
    )
    .alias("prediction")
)
```

The `.shift(25)` ensures predictions use coefficients estimated through the prior refit window, making them truly out-of-sample. The `coefficients` column is a struct containing intercept and betas—one expression returns fitted coefficients for all rolling windows. For example:

```
┌─────────────┬─────────────────────────────────────────┐
│ time_idx    │ coefficients                            │
├─────────────┼─────────────────────────────────────────┤
│ 504         │ {intercept: 0.05, X_vol_5: 0.3, ...}   │
│ 514         │ {intercept: 0.06, X_vol_5: 0.28, ...}  │
│ 524         │ {intercept: 0.04, X_vol_5: 0.32, ...}  │
└─────────────┴─────────────────────────────────────────┘
```

Volatility data can contain outliers—stocks that jump 10x during earnings or crash during liquidations. To prevent these outliers from heavily impacting the model, I clip volatility features and targets to [2.5%, 200%] during model training. All reported metrics are computed on raw, unclipped volatility. Final predictions are clipped to [2.5%, 200%] for visualization only.

## Results

### Forecast Quality

The central question: should we fit a model per asset or pool information across assets? The analysis builds up the answer step by step.

#### Step 1: Baselines

These are the simple rules I would use if I wanted something fast and robust:

- Simple vol‑5: 5‑day rolling volatility
- Simple vol‑21: 21‑day rolling volatility (current production baseline for longs)
- Simple vol‑63: 63‑day rolling volatility (current production baseline for shorts)
- Composite average: equal‑weighted average of 5, 21, and 63‑day rolling vol
- Weighted blend: 70% × 21‑day vol + 30% × 252‑day vol

The 21‑day and 63‑day simple vols are my current production volatility estimators, so they’re the main benchmarks I’m trying to beat.

Simple vol‑21 and vol‑63 land around 0.67–0.69, while vol‑5 lags. The composite average edges out the weighted blend (0.697 vs 0.676). Here's what the predictions look like:

![Figure 4](/assets/vol_forecasting/residuals_baseline.png)  
<p class="figure-caption"><strong>Figure 4:</strong> Predicted vs actual volatility for the weighted blend baseline.</p>

The predictions follow the diagonal but with significant scatter. Learning the weights from data instead of fixing them should improve forecasts.

#### Step 2: Per-Asset Regression

First attempt: fit a separate model for each stock. Each asset gets its own coefficients estimated on its own 2-year history.

| Model | Correlation | RMSE |
|-------|-------------|------|
| Simple vol‑5 | 0.591 | 0.235 |
| Simple vol‑21 | 0.672 | 0.199 |
| Simple vol‑63 | 0.689 | 0.190 |
| Composite avg | 0.697 | 0.189 |
| Weighted baseline | 0.676 | 0.184 |
| Per-asset regression | 0.661 | 0.191 |

<p class="table-caption"><strong>Table 3:</strong> Baselines and per‑asset regression comparison.</p>

Surprisingly, per-asset regressions actually underperform the composite baseline. With only ~500 observations per stock in a 2-year window, coefficients are noisy and the model overfits idiosyncratic patterns. More sophisticated isn't always better.

#### Step 3: Pooling Across Stocks

What if volatility dynamics are shared across assets? Mean reversion, clustering, and leverage effects should look similar across stocks, even if their levels differ.

I test pooled models (per-sector and global) and then add sector dummies so the model can share dynamics while allowing different baseline levels:

| Model | Correlation | RMSE |
|-------|-------------|------|
| Per-sector | 0.715 | 0.178 |
| Global | 0.715 | 0.178 |
| Global + sector dummies | 0.714 | 0.178 |

<p class="table-caption"><strong>Table 4:</strong> Impact of pooling across stocks.</p>

Pooling is the first real lift: correlations rise to ~0.71–0.72 across per-sector and global models. The gains are modest but consistent, and the per-sector and global results are effectively the same. I expected sector dummies to help more, but they don't on this run—the global model already captures most of the level differences.

Here's what the pooled linear model looks like compared to the baseline:

![Figure 5](/assets/vol_forecasting/residuals_best.png)  
<p class="figure-caption"><strong>Figure 5:</strong> Predicted vs actual volatility for the global + dummies model.</p>

The predictions are much tighter around the diagonal. The improvement is visible.

#### Step 4: Log-Space and Macro Factors

I tested whether log-transforming volatility or adding macro factors helps. The target is right-skewed, and market/sector factors might capture shared risk.

| Model | Correlation | RMSE |
|-------|-------------|------|
| Global + log dummies | 0.720 | 0.178 |
| + market vol factor | 0.716 | 0.179 |
| + group risk factor | 0.722 | 0.178 |

Log-space gives a small but consistent edge over the linear pooled models. The group risk factor (sector‑level volatility relative to its long‑run norm) adds a tiny improvement, while the market volatility factor adds little once asset‑level features are present. The best model is log‑space + GRF, but for simplicity I stick with log‑space + dummies.

#### Summary

![Figure 6](/assets/vol_forecasting/metrics_comparison.png)  
<p class="figure-caption"><strong>Figure 6:</strong> Comparison of all model variants across RMSE, MAE, correlation, and MAPE metrics.</p>

| Step | Model | Correlation | RMSE |
|------|-------|-------------|------|
| Baseline | Simple vol‑5 | 0.591 | 0.235 |
| Baseline | Simple vol‑21 | 0.672 | 0.199 |
| Baseline | Simple vol‑63 | 0.689 | 0.190 |
| Baseline | Composite average | 0.697 | 0.189 |
| Baseline | Weighted baseline | 0.676 | 0.184 |
| +Regression | Per-asset | 0.661 | 0.191 |
| +Pooling | Per-sector | 0.715 | 0.178 |
| +Pooling | Global | 0.715 | 0.178 |
| +Dummies | Global + sector dummies | 0.714 | 0.178 |
| +Log-space | Global + log dummies | 0.720 | 0.178 |
| +Risk factors | Global + log dummies + GRF | 0.722 | 0.178 |

<p class="table-caption"><strong>Table 5:</strong> Model development progression summary.</p>

The progression is clear: per-asset regressions are too noisy, while pooling across assets provides modest but consistent gains. Log-space gives a slight edge, and macro factors help only marginally.

#### Robustness & Validation

##### Window Sensitivity

I swept rolling windows from 6 months to 10 years. How sensitive are results to this choice?

![Figure 7](/assets/vol_forecasting/window_trends.png)  
<p class="figure-caption"><strong>Figure 7:</strong> Model performance across different rolling window sizes (252 to 2520 days).</p>

Longer windows help a bit. Correlation rises from 0.712 (252 days) to 0.728 (2048 days), with steady RMSE improvements. I use 504 days as a balance between stability and responsiveness.

##### Regime Robustness

Do models hold up when volatility spikes? Figure 8 buckets performance by market vol regime:

![Figure 8](/assets/vol_forecasting/regime_analysis.png)  
<p class="figure-caption"><strong>Figure 8:</strong> Correlation by market volatility regime—low (<20%), neutral (20-30%), high (>30%).</p>

A few observations:

1. All models improve in high-vol regimes. When vol is elevated, it's more persistent and easier to predict. During calm periods, vol is compressed and harder to differentiate.

2. The pooled model maintains its edge across regimes. The gap vs per-asset remains whether markets are calm or stressed.

3. Per-asset models suffer most in low-vol regimes. With less signal, noisy estimates hurt more. Pooling provides stability when there is less to work with.

##### Coefficient Interpretability

<iframe src="/assets/vol_forecasting/coefficient_heatmap.html" title="Figure 9" style="width: 100%; max-width: 1100px; height: 520px; border: 0; display: block; margin: 2rem auto;"></iframe>
<p class="figure-caption"><strong>Figure 9:</strong> Rolling regression coefficients over time. Red = predicts higher vol, blue = predicts lower vol.</p>

The heatmap shows which inputs consistently matter. The long‑horizon vol (126d, 63d) carries most of the signal; short‑horizon vol (5d) often flips negative, which reads as mean‑reversion. Market cap is negative as expected.
Note: this coefficient view is from the log‑space specification, so both the target and features are log‑transformed; interpret magnitudes and signs with that in mind.

Most important features:

1. 126-day vol (~0.5): Strongest positive predictor. Long-term vol acts as the mean-reversion anchor.
2. 63-day vol (~0.3): Second strongest. Bridges short-term noise and long-term structure.
3. 5-day vol (negative!): This one surprised me. It's mean-reversion in action—when short-term vol spikes above long-term, the model predicts it will come down.
4. Log market cap (~-0.1): Negative as expected. Smaller firms are more volatile.

The sector dummies tell a story:

- Energy: huge spike in 2020 (COVID oil crash, negative prices). Also elevated during 2008 and 2014-2016.
- Financials: spike in 2008-2009 (GFC). The model learned Financials needed a higher vol intercept during the crisis.
- Technology: elevated in early 2000s (dot-com bust), moderate since.
- Utilities: consistently low. Defensive stocks live up to their reputation.

Asymmetric features (downside/upside vol) both have small negative coefficients. The leverage effect is present but subtle—most asymmetry is already captured by the level dynamics.

## Conclusion

The final model: global Ridge regression in log space with sector dummies and a 2-year rolling window. It is a pragmatic choice—simple, stable, and close to the best forecasting performance in this study.

| Component | Choice |
|-----------|--------|
| Target | log 21-day forward realized vol (converted back for evaluation) |
| Features | Rolling vol (5/21/63/126d), downside/upside vol, log market cap, sector dummies (log-transformed) |
| Model | Ridge regression (α=1) |
| Estimation | 2-year rolling window |
| Pooling | Global (all assets) |
| Implementation | polars-ols for fast rolling regressions |

<p class="table-caption"><strong>Table 6:</strong> Final model specification.</p>

The key insight is that volatility dynamics are shared across assets. Per-asset models waste data chasing idiosyncratic noise. Global and per‑sector models perform almost identically, suggesting shared dynamics dominate.

This lines up with the global evidence in [How Global is Predictability? The Power of Financial Transfer Learning](https://ssrn.com/abstract=4620157) and AQR’s [Risk Everywhere: Modeling and Managing Volatility](https://www.aqr.com/Insights/Research/Working-Paper/Risk-Everywhere-Modeling-and-Managing-Volatility), both of which emphasize shared structure and the benefits of panel‑style risk forecasting.

We started with two questions: can we improve volatility forecasts, and do better forecasts translate to better performance? The best pooled models lift forecast correlation from ~0.70 to ~0.72. That's real signal. But here's the honest conclusion: in this strategy, it still doesn't translate to better portfolio performance. I was hoping for more. The gains are modest, which suggests we likely need more informative features and more powerful models to move the needle.

## What's Next

The next step is to test these forecasts directly inside the position‑sizing pipeline and measure the impact on portfolio performance. I still need to run that experiment—it's the one that actually matters.

After that, I want to add event‑timing features—especially days to earnings—as a potential driver of short‑horizon volatility. I also want to explore richer feature sets and more flexible models to capture interactions and non‑linearities. Finally, the natural extension is to optimize a loss aligned with risk‑adjusted returns or forecast the specific components that drive position‑sizing errors.

Related reading: [How Global is Predictability? The Power of Financial Transfer Learning](https://ssrn.com/abstract=4620157); [Risk Everywhere: Modeling and Managing Volatility](https://www.aqr.com/Insights/Research/Working-Paper/Risk-Everywhere-Modeling-and-Managing-Volatility). These are related, and both point to a similar theme: adding more data and sharing information across assets tends to help, but the gains are incremental.

