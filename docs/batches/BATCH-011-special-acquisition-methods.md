# BATCH-011 — Special Acquisition Methods

**Feature Branch:** `feature/catalog-game-availability`  
**Batch:** 011  
**Status:** Completed  
**Scope:** Documentation normalization; no availability values changed

## Objective

Normalize how special acquisition requirements are documented in the game
availability catalog. A row remains `TRUE` whenever the Pokémon is obtainable
in the game under the project rules, while the comment records the exact
requirement.

## Standard terminology

- **Method: QR Code** — obtainable only through QR Code.
- **Method: Island Scan QR Code** — obtainable only through Island Scan QR Codes.
- **Method: Mystery Gift** — obtainable only through Mystery Gift.
- **Method: Save Data** — obtainable only through qualifying save data from
  another Pokémon game.
- **Method: DexNav / Mirage Spots / Soaring** — obtainable through permanent
  ORAS in-game systems.
- **Method: Ultra Warp Ride** — obtainable through the permanent USUM feature.
- **Method: Dynamax Adventures** — obtainable through the permanent Crown
  Tundra Max Lair feature.

## Documented cases

### Sun / Moon and Ultra Sun / Ultra Moon

Magearna is documented as obtainable **only through QR Code**. Island Scan
species are documented as obtainable **only through Island Scan QR Codes**.
These comments deliberately avoid describing QR acquisition as ordinary
in-game availability.

### Legends: Arceus and Brilliant Diamond / Shining Pearl

Darkrai, Shaymin, Mew, Jirachi, and Arceus retain `TRUE` availability where
applicable, with their required external save data documented explicitly.

### Scarlet / Violet and Legends: Z-A

Pecharunt, Mewtwo, Diancie, and Zeraora retain `TRUE` availability where
applicable, but are documented as obtainable only through Mystery Gift.

### ORAS, USUM, and Sword / Shield

DexNav, Mirage Spots, soaring encounters, Ultra Warp Ride, and Dynamax
Adventures are documented as permanent in-game acquisition methods.

## Validation

A regression test treats the standardized comments as part of the catalog's
documentation contract. This prevents later edits from accidentally describing
QR Code or other restricted methods as ordinary availability.

## Behavioral impact

None. This batch changes comments and technical documentation only; the parsed
YAML data and generated Boolean values are unchanged.
