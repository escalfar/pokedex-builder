import pytest

from pokedex.entries import (
    build_pokemon_entries,
    validate_pokemon_entries,
)
from pokedex.exceptions import ValidationError
from pokedex.models import (
    GameAvailability,
    PokemonEntry,
    PokemonForm,
    PokemonSpecies,
)


def test_build_entries_combines_forms_and_species() -> None:
    species = (
        PokemonSpecies(
            national_dex=150,
            name="Mewtwo",
            generation=1,
            is_legendary=True,
        ),
    )

    forms = (
        PokemonForm(
            national_dex=150,
            pokemon="Mewtwo",
            form="Normal",
            name="Mewtwo",
            generation=1,
            home_id="00150_NORMAL",
        ),
    )

    entries = build_pokemon_entries(forms, species)

    assert len(entries) == 1
    assert entries[0].legendary_mythical is True
    assert entries[0].obtainable_shiny is False
    assert all(value is False for value in entries[0].availability.values.values())


def test_build_entries_rejects_unknown_species() -> None:
    forms = (
        PokemonForm(
            national_dex=9999,
            pokemon="Unknown",
            form="Normal",
            name="Unknown",
            generation=1,
            home_id="09999_NORMAL",
        ),
    )

    with pytest.raises(
        ValidationError,
        match="no matching species",
    ):
        build_pokemon_entries(forms, ())


def test_validate_entries_rejects_empty_collection() -> None:
    with pytest.raises(
        ValidationError,
        match="cannot be empty",
    ):
        validate_pokemon_entries(())


def test_validate_entries_rejects_duplicate_home_ids() -> None:
    first = PokemonEntry(
        national_dex=1,
        pokemon="Bulbasaur",
        form="Normal",
        name="Bulbasaur",
        generation=1,
        home_id="00001_NORMAL",
        availability=GameAvailability(),
        legendary_mythical=False,
        obtainable_shiny=True,
    )

    second = PokemonEntry(
        national_dex=1,
        pokemon="Bulbasaur",
        form="Duplicate",
        name="Duplicate Bulbasaur",
        generation=1,
        home_id="00001_NORMAL",
        availability=GameAvailability(),
        legendary_mythical=False,
        obtainable_shiny=True,
    )

    with pytest.raises(
        ValidationError,
        match="Duplicate Pokémon entry HOME IDs",
    ):
        validate_pokemon_entries((first, second))
