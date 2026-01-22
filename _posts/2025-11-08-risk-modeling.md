---
layout: post
title: "Forecasting Volatility with Panel Regressions"
date: 2025-11-08
categories: [Quants]
---

## Introduction

I scale positions by volatility. And so should you.

The idea is simple: take smaller positions in volatile stocks, larger positions in stable ones. This keeps your portfolio risk roughly constant over time. It's called volatility targeting, and it works.

But here's the thing—to do this well, you need to *predict* future volatility. Not yesterday's volatility, but what volatility will be over your holding period. Most people don't spend much time on this. They use the last month's realized vol and call it a day.

<div style="border: 2px solid #333; padding: 1em; margin: 1em 0; background-color: #f9f9f9;">
<strong>The question:</strong> Is it worth spending time trying to predict volatility better?
</div>

This post answers that question. Spoiler: yes, it's worth it. Perfect volatility forecasts would add 3-4% annualized return to my strategy. Even modest improvements (correlation 0.70 → 0.86) should capture a good chunk of that.

### How I Use Volatility Forecasts

In my [previous post on the low-volatility factor]({% post_url 2024-12-15-low-volatility-factor %}), I built a long-short equity strategy. Position sizing combines two things: ML signal quality and volatility forecasts.

The allocation has two stages. First, I convert ML scores into initial weights $\alpha_i$. Better predictions get more capital on the long side; worse predictions get more capital on the short side (weights are always positive, just assigned to different legs).

Then I scale each position by volatility to target a fixed risk level:

$$w_i = \alpha_i \cdot \min\left(\frac{\sigma_{\text{target}}}{\hat{\sigma}_i}, \lambda_{\max}\right)$$

where:
- \\(\hat{\sigma}_i\\) = volatility forecast for stock \\(i\\)
- \\(\sigma_{\text{target}}\\) = target volatility (20% annualized)
- \\(\lambda_{\max} = 3\\) = leverage cap

The intuition: if a stock has half the target vol, I can take twice the position (up to the cap).

Finally, I apply constraints: 5% max per stock, total exposure ≤ 100%.

The key term is $\hat{\sigma}_i$. Currently I estimate it with simple moving averages—20-day rolling vol for longs, 60-day for shorts. When these forecasts are wrong, position sizing suffers:

- **Underestimate vol** → positions too large → deeper drawdowns
- **Overestimate vol** → positions too small → missed returns

### The Perfect Foresight Experiment

To see what's at stake, I run a backtest with perfect foresight. What if I knew the exact realized volatility for the next 21 days? This is obviously impossible in practice, but it shows the upper bound.

I test three scenarios:
- **Current:** Rolling volatility estimates (what I use now)
- **Perfect Long:** Perfect foresight on the long leg only
- **Perfect:** Perfect foresight on both legs (the upper bound)

### Long-Short Performance

<figure style="margin: 0.3em 0 0 0; padding: 0; line-height: 1;">
<iframe src="/assets/vol_impact/vol_impact_comparison.html" width="100%" height="420" frameborder="0" style="display: block; margin: 0; padding: 0; border: none; vertical-align: bottom;"></iframe>
<figcaption style="margin: 0.1em 0 0 0; padding: 0; font-size: 0.9em; line-height: 1.3; color: #888;">Figure 1: Long-short portfolio performance with different volatility estimation methods.</figcaption>
</figure>

### Individual Legs

<figure style="margin: 0.25em 0 0 0; padding: 0; line-height: 1;">
<iframe src="/assets/vol_impact/long_short_legs_comparison.html" width="100%" height="410" frameborder="0" style="display: block; margin: 0; padding: 0; border: none; vertical-align: bottom;"></iframe>
<figcaption style="margin: 0.08em 0 0 0; padding: 0; font-size: 0.9em; line-height: 1.3; color: #888;">Figure 2: Long and short legs separately—where does the improvement come from?</figcaption>
</figure>

### The Numbers

Here's the punchline. First, the long-short portfolios:

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
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">12.3%</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee;">1.76</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; color: #b00;">-16.2%</td>
</tr>
<tr style="background: #e8f5e9;">
<td style="padding: 0.6em; font-weight: bold; border-bottom: 1px solid #eee;">Perfect Long</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; color: #2e7d32; font-weight: bold;">16.0%</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; color: #2e7d32; font-weight: bold;">2.65</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; color: #2e7d32;">-7.8%</td>
</tr>
<tr style="background: #f5f5f5;">
<td style="padding: 0.6em;">Perfect</td>
<td style="padding: 0.6em; text-align: center;">12.5%</td>
<td style="padding: 0.6em; text-align: center;">2.18</td>
<td style="padding: 0.6em; text-align: center; color: #2e7d32;">-7.8%</td>
</tr>
</tbody>
</table>
</div>
<p style="margin: 0.3em 0 1em 0; font-size: 0.9em; color: #888;">Table 1: Long-short portfolio performance (with fees). Perfect Long = perfect foresight on long leg only.</p>

Wait—Perfect Long beats Perfect? Yes. When you give the short leg perfect foresight, it takes larger positions in low-vol stocks that happen to be bad shorts. The long leg is where better vol forecasts really pay off.

And here's the leg-by-leg breakdown:

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
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; background: #fafafa;">13.1%</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; background: #fafafa;">1.14</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; background: #fafafa; color: #b00;">-29.7%</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; background: #e8f5e9; color: #2e7d32; font-weight: bold;">17.1%</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; background: #e8f5e9; color: #2e7d32; font-weight: bold;">1.92</td>
<td style="padding: 0.6em; text-align: center; border-bottom: 1px solid #eee; background: #e8f5e9; color: #2e7d32;">-14.1%</td>
</tr>
<tr>
<td style="padding: 0.6em; font-weight: bold;">Short</td>
<td style="padding: 0.6em; text-align: center; background: #fafafa;">0.7%</td>
<td style="padding: 0.6em; text-align: center; background: #fafafa;">0.07</td>
<td style="padding: 0.6em; text-align: center; background: #fafafa; color: #b00;">-29.3%</td>
<td style="padding: 0.6em; text-align: center; background: #e8f5e9;">3.8%</td>
<td style="padding: 0.6em; text-align: center; background: #e8f5e9;">0.42</td>
<td style="padding: 0.6em; text-align: center; background: #e8f5e9;">-24.3%</td>
</tr>
</tbody>
</table>
</div>
<p style="margin: 0.3em 0 1em 0; font-size: 0.9em; color: #888;">Table 2: Individual leg performance with Current vs Perfect volatility forecasts.</p>

The long leg improves dramatically: +4% return, nearly double the Sharpe, half the drawdown. The short leg improves too, but it's a smaller effect—it runs at lower leverage and benefits less from accurate position sizing.

### So What?

The takeaway: perfect volatility forecasts on the long leg alone would boost Sharpe from 1.76 to 2.65. That's huge. Obviously we can't achieve perfect foresight, but it shows what's at stake.

The rest of this post is about getting closer to that upper bound. Can we beat the simple rolling averages I currently use? Spoiler: yes. Global panel regressions with sector structure achieve 0.86 correlation with realized vol (vs 0.70 for moving averages). That should translate to meaningful alpha.

**What I test:**
- Baselines: simple moving averages
- Per-asset regressions: one model per stock
- Per-sector: one model per sector
- Global: one model for all assets
- Global + sector dummies: shared dynamics, sector-specific levels

**Structure:**
1. Data exploration
2. Walk-forward methodology (no lookahead!)
3. Step-by-step model comparison
4. Robustness checks

## Data

Russell 1000 constituents, 1995–2024. After cleaning, that's about 7 million date × asset observations. Roughly 1,000 stocks in the universe at any point.

## Data Exploration

Before throwing regressions at the problem, let's look at what we're working with.

### Volatility Distribution by Sector

<figure style="margin: 0.3em 0 1.5em 0; padding: 0; line-height: 1;">
<iframe src="/assets/vol_forecasting/sector_distribution.html" width="100%" height="580" frameborder="0" style="display: block; margin: 0; padding: 0; border: none; vertical-align: bottom;"></iframe>
<figcaption style="margin: 0.1em 0 0 0; padding: 0; font-size: 0.9em; line-height: 1.3; color: #888;">Figure 3: Volatility distribution by sector—box plots show median and quartiles, density curves show the full distribution.</figcaption>
</figure>

Volatility varies a lot by sector. Median vol ranges from ~15% in Utilities to ~30% in Energy. Two things stand out:

1. Different sectors have structurally different volatility levels. This motivates adding sector dummies.
2. The distribution is right-skewed (long right tail). This motivates testing log-space models.

### Feature Correlations

| Feature | Correlation |
|---------|-------------|
| Composite volatility (5/21/63d avg) | 0.738 |
| EWM volatility (21d) | 0.715 |
| Rolling volatility (21d) | 0.696 |

<p style="margin: 0.3em 0 1em 0; font-size: 0.9em; color: #888;">Table 3: Feature correlations with 21-day forward volatility.</p>

All volatility features are predictive. The composite (averaging multiple horizons) slightly outperforms single-horizon measures, motivating the use of multi-horizon features.

## Walk-Forward Methodology

This is important: all predictions use strict day-by-day walk-forward testing. Train on the past 2 years, predict today. No lookahead bias—yesterday's coefficients predict today.

```
Training:    Day t-504 ──────────────────── Day t-1
Prediction:                                          Day t
```

For each date, I estimate coefficients on the past 504 days, then apply them to today's features. This is powered by [polars-ols](https://github.com/azmyrajab/polars_ols)—a fast, Rust-based OLS implementation for Polars:

```python
import polars as pl
import polars_ols  # Registers least_squares namespace

feature_cols = ["X_feature_vol_5", "X_feature_vol_21", "X_feature_vol_63", "X_feature_vol_126"]

# Step 1: Estimate rolling coefficients and lag by 1 day (out-of-sample)
df = df.with_columns(
    pl.col("y_target_vol_21")
    .least_squares.rolling_ols(
        *[pl.col(c) for c in feature_cols],
        window_size=504,      # 2-year rolling window
        min_periods=252,      # Start after 1 year
        mode="coefficients",
    )
    .shift(1)                 # Use yesterday's coefficients (critical!)
    .over("date", order_by="date")  # Group by date, pool all assets (global model)
    .alias("coefficients_oos")
)

# Step 2: Generate predictions from lagged coefficients
df = df.with_columns(
    pl.col("coefficients_oos")
    .least_squares.predict(*[pl.col(c) for c in feature_cols])
    .alias("prediction")
)
```

The `.shift(1)` after `.rolling_ols()` is critical—it ensures predictions on day $t$ use coefficients estimated through day $t-1$, making predictions truly out-of-sample.

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

Each feature is motivated by something we know about how volatility behaves.

### Rolling Volatility

Volatility clusters. High-vol days follow high-vol days. This is the most robust finding in finance. Recent realized vol is the single best predictor of future vol.

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

Volatility responds asymmetrically to returns. Bad news increases vol more than good news reduces it—the "leverage effect." EGARCH is the standard way to model this.

But EGARCH has problems for what we're doing:

1. No observable target. EGARCH models latent conditional variance. You can't measure it directly—only infer it from the model. Our target (21-day realized vol) is directly observable.

2. Can't pool across assets. EGARCH is fit per asset. You can't share parameters across stocks, so you're back to the per-asset overfitting problem.

3. Computationally expensive. MLE optimization for each stock, each day, in a rolling window? That's millions of optimizations.

The alternative: I capture the leverage effect with explicit downside/upside volatility features:

$$
\hat{\sigma}_{i,t}^{\text{down}} = \sqrt{\frac{252}{w} \sum_{k=0}^{w-1} r_{i,t-k}^2 \cdot \mathbf{1}_{r_{i,t-k} < 0}}
$$

$$
\hat{\sigma}_{i,t}^{\text{up}} = \sqrt{\frac{252}{w} \sum_{k=0}^{w-1} r_{i,t-k}^2 \cdot \mathbf{1}_{r_{i,t-k} \geq 0}}
$$

The downside volatility counts only negative return days; upside counts only positive days. If the leverage effect exists, the regression will learn a higher coefficient on downside vol than upside vol—and that's exactly what we see in the coefficient heatmap.

This gives us:
- Observable target (realized vol, not latent variance)
- Poolable (works in cross-sectional regression)
- Fast (just rolling sums, no optimization)
- Interpretable (downside coef > upside coef = leverage effect)

### Sector Dummies

Different sectors have structurally different vol levels. Utilities are stable. Energy is volatile. Tech sits somewhere in between. I add sector dummies (BICS Level 1) so the model can learn these level differences while sharing the dynamics across all assets.

### Log Market Cap

Small firms are more volatile than large firms. Less diversified revenue, higher leverage, lower liquidity, more idiosyncratic risk.

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

### Clipping & Bounds

Volatility data can contain outliers—stocks that jump 10x during earnings or crash during liquidations. These extreme values corrupt coefficient estimates.

**Training:** I clip volatility features and targets to [2.5%, 200%] during model training:
- Values below 2.5% are unrealistic for daily-rebalanced portfolios (bid-ask spreads alone create this much noise)
- Values above 200% annualized volatility are tail events that shouldn't drive regression weights
- Clipping during training prevents outliers from distorting coefficient estimates

**Evaluation:** All reported metrics (correlation, RMSE, MAE) are computed on **raw, unclipped volatility**. This gives an honest assessment of model performance on real data, including tail events.

**Predictions:** I clip final predictions to [2%, 200%] for visualization in figures. This prevents nonsensical outputs (negative volatility, infinite leverage recommendations) and keeps plots readable. The metrics themselves are evaluated on raw volatility.

**Note:** Performance on clipped volatility would be slightly higher (outliers are easier to predict when bounded), but the difference is small. I report raw metrics to be conservative.

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

The central question: should we fit a model per asset, per sector, or globally? Let me build up the answer step by step.

### Step 1: Baselines

What most practitioners use:

- Composite average: equal-weighted average of 5, 21, and 63-day rolling vol
- Weighted blend: 70% × 21-day vol + 30% × 252-day vol (RiskMetrics-style)

These achieve correlations around 0.70. Here's what the predictions look like:

<figure style="margin: 0.3em 0 1.5em 0; padding: 0; line-height: 1;">
<iframe src="/assets/vol_forecasting/residuals_baseline.html" width="100%" height="420" frameborder="0" style="display: block; margin: 0; padding: 0; border: none; vertical-align: bottom;"></iframe>
<figcaption style="margin: 0.1em 0 0 0; padding: 0; font-size: 0.9em; line-height: 1.3; color: #888;">Figure 4: Predicted vs actual volatility for the weighted blend baseline.</figcaption>
</figure>

The predictions follow the diagonal but with significant scatter. Can we do better by learning the weights from data instead of fixing them?

### Step 2: Per-Asset Regression

First attempt: fit a separate model for each stock. Each asset gets its own coefficients estimated on its own 2-year history.

| Model | Correlation | RMSE |
|-------|-------------|------|
| Baseline (weighted avg) | 0.70 | 0.17 |
| Per-asset regression | 0.75 | 0.15 |

<p style="margin: 0.3em 0 1em 0; font-size: 0.9em; color: #888;">Table 4: Per-asset regression vs baseline.</p>

Correlation improves to 0.75. The regression learns better weights than fixed heuristics.

But there's a problem: with only ~500 observations per stock in a 2-year window, coefficients are noisy. The model overfits to idiosyncratic patterns. Can we do better by sharing information?

### Step 3: Pooling Across Stocks

Here's the key insight: what if volatility dynamics are shared across assets? Mean reversion, clustering, the leverage effect—these should work similarly for Apple and Exxon.

I test two pooling levels:

- Per-sector: one model per BICS sector (~700k obs/sector)
- Global: one model for all assets (~7M obs total)

| Model | Correlation | RMSE |
|-------|-------------|------|
| Per-asset | 0.75 | 0.15 |
| Per-sector | 0.84 | 0.13 |
| Global | 0.85 | 0.13 |

<p style="margin: 0.3em 0 1em 0; font-size: 0.9em; color: #888;">Table 5: Impact of pooling across stocks.</p>

Both jump to 0.84-0.85—a 10-point improvement over per-asset. Pooling works. Volatility dynamics are indeed shared across assets. Estimating them on more data reduces noise.

This is bias-variance tradeoff in action. Per-asset models: low bias (flexible), high variance (noisy). Global models: slightly higher bias (same coefficients for all), much lower variance (millions of observations).

### Step 4: Adding Sector Structure

Global pooling assumes all stocks share identical dynamics. But we saw that volatility *levels* differ by sector (15% for Utilities, 30% for Energy).

Can we get the best of both worlds? Shared coefficients for dynamics, sector-specific intercepts for levels?

Add sector dummies to the global model:

| Model | Correlation | RMSE |
|-------|-------------|------|
| Global | 0.85 | 0.130 |
| Global + sector dummies | 0.86 | 0.124 |

<p style="margin: 0.3em 0 1em 0; font-size: 0.9em; color: #888;">Table 6: Adding sector structure.</p>

A further boost to 0.86. The dummies let the model learn that Energy stocks have higher baseline vol than Utilities, while still sharing the dynamics across all assets.

Here's what the best model looks like compared to the baseline:

<figure style="margin: 0.3em 0 1.5em 0; padding: 0; line-height: 1;">
<iframe src="/assets/vol_forecasting/residuals_best.html" width="100%" height="420" frameborder="0" style="display: block; margin: 0; padding: 0; border: none; vertical-align: bottom;"></iframe>
<figcaption style="margin: 0.1em 0 0 0; padding: 0; font-size: 0.9em; line-height: 1.3; color: #888;">Figure 5: Predicted vs actual volatility for the global + dummies model.</figcaption>
</figure>

The predictions are much tighter around the diagonal. The improvement is visible.

### Step 5: Log-Space Models

The volatility distribution is right-skewed. Log-transforming should normalize the target. Does it help?

| Model | Raw-Space | Log-Space |
|-------|-----------|-----------|
| Global | 0.845 | 0.849 |
| Global + dummies | 0.857 | 0.860 |

<p style="margin: 0.3em 0 1em 0; font-size: 0.9em; color: #888;">Table 7: Raw-space vs log-space models.</p>

Marginally better (~0.003). The difference is tiny. I stick with raw-space for interpretability—coefficients are directly in volatility units, easier to sanity-check.

### Step 6: Additional Risk Factors

Can we improve further with macro risk factors?

- Market volatility factor: rolling 21-day vol of the market index
- Group Risk Factor (GRF): sector-level vol relative to long-run norm (AQR-style)

| Model | Correlation |
|-------|-------------|
| Global + dummies | 0.857 |
| + market factor | 0.855 |
| + GRF | 0.844 |

<p style="margin: 0.3em 0 1em 0; font-size: 0.9em; color: #888;">Table 8: Adding macro risk factors.</p>

Neither helps. In fact, they slightly hurt. Why? The asset-level vol features already capture this. If the market is volatile, individual stocks are volatile, and our features pick that up. Adding redundant factors just adds noise.

### Summary

<figure style="margin: 0.3em 0 1.5em 0; padding: 0; line-height: 1;">
<iframe src="/assets/vol_forecasting/metrics_comparison.html" width="100%" height="950" frameborder="0" style="display: block; margin: 0; padding: 0; border: none; vertical-align: bottom;"></iframe>
<figcaption style="margin: 0.1em 0 0 0; padding: 0; font-size: 0.9em; line-height: 1.3; color: #888;">Figure 6: Comparison of all model variants across RMSE, MAE, correlation, and MAPE metrics.</figcaption>
</figure>

| Step | Model | Correlation | RMSE |
|------|-------|-------------|------|
| Baseline | Moving averages | 0.70 | 0.17 |
| +Regression | Per-asset | 0.75 | 0.15 |
| +Pooling | Global | 0.85 | 0.13 |
| +Structure | Global + dummies | 0.86 | 0.124 |
| +Log-space | Global + dummies (log) | 0.86 | 0.124 |
| +Risk factors | Global + dummies + market | 0.86 | 0.125 |

<p style="margin: 0.3em 0 1em 0; font-size: 0.9em; color: #888;">Table 9: Model development progression summary.</p>

The progression is clear: learning weights beats heuristics, pooling beats per-asset, sector structure squeezes out the last bit of signal. Log-space and macro factors don't help.

## Robustness & Validation

### Window Sensitivity

I swept rolling windows from 6 months to 10 years. How sensitive are results to this choice?

<figure style="margin: 0.3em 0 1.5em 0; padding: 0; line-height: 1;">
<iframe src="/assets/vol_forecasting/window_trends.html" width="100%" height="420" frameborder="0" style="display: block; margin: 0; padding: 0; border: none; vertical-align: bottom;"></iframe>
<figcaption style="margin: 0.1em 0 0 0; padding: 0; font-size: 0.9em; line-height: 1.3; color: #888;">Figure 7a: Global model performance across different rolling window sizes (252 to 2520 days).</figcaption>
</figure>

<figure style="margin: 0.3em 0 1.5em 0; padding: 0; line-height: 1;">
<iframe src="/assets/vol_forecasting/window_trends_sector.html" width="100%" height="420" frameborder="0" style="display: block; margin: 0; padding: 0; border: none; vertical-align: bottom;"></iframe>
<figcaption style="margin: 0.1em 0 0 0; padding: 0; font-size: 0.9em; line-height: 1.3; color: #888;">Figure 7b: Per-sector model performance across different rolling window sizes (252 to 2520 days).</figcaption>
</figure>

Performance is stable between 1–3 years. Very short windows are noisier; very long windows lag regime changes. I use 504 days (2 years).

### Regime Robustness

Do models hold up when volatility spikes? Here's performance bucketed by market vol regime:

<figure style="margin: 0.3em 0 1.5em 0; padding: 0; line-height: 1;">
<iframe src="/assets/vol_forecasting/regime_analysis.html" width="100%" height="820" frameborder="0" style="display: block; margin: 0; padding: 0; border: none; vertical-align: bottom;"></iframe>
<figcaption style="margin: 0.1em 0 0 0; padding: 0; font-size: 0.9em; line-height: 1.3; color: #888;">Figure 8: Correlation by market volatility regime—low (&lt;20%), neutral (20-30%), high (&gt;30%).</figcaption>
</figure>

| Model | Low (<20%) | Neutral (20-30%) | High (>30%) |
|-------|------------|------------------|-------------|
| Global + dummies | 0.79 | 0.83 | 0.87 |
| Global + log dummies | 0.79 | 0.83 | 0.87 |
| Per-sector | 0.79 | 0.82 | 0.85 |
| Per-asset | 0.67 | 0.69 | 0.76 |
| Baselines | 0.61-0.62 | 0.62-0.66 | 0.68-0.70 |

<p style="margin: 0.3em 0 1em 0; font-size: 0.9em; color: #888;">Table 10: Model correlation by market volatility regime.</p>

A few observations:

1. All models improve in high-vol regimes. When vol is elevated, it's more persistent and easier to predict. During calm periods, vol is compressed and harder to differentiate.

2. Global models maintain their edge across all regimes. The 10+ point gap vs per-asset holds whether markets are calm or stressed.

3. Per-asset models suffer most in low-vol regimes. With less signal, the noisy estimates hurt more. Global pooling provides stability when there's less to work with.

### Coefficient Interpretability

<figure style="margin: 0.3em 0 1.5em 0; padding: 0; line-height: 1;">
<iframe src="/assets/vol_forecasting/coefficient_heatmap.html" width="100%" height="550" frameborder="0" style="display: block; margin: 0; padding: 0; border: none; vertical-align: bottom;"></iframe>
<figcaption style="margin: 0.1em 0 0 0; padding: 0; font-size: 0.9em; line-height: 1.3; color: #888;">Figure 9: Global rolling regression coefficients over time. Red = predicts higher vol, Blue = predicts lower vol.</figcaption>
</figure>

<figure style="margin: 0.3em 0 1.5em 0; padding: 0; line-height: 1;">
<iframe src="/assets/vol_forecasting/coefficient_heatmap_sector.html" width="100%" height="550" frameborder="0" style="display: block; margin: 0; padding: 0; border: none; vertical-align: bottom;"></iframe>
<figcaption style="margin: 0.1em 0 0 0; padding: 0; font-size: 0.9em; line-height: 1.3; color: #888;">Figure 10: Per-sector rolling regression coefficients over time. Red = predicts higher vol, Blue = predicts lower vol.</figcaption>
</figure>

The heatmaps reveal which features drive predictions.

Most important features:

1. 126-day vol (~0.5): Strongest positive predictor. Long-term vol acts as the mean-reversion anchor.
2. 63-day vol (~0.3): Second strongest. Bridges short-term noise and long-term structure.
3. 5-day vol (negative!): Surprisingly negative. This is mean-reversion—when short-term vol spikes above long-term, the model predicts it will come down.
4. Log market cap (~-0.1): Negative as expected. Smaller firms are more volatile.

The sector dummies tell a story:

- Energy: huge spike in 2020 (COVID oil crash, negative prices). Also elevated during 2008 and 2014-2016.
- Financials: spike in 2008-2009 (GFC). The model learned Financials needed a higher vol intercept during the crisis.
- Technology: elevated in early 2000s (dot-com bust), moderate since.
- Utilities: consistently low. Defensive stocks live up to their reputation.

Asymmetric features (downside/upside vol) both have small negative coefficients. The leverage effect is present but subtle—most asymmetry is already captured by the level dynamics.

## Conclusion

The final model: global Ridge regression with sector dummies, 2-year rolling window, 3-model ensemble.

| Component | Choice |
|-----------|--------|
| Target | 21-day forward realized vol |
| Features | Rolling vol (5/21/63/126d), downside/upside vol, log market cap, sector dummies |
| Model | Ridge regression (α=1) |
| Estimation | 2-year rolling window, 3-model ensemble |
| Pooling | Global (all assets) |
| Implementation | polars-ols for fast rolling regressions |

<p style="margin: 0.3em 0 1em 0; font-size: 0.9em; color: #888;">Table 11: Final model specification.</p>

The key insight: volatility dynamics are shared across assets. Mean reversion, clustering, the leverage effect—they work the same way for Apple and Exxon. Per-asset models waste data chasing idiosyncratic noise. Global models with sector structure extract signal efficiently.

We started with the question: is it worth predicting volatility better? The answer is yes. Perfect foresight would boost Sharpe from 1.76 to 2.65. We can't achieve perfect foresight, but improving correlation from 0.70 to 0.86 should capture a meaningful chunk of that improvement.

## What's Next

ML models (LightGBM, neural nets). Can they beat these structured regressions? The linear model can't capture interactions—for example, how 21-day vol might predict forward vol differently for Energy vs Utilities. Tree-based models can discover these automatically. That's the next experiment.

