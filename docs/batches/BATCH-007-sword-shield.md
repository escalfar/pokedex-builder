# BATCH-007 — Sword / Shield

**Feature branch:** `feature/catalog-game-availability`  
**Batch:** 007  
**Status:** Regional Pokédexes and Dynamax Adventures audited

## Objective

Classify the Galar, Isle of Armor, and Crown Tundra Pokédexes together with
permanently available Dynamax Adventures encounters.

## Dynamax Adventures

**Method: Dynamax Adventures.** These encounters are obtainable through the
permanent Max Lair feature in the Crown Tundra. The catalog adds:

- Legendary Pokémon available as the final special encounter.
- Ultra Beasts unlocked after the Crown Tundra clue progression.
- The Hoenn first-partner lines that are exclusive to Dynamax Adventures among
  non-special encounters.

Representative verified rows include Mewtwo, Xerneas, Nihilego, Sceptile, and
Swampert.

## Form and event decisions

- Supported Alolan and Galarian forms remain available.
- Hisuian and Paldean forms remain unavailable.
- Zarude and Dada Zarude remain `FALSE` because they require event distributions.
- Ice Rider and Shadow Rider Calyrex remain unavailable as stored HOME rows
  because the fusion states cannot be deposited.

## Coverage decision

`swsh.complete` remains `false` because HOME-transfer-only compatible species
outside the audited encounter systems still require a separate pass.

## Sources

- Galar, Isle of Armor, and Crown Tundra Pokédexes.
- Bulbapedia and Serebii Dynamax Adventures encounter tables.

## Tests

Regression tests verify Dynamax Adventures additions, regional forms, Zarude,
Calyrex fusion states, and coverage accounting.
