# BATCH-015 — Shiny Catalog: Sinnoh

**Feature branch:** `feature/catalog-shiny`  
**Status:** Completed

## Objective

Classify retained Pokémon HOME variants with National Dex numbers `387–493`
according to whether their Shiny form can be obtained legitimately without a
limited-time event.

## Rules added

- Added the inclusive National Dex range `387–493`.
- Manaphy is `TRUE` through the permanent Pokémon HOME reward for completing
  the Brilliant Diamond and Shining Pearl Sinnoh Pokédex.
- Phione is `TRUE` because it can be bred from Manaphy in compatible games.
- Arceus is `TRUE` through the permanent Hall of Origin encounter in Brilliant
  Diamond and Shining Pearl after satisfying the Pokémon Legends: Arceus
  save-data and progression requirements.
- Darkrai is `FALSE`; its legitimate Shiny routes depend on a limited-time
  Member Card or rotating/event Pokémon GO access.
- Shaymin Land Forme and Sky Forme are `FALSE`; their legitimate Shiny routes
  depend on the limited-time Oak's Letter or event-style Pokémon GO research.

## Pokémon GO policy

Pokémon GO is considered only when it is the sole permanent legitimate route.
It is not used for Darkrai or Shaymin because their GO availability is tied to
rotating raids or limited research rather than a permanent acquisition method.

## Tests

Regression tests verify:

- Standard Sinnoh species are `TRUE`.
- Manaphy, Phione, and Arceus are `TRUE`.
- Darkrai and both Shaymin forms are `FALSE`.
- Coverage reports classify all sampled rows with no unknown values.

## Sources

- Bulbapedia: *List of unobtainable Shiny Pokémon*.
- Bulbapedia: *Pokémon Brilliant Diamond and Shining Pearl*.
- Official Pokémon announcement for the BDSP Arceus encounter.
