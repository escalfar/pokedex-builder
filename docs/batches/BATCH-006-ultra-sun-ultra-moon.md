# BATCH-006 — Ultra Sun / Ultra Moon

**Feature branch:** `feature/catalog-game-availability`  
**Batch:** 006  
**Status:** Regional Pokédex, QR methods, and Ultra Warp Ride audited

## Objective

Classify the expanded Alola Pokédex and the permanent encounter systems outside
that regional Pokédex.

## QR methods

- Magearna counts as `TRUE`, but only through its permanent QR Code gift.
- All daily Island Scan encounters count as `TRUE` through QR Scanner points.
- Marshadow and Zeraora remain `FALSE` because they require event distributions.

## Ultra Warp Ride

Ultra Warp Ride is a permanent in-game method and therefore counts as `TRUE`.
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
