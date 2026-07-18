# Batch 003 — Pokémon X / Pokémon Y

## Objective

Classify every retained Pokémon HOME-compatible variant obtainable across
Pokémon X and Pokémon Y for the `X/Y` output column and mark the game pair as
fully audited.

## Sources

- PokéAPI `pokemon_dex_numbers.csv`, using the Central Kalos (ID 12), Coastal
  Kalos (ID 13), and Mountain Kalos (ID 14) Pokédexes.
- PokéAPI Pokédex endpoints for the three Kalos regional lists.
- Bulbapedia, *List of Pokémon by availability*, used to confirm that X/Y
  together contain all non-event Pokémon from the three Kalos Pokédexes.
- Bulbapedia regional Kalos Pokédex pages, used to cross-check the 457 total
  entries and the three event-only Mythical Pokémon.

## Rules added

- Added 454 non-event species from the three Kalos Pokédexes through compact
  National Dex ranges and isolated numbers.
- Excluded Diancie, Hoopa, and Volcanion because they require event
  distributions in X/Y.
- Preserved stored forms obtainable in Generation VI, including Wormadam
  cloaks, Rotom appliances, both original Basculin stripes, and all Pumpkaboo
  and Gourgeist sizes represented by the project.
- Preserved visible male/female differences because both sexes can be obtained
  normally when the species is available.
- Excluded all Alolan, Galarian, Hisuian, and Paldean variants that share a
  National Dex number with a species present in Kalos.
- Excluded Cosplay Pikachu costumes, which are specific to Omega Ruby and Alpha
  Sapphire.
- Kept only Zygarde's original 50% Forme with Aura Break. The 10% and Power
  Construct variants were introduced later.
- Marked the X/Y game rule as complete, so every unmatched variant is treated
  as verified unavailable rather than unknown.

## Validation

Regression tests cover:

- The exact 454-species non-event catalog.
- Exclusion of the three event Mythical Pokémon.
- Later regional forms and Cosplay Pikachu.
- Wormadam, Rotom, Basculin, and Pumpkaboo stored forms.
- Original Zygarde versus later Zygarde variants.
- 100% coverage behavior for a completed game rule.
