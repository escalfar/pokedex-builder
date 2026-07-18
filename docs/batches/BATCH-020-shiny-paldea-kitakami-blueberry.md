# BATCH-020 — Shiny Catalog: Paldea, Kitakami, and Blueberry

**Feature branch:** `feature/catalog-shiny`  
**Status:** Completed

## Objective

Classify every retained Pokémon HOME variant with National Dex numbers
`906–1025` according to whether it has a permanent legitimate shiny acquisition
method that does not require a limited event.

## Files modified

```text
data/shiny_availability.yaml
tests/test_shiny_availability.py
tests/test_catalog_coverage.py
docs/batches/BATCH-020-shiny-paldea-kitagami-blueberry.md
```

## Rules added

- The inclusive National Dex range `906–1025` is classified as shiny obtainable.
- Explicit exclusions override the range for shiny-locked or event-only species.
- Retained forms inherit the species rule unless a form-specific exclusion is
  necessary.

## Special cases

### Gimmighoul and Gholdengo

Chest Form and Roaming Form Gimmighoul remain `FALSE`. Shiny Chest Form has
appeared only in limited-time Tera Raid Battle events and neither form has a
permanent non-event shiny route. Gholdengo also remains `FALSE` because it must
evolve from a shiny Gimmighoul.

### Treasures of Ruin

Wo-Chien, Chien-Pao, Ting-Lu, and Chi-Yu remain `FALSE`. Their permanent shrine
encounters are shiny-locked. Their legitimate shiny releases were limited 2025
raid-challenge rewards distributed through Mystery Gift.

### Koraidon and Miraidon

Both species and every retained ride form remain `FALSE`. Their permanent story
encounters are shiny-locked, while their first legitimate shiny releases were
limited serial-code distributions in 2025.

### Walking Wake and Iron Leaves

Both remain `FALSE`. They are available only through rotating Tera Raid Battle
events and do not have a permanent legitimate shiny method.

### Kitakami legendary Pokémon

Okidogi, Munkidori, Fezandipiti, and Ogerpon remain `FALSE` because their
permanent encounters are shiny-locked.

### Blueberry and epilogue legendary Pokémon

Gouging Fire, Raging Bolt, Iron Boulder, Iron Crown, Terapagos, and Pecharunt
remain `FALSE`. None has a permanent legitimate shiny acquisition route.

### Ordinary DLC species

Dipplin, Poltchageist, Sinistcha, Archaludon, and Hydrapple remain `TRUE`
through permanent wild, breeding, evolution, or outbreak methods.

## Tests added

- Ordinary Paldea and DLC species classified as `TRUE`.
- Both retained Gimmighoul forms and Gholdengo exclusions.
- Treasures of Ruin and Koraidon/Miraidon exclusions.
- Walking Wake, Iron Leaves, Loyal Three, Ogerpon, later Paradox legends,
  Terapagos, and Pecharunt exclusions.
- Coverage accounting with three verified `TRUE` and four verified `FALSE`
  sample rows.
- Regression checks preserving explanatory catalog comments.

## Sources

- Official Pokémon Scarlet and Pokémon Violet event notices for Shiny
  Gimmighoul, the Treasures of Ruin, Walking Wake, and Iron Leaves.
- Official 2025 Shiny Koraidon and Shiny Miraidon distribution notice.
- Pokémon Scarlet and Pokémon Violet encounter and shiny-lock data.
- Bulbapedia list of unobtainable Shiny Pokémon, used as a secondary audit.

## Next batch

`BATCH-021 — Shiny Catalog Completion and Final Audit`
