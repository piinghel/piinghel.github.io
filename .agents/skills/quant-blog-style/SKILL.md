---
name: quant-blog-style
description: Prepare, edit and launch Pieter-Jan Inghelbrecht's research notes on piinghel.github.io. Use by default for article releases, site layout, prose, research figures, tables and captions. Follow the user's authorization for publication and empirical reruns.
---

# Quant blog style

Write like a quant speaking to another quant: correct domain terminology,
natural sentences and a direct explanation of the research. Assume expertise
in finance, statistical modelling, machine learning and portfolio management.
Conversational means an easy flow of reasoning, not beginner vocabulary.
Use terms such as volatility deciles, long and short books, turnover, beta and
leverage without routine definitions or casual substitutes such as “the
calmer stocks” or “the calmest tenth.” Simplify sentence structure, not the
technical content; avoid overcorrecting into stiff, impersonal prose.

Keep the modelling problem central in modelling articles. In portfolio-
construction articles, centre the allocation problem, exposures and risk
trade-offs. Introduce study-specific definitions and conventions where they
matter to the comparison.

Frame public articles as Pieter-Jan's personal research and exploration. Never
refer to his models as production models, live strategies or deployed systems,
or imply actual trading, funded portfolios, operational use or models used at
work. These articles follow his interests and curiosity. Express preferences
as research judgments and comparisons.
Apply this quietly through the prose. Do not add disclaimers, explanations of
what cannot be mentioned, or repeated announcements that this is personal research.

Lead with the concrete problem in conversational language, then explain what
the comparison will try to resolve. The author does not want recurring prose,
caption or end-note disclaimers about having inspected or reused the later/test
period. Do not reintroduce them through synonyms such as "both periods shaped
the strategy." Preserve reporting dates and calculation conventions without
describing the evidence as independent or untouched validation.

Use “research baseline” or name the model being compared rather than “incumbent”
in this author's articles. Avoid “current model” when it could suggest a model
in operational use. Name the actual model family when that distinction matters.

Make the research comparison easy to understand at normal article width.
Preserve the author's question, evidence and judgment. These are house defaults,
not reasons to redesign an effective display or override the user's choices.

## Establish the argument

Define unfamiliar or study-specific objects only when the reader needs it.
Use a short, direct definition. Remove sentences whose only purpose is saying
what something is not.
Express consequential limits through the actual sample, calculation, assumptions
or required next test. Apply this to prose, headings, captions and interactive
labels. For example: “The model attributes realized returns to stock exposures.”
State failed outcomes directly and preserve their evidence.

For drafting or prose edits, read [the voice guide](references/voice.md).
It draws on Sander Dieleman, Max Halford, Chip Huyen and Rob Carver, together
with the user's preference for Cliff Asness's selective arguments and footnotes,
without prescribing an imitation or template.

Read the current post, its rendered page and repository guidance. For a new
post, identify the practical question and the evidence that answers it. Use
short headings and connected prose: research decision, experiment, result,
interpretation. This is a reasoning sequence, not a mandatory section template.

Never add a summary, summary box, key takeaways or TL;DR, at the top or anywhere
else; open with the concrete problem in the first paragraph. Use first person for
actual choices and judgments.
Headings are statements; don't pose a question and answer it yourself. Keep
footnotes to one or two short sentences (a source or one clarification). Don't
hedge with "noise"; state uncertainty once, as an interval or a plain judgement.
Keep useful accounts of failed research comparisons and stopping decisions.
Keep internal workflow out of public prose, captions, footnotes and collapsed
details: simulation defects, saved-run handling, pending reruns, missing checks,
repairs, bookkeeping, editing and deployment belong in the private research
registry or engineering workflow. Resolve defects that affect results before
publishing those results; removing a notice does not correct the evidence.
State reader-relevant assumptions and limitations through the method and its
scope, without narrating internal progress or promising future work.
Explain enough method to assess the comparison, with detailed settings in a
quiet table or research documentation. End on what the comparison establishes.
End on the judgement the work supports, not on open questions; do not
manufacture a next experiment to give the ending a sense of purpose.

Keep useful concrete examples. Consolidate repeated qualifications without
losing material limitations. Preserve an effective article's structure during
a visual pass. Do not start new experiments to make a conclusion stronger.

## Give each display one job

Before redesigning a figure or table, record its reader question in working
notes, together with the comparison, units, sample and transformation. Keep
these notes out of the public caption unless they help the reader.

Use a chart for patterns, paths or mechanisms; use a table for exact comparison
across metrics. A heatmap should reveal a pattern before inviting cell lookup.
A mechanism diagram should explain what happens, without pretending to be
empirical evidence. Avoid an extra display that repeats an existing answer.

Apply the author's `wilke-research-figures` skill for figure work. Try the
argument with the figure removed. When a short paragraph carries the finding,
keep the numbers, any essential uncertainty, and the simpler page. When a
figure earns its place, decide what the reader should see first, what needs
a label, and what can leave.

For display edits, read [the display standard](references/displays.md). It
contains chart-specific decisions, typography, colors and table conventions.

## Keep claims attached to evidence

Style changes preserve values and definitions. Regenerate empirical graphics
from verified saved evidence and the plotting source; do not repair labels by
editing generated SVG elements. If the data are missing, preserve the empirical
asset and report that limitation. A diagram may be authored directly as SVG.

Distinguish arithmetic and geometric annualization, standalone schedule means
and combined daily returns, fixed-notional indices and funded wealth. State
costs, turnover units and reporting periods where needed to interpret
results. Similar paths are an empirical result, not a reason for a dramatic zoom.

Keep confidential reports and licensed security-level data out of public
articles, assets and commits. The style skill supplies no authority to rerun
research, publish, merge, send messages or clean another task's files.

## Integrate with this site

Use `layout: post` for new articles. Shared templates provide the serif headline,
publication metadata, a narrow reading column, a left contents rail on desktop
and a disclosure on smaller screens. Let the layout build contents from H2s.
Preserve permalinks, site identity, chronological RSS and the repository's
homepage and Previous/Next ordering. Keep the introduction in the article body.

Use the site's `research-figure responsive-figure` containers with
`theme-svg-figure.html` or `blog-chart.html`. Start figures at reading width.
Widen an individual figure only to make a particular comparison legible.
On phones, keep related panels in the same view when their labels fit. Keep comparison tables in their shared
`research-table` / `comparison-table` styles.

Preserve the original homepage. Each entry uses the same article title,
date, topic and short description beneath the “Research notes” heading.
Keep all figures and captions inside articles.

Restart numbering in each article. Use “Figure 1.” and “Table 1.” as independent sequences in reading order. Put the figure's one
main title at the beginning of its caption below the display. Put a table's
caption above it. Panel labels identify variables or scope; they do not repeat
the caption's title. Keep axis units visible.

Do not add inline CSV downloads or “supporting results” links to table captions.
Keep reproducibility material in the existing research repository and its
documentation unless the user explicitly requests a reader-facing download.

## Verify the reading experience

Render light and dark variants from the same data and layout. Inspect the page
at its actual desktop reading width, at narrow-window width around 540 px
and at approximately 390 px phone width in both themes. Read each figure
with the surrounding paragraph. For redesigns, share a working intermediate
version while the author can still give feedback.

Check purpose, definitions, readable text, appropriate emphasis, honest scales
and complete exports. Check labels against data lines as well as other labels;
verify the last observation, legends and direct labels lie inside the export.
Do not treat a successful build as visual verification.

Use the repository's build and test commands in `AGENTS.md`. Update dimension
metadata if vector exports change. For a launch, check the lead note on the
homepage, the article and its captions in both themes and at phone width,
then verify the public URL after publication when publication is in scope.

## Basis

These house decisions apply Wilke's principles to this blog; they are not claims
that he prescribed this palette, layout or wording:
[context](https://clauswilke.com/dataviz/balance-data-context.html),
[readable labels](https://clauswilke.com/dataviz/small-axis-labels.html),
[color](https://clauswilke.com/dataviz/color-basics.html),
[panels](https://clauswilke.com/dataviz/multi-panel-figures.html), and
[titles, captions and tables](https://clauswilke.com/dataviz/figure-titles-captions.html).
