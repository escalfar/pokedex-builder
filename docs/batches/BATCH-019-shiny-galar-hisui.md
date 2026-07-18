# BATCH-019 — Shiny Catalog: Galar and Hisui

**Feature branch:** `feature/catalog-shiny`  
**Status:** Completed

## Objective

Classify every retained Pokémon HOME variant with National Dex numbers
`810–905` according to whether it has a permanent legitimate shiny acquisition
method that does not require a limited event.

## Files modified

```text
data/shiny_availability.yaml
tests/test_shiny_availability.py
tests/test_catalog_coverage.py
docs/batches/BATCH-019-shiny-galar-hisui.md
```

## Rules added

- The inclusive National Dex range `810–905` is classified as shiny obtainable.
- Explicit exclusions override the range for shiny-locked or event-only species.
- Retained forms inherit the species rule unless an explicit form exclusion exists.

## Special cases

### Zacian, Zamazenta, and Eternatus

All remain `FALSE`. Their permanent encounters are shiny-locked, and their
legitimate shiny releases were limited-time distributions.

### Kubfu and Urshifu

Kubfu and both Urshifu styles remain `FALSE`. They have no catchable legitimate
shiny release. A temporary raid-event oversight could display a shiny Urshifu,
but that raid boss could not be caught.

### Zarude

Normal Zarude and Dada Zarude remain `FALSE` because neither has a legitimate
shiny acquisition method.

### Regieleki and Regidrago

Both are `TRUE`. Their permanent temple encounters in The Crown Tundra are not
shiny-locked.

### Glastrier, Spectrier, and Calyrex

All remain `FALSE`. Their permanent Crown Tundra encounters are shiny-locked,
and no permanent legitimate shiny method has been released. This applies to
normal Calyrex and its retained Ice Rider and Shadow Rider forms.

### Hisui species and Enamorus

Wyrdeer, Kleavor, Ursaluna, Basculegion, Sneasler, and Overqwil are `TRUE`
through permanent breeding, evolution, outbreak, or encounter methods. Enamorus
is `TRUE` through the permanent Pokémon HOME reward for completing the Hisui
Pokédex from Pokémon Legends: Arceus.

## Tests added

- Standard Galar and Hisui species.
- Regieleki permanent shiny encounter.
- Enamorus Pokémon HOME reward.
- Zacian, Eternatus, Kubfu, Urshifu, Zarude, Glastrier, and Calyrex exclusions.
- Coverage accounting with four verified `TRUE` and three verified `FALSE` rows.
- Regression checks preserving explanatory catalog comments.

## Sources

- Pokémon HOME Pokédex-completion rewards.
- Pokémon Sword and Shield: The Crown Tundra encounter and shiny-lock data.
- Pokémon Legends: Arceus and Hisui Pokédex completion information.
- Bulbapedia list of unobtainable Shiny Pokémon.

## Next batch

`BATCH-020 — Shiny Catalog: Paldea and Kitakami`
