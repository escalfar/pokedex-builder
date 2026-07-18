# Batch 002 — Pokémon Legends: Arceus

## Objective

Classify all Pokémon HOME-compatible variants obtainable in Pokémon Legends:
Arceus for the `Legends Arceus` output column.

## Special acquisition methods

- **Method: Save Data.** Darkrai is obtainable only through save data from
  Pokémon Brilliant Diamond or Pokémon Shining Pearl. The research request is
  available after viewing the end credits.
- **Method: Save Data.** Shaymin is obtainable only through save data from
  Pokémon Sword or Pokémon Shield. Its research request is available after the
  end credits.
- Both methods count as `TRUE` because they do not depend on a timed event.

## Rules retained

- All 242 species in the Hisui Pokédex are classified.
- Hisuian forms and new Hisui evolutions remain available.
- Darkrai, Land Forme Shaymin, and Sky Forme Shaymin are explicitly documented
  as save-data-gated permanent acquisitions.
- Red-Striped and Blue-Striped Basculin remain unavailable; Hisui provides
  White-Striped Basculin.
- Bloodmoon Ursaluna remains unavailable because it was introduced later.

## Sources

- Official Pokémon Legends: Arceus save-data bonus page.
- Hisui Pokédex references from PokéAPI, Bulbapedia, and Serebii.

## Validation

Regression tests verify the save-data Darkrai and Shaymin methods, regional
form precedence, stored forms, and complete coverage behavior.
