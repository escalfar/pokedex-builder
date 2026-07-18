# BATCH-006 — Ultra Sun / Ultra Moon

**Feature branch:** `feature/catalog-game-availability`  
**Batch:** 006  
**Status:** Regional Pokédex, QR methods, and Ultra Warp Ride audited

## Objective

Classify the expanded Alola Pokédex and the permanent encounter systems outside
that regional Pokédex.

## QR methods

- **Method: QR Code.** Magearna is obtainable only through QR Code.
- **Method: Island Scan QR Code.** Island Scan species are obtainable only
  through Island Scan QR Codes.
- Marshadow and Zeraora remain `FALSE` because they require event distributions.

## Ultra Warp Ride

**Method: Ultra Warp Ride.** These encounters are obtainable through a permanent
in-game feature and therefore count as `TRUE`.
The catalog includes:

- The 20 repeatable non-Legendary species in the Ultra Space Wilds.
- Prior-generation Legendary Pokémon available through colored wormholes.
- Ultra Beasts already represented by the regional catalog.

Later regional forms of those species remain explicitly excluded.

## Other form decisions

Own Tempo Rockruff and Dusk Form Lycanroc remain unavailable because their
originating Rockruff depended on a limited Mystery Gift.

## Coverage decision

`usum.complete` remains `false`, but QR and Ultra Warp Ride rows are now
verified rather than unknown.

## Sources

- Official Pokémon Magearna QR Code documentation.
- Bulbapedia Ultra Warp Ride and Ultra Space Wilds encounter tables.
- USUM Island Scan encounter tables.

## Tests

Regression tests verify Magearna, Island Scan, Ultra Space Wilds, Legendary
wormhole encounters, event-only species, later regional forms, and coverage.
