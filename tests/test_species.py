import pytest

from pokedex.exceptions import ValidationError
from pokedex.models import PokemonSpecies
from pokedex.pokeapi import SpeciesDetails, SpeciesVariety
from pokedex.species import build_species, validate_species


def build_details(
    *,
    national_dex: int,
    english_name: str,
    generation: int = 1,
    is_legendary: bool = False,
    is_mythical: bool = False,
) -> SpeciesDetails:
    return SpeciesDetails(
        national_dex=national_dex,
        api_name=english_name.casefold(),
        english_name=english_name,
        generation=generation,
        is_legendary=is_legendary,
        is_mythical=is_mythical,
        resource_url=("https://pokeapi.co/api/v2/" f"pokemon-species/{national_dex}/"),
        varieties=(
            SpeciesVariety(
                api_name=english_name.casefold(),
                resource_url=("https://pokeapi.co/api/v2/" f"pokemon/{national_dex}/"),
                is_default=True,
            ),
        ),
    )


def test_build_species_converts_and_orders_details() -> None:
    details = (
        build_details(
            national_dex=3,
            english_name="Venusaur",
        ),
        build_details(
            national_dex=1,
            english_name="Bulbasaur",
        ),
        build_details(
            national_dex=2,
            english_name="Ivysaur",
        ),
    )

    species = build_species(details)

    assert [item.national_dex for item in species] == [1, 2, 3]

    assert [item.name for item in species] == [
        "Bulbasaur",
        "Ivysaur",
        "Venusaur",
    ]


def test_build_species_preserves_legendary_and_mythical_flags() -> None:
    details = (
        build_details(
            national_dex=150,
            english_name="Mewtwo",
            is_legendary=True,
        ),
        build_details(
            national_dex=151,
            english_name="Mew",
            is_mythical=True,
        ),
    )

    species = build_species(details)

    assert species[0].is_legendary is True
    assert species[0].is_mythical is False
    assert species[1].is_legendary is False
    assert species[1].is_mythical is True


def test_build_species_preserves_generation() -> None:
    details = (
        build_details(
            national_dex=26,
            english_name="Raichu",
            generation=1,
        ),
    )

    species = build_species(details)

    assert species[0].generation == 1


def test_validate_species_rejects_empty_collection() -> None:
    with pytest.raises(
        ValidationError,
        match="cannot be empty",
    ):
        validate_species(())


def test_validate_species_rejects_duplicate_dex_numbers() -> None:
    species = (
        PokemonSpecies(
            national_dex=1,
            name="Bulbasaur",
            generation=1,
        ),
        PokemonSpecies(
            national_dex=1,
            name="Ivysaur",
            generation=1,
        ),
    )

    with pytest.raises(
        ValidationError,
        match="Duplicate National Pokédex numbers",
    ):
        validate_species(species)


def test_validate_species_rejects_duplicate_names() -> None:
    species = (
        PokemonSpecies(
            national_dex=1,
            name="Bulbasaur",
            generation=1,
        ),
        PokemonSpecies(
            national_dex=2,
            name="BULBASAUR",
            generation=1,
        ),
    )

    with pytest.raises(
        ValidationError,
        match="Duplicate Pokémon species names",
    ):
        validate_species(species)


def test_validate_species_rejects_unordered_collection() -> None:
    species = (
        PokemonSpecies(
            national_dex=2,
            name="Ivysaur",
            generation=1,
        ),
        PokemonSpecies(
            national_dex=1,
            name="Bulbasaur",
            generation=1,
        ),
    )

    with pytest.raises(
        ValidationError,
        match="not ordered",
    ):
        validate_species(species)


def test_validate_species_rejects_missing_dex_number() -> None:
    species = (
        PokemonSpecies(
            national_dex=1,
            name="Bulbasaur",
            generation=1,
        ),
        PokemonSpecies(
            national_dex=3,
            name="Venusaur",
            generation=1,
        ),
    )

    with pytest.raises(
        ValidationError,
        match="Missing National Pokédex numbers: 2",
    ):
        validate_species(species)


def test_validate_species_accepts_valid_collection() -> None:
    species = (
        PokemonSpecies(
            national_dex=1,
            name="Bulbasaur",
            generation=1,
        ),
        PokemonSpecies(
            national_dex=2,
            name="Ivysaur",
            generation=1,
        ),
        PokemonSpecies(
            national_dex=3,
            name="Venusaur",
            generation=1,
        ),
    )

    validate_species(species)
