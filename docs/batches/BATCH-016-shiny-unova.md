# BATCH-016 — Shiny Catalog: Unova

**Feature branch:** `feature/catalog-shiny`  
**Status:** Completed

## Objective

Classify every retained Pokémon HOME variant with National Dex numbers
`494–649` according to whether it has a permanent legitimate shiny acquisition
method that does not require a limited event.

## Files modified

```text
data/shiny_availability.yaml
tests/test_shiny_availability.py
tests/test_catalog_coverage.py
docs/batches/BATCH-016-shiny-unova.md
```

## Rules added

- The inclusive National Dex range `494–649` is classified as shiny obtainable.
- Form-specific exclusions override that range for Victini and Genesect.
- Later regional or gender variants associated with an Unova National Dex
  number inherit the species rule unless a form-specific exclusion exists.

## Special cases

### Keldeo

Shiny Keldeo is classified as obtainable through the permanent Pokémon HOME
Pokédex-completion reward for completing the Galar, Isle of Armor, and Crown
Tundra Pokédexes using Pokémon Sword or Pokémon Shield origin data.

Both retained Keldeo forms are covered by the species-level rule.

### Meloetta

Shiny Meloetta is classified as obtainable through the permanent Pokémon HOME
Pokédex-completion reward for completing the Paldea, Kitakami, and Blueberry
Pokédexes using Pokémon Scarlet or Pokémon Violet origin data.

Pokémon GO is not used because a permanent Pokémon HOME method exists.

### Victini

Victini remains `FALSE`. No permanent legitimate shiny acquisition method is
currently available.

### Genesect

Genesect remains `FALSE`. Its legitimate shiny releases have depended on
limited distributions or rotating/event Pokémon GO availability. Those methods
do not satisfy the project's non-event rule.

## Tests added

- Permanent HOME rewards for Keldeo and Meloetta.
- Both retained Keldeo forms.
- Explicit exclusions for Victini and Genesect.
- Coverage accounting with three verified `TRUE` rows and two verified `FALSE`
  rows.
- Regression checks preserving the explanatory catalog comments.

## Sources

- Pokémon HOME — Pokédex Completion Rewards:  
  https://home.pokemon.com/en-us/features/
- Bulbapedia — List of unobtainable Shiny Pokémon:  
  https://bulbapedia.bulbagarden.net/wiki/List_of_unobtainable_Shiny_Pok%C3%A9mon

## Next batch

`BATCH-017 — Shiny Catalog: Kalos`
