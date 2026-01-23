---
layout: post
title: "Good Reads"
date: 2025-04-20
categories: [Quants]
---

## Notes

A running list of articles and papers I've found interesting, mostly around cross-sectional asset pricing, machine learning models, and quant investing.

### Machine Learning + Asset Pricing

**[Artificial Intelligence Asset Pricing Models](https://ssrn.com/abstract=5103546)**  
*Kelly et al. (2025)*  
Uses transformers to learn the stochastic discount factor from raw panel data. Introduces the transformer architecture in a clean way and explicitly learns cross-stock structure.

**[Building Cross-Sectional Systematic Strategies by Learning to Rank](https://ssrn.com/abstract=3751012)**  
*Poh et al. (2021)*  
Applies learning-to-rank techniques to directly optimize for cross-sectional ordering instead of predicting returns. Tightly aligned with how quant signals are actually used.

### Tabular Foundation Models

**[TabPFN-2.5: Advancing the State of the Art in Tabular Foundation Models](https://arxiv.org/abs/2511.08667)**  
*Grinsztajn et al. (2024)*  
A pre-trained model for tabular data that learns general patterns across many datasets, then predicts on new tables with little or no tuning. Promising for learning cross-sectional structure, but I'm still worried about scalability and potential information leakage in point-in-time backtests.

**[TabPFN (YouTube)](https://www.youtube.com/watch?v=IpqBLWueeog)**  
Video overview of TabPFN and how it works for tabular prediction.

### Return Predictability

**[How Global is Predictability? The Power of Financial Transfer Learning](https://ssrn.com/abstract=4620157)**  
*Hellum et al. (2023)*  
Asks whether return predictability is global or country-specific. Key takeaway: predictability is overwhelmingly global (94 to 96% of the signal). Local adjustments help at the margin, but the global model dominates out of sample.

### Anomaly Replication

**[Replicating Anomalies](https://ssrn.com/abstract=2961979)**  
*Hou et al. (2017)*  
Compiles 447 anomalies and shows most lose significance once microcaps are controlled (NYSE breakpoints, value-weighted returns) and stronger t-cutoffs are applied. Once you remove small and micro-caps, a lot of the "anomalies" just don't survive.

### Risk Management

**[Risk Everywhere: Modeling and Managing Volatility](https://www.aqr.com/Insights/Research/Working-Paper/Risk-Everywhere-Modeling-and-Managing-Volatility)**  
*Bollerslev et al.*  
Examines realized volatility patterns across 50+ commodities, currencies, equity indices, and fixed-income instruments. Uses panel-based estimation to achieve superior out-of-sample risk forecasts. Their best vol model only improves performance by about 50 bps versus a simple rolling volatility model.

### Limits to Arbitrage / Capacity

**[Bottom-Up Capacity Constraints and the Limits of Anomaly Profitability](https://papers.ssrn.com/sol3/results.cfm?txtKeyWords=Bottom-Up%20Capacity%20Constraints%20and%20the%20Limits%20of%20Anomaly%20Profitability)**  
*Cartea et al. (2025)*  
Argues that asset-level capacity constraints sharply limit anomaly scalability. Profitability falls once realistic trading capacity is imposed. One of the few papers that really digs into the mechanics of what's scalable.
