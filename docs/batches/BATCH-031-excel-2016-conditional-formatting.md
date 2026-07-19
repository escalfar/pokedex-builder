# Batch 31 — Excel 2016 conditional formatting

The previous workbook serialized valid `cellIs` rules, but Excel 2016 did not render them reliably for the Unicode check mark and the numeric zero.

This batch replaces those rules with expression rules:

- `Obtenido`: `EXACT($G2,"☑")`
- `Prioridad 0`: `AND(ISNUMBER($H2),$H2=0)`
- `Prioridad 1–10`: equivalent explicit numeric expressions

The column references are anchored and the row remains relative, allowing the formulas to apply correctly to every data row.
