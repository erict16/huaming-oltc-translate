# Word / PDF layout (English delivery)

A page that still shows Chinese, 宋体 on English, a header overlapping the title row, or a wrapped Yes/No box is not finished.

## Font

After CN to EN, set Latin text to **Calibri** (ascii / hAnsi / cs). Do not leave 宋体 on English letters. East-Asian font may stay Calibri on an English-only file.

Body Latin is **Calibri 10.5 pt** (`w:sz` 21). User locked Calibri. Do not switch to Times.

Do not run Word COM `Range.Font.Name` on the whole document — that bumped header from 10.5 pt to 15 pt and caused overlap.

## Header

Original Chinese header is ONE line: company name (left/center) + document code like `HMTC/WJ-G-2026` (right). English company name is longer. NEVER leave it as one overflowing centered string.

Use a 2-cell header table:

- left = company + "Tap-changer Test Centre"
- right = document code
- both Calibri 10.5 pt (`w:sz` 21)
- table 100% width, bottom border

Delete empty header paragraphs that still have `w:sz` 30 (15 pt).

After translating a Word form, inspect the first page in the actual file: header vs title row must not collide.

## Checkboxes

Source `□是  □否` is one line in a ~2.4 cm column.

`□ Yes  □ No` on one line WILL wrap in WPS even with cell `noWrap` (WPS ignores `noWrap`). Required layout is TWO paragraphs in the cell:

```
□ Yes
□ No
```

9 pt Calibri, centered. Turn off auto-hyperlink. `Yes` must not turn blue or underlined.

Do not ship a wrap that looks like:

```
□ Yes  □
No
```

## Figures and tables inside pictures

`w:t` having no Chinese is not enough. Open every `word/media/*` image.

| What you see | What to do |
|--------------|------------|
| Data table (conductor sizes, limits, footnotes) | Redraw an English table (PIL/Word table) and replace the image. Do not leave a Chinese table with an English caption. |
| CAD / photo with a short label (油温监测点, 加压端, 接地) | Replace the label in the image. Keep the drawing. |
| Circuit / sequence diagram with a Chinese legend | Replace the legend; keep the geometry and the numbers. |

Visible Chinese on a figure is a fail. Ask the user only if a stamp or handwritten mark cannot be read.

## Phrasing on test procedures

Write like IEC 60214 / Huaming OI, not like a machine calque.

- `<= +/- 3%` → `within +/- 3%`
- `do not leave at once` → `do not leave immediately`
- `raise button` → name the control in plain words, or just `raise the current smoothly`
- `take thermal stability as reached` → `consider the temperature stable`
- `Judge the result against` → `Assess the result against`

Keep form numbers, currents, and standard numbers exact. No em-dash.

## Self-check before handing over

1. No CJK in any `w:t`.
2. Every media image viewed; no leftover Chinese labels or untranslated tables.
3. Header is a 2-cell table; first page header does not overlap the title row. No leftover `w:sz` 30 header paragraphs.
4. Checkbox cell is two centered 9 pt lines (`□ Yes` then `□ No`), not one overflowing line and not `□ Yes  □` / `No`.
5. Body Latin font is Calibri 10.5 pt (`w:sz` 21). Header same size. Not Times, not 宋体.
6. lookup.py `--en` on the body text: locked terms present, banned list empty.
