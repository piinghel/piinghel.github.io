---
layout: post
title: "Multiple Testing in the Age of AI"
description: "How a faster search changes the evidence needed to trust a research result."
permalink: /quants/multiple-testing-in-the-age-of-ai.html
toc: true
date: 2026-10-27
categories: ["Research methods"]
article_label: Research methods · Multiple testing
---

When I research a quantitative idea, there are usually several ways to express
it: a different signal, lookback or portfolio construction. AI makes it easier
to explore those variations and suggest the next comparison.

The problem is familiar: the best result becomes more impressive as the search
gets larger, even if the ideas have no edge. Multiple testing and research
selection have been studied extensively for decades. AI makes this discipline
more important by making it easier to try and refine more ideas on the same
limited history.

## A larger search produces better-looking winners

Suppose I test 100 strategies using independent, valid one-sided tests at the
5% level, and none has a real edge. The chance that at least one looks
significant is

$$
1-(1-0.05)^{100} \approx 99.4\%.
$$

The selected result needs to be interpreted in light of the other attempts.

Strategies are often related: a 20-day and a 21-day lookback do not provide two
independent shots. With a pairwise correlation of 0.5, my simulation found at
least one false discovery in 56% of exercises instead of 99%.

## Corrections trade discoveries for confidence

I simulated 20,000 exercises with 100 independent one-sided Gaussian tests.
First all true effects are zero. Then 10 are positive, shifting their test
statistics by 2.5 standard errors. Every method uses a nominal 5% level.

| Method | All null: at least one false discovery | 10 real signals: at least one false discovery | 10 real signals: false discovery rate | 10 real signals: power |
|:--|--:|--:|--:|--:|
| Unadjusted tests | 99.4% | 98.9% | 34.5% | 80.4% |
| Bonferroni | 5.0% | 4.3% | 1.7% | 21.3% |
| Holm | 5.0% | 4.5% | 1.7% | 21.5% |
| Benjamini–Hochberg | 5.1% | 19.5% | 4.5% | 36.3% |

Here **power** is the average fraction of the 10 real signals detected. The
**false discovery rate** is the average fraction of selected signals that are
false, counting an exercise with no selections as zero. It is different from
the probability of making even one false discovery.

Bonferroni and Holm aim to control the probability of any false discovery.
Benjamini–Hochberg controls the expected proportion under suitable dependence
assumptions. Here it detects more real signals but permits a false discovery
in more individual exercises. The choice depends on the decision and the cost
of being wrong.

The simulations assume valid test statistics, known standard errors and a fixed
family, without leakage or costs. They illustrate a trade-off, not which method
will be best for a portfolio.

## Counting the trials is harder than it sounds

What counts as a trial? A different lookback, universe or metric chosen after
seeing the data can all be part of the search. Related variants are not
independent, and previous work may have used the same market history. There is
no universal way to turn all those choices into an exact number of independent
tests. I would record what I can and check sensitivity to plausible assumptions,
while recognizing that an unknown search cannot be fully corrected after the
fact. Gelman and Loken call this the
[*garden of forking paths*](https://stat.columbia.edu/~gelman/research/unpublished/p_hacking.pdf):
even a single reported analysis can reflect choices that depended on the data.

## Confirmation depends on what is independent

In another 20,000 exercises, I select the strongest of 100 independent null
ideas if it passes a one-sided 5% test, then test that idea once more.

| Confirmation test | Selected null ideas passing confirmation |
|:--|--:|
| Independent test statistic | 4.9% |
| Test statistic correlated 0.7 with its discovery statistic | 55.5% |

The second row models shared variation; it does not measure overlap between
real universes. Two universes can share stocks, dates and market shocks. Even
independent confirmation has a 5% false-positive rate for this one selected
idea; selecting again on that test introduces another search.

## Accounting for a family of strategies

White's **Reality Check** and Hansen's **Superior Predictive Ability** test
compare a family of strategies with a benchmark while accounting for the
search. Bailey and López de Prado's **Deflated Sharpe Ratio** adjusts the
interpretation of a selected Sharpe for multiple trials and non-normal returns.
Their work with co-authors on the **probability of backtest overfitting** asks
whether the in-sample winner ranks poorly in held-out partitions.

Paleologo's **Rademacher Anti-Serum** uses random sign changes to estimate the
complexity of a strategy family and incorporate it into a performance bound.
Similar strategies add less complexity than very different ones. Each method
depends on the family and assumptions supplied to it; none can repair an
unknown search or leakage. The simulations above test the simpler corrections,
not these methods.

## A few questions before trusting a result

The statistical adjustment is one part of the decision. These are the questions
I want to carry into an AI-assisted research process:

1. **What did I expect, and why?** Write down the mechanism, a simple baseline
   and what would make the idea worth pursuing. What result would make me
   reconsider the explanation?
2. **What was tried?** Record failed variants, data choices and AI iterations,
   including changes made after seeing results. Define the family being
   assessed and show how sensitive the conclusion is to the assumed search.
3. **How much evidence is there?** Report the effect and its uncertainty, and
   use an adjustment appropriate to the decision. A paired interval for a
   selected winner does not automatically account for all the variants tried.
4. **Does the result hold up?** Check reasonable alternative definitions,
   periods, sectors and universes; inspect concentration in a few names or
   dates. Use a placebo where it can expose a specific failure. Small subsets
   may be too imprecise to settle the question, and choosing the best of many
   checks starts another search.
5. **Is it useful?** Compare with a simple baseline at matched risk. Look at
   net return, volatility, drawdowns, two-way turnover, liquidity and costs.
   A stronger Sharpe alone does not tell me whether the result is practical.

Those questions depend on sound data: point-in-time inputs, valid timing and a
test not used to choose the idea. In machine learning, Cawley and Talbot show
that repeatedly optimizing a validation measure can overfit the validation
process itself. In finance, Harvey, Liu and Zhu argue that a long history of
factor searches calls for a higher hurdle. Chen and Zimmermann reproduce many
published predictors, a reminder that selection concerns do not make every
result false; historical reproduction and future usefulness remain different
questions.

I do not want every idea to pass every conceivable test. I want the evidence to
match the decision. AI can make exploration faster, but it cannot supply more
independent market history. The useful habit is to keep the search visible,
challenge the explanation and judge the result on more than its best number.

## References

Yoav Benjamini and Yosef Hochberg, [*Controlling the False Discovery Rate: a
Practical and Powerful Approach to Multiple Testing*](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x), 1995.

Halbert White, [*A Reality Check for Data Snooping*](https://users.ssc.wisc.edu/~behansen/718/White2000.pdf), 2000.

Peter R. Hansen, [*A Test for Superior Predictive Ability*](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Hansen.pdf), 2005.

David H. Bailey and Marcos López de Prado, [*The Deflated Sharpe Ratio*](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf), 2014.

David H. Bailey and co-authors, [*The Probability of Backtest Overfitting*](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf), 2015 working paper.

Giuseppe A. Paleologo, *The Elements of Quantitative Investing*, Wiley, 2025;
see also [Stanford's description of the Rademacher Anti-Serum talk](https://icme.stanford.edu/events/tech-talk-featuring-stanford-alum-gappy-paleologo-global-head-quantitative-research-balyasny).

Joseph P. Simmons, Leif D. Nelson and Uri Simonsohn, [*False-Positive Psychology*](https://doi.org/10.1177/0956797611417632), 2011.

Cynthia Dwork and co-authors, [*The Reusable Holdout: Preserving Validity in
Adaptive Data Analysis*](https://pubmed.ncbi.nlm.nih.gov/26250683/), 2015.

Gavin C. Cawley and Nicola L. C. Talbot, [*On Over-fitting in Model Selection*](https://jmlr.csail.mit.edu/beta/papers/v11/cawley10a.html), 2010.

Campbell R. Harvey, Yan Liu and Heqing Zhu, [*... and the Cross-Section of Expected Returns*](https://doi.org/10.1093/rfs/hhv059), 2016.

Andrew Y. Chen and Tom Zimmermann, [*Open Source Cross-Sectional Asset Pricing*](https://doi.org/10.1561/104.00000112), 2022.
