---
layout: post
title: "Good Reads"
date: 2025-04-20
last_modified_at: 2026-08-22
categories: [Quants]
article_mark: /assets/brand/quant-notes-mark.svg
article_label: Reading list · Quantitative research
---

A curated list of research I return to, rather than a complete bibliography.
The common thread is practical quantitative work: forming a good question,
testing it carefully, and explaining the result without hiding the important
choices.

## Research blogs

**[Chip Huyen](https://huyenchip.com/blog/).** Clear technical writing built
around one question at a time. Her posts are a
useful reference for structure, intuition, and deciding which details deserve
space.

**[Max Halford](https://maxhalford.github.io/).** Compact, reproducible posts on
machine learning and statistics. Particularly
good at moving from a concrete problem to code and evidence without making the
article feel like a notebook dump.

**[OSQuant](https://osquant.com/).** Careful quantitative-finance research with
restrained figures and explicit
methodology. I like the balance between mathematical detail, implementation,
and economic interpretation.

**[Concretum Research](https://concretumgroup.com/research/).** Applied
systematic-investing research with enough detail to understand how the
idea becomes a portfolio. Useful for thinking about robustness, execution, and
which results matter outside the backtest.

## Portfolio construction

**[Enhanced Portfolio Optimization](https://www.aqr.com/Insights/Research/White-Papers/Enhanced-Portfolio-Optimization).**
*Pedersen, Babu, and Levine (2020).* Reframes several regularized and Bayesian
portfolio methods in one framework.
The practical appeal is the same one that motivates shrinkage elsewhere:
reduce the optimizer's sensitivity to noisy inputs while retaining economically
meaningful differences between assets.

## Machine learning and asset pricing

**[Artificial Intelligence Asset Pricing Models](https://ssrn.com/abstract=5103546)**  
*Kelly et al. (2025)*  
Uses transformers to learn the stochastic discount factor from raw panel data. Introduces the transformer architecture in a clean way and explicitly learns cross-stock structure.

**[Building Cross-Sectional Systematic Strategies by Learning to Rank](https://ssrn.com/abstract=3751012)**  
*Poh et al. (2021)*  
Applies learning-to-rank techniques to directly optimize for cross-sectional ordering instead of predicting returns. Tightly aligned with how quant signals are actually used.

## Tabular foundation models

**[TabPFN-2.5: Advancing the State of the Art in Tabular Foundation Models](https://arxiv.org/abs/2511.08667)**  
*Grinsztajn et al. (2024)*  
A pre-trained model for tabular data that learns general patterns across many datasets, then predicts on new tables with little or no tuning. Promising for learning cross-sectional structure, but I'm still worried about scalability and potential information leakage in point-in-time backtests.

**[TabPFN (YouTube)](https://www.youtube.com/watch?v=IpqBLWueeog)**  
Video overview of TabPFN and how it works for tabular prediction.

## Return predictability

**[How Global is Predictability? The Power of Financial Transfer Learning](https://ssrn.com/abstract=4620157)**  
*Hellum et al. (2023)*  
Asks whether return predictability is global or country-specific. Key takeaway: predictability is overwhelmingly global (94 to 96% of the signal). Local adjustments help at the margin, but the global model dominates out of sample.

## Anomaly replication

**[Replicating Anomalies](https://ssrn.com/abstract=2961979)**  
*Hou et al. (2017)*  
Compiles 447 anomalies and shows most lose significance once microcaps are controlled (NYSE breakpoints, value-weighted returns) and stronger t-cutoffs are applied. Once you remove small and micro-caps, a lot of the "anomalies" just don't survive.

## Risk management

**[Risk Everywhere: Modeling and Managing Volatility](https://www.aqr.com/Insights/Research/Working-Paper/Risk-Everywhere-Modeling-and-Managing-Volatility)**  
*Bollerslev et al.*  
Examines realized volatility patterns across 50+ commodities, currencies, equity indices, and fixed-income instruments. Uses panel-based estimation to achieve superior out-of-sample risk forecasts. Their best vol model only improves performance by about 50 bps versus a simple rolling volatility model.

## Limits to arbitrage and capacity

**[Bottom-Up Capacity Constraints and the Limits of Anomaly Profitability](https://papers.ssrn.com/sol3/results.cfm?txtKeyWords=Bottom-Up%20Capacity%20Constraints%20and%20the%20Limits%20of%20Anomaly%20Profitability)**  
*Cartea et al. (2025)*  
Argues that asset-level capacity constraints sharply limit anomaly scalability. Profitability falls once realistic trading capacity is imposed. One of the few papers that really digs into the mechanics of what's scalable.
