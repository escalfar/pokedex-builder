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
            national_dex_ranges=(),
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
    national_dex_ranges: []
    home_ids: []
    excluded_home_ids: ["00025_ALOLA_NONE"]
  oras: {national_dex: [], national_dex_ranges: [], home_ids: [], excluded_home_ids: []}
  sm: {national_dex: [], national_dex_ranges: [], home_ids: ["00025_ALOLA_NONE"], excluded_home_ids: []}
  usum: {national_dex: [], national_dex_ranges: [], home_ids: [], excluded_home_ids: []}
  lgpe: {national_dex: [], national_dex_ranges: [], home_ids: [], excluded_home_ids: []}
  swsh: {national_dex: [], national_dex_ranges: [], home_ids: [], excluded_home_ids: []}
  pla: {national_dex: [], national_dex_ranges: [], home_ids: [], excluded_home_ids: []}
  bdsp: {national_dex: [], national_dex_ranges: [], home_ids: [], excluded_home_ids: []}
  sv: {national_dex: [], national_dex_ranges: [], home_ids: [], excluded_home_ids: []}
  za: {national_dex: [], national_dex_ranges: [], home_ids: [], excluded_home_ids: []}
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
        national_dex_ranges=(),
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
        national_dex_ranges=(),
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
        national_dex_ranges=(),
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
        "{national_dex: [], national_dex_ranges: [], home_ids: [], excluded_home_ids: []}\n",
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


def test_dex_range_includes_both_endpoints() -> None:
    games = empty_rules()
    games[GameColumn.LGPE] = GameRule(
        national_dex=frozenset(),
        national_dex_ranges=((1, 150),),
        home_ids=frozenset(),
        excluded_home_ids=frozenset(),
    )
    rules = GameAvailabilityRules(complete=False, games=games)

    first, last, outside = apply_game_availability(
        (
            build_entry(national_dex=1, home_id="00001_NORMAL_NONE"),
            build_entry(national_dex=150, home_id="00150_NORMAL_NONE"),
            build_entry(national_dex=151, home_id="00151_NORMAL_NONE"),
        ),
        rules,
    )

    assert first.availability.is_available_in(GameColumn.LGPE) is True
    assert last.availability.is_available_in(GameColumn.LGPE) is True
    assert outside.availability.is_available_in(GameColumn.LGPE) is False


def test_form_exclusion_overrides_dex_range() -> None:
    games = empty_rules()
    games[GameColumn.LGPE] = GameRule(
        national_dex=frozenset(),
        national_dex_ranges=((1, 150),),
        home_ids=frozenset(),
        excluded_home_ids=frozenset({"00052_GALAR_NONE"}),
    )
    rules = GameAvailabilityRules(complete=False, games=games)

    kantonian, galarian = apply_game_availability(
        (
            build_entry(national_dex=52, home_id="00052_NORMAL_NONE"),
            build_entry(national_dex=52, home_id="00052_GALAR_NONE"),
        ),
        rules,
    )

    assert kantonian.availability.is_available_in(GameColumn.LGPE) is True
    assert galarian.availability.is_available_in(GameColumn.LGPE) is False


def test_load_rules_rejects_reversed_dex_range(tmp_path: Path) -> None:
    path = tmp_path / "invalid_range.yaml"
    write_rules(path)
    content = path.read_text(encoding="utf-8").replace(
        "national_dex_ranges: []",
        "national_dex_ranges: [[150, 1]]",
        1,
    )
    path.write_text(content, encoding="utf-8")

    with pytest.raises(
        ConfigurationError,
        match="reversed range",
    ):
        GameAvailabilityRules.from_yaml(path)


def test_legends_arceus_hisuian_form_overrides_normal_form() -> None:
    games = empty_rules()
    games[GameColumn.PLA] = GameRule(
        national_dex=frozenset({724}),
        national_dex_ranges=(),
        home_ids=frozenset(),
        excluded_home_ids=frozenset({"00724_NORMAL_NONE"}),
    )
    rules = GameAvailabilityRules(complete=False, games=games)

    normal, hisuian = apply_game_availability(
        (
            build_entry(national_dex=724, home_id="00724_NORMAL_NONE"),
            build_entry(national_dex=724, home_id="00724_HISUI_NONE"),
        ),
        rules,
    )

    assert normal.availability.is_available_in(GameColumn.PLA) is False
    assert hisuian.availability.is_available_in(GameColumn.PLA) is True


def test_legends_arceus_only_includes_white_striped_basculin() -> None:
    games = empty_rules()
    games[GameColumn.PLA] = GameRule(
        national_dex=frozenset({550}),
        national_dex_ranges=(),
        home_ids=frozenset(),
        excluded_home_ids=frozenset({"00550_NORMAL_NONE", "00550_BLUE_STRIPED_NONE"}),
    )
    rules = GameAvailabilityRules(complete=False, games=games)

    red, blue, white = apply_game_availability(
        (
            build_entry(national_dex=550, home_id="00550_NORMAL_NONE"),
            build_entry(national_dex=550, home_id="00550_BLUE_STRIPED_NONE"),
            build_entry(national_dex=550, home_id="00550_WHITE_STRIPED_NONE"),
        ),
        rules,
    )

    assert red.availability.is_available_in(GameColumn.PLA) is False
    assert blue.availability.is_available_in(GameColumn.PLA) is False
    assert white.availability.is_available_in(GameColumn.PLA) is True


def test_legends_arceus_accepts_both_sneasel_forms() -> None:
    games = empty_rules()
    games[GameColumn.PLA] = GameRule(
        national_dex=frozenset({215}),
        national_dex_ranges=(),
        home_ids=frozenset(),
        excluded_home_ids=frozenset(),
    )
    rules = GameAvailabilityRules(complete=False, games=games)

    normal, hisuian = apply_game_availability(
        (
            build_entry(national_dex=215, home_id="00215_NORMAL_FEMALE"),
            build_entry(national_dex=215, home_id="00215_HISUI_FEMALE"),
        ),
        rules,
    )

    assert normal.availability.is_available_in(GameColumn.PLA) is True
    assert hisuian.availability.is_available_in(GameColumn.PLA) is True


def test_legends_arceus_excludes_bloodmoon_ursaluna() -> None:
    games = empty_rules()
    games[GameColumn.PLA] = GameRule(
        national_dex=frozenset({901}),
        national_dex_ranges=(),
        home_ids=frozenset(),
        excluded_home_ids=frozenset({"00901_BLOODMOON_NONE"}),
    )
    rules = GameAvailabilityRules(complete=False, games=games)

    normal, bloodmoon = apply_game_availability(
        (
            build_entry(national_dex=901, home_id="00901_NORMAL_NONE"),
            build_entry(national_dex=901, home_id="00901_BLOODMOON_NONE"),
        ),
        rules,
    )

    assert normal.availability.is_available_in(GameColumn.PLA) is True
    assert bloodmoon.availability.is_available_in(GameColumn.PLA) is False


def test_load_rules_reads_per_game_complete_flag(tmp_path: Path) -> None:
    path = tmp_path / "complete_game.yaml"
    write_rules(path)
    content = path.read_text(encoding="utf-8").replace(
        "xy:\n    national_dex",
        "xy:\n    complete: true\n    national_dex",
    )
    path.write_text(content, encoding="utf-8")

    rules = GameAvailabilityRules.from_yaml(path)

    assert rules.games[GameColumn.XY].complete is True
    assert rules.games[GameColumn.SM].complete is False


def test_load_rules_rejects_non_boolean_game_complete(tmp_path: Path) -> None:
    path = tmp_path / "invalid_complete.yaml"
    write_rules(path)
    content = path.read_text(encoding="utf-8").replace(
        "xy:\n    national_dex",
        "xy:\n    complete: yes-please\n    national_dex",
    )
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ConfigurationError, match="xy.complete.*boolean"):
        GameAvailabilityRules.from_yaml(path)


def load_project_game_rules() -> GameAvailabilityRules:
    """Load the production catalog used by integration-style rule tests."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "game_availability.yaml"
    )
    return GameAvailabilityRules.from_yaml(catalog_path)


def test_xy_catalog_contains_454_non_event_species() -> None:
    rule = load_project_game_rules().games[GameColumn.XY]
    covered = set(rule.national_dex)

    for start, end in rule.national_dex_ranges:
        covered.update(range(start, end + 1))

    assert rule.complete is True
    assert len(covered) == 454
    assert 650 in covered  # Chespin starts the Central Kalos Pokédex.
    assert 718 in covered  # Zygarde closes the non-event Kalos collection.
    assert 719 not in covered  # Diancie requires an event in X/Y.
    assert 720 not in covered  # Hoopa requires an event in X/Y.
    assert 721 not in covered  # Volcanion requires an event in X/Y.


def test_xy_excludes_later_regional_and_cosplay_forms() -> None:
    rules = load_project_game_rules()
    normal, alolan, hisuian, cosplay = apply_game_availability(
        (
            build_entry(national_dex=26, home_id="00026_NORMAL_FEMALE"),
            build_entry(national_dex=26, home_id="00026_ALOLA_NONE"),
            build_entry(national_dex=100, home_id="00100_HISUI_NONE"),
            build_entry(national_dex=25, home_id="00025_LIBRE_NONE"),
        ),
        rules,
    )

    assert normal.availability.is_available_in(GameColumn.XY) is True
    assert alolan.availability.is_available_in(GameColumn.XY) is False
    assert hisuian.availability.is_available_in(GameColumn.XY) is False
    assert cosplay.availability.is_available_in(GameColumn.XY) is False


def test_xy_keeps_forms_obtainable_in_generation_six() -> None:
    rules = load_project_game_rules()
    sandy_wormadam, wash_rotom, blue_basculin, super_pumpkaboo = (
        apply_game_availability(
            (
                build_entry(national_dex=413, home_id="00413_SANDY_NONE"),
                build_entry(national_dex=479, home_id="00479_WASH_NONE"),
                build_entry(national_dex=550, home_id="00550_BLUE_STRIPED_NONE"),
                build_entry(national_dex=710, home_id="00710_SUPER_NONE"),
            ),
            rules,
        )
    )

    assert sandy_wormadam.availability.is_available_in(GameColumn.XY) is True
    assert wash_rotom.availability.is_available_in(GameColumn.XY) is True
    assert blue_basculin.availability.is_available_in(GameColumn.XY) is True
    assert super_pumpkaboo.availability.is_available_in(GameColumn.XY) is True


def test_xy_only_includes_original_zygarde_form() -> None:
    rules = load_project_game_rules()
    original, ten_percent, power_construct = apply_game_availability(
        (
            build_entry(national_dex=718, home_id="00718_NORMAL_NONE"),
            build_entry(national_dex=718, home_id="00718_10_NONE"),
            build_entry(
                national_dex=718,
                home_id="00718_50_POWER_CONSTRUCT_NONE",
            ),
        ),
        rules,
    )

    assert original.availability.is_available_in(GameColumn.XY) is True
    assert ten_percent.availability.is_available_in(GameColumn.XY) is False
    assert power_construct.availability.is_available_in(GameColumn.XY) is False


def test_oras_regional_catalog_contains_210_non_event_species() -> None:
    """The updated Hoenn Dex has 211 entries; event-only Jirachi is omitted."""
    rule = load_project_game_rules().games[GameColumn.ORAS]
    covered = set(rule.national_dex)

    for start, end in rule.national_dex_ranges:
        covered.update(range(start, end + 1))

    assert rule.complete is False
    assert len(covered) == 210
    assert 252 in covered  # Treecko opens the updated Hoenn Pokédex.
    assert 384 in covered  # Rayquaza is obtainable during normal play.
    assert 385 not in covered  # Jirachi requires an external event.
    assert 386 in covered  # Deoxys is obtainable in the Delta Episode.


def test_oras_keeps_all_deoxys_formes() -> None:
    # ORAS lets Deoxys change between all four retained formes, so every
    # corresponding HOME row inherits the species-level availability rule.
    rules = load_project_game_rules()
    normal, attack, defense, speed = apply_game_availability(
        (
            build_entry(national_dex=386, home_id="00386_NORMAL_NONE"),
            build_entry(national_dex=386, home_id="00386_ATTACK_NONE"),
            build_entry(national_dex=386, home_id="00386_DEFENSE_NONE"),
            build_entry(national_dex=386, home_id="00386_SPEED_NONE"),
        ),
        rules,
    )

    assert normal.availability.is_available_in(GameColumn.ORAS) is True
    assert attack.availability.is_available_in(GameColumn.ORAS) is True
    assert defense.availability.is_available_in(GameColumn.ORAS) is True
    assert speed.availability.is_available_in(GameColumn.ORAS) is True


def test_oras_excludes_later_regional_forms_and_cosplay_pikachu() -> None:
    rules = load_project_game_rules()
    normal, alolan, hisuian, cosplay = apply_game_availability(
        (
            build_entry(national_dex=26, home_id="00026_NORMAL_FEMALE"),
            build_entry(national_dex=26, home_id="00026_ALOLA_NONE"),
            build_entry(national_dex=100, home_id="00100_HISUI_NONE"),
            build_entry(national_dex=25, home_id="00025_LIBRE_NONE"),
        ),
        rules,
    )

    assert normal.availability.is_available_in(GameColumn.ORAS) is True
    assert alolan.availability.is_available_in(GameColumn.ORAS) is False
    assert hisuian.availability.is_available_in(GameColumn.ORAS) is False
    assert cosplay.availability.is_available_in(GameColumn.ORAS) is False


def test_sm_regional_catalog_contains_300_non_event_species() -> None:
    """The original Alola Dex has 302 entries; two require external gifts."""
    rule = load_project_game_rules().games[GameColumn.SM]
    covered = set(rule.national_dex)

    for start, end in rule.national_dex_ranges:
        covered.update(range(start, end + 1))

    assert rule.complete is False
    assert len(covered) == 300
    assert 722 in covered
    assert 800 in covered
    assert 801 not in covered
    assert 802 not in covered


def test_sm_uses_alolan_forms_for_replaced_kanto_lines() -> None:
    rules = load_project_game_rules()
    normal_rattata, alolan_rattata, pikachu, normal_raichu, alolan_raichu = (
        apply_game_availability(
            (
                build_entry(national_dex=19, home_id="00019_NORMAL_FEMALE"),
                build_entry(national_dex=19, home_id="00019_ALOLA_NONE"),
                build_entry(national_dex=25, home_id="00025_NORMAL_FEMALE"),
                build_entry(national_dex=26, home_id="00026_NORMAL_FEMALE"),
                build_entry(national_dex=26, home_id="00026_ALOLA_NONE"),
            ),
            rules,
        )
    )

    assert normal_rattata.availability.is_available_in(GameColumn.SM) is False
    assert alolan_rattata.availability.is_available_in(GameColumn.SM) is True
    assert pikachu.availability.is_available_in(GameColumn.SM) is True
    assert normal_raichu.availability.is_available_in(GameColumn.SM) is False
    assert alolan_raichu.availability.is_available_in(GameColumn.SM) is True


def test_sm_excludes_forms_introduced_in_usum_or_later() -> None:
    rules = load_project_game_rules()
    rockruff, own_tempo, midnight, dusk, necrozma, dawn, hisuian = (
        apply_game_availability(
            (
                build_entry(national_dex=744, home_id="00744_NORMAL_NONE"),
                build_entry(national_dex=744, home_id="00744_OWN_TEMPO_NONE"),
                build_entry(national_dex=745, home_id="00745_MIDNIGHT_NONE"),
                build_entry(national_dex=745, home_id="00745_DUSK_NONE"),
                build_entry(national_dex=800, home_id="00800_NORMAL_NONE"),
                build_entry(national_dex=800, home_id="00800_DAWN_NONE"),
                build_entry(national_dex=724, home_id="00724_HISUI_NONE"),
            ),
            rules,
        )
    )

    assert rockruff.availability.is_available_in(GameColumn.SM) is True
    assert own_tempo.availability.is_available_in(GameColumn.SM) is False
    assert midnight.availability.is_available_in(GameColumn.SM) is True
    assert dusk.availability.is_available_in(GameColumn.SM) is False
    assert necrozma.availability.is_available_in(GameColumn.SM) is True
    assert dawn.availability.is_available_in(GameColumn.SM) is False
    assert hisuian.availability.is_available_in(GameColumn.SM) is False


def test_sm_keeps_oricorio_and_zygarde_stored_forms() -> None:
    rules = load_project_game_rules()
    baile, pom_pom, pau, sensu, fifty, ten_percent = apply_game_availability(
        (
            build_entry(national_dex=741, home_id="00741_NORMAL_NONE"),
            build_entry(national_dex=741, home_id="00741_POM_POM_NONE"),
            build_entry(national_dex=741, home_id="00741_PAU_NONE"),
            build_entry(national_dex=741, home_id="00741_SENSU_NONE"),
            build_entry(national_dex=718, home_id="00718_NORMAL_NONE"),
            build_entry(national_dex=718, home_id="00718_10_NONE"),
        ),
        rules,
    )

    for entry in (baile, pom_pom, pau, sensu, fifty, ten_percent):
        assert entry.availability.is_available_in(GameColumn.SM) is True


def test_usum_regional_catalog_contains_400_non_event_species() -> None:
    """The updated Alola Dex has 403 entries; three event species are omitted."""
    rule = load_project_game_rules().games[GameColumn.USUM]
    covered = set(rule.national_dex)

    for start, end in rule.national_dex_ranges:
        covered.update(range(start, end + 1))

    assert rule.complete is False
    assert len(covered) == 400
    assert 722 in covered  # Rowlet remains the first Alola starter.
    assert 803 in covered  # Poipole was introduced in Ultra Sun/Moon.
    assert 806 in covered  # Blacephalon is available in Ultra Sun.
    assert 801 not in covered  # Magearna requires an external QR-code gift.
    assert 802 not in covered  # Marshadow requires an event distribution.
    assert 807 not in covered  # Zeraora requires an event distribution.


def test_usum_prefers_alolan_forms_during_normal_play() -> None:
    rules = load_project_game_rules()
    normal, alolan = apply_game_availability(
        (
            build_entry(national_dex=26, home_id="00026_NORMAL_FEMALE"),
            build_entry(national_dex=26, home_id="00026_ALOLA_NONE"),
        ),
        rules,
    )

    assert normal.availability.is_available_in(GameColumn.USUM) is False
    assert alolan.availability.is_available_in(GameColumn.USUM) is True


def test_usum_excludes_event_only_dusk_lycanroc_line() -> None:
    rules = load_project_game_rules()
    regular, own_tempo, midday, dusk = apply_game_availability(
        (
            build_entry(national_dex=744, home_id="00744_NORMAL_NONE"),
            build_entry(national_dex=744, home_id="00744_OWN_TEMPO_NONE"),
            build_entry(national_dex=745, home_id="00745_MIDDAY_NONE"),
            build_entry(national_dex=745, home_id="00745_DUSK_NONE"),
        ),
        rules,
    )

    assert regular.availability.is_available_in(GameColumn.USUM) is True
    assert own_tempo.availability.is_available_in(GameColumn.USUM) is False
    assert midday.availability.is_available_in(GameColumn.USUM) is True
    assert dusk.availability.is_available_in(GameColumn.USUM) is False


def test_usum_excludes_later_regional_forms() -> None:
    rules = load_project_game_rules()
    normal, galarian, hisuian, paldean = apply_game_availability(
        (
            build_entry(national_dex=52, home_id="00052_ALOLA_NONE"),
            build_entry(national_dex=52, home_id="00052_GALAR_NONE"),
            build_entry(national_dex=215, home_id="00215_HISUI_FEMALE"),
            build_entry(
                national_dex=128,
                home_id="00128_PALDEA_COMBAT_BREED_NONE",
            ),
        ),
        rules,
    )

    assert normal.availability.is_available_in(GameColumn.USUM) is True
    assert galarian.availability.is_available_in(GameColumn.USUM) is False
    assert hisuian.availability.is_available_in(GameColumn.USUM) is False
    assert paldean.availability.is_available_in(GameColumn.USUM) is False
