# BATCH-017 — Shiny Catalog: Kalos

**Feature branch:** `feature/catalog-shiny`  
**Status:** Completed

## Objective

Classify every retained Pokémon HOME variant with National Dex numbers
`650–721` according to whether it has a permanent legitimate shiny acquisition
method that does not require a limited event.

## Files modified

```text
data/shiny_availability.yaml
tests/test_shiny_availability.py
tests/test_catalog_coverage.py
docs/batches/BATCH-017-shiny-kalos.md
```

## Rules added

- The inclusive National Dex range `650–721` is classified as shiny obtainable.
- Form-specific exclusions override that range for Eternal Flower Floette,
  Diancie, and both retained Hoopa forms.
- Regional, gender, size, and Zygarde variants inherit the species rule unless
  an explicit form exclusion exists.

## Special cases

### Eternal Flower Floette

Eternal Flower Floette remains `FALSE`. The form has never received a
legitimate release, so no legitimate shiny specimen can be obtained or moved
into Pokémon HOME.

### Xerneas, Yveltal, and Zygarde

These species are classified as `TRUE` through permanent Dynamax Adventures
encounters in The Crown Tundra. A shiny Zygarde obtained there can be changed
among the retained Zygarde forms in compatible games.

### Diancie

Diancie remains `FALSE`. Its shiny releases have depended on limited
distributions, while the permanent Pokémon Legends: Z-A encounter is
shiny-locked.

### Hoopa

Both retained Hoopa forms remain `FALSE`. Hoopa has no permanent legitimate
shiny acquisition method, and changing form cannot create Shininess.

### Volcanion

Volcanion is classified as `TRUE` through the permanent Pokémon HOME reward
introduced on April 27, 2026. The reward requires completion of the Lumiose,
Hyperspace, and Mega Evolution Pokédexes using Pokémon Legends: Z-A origin
data. Pokémon GO is not used because this permanent HOME method exists.

## Tests added

- Standard and later regional Kalos variants.
- Eternal Flower Floette exclusion.
- Multiple retained Zygarde forms.
- Diancie and both Hoopa form exclusions.
- Permanent shiny Volcanion HOME reward.
- Coverage accounting with three verified `TRUE` rows and three verified
  `FALSE` rows.
- Regression checks preserving the explanatory catalog comments.

## Sources

- Pokémon — Receive Shiny Volcanion When You Complete Your Pokémon Legends:
  Z-A Pokédexes:
  https://www.pokemon.com/uk/news/receive-shiny-volcanion-when-you-complete-your-pokemon-legends-z-a-pokedexes
- Serebii — Pokémon HOME Gift Pokémon:
  https://www.serebii.net/pokemonhome/giftpokemon.shtml
- Serebii — Pokémon Legends: Z-A Legendary Pokémon:
  https://www.serebii.net/legendsz-a/legendary.shtml
- Bulbapedia — List of unobtainable Shiny Pokémon:
  https://bulbapedia.bulbagarden.net/wiki/List_of_unobtainable_Shiny_Pok%C3%A9mon

## Next batch

`BATCH-018 — Shiny Catalog: Alola`
