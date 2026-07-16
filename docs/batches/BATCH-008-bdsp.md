# BATCH-008 — Brilliant Diamond / Shining Pearl

**Feature branch:** `feature/catalog-game-availability`  
**Batch:** 008  
**Status:** Completed

## Objective

Complete the availability classification for Pokémon Brilliant Diamond and
Pokémon Shining Pearl using the games' National Pokédex and permanent in-game
encounters.

## Sources

- Official Pokémon Brilliant Diamond / Shining Pearl Trainer's Guide.
- Official Pokémon HOME compatibility guidance.
- Bulbapedia: list of Pokémon available in Brilliant Diamond and Shining Pearl.
- Bulbapedia: National Pokédex implementation in BDSP.

BDSP supports the first 493 species. The project therefore uses one inclusive
National Dex range and records form-level exceptions explicitly.

## Rules added

- National Dex numbers 001–493 inherit BDSP availability.
- Gender differences and stable forms available by Generation IV remain
  included, including Wormadam cloaks and Rotom appliances.
- Alolan, Galarian, Hisuian, and Paldean forms are excluded.
- Cosplay Pikachu costumes and temporary Castform weather states are excluded.
- Mew and Jirachi remain included because their save-data gifts are permanent
  and do not depend on a timed distribution.
- Arceus remains included because its encounter is permanently unlockable with
  qualifying Pokémon Legends: Arceus save data.
- Celebi and all four Deoxys Formes remain present in the project but are marked
  unavailable in BDSP because they cannot originate there without transfer.
- Phione, Manaphy, Darkrai, and both Shaymin forms are excluded because their
  native acquisition depended on expired event distributions or items.

## Deoxys decision

All Deoxys Formes are intentionally retained in the generated Pokédex, as
requested. Their BDSP availability is `FALSE`; this does not remove the rows
from CSV, JSON, or Excel.

## Tests added

- The complete range includes 001–493 and excludes later species.
- Gender differences, Wormadam cloaks, and Rotom appliances remain available.
- Later regional forms, Cosplay Pikachu, and temporary Castform states are
  unavailable.
- Every retained Deoxys Forme is classified as unavailable in BDSP.
- Permanent save-data gifts and event-only Mythicals follow the documented
  precedence.
- Coverage reaches 100% for BDSP, with later species treated as verified false.

## Coverage status

`bdsp.complete` is set to `true`.

Every generated row is now classified as either available or unavailable for
Brilliant Diamond / Shining Pearl.
