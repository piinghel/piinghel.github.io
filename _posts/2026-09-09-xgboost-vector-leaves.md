---
layout: post
title: "Can Two Return Horizons Share a Tree?"
description: "A small XGBoost comparison finds mixed ranking gains from sharing tree splits across return horizons."
permalink: /quants/xgboost-vector-leaves.html
toc: false
show_date: false
date: 2026-09-09
categories: ["Machine learning"]
---

XGBoost’s [vector-leaf model](https://xgboost.ai/2026/08/25/introducing-the-xgboost-vector-leaf-model) made me curious: would sharing tree splits help predict two related return horizons?

I compared separate XGBoost models with one vector-leaf model for 20- and 60-day targets: future mean daily excess return divided by future daily return volatility. Same features, chronological splits and eligible observations. Tuning was deliberately small. The procedures still differ in joint versus separate model selection and training budgets, so this does not isolate tree architecture perfectly.

Here is the ranking result. ICIR is mean daily cross-sectional Spearman correlation divided by its sample standard deviation, **unannualized**. Each cell shows separate → shared trees.

<div markdown="1">
<p class="table-caption"><strong>Table 1: Shared trees give mixed ranking results.</strong> Unannualized ICIR, separate → shared trees.</p>

| Horizon | Full history | Ten-year window | Five-year window |
| --- | ---: | ---: | ---: |
| 20 days | 0.253 → 0.270 | 0.230 → 0.221 | 0.150 → 0.162 |
| 60 days | 0.327 → 0.331 | 0.280 → 0.272 | 0.237 → 0.231 |
{: .research-table .comparison-table }
</div>

The full sample starts in January 2000. The recent windows start in May 2016 and May 2021; all three end on 2 March 2026 because both future labels must be available. ICIR was added after the initial predictive evaluation, without refitting. These historical windows overlap and have already been inspected.

I don’t see a consistent win. The small full-history improvement at 60 days actually comes from steadier IC, despite a lower average IC. Shared trees also slightly worsen the original squared-error metric in every window, by roughly 0.10–0.35% relative to separate models.

The prediction tests are complete. **Portfolio performance still needs validation**, so I’m drawing the conclusion from ranking quality and prediction error. I don’t yet have a reliable full-history portfolio Sharpe comparison.

For now, I would keep production unchanged. Sharing splits is an interesting constraint; these results give me no reason to adopt it or keep searching settings until it looks better.
