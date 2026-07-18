# Batch 024 — Excel Name Label Simplification

## Objective

Simplify selected form labels exclusively in the `Nombre` column of the generated
Excel workbook. Domain objects, HOME IDs, YAML catalogs, CSV output, and JSON
output remain unchanged.

## Changes

- Removed `Breed` from the three Paldean Tauros labels.
- Simplified the selected base-form labels, including Deoxys, Wormadam, Shaymin,
  Basculin, Pumpkaboo, Gourgeist, Oricorio, Lycanroc, Toxtricity, Urshifu,
  Squawkabilly, Tatsugiri, and Gimmighoul.
- Removed `Cloak` from Burmy and the base Wormadam display labels.
- Reduced Basculin and Squawkabilly labels to their colors.
- Removed `Pattern` from every Vivillon display label.
- Removed `Flower` from Flabébé, Floette, and Florges display labels while
  preserving their shared color order and keeping Floette (Eternal) last.
- Renamed Average Size to Medium and Super Size to Jumbo for Pumpkaboo and
  Gourgeist.
- Reduced Urshifu styles to `Single` and `Rapid`.

## Scope

All transformations occur only while writing the Excel `Nombre` column. Internal
forms and names are not mutated.
