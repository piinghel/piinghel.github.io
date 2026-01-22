---
layout: post
title: "Good Reads"
date: 2025-04-20
categories: [Quants]
---

## Notes

This is just a running list of articles, papers, and blog posts I've found interesting — mostly around cross-sectional asset pricing, machine learning models, and quant investing. I'll keep adding to it over time as I go deeper.

Some of this is academic, some more hands-on.


### Machine Learning + Asset Pricing

**[Artificial Intelligence Asset Pricing Models](https://ssrn.com/abstract=5103546)**  
*Bryan T. Kelly, Boris Kuznetsov, Semyon Malamud, Teng Andrea Xu (2025)*  
Uses transformers to directly learn the stochastic discount factor from raw panel data. A step toward end‑to‑end portfolio optimization. My take: it introduces the transformer architecture in a clean way and explicitly learns cross‑stock structure, which is exactly what most factor models struggle to capture.

**[Building Cross-Sectional Systematic Strategies by Learning to Rank](https://ssrn.com/abstract=3751012)**  
*Daniel Poh, Bryan Lim, Stefan Zohren, Stephen Roberts (2021)*  
Applies learning-to-rank techniques to directly optimize for cross-sectional ordering instead of predicting returns. Tightly aligned with how quant signals are actually used.

### Tabular Foundation Models

**[TabPFN-2.5: Advancing the State of the Art in Tabular Foundation Models](https://arxiv.org/abs/2511.08667)**  
*Léo Grinsztajn, Klemens Flöge, Oscar Key, Felix Birkel, Philipp Jund, Brendan Roof, Benjamin Jäger, Dominik Safaric, Simone Alessi, Adrian Hayler, Mihir Manium, Rosen Yu, Felix Jablonski, Shi Bin Hoo, Anurag Garg, Jake Robertson, Magnus Bühler, Vladyslav Moroshan, Lennart Purucker, Clara Cornu, Lilly Charlotte Wehrhahn, Alessandro Bonetto, Bernhard Schölkopf, Sauraj Gambhir, Noah Hollmann, Frank Hutter*  
A pre-trained model for tabular data (think Excel‑style tables) that learns general patterns across many datasets, then predicts on new tables with little or no tuning. This version is faster and more accurate on many tabular benchmarks. My take: it's promising for learning cross‑sectional structure, but I'm still worried about scalability and potential information leakage in point‑in‑time backtests.

**[TabPFN (YouTube)](https://www.youtube.com/watch?v=IpqBLWueeog)**  
Video overview of TabPFN and how it works for tabular prediction.

### Return Predictability

**[How Global is Predictability? The Power of Financial Transfer Learning](https://ssrn.com/abstract=4620157)**  
*Oliver Hellum, Lasse Heje Pedersen, Anders Rønn-Nielsen (2023)*  
Asks whether return predictability is mostly global vs. country-specific. Introduces GENet (a transfer-learning/elastic-net style regularization) that shrinks local coefficients toward a global model. Key takeaway: predictability is overwhelmingly global (~94–96% of the signal). Local adjustments help at the margin, but the global model tends to dominate out of sample.

### Anomaly Replication

**[Replicating Anomalies](https://ssrn.com/abstract=2961979)**  
*Kewei Hou, Chen Xue, Lu Zhang (2017)*  
Compiles 447 anomalies and shows most lose significance once microcaps are controlled (NYSE breakpoints, value‑weighted returns) and stronger t‑cutoffs are applied; many remaining effects shrink materially. Even among "significant" anomalies, q‑factor alphas largely vanish, suggesting markets are more efficient than the original literature implies. Once you remove small and micro‑caps, a lot of the "anomalies" just don't survive or are far less profitable.

### Risk Management

**[Risk Everywhere: Modeling and Managing Volatility](https://www.aqr.com/Insights/Research/Working-Paper/Risk-Everywhere-Modeling-and-Managing-Volatility)**  
*Tim Bollerslev, Benjamin Hood, John Huss, Lasse Heje Pedersen*  
Examines realized volatility patterns across 50+ commodities, currencies, equity indices, and fixed-income instruments. Uses panel-based estimation to achieve superior out-of-sample risk forecasts. Their best vol model only improves performance by about 50 bps versus a simple rolling volatility model, which was a bit disappointing to see.

### Limits to Arbitrage / Capacity

**[Bottom-Up Capacity Constraints and the Limits of Anomaly Profitability](https://papers.ssrn.com/sol3/results.cfm?txtKeyWords=Bottom-Up%20Capacity%20Constraints%20and%20the%20Limits%20of%20Anomaly%20Profitability)**  
*Álvaro Cartea, Mihai Cucuringu, Qi Jin, Jiexiu Zhu (2025)*  
Argues that asset‑level capacity constraints sharply limit anomaly scalability; profitability falls once realistic trading capacity is imposed. A lot of anomalies are not really exploitable once you model trading frictions and capacity. It's one of the few papers that really digs into the mechanics in detail and gives a good sense of what's scalable.
