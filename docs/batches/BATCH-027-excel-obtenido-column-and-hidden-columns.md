# Batch 27 — Excel tracking column and hidden columns

## Changes

- Added `Obtenido` as an empty editable tracking column.
- Applied the requested output column order.
- Shortened game column headers.
- Hid these columns by default in the `Pokédex` worksheet:
  - `Pokemon`
  - `Forma`
  - `Gen`
  - `ID HOME`
  - `Legendario/Mítico`
  - `Obtenible`

The columns remain present and can be unhidden in Excel. CSV and JSON retain all columns and use an empty value (`null` in JSON) for `Obtenido`.
