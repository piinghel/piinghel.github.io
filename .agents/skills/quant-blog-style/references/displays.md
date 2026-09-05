# Display standard

## Typography and color

Use one readable sans-serif font across research charts. DejaVu Sans is the
portable Matplotlib default for this site; preserve the existing serif body
text and sans-serif site headings. Set chart type sizes for the displayed size:
aim for roughly 12–14 CSS px ticks/legends and 14–16 px variable labels. Judge
the rendered result, not the export's nominal point size. Use modest semibold
panel labels; reserve larger type for article headings.

Use a white canvas with slate text in light mode and the site's dark surface
with light text in dark mode. References are cool gray. Comparisons use muted
blue, teal, orange or red; pick only as many as the figure needs. Preserve a
semantic mapping across an article: a strategy or book keeps its color, label,
ordering and line style. Long/short contributions use teal/muted red when no
existing mapping needs preserving. Do not encode winners with red/green cells.

Color has one defined job within an encoding: distinguish categories, encode
signed magnitude, or highlight a setting. Use line style, labels or symbols
when color alone would make a key distinction fragile. Dark variants need
contrast checks, not automatic inversion. Keep pale horizontal grids and
meaningful zero/starting-value references; remove unrelated visual structure.

## Time paths and drawdowns

Use clear lines and one compact legend or collision-free direct labels.
Comparable models receive similar prominence; a designated reference may be
thinner but remains readable. Use solid/dashed lines when two models nearly
overlap. Keep the time axis common across vertically aligned panels.

Check whether compared strategies take different amounts of risk. State that
growth paths retain their actual exposures/volatilities, and point to the
nearby volatility and risk-adjusted metrics. A higher endpoint alone does not
establish a better strategy. Do not silently rescale paths to equal volatility:
that changes the experiment and needs an explicit definition and authorization.
Keep this caution proportional to the actual difference, rather than adding a
generic warning to every chart.

Drawdowns normally use thin lines. If a fill helps, use a light gray reference
fill or one lightly filled primary series. Avoid several overlapping filled
areas. Include the initial index level in peak/drawdown calculations; changing
an existing calculation requires an explicit evidence reconciliation.

Keep the full economically meaningful range, including extreme losses. Label
log scales explicitly. Use “Growth of $1” for an appropriate compounded wealth
index, or “Net growth index (log scale)” for a fixed-notional P&L construction
that should not imply funded-account wealth. Drawdown labels state percent.
Mark a development/later boundary with a quiet line and short label. Make
development-only scope visible in the caption or a compact scope label.

## Heatmaps and sensitivity panels

Signed coefficient heatmaps use one diverging scale centered on zero, symmetric
limits and a small color bar labeled “Coefficient.” Keep one common scale
across predictors; row normalization would conceal magnitude differences.
Retain descriptive labels, chronological refit years and a “Refit year” label.
Remove routine cell annotations; show selected values only when necessary for
the argument, and retain exact values separately when permitted.

For sensitivity panels, match scales across the same metric. Highlight the
chosen setting without implying a statistically identified optimum. State
exactly what points and whiskers mean, for example: “Points are schedule means;
Sharpe whiskers span observed schedules. Turnover panels show means only.”
Observed ranges are not confidence intervals.

For episode panels, try shared limits for corresponding variables first. If
they hide the smaller episode's mechanism, use separate limits and make that
exception prominent in the caption. Retain zero contribution references and
label cumulative contributions explicitly. Event markers name the actual event
or trough supported by the data.

## Tables

Use no vertical rules and no routine lines between data rows. Left-align text,
right-align numbers and align each header with its data. Preserve tabular
numerals. Group Development and Later periods using a clear spanning header
and whitespace; keep strategy order stable across tables and figures.

Use short labels explained once. Precision follows the question: normally one
decimal for turnover, two for Sharpe, and enough return or IC precision to
preserve the relevant comparison. Apply one precision within each column.
Do not discard an economically meaningful difference merely to fit a default.

Make annualization, costs and turnover units explicit locally. “Net return”
alone is insufficient when arithmetic and geometric returns both appear in
the series. “Turnover” states per rebalance, per year or traded-notional basis.
Keep gross return when the gross/net gap answers the question; otherwise it may
live in supporting results. Prioritize the columns that assess the claim.

Use subtle shading for a selected construction or combined rule, never a field
of winning cells. Make settings tables quieter than results tables. A caption
begins with the comparison and scope, followed by essential conventions.

## Mechanisms and mobile layout

For a staggered rebalance schedule, three sleeve rows over six weeks can show
two rotations. Label each row “⅓ notional”; mark each rebalance with a symbol
as well as restrained color. Place the schedule before accounting detail.
Use the same sleeve identities in related performance displays.

Ordinary line charts should fit a phone. When a wide export would shrink labels
too far, generate a narrow layout from the same data and plotting functions.
Stack panel groups on mobile while preserving their logic: for an episode,
growth remains above contribution. Keep genuinely comparable scales intact.

Dense heatmaps and genuinely wide tables may scroll locally. Make scrolling
discoverable with a brief visible hint when needed; check keyboard access,
both ends of the scroll region and absence of page-level horizontal overflow.
Do not impose a large global minimum width on every chart. Do not clip columns
or convert comparison tables into cards that obscure cross-row comparisons.

## Export checks

Regenerate every variant from one composition with intentional margins. Check
all text bounding boxes and the actual page: a valid view box alone does not
prove readability. Verify no duplicate labels, clipped endpoints, cut legends,
missing glyphs or inconsistent theme variants. Keep one reproducible source
and preserve the previous version in Git before replacing an empirical asset.
