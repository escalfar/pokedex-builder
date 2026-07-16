# BATCH-004 — Omega Ruby / Alpha Sapphire

**Feature branch:** `feature/catalog-game-availability`  
**Batch:** 004  
**Status:** Regional catalog foundation  

## Objective

Add the verified Omega Ruby / Alpha Sapphire regional Pokédex core to the game availability catalog without prematurely classifying the additional post-National-Dex encounters.

## Scope

This batch classifies the 211-entry updated Hoenn Pokédex, excluding Jirachi because it requires an external event. All four Deoxys formes are retained because Deoxys is obtainable through the Delta Episode and can change forme in ORAS.

The resulting verified species set contains **210 National Dex species**.

## Form handling

The catalog explicitly excludes:

- Cosplay Pikachu, because it cannot be transferred to Pokémon Bank or Pokémon HOME.
- Castform weather transformations, because they are temporary battle states rather than retained HOME forms.
- Alolan, Galarian, and Hisuian forms introduced after Generation VI when they share a National Dex number with a covered species.

Visible female and male differences remain available when the underlying species is present because both appearances are valid stored Pokémon.

## Coverage decision

`oras.complete` remains `false` in this batch. ORAS also contains Pokémon obtainable after receiving the National Pokédex through DexNav, Mirage Spots, soaring encounters, gifts, and other methods. Those encounters require a separate verified pass before unmatched entries can safely be treated as unavailable.

## Sources

- PokéAPI updated Hoenn Pokédex (`pokedex/15`).
- Pokémon Omega Ruby / Alpha Sapphire Delta Episode documentation for Deoxys.
- Pokémon Bank and HOME transfer restrictions for Cosplay Pikachu.

## Tests added

Regression tests verify that:

- The regional non-event set contains 210 species.
- Jirachi is not classified as obtainable by this tranche.
- Normal, Attack, Defense, and Speed Forme Deoxys are all retained and available.
- Later regional forms do not inherit availability from their base species.
- Coverage remains incomplete for entries outside the regional tranche.

## Next step

Complete the ORAS post-National-Dex availability pass before setting `oras.complete` to `true`.
