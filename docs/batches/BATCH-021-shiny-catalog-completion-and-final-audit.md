# BATCH-021 — Shiny Catalog Completion and Final Audit

**Feature branch:** `feature/catalog-shiny`  
**Status:** Completed

## Objective

Close the shiny-availability catalog after auditing every retained Pokémon HOME
variant and correct the independent classifications of both Gimmighoul forms.

## Files modified

```text
data/shiny_availability.yaml
tests/test_shiny_availability.py
tests/test_catalog_coverage.py
docs/batches/BATCH-021-shiny-catalog-completion-and-final-audit.md
```

## Final catalog state

- `complete` is now `true`.
- Every retained HOME entry is classified as verified `TRUE` or verified `FALSE`.
- The catalog version is increased to `1.2`.
- The National Dex ranges and explicit exclusions continue to provide 100%
  coverage without duplicating form-specific rules unnecessarily.

## Gimmighoul correction

Pokémon HOME retains Chest Form and Roaming Form as distinct forms, so their
shiny availability is evaluated independently.

- **Chest Form Gimmighoul:** `TRUE`. It has a permanent shiny acquisition method
  through encounters in *Pokémon Legends: Z-A – Mega Dimension*.
- **Roaming Form Gimmighoul:** `FALSE`. Its legitimate shiny availability has
  depended on time-bound Pokémon GO periods and therefore does not satisfy the
  permanent non-event rule.
- **Gholdengo:** `TRUE`. It can be obtained by evolving a shiny Chest Form
  Gimmighoul.

## Audit protections

Tests now ensure that:

- the shiny catalog remains marked complete;
- Chest and Roaming Form Gimmighoul never collapse into one decision;
- Gholdengo follows the permanent Chest Form evolution route;
- a completed catalog reports no unknown shiny rows;
- Generation IX coverage accounts for both Gimmighoul forms independently.

## Sources

- Official *Pokémon Legends: Z-A – Mega Dimension* information for the permanent
  game content.
- Official Pokémon GO event notices confirming that Shiny Roaming Form
  Gimmighoul is enabled only during specified event periods.
- Pokémon HOME form data used by the project catalog to preserve both forms.

## Branch transition

After all local checks pass, merge `feature/catalog-shiny` into `develop`. Do
not merge `develop` into `main` until the integrated build and export validation
also pass on `develop`.
