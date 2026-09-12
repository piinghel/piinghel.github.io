# Personal research writing

Write as Pieter-Jan explaining his work to a capable colleague. The reader
should understand both the result and why he cares about it. These are editing
preferences, not a required structure, tone quota or checklist for every post.

## Useful qualities in the reference writers

These are readings of particular examples, not claims that the writers follow
fixed formulas. Borrow the qualities, not their phrases or personas.

- [Sander Dieleman](https://sander.ai/2023/01/09/diffusion-language.html)
  starts from a puzzle and connects the technical explanation to why that
  puzzle remains unresolved. Let the reader follow the reasoning; introduce
  machinery when it helps answer the question.
- [Max Halford](https://maxhalford.github.io/blog/online-learning-evaluation/)
  develops a concrete comparison and explains why an apparently reasonable
  evaluation misses the practical problem. Give examples a job and explain
  the consequence of a result before moving on.
- [Chip Huyen](https://huyenchip.com/2024/03/14/ai-oss.html)
  makes her choices, effort and judgments visible beside the analysis.
  Honest research experience can carry the voice without decorative banter.
- [Rob Carver](https://qoppac.blogspot.com/2016/06/obligatory-brexit-ex-post-survival-skew.html)
  discusses what happened to his positions, including losses and mistaken
  expectations, while separating returns from the quality of risk management.
  State what the author would do and why; a disappointing result is still
  worth explaining.

## Applying this voice

The user's preferred register is a hands-on practitioner explaining the work
to allocators and quant peers. Keep the technical content rigorous; let the
framing sentences sound conversational. Make the author's reasoning visible:
the problem, the genuine prior or expectation when known, what happened, and
what the author now thinks or would do. Merely reporting results misses that
personal connection. This is a preference, not a story arc to fabricate.

The user's additional reference is Cliff Asness: choose the strongest one or
two arguments rather than explaining a point several ways, and use footnotes
for secondary qualifications that interrupt the flow. Avoid his combative tone
or sarcasm. Across the references, avoid borrowed personas, forced humour,
emoji, listicle structures or extra length added for personality.

Start from the author's actual question or decision. Preserve useful language
already in the draft. Use first person where it reveals a choice, motivation,
doubt or interpretation supported by the conversation or research. Don't invent
surprise, frustration, expectations, anecdotes or live trading experience.

Open with why the question matters to the author, and include a prior before
a test when the record supports one. React to the evidence with an actual
judgment about its practical value. If the prior is unknown, explain why the
comparison is useful instead of inventing what the author expected. Treat
user-supplied sample wording as editorial illustrations: verify its research
status and factual claims before reuse, especially claims that a test is still
unrun or that a portfolio is traded live.

Prefer a concrete example before an unfamiliar formula when it helps the
reader. Round prose numbers sensibly with “about” or “roughly”; retain useful
precision in tables and preserve thresholds and definitions. Brief parentheses
can carry a natural aside. Explain scope through concrete choices such as
holding predictions fixed, without adding repeated negative definitions.

Connect facts through reasoning, not ceremonial transitions. A number should
help the reader understand what changed or why a choice follows. Familiar
technical terms and necessary equations can stay; sounding natural does not
require replacing precision with vague language.

Allow contractions and an occasional aside when they sound like the author.
Don't manufacture personality with jokes, rhetorical questions, dramatic
one-line paragraphs, repeated “I think,” or stock phrases such as “the key
takeaway.” Neither a personal pronoun in every sentence nor extreme brevity
makes a post more human.

Keep limitations that affect the comparison, confidence or decision. Say what
happened concretely and usually once near the result. For an abandoned test,
state how much completed, what failed and why the author stopped. Don't promise
future updates or call results “awaiting” when no further work is planned.
Retain actual solver warnings and missing checks; don't replace them with vague
status labels or erase them to make the story smoother.

Prefer numbered footnotes for secondary methodological caveats, consolidating
repeated hindsight or sample-reuse disclosures. Keep limitations that change
the headline interpretation visible beside the claim; a concise existing
in-sample box can still serve that purpose. Footnotes should improve flow
without hiding material information. Close on the supported decision, what
the author would change, or what remains unknown. Link existing shareable code
when useful; an invitation for feedback should be specific and natural, and
never implies permission to publish private data.

## Examples, not reusable templates

Use these to judge the kind of edit, not as sentences to paste into every post.

- **Make a choice intelligible.** Instead of “The experimental configuration
  was held constant,” use “I kept the predictions and trading rules fixed
  because I wanted to see what the risk limits changed.” This is the concrete
  comparison principle illustrated by Halford, not a quotation from him.
- **Report a dead end plainly.** When supported by the run record: “Only one
  schedule finished. The next attempt hit the iteration limit. It was taking
  too long, and the result wasn't promising enough to keep pursuing it.” The
  useful quality in Huyen and Carver is candor about the work, not comic relief.
  Don't turn a solver failure into a claim that no feasible solution exists.
- **Calibrate the interpretation.** Replace “The cap makes the portfolio
  safer” with “The cap reduces concentration under the risk model. I still
  want to understand which losses that might protect against.” Like the
  distinction Carver makes between an outcome and risk management, this keeps
  judgment separate from what the observation establishes.

## Final read

Read every negative definition as a deletion candidate. Replace “This is not an
independent test” with “The schedules share the same market history.” Replace
“It does not tell us which predictor selected the stocks” with “It attributes
realized returns to the stocks' exposures.” Keep the useful definition once,
near the measure; delete an empty qualification outright.

Finish with the author's current decision and the specific unresolved question,
if there is one. Then read the paragraphs as continuous speech. Does every
paragraph advance the explanation? Cut repeated setup, repeated caveats and a
second concluding recap. Keep uncertainty where it changes the claim, without
hedging every sentence. Remove any joke, aside or polished-sounding sentence
that draws attention to the writing instead of helping explain the work.
