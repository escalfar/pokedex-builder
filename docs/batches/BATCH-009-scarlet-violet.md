# BATCH-009 — Scarlet / Violet

## Objective

Complete the Scarlet/Violet availability catalog using the Paldea, Kitakami,
and Blueberry regional Pokédexes, including both DLC expansions.

## Coverage

- Paldea Pokédex: 400 species.
- Kitakami Pokédex: 200 species.
- Blueberry Pokédex: 243 species.
- Union: 664 unique species.
- Positive non-event set: 661 species.

Walking Wake, Iron Leaves, and Pecharunt remain unavailable because their
acquisition depends on limited-time or externally distributed event content.

## Form decisions

- Paldean breeds, Bloodmoon Ursaluna, Roaming Gimmighoul, and other retained
  HOME forms belonging to included species remain available.
- Cosplay Pikachu costumes are excluded.
- Koraidon and Miraidon ride modes are excluded because they are temporary
  states rather than depositable HOME forms.

## Sources

- https://pokeapi.co/api/v2/pokedex/31/
- https://pokeapi.co/api/v2/pokedex/32/
- https://pokeapi.co/api/v2/pokedex/33/
- https://scarletviolet.pokemon.com/en-gb/events/regulation-j/

## Tests

Regression tests cover the three regional Pokédexes, event-only species,
regional forms, temporary ride modes, and complete catalog coverage.
