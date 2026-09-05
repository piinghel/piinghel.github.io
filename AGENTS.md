# Website contribution guide

## Project

This is a Jekyll site for concise, technically serious research articles. Keep prose natural and direct: explain the research decision and evidence clearly, without marketing language or unnecessary abstraction.

## Editing rules

- Recover the article's practical research question before rewriting. Keep
  follow-up questions when a result motivates the next decision within that
  same argument. Delete unsupported branches rather than filling an appendix.
- Describe implementation only when it changes the research design, evidence
  or interpretation. Keep material limitations once, where they matter.
- Do not publish confidential sell-side reports, citations to them, Bloomberg
  references, or licensed source data. Keep private research inputs local.

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
- Describe what measures show and which assumptions they use. Replace repeated
  negative contrasts with direct definitions, such as observed ranges across
  schedules. Preserve material limitations through concrete scope statements.

- Inspect the current article, assets, and git state before editing.
- Use `apply_patch` for source edits and keep changes narrowly scoped.
- Never stage, modify, revert, or delete `.DS_Store` files.
- Do not add temporary plotting scripts, scratch files, generated caches, or speculative refactors to the repository.
- Preserve existing article framing and quantitative claims unless the source evidence is checked first.
- Do not reintroduce dollar-neutrality, market-neutrality, mandate, or neutrality framing into the low-volatility article.
- Keep the low-volatility article's visible publication date hidden while
  retaining its stable permalink and front-matter date for Jekyll ordering.

## Figures

- Use captions for interpretation; do not embed figure titles in images.
- Use captions above tables and below figures. Keep numeric columns aligned,
  define units and periods, and avoid repeating the same title inside an image.
- The low-volatility performance figure combines performance and drawdown.
- Its rally figure is one 2-by-2 image: dot-com on the left and the
  April 2025–May 2026 rally on the right, indexed growth above linked gross
  book contributions. Do not assign an AI or growth-factor cause without
  holdings-level attribution.
- Keep figures minimal: restrained grids, subtle reference lines, no unnecessary axis pins, and no duplicate legends.
- Publish reproducible light and dark SVG variants from one shared figure
  composition, and keep the same table structure at every viewport width.

## Verification and delivery

Run `bundle exec jekyll build` after concrete article or asset changes, followed
by `python3 scripts/check_site.py _site`. Check rendered references and
`git diff --check`. Preserve any user-owned changes, especially `.DS_Store`,
then commit and push `main` so the live page can be checked.
