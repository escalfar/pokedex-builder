import json
from pathlib import Path

from pokedex.catalog_coverage import (
    build_catalog_coverage_report,
    export_catalog_coverage_json,
)
from pokedex.constants import GAME_COLUMNS, Gender, GameColumn
from pokedex.game_availability import GameAvailabilityRules, GameRule
from pokedex.models import GameAvailability, PokemonEntry
from pokedex.shiny_availability import ShinyAvailabilityRules


def build_entry(
    *,
    national_dex: int,
    name: str,
    home_id: str,
) -> PokemonEntry:
    return PokemonEntry(
        national_dex=national_dex,
        pokemon=name,
        form="Normal",
        name=name,
        generation=1,
        home_id=home_id,
        gender=Gender.NONE,
        availability=GameAvailability(),
        legendary_mythical=False,
        obtainable_shiny=False,
    )


def build_game_rules() -> GameAvailabilityRules:
    empty_rule = GameRule(
        national_dex=frozenset(),
        home_ids=frozenset(),
        excluded_home_ids=frozenset(),
    )
    games = {game: empty_rule for game in GAME_COLUMNS}
    games[GameColumn.XY] = GameRule(
        national_dex=frozenset({1}),
        home_ids=frozenset({"00002_NORMAL_NONE"}),
        excluded_home_ids=frozenset({"00003_NORMAL_NONE"}),
    )
    return GameAvailabilityRules(complete=False, games=games)


def test_build_coverage_distinguishes_true_false_and_unknown() -> None:
    entries = (
        build_entry(
            national_dex=1,
            name="Bulbasaur",
            home_id="00001_NORMAL_NONE",
        ),
        build_entry(
            national_dex=2,
            name="Ivysaur",
            home_id="00002_NORMAL_NONE",
        ),
        build_entry(
            national_dex=3,
            name="Venusaur",
            home_id="00003_NORMAL_NONE",
        ),
        build_entry(
            national_dex=4,
            name="Charmander",
            home_id="00004_NORMAL_NONE",
        ),
    )
    shiny_rules = ShinyAvailabilityRules(
        complete=False,
        national_dex=frozenset({1}),
        home_ids=frozenset({"00002_NORMAL_NONE"}),
        excluded_home_ids=frozenset({"00003_NORMAL_NONE"}),
    )

    report = build_catalog_coverage_report(
        entries,
        build_game_rules(),
        shiny_rules,
    )

    xy = report.games[GameColumn.XY]
    assert xy.total == 4
    assert xy.verified_true == 2
    assert xy.verified_false == 1
    assert xy.unknown == 1
    assert xy.percent == 75.0

    assert report.shiny.verified_true == 2
    assert report.shiny.verified_false == 1
    assert report.shiny.unknown == 1
    assert report.is_complete is False


def test_empty_rules_report_zero_percent_coverage() -> None:
    entries = (
        build_entry(
            national_dex=1,
            name="Bulbasaur",
            home_id="00001_NORMAL_NONE",
        ),
    )
    report = build_catalog_coverage_report(
        entries,
        build_game_rules(),
        ShinyAvailabilityRules(
            complete=False,
            national_dex=frozenset(),
            home_ids=frozenset(),
            excluded_home_ids=frozenset(),
        ),
    )

    assert report.games[GameColumn.SM].percent == 0.0
    assert report.shiny.percent == 0.0


def test_export_coverage_json(tmp_path: Path) -> None:
    entries = (
        build_entry(
            national_dex=1,
            name="Bulbasaur",
            home_id="00001_NORMAL_NONE",
        ),
    )
    report = build_catalog_coverage_report(
        entries,
        build_game_rules(),
        ShinyAvailabilityRules(
            complete=False,
            national_dex=frozenset({1}),
            home_ids=frozenset(),
            excluded_home_ids=frozenset(),
        ),
    )
    output_path = tmp_path / "Catalog_Coverage.json"

    result = export_catalog_coverage_json(report, output_path)
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == output_path
    assert payload["complete"] is False
    assert payload["games"]["X/Y"]["verified"] == 1
    assert payload["shiny"]["percent"] == 100.0
