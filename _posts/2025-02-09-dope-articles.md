---
layout: post
title: "Reading and Tools"
date: 2025-04-20
last_modified_at: 2026-08-22
categories: [Quants]
article_label: Reading list · Research and software
permalink: /quants/2025/04/20/reading-and-tools.html
---

This is a working shelf rather than a complete bibliography: people whose
writing I return to, software that makes research more pleasant, and papers
that have changed how I think about a problem. I have kept the list short
enough that each entry can still carry a reason for being here.

## People and learning

**[Chip Huyen](https://huyenchip.com/blog/).** Clear technical writing built
around one question at a time. Her posts are a useful reference for structure,
intuition, and deciding which details deserve space.

**[Max Halford](https://maxhalford.github.io/).** Compact, reproducible posts on
machine learning and statistics. He is particularly good at moving from a
concrete problem to code and evidence without making the article feel like a
notebook dump.

**[Open Source Quant](https://osquant.com/).** Careful quantitative-finance
research with restrained figures and explicit methodology. I like the balance
between mathematics, implementation, and economic interpretation.

**[CalmCode](https://calmcode.io/).** Short, focused tutorials that make one
tool or idea feel approachable without sanding away the important details.

**[fast.ai](https://www.fast.ai/).** Practical deep-learning courses and
writing that begin with useful models, then work back toward the ideas needed
to understand and improve them.

**[Concretum Research](https://concretumgroup.com/research/).** Applied
systematic-investing research with enough detail to see how an idea becomes a
portfolio. It is useful for thinking about robustness, execution, and which
results survive outside the backtest.

## Open-source tools

**[Polars](https://pola.rs/).** A fast DataFrame library with a thoughtful
expression API and a lazy query engine. It is a good fit for the repeated,
columnar transformations that dominate empirical research.

**[DuckLake](https://ducklake.select/).** An open lakehouse format that keeps
catalog metadata in SQL and data in open columnar files. The design is
interesting because it aims to make versioned analytical data less dependent
on a large collection of specialized services.

**[Streamlit](https://streamlit.io/).** A direct way to turn Python analysis
into an interactive data application. I find it most useful for research
diagnostics and internal tools, where a small amount of interface code can make
an experiment much easier to inspect.

## Portfolio construction

**[Enhanced Portfolio Optimization](https://www.aqr.com/Insights/Research/White-Papers/Enhanced-Portfolio-Optimization).**
*Pedersen, Babu, and Levine (2021).* This paper puts several regularized and
Bayesian portfolio methods into one framework. The practical appeal is the
same one that motivates shrinkage elsewhere: reduce the optimizer's sensitivity
to noisy inputs without erasing economically meaningful differences between
assets.

## Asset pricing and return prediction

**[Artificial Intelligence Asset Pricing Models](https://ssrn.com/abstract=5103546).**
*Kelly et al. (2025).* Uses transformers to learn a stochastic discount factor
from panel data and, importantly, lets the model learn cross-stock structure
rather than treating each observation in isolation.

**[Building Cross-Sectional Systematic Strategies by Learning to Rank](https://ssrn.com/abstract=3751012).**
*Poh et al. (2021).* Optimizes cross-sectional ordering directly instead of
first predicting returns. That objective is closely aligned with the way many
stock signals are ultimately used.

**[How Global Is Predictability? The Power of Financial Transfer Learning](https://ssrn.com/abstract=4620157).**
*Hellum et al. (2023).* Asks whether return predictability is global or
country-specific. The main result is that shared structure carries most of the
signal, while local adaptation helps at the margin.

**[Replicating Anomalies](https://ssrn.com/abstract=2961979).**
*Hou et al. (2017).* Re-examines hundreds of published anomalies using stricter
breakpoints, value weighting, and higher statistical hurdles. It is a useful
reminder that an apparent return pattern can be a micro-cap or specification
effect rather than a scalable source of return.

**[TabPFN-2.5: Advancing the State of the Art in Tabular Foundation Models](https://arxiv.org/abs/2511.08667).**
*Grinsztajn et al. (2025).* A pre-trained model for tabular prediction that can
adapt to new tables with little tuning. The approach is promising for
cross-sectional work, though point-in-time integrity, training-data overlap,
and scale need especially careful treatment in financial applications.

## Risk, costs, and capacity

**[Risk Everywhere: Modeling and Managing Volatility](https://www.aqr.com/Insights/Research/Working-Paper/Risk-Everywhere-Modeling-and-Managing-Volatility).**
*Bollerslev et al.* Studies realized volatility across commodities, currencies,
equity indexes, and fixed income. I like the comparison with simple rolling
volatility: the more elaborate panel model helps, but the economic improvement
is modest enough to keep the benchmark honest.

**[Bottom-Up Capacity Constraints and the Limits of Anomaly Profitability](https://ssrn.com/abstract=5797502).**
*Cartea et al. (2025).* Builds capacity from the assets and trades underneath a
strategy rather than applying one coarse top-down haircut. The paper is useful
because it connects published anomaly returns to the mechanics of what can
actually be traded.
