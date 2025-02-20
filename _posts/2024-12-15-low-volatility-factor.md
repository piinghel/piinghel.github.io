---
layout: post
title: "The Low Volatility Factor: A Boring Way to Make Money?"
date: 2024-12-15
categories: [Quant]
---



## The Low-Volatility Factor: A Steady Approach  

The **low-volatility factor** is a well-known idea in factor investing. It’s based on a simple observation: stocks that move **more gradually** tend to outperform their more volatile counterparts **on a risk-adjusted basis**.  

But wait—shouldn’t higher risk mean higher returns? Not always. In this post, I’ll look at whether that assumption holds up.  

I’ll walk through how to build a **long-short portfolio** using the **low-volatility factor** in the **Russell 1000**. We’ll also see how **volatility targeting** can help refine the strategy.  


## Tradeable Universe  

First, let’s define the universe. I’m using the **Russell 1000**, which includes the **largest U.S. stocks**. To keep it realistic, I filter out those trading below **$5**, which are less liquid and more prone to erratic moves.  

The dataset spans **1995 to 2024**, covering about **3,300 stocks** as companies come and go. At any given time, there are around **1,000 tradeable stocks**. Since I’m using **point-in-time constituents**, there’s no **survivorship bias**—we’re not just looking at the winners.  

![Figure 1](/assets/2024-12-15-low-volatility-factor/nr_stocks.svg)  

**Figure 1**: Number of tradeable stocks over time.

### Defining the Low Volatility Factor

The **low-volatility factor** focuses on stocks that move **more gradually** rather than making sharp swings. To measure this, I calculate volatility using three relatively short time windows:  

- **5-day volatility**  
- **10-day volatility**  
- **21-day volatility**  

These windows might seem short, but they help track **recent price movements** while staying reactive to shifts in volatility. Longer windows could smooth things out more, but they also take longer to adjust when market conditions change. A mix of short windows balances responsiveness with stability.  

On average, **volatility is 33%**, with most stocks falling between **18% and 39%** and a median of **26%**. Since some stocks experience extreme price swings, I **winsorized the data**, capping the lower bound at **5%** and the upper bound at **200%**. This helps prevent outliers from distorting the analysis and also explains the **small bump at the right tail** of the distribution.  

Here’s what the **distribution of annualized volatilities** looks like across **3,300 stocks** in the dataset. The shape is **positively skewed**, meaning most stocks have moderate volatility, but a few are far more erratic.  

![Figure 2](/assets/2024-12-15-low-volatility-factor/distribution_volatilities.svg)  

**Figure 2**: Histogram showing the distribution of volatility across the tradeable universe.  



### Does Low Volatility Actually Matter?

To see if lower volatility has any predictive power, I checked its correlation with **forward returns (next 10 days)** and the **Sharpe ratio**.  

- **Returns**: The Pearson correlation is **0.03**, meaning higher-volatility stocks tend to have slightly higher returns. But when switching to **Spearman correlation**, which is less sensitive to outliers, the relationship disappears (**0.00**).  
- **Sharpe Ratio**: The trend flips. Pearson shows a **-0.035** correlation, and Spearman strengthens that to **-0.04**—suggesting that more volatile stocks tend to have **lower risk-adjusted returns**.  

These numbers might seem small, but in finance, that’s expected. The **signal-to-noise ratio is low**, and even weak relationships can matter when applied systematically.



## Portfolio Bucketing  

To construct the portfolios, I performed a **cross-sectional ranking** of stocks based on their volatilities at each point in time. Specifically, I ranked all stocks in the universe by their volatility and mapped these ranks to a uniform **0 to 1** distribution. Then, I assigned each stock to one of five portfolios according to its percentile rank.  

Let $r_{i,t}$ be the cross-sectional rank of stock $i$ at point $t$ based on its volatility, and $N$ be the total number of stocks at a given time. The normalized rank is computed as:  

$$
\text{Rank Score}_i = \frac{r_{i,t}}{N}
$$  

Using this score, stocks are bucketed into the following volatility-based portfolios:  

- **Portfolio 1**: Lowest 10% of stocks ($ 0 \leq \text{Rank Score} < 0.1 $) → **Low volatility**  
- **Portfolio 2**: 10% to 20% of stocks ($ 0.1 \leq \text{Rank Score} < 0.2 $)  
- **Portfolio 3**: 20% to 80% of stocks ($ 0.2 \leq \text{Rank Score} < 0.8 $)  
- **Portfolio 4**: 80% to 90% of stocks ($ 0.8 \leq \text{Rank Score} < 0.9 $)  
- **Portfolio 5**: Highest 10% of stocks ($ 0.9 \leq \text{Rank Score} \leq 1.0 $) → **High volatility**  

This process ensures that each stock's portfolio assignment is determined **relative to the cross-sectional volatility distribution** at that specific point.  

### Rebalancing  

The portfolios are rebalanced **weekly** to reflect changes in volatility over time. For simplicity, I haven’t factored in transaction costs in this analysis.  

## Constructing a Long-Only and Long-Short Portfolio  

Once the stocks are bucketed, I created two types of portfolios: **equal-weighted** and **volatility-targeted**.  

### Equal-Weighted Portfolio 

In the **equal-weighted portfolio**, all stocks are given equal weight, and I remain fully invested at all times. However, this creates a mismatch between the volatilities of the long and short positions, which I’ll explain further below. To construct the long-short portfolio, I simply take the difference between the low-volatility (P1) and high-volatility portfolios (P5).  

### Volatility-Targeted Portfolio  

**Volatility targeting** adjusts stock weights based on their volatility to create a more stable portfolio. Here’s how it works:  

1. **Compute the Volatility Scaling Factor**: For each stock, calculate:  
   $$
   \text{vol_ratio} = \frac{\sigma_{target}}{\hat{\sigma}_{i,t}}
   $$  
   where:  
   - $\sigma_{target} = 20\%$ is an arbitrary target, chosen because it’s close to the average stock volatility. This ensures that the overall portfolio volatility remains around **8%**.  
   - ${\hat{\sigma}_{i,t}}$ represents the stock’s estimated future volatility, typically calculated using a rolling **60-day standard deviation**. More complex models could be used, but we’ll keep it simple for now.  

2. **Adjust Equal Weights**: Multiply the equal weight of each stock by its $\text{vol\_ratio}$:  
   $$
   w_i = \text{equal_weight} \times \text{vol_ratio}
   $$  

3. **Cap Individual Weights**: Ensure no stock weight exceeds **4%** to prevent excessive concentration. This cap is somewhat arbitrary and depends on the number of stocks in the portfolio and possibly other factors, such as sector diversification or liquidity constraints.  

4. **Constrain Portfolio Exposure**: Ensure that the total portfolio weight does not exceed **1** (i.e., fully invested). During periods of high volatility, the total weight may decrease to limit risk. While this may resemble **market timing**, I see it as **dynamically adjusting risk**—a common technique in **trend-following** strategies.  

The resulting portfolio balances the **long** and **short** legs by dynamically adjusting stock weights to achieve the target volatility.  


 
## Performance Analysis  

### Equal-Weighted Portfolio  

The performance of the **equal-weighted long-short portfolio** is summarized below. The key metrics include **return, volatility, and Sharpe ratio**—all annualized.  

Interestingly, the **low-volatility portfolio** delivers significantly higher returns than the **high-volatility portfolio**. As expected, the lowest-volatility stocks also exhibit the lowest total volatility, while the highest-volatility stocks show the highest. As a result, the low-volatility portfolio achieves **better risk-adjusted performance**.  

However, there’s a catch. Since the **long portfolio (low-volatility stocks)** is much less volatile than the **short portfolio (high-volatility stocks)**, the **long-short portfolio ends up unbalanced**, leading to poor performance.  

**Performance Before Volatility Targeting**:  

![Figure 3](/assets/2024-12-15-low-volatility-factor/barplot_metrics_ew.png)  

**Figure 3**: Geometric Return, Volatility, and Sharpe Ratio for equal-weighted portfolios (before volatility targeting).  

### Improving Performance with Volatility Targeting  

Volatility targeting helps correct the **imbalance between long and short positions** by scaling portfolio weights based on volatility. This adjustment leads to **more stable performance** and a **higher Sharpe ratio** for both long-only and long-short portfolios.  

Figure 4 shows the effect—volatility is now **more aligned across the five portfolios**, reducing the mismatch. As a result, the **long-short portfolio improves**, benefiting from a more balanced risk distribution.  

**Performance After Volatility Targeting**:  

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

**Table 1**: Portfolio statistics for the long, short, and long-short portfolios after volatility targeting.  

Finally, **Figure 6** shows the **portfolio weights for the long (low-volatility) and short (high-volatility) portfolios** after volatility targeting.  

Clearly, the short portfolio (high-volatility stocks) receives a **much lower allocation**, fluctuating between **0.2 and 0.6**. Meanwhile, the **low-volatility portfolio stays almost fully invested**. This makes sense—since the high-volatility stocks naturally have larger price swings, **less capital is allocated to them** to keep risk balanced.  

Notably, during extreme market events like the **dot-com crash (2000), the financial crisis (2009), and COVID (2020)**, **both portfolios temporarily reduce exposure**, reflecting increased overall volatility.  

![Figure 6](/assets/2024-12-15-low-volatility-factor/portfolio_weights_long_short_vol_target.svg)  

**Figure 6**: Portfolio weights for Long and Short portfolios after volatility targeting.  

## Key Takeaways  

1. **The low-volatility factor delivers strong risk-adjusted returns.** Lower-volatility stocks tend to outperform, contradicting the idea that higher risk always leads to higher returns.  
2. **Equal weighting in long-short portfolios creates a risk imbalance.** Since low-volatility stocks are naturally less risky, shorting high-volatility stocks at equal weight leads to uneven exposure and weaker performance.  
3. **Volatility targeting balances risk and improves performance.** Adjusting weights based on volatility evens out risk between long and short positions, leading to a more stable strategy.  
4. **Dynamic risk adjustment smooths returns.** Volatility-targeted portfolios adapt to market shifts, reducing drawdowns and improving long-term stability.  

A simple **volatility-targeting adjustment** makes a long-short portfolio **more stable and effective**. In the next post, I’ll explore how **combining multiple factors** can further enhance results.  

