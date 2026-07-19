# Batch 28: Excel tracking, priority, and XY header

## Changes

- Added `Prioridad` immediately after `Obtenido`.
- `Prioridad` defaults to blank and accepts blank or whole numbers from 0 through 10.
- Priority 0 uses a light-purple fill.
- Priority values 1 through 10 use a red-to-yellow-to-green color scale.
- Blank priority cells receive no conditional formatting.
- `Obtenido` defaults to `☐` and uses an Excel 2016-compatible dropdown with `☐` and `☑`.
- `Obtenido` receives a blue fill only when `☑` is selected.
- Renamed `X/Y` to `XY` in Excel, CSV, JSON, models, constants, and tests.
