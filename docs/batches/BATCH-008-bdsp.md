# BATCH-008 — Brilliant Diamond / Shining Pearl

**Feature branch:** `feature/catalog-game-availability`  
**Batch:** 008  
**Status:** Completed

## Objective

Complete Brilliant Diamond / Shining Pearl availability for the first 493
species and all retained form-level exceptions.

## Save-data-only permanent unlocks

The following rows count as `TRUE` under **Method: Save Data** and are
obtainable only through qualifying save data:

- Mew: Pokémon: Let’s Go, Pikachu! or Let’s Go, Eevee! save data.
- Jirachi: Pokémon Sword or Pokémon Shield save data.
- Arceus: qualifying completed Pokémon Legends: Arceus save data.

These methods are permanent and do not depend on a timed distribution.

## Other decisions

- Later regional forms, Cosplay Pikachu, and temporary Castform states remain
  unavailable.
- Celebi and all four Deoxys Formes remain in the project but are unavailable
  as BDSP-origin encounters.
- Phione, Manaphy, Darkrai, and Shaymin remain unavailable because their native
  BDSP methods depended on expired distributions or Mystery Gift items.

## Sources

- Official BDSP save-data bonus page for Mew and Jirachi.
- Official Pokémon announcement for the Arceus save-data encounter.
- BDSP National Pokédex and HOME compatibility references.

## Tests

Regression tests distinguish permanent save-data unlocks from expired events,
retain all Deoxys rows, and confirm complete coverage.
