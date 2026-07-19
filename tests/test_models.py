import pytest

from pokedex.constants import GAME_COLUMNS, Gender, GameColumn
from pokedex.models import (
    GameAvailability,
    PokemonEntry,
    PokemonSpecies,
    PokemonVariant,
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

    with pytest.raises(
        ValueError,
        match="Missing availability",
    ):
        GameAvailability(values=values)


def test_species_legendary_or_mythical_property() -> None:
    species = PokemonSpecies(
        national_dex=150,
        name="Mewtwo",
        generation=1,
        is_legendary=True,
    )

    assert species.is_legendary_or_mythical is True


def test_variant_generates_home_id() -> None:
    variant = PokemonVariant(
        national_dex=26,
        pokemon="Raichu",
        species_api_name="raichu",
        variety_api_name="raichu-alola",
        form_slug="alola",
        form_name="Alolan",
        display_name="Alolan Raichu",
        generation=7,
        resource_url=("https://pokeapi.co/api/v2/pokemon/10100/"),
        is_default=False,
    )

    assert variant.home_id == "00026_ALOLA_NONE"


def test_gendered_variant_generates_gendered_home_id() -> None:
    variant = PokemonVariant(
        national_dex=25,
        pokemon="Pikachu",
        species_api_name="pikachu",
        variety_api_name="pikachu",
        form_slug="normal",
        form_name="Female",
        display_name="Female Pikachu",
        generation=1,
        resource_url=("https://pokeapi.co/api/v2/pokemon/25/"),
        is_default=True,
        gender=Gender.FEMALE,
    )

    assert variant.home_id == "00025_NORMAL_FEMALE"


def test_variant_logical_key_contains_identity_dimensions() -> None:
    variant = PokemonVariant(
        national_dex=215,
        pokemon="Sneasel",
        species_api_name="sneasel",
        variety_api_name="sneasel-hisui",
        form_slug="hisui",
        form_name="Hisuian",
        display_name="Male Hisuian Sneasel",
        generation=8,
        resource_url=("https://pokeapi.co/api/v2/pokemon/10235/"),
        is_default=False,
        gender=Gender.MALE,
    )

    assert variant.logical_key == (
        215,
        "hisui",
        Gender.MALE,
    )


def test_entry_exports_only_final_columns() -> None:
    entry = PokemonEntry(
        national_dex=25,
        pokemon="Pikachu",
        form="Female",
        name="Female Pikachu",
        generation=1,
        home_id="00025_NORMAL_FEMALE",
        gender=Gender.FEMALE,
        availability=GameAvailability(),
        legendary_mythical=False,
        obtainable_shiny=True,
    )

    row = entry.to_dict()

    assert row["Nat Dex"] == 25
    assert row["Pokemon"] == "Pikachu"
    assert row["Forma"] == "Female"
    assert row["Nombre"] == "Female Pikachu"
    assert row["Obtenido"] == "☐"
    assert row["Prioridad"] is None
    assert row["Gen"] == 1
    assert row["ID HOME"] == "00025_NORMAL_FEMALE"
    assert row["XY"] is False
    assert row["Obtenible"] is True
    assert row["Posibles"] is None
    assert "Gender" not in row
    assert len(row) == 21


def test_models_reject_boolean_as_integer() -> None:
    with pytest.raises(
        TypeError,
        match="must be an integer",
    ):
        PokemonSpecies(
            national_dex=True,
            name="Invalid",
            generation=1,
        )


def test_variant_rejects_invalid_gender_type() -> None:
    with pytest.raises(
        TypeError,
        match="gender must be a Gender value",
    ):
        PokemonVariant(
            national_dex=25,
            pokemon="Pikachu",
            species_api_name="pikachu",
            variety_api_name="pikachu",
            form_slug="normal",
            form_name="Normal",
            display_name="Pikachu",
            generation=1,
            resource_url=("https://pokeapi.co/api/v2/pokemon/25/"),
            is_default=True,
            gender="Female",  # type: ignore[arg-type]
        )
