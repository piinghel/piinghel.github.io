---
layout: post
title: "The Low Volatility Factor: A Boring Way to Make Money?"
date: 2024-12-15
categories: [Quant]
---


## The Low-Volatility Factor: A Steady Approach

The low-volatility factor is a well-known concept in quantitative investing. It’s based on a simple observation: stocks that fluctuate less tend to have better risk-adjusted returns than those with more extreme price swings.

This post is part of a series on ranking stocks. I'll start with a single-factor approach and gradually build up—first by combining multiple factors using linear regression, then testing more advanced design choices, and finally exploring interactions and non-linearities with LightGBM. At the end, I'll compare all three approaches to see whether complexity actually adds value.

For now, let's focus on constructing a long-short portfolio using the low-volatility factor in the Russell 1000.



## Tradeable Universe

The dataset covers the Russell 1000 (RIY), which tracks the largest U.S. stocks. To keep things realistic, I filter out stocks trading below $5.

The sample runs from 1995 to 2024, covering around 3,300 stocks as companies enter and exit the index. At any given time, about 1,000 stocks are tradeable. Since the dataset uses point-in-time constituents, there’s no survivorship bias—this isn’t just a filtered list of stocks that happened to do well.

![Figure 1](/assets/2024-12-15-low-volatility-factor/nr_stocks.svg)  
Figure 1: Number of tradeable stocks over time.



## Measuring Volatility

The low-volatility factor identifies stocks with more stable price movements. To measure this, I compute the standard deviation of daily returns over three short-term rolling windows:

- 5-day  
- 10-day  
- 21-day

Shorter windows help capture shifts in volatility faster, while longer ones smooth things out. A mix of these gives a balance between stability and adaptability.

Across the dataset, the average volatility is 33%, with most stocks falling between 18% and 39%. The median is 26%. Some stocks exhibit extreme price swings, so I winsorized the data at 5% and 200% to prevent outliers from distorting the results.

The distribution is skewed to the right, meaning most stocks cluster around moderate volatility, but a few experience significantly higher fluctuations.

![Figure 2](/assets/2024-12-15-low-volatility-factor/distribution_volatilities.svg)  

Figure 2: Annualized volatility across all stocks in the dataset.


## Does Low Volatility Matter?

I was testing if low-volatility stocks actually perform differently, so I checked a couple of things:

1. How they did in the next 10 days
2. Their Sharpe ratio also for the next 10 days

For returns, the Pearson correlation was only 0.03, so higher-volatility stocks showed a tiny edge in raw returns. But when I switched to Spearman, it pretty much flattened out to zero (0.00). I prefer Spearman here because it works with ranks, not raw values, which helps avoid the noise from outliers.

When I looked at Sharpe ratios, the pattern flipped. Pearson showed a small negative correlation (-0.035), and Spearman bumped it up to -0.04. This suggests that more volatile stocks tend to have lower Sharpe ratios.

The numbers are small, but that’s to be expected—there’s always a lot of noise in finance. Even weak signals can matter if you apply them consistently over a large universe of stocks.


## Sorting Stocks into Portfolios 

To turn this into a tradeable strategy, I rank stocks by volatility at each point in time and sort them into five portfolios. This ensures that portfolio assignments are always relative to the current market.

Here’s how it works:  
1. Compute rolling volatility for each stock.  
2. Rank stocks by volatility within the universe.  
3. Normalize ranks to a 0-1 scale.  
4. Assign stocks to one of five portfolios based on percentile rank.

Let $r_{i,t}$ be the cross-sectional rank of stock $i$ at time $t$, and $N$ be the number of stocks. The normalized rank is:

$$
\frac{r_{i,t}}{N}
$$

Stocks are then grouped into these buckets:

- Portfolio 1: Lowest 10% of stocks ($0 \leq \text{Rank Score} < 0.1$) → Low volatility  
- Portfolio 2: 10% to 20% of stocks ($0.1 \leq \text{Rank Score} < 0.2$)  
- Portfolio 3: Middle 60% ($0.2 \leq \text{Rank Score} < 0.8$)  
- Portfolio 4: 80% to 90% of stocks ($0.8 \leq \text{Rank Score} < 0.9$)  
- Portfolio 5: Highest 10% ($0.9 \leq \text{Rank Score} \leq 1.0$) → High volatility

This way, every stock’s classification is determined relative to the cross-sectional volatility of the market at that time.


## Constructing a Long-Only and Long-Short Portfolio

Once the stocks are bucketed, I create two types of portfolios: equal-weighted and volatility-targeted.

### Equal-Weighted Portfolio 

In the equal-weighted portfolio, all stocks are given equal weight, and I remain fully invested at all times. However, this creates a mismatch between the volatilities of the long and short positions, which I’ll explain further below. To construct the long-short portfolio, I simply take the difference between the low-volatility (P1) and high-volatility portfolios (P5).  

### Volatility-Targeted Portfolio


Volatility targeting adjusts stock weights based on their volatility to create a more stable portfolio. Here’s how it works:  

1. Compute the Volatility Scaling Factor: For each stock, calculate:  
   $$
   \text{vol_ratio} = \frac{\sigma_{target}}{\hat{\sigma}_{i,t}}
   $$  
   where:  
   - $\sigma_{target} = 20\%$ is an arbitrary target, chosen because it’s close to the average stock volatility. This ensures that the overall portfolio volatility remains around 8%.  
   - ${\hat{\sigma}_{i,t}}$ represents the stock’s estimated future volatility, typically calculated using a rolling 60-day standard deviation. More complex models could be used, but we’ll keep it simple for now.  

2. Adjust Equal Weights: Multiply the equal weight of each stock by its $\text{vol\_ratio}$:  
   $$
   w_i = \text{equal_weight} \times \text{vol_ratio}
   $$  

3. Cap Individual Weights: Ensure no stock weight exceeds 4% to prevent excessive concentration. This cap is somewhat arbitrary and depends on the number of stocks in the portfolio and possibly other factors, such as sector diversification or liquidity constraints.  

4. Constrain Portfolio Exposure: Ensure that the total portfolio weight does not exceed $1$ (i.e., fully invested). During periods of high volatility, the total weight may decrease to limit risk. While this may resemble market timing, I see it as dynamically adjusting risk—a common technique in trend-following strategies.  

The resulting portfolio balances the long and short legs by dynamically adjusting stock weights to achieve the target volatility. The portfolios are rebalanced weekly to reflect changes in volatility over time. For simplicity, I haven’t factored in transaction costs in this analysis.


## Performance Analysis  

### Equal-Weighted Portfolio  

Let’s look at the performance of the equal-weighted long-short portfolio. The main metrics here are return, volatility, and Sharpe ratio—annualized, of course.  

What stands out is that the low-volatility portfolio delivers much higher returns than the high-volatility one. As expected, the low-volatility stocks show the lowest total volatility, while the high-volatility stocks show the highest. This results in the low-volatility portfolio performing better in terms of risk-adjusted returns.  

But there’s a problem. Since the long portfolio (low-volatility stocks) is much less volatile than the short portfolio (high-volatility stocks), the long-short portfolio becomes unbalanced, which hurts its performance.  



![Figure 3](/assets/2024-12-15-low-volatility-factor/barplot_metrics_ew.png)  

**Figure 3**: Geometric Return, Volatility, and Sharpe Ratio for equal-weighted portfolios (before volatility targeting).  

### Improving Performance with Volatility Targeting  

Volatility targeting helps adjust for the imbalance between long and short positions by scaling portfolio weights based on volatility. This adjustment leads to more stable performance and a higher Sharpe ratio for both the long-only and long-short portfolios.  

Figure 4 shows how this works—volatility is more aligned across the five portfolios, reducing the mismatch. As a result, the long-short portfolio improves, benefiting from more balanced risk.  

 

![Figure 4](/assets/2024-12-15-low-volatility-factor/barplot_metrics_ew_vt.png)  

**Figure 4**: Geometric Return, Volatility, and Sharpe Ratio after volatility targeting.  

### Metrics After Volatility Targeting  

![Figure 5](/assets/2024-12-15-low-volatility-factor/perf_backtest_ew_vt.png)  

**Figure 5**: Net Asset Value of the volatility-targeted portfolio.  

| Metric                        |  Long  | Short  | Long-Short |
|-------------------------------|--------|--------|------------|
| Geometric Return (ann. %)     | 11.1   | 2.9    | 7.7        |
| Volatility (ann. %)           | 9.7    | 9.7    | 8.3        |
| Modified Sharpe Ratio (ann.)  | 1.1    | 0.3    | 0.9        |
| Maximum Drawdown (%)          | 29.5   | 36.7   | 33.6       |
| Maximum Time Under Water      | 612.0  | 1647.0 | 944.0      |

**Table 1**: Portfolio statistics for the long, short, and long-short portfolios after volatility targeting  

Figure 6 shows the portfolio weights for both the long (low-volatility) and short (high-volatility) portfolios after volatility targeting.  

As shown, the short portfolio (high-volatility stocks) now receives a much lower allocation, fluctuating between 0.2 and 0.6. Meanwhile, the low-volatility portfolio stays almost fully invested. This makes sense—high-volatility stocks naturally experience larger price swings, so less capital is allocated to them to keep the risk balanced.  

During extreme market events like the dot-com crash (2000), the financial crisis (2009), and COVID (2020), both portfolios temporarily reduce exposure, reflecting overall higher volatility.  

![Figure 6](/assets/2024-12-15-low-volatility-factor/portfolio_weights_long_short_vol_target.svg)  

**Figure 6**: Portfolio weights for Long and Short portfolios after volatility targeting.  

## Key Takeaways  

1. The low-volatility factor delivers strong risk-adjusted returns. Lower-volatility stocks tend to outperform, which contradicts the idea that higher risk always leads to higher returns.  
2. Equal weighting in long-short portfolios creates a risk imbalance. Since low-volatility stocks are naturally less risky, shorting high-volatility stocks at equal weight leads to uneven exposure and weaker performance.  
3. Volatility targeting balances risk and improves performance. Adjusting weights based on volatility evens out risk between long and short positions, leading to a more stable strategy.  
4. Dynamic risk adjustment smooths returns. Volatility-targeted portfolios adapt to market shifts, reducing drawdowns and improving long-term stability.  

A simple volatility-targeting adjustment makes a long-short portfolio more stable and effective. In the next post, I’ll explore how combining multiple factors can further enhance results.
  
