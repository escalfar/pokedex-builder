from pathlib import Path

import pytest

from pokedex.constants import Gender, GameColumn
from pokedex.exceptions import ConfigurationError
from pokedex.game_availability import (
    GameAvailabilityRules,
    GameRule,
    apply_game_availability,
)
from pokedex.models import GameAvailability, PokemonEntry


def build_entry(
    *,
    national_dex: int = 25,
    home_id: str = "00025_NORMAL_NONE",
    gender: Gender = Gender.NONE,
) -> PokemonEntry:
    return PokemonEntry(
        national_dex=national_dex,
        pokemon="Pikachu",
        form="Normal",
        name="Pikachu",
        generation=1,
        home_id=home_id,
        gender=gender,
        availability=GameAvailability(),
        legendary_mythical=False,
        obtainable_shiny=False,
    )


def empty_rules() -> dict[GameColumn, GameRule]:
    return {
        game: GameRule(
            national_dex=frozenset(),
            home_ids=frozenset(),
            excluded_home_ids=frozenset(),
        )
        for game in GameColumn
    }


def write_rules(path: Path) -> None:
    path.write_text(
        """
version: "1.0"
complete: false
games:
  xy:
    national_dex: [25]
    home_ids: []
    excluded_home_ids: ["00025_ALOLA_NONE"]
  oras: {national_dex: [], home_ids: [], excluded_home_ids: []}
  sm: {national_dex: [], home_ids: ["00025_ALOLA_NONE"], excluded_home_ids: []}
  usum: {national_dex: [], home_ids: [], excluded_home_ids: []}
  lgpe: {national_dex: [], home_ids: [], excluded_home_ids: []}
  swsh: {national_dex: [], home_ids: [], excluded_home_ids: []}
  pla: {national_dex: [], home_ids: [], excluded_home_ids: []}
  bdsp: {national_dex: [], home_ids: [], excluded_home_ids: []}
  sv: {national_dex: [], home_ids: [], excluded_home_ids: []}
  za: {national_dex: [], home_ids: [], excluded_home_ids: []}
""".strip(),
        encoding="utf-8",
    )


def test_load_game_availability_rules(tmp_path: Path) -> None:
    path = tmp_path / "game_availability.yaml"
    write_rules(path)

    rules = GameAvailabilityRules.from_yaml(path)

    assert rules.complete is False
    assert 25 in rules.games[GameColumn.XY].national_dex
    assert "00025_ALOLA_NONE" in rules.games[GameColumn.SM].home_ids


def test_species_rule_applies_to_every_variant() -> None:
    games = empty_rules()
    games[GameColumn.XY] = GameRule(
        national_dex=frozenset({25}),
        home_ids=frozenset(),
        excluded_home_ids=frozenset(),
    )
    rules = GameAvailabilityRules(complete=False, games=games)

    normal, alolan = apply_game_availability(
        (
            build_entry(),
            build_entry(home_id="00025_ALOLA_NONE"),
        ),
        rules,
    )

    assert normal.availability.is_available_in(GameColumn.XY) is True
    assert alolan.availability.is_available_in(GameColumn.XY) is True


def test_home_id_rule_can_include_one_specific_variant() -> None:
    games = empty_rules()
    games[GameColumn.SM] = GameRule(
        national_dex=frozenset(),
        home_ids=frozenset({"00025_ALOLA_NONE"}),
        excluded_home_ids=frozenset(),
    )
    rules = GameAvailabilityRules(complete=False, games=games)

    normal, alolan = apply_game_availability(
        (
            build_entry(),
            build_entry(home_id="00025_ALOLA_NONE"),
        ),
        rules,
    )

    assert normal.availability.is_available_in(GameColumn.SM) is False
    assert alolan.availability.is_available_in(GameColumn.SM) is True


def test_form_exclusion_overrides_species_inclusion() -> None:
    games = empty_rules()
    games[GameColumn.XY] = GameRule(
        national_dex=frozenset({25}),
        home_ids=frozenset(),
        excluded_home_ids=frozenset({"00025_ALOLA_NONE"}),
    )
    rules = GameAvailabilityRules(complete=False, games=games)

    normal, alolan = apply_game_availability(
        (
            build_entry(),
            build_entry(home_id="00025_ALOLA_NONE"),
        ),
        rules,
    )

    assert normal.availability.is_available_in(GameColumn.XY) is True
    assert alolan.availability.is_available_in(GameColumn.XY) is False


def test_apply_availability_preserves_entry_order_and_other_fields() -> None:
    entries = (
        build_entry(home_id="00025_NORMAL_FEMALE", gender=Gender.FEMALE),
        build_entry(home_id="00025_NORMAL_MALE", gender=Gender.MALE),
    )
    result = apply_game_availability(
        entries,
        GameAvailabilityRules(complete=False, games=empty_rules()),
    )

    assert [entry.home_id for entry in result] == [
        "00025_NORMAL_FEMALE",
        "00025_NORMAL_MALE",
    ]
    assert result[0].gender == Gender.FEMALE
    assert result[0].obtainable_shiny is False


def test_load_rules_requires_every_supported_game(tmp_path: Path) -> None:
    path = tmp_path / "incomplete.yaml"
    path.write_text(
        "complete: false\ngames:\n  xy: "
        "{national_dex: [], home_ids: [], excluded_home_ids: []}\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ConfigurationError,
        match="oras.*must be an object",
    ):
        GameAvailabilityRules.from_yaml(path)


def test_load_rules_rejects_invalid_dex_values(tmp_path: Path) -> None:
    path = tmp_path / "invalid.yaml"
    write_rules(path)
    content = path.read_text(encoding="utf-8").replace(
        "national_dex: [25]",
        "national_dex: [true]",
    )
    path.write_text(content, encoding="utf-8")

    with pytest.raises(
        ConfigurationError,
        match="positive integers",
    ):
        GameAvailabilityRules.from_yaml(path)
