# Word / PDF layout (English delivery)

A page that still shows Chinese, 宋体 on English, a header over the title row, a wrapped Yes/No box, or a clipped data table is not finished.

Do not hand over until you have exported PDF and looked at the first pages.

## Font

Latin text: **Calibri 10.5 pt** (`w:sz` 21). User locked Calibri. Do not switch to Times.

Do **not** run Word COM `Range.Font.Name` on the whole document. That bumped the header from 10.5 pt to 15 pt and made it overlap the body.

## Header

Chinese source is one line: company + code (`HMTC/WJ-G-2026`). English company name is longer and will wrap.

Use a **2-cell header table** in every `header*.xml`:

- left: `Shanghai Huaming Power Equipment Co., Ltd.` then `Tap-changer Test Centre`
- right: document code, right-aligned, vertical center
- both Calibri 10.5 pt
- table 100% width, bottom border only
- delete empty header paragraphs that still have `w:sz` 30

Landscape A4 content height is about 14.6 cm after 1800 twip margins. Nothing in the header may spill into that.

## Checkboxes (`□是  □否`)

WPS ignores `noWrap`. One paragraph of `□ Yes  □ No` (U+25A1) wraps to `□ Yes  □` / `No` and looks like a geometry square.

Required:

1. Ballot box **U+2610** `☐` in Segoe UI Symbol 12 pt, then Calibri 10.5 pt ` Yes  ☐ No`.
2. Widen the Done column in **`tblGrid`** (not only `tcW`) to about **2200 dxa**. Word uses the grid for column width.
3. Keep it **one line**, left-right.

Do not stack Yes over No. Nested 2-cell tables are a last fallback if it still wraps after the grid is widened.

## Data tables that were pictures

Do not leave a Chinese table with an English caption.

**Prefer a real Word table.** Two conductor charts (Table 1 / Table 2) sit side by side in the source cell. Rebuild them as Word tables, 9 pt body, 8 pt notes, Calibri. Do not paste a 17 cm-tall PNG: landscape content is only ~14.6 cm tall and the picture will cover the header and clip.

If you must keep a picture:

- keep the source display size (those two charts were ~10 cm × 8 cm each, side by side)
- fill that box; do not leave a postage-stamp table in white space
- never set `wp:extent` taller than the remaining page

Look at the PDF. If the last two rows or footnotes sit alone on the next page, tighten row height or start the charts on a new page.

## Other figures

`w:t` with no Chinese is not enough. Open every `word/media/*` image.

| What you see | What to do |
|--------------|------------|
| CAD / photo label (油温监测点, 加压端, 接地) | Replace the label in the image |
| Circuit / sequence legend | Replace the legend; keep geometry and numbers |

Visible Chinese on a figure is a fail.

## Phrasing (test procedures)

- `<= +/- 3%` → `within +/- 3%`
- `do not leave at once` → `do not leave immediately`
- `raise button` → `raise the current smoothly`
- `take thermal stability as reached` → `consider the temperature stable`
- `Judge the result against` → `Assess the result against`

No em-dash. Form numbers, currents, and standard numbers stay exact.

## Self-check (export PDF)

Word COM `SaveAs` PDF, then look at page 1, a checkbox page, and the data-table page.

1. No CJK in any `w:t`.
2. Every media image viewed.
3. Header is a 2-cell table; it does not sit on the title row.
4. `☐ Yes  ☐ No` is one line; boxes are ballot boxes, not `□`.
5. Data tables are readable Word tables (or pictures at source size), not clipped, not covering the header.
6. Body and header are Calibri 10.5 pt.
7. `lookup.py --en` on the body: locks present, banned list empty.
