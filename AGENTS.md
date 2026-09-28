# Website contribution guide

## Project

This is a Jekyll site for concise, technically serious research articles. Keep prose natural and direct: explain the research decision and evidence clearly, without marketing language or unnecessary abstraction.

## Editing rules

- Frame the blog as personal research and exploration. Never describe the
  author's models as production models, live strategies, deployed systems or
  models used at work. Avoid related wording that implies actual trading,
  funded portfolios or operational use. Describe tests, backtests and research
  preferences naturally, preserving the author's curiosity and opinions.
  Apply this quietly; do not add disclaimers or announce the framing in the prose.
- Give every article the same structure: header, the small Contents list, an
  introduction that opens with the concrete problem, the analysis sections, a
  closing section with the judgement, then references if any. Never add a
  summary in any form. List articles newest first everywhere, and never show
  unpublished or unfinished articles on the site.
- Headings are statements. Don't pose a question and answer it yourself, and end
  on the judgement rather than on open questions.
- Keep footnotes to one or two short sentences: a source or one clarification.
  Settings lists and caveat chains go into a small table or are cut.
- Don't hedge with "noise" ("within noise", "can't distinguish from noise"). State
  uncertainty once, as an interval or a plain judgement.
- Write as a quant explaining a result (what was compared, what happened, why,
  what it means), not as a lab log of implementation steps and settings.
- Recover the article's practical research question before rewriting. Keep
  follow-up questions when a result motivates the next decision within that
  same argument. Delete unsupported branches rather than filling an appendix.
- Preserve figures that substantiate a central claim or connect steps in the
  story. Mentioning their endpoint values in prose does not replace showing
  the comparison. In the low-volatility article, retain the decile bar plot
  beside the discussion of return, volatility and Sharpe across deciles.
- Open conversationally with the concrete problem and what the article will
  try to resolve. Do not add or reintroduce boilerplate about having inspected,
  reused or learned from the later/test period, including paraphrases such as
  "both periods shaped the strategy." Keep reporting dates and calculation
  conventions clear without claiming independent or untouched validation.
- Describe implementation only when it changes the research design, evidence
  or interpretation. Keep material limitations once, where they matter.
- Do not publish confidential sell-side reports, citations to them, proprietary
  source identifiers, or licensed source data. Keep private research inputs local.

- Let the first-person voice come from actual experiments and choices: what I
  tried, what I observed, and why I chose the next step. Use Max Halford and Rob
  Carver as broad references for conversational technical writing; avoid forced
  anecdotes, jokes, and academic scaffolding. Keep Resources mostly links.
- Write for a systematic-equity reader: use "two-way turnover", "traded
  notional", and other normal domain terms. Define the convention once.
- Use short, natural headings and introduce each practical problem before its
  equation. Avoid formulaic process language and the word "fresh" in prose.
- Keep revision logs, archive searches, hashes, and renderer details in project
  documentation. Article source notes should be brief and useful to the reader.
- Keep internal workflow out of public articles, including captions, footnotes
  and collapsed details. Do not narrate simulation defects, saved-run handling,
  pending reruns, missing checks, repairs or bookkeeping. Manage these in the
  private research registry and engineering workflow. Resolve defects that
  affect results before publishing those results; deleting a notice is not a
  correction. Keep reader-relevant assumptions and limitations as concise
  statements about the method or evidence, without a progress report or a
  promise of future work. Preserve useful failed research comparisons.
- Keep facts shared across articles identical everywhere: the predictor set
  (80 ranking predictors), sample periods, cost and turnover conventions, and
  headline returns. Take each from its configuration or saved output, never
  from memory or another article's prose. When a shared fact changes, rerun
  the analysis, then `grep` every post, chart source and caption for the old
  value and update them in the same commit. The attribution uses exactly the
  80 ranking predictors, set in `descriptors.json` of the attribution study.
- Describe what measures show and which assumptions they use. Replace repeated
  negative contrasts with direct definitions, such as observed ranges across
  schedules. Preserve material limitations through concrete scope statements.

- Inspect the current article, assets, and git state before editing.
- Use `apply_patch` for source edits and keep changes narrowly scoped.
- Never stage, modify, revert, or delete `.DS_Store` files.
- Do not add temporary plotting scripts, scratch files, generated caches, or speculative refactors to the repository.
- Preserve existing article framing and quantitative claims unless the source evidence is checked first.
- Do not reintroduce dollar-neutrality, market-neutrality, mandate, or neutrality framing into the low-volatility article.
- Show the publication date on every post; add `last_modified_at` when an
  article's content changes so the header also shows "Updated".

## Figures

- Prefer short horizontal panel headings to rotated y-axis titles. Keep any
  remaining axis title very short; preserve units. Keep labels clear of lines
  and allow table text to wrap on phones without overlapping adjacent columns.
- Prefer series names directly beside time-series lines over a separate legend;
  separate close labels and keep them outside the data where possible.
- Use captions for interpretation; do not embed figure titles in images.
- Use captions above tables and below figures. Keep numeric columns aligned,
  define units and periods, and avoid repeating the same title inside an image.
- The low-volatility performance figure combines performance and drawdown.
- Its rally figure has a 2-by-2 composition: dot-com on the left and the
  April 2025–May 2026 rally on the right, indexed growth above linked gross
  book contributions. Do not assign an AI or growth-factor cause without
  holdings-level attribution.
- Keep figures minimal: restrained grids, subtle reference lines, no unnecessary axis pins, and no duplicate legends.
- Use the shared interactive chart helper for finalized evidence, with quiet
  defaults and optional controls under Explore. Keep statistics collapsed and
  omit miniature range previews. Retain reproducible light and dark SVG fallbacks
  from one shared composition per viewport. Stack episode groups and multi-panel charts
  on phones when needed for readable labels; preserve scales and definitions.
  Keep the same table structure at every viewport width.

## Verification and delivery

Run `bundle exec jekyll build` after concrete article or asset changes, followed
by `python3 scripts/check_site.py _site`. Check rendered references and
`git diff --check`. Preserve any user-owned changes, especially `.DS_Store`,
then commit and push `main` so the live page can be checked.
