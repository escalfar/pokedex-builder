# Batch 30 — Excel possible totals and conditional-format fixes

## Scope

- Correct Excel 2016 conditional formatting for `Obtenido` and priority `0`.
- Center `Nat Dex` values.
- Add the final hidden `Posibles` column.
- Add dynamic collection statistics to `Resumen`.

## Excel behavior

- `Obtenido` turns blue only when its value is `☑`.
- Blank priority cells have no fill.
- Priority `0` uses a light-purple fill.
- Priorities 1–10 use ten exact-value fills progressing from red to green, avoiding the Excel 2016 overlap between a color scale and the special `0` rule.
- `Posibles` uses `=OR(Obtenido="☑", Obtenible=TRUE)` for each data row and is hidden by default.
- Workbook calculation mode is automatic and formulas are forced to recalculate when opened.

## Resumen

The summary sheet now includes formulas for:

- Total obtained.
- Total not obtained.
- Total possible.
- Obtained divided by possible, formatted as a percentage.

These metrics update when the user changes `Obtenido`.

## Other exports

CSV and JSON include the final `Posibles` field as blank/`null`, since their rows cannot provide an interactive Excel formula.
