
## Batch 27 — Excel tracking column and compact headers

- Added the empty `Obtenido` tracking column to all exports.
- Reordered output columns for collection tracking.
- Shortened game availability headers (`ORAS`, `SM`, `USUM`, `LGPE`, `SwSh`, `Arceus`, `BDSP`, `ScVi`, `ZA`).
- Hid internal/reference columns by default in the main Excel worksheet.

# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- Added all 28 Unown forms (A-Z, !, ?).
- Added seven Alcremie forms based only on Sweets, without cream variations.

### Changed

### Fixed
## Batch 28

### Added
- Added the optional `Prioridad` output column after `Obtenido`.
- Added Excel 2016-compatible dropdowns for `Obtenido` (`☐` and `☑`).
- Added integer validation from 0 to 10 for `Prioridad`, while allowing blank cells.
- Added conditional formatting: obtained cells turn blue only for `☑`; priority 0 is light purple and values 1–10 use a red-to-green scale.

### Changed
- Renamed the game column `X/Y` to `XY` in all output formats.
## Batch 30

### Added
- Added the hidden `Posibles` column at the end of every export schema.
- Added Excel formulas that return `TRUE` when `Obtenido` is `☑` or `Obtenible` is `TRUE`.
- Added dynamic `Resumen` metrics for obtained, not obtained, possible, and obtained-as-a-percentage-of-possible counts.

### Changed
- Centered all `Nat Dex` values in the Excel worksheet.
- Replaced the priority color scale with Excel 2016-compatible exact-value rules from 1 (red) to 10 (green).

### Fixed
- Fixed the blue conditional format for `Obtenido` in Excel 2016.
- Fixed the light-purple conditional format for priority value `0` by preventing overlap with the 1–10 gradient rules.


## Batch 31
- Replaced Excel conditional-format equality rules with formula-based rules for Excel 2016 compatibility.
- `Obtenido` now uses `EXACT($G2,"☑")`.
- `Prioridad` now uses explicit numeric formulas for values 0 through 10.
