# BATCH-018 — Shiny Catalog: Alola

**Feature branch:** `feature/catalog-shiny`  
**Status:** Completed

## Objective

Classify every retained Pokémon HOME variant with National Dex numbers
`722–809` according to whether it has a permanent legitimate shiny acquisition
method that does not require a limited event.

## Files modified

```text
data/shiny_availability.yaml
tests/test_shiny_availability.py
tests/test_catalog_coverage.py
docs/batches/BATCH-018-shiny-alola.md
```

## Rules added

- The inclusive National Dex range `722–809` is classified as shiny obtainable.
- Explicit exclusions override that range for Cosmog, Cosmoem, Magearna,
  Marshadow, Zeraora, and Melmetal.
- Regional, gender, size, and retained Necrozma forms inherit the species rule
  unless an explicit form exclusion exists.

## Special cases

### Cosmog, Cosmoem, Solgaleo, and Lunala

Cosmog and Cosmoem remain `FALSE` because they have never had a legitimate
shiny release. Solgaleo and Lunala are `TRUE` because they can be encountered
and shiny hunted permanently in Dynamax Adventures in The Crown Tundra.

### Guardian deities, Ultra Beasts, and Necrozma

These species are `TRUE`. Permanent encounters such as Ultra Warp Ride and
Dynamax Adventures provide legitimate non-event shiny methods. Retained
Necrozma forms are covered because a shiny Necrozma can change form in
compatible games.

### Magearna and Marshadow

Both remain `FALSE` because neither has a legitimate shiny acquisition method.

### Zeraora

Zeraora remains `FALSE`. Its shiny release was a time-limited Pokémon HOME
Mystery Gift in 2020 and therefore does not satisfy the permanent non-event
rule.

### Meltan

Meltan is `TRUE` through the permanent Pokémon HOME reward for completing the
Kanto Pokédex using Pokémon: Let's Go, Pikachu! or Pokémon: Let's Go, Eevee!
Pokémon GO is not used because this permanent HOME method exists.

### Melmetal

Melmetal remains `FALSE`. Meltan can evolve only in Pokémon GO, but a Meltan
received in Pokémon HOME cannot be transferred back to GO. Legitimate shiny
Melmetal therefore still depends on time-limited periods when Shiny Meltan is
enabled in Pokémon GO.

## Tests added

- Standard Alola species and permanent shiny encounters.
- Cosmog exclusion and Solgaleo/Lunala Dynamax Adventures inclusion.
- Necrozma inclusion.
- Magearna, Marshadow, and Zeraora exclusions.
- Permanent Shiny Meltan HOME reward.
- Shiny Melmetal exclusion.
- Coverage accounting with five verified `TRUE` and three verified `FALSE`
  sample rows.
- Regression checks preserving the explanatory catalog comments.

## Sources

- Pokémon HOME — Pokédex Completion Rewards:
  https://home.pokemon.com/en-us/features/
- Pokémon — Complete Pokédexes to Earn Shiny Keldeo and Shiny Meltan in
  Pokémon HOME:
  https://www.pokemon.com/uk/pokemon-news/complete-pokedexes-to-earn-shiny-keldeo-and-shiny-meltan-in-pokemon-home
- Pokémon Sword and Shield — Shiny Zeraora distribution:
  https://swordshield.pokemon.com/en-au/expansionpass/mythical-zeraora/
- Dynamax Adventures encounter list and shiny mechanics:
  https://www.serebii.net/swordshield/dynamaxadventures.shtml
  https://www.serebii.net/swordshield/dynamaxadventurespokemon.shtml
- Pokémon: Let's Go — Meltan evolution information:
  https://pokemonletsgo.pokemon.com/es-la/new-pokemon/

## Next batch

`BATCH-019 — Shiny Catalog: Galar and Hisui`
