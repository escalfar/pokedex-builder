# BATCH-006 — Ultra Sun / Ultra Moon

**Feature branch:** `feature/catalog-game-availability`  
**Batch:** 006  
**Status:** Completed — regional Pokédex tranche  
**Date:** 2026-07-16

## Objective

Classify the non-event species in the expanded Alola Pokédex for Pokémon Ultra
Sun and Pokémon Ultra Moon, while keeping encounters outside the regional
Pokédex pending for a later audit.

## Scope

Modified files:

```text
data/game_availability.yaml
tests/test_game_availability.py
tests/test_catalog_coverage.py
docs/batches/BATCH-006-ultra-sun-ultra-moon.md
```

## Catalog changes

- Added the 400 non-event species from the 403-entry updated Alola Pokédex.
- Excluded Magearna, Marshadow, and Zeraora because they require external event
  or gift distributions.
- Included Poipole, Naganadel, Stakataka, and Blacephalon, which were introduced
  in Ultra Sun and Ultra Moon.
- Preferred Alolan forms for lines whose original forms are not caught during
  normal play in Alola.
- Excluded Own Tempo Rockruff and Dusk Form Lycanroc because their originating
  Rockruff was distributed through a limited Mystery Gift.
- Excluded regional forms introduced after Generation VII.

## Coverage policy

`usum.complete` remains `false`. The regional Pokédex tranche is classified,
but Island Scan, Ultra Warp Ride, and other encounters outside the regional
Pokédex still require a dedicated audit. Unmatched rows therefore remain
`unknown` in `Catalog_Coverage.json`.

## Priority rules

1. Explicit HOME-ID exclusion.
2. Explicit HOME-ID inclusion.
3. National Dex inclusion or range.
4. Unmatched rows remain unknown while the game rule is incomplete.

## Tests added

- The regional catalog contains exactly 400 non-event species.
- The four non-event Ultra additions are represented.
- Event-only Magearna, Marshadow, and Zeraora are excluded.
- Alolan forms override their original counterparts during normal play.
- Own Tempo Rockruff and Dusk Form Lycanroc remain excluded.
- Later regional forms remain unavailable.
- Coverage distinguishes the verified regional tranche from pending external
  encounters.

## Sources

- PokéAPI updated Alola Pokédex (`pokedex/21`).
- Bulbapedia, “List of Pokémon by Alola Pokédex number in Pokémon Ultra Sun and
  Ultra Moon.”
- The Pokémon Company announcement for special Own Tempo Rockruff / Dusk Form
  Lycanroc distribution.

## Next batch

**BATCH-007 — Sword / Shield**
