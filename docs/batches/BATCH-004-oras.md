# BATCH-004 — Omega Ruby / Alpha Sapphire

**Feature branch:** `feature/catalog-game-availability`  
**Batch:** 004  
**Status:** Regional and permanent post-National-Dex methods audited

## Objective

Classify the updated Hoenn Pokédex together with permanently available
post-National-Dex encounter systems.

## Permanent encounter systems

The following methods count as `TRUE` because they remain available in every
save and do not require a timed distribution:

- Post-National-Dex DexNav encounters.
- Daily Mirage Forest, Island, Cave, and Mountain encounters.
- Conditional Mirage Spot and soaring Legendary encounters.

Representative additions include Zorua through DexNav, Cresselia through
Crescent Isle, and Zekrom/Reshiram through conditional Mirage Spots.

## Form handling

- All four retained Deoxys Formes remain available. Deoxys is obtained during
  the Delta Episode and can change Forme using the meteorite in Fallarbor Town.
- Cosplay Pikachu and temporary Castform weather states remain unavailable.
- Regional forms introduced after Generation VI are explicitly excluded so
  they do not inherit species-level availability.
- Jirachi remains unavailable because ORAS requires an external distribution.

## Coverage decision

`oras.complete` remains `false` because the broader non-regional catalog still
contains acquisition categories outside this focused pass. The methods listed
above are nevertheless classified as verified permanent availability.

## Sources

- PokéAPI updated Hoenn Pokédex.
- Serebii ORAS DexNav and soaring/Mirage Spot references.
- Pokémon Database and Bulbapedia Mirage Spot encounter lists.

## Tests

Regression tests cover DexNav, daily Mirage Spots, soaring Legendary
encounters, Deoxys Formes, regional-form exclusions, and coverage accounting.
