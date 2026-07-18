# Batch 022 — HOME Form Corrections and Excel Display Names

## Objective

Align the generated catalog with Pokémon HOME form storage and improve the
Excel-only presentation of the `Nombre` column without changing internal names
or the CSV and JSON exports.

## Removed forms

The following forms are excluded because Pokémon HOME does not store them as
independent forms:

- Cosplay Pikachu: Belle, Libre, PhD, Pop Star, and Rock Star
- Castform: Rainy, Snowy, and Sunny
- Kyurem: Black and White
- Meloetta: Pirouette
- Necrozma: Dawn Wings and Dusk Mane
- Calyrex: Ice Rider and Shadow Rider
- Koraidon: Limited, Sprinting, Swimming, and Gliding Build
- Miraidon: Low-Power, Drive, Aquatic, and Glide Mode

The exclusions are defined by exact PokéAPI variety name so they cannot be
reintroduced accidentally by broader form rules.

## Added HOME-persistent forms

The builder now supplements PokéAPI species varieties with cosmetic forms that
Pokémon HOME stores independently but PokéAPI exposes outside the varieties
list:

- Burmy: Plant Cloak, Sandy Cloak, and Trash Cloak
- Vivillon: all 20 patterns, including Fancy and Poké Ball
- Flabébé: Red, Yellow, Orange, Blue, and White Flower
- Floette: Red, Yellow, Orange, Blue, and White Flower
- Florges: Red, Yellow, Orange, Blue, and White Flower

The existing normal HOME ID remains the canonical default row for Plant Cloak,
Meadow Pattern, and Red Flower respectively. Supplemental forms receive stable,
deterministic HOME IDs.

Eternal Flower Floette remains a separate retained form.

## Excel-only `Nombre` rule

Only the `.xlsx` exporter changes the presentation of `Nombre`:

- The species name is always the first word.
- A non-normal form is written as `Species (Form)`.
- Internal domain names remain unchanged.
- CSV and JSON retain their existing names.

Examples:

- `Alolan Raichu` → `Raichu (Alolan)` in Excel
- `Sandy Cloak Burmy` → `Burmy (Sandy Cloak)` in Excel
- `Poké Ball Pattern Vivillon` → `Vivillon (Poké Ball Pattern)` in Excel
- `Blue Flower Flabébé` → `Flabébé (Blue Flower)` in Excel

## Validation

- 285 tests passed.
- 1266 catalog rows generated.
- Shiny coverage remains 100% (`1266/1266`).
- All 23 non-HOME-storable IDs are absent from generated outputs.
- Burmy, Vivillon, Flabébé, Floette, and Florges contain the requested forms.
- Excel display names begin with the species while JSON and CSV names remain
  unchanged.
