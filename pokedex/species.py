from __future__ import annotations

from collections.abc import Iterable

from pokedex.exceptions import ValidationError
from pokedex.models import PokemonSpecies
from pokedex.pokeapi import SpeciesDetails


def build_species(
    details: Iterable[SpeciesDetails],
) -> tuple[PokemonSpecies, ...]:
    """Convert normalized PokéAPI details into domain models."""
    species = tuple(
        PokemonSpecies(
            national_dex=item.national_dex,
            name=item.english_name,
            generation=item.generation,
            is_legendary=item.is_legendary,
            is_mythical=item.is_mythical,
        )
        for item in details
    )

    ordered_species = tuple(
        sorted(
            species,
            key=lambda item: item.national_dex,
        )
    )

    validate_species(ordered_species)

    return ordered_species


def validate_species(
    species: tuple[PokemonSpecies, ...],
) -> None:
    """Validate integrity rules for the base species collection."""
    if not species:
        raise ValidationError("Species collection cannot be empty.")

    _validate_unique_dex_numbers(species)
    _validate_unique_names(species)
    _validate_dex_order(species)
    _validate_contiguous_dex_numbers(species)


def _validate_unique_dex_numbers(
    species: tuple[PokemonSpecies, ...],
) -> None:
    seen: set[int] = set()
    duplicates: set[int] = set()

    for item in species:
        if item.national_dex in seen:
            duplicates.add(item.national_dex)

        seen.add(item.national_dex)

    if duplicates:
        values = ", ".join(str(value) for value in sorted(duplicates))
        raise ValidationError(f"Duplicate National Pokédex numbers found: {values}")


def _validate_unique_names(
    species: tuple[PokemonSpecies, ...],
) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()

    for item in species:
        normalized_name = item.name.casefold()

        if normalized_name in seen:
            duplicates.add(item.name)

        seen.add(normalized_name)

    if duplicates:
        values = ", ".join(sorted(duplicates))
        raise ValidationError(f"Duplicate Pokémon species names found: {values}")


def _validate_dex_order(
    species: tuple[PokemonSpecies, ...],
) -> None:
    dex_numbers = tuple(item.national_dex for item in species)

    if dex_numbers != tuple(sorted(dex_numbers)):
        raise ValidationError(
            "Species collection is not ordered by National Pokédex number."
        )


def _validate_contiguous_dex_numbers(
    species: tuple[PokemonSpecies, ...],
) -> None:
    first_dex = species[0].national_dex
    last_dex = species[-1].national_dex
    expected = set(range(first_dex, last_dex + 1))
    actual = {item.national_dex for item in species}

    missing = sorted(expected - actual)

    if missing:
        values = ", ".join(str(value) for value in missing)
        raise ValidationError(f"Missing National Pokédex numbers: {values}")
