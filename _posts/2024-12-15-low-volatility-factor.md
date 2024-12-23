---
layout: post
title: "The Low Volatility Factor"
date: 2024-12-15
categories: [Quant]
---



The **low-volatility factor** is a well-known and widely researched concept in factor investing. Simply put, it focuses on selecting stocks with smaller price swings. Interestingly, these more stable, often "boring" stocks tend to outperform their more volatile counterparts on a **risk-adjusted** basis. You might be thinking—doesn’t higher risk mean higher returns? Well, not always. In this post, I’ll dive into whether this conventional belief still holds true.

I’ll show you how to construct a **simple long-short portfolio** using the low-volatility factor, drawing on the **Russell 1000 universe**. I’ll also explain how **volatility targeting** can further enhance your strategy’s performance.



### **Tradeable Universe**

Let’s start by defining our tradeable universe. I’m using the **Russell 1000** index, which includes the largest 1000 companies in the U.S. Over time, I’ve excluded stocks trading below $5. The analysis spans from **1995 to 2024**, and I’ve visualized the number of tradable stocks during this period, which hovers around 1000. It’s also worth mentioning that we have over **3,300 different stocks** in our universe, as stocks enter and exit over time. Most importantly, these are the **point-in-time constituents**, helping to avoid **survivorship bias**. Check out the figure below for a visual representation.

![Figure 1](/assets/2024-12-15-low-volatility-factor/nr_stocks.svg)

**Figure 1**: Number of tradable stocks over time.


### **Defining the Low Volatility Factor**

The **low-volatility factor** targets stocks that have historically demonstrated lower price fluctuations. To identify these stocks, I calculated volatility over three different time windows: **5**, **10**, and **21 days**. 

For a more robust measure of volatility, I use multiple time windows:

- **5-day volatility**
- **10-day volatility**
- **21-day volatility**

Each stock’s combined volatility score determines which quintile it falls into. While you could use just one time window for simplicity, this combined approach helps smooth out short-term noise and generally delivers better results in the long run (before considering transaction costs). Below, you can see the distribution of annualized volatilities across over **3,000 stocks** throughout the entire sample period. I winsorized the data, capping the lower bound at 5% and the upper bound at 200%. The average volatility is 33%, with quartile 1 at 26%, quartile 3 at 39%, and a median of 26%. The winsorization explains the small bump seen at the right tail of the distribution.

The distribution of volatilities shows a **positively skewed** pattern, resembling a **log-normal** distribution. This suggests that while the majority of stocks have low volatility, a smaller number of stocks exhibit high volatility.

![Figure 2](/assets/2024-12-15-low-volatility-factor/distribution_volatilities.svg)

**Figure 2**: Histogram showing the distribution of volatility across the tradeable universe.



### **A Quick Look at the Volatility Distribution**

#### **Portfolio Bucketing**

Next, I mapped each stock’s volatility score to a uniform **0 to 1** distribution and categorized them into one of five portfolios based on their volatility rankings:

- **Portfolio 1**: Lowest 10% of stocks (low volatility)
- **Portfolio 2**: 10% to 20% of stocks
- **Portfolio 3**: 20% to 80% of stocks
- **Portfolio 4**: 80% to 90% of stocks
- **Portfolio 5**: Highest 10% of stocks (high volatility)

#### **Rebalancing**

The portfolios are rebalanced **weekly** to reflect changes in volatility over time. For simplicity, I haven’t factored in transaction costs in this analysis.



### **Constructing a Long-Only and Long-Short Portfolio**

Once the stocks are bucketed, I created two types of portfolios: **equal-weighted** and **volatility-targeted**.

#### **1. Equal-Weighted Portfolio**

In the **equal-weighted portfolio**, all stocks are given equal weight, and I remain fully invested at all times. However, this creates a mismatch between the volatilities of the long and short positions, which I will explain further below. To construct the long-short portfolio, I simply take the difference between the low-volatility and high-volatility portfolios.

#### **2. Volatility-Targeted Portfolio**

**Volatility targeting** adjusts the weight of each stock based on its volatility to stabilize the portfolio. Here’s how it works:

1. **Target Volatility**: Set a target volatility of 20% annualized.
2. **Compute Volatility Ratio**: For each stock, calculate:
   $$
   \text{vol_ratio} = \frac{\text{vol_target}}{\text{vol_estimated}}
   $$
   where:
   - $\text{vol_target} = 20\%$
   - $\text{vol_estimated}$ is the stock's historical volatility.
3. **Adjust Equal Weights**: Multiply the equal weight of each stock by its $\text{vol\_ratio}$:
   $$
   w_i = \text{equal_weight} \times \text{vol_ratio}
   $$

4. **Cap Individual Weights**: Ensure no stock weight exceeds 0.05.
5. **Portfolio Weight Constraint**: Ensure that the portfolio weights total 1. In periods of high volatility, the total weight may be reduced to limit exposure. While this may seem like market timing, I view it more as **dynamically adjusting risk**—a technique commonly used in **CTA** strategies.

The resulting portfolio balances the long and short legs by dynamically adjusting stock weights to achieve the target volatility.



### **Performance Analysis**

#### **Equal-Weighted Portfolio**

The performance of the equal-weighted long-short portfolio is summarized below. The metrics visualized include return, volatility, and Sharpe ratio—all annualized. Surprisingly, the return in the low-volatility portfolio is significantly higher than in the high-volatility portfolio, which contradicts the **CAMP** theorem. As expected, the lowest-volatility stocks exhibit the lowest volatility, while the highest-volatility stocks show the highest volatility. Consequently, the low-volatility portfolio exhibits significantly better **risk-adjusted performance**. However, the mismatch between the low-volatility and high-volatility portfolios results in a less-than-optimal performance for the long-short portfolio.

**Metrics Before Volatility Targeting**:

![Figure 3](/assets/2024-12-15-low-volatility-factor/barplot_metrics_ew.svg)

**Figure 3**: Bar chart showing Geometric Return, Volatility, and Sharpe Ratio for equal-weighted portfolios (before volatility targeting).

---

### **Improving Performance with Volatility Targeting**

As shown in the previous figure, volatility targeting adjusts weights to balance risk between the long and short legs, resulting in more stable performance. After applying volatility targeting, we see that the volatility is much more stable across the portfolios. This adjustment significantly improves the **Sharpe ratio** for both the long-short portfolio and the long-only portfolios. The figure below demonstrates the improvement.

![Figure 4](/assets/2024-12-15-low-volatility-factor/barplot_metrics_ew_vt.svg)

#### **Metrics After Volatility Targeting**:

![Figure 5](/assets/2024-12-15-low-volatility-factor/perf_backtest_ew_vt.png)

**Figure 5**: Net Asset Value of the volatility-targeted portfolio (after volatility targeting).


### **Key Takeaways**

1. The low-volatility factor has historically delivered strong **risk-adjusted returns**.
2. Equal weighting in long-short portfolios leads to volatility imbalances, resulting in suboptimal performance.
3. Volatility targeting effectively balances risk between long and short positions, significantly improving portfolio stability and performance.

Harnessing the low-volatility factor requires careful portfolio construction. By incorporating volatility targeting, investors can create a more balanced and high-performing long-short portfolio.




