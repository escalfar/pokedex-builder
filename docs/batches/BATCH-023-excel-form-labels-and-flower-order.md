# Batch 023 — Excel form labels and flower ordering

## Objective

Refine only the presentation of the `Nombre` column and row order in the generated `.xlsx` file. The internal catalog, HOME IDs, CSV, JSON, and domain models remain unchanged.

## Excel-only base-form labels

The normal record for each of these species now displays its explicit form in `Nombre`:

- Deoxys — Normal Form
- Wormadam — Plant Cloak
- Shaymin — Land Form
- Basculin — Red-Striped Form
- Pumpkaboo — Average Size
- Gourgeist — Average Size
- Oricorio — Baile Style
- Lycanroc — Midday Form
- Toxtricity — Amped Form
- Urshifu — Single Strike Style
- Squawkabilly — Green Plumage
- Tatsugiri — Curly Form
- Gimmighoul — Chest Form

## Flower-form ordering

Flabébé, Floette, and Florges use the same Excel order:

1. Red Flower
2. Yellow Flower
3. Orange Flower
4. Blue Flower
5. White Flower

`Floette (Eternal)` is placed after all five standard flower colors.

## Scope

These rules affect only the `.xlsx` exporter. They do not modify internal names, forms, HOME IDs, CSV output, or JSON output.

## Validation

Tests verify every Excel-only base-form label, the common flower sequence, and that Eternal Floette is the final Floette row.
