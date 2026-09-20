# Word / PDF layout (English delivery)

A page that still shows Chinese, 宋体 on English, or a wrapped Yes/No box is not finished.

## Font

After CN to EN, set Latin text to **Calibri** (ascii / hAnsi / cs). Do not leave 宋体 on English letters. East-Asian font may stay Calibri on an English-only file. Body size follows the source (often 10.5 pt).

## Checkboxes

Source `□是  □否` is one line in a narrow column.

- Keep **one line**: `□ Yes  □ No`
- Set the cell `noWrap`. Widen the column a little if Word still wraps.
- 9 pt is allowed in that column only.
- Turn off auto-hyperlink. `Yes` must not turn blue or underlined.

Do not expand the cell into:

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
3. Checkbox column is one line in a sample row.
4. Latin font is Calibri (or the source's Latin font if it already had one).
5. lookup.py `--en` on the body text: locked terms present, banned list empty.
