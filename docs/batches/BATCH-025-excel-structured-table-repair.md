# Batch 025 — Excel Structured Table Repair

## Objective

Prevent Microsoft Excel from showing a recovery warning and removing the
`PokedexTable` object when opening the generated workbook.

## Cause

The recovery log identified `/xl/tables/table1.xml` as the invalid part. The
cell data, worksheets, styles, and display names were not affected.

## Changes

- Removed the OOXML structured table from the `Pokédex` worksheet.
- Kept the worksheet-level automatic filter over the full populated range.
- Preserved the frozen header row, header styling, boolean fills, widths, and
  all Excel-only `Nombre` transformations.
- Added a regression test confirming that the exported worksheet has an
  automatic filter and contains no structured tables.

## Scope

This changes only the Excel workbook structure. It does not modify catalog
logic, domain objects, HOME IDs, YAML, CSV, or JSON output.
