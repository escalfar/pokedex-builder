# BATCH-005 — Sun / Moon

**Feature branch:** `feature/catalog-game-availability`  
**Batch:** 005  
**Status:** Regional catalog foundation

## Objective

Add the verified Pokémon Sun / Moon regional Pokédex core without prematurely classifying the additional Island Scan encounters.

## Scope

The original Alola Pokédex contains **302 species**. This batch classifies the **300 entries obtainable without external event distributions**:

- Magearna is excluded from the obtainable set because it is received through an external QR-code gift.
- Marshadow is excluded because it requires an event distribution.
- Island Scan encounters remain pending for a separate audit, so `sm.complete` remains `false`.

## Form handling

The catalog gives form-specific precedence to the regional forms used in Alola. Original Kanto forms such as Rattata, Raichu, Sandshrew, Vulpix, Diglett, Meowth, Geodude, Grimer, Exeggutor, and Marowak are excluded where Sun/Moon only produces the Alolan form during normal gameplay.

The catalog also:

- Retains all four Oricorio styles.
- Retains the stored 10% and 50% Zygarde forms available through the Reassembly Unit.
- Retains Midday and Midnight Lycanroc across the paired games.
- Excludes Own Tempo Rockruff, Dusk Lycanroc, and fused Necrozma forms because they were introduced in Ultra Sun / Ultra Moon.
- Excludes later Galarian, Hisuian, and Paldean forms sharing covered National Dex numbers.
- Excludes Cosplay Pikachu and temporary Castform weather states.

Visible female and male differences remain available whenever the underlying stored form is obtainable.

## Coverage decision

`sm.complete` remains `false`. Unmatched entries are still reported as unknown until Island Scan and any other non-regional acquisition methods receive a dedicated verification pass.

Event-only Magearna and Marshadow are explicit verified-false entries rather than unknowns.

## Sources

- PokéAPI original Alola Pokédex (`pokedex/16`).
- Pokémon Sun / Moon Alola Pokédex documentation.
- Bulbapedia regional Pokédex and form documentation.
- Serebii Sun / Moon Alola Pokédex and form references.

## Tests added

Regression tests verify that:

- The non-event regional set contains 300 species.
- Magearna and Marshadow are excluded from normal in-game obtainability.
- Alolan forms override unavailable original forms for replaced Kanto lines.
- Own Tempo Rockruff, Dusk Lycanroc, fused Necrozma, and later regional forms remain unavailable.
- Oricorio and Zygarde retained forms inherit Sun/Moon availability.
- Coverage distinguishes the verified regional tranche from pending Island Scan species.

## Next step

Audit Island Scan and any remaining non-regional Sun/Moon encounters before setting `sm.complete` to `true`.
