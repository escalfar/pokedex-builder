import pytest

from pokedex.constants import GAME_COLUMNS, GameColumn
from pokedex.models import (
    GameAvailability,
    PokemonEntry,
    PokemonForm,
    PokemonSpecies,
)


def test_game_availability_defaults_to_false() -> None:
    availability = GameAvailability()

    assert all(availability.is_available_in(game) is False for game in GAME_COLUMNS)


def test_game_availability_accepts_complete_mapping() -> None:
    values = {game: game == GameColumn.SV for game in GAME_COLUMNS}

    availability = GameAvailability(values=values)

    assert availability.is_available_in(GameColumn.SV) is True
    assert availability.is_available_in(GameColumn.XY) is False


def test_game_availability_rejects_missing_game() -> None:
    values = {game: False for game in GAME_COLUMNS}
    values.pop(GameColumn.ZA)

    with pytest.raises(ValueError, match="Missing availability"):
        GameAvailability(values=values)


def test_game_availability_rejects_non_boolean_value() -> None:
    values = {game: False for game in GAME_COLUMNS}
    values[GameColumn.XY] = 1  # type: ignore[assignment]

    with pytest.raises(TypeError, match="must be boolean"):
        GameAvailability(values=values)


def test_pokemon_species_legendary_property() -> None:
    species = PokemonSpecies(
        national_dex=150,
        name="Mewtwo",
        generation=1,
        is_legendary=True,
    )

    assert species.is_legendary_or_mythical is True


def test_pokemon_species_rejects_invalid_dex_number() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        PokemonSpecies(
            national_dex=0,
            name="MissingNo.",
            generation=1,
        )


def test_pokemon_form_uses_variant_generation() -> None:
    form = PokemonForm(
        national_dex=26,
        pokemon="Raichu",
        form="Alolan",
        name="Alolan Raichu",
        generation=7,
        home_id="00026_ALOLAN",
    )

    assert form.generation == 7


def test_pokemon_entry_exports_expected_columns() -> None:
    availability_values = {game: False for game in GAME_COLUMNS}
    availability_values[GameColumn.SM] = True
    availability_values[GameColumn.USUM] = True

    entry = PokemonEntry(
        national_dex=26,
        pokemon="Raichu",
        form="Alolan",
        name="Alolan Raichu",
        generation=7,
        home_id="00026_ALOLAN",
        availability=GameAvailability(values=availability_values),
        legendary_mythical=False,
        obtainable_shiny=True,
    )

    row = entry.to_dict()

    assert row["Nat Dex"] == 26
    assert row["Pokemon"] == "Raichu"
    assert row["Forma"] == "Alolan"
    assert row["Nombre"] == "Alolan Raichu"
    assert row["Gen"] == 7
    assert row["ID HOME"] == "00026_ALOLAN"
    assert row["Sun / Moon"] is True
    assert row["X/Y"] is False
    assert row["Legendario/Mítico"] is False
    assert row["Obtenible"] is True
    assert len(row) == 18
