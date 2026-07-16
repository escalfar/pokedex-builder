# Batch 002 — Pokémon Legends: Arceus

## Objective

Classify the Pokémon HOME-compatible variants obtainable in Pokémon Legends:
Arceus for the `Legends Arceus` output column and mark the game catalog as
fully audited.

## Sources

- PokéAPI `pokemon_dex_numbers.csv`, Hisui Pokédex ID 30 (242 species).
- Bulbapedia, *List of Pokémon by Hisui Pokédex number*, used to verify forms
  represented in the regional Pokédex.
- Serebii, *Hisui Pokédex* and *Hisuian Form Pokémon*, used as a secondary
  cross-check for regional forms and new evolutions.

## Rules added

- Added all 242 species in the Hisui Pokédex through explicit National Dex
  numbers and compact inclusive ranges.
- Kept both Kantonian and Alolan Vulpix/Ninetales because the Alolan line is
  obtainable through the in-game request.
- Kept both Johtonian and Hisuian Sneasel because both are obtainable in PLA.
- Kept all stored Burmy, Wormadam, Shellos, Gastrodon, Rotom, Unown, Shaymin,
  forces-of-nature, and Enamorus forms represented by the project.
- Excluded non-Hisuian final starter evolutions and other non-Hisuian forms
  where PLA only provides the Hisuian form.
- Excluded Red-Striped and Blue-Striped Basculin; only White-Striped Basculin
  is available in Hisui.
- Excluded Bloodmoon Ursaluna because it was introduced after PLA.
- Marked the PLA game rule as complete, so variants absent from the audited
  positive list are counted as verified unavailable instead of unknown.

## Validation

Regression tests cover:

- Hisuian-only final starter forms.
- White-Striped Basculin versus its other stripes.
- Both forms of Sneasel.
- Alolan Vulpix and exclusion of unrelated regional forms.
- Bloodmoon Ursaluna exclusion.
- Per-game completeness and 100% coverage behavior.
