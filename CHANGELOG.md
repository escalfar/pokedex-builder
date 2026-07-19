
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
