---
layout: post
title: "Resources"
date: 2025-04-20
last_modified_at: 2026-09-05
categories: ["Resources"]
article_label: Resources · Research and software
permalink: /quants/2025/04/20/reading-and-tools.html
---

I keep this page as a short map of the questions behind the research here:
how to combine signals, turn predictions into positions, and find out whether
a result survives implementation. The papers are starting points for those
questions, not evidence that the same methods will work in my backtests.

## Writing, research, and learning

- [Chip Huyen](https://huyenchip.com/blog/) — Clear explanations of the gap between a model demo and a working system.
- [Max Halford](https://maxhalford.github.io/blog/) — Technical posts that connect intuition, small examples, and implementation. His [Bayesian linear regression walkthrough](https://maxhalford.github.io/blog/bayesian-linear-regression/) is a good place to start.
- [Bryan Kelly](https://www.bryankellyacademic.org/)
- [Gappy](https://linktr.ee/paleologo)
- [Gauthier Marti](https://gmarti.gitlab.io/)
- [Rob Carver · This Blog is Systematic](https://qoppac.blogspot.com/)
- [Open Source Quant](https://osquant.com/)
- [CalmCode](https://calmcode.io/)
- [fast.ai](https://www.fast.ai/)
- [Concretum Research](https://concretumgroup.com/research/)
- [Christoph Molnar · Interpretable Machine Learning](https://christophm.github.io/interpretable-ml-book/) — A practical, critical guide to explaining models and individual predictions.

## Software

The research repositories use Polars for tabular work and Python for estimation
and figures. I keep the blog on Jekyll: static pages, equations, and versioned
SVGs cover what these notes need. The other tools below serve different jobs;
they are not prerequisites for reproducing an article.

- [Polars](https://pola.rs/) — DataFrames with a strong expression API and lazy execution.
- [DuckLake](https://ducklake.select/) — An open lakehouse format that keeps its catalogue in SQL.
- [Streamlit](https://streamlit.io/) — Turns Python analyses into interactive internal apps.

## Portfolio construction and risk modelling

**[Enhanced Portfolio Optimization](https://www.aqr.com/Insights/Research/White-Papers/Enhanced-Portfolio-Optimization).**
*Pedersen, Babu, and Levine (2021).* Connects portfolio regularization to
estimation error. Relevant to the [joint-sizing article](/quants/2026/08/29/portfolio-optimization.html),
where changing the correlation estimate changes the optimizer's allocation.

**[Risk Everywhere: Modeling and Managing Volatility](https://www.aqr.com/Insights/Research/Working-Paper/Risk-Everywhere-Modeling-and-Managing-Volatility).**
*Bollerslev, Hood, Huss, and Pedersen (2016).* Uses common volatility patterns
across assets to improve forecasts, then examines the value of those forecasts
when trading costs and model responsiveness matter.

## Asset pricing, return prediction, and implementation

**[Artificial Intelligence Asset Pricing Models](https://www.nber.org/papers/w33351).**
*Kelly, Kuznetsov, Malamud, and Xu (2025; revised 2026).* Places a transformer
inside a stochastic discount factor. Its asset-pricing objective is different
from the stock-ranking loss used in my regression article.

**[Building Cross-Sectional Systematic Strategies by Learning to Rank](https://arxiv.org/abs/2012.07149).**
*Poh, Lim, Zohren, and Roberts (2021).* Learns the cross-sectional ordering
directly, using momentum as a case study. It motivates asking whether a
regression loss matches the portfolio decision made from its predictions.

**[How Global Is Predictability? The Power of Financial Transfer Learning](https://ssrn.com/abstract=4620157).**
*Hellum, Pedersen, and Rønn-Nielsen (2023).* Tests how much return predictability
can be shared across countries and how much must remain local.

**[Replicating Anomalies](https://ssrn.com/abstract=2961979).**
*Hou et al. (2017).* Tests how much published predictability survives stricter
implementation choices.

**[TabPFN-2.5: Advancing the State of the Art in Tabular Foundation Models](https://arxiv.org/abs/2511.08667).**
*Grinsztajn et al. (2025).* A tabular foundation-model reference. General
tabular benchmarks are not financial validation; date splits, overlapping
targets, and the eventual trading rule still need their own tests.

**[Bottom-Up Capacity Constraints and the Limits of Anomaly Profitability](https://ssrn.com/abstract=5797502).**
*Cartea et al. (2025).* Estimates capacity from the underlying assets and trades,
rather than imposing a single top-down haircut on the strategy.
