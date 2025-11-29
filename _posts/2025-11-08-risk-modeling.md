---
layout: post
title: "Forecasting Volatility with Panel Regressions"
date: 2025-11-08
categories: [Quants]
---

## Introduction

Volatility forecasts are essential for portfolio construction. They drive position sizing, leverage decisions, and risk limits. Get them wrong, and you're either leaving money on the table or taking on too much risk.

The standard approach is to fit a GARCH or EWMA model per asset and roll it forward. This works, but it treats each stock in isolation. Every stock gets its own model, estimated on its own history, ignoring the fact that volatility dynamics are largely shared across assets.

In this post, I test whether pooling information across assets improves volatility forecasts. Specifically, I compare:

- **Baselines:** Simple moving averages
- **Per-asset regressions:** One model per stock
- **Per-sector regressions:** One model per sector
- **Global regressions:** One model for all assets
- **Global + sector dummies:** Shared dynamics, sector-specific levels
- **Additional factors:** Market volatility, sector risk factors, log-space transformations

The result: global panel regressions with sector structure beat everything else, achieving 0.86 correlation with realized volatility versus 0.70 for moving averages.

## Data

I use Russell 1000 (RIY) constituents from 1995 to 2024. After filtering and cleaning, the dataset contains about 7 million date × asset observations. At any point in time, around 1,000 stocks are in the universe.

## Data Exploration

Before modeling, I look at the data to understand what we're working with.

### Volatility Distribution by Sector

![Sector Distribution](/assets/vol_forecasting/sector_distribution.png)
*Volatility distribution by sector: box plots show median and quartiles, density curves show the full distribution.*

Volatility varies significantly across sectors. Median annualized volatility ranges from ~15% in Utilities to ~30% in Energy. Two things stand out:

1. **Cross-sectional variation:** Different sectors have structurally different volatility levels → this motivates adding sector dummies to capture level differences
2. **Right-skewed distribution:** Volatility has a long right tail → this motivates testing log-space models to normalize the target

### Feature Correlations

| Feature | Correlation with 21d Forward Vol |
|---------|----------------------------------|
| Composite volatility (5/21/63d avg) | 0.738 |
| EWM volatility (21d) | 0.715 |
| Rolling volatility (21d) | 0.696 |

All volatility features are predictive. The composite (averaging multiple horizons) slightly outperforms single-horizon measures, motivating the use of multi-horizon features.

## Walk-Forward Methodology

All predictions use strict **day-by-day walk-forward testing**. For each day $t$, I train on days $[t-504, t-1]$ and predict on day $t$. No lookahead bias—yesterday's coefficients predict today.

```
Training:    Day t-504 ──────────────────── Day t-1
Prediction:                                          Day t
```

For each date, I estimate coefficients on the past 504 days, then apply them to today's features. This is powered by [polars-ols](https://github.com/azmyrajab/polars_ols)—a fast, Rust-based OLS implementation for Polars:

```python
import polars as pl
import polars_ols  # Registers least_squares namespace

feature_cols = ["X_feature_vol_5", "X_feature_vol_21", "X_feature_vol_63", "X_feature_vol_126"]

# Step 1: Estimate rolling coefficients (global model)
df = df.with_columns(
    pl.col("y_target_vol_21")
    .least_squares.rolling_ols(
        *[pl.col(c) for c in feature_cols],
        window_size=504,      # 2-year rolling window
        min_periods=252,      # Start after 1 year
        mode="coefficients",
    )
    .over(order_by="date")    # Pool all assets (global model)
    .alias("coefficients_raw")
)

# Step 2: Lag coefficients by 1 day for out-of-sample predictions
df = df.with_columns(
    pl.col("coefficients_raw")
    .shift(1)                 # Use yesterday's coefficients
    .over(order_by="date")
    .alias("coefficients_oos")
)

# Step 3: Generate predictions from lagged coefficients
df = df.with_columns(
    pl.col("coefficients_oos")
    .least_squares.predict(*[pl.col(c) for c in feature_cols])
    .alias("prediction")
)
```

The `.shift(1)` in Step 2 is critical—it ensures predictions on day $t$ only use coefficients estimated through day $t-1$.

**What does `.predict()` do?** The `coefficients_oos` column contains a struct with fitted coefficients (intercept + betas). The `.predict()` method computes:

$$\hat{\sigma} = \beta_0 + \beta_1 X_1 + \beta_2 X_2 + \beta_3 X_3 + \beta_4 X_4$$

This is equivalent to writing it manually:

```python
(
    pl.col("coefficients_oos").struct.field("const")
    + pl.col("coefficients_oos").struct.field("X_feature_vol_5") * pl.col("X_feature_vol_5")
    + pl.col("coefficients_oos").struct.field("X_feature_vol_21") * pl.col("X_feature_vol_21")
    + pl.col("coefficients_oos").struct.field("X_feature_vol_63") * pl.col("X_feature_vol_63")
    + pl.col("coefficients_oos").struct.field("X_feature_vol_126") * pl.col("X_feature_vol_126")
)
```

The `.predict()` shortcut keeps the code clean.

## Target & Evaluation

### Target: Forward Realized Volatility

The target is 21-day forward realized volatility:

$$
\sigma_{i,t}^{\text{fwd}} = \sqrt{\frac{252}{21} \sum_{k=1}^{21} r_{i,t+k}^2}
$$

where $r_{i,t}$ is the daily return of stock $i$ on day $t$. The factor $\sqrt{252}$ annualizes the volatility.

This target is observable and directly measurable—unlike GARCH's latent conditional variance. Clean target, clean evaluation.

### Evaluation Metrics

I evaluate predictions using:
- **RMSE:** Root mean squared error
- **MAE:** Mean absolute error
- **Correlation:** Spearman rank correlation with realized volatility

## Feature Engineering

Each feature is motivated by a specific stylized fact about volatility.

### Rolling Volatility

**Motivation:** Volatility clusters—high-vol days follow high-vol days. Recent realized volatility is the single best predictor of future volatility.

For each stock, I compute rolling volatility at multiple horizons:

$$
\hat{\sigma}_{i,t}^{(w)} = \sqrt{\frac{252}{w} \sum_{k=0}^{w-1} r_{i,t-k}^2}
$$

with windows $w \in \{5, 21, 63, 126\}$ days:
- **5-day:** Captures very recent shocks (earnings, news)
- **21-day:** Standard monthly volatility, balances noise and signal
- **63-day:** Quarterly horizon, smooths out short-term noise
- **126-day:** Semi-annual, provides mean-reversion anchor

### Asymmetric Features (Why Not EGARCH?)

**Motivation:** Volatility responds asymmetrically to returns—negative returns predict higher future volatility than positive returns of the same magnitude. This is the **leverage effect**: bad news increases uncertainty more than good news reduces it.

EGARCH is the standard way to model this.

But EGARCH has problems for our use case:

1. **No observable target:** EGARCH models latent conditional variance $h_t$. You can't directly measure it—you can only infer it from the model. This makes evaluation messy. Our target (21-day realized vol) is directly observable.

2. **Can't pool across assets:** EGARCH is a time-series model fit per asset. You can't easily share parameters across stocks, which means you're back to the per-asset overfitting problem we're trying to avoid.

3. **Computationally expensive:** MLE optimization for each stock, each day, in a rolling window? That's millions of optimizations.

**The alternative:** I capture the leverage effect with explicit downside/upside volatility features:

$$
\hat{\sigma}_{i,t}^{\text{down}} = \sqrt{\frac{252}{w} \sum_{k=0}^{w-1} r_{i,t-k}^2 \cdot \mathbf{1}_{r_{i,t-k} < 0}}
$$

$$
\hat{\sigma}_{i,t}^{\text{up}} = \sqrt{\frac{252}{w} \sum_{k=0}^{w-1} r_{i,t-k}^2 \cdot \mathbf{1}_{r_{i,t-k} \geq 0}}
$$

The downside volatility counts only negative return days; upside counts only positive days. If the leverage effect exists, the regression will learn a higher coefficient on downside vol than upside vol—and that's exactly what we see in the coefficient heatmap.

This approach gives us:
- **Observable target:** realized vol, not latent variance
- **Poolable:** works in a cross-sectional regression
- **Fast:** just rolling sums, no optimization
- **Interpretable:** "downside vol coefficient > upside vol coefficient" = leverage effect

### Sector Dummies

**Motivation:** Different sectors have structurally different volatility levels. Utilities are stable (regulated, predictable cash flows). Energy is volatile (commodity prices, geopolitical risk). Tech sits somewhere in between.

I add one-hot encoded sector dummies (BICS Level 1). As we saw in the data exploration, median volatility ranges from 15% (Utilities) to 30% (Energy). The dummies let the model learn these level differences while sharing the dynamics across all assets.

### Log Market Cap

**Motivation:** Small firms are more volatile than large firms. They have less diversified revenue streams, higher leverage, lower liquidity, and more sensitivity to idiosyncratic shocks.

I include log market cap as a feature:

$$
\text{LogMktCap}_{i,t} = \log(\text{MarketCap}_{i,t})
$$

The log transformation handles the skewed distribution of market caps (a few mega-caps, many small-caps) and makes the relationship with volatility more linear.

## Model Specification

### The Regression

For each date $t$, I fit a cross-sectional Ridge regression:

$$
\sigma_{i,t}^{\text{fwd}} = \beta_0 + \sum_{j=1}^{J} \beta_j X_{i,t}^{(j)} + \sum_{s=1}^{S} \gamma_s D_{i,s} + \varepsilon_{i,t}
$$

where:
- $X_{i,t}^{(j)}$ are volatility features (5d, 21d, 63d, 126d, downside, upside) and log market cap
- $D_{i,s}$ are sector dummies
- $\varepsilon_{i,t}$ is the error term

### Ridge Regularization

Volatility features at different horizons are highly correlated (~0.8+). OLS estimates become unstable. Ridge regression stabilizes them:

$$
\hat{\boldsymbol{\beta}} = \arg\min_{\boldsymbol{\beta}} \left\{ \sum_{i} \left( y_i - \mathbf{X}_i \boldsymbol{\beta} \right)^2 + \alpha \|\boldsymbol{\beta}\|_2^2 \right\}
$$

I use $\alpha = 1$. This shrinks coefficients toward zero without eliminating any feature.

### Ensemble Subsampling

Instead of a single model, I run 3 models with offset estimation windows:

```
Model 1: trained on days 0, 3, 6, 9, ...
Model 2: trained on days 1, 4, 7, 10, ...
Model 3: trained on days 2, 5, 8, 11, ...
```

Final prediction is the average:

$$
\hat{\sigma}_{i,t}^{\text{ensemble}} = \frac{1}{3} \sum_{m=1}^{3} \hat{\sigma}_{i,t}^{(m)}
$$

Each model sees slightly different data. Averaging reduces variance.

## Results: Step-by-Step Model Comparison

The central question: should we fit a model per asset, per sector, or globally? I build up the answer step by step, showing what each modeling choice adds.

### Step 1: Baselines

I start with what most practitioners use as simple benchmarks:

- **Composite average:** Equal-weighted average of 5, 21, and 63-day rolling volatility
- **Weighted blend:** 70% × 21-day vol + 30% × 252-day vol (similar to RiskMetrics EWMA)

These achieve correlations around **0.70**. Here's what the predictions look like:

![Baseline Residuals](/assets/vol_forecasting/residuals_baseline.png)
*Predicted vs actual volatility for the weighted blend baseline.*

The predictions follow the diagonal but with significant scatter. The model captures the broad relationship but misses a lot of variation. Can we do better by learning the weights from data instead of fixing them?

### Step 2: Per-Asset Regression

The first regression approach: fit a separate model for each stock. Each asset gets its own coefficients estimated on its own 2-year history.

| Model | Correlation | RMSE |
|-------|-------------|------|
| Baseline (weighted avg) | 0.70 | 0.17 |
| **Per-asset regression** | **0.75** | **0.15** |

Result: correlation improves to **0.75**. The regression learns better weights than the fixed heuristics.

But there's a problem: with only ~500 observations per stock in a 2-year window, coefficients are noisy. The model overfits to idiosyncratic patterns. Can we do better by sharing information across assets?

### Step 3: Pooling Across Stocks

What if volatility dynamics are shared across assets? Mean reversion, clustering, the leverage effect—these should work similarly for Apple and Exxon.

I test two pooling levels:

- **Per-sector:** One model per BICS sector (~700k obs/sector)
- **Global:** One model for all assets (~7M obs total)

| Model | Correlation | RMSE |
|-------|-------------|------|
| Per-asset | 0.75 | 0.15 |
| Per-sector | 0.84 | 0.13 |
| **Global** | **0.85** | **0.13** |

Both per-sector and global models jump to **0.84-0.85**—a 10-point improvement over per-asset. Pooling works. The volatility dynamics are indeed shared; estimating them on more data reduces noise.

This is the bias-variance tradeoff in action: per-asset models have low bias (flexible) but high variance (noisy estimates). Global models have slightly higher bias (same coefficients for all) but much lower variance (millions of observations).

### Step 4: Adding Sector Structure

Global pooling assumes all stocks share identical dynamics. But we saw in the data exploration that volatility levels differ by sector (15% for Utilities, 30% for Energy). 

Can we get the best of both worlds? Shared coefficients for dynamics, but sector-specific intercepts for levels?

I add sector dummies to the global model:

| Model | Correlation | RMSE |
|-------|-------------|------|
| Global | 0.85 | 0.130 |
| **Global + sector dummies** | **0.86** | **0.124** |

A further boost to **0.86**. The dummies let the model learn that Energy stocks have higher baseline volatility than Utilities, while still sharing the dynamics (how 21-day vol predicts forward vol) across all assets.

Here's what the best model predictions look like compared to the baseline:

![Best Model Residuals](/assets/vol_forecasting/residuals_best.png)
*Predicted vs actual volatility for the global + dummies model.*

The predictions are much tighter around the diagonal. The improvement is visible.

### Step 5: Log-Space Models

The volatility distribution is right-skewed (we saw this in the data exploration). Log-transforming should normalize the target. Does it help?

I test the same models but predicting $\log(\sigma)$ instead of $\sigma$, with log-transformed features:

| Model | Raw-Space Correlation | Log-Space Correlation |
|-------|----------------------|----------------------|
| Global | 0.845 | 0.849 |
| Global + dummies | 0.857 | 0.860 |

Log-space models are marginally better (~0.003 improvement). The difference is tiny—both approaches work well. I stick with raw-space for interpretability: coefficients are directly in volatility units, making them easier to sanity-check.

### Step 6: Additional Risk Factors

Can we improve further by adding macro risk factors?

**Market Volatility Factor:** Rolling 21-day volatility of the market index. The idea: when the market is volatile, all stocks should have higher volatility.

**Group Risk Factor (GRF):** Sector-level average volatility relative to its long-run norm. Inspired by AQR's "Risk Everywhere" factor. The idea: when a sector is stressed, stocks in that sector should have higher volatility.

| Model | Correlation |
|-------|-------------|
| Global + dummies | 0.857 |
| Global + dummies + market factor | 0.855 |
| Global + dummies + GRF | 0.844 |

Neither helps. In fact, they slightly hurt. Why? The existing asset-level volatility features already capture this information. If the market is volatile, individual stocks are volatile, and our features pick that up. Adding a redundant market factor just adds noise.

### Summary

![Metrics Comparison](/assets/vol_forecasting/metrics_comparison.png)
*Comparison of all model variants across RMSE and correlation metrics.*

| Step | Model | Correlation | RMSE |
|------|-------|-------------|------|
| Baseline | Moving averages | 0.70 | 0.17 |
| +Regression | Per-asset | 0.75 | 0.15 |
| +Pooling | Global | 0.85 | 0.13 |
| +Structure | Global + dummies | 0.86 | 0.124 |
| +Log-space | Global + dummies (log) | 0.86 | 0.124 |
| +Risk factors | Global + dummies + market | 0.86 | 0.125 |

The progression is clear: learning weights beats heuristics, pooling beats per-asset, and adding sector structure squeezes out the last bit of signal. Log-space and risk factors don't add much.

## Robustness & Validation

### Window Sensitivity

I swept rolling windows from 6 months to 10 years:

![Window Sensitivity](/assets/vol_forecasting/window_trends.png)
*Model performance across different rolling window sizes (126 to 2520 days).*

Performance is stable between 1–3 years. Very short windows (<6 months) are noisier; very long windows (>5 years) start lagging regime changes. I use 504 days (2 years).

### Regime Robustness

Do models hold up when volatility spikes? I bucket predictions by market volatility regime:

![Regime Analysis](/assets/vol_forecasting/regime_analysis.png)
*Correlation by market volatility regime: low (<20%), neutral (20-30%), high (>30%).*

| Model | Low (<20%) | Neutral (20-30%) | High (>30%) |
|-------|------------|------------------|-------------|
| Global + dummies | 0.77 | 0.83 | 0.86 |
| Per-asset | 0.67 | 0.68 | 0.76 |
| Baseline | 0.60 | 0.62 | 0.68 |

Interestingly, all models perform better in high-vol regimes. When volatility is elevated, it's more persistent and easier to predict. The global model maintains its edge across all regimes.

### Coefficient Interpretability

![Coefficient Heatmap](/assets/vol_forecasting/coefficient_heatmap.png)
*Rolling regression coefficients over time for the global + dummies model.*

The coefficients behave as expected:
- **Short-term vol dominates:** 5d and 21d coefficients carry most weight
- **Long-term vol anchors:** 126d coefficient provides mean-reversion target
- **Sector dummies spike in crises:** Financials and Energy loadings balloon in 2008, 2020
- **Downside > upside:** Higher coefficient on downside vol (leverage effect)

## Conclusion

The final model: **global Ridge regression with sector dummies, asymmetric vol features, 2-year rolling window, and 3-model ensemble**.

| Component | Choice |
|-----------|--------|
| Target | 21-day forward realized vol |
| Features | Rolling vol (5/21/63/126d), downside/upside vol, log market cap, sector dummies |
| Model | Ridge regression ($\alpha=1$) |
| Estimation | 2-year rolling window, 3-model ensemble |
| Pooling | Global (all assets) |
| Implementation | polars-ols for fast rolling regressions |

The key insight: **volatility dynamics are shared across assets**. Mean reversion, clustering, and the leverage effect work the same way whether you're looking at Apple or Exxon. Per-asset models waste data chasing idiosyncratic noise. Global models with sector structure extract the signal efficiently.

## What's Next

In the next post, I'll test whether ML models (LightGBM, neural nets) can beat these structured regressions. I also want to look at the economic value of better volatility forecasts—how much does 0.86 vs 0.70 correlation actually matter for portfolio performance?
