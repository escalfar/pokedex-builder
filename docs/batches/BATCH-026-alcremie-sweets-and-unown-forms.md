# Batch 026 — Alcremie sweets and Unown forms

## Changes

- Adds seven Alcremie catalog rows, one for each Sweet.
- Deliberately ignores Alcremie cream flavors, as required by the project scope.
- Reuses the default Alcremie variety as Strawberry Sweet, preventing an extra
  generic Normal row.
- Adds all 28 Unown forms: A through Z, exclamation mark, and question mark.
- Reuses the default Unown variety as form A, preventing an extra generic Normal
  row.
- Adds deterministic special ordering for both species in variants and final
  export entries.
- Adds regression tests for counts, names, HOME IDs, order, and default-variety
  integrity.

## Expected catalog rows

- Unown: 28 rows.
- Alcremie: 7 rows.
