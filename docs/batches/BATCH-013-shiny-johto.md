# BATCH-013 — Shiny Catalog: Johto

**Feature branch:** `feature/catalog-shiny`  
**Batch:** 013  
**Status:** Completed

## Objective

Classify every retained Pokémon HOME variant whose National Dex number is
152–251 under the project rule: `Obtenible = TRUE` only when a legitimate shiny
can be obtained without relying on a limited distribution event.

## Scope

Files modified:

```text
data/shiny_availability.yaml
tests/test_shiny_availability.py
tests/test_catalog_coverage.py
docs/batches/BATCH-013-shiny-johto.md
```

## Decisions

### National Dex 152–251

Every retained HOME variant sharing a Johto National Dex number is classified
`TRUE`. The species-level range intentionally covers later regional forms too,
because those retained forms also have legitimate non-event shiny methods in
core games. Examples include Hisuian Typhlosion, Hisuian Qwilfish, Hisuian
Sneasel, Galarian Corsola, Galarian Slowking, and Paldean Wooper.

### Celebi

Celebi is classified `TRUE` through the in-game GS Ball encounter in the
Nintendo 3DS Virtual Console release of Pokémon Crystal. The international
Virtual Console release unlocks the GS Ball after entering the Hall of Fame, so
the encounter is not a distribution event and Celebi may be shiny.

This route now has an important operational limitation: Pokémon Crystal can no
longer be newly purchased from the closed Nintendo 3DS eShop. A legitimate
transfer into Pokémon HOME therefore requires a legacy installation of Crystal
and access to Pokémon Bank/Poké Transporter. The catalog records the species as
obtainable because the encounter itself is legitimate and non-event, but the
legacy requirement is documented explicitly.

Pokémon GO is not used for Celebi because a legitimate core-series method
exists, consistent with the project's source-priority rule.

## Coverage behavior

The inclusive range `[152, 251]` classifies normal, gendered, regional, and
other retained HOME variants in the tranche. Form-level exclusions would still
override the range if a future audit discovers a shiny-locked retained form.

## Tests

Regression coverage verifies that:

- normal and Hisuian Typhlosion are `TRUE`;
- Paldean Wooper inherits the Johto species rule;
- Celebi is `TRUE`;
- the legacy GS Ball method remains documented;
- the coverage report counts Johto sample rows as verified `TRUE`.

## Sources

- Bulbapedia, Celebi: identifies Virtual Console Crystal as a legitimate
  in-game, non-distribution Celebi encounter.
- Bulbapedia, Pokémon Crystal Version and GS Ball: documents the Hall of Fame
  unlock in all Virtual Console language releases.
- Bulbapedia, List of unobtainable Shiny Pokémon: confirms that the Virtual
  Console Crystal encounter can legitimately produce Shiny Celebi.
- Bulbapedia and the relevant core-game availability pages for retained Johto
  regional variants.

## Next batch

`BATCH-014` will classify the Hoenn tranche and document its species- and
form-specific shiny exceptions.
