# BATCH-014 — Shiny Catalog: Hoenn

**Feature branch:** `feature/catalog-shiny`  
**Status:** Completed

## Objective

Classify retained Pokémon HOME variants with National Dex numbers `252–386`
as obtainable shiny without relying on limited-time events.

## Scope

- Added the inclusive Hoenn range `252–386`.
- Included later regional variants whose base species belongs to Hoenn.
- Kept all four Deoxys forms and classified each as shiny obtainable.
- Documented the exceptional legacy method for Jirachi.
- Documented the permanent AuroraTicket method for Deoxys in the Nintendo
  Switch re-releases of FireRed and LeafGreen.

## Special acquisition methods

### Jirachi

Shiny Jirachi can be generated legitimately through the North American
Pokémon Colosseum Bonus Disc and Pokémon Channel. These methods require legacy
hardware and software, but they are game-based and are not limited-time
Mystery Gift distributions. Pokémon GO is therefore not used.

### Deoxys

The Nintendo Switch re-releases of Pokémon FireRed and LeafGreen award the
AuroraTicket permanently after the required post-game milestone. The Birth
Island Deoxys encounter can be shiny. A legitimate shiny Deoxys can later be
changed among Normal, Attack, Defense, and Speed Formes in compatible games,
so every retained Deoxys form is classified as obtainable. Pokémon GO is not
used.

## Files modified

```text
data/shiny_availability.yaml
tests/test_shiny_availability.py
tests/test_catalog_coverage.py
docs/batches/BATCH-014-shiny-hoenn.md
```

## Tests added

- Hoenn range coverage.
- Galarian Zigzagoon inheritance from its Hoenn National Dex number.
- Jirachi special-method regression.
- All four Deoxys forms.
- Coverage reporting for Hoenn sample rows.

## Sources

- Bulbapedia: List of unobtainable Shiny Pokémon.
- Bulbapedia: Pokémon Colosseum Bonus Disc.
- Bulbapedia: AuroraTicket and Birth Island.
- Nintendo Switch FireRed/LeafGreen re-release documentation and observed
  post-game ticket behavior.

## Next batch

`BATCH-015 — Shiny Catalog: Sinnoh`
