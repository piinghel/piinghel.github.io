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

When I research a quantitative idea, there are usually several reasonable ways
to express it: a different signal, a different lookback, a different way to
build the portfolio. AI makes it easier to explore those variations. It can help
write the code and suggest the next comparison while I concentrate on the
research question.

The problem is that the best result becomes more impressive as the search gets
larger, even if the underlying ideas have no edge. I wanted to see how much a
few familiar corrections change that picture, and what they cost in terms of
the signals they miss.

## A larger search produces better-looking winners

Suppose I test 100 unrelated strategies and none has a real edge. Each gets a
valid one-sided test at the 5% level. The chance that at least one looks
significant is

$$
1-(1-0.05)^{100} \approx 99.4\%.
$$

The issue is not that the individual test was calculated incorrectly. It is
that I selected a result after looking at many tests. The other attempts belong
in the interpretation too.

In practice, strategies are related. A 20-day and a 21-day lookback do not
provide two independent shots at a discovery. In a simulation with 100 null
tests and a pairwise correlation of 0.5, at least one passed the ordinary 5%
threshold in 56% of the simulated research exercises. That is less than the
99% for independent tests, but it still happens often.

## Corrections trade discoveries for confidence

I simulated 20,000 research exercises, each with 100 one-sided Gaussian tests.
First all 100 hypotheses are false ideas: their true effects are zero. Then 10
have a positive effect, represented by a shift of 2.5 standard errors in the
test statistic; the other 90 remain null. The table reports the independent
case. Every method uses a nominal 5% level.

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

Bonferroni and Holm aim to control that latter probability, the family-wise
error rate. Benjamini–Hochberg instead controls the expected proportion of
false discoveries under suitable dependence assumptions. In this example it
detects more genuine signals, while allowing a false discovery in more of the
individual exercises. Neither choice is automatically right: it depends on
whether a discovery is a candidate for more research or a decision with a
high cost of being wrong.

With pairwise correlation of 0.5, the all-null false-discovery probability was
56.2% without correction, 2.6% for Bonferroni and Holm, and 3.2% for
Benjamini–Hochberg. With 10 real signals, power was 21.8%, 22.1% and 37.1%
for the three adjusted methods respectively; their false discovery rates were
0.4%, 0.5% and 3.9%. Dependence changes the result, and the correlations in a
real strategy family will not all be equal.

These are deliberately simple simulations. They assume valid test statistics,
known standard errors, a fixed family of tests and no leakage or transaction
costs. A real backtest can violate those assumptions. The experiment illustrates
the trade-off; it does not tell us which method will be best for a portfolio.

## Counting the trials is harder than it sounds

In the simulation I know the answer: I tested exactly 100 ideas. In actual
research, where does one idea end and another begin? Changing a lookback by one
day is not the same as testing an unrelated signal. But choosing a time period,
metric, universe or model after looking at the results is also part of the
search, even if it never appears in a parameter grid.

The search may extend beyond one researcher. A strategy inspired by a paper or
an earlier project inherits choices made using the same market history. Those
attempts are usually impossible to reconstruct completely. The number of
independent trials is therefore often an estimate, not a fact we can read from
a log. Correlation matters, but there is no universal conversion from a list of
related tests to an exact effective count.

My practical answer is to log observable choices, define the family relevant
to the decision, and show how the conclusion changes under plausible trial
counts or dependence assumptions. That sensitivity analysis does not correct
for unknown searches by itself. It makes the uncertainty visible. It also
helps to reserve independent data for confirmation, because a retrospective
count cannot recover every unrecorded choice.

## Accounting for a family of strategies

Classical corrections work with p-values. Other methods use the behavior of the
candidate strategies directly. White's Reality Check asks whether the best
strategy found in a search beats a benchmark after accounting for that search.
Hansen's Superior Predictive Ability test addresses the same broad comparison
with a different construction. Both need an appropriate benchmark and a
resampling method suited to the time series.

David Bailey and Marcos López de Prado's **Deflated Sharpe Ratio** asks whether
a selected Sharpe is exceptional after allowing for selection among trials and
non-normal returns. Its answer depends on how the trials and their dependence
are represented, and on the return assumptions. Their work with co-authors on
the **probability of backtest overfitting** takes another angle: does the
in-sample winner tend to rank poorly in held-out partitions? That is a useful
selection-stability diagnostic, although partition-based cross-validation does
not replace a forward-looking test when markets change over time.

Giuseppe “Gappy” Paleologo's Rademacher Anti-Serum is another approach. It
uses random sign changes to estimate how well the best member of a strategy
family could align with random variation, then incorporates that complexity
into a performance bound. Similar strategies contribute less additional
complexity than very different ones. The method's guarantees depend on its
assumptions, including how dependence over time and the strategy family are
handled; its bound can be conservative. The simulation above does not test it.

## The same problem appears outside finance

The decisions do not have to be trading strategies. In psychology, Simmons,
Nelson and Simonsohn showed how choices about outcomes, sample size and
controls can raise the false-positive rate when researchers report only the
successful analysis. In machine learning, repeatedly selecting models against
the same benchmark or holdout can also adapt the research to that data. A
holdout remains useful only insofar as the decisions being evaluated have not
already been tuned to its feedback.

## A protocol for a faster research process

The correction is only one part of the work. I find the following habits just
as important:

- **Write the question and baseline down first.** Define the comparison, the
  primary measure and what would make the idea worth pursuing.
- **Keep the unsuccessful attempts.** Record variants, data choices and
  changes made after seeing results. A correction can only address the search
  represented in the analysis.
- **Separate exploration from confirmation.** Exploration can be broad; an
  idea chosen from that exploration needs a subsequent evaluation that was not
  used to choose it. Keep model selection inside each validation split.
- **Respect time and data availability.** Use point-in-time inputs and
  time-ordered evaluation; account for overlapping labels and dependence.
- **Protect the final test.** Repeatedly choosing variants based on a holdout
  turns it into development data. A later period can provide additional
  evidence, though it also has its own market conditions.
- **Look beyond significance.** Effect size, uncertainty, economic rationale,
  costs, capacity and risk all matter to the eventual decision.

AI can help with both sides of this process: it can explore more ideas and help
document the choices that produced them. The important discipline is to carry
the full search into the evaluation. Faster experiments are valuable when they
lead to better-calibrated conclusions, not just more impressive winners.

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
