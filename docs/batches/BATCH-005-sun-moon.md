# BATCH-005 — Sun / Moon

**Feature branch:** `feature/catalog-game-availability`  
**Batch:** 005  
**Status:** Regional Pokédex and QR methods audited

## Objective

Classify the original Alola Pokédex together with permanent QR-based
acquisition methods.

## QR methods

- Magearna counts as `TRUE`, but only through its permanent postgame QR Code.
- Every daily Island Scan encounter counts as `TRUE`. Island Scan is activated
  by accumulating QR Scanner points; it is not a timed event.
- Marshadow remains `FALSE` because it requires an event distribution.

## Form handling

- Alolan forms take precedence where Sun/Moon normally produces the regional
  form rather than the original Kanto form.
- All four Oricorio styles and retained Zygarde forms remain available.
- Own Tempo Rockruff, Dusk Lycanroc, fused Necrozma forms, later regional forms,
  Cosplay Pikachu, and temporary Castform weather states remain unavailable.

## Coverage decision

`sm.complete` remains `false`, but Magearna and all Island Scan encounters are
now verified rather than unknown.

## Sources

- Official Pokémon Magearna QR Code documentation.
- Sun/Moon Island Scan encounter tables.
- PokéAPI original Alola Pokédex.

## Tests

Regression tests verify Magearna, representative Island Scan encounters,
Marshadow exclusion, regional-form precedence, and coverage accounting.
