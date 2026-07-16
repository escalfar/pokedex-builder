# BATCH-012 — Shiny Catalog: Kanto

**Feature branch:** `feature/catalog-shiny`  
**Batch:** 012  
**Status:** Completed

## Objective

Begin the verified non-event shiny catalog with National Dex numbers 001–151
and add reusable range support to the shiny rules engine.

## Scope

Files modified:

```text
data/shiny_availability.yaml
pokedex/shiny_availability.py
pokedex/catalog_coverage.py
tests/test_shiny_availability.py
tests/test_catalog_coverage.py
docs/batches/BATCH-012-shiny-kanto.md
```

## Decisions

### National Dex 001–150

Every retained HOME variant sharing National Dex numbers 001–150 is marked
`TRUE`. Pokémon GO is not used when a supported core game already supplies a
permanent, non-event shiny method.

The exception is Galarian Articuno, Galarian Zapdos, and Galarian Moltres. Their
Sword/Shield shiny distributions were limited events, while Pokémon GO now
provides permanent shiny encounters through Daily Adventure Incense. Therefore
GO is currently their only permanent, non-event legitimate shiny source, and
the three variants remain `TRUE` with that exception documented explicitly.

### Mew

Mew is explicitly classified `FALSE`. Legitimate shiny Mew acquisition has
required event-limited items, distributions, or ticket/event research, so it
does not satisfy the project rule of availability without an event.

## Engine changes

The shiny catalog now accepts inclusive ranges:

```yaml
national_dex_ranges:
  - [1, 150]
```

A form-specific exclusion still overrides a species number or range. This keeps
large audited batches readable without losing form-level accuracy.

## Coverage behavior

Coverage now recognizes shiny range rules as verified `TRUE`. A future completed
catalog may also use `complete: true`, in which case unlisted variants become
verified `FALSE` rather than unknown.

## Tests

Regression coverage includes:

- loading inclusive shiny ranges;
- applying a range to normal and regional variants;
- preserving form-specific exclusion priority;
- rejecting malformed or reversed ranges;
- counting range decisions in the coverage report.

## Sources

- Pokémon GO official announcement for the permanent Daily Adventure Incense
  shiny encounters for Galarian Articuno, Zapdos, and Moltres.
- Serebii event records for the limited 2022 Sword/Shield distributions of the
  same three shiny Galarian birds.
- Bulbapedia list of unobtainable and shiny-locked Pokémon.
- Serebii event records for historical shiny Mew distributions.

## Next batch

`BATCH-013` will classify the Johto tranche and document its species-specific
exceptions.
