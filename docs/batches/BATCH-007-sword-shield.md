# BATCH-007 — Sword / Shield

**Feature branch:** `feature/catalog-game-availability`  
**Batch:** 007  
**Status:** Regional Pokédex tranche completed; transferable extras pending

## Objective

Add the verified Sword/Shield availability core from the three Generation VIII
regional Pokédexes:

- Galar Pokédex
- Isle of Armor Pokédex
- Crown Tundra Pokédex

The rules remain deliberately incomplete because several Pokémon can be used in
Sword/Shield without belonging to any of those three Pokédexes, including some
Dynamax Adventure encounters and HOME-transfer-only species.

## Sources

- PokéAPI `pokemon_dex_numbers.csv`, Pokédex IDs 27, 28, and 29.
- Pokémon Database: Sword/Shield, Isle of Armor, and Crown Tundra Pokédex lists.
- Pokémon HOME storage rules for fused Calyrex forms.

The union of the three regional Pokédexes contains 584 species. Zarude is
removed from the positive set because both Normal and Dada Zarude required event
distributions, leaving 583 species classified as obtainable without an event.

## Rules added

- Species in the three regional Pokédexes inherit Sword/Shield availability.
- Supported Alolan and Galarian forms inherit the species rule.
- Hisuian and Paldean forms are explicitly excluded.
- White-Striped Basculin is excluded because it was introduced in Legends:
  Arceus.
- Zarude and Dada Zarude are explicitly classified as unavailable without an
  event.
- Ice Rider and Shadow Rider Calyrex are excluded because fused states cannot
  be deposited in Pokémon HOME; base Calyrex remains available.
- Cosplay Pikachu costumes remain excluded because they cannot be transferred.

## Tests added

- The regional union contains exactly 583 non-event species.
- Galarian and supported Alolan forms are accepted.
- Later regional forms are rejected.
- Zarude and fused Calyrex states are rejected.
- Coverage distinguishes verified regional rows from transferable species that
  are still pending audit.

## Coverage status

`swsh.complete` remains `false`.

A later Sword/Shield audit will classify Pokémon outside the three regional
Pokédexes that are nevertheless compatible through HOME transfer, gifts, or
Dynamax Adventures.
