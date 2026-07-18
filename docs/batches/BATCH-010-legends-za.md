# BATCH-010 — Legends: Z-A

## Objective

Complete the game-availability rules for Pokémon Legends: Z-A using the base
Lumiose Pokédex, Mega Dimension content, current Pokémon HOME compatibility,
and permanent Mystery Gift unlocks.

## Coverage

- Lumiose Pokédex: 232 species.
- Mega Dimension Pokédex: 132 species.
- Combined audited set: 364 unique species.
- Compatible regional forms can be transferred into the game through HOME.
- The Z-A catalog is marked `complete: true`.

## Form decisions

- Eternal Flower Floette is retained as `00670_ETERNAL_NONE`.
- Compatible Alolan, Galarian, and Hisuian forms inherit availability when the
  corresponding species is supported by Z-A.
- Mega Evolutions remain outside the output because they are temporary battle
  transformations and were excluded by the original project specification.
- Cosplay Pikachu costumes remain excluded because they are not depositable
  Pokémon HOME forms.

## Mystery Gift decisions

The game-availability columns answer whether a Pokémon can be obtained in the
game. Therefore permanent Mystery Gift unlocks are marked `TRUE`; the separate
shiny catalog continues to enforce the user's event-free shiny requirement.

- Mewtwo: extra side mission unlocked by receiving Mewtwonite X and Y.
- Diancie: extra side mission unlocked by receiving Diancite.
- Zeraora: obtainable through its Mystery Gift content.

## Sources

- https://pokemondb.net/pokedex/game/legends-z-a
- https://pokemondb.net/pokedex/game/legends-z-a/mega-dimension
- https://legends.pokemon.com/en-us/news/pokemon-home-connectivity
- https://legends.pokemon.com/en-us/news/get-diancie
- https://legends.pokemon.com/en-us/news/get-mewtwo-and-mewtonite-stones

## Tests

Regression tests cover:

- Representative base-game and DLC species.
- Current HOME-compatible regional forms.
- Eternal Flower Floette retention.
- Mystery Gift availability for Mewtwo, Diancie, and Zeraora.
- Storable alternate forms.
- Complete catalog coverage accounting.
