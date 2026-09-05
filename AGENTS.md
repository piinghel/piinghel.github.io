# Website contribution guide

## Project

This is a Jekyll site for concise, technically serious research notes. Keep prose natural and direct: explain the implementation and evidence clearly, without marketing language or unnecessary abstraction.

## Editing rules

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
- In the low-volatility article, Figure 3 uses the panel labels `Long gross`,
  `Short gross`, and `Net exposure`. Figure 5 combines performance and drawdown.
- Low-volatility Figure 6 is one 2-by-2 image: dot-com on the left and the
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
