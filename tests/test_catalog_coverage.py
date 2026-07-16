import json

import pytest
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
        national_dex_ranges=(),
        home_ids=frozenset(),
        excluded_home_ids=frozenset(),
    )
    games = {game: empty_rule for game in GAME_COLUMNS}
    games[GameColumn.XY] = GameRule(
        national_dex=frozenset({1}),
        national_dex_ranges=(),
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
        national_dex_ranges=(),
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
            national_dex_ranges=(),
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
            national_dex_ranges=(),
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


def test_game_coverage_counts_dex_range_as_verified_true() -> None:
    entries = (
        build_entry(
            national_dex=1,
            name="Bulbasaur",
            home_id="00001_NORMAL_NONE",
        ),
        build_entry(
            national_dex=151,
            name="Mew",
            home_id="00151_NORMAL_NONE",
        ),
    )

    empty_rule = GameRule(
        national_dex=frozenset(),
        national_dex_ranges=(),
        home_ids=frozenset(),
        excluded_home_ids=frozenset(),
    )
    games = {game: empty_rule for game in GAME_COLUMNS}
    games[GameColumn.LGPE] = GameRule(
        national_dex=frozenset(),
        national_dex_ranges=((1, 150),),
        home_ids=frozenset(),
        excluded_home_ids=frozenset(),
    )

    report = build_catalog_coverage_report(
        entries,
        GameAvailabilityRules(complete=False, games=games),
        ShinyAvailabilityRules(
            complete=False,
            national_dex=frozenset(),
            national_dex_ranges=(),
            home_ids=frozenset(),
            excluded_home_ids=frozenset(),
        ),
    )

    lgpe = report.games[GameColumn.LGPE]
    assert lgpe.verified_true == 1
    assert lgpe.unknown == 1


def test_complete_game_treats_unmatched_entries_as_verified_false() -> None:
    entries = (
        build_entry(
            national_dex=1,
            name="Bulbasaur",
            home_id="00001_NORMAL_NONE",
        ),
        build_entry(
            national_dex=151,
            name="Mew",
            home_id="00151_NORMAL_NONE",
        ),
    )

    empty_rule = GameRule(
        national_dex=frozenset(),
        national_dex_ranges=(),
        home_ids=frozenset(),
        excluded_home_ids=frozenset(),
    )
    games = {game: empty_rule for game in GAME_COLUMNS}
    games[GameColumn.LGPE] = GameRule(
        national_dex=frozenset(),
        national_dex_ranges=((1, 150),),
        home_ids=frozenset(),
        excluded_home_ids=frozenset(),
        complete=True,
    )

    report = build_catalog_coverage_report(
        entries,
        GameAvailabilityRules(complete=False, games=games),
        ShinyAvailabilityRules(
            complete=False,
            national_dex=frozenset(),
            national_dex_ranges=(),
            home_ids=frozenset(),
            excluded_home_ids=frozenset(),
        ),
    )

    lgpe = report.games[GameColumn.LGPE]
    assert lgpe.verified_true == 1
    assert lgpe.verified_false == 1
    assert lgpe.unknown == 0
    assert lgpe.percent == 100.0


def test_xy_complete_catalog_reports_no_unknown_rows() -> None:
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "game_availability.yaml"
    )
    game_rules = GameAvailabilityRules.from_yaml(catalog_path)
    entries = (
        build_entry(
            national_dex=25,
            name="Pikachu",
            home_id="00025_NORMAL_NONE",
        ),
        build_entry(
            national_dex=26,
            name="Alolan Raichu",
            home_id="00026_ALOLA_NONE",
        ),
        build_entry(
            national_dex=721,
            name="Volcanion",
            home_id="00721_NORMAL_NONE",
        ),
    )

    report = build_catalog_coverage_report(
        entries,
        game_rules,
        ShinyAvailabilityRules(
            complete=False,
            national_dex=frozenset(),
            national_dex_ranges=(),
            home_ids=frozenset(),
            excluded_home_ids=frozenset(),
        ),
    )

    xy = report.games[GameColumn.XY]
    assert xy.verified_true == 1
    assert xy.verified_false == 2
    assert xy.unknown == 0
    assert xy.percent == 100.0


def test_oras_regional_tranche_keeps_unmatched_entries_unknown() -> None:
    """ORAS stays incomplete until post-National-Dex encounters are audited."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "game_availability.yaml"
    )
    game_rules = GameAvailabilityRules.from_yaml(catalog_path)
    entries = (
        build_entry(
            national_dex=252,
            name="Treecko",
            home_id="00252_NORMAL_NONE",
        ),
        build_entry(
            national_dex=570,
            name="Zorua",
            home_id="00570_NORMAL_NONE",
        ),
        build_entry(
            national_dex=488,
            name="Cresselia",
            home_id="00488_NORMAL_NONE",
        ),
        build_entry(
            national_dex=385,
            name="Jirachi",
            home_id="00385_NORMAL_NONE",
        ),
        build_entry(
            national_dex=1,
            name="Bulbasaur",
            home_id="00001_NORMAL_NONE",
        ),
    )

    report = build_catalog_coverage_report(
        entries,
        game_rules,
        ShinyAvailabilityRules(
            complete=False,
            national_dex=frozenset(),
            national_dex_ranges=(),
            home_ids=frozenset(),
            excluded_home_ids=frozenset(),
        ),
    )

    oras = report.games[GameColumn.ORAS]
    assert oras.verified_true == 3
    assert oras.verified_false == 0
    assert oras.unknown == 2
    assert oras.percent == 60.0


def test_sm_qr_methods_are_classified_in_coverage() -> None:
    """Magearna and Island Scan are verified QR-based methods."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "game_availability.yaml"
    )
    game_rules = GameAvailabilityRules.from_yaml(catalog_path)
    entries = (
        build_entry(national_dex=722, name="Rowlet", home_id="00722_NORMAL_NONE"),
        build_entry(national_dex=801, name="Magearna", home_id="00801_NORMAL_NONE"),
        build_entry(national_dex=802, name="Marshadow", home_id="00802_NORMAL_NONE"),
        build_entry(national_dex=1, name="Bulbasaur", home_id="00001_NORMAL_NONE"),
    )

    report = build_catalog_coverage_report(
        entries,
        game_rules,
        ShinyAvailabilityRules(
            complete=False,
            national_dex=frozenset(),
            national_dex_ranges=(),
            home_ids=frozenset(),
            excluded_home_ids=frozenset(),
        ),
    )

    sm = report.games[GameColumn.SM]
    assert sm.verified_true == 2
    assert sm.verified_false == 1
    assert sm.unknown == 1
    assert sm.percent == 75.0


def test_usum_qr_and_ultra_warp_methods_are_classified_in_coverage() -> None:
    """QR and Ultra Warp Ride entries are verified rather than unknown."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "game_availability.yaml"
    )
    game_rules = GameAvailabilityRules.from_yaml(catalog_path)
    entries = (
        build_entry(national_dex=803, name="Poipole", home_id="00803_NORMAL_NONE"),
        build_entry(national_dex=801, name="Magearna", home_id="00801_NORMAL_NONE"),
        build_entry(national_dex=802, name="Marshadow", home_id="00802_NORMAL_NONE"),
        build_entry(national_dex=807, name="Zeraora", home_id="00807_NORMAL_NONE"),
        build_entry(national_dex=1, name="Bulbasaur", home_id="00001_NORMAL_NONE"),
    )

    report = build_catalog_coverage_report(
        entries,
        game_rules,
        ShinyAvailabilityRules(
            complete=False,
            national_dex=frozenset(),
            national_dex_ranges=(),
            home_ids=frozenset(),
            excluded_home_ids=frozenset(),
        ),
    )

    usum = report.games[GameColumn.USUM]
    assert usum.verified_true == 3
    assert usum.verified_false == 2
    assert usum.unknown == 0
    assert usum.percent == 100.0


def test_swsh_regional_tranche_classifies_events_and_later_forms() -> None:
    """Regional-Dex rows are verified while non-Dex transferable rows stay unknown."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "game_availability.yaml"
    )
    game_rules = GameAvailabilityRules.from_yaml(catalog_path)
    entries = (
        build_entry(
            national_dex=810,
            name="Grookey",
            home_id="00810_NORMAL_NONE",
        ),
        build_entry(
            national_dex=893,
            name="Zarude",
            home_id="00893_NORMAL_NONE",
        ),
        build_entry(
            national_dex=58,
            name="Hisuian Growlithe",
            home_id="00058_HISUI_NONE",
        ),
        build_entry(
            national_dex=151,
            name="Mew",
            home_id="00151_NORMAL_NONE",
        ),
        build_entry(
            national_dex=150,
            name="Mewtwo",
            home_id="00150_NORMAL_NONE",
        ),
    )

    report = build_catalog_coverage_report(
        entries,
        game_rules,
        ShinyAvailabilityRules(
            complete=False,
            national_dex=frozenset(),
            national_dex_ranges=(),
            home_ids=frozenset(),
            excluded_home_ids=frozenset(),
        ),
    )

    swsh = report.games[GameColumn.SWSH]
    assert swsh.verified_true == 2
    assert swsh.verified_false == 2
    assert swsh.unknown == 1
    assert swsh.percent == 80.0


def test_bdsp_complete_catalog_classifies_every_sample_row() -> None:
    """A completed BDSP audit treats unmatched later species as verified false."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "game_availability.yaml"
    )
    game_rules = GameAvailabilityRules.from_yaml(catalog_path)
    entries = (
        build_entry(
            national_dex=1,
            name="Bulbasaur",
            home_id="00001_NORMAL_NONE",
        ),
        build_entry(
            national_dex=26,
            name="Alolan Raichu",
            home_id="00026_ALOLA_NONE",
        ),
        build_entry(
            national_dex=386,
            name="Attack Forme Deoxys",
            home_id="00386_ATTACK_NONE",
        ),
        build_entry(
            national_dex=906,
            name="Sprigatito",
            home_id="00906_NORMAL_NONE",
        ),
    )

    report = build_catalog_coverage_report(
        entries,
        game_rules,
        ShinyAvailabilityRules(
            complete=False,
            national_dex=frozenset(),
            national_dex_ranges=(),
            home_ids=frozenset(),
            excluded_home_ids=frozenset(),
        ),
    )

    bdsp = report.games[GameColumn.BDSP]
    assert bdsp.verified_true == 1
    assert bdsp.verified_false == 3
    assert bdsp.unknown == 0
    assert bdsp.percent == 100.0


def test_sv_complete_catalog_classifies_every_sample_row() -> None:
    """A completed SV audit treats event-only and unsupported rows as false."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "game_availability.yaml"
    )
    game_rules = GameAvailabilityRules.from_yaml(catalog_path)
    entries = (
        build_entry(national_dex=906, name="Sprigatito", home_id="00906_NORMAL_NONE"),
        build_entry(national_dex=1017, name="Ogerpon", home_id="01017_NORMAL_NONE"),
        build_entry(
            national_dex=1009, name="Walking Wake", home_id="01009_NORMAL_NONE"
        ),
        build_entry(national_dex=1025, name="Pecharunt", home_id="01025_NORMAL_NONE"),
    )

    report = build_catalog_coverage_report(
        entries,
        game_rules,
        ShinyAvailabilityRules(
            complete=False,
            national_dex=frozenset(),
            national_dex_ranges=(),
            home_ids=frozenset(),
            excluded_home_ids=frozenset(),
        ),
    )

    sv = report.games[GameColumn.SV]
    assert sv.verified_true == 3
    assert sv.verified_false == 1
    assert sv.unknown == 0
    assert sv.percent == 100.0


def test_za_complete_catalog_classifies_home_and_mystery_gift_rows() -> None:
    """Completed Z-A rules classify HOME transfers and permanent gifts."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "game_availability.yaml"
    )
    game_rules = GameAvailabilityRules.from_yaml(catalog_path)
    entries = (
        build_entry(national_dex=152, name="Chikorita", home_id="00152_NORMAL_NONE"),
        build_entry(
            national_dex=670,
            name="Eternal Flower Floette",
            home_id="00670_ETERNAL_NONE",
        ),
        build_entry(national_dex=719, name="Diancie", home_id="00719_NORMAL_NONE"),
        build_entry(
            national_dex=705,
            name="Hisuian Sliggoo",
            home_id="00705_HISUI_NONE",
        ),
        build_entry(national_dex=906, name="Sprigatito", home_id="00906_NORMAL_NONE"),
    )

    report = build_catalog_coverage_report(
        entries,
        game_rules,
        ShinyAvailabilityRules(
            complete=False,
            national_dex=frozenset(),
            national_dex_ranges=(),
            home_ids=frozenset(),
            excluded_home_ids=frozenset(),
        ),
    )

    za = report.games[GameColumn.ZA]
    assert za.verified_true == 4
    assert za.verified_false == 1
    assert za.unknown == 0
    assert za.percent == 100.0


def test_shiny_coverage_counts_dex_range_as_verified_true() -> None:
    entries = (
        build_entry(
            national_dex=26,
            name="Raichu",
            home_id="00026_ALOLA_NONE",
        ),
        build_entry(
            national_dex=151,
            name="Mew",
            home_id="00151_NORMAL_NONE",
        ),
    )

    report = build_catalog_coverage_report(
        entries,
        build_game_rules(),
        ShinyAvailabilityRules(
            complete=False,
            national_dex=frozenset(),
            national_dex_ranges=((1, 150),),
            home_ids=frozenset(),
            excluded_home_ids=frozenset({"00151_NORMAL_NONE"}),
        ),
    )

    assert report.shiny.verified_true == 1
    assert report.shiny.verified_false == 1
    assert report.shiny.unknown == 0
    assert report.shiny.percent == 100.0


def test_johto_shiny_catalog_classifies_sample_rows_as_verified_true() -> None:
    """The Johto range should classify normal, regional, and Celebi rows."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    shiny_rules = ShinyAvailabilityRules.from_yaml(catalog_path)
    entries = (
        build_entry(
            national_dex=157,
            name="Typhlosion",
            home_id="00157_NORMAL_NONE",
        ),
        build_entry(
            national_dex=157,
            name="Hisuian Typhlosion",
            home_id="00157_HISUI_NONE",
        ),
        build_entry(
            national_dex=251,
            name="Celebi",
            home_id="00251_NORMAL_NONE",
        ),
    )

    report = build_catalog_coverage_report(
        entries,
        build_game_rules(),
        shiny_rules,
    )

    assert report.shiny.verified_true == 3
    assert report.shiny.verified_false == 0
    assert report.shiny.unknown == 0
    assert report.shiny.percent == 100.0


def test_hoenn_shiny_catalog_classifies_sample_rows_as_verified_true() -> None:
    """The Hoenn range classifies standard, regional, and Deoxys rows."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    shiny_rules = ShinyAvailabilityRules.from_yaml(catalog_path)
    entries = (
        build_entry(national_dex=252, name="Treecko", home_id="00252_NORMAL_NONE"),
        build_entry(
            national_dex=263,
            name="Galarian Zigzagoon",
            home_id="00263_GALAR_NONE",
        ),
        build_entry(national_dex=385, name="Jirachi", home_id="00385_NORMAL_NONE"),
        build_entry(
            national_dex=386,
            name="Attack Forme Deoxys",
            home_id="00386_ATTACK_NONE",
        ),
    )

    report = build_catalog_coverage_report(
        entries,
        build_game_rules(),
        shiny_rules,
    )

    assert report.shiny.verified_true == 4
    assert report.shiny.verified_false == 0
    assert report.shiny.unknown == 0
    assert report.shiny.percent == 100.0
