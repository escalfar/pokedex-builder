from __future__ import annotations

from collections.abc import Iterable

from pokedex.constants import Gender, GENDER_SORT_ORDER
from pokedex.exceptions import ValidationError
from pokedex.models import (
    GameAvailability,
    PokemonEntry,
    PokemonSpecies,
    PokemonVariant,
)

_SPECIAL_FORM_ORDER: dict[int, dict[str, int]] = {
    201: {
        "normal": 0,
        **{
            letter.casefold(): index
            for index, letter in enumerate("BCDEFGHIJKLMNOPQRSTUVWXYZ", start=1)
        },
        "exclamation": 26,
        "question": 27,
    },
    666: {
        slug: index
        for index, slug in enumerate(
            (
                "normal",
                "archipelago_pattern",
                "continental_pattern",
                "elegant_pattern",
                "garden_pattern",
                "high_plains_pattern",
                "icy_snow_pattern",
                "jungle_pattern",
                "marine_pattern",
                "modern_pattern",
                "monsoon_pattern",
                "ocean_pattern",
                "polar_pattern",
                "river_pattern",
                "sandstorm_pattern",
                "savanna_pattern",
                "sun_pattern",
                "tundra_pattern",
                "fancy_pattern",
                "poke_ball_pattern",
            )
        )
    },
    869: {
        slug: index
        for index, slug in enumerate(
            (
                "normal",
                "berry_sweet",
                "love_sweet",
                "star_sweet",
                "clover_sweet",
                "flower_sweet",
                "ribbon_sweet",
            )
        )
    },
}


def build_pokemon_entries(
    variants: Iterable[PokemonVariant],
    species: Iterable[PokemonSpecies],
) -> tuple[PokemonEntry, ...]:
    """Build preliminary export entries directly from Pokémon variants."""
    species_by_dex = {item.national_dex: item for item in species}

    entries: list[PokemonEntry] = []

    for variant in variants:
        base_species = species_by_dex.get(variant.national_dex)

        if base_species is None:
            raise ValidationError(
                "Pokémon variant has no matching species: "
                f"{variant.national_dex} "
                f"({variant.display_name})"
            )

        if base_species.name != variant.pokemon:
            raise ValidationError(
                "Pokémon variant and species names do not match: "
                f"{variant.national_dex} "
                f"({variant.pokemon} != {base_species.name})"
            )

        entries.append(
            PokemonEntry(
                national_dex=variant.national_dex,
                pokemon=variant.pokemon,
                form=variant.form_name,
                name=variant.display_name,
                generation=variant.generation,
                home_id=variant.home_id,
                gender=variant.gender,
                availability=GameAvailability(),
                legendary_mythical=(base_species.is_legendary_or_mythical),
                obtainable_shiny=False,
            )
        )

    ordered_entries = sort_pokemon_entries(entries)

    validate_pokemon_entries(ordered_entries)

    return ordered_entries


def sort_pokemon_entries(
    entries: Iterable[PokemonEntry],
) -> tuple[PokemonEntry, ...]:
    """Return entries in deterministic export order."""
    return tuple(
        sorted(
            entries,
            key=_entry_sort_key,
        )
    )


def validate_pokemon_entries(
    entries: tuple[PokemonEntry, ...],
) -> None:
    """Validate integrity rules for final export entries."""
    if not entries:
        raise ValidationError("Pokémon entry collection cannot be empty.")

    _validate_unique_home_ids(entries)
    _validate_unique_names(entries)
    _validate_species_consistency(entries)
    _validate_gender_representation(entries)
    _validate_deterministic_order(entries)


def _entry_sort_key(
    entry: PokemonEntry,
) -> tuple[int, int, int, str, int, str]:
    """Return the deterministic sort key for an export entry."""
    form_slug = _extract_form_slug(entry.home_id)
    special_order = _SPECIAL_FORM_ORDER.get(entry.national_dex)

    if special_order is None:
        group = 0 if form_slug == "normal" else 1
        rank = 0
    else:
        group = 0
        rank = special_order.get(form_slug, len(special_order))

    return (
        entry.national_dex,
        group,
        rank,
        form_slug,
        GENDER_SORT_ORDER[entry.gender],
        entry.home_id,
    )


def _validate_unique_home_ids(
    entries: tuple[PokemonEntry, ...],
) -> None:
    counts: dict[str, int] = {}

    for entry in entries:
        counts[entry.home_id] = counts.get(entry.home_id, 0) + 1

    duplicates = sorted(home_id for home_id, count in counts.items() if count > 1)

    if duplicates:
        raise ValidationError(
            "Duplicate Pokémon entry HOME IDs found: " f"{', '.join(duplicates)}"
        )


def _validate_unique_names(
    entries: tuple[PokemonEntry, ...],
) -> None:
    names: dict[str, list[str]] = {}

    for entry in entries:
        normalized_name = entry.name.casefold()
        names.setdefault(
            normalized_name,
            [],
        ).append(entry.home_id)

    duplicates = {
        name: home_ids for name, home_ids in names.items() if len(home_ids) > 1
    }

    if duplicates:
        details = "; ".join(
            f"{name}: {', '.join(home_ids)}"
            for name, home_ids in sorted(duplicates.items())
        )

        raise ValidationError("Duplicate Pokémon entry names found: " f"{details}")


def _validate_species_consistency(
    entries: tuple[PokemonEntry, ...],
) -> None:
    pokemon_by_dex: dict[int, set[str]] = {}

    for entry in entries:
        pokemon_by_dex.setdefault(
            entry.national_dex,
            set(),
        ).add(entry.pokemon)

    inconsistent = {
        national_dex: names
        for national_dex, names in pokemon_by_dex.items()
        if len(names) > 1
    }

    if inconsistent:
        details = "; ".join(
            f"{national_dex}: {', '.join(sorted(names))}"
            for national_dex, names in sorted(inconsistent.items())
        )

        raise ValidationError(
            "Entries with the same National Dex must share "
            f"the same Pokémon name: {details}"
        )


def _validate_gender_representation(
    entries: tuple[PokemonEntry, ...],
) -> None:
    genders_by_variant: dict[
        tuple[int, str],
        set[Gender],
    ] = {}

    for entry in entries:
        form_slug = _extract_form_slug(entry.home_id)

        key = (
            entry.national_dex,
            form_slug,
        )

        genders_by_variant.setdefault(
            key,
            set(),
        ).add(entry.gender)

    invalid: dict[
        tuple[int, str],
        set[Gender],
    ] = {}

    for key, genders in genders_by_variant.items():
        is_ungendered = genders == {Gender.NONE}
        is_gender_pair = genders == {
            Gender.MALE,
            Gender.FEMALE,
        }

        if not is_ungendered and not is_gender_pair:
            invalid[key] = genders

    if invalid:
        details = "; ".join(
            (
                f"{national_dex}:{form_slug}="
                f"{','.join(sorted(gender.value for gender in genders))}"
            )
            for (
                national_dex,
                form_slug,
            ), genders in sorted(invalid.items())
        )

        raise ValidationError(
            "Each entry form must be represented by either "
            "one ungendered row or one male/female pair: "
            f"{details}"
        )


def _validate_deterministic_order(
    entries: tuple[PokemonEntry, ...],
) -> None:
    expected = sort_pokemon_entries(entries)

    if entries != expected:
        raise ValidationError("Pokémon entries are not in deterministic order.")


def _extract_form_slug(
    home_id: str,
) -> str:
    """Extract the normalized form dimension from a HOME ID."""
    parts = home_id.split("_")

    if len(parts) < 3:
        raise ValidationError(f"Invalid Pokémon entry HOME ID: {home_id}")

    return "_".join(parts[1:-1]).casefold()
