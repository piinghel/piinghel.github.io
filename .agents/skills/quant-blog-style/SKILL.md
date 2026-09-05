---
name: quant-blog-style
description: Apply Pieter-Jan Inghelbrecht's research-blog style to new or existing posts, figures, tables and captions. Use for presentation and editorial consistency on piinghel.github.io or when this house style is requested; empirical reruns and publication need their own task authorization.
---

# Quant blog style

Make the research comparison easy to understand at normal article width.
Preserve the author's question, evidence and judgment. These are house defaults,
not reasons to redesign an effective display or override the user's choices.

## Establish the argument

Read the current post, its rendered page and repository guidance. For a new
post, identify the practical question and the evidence that answers it. Use
short headings and connected prose: research decision, experiment, result,
interpretation. This is a reasoning sequence, not a mandatory section template.

Keep the summary brief. Let the introduction develop the question rather than
repeat the summary's results. Use first person for actual choices and judgments;
avoid invented anecdotes, promotional claims and narrating the workflow.
Explain enough method to assess the comparison, with detailed settings in a
quiet table or research documentation. End on the decision supported by the
evidence and the uncertainty that could change it.

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

For display edits, read [the display standard](references/displays.md). It
contains chart-specific decisions, typography, colors and table conventions.

## Keep claims attached to evidence

Style changes preserve values and definitions. Regenerate empirical graphics
from verified saved evidence and the plotting source; do not repair labels by
editing generated SVG elements. If the data are missing, preserve the empirical
asset and report that limitation. A diagram may be authored directly as SVG.

Distinguish arithmetic and geometric annualization, standalone schedule means
and combined daily returns, fixed-notional indices and funded wealth. State
costs, turnover units and reused later-period history where needed to interpret
results. Similar paths are an empirical result, not a reason for a dramatic zoom.

Keep confidential reports and licensed security-level data out of public
articles, assets and commits. The style skill supplies no authority to rerun
research, publish, merge, send messages or clean another task's files.

## Integrate with this site

Preserve permalinks, site identity and the existing prose fonts. Use the site's
`research-figure` containers and `theme-svg-figure.html` include, its
`research-table` / `comparison-table` classes, and `period-heading` rows where
appropriate. Inspect current CSS and include arguments rather than assuming
their interface has remained unchanged.

Number figures and tables independently in reading order. Put the figure's one
main title at the beginning of its caption below the display. Put a table's
caption above it. Panel labels identify variables or scope; they do not repeat
the caption's title. Keep axis units visible.

Do not add inline CSV downloads or “supporting results” links to table captions.
Keep reproducibility material in the existing research repository and its
documentation unless the user explicitly requests a reader-facing download.

## Verify the reading experience

Render light and dark variants from the same data and layout. Inspect the page
at its actual desktop reading width and approximately 390 px phone width in
both themes, beginning at the top and encountering displays in reading order.

Check purpose, definitions, readable text, appropriate emphasis, honest scales
and complete exports. Check labels against data lines as well as other labels;
verify the last observation, legends and direct labels lie inside the export.
Do not treat a successful build as visual verification.

For this Jekyll site, run the relevant figure-input tests, regenerate dimension
metadata with the documented command when assets change, then run
`bundle exec jekyll build`, `python3 scripts/check_site.py _site` and
`git diff --check`. Use the repository's current environment instructions.
Report what changed and what was verified; state any blocked evidence or QA.

## Basis

These house decisions apply Wilke's principles to this blog; they are not claims
that he prescribed this palette, layout or wording:
[context](https://clauswilke.com/dataviz/balance-data-context.html),
[readable labels](https://clauswilke.com/dataviz/small-axis-labels.html),
[color](https://clauswilke.com/dataviz/color-basics.html),
[panels](https://clauswilke.com/dataviz/multi-panel-figures.html), and
[titles, captions and tables](https://clauswilke.com/dataviz/figure-titles-captions.html).
