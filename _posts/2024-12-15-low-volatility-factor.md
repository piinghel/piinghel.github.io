---
layout: post
title: "The Low Volatility Factor"
date: 2024-12-15
categories: [Quant]
---

### **What Is the Low Volatility Factor?**

The low-volatility factor is one of the most well-established factors in investing, consistently delivering strong risk-adjusted returns. It involves selecting stocks with historically lower price fluctuations, which tend to outperform their high-volatility counterparts. 

In this post, we’ll explore how to construct an effective long-short portfolio using the low-volatility factor, based on a classical universe: the Russell 1000. We’ll also demonstrate how volatility targeting can significantly enhance portfolio performance.

---

### **Defining the Low Volatility Factor**

The low-volatility factor is computed using a short historical window of 5, 10, and 21 days. Stocks are sorted into quintiles (five portfolios) based on their volatilities, with the lowest 10% (Portfolio 1) representing low-volatility stocks and the highest 10% (Portfolio 5) representing high-volatility stocks.

#### **Portfolio Bucketing**
Stocks are assigned to one of five groups based on their historical volatility rankings:
- **Portfolio 1**: Lowest 10% of stocks (low volatility).
- **Portfolio 5**: Highest 10% of stocks (high volatility).

#### **Rebalancing**
The portfolio is rebalanced weekly to adjust for changes in volatility over time.

---

### **Constructing a Long-Short Portfolio**

Once stocks are bucketed, we construct two types of portfolios: equal-weighted and volatility-targeted.

#### **1. Equal-Weighted Portfolio**
In the equal-weighted portfolio, all stocks receive equal weight. To ensure no single stock dominates, weights are capped at 0.05%. However, this approach results in a mismatch between the volatilities of the long and short legs, leading to poor portfolio performance.

#### **2. Volatility-Targeted Portfolio**
Volatility targeting improves portfolio stability by adjusting weights based on the estimated volatility of each stock. The key steps are:

1. **Target Volatility**: Set a target volatility of 20% annualized.
2. **Compute Volatility Ratio**: For each stock, calculate:
   $$
   \text{vol\_ratio} = \frac{\text{vol\_target}}{\text{vol\_estimated}}
   $$
   where:
   - $\text{vol\_target} = 20\%$
   - $\text{vol\_estimated}$ is the stock’s historical volatility.
3. **Adjust Equal Weights**: Multiply the equal weight of each stock by its $\text{vol\_ratio}$:
   $$
   w_i = \text{equal\_weight} \times \text{vol\_ratio}
   $$
4. **Cap Individual Weights**: Ensure no stock weight exceeds 0.05.
5. **Portfolio Weight Constraint**: Normalize the weights such that the total portfolio weight does not exceed 1. In periods of high volatility, the total weight may be lower than 1, reflecting a reduction in exposure.

The resulting portfolio balances the long and short legs by dynamically adjusting stock weights to achieve the target volatility.

---

### **Performance Analysis**

#### **Equal-Weighted Portfolio**
The performance of the equal-weighted long-short portfolio is summarized below. This approach results in significant volatility mismatch and poor performance.

**Metrics Before Volatility Targeting**:
| Metric                | Portfolio 1 (Long) | Portfolio 5 (Short) | Long-Short |
|-----------------------|--------------------|---------------------|------------|
| Geometric Return (%)  | 11.88             | 5.08                | -5.77      |
| Volatility (%)        | 12.22             | 38.81               | 32.83      |
| Sharpe Ratio          | 0.98              | 0.32                | -0.02      |



---

![Figure 1](/assets/2024-12-15-low-volatility-factor/barplot_metrics_ew.png)




**Figure 1**: Include the chart showing the NAV of the equal-weighted portfolio (before volatility targeting).

---

### **Improving Performance with Volatility Targeting**

Volatility targeting adjusts weights to balance risk between the long and short legs, resulting in more stable performance.

#### **Metrics After Volatility Targeting**:
| Metric                | Portfolio 1 (Long) | Portfolio 5 (Short) | Long-Short |
|-----------------------|--------------------|---------------------|------------|
| Geometric Return (%)  | 11.04             | 3.35                | 7.70       |
| Volatility (%)        | 9.75              | 9.72                | 8.32       |
| Sharpe Ratio          | 1.13              | 0.34                | 0.92       |

**Figure 2**: Include the chart showing the NAV of the volatility-targeted portfolio (after volatility targeting).

---

### **Key Takeaways**

1. The low-volatility factor has historically delivered strong risk-adjusted returns.
2. Equal weighting in long-short portfolios leads to volatility imbalances and poor performance.
3. Volatility targeting effectively balances the risks in long and short legs, significantly improving portfolio stability and performance.

Harnessing the low-volatility factor requires thoughtful portfolio construction. By incorporating volatility targeting, investors can achieve a well-balanced and high-performing long-short portfolio.
