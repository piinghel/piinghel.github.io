---
layout: post
title: "Following portfolio P&L back to the positions"
description: "A small dashboard for exploring portfolio contributions and the positions behind them."
article_label: Portfolio attribution · Working draft
permalink: /drafts/portfolio-dashboard/
published: false
show_date: false
toc: false
navigation: false
---

I built a small Streamlit dashboard to connect portfolio performance with the positions and exposures behind it.

Start with a drawdown or an unusually strong month. Select that period, inspect the stock, sector or industry contributions, then open a stock directly from its bar. Prices, cumulative P&L, position size, predictor contributions and model inputs sit on the same date axis. Selecting a shorter period recalculates the analysis across the views.

That shared context matters to me. I want to see how a position changed while its price moved, then inspect the saved prediction behind a holding decision. Factor attribution provides another view of the same portfolio, with residual and uncovered P&L kept explicit. The decomposition helps identify questions to investigate; it does not establish what caused a return.

[Try the dashboard](https://piinghel-portfolio-pnl.streamlit.app/). The public version uses entirely synthetic data, including fictional companies and predictions. The [source code](https://github.com/piinghel/portfolio-pnl-dashboard) and data format are available for anyone who wants to explore it with their own portfolio.
