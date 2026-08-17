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

## Figures

- Use captions for interpretation; do not embed figure titles in images.
- Figure 4 may retain the three panel labels `Long gross`, `Short gross`, and `Net exposure`.
- Figure 6 is one image with cumulative wealth above shaded drawdowns, a shared x-axis, and one legend.
- Keep figures minimal: restrained grids, subtle reference lines, no unnecessary axis pins, and no duplicate legends.
- Provide desktop and mobile variants from the same data and verify both visually.

## Verification and delivery

Run `bundle exec jekyll build` after concrete article or asset changes. Check rendered references and `git diff --check`. Leave only the two known `.DS_Store` modifications in the working tree, then commit and push `main` so the live page can be checked.
