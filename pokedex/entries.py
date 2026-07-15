from __future__ import annotations

from pokedex.exceptions import ValidationError
from pokedex.models import (
    GameAvailability,
    PokemonEntry,
    PokemonForm,
    PokemonSpecies,
)


def build_pokemon_entries(
    forms: tuple[PokemonForm, ...],
    species: tuple[PokemonSpecies, ...],
) -> tuple[PokemonEntry, ...]:
    """Build preliminary export entries from forms and species data."""
    species_by_dex = {item.national_dex: item for item in species}

    entries: list[PokemonEntry] = []

    for form in forms:
        base_species = species_by_dex.get(form.national_dex)

        if base_species is None:
            raise ValidationError(
                "Pokémon form has no matching species: "
                f"{form.national_dex} ({form.name})"
            )

        entries.append(
            PokemonEntry(
                national_dex=form.national_dex,
                pokemon=form.pokemon,
                form=form.form,
                name=form.name,
                generation=form.generation,
                home_id=form.home_id,
                availability=GameAvailability(),
                legendary_mythical=(base_species.is_legendary_or_mythical),
                obtainable_shiny=False,
            )
        )

    result = tuple(entries)

    validate_pokemon_entries(result)

    return result


def validate_pokemon_entries(
    entries: tuple[PokemonEntry, ...],
) -> None:
    """Validate preliminary export entries."""
    if not entries:
        raise ValidationError("Pokémon entry collection cannot be empty.")

    _validate_unique_home_ids(entries)
    _validate_unique_names(entries)
    _validate_order(entries)


def _validate_unique_home_ids(
    entries: tuple[PokemonEntry, ...],
) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()

    for entry in entries:
        if entry.home_id in seen:
            duplicates.add(entry.home_id)

        seen.add(entry.home_id)

    if duplicates:
        values = ", ".join(sorted(duplicates))
        raise ValidationError(f"Duplicate Pokémon entry HOME IDs found: {values}")


def _validate_unique_names(
    entries: tuple[PokemonEntry, ...],
) -> None:
    names: dict[str, list[str]] = {}

    for entry in entries:
        normalized_name = entry.name.casefold()
        names.setdefault(normalized_name, []).append(entry.home_id)

    duplicates = {
        name: home_ids for name, home_ids in names.items() if len(home_ids) > 1
    }

    if duplicates:
        details = "; ".join(
            f"{name}: {', '.join(home_ids)}"
            for name, home_ids in sorted(duplicates.items())
        )
        raise ValidationError(f"Duplicate Pokémon entry names found: {details}")


def _validate_order(
    entries: tuple[PokemonEntry, ...],
) -> None:
    expected = tuple(
        sorted(
            entries,
            key=lambda item: (
                item.national_dex,
                item.home_id != f"{item.national_dex:05d}_NORMAL",
                item.home_id,
            ),
        )
    )

    if entries != expected:
        raise ValidationError("Pokémon entries are not in deterministic order.")
