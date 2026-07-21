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


def test_xy_catalog_contains_friend_safari_and_evolution_lines() -> None:
    rule = load_project_game_rules().games[GameColumn.XY]
    covered = set(rule.national_dex)

    for start, end in rule.national_dex_ranges:
        covered.update(range(start, end + 1))

    assert rule.complete is True
    assert len(covered) == 577
    assert 650 in covered  # Chespin starts the Central Kalos Pokédex.
    assert 718 in covered  # Zygarde closes the non-event Kalos collection.
    assert 719 not in covered  # Diancie requires an event in X/Y.
    assert 720 not in covered  # Hoopa requires an event in X/Y.
    assert 721 not in covered  # Volcanion requires an event in X/Y.


def test_xy_excludes_later_regional_and_cosplay_forms() -> None:
    rules = load_project_game_rules()
    normal, alolan, hisuian = apply_game_availability(
        (
            build_entry(national_dex=26, home_id="00026_NORMAL_FEMALE"),
            build_entry(national_dex=26, home_id="00026_ALOLA_NONE"),
            build_entry(national_dex=100, home_id="00100_HISUI_NONE"),
        ),
        rules,
    )

    assert normal.availability.is_available_in(GameColumn.XY) is True
    assert alolan.availability.is_available_in(GameColumn.XY) is False
    assert hisuian.availability.is_available_in(GameColumn.XY) is False


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


def test_oras_catalog_includes_permanent_post_national_dex_methods() -> None:
    """DexNav, Mirage Spots, and soaring encounters count as permanent."""
    rules = load_project_game_rules()
    treecko, zorua, cresselia, zekrom, jirachi = apply_game_availability(
        (
            build_entry(national_dex=252, home_id="00252_NORMAL_NONE"),
            build_entry(national_dex=570, home_id="00570_NORMAL_NONE"),
            build_entry(national_dex=488, home_id="00488_NORMAL_NONE"),
            build_entry(national_dex=644, home_id="00644_NORMAL_NONE"),
            build_entry(national_dex=385, home_id="00385_NORMAL_NONE"),
        ),
        rules,
    )

    for entry in (treecko, zorua, cresselia, zekrom):
        assert entry.availability.is_available_in(GameColumn.ORAS) is True

    # Jirachi still requires an external distribution in ORAS.
    assert jirachi.availability.is_available_in(GameColumn.ORAS) is False


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
    normal, alolan, hisuian = apply_game_availability(
        (
            build_entry(national_dex=26, home_id="00026_NORMAL_FEMALE"),
            build_entry(national_dex=26, home_id="00026_ALOLA_NONE"),
            build_entry(national_dex=100, home_id="00100_HISUI_NONE"),
        ),
        rules,
    )

    assert normal.availability.is_available_in(GameColumn.ORAS) is True
    assert alolan.availability.is_available_in(GameColumn.ORAS) is False
    assert hisuian.availability.is_available_in(GameColumn.ORAS) is False


def test_sm_qr_methods_include_magearna_and_island_scan() -> None:
    """Permanent QR-based methods count as obtainable in Sun/Moon."""
    rules = load_project_game_rules()
    magearna, chikorita, deino, samurott, marshadow = apply_game_availability(
        (
            build_entry(national_dex=801, home_id="00801_NORMAL_NONE"),
            build_entry(national_dex=152, home_id="00152_NORMAL_NONE"),
            build_entry(national_dex=633, home_id="00633_NORMAL_NONE"),
            build_entry(national_dex=503, home_id="00503_NORMAL_NONE"),
            build_entry(national_dex=802, home_id="00802_NORMAL_NONE"),
        ),
        rules,
    )

    for entry in (magearna, chikorita, deino, samurott):
        assert entry.availability.is_available_in(GameColumn.SM) is True

    assert marshadow.availability.is_available_in(GameColumn.SM) is False


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


def test_usum_qr_and_ultra_warp_ride_methods_are_obtainable() -> None:
    """QR methods and Ultra Warp Ride are permanent USUM encounter systems."""
    rules = load_project_game_rules()
    magearna, bulbasaur, greninja, hippowdon, mewtwo, zeraora = apply_game_availability(
        (
            build_entry(national_dex=801, home_id="00801_NORMAL_NONE"),
            build_entry(national_dex=1, home_id="00001_NORMAL_NONE"),
            build_entry(national_dex=658, home_id="00658_NORMAL_NONE"),
            build_entry(national_dex=450, home_id="00450_NORMAL_FEMALE"),
            build_entry(national_dex=150, home_id="00150_NORMAL_NONE"),
            build_entry(national_dex=807, home_id="00807_NORMAL_NONE"),
        ),
        rules,
    )

    for entry in (magearna, bulbasaur, greninja, hippowdon, mewtwo):
        assert entry.availability.is_available_in(GameColumn.USUM) is True

    assert zeraora.availability.is_available_in(GameColumn.USUM) is False


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


def test_swsh_includes_permanent_dynamax_adventure_encounters() -> None:
    """Dynamax Adventures add permanent encounters beyond the regional Dexes."""
    rules = load_project_game_rules()
    sceptile, swampert, mewtwo, xerneas, nihilego, zarude = apply_game_availability(
        (
            build_entry(national_dex=254, home_id="00254_NORMAL_NONE"),
            build_entry(national_dex=260, home_id="00260_NORMAL_NONE"),
            build_entry(national_dex=150, home_id="00150_NORMAL_NONE"),
            build_entry(national_dex=716, home_id="00716_NORMAL_NONE"),
            build_entry(national_dex=793, home_id="00793_NORMAL_NONE"),
            build_entry(national_dex=893, home_id="00893_NORMAL_NONE"),
        ),
        rules,
    )

    for entry in (sceptile, swampert, mewtwo, xerneas, nihilego):
        assert entry.availability.is_available_in(GameColumn.SWSH) is True

    assert zarude.availability.is_available_in(GameColumn.SWSH) is False


def test_swsh_accepts_galarian_and_supported_alolan_forms() -> None:
    rules = load_project_game_rules()
    alolan, galarian = apply_game_availability(
        (
            build_entry(national_dex=26, home_id="00026_ALOLA_NONE"),
            build_entry(national_dex=77, home_id="00077_GALAR_NONE"),
        ),
        rules,
    )

    assert alolan.availability.is_available_in(GameColumn.SWSH) is True
    assert galarian.availability.is_available_in(GameColumn.SWSH) is True


def test_swsh_excludes_later_regional_forms() -> None:
    rules = load_project_game_rules()
    hisuian, paldean, white_striped = apply_game_availability(
        (
            build_entry(national_dex=58, home_id="00058_HISUI_NONE"),
            build_entry(national_dex=194, home_id="00194_PALDEA_NONE"),
            build_entry(national_dex=550, home_id="00550_WHITE_STRIPED_NONE"),
        ),
        rules,
    )

    assert hisuian.availability.is_available_in(GameColumn.SWSH) is False
    assert paldean.availability.is_available_in(GameColumn.SWSH) is False
    assert white_striped.availability.is_available_in(GameColumn.SWSH) is False


def test_swsh_excludes_event_zarude_and_unstorable_calyrex_fusions() -> None:
    rules = load_project_game_rules()
    zarude, dada, calyrex = apply_game_availability(
        (
            build_entry(national_dex=893, home_id="00893_NORMAL_NONE"),
            build_entry(national_dex=893, home_id="00893_DADA_NONE"),
            build_entry(national_dex=898, home_id="00898_NORMAL_NONE"),
        ),
        rules,
    )

    assert zarude.availability.is_available_in(GameColumn.SWSH) is False
    assert dada.availability.is_available_in(GameColumn.SWSH) is False
    assert calyrex.availability.is_available_in(GameColumn.SWSH) is True


def test_pla_save_data_research_requests_are_obtainable() -> None:
    """Permanent save-data research requests count as obtainable in PLA."""
    rules = load_project_game_rules()
    darkrai, shaymin_land, shaymin_sky = apply_game_availability(
        (
            build_entry(national_dex=491, home_id="00491_NORMAL_NONE"),
            build_entry(national_dex=492, home_id="00492_NORMAL_NONE"),
            build_entry(national_dex=492, home_id="00492_SKY_NONE"),
        ),
        rules,
    )

    assert darkrai.availability.is_available_in(GameColumn.PLA) is True
    assert shaymin_land.availability.is_available_in(GameColumn.PLA) is True
    assert shaymin_sky.availability.is_available_in(GameColumn.PLA) is True


def test_bdsp_complete_catalog_covers_first_four_generations() -> None:
    """BDSP supports the first 493 species before form-specific exclusions."""
    rule = load_project_game_rules().games[GameColumn.BDSP]

    assert rule.complete is True
    assert rule.national_dex_ranges == ((1, 250), (252, 385), (387, 488))
    assert rule.national_dex == ({493})
    assert rule.includes_national_dex(1) is True
    assert rule.includes_national_dex(493) is True
    assert rule.includes_national_dex(494) is False


def test_bdsp_keeps_supported_gender_and_platinum_forms() -> None:
    rules = load_project_game_rules()
    female, male, sandy, trash, wash = apply_game_availability(
        (
            build_entry(national_dex=25, home_id="00025_NORMAL_FEMALE"),
            build_entry(national_dex=25, home_id="00025_NORMAL_MALE"),
            build_entry(national_dex=413, home_id="00413_SANDY_NONE"),
            build_entry(national_dex=413, home_id="00413_TRASH_NONE"),
            build_entry(national_dex=479, home_id="00479_WASH_NONE"),
        ),
        rules,
    )

    for entry in (female, male, sandy, trash, wash):
        assert entry.availability.is_available_in(GameColumn.BDSP) is True


def test_bdsp_excludes_regional_cosplay_and_temporary_forms() -> None:
    rules = load_project_game_rules()
    alolan, galarian, hisuian, paldean = apply_game_availability(
        (
            build_entry(national_dex=26, home_id="00026_ALOLA_NONE"),
            build_entry(national_dex=77, home_id="00077_GALAR_NONE"),
            build_entry(national_dex=58, home_id="00058_HISUI_NONE"),
            build_entry(
                national_dex=128,
                home_id="00128_PALDEA_COMBAT_BREED_NONE",
            ),
        ),
        rules,
    )

    for entry in (alolan, galarian, hisuian, paldean):
        assert entry.availability.is_available_in(GameColumn.BDSP) is False


def test_bdsp_keeps_all_deoxys_formes_but_marks_them_unavailable() -> None:
    """Deoxys Formes stay in the dataset even though BDSP cannot originate them."""
    rules = load_project_game_rules()
    formes = apply_game_availability(
        (
            build_entry(national_dex=386, home_id="00386_NORMAL_NONE"),
            build_entry(national_dex=386, home_id="00386_ATTACK_NONE"),
            build_entry(national_dex=386, home_id="00386_DEFENSE_NONE"),
            build_entry(national_dex=386, home_id="00386_SPEED_NONE"),
        ),
        rules,
    )

    assert all(
        entry.availability.is_available_in(GameColumn.BDSP) is False for entry in formes
    )


def test_bdsp_handles_save_data_unlocks_and_event_only_mythicals() -> None:
    rules = load_project_game_rules()
    mew, jirachi, arceus, celebi, manaphy, darkrai, shaymin = apply_game_availability(
        (
            build_entry(national_dex=151, home_id="00151_NORMAL_NONE"),
            build_entry(national_dex=385, home_id="00385_NORMAL_NONE"),
            build_entry(national_dex=493, home_id="00493_NORMAL_NONE"),
            build_entry(national_dex=251, home_id="00251_NORMAL_NONE"),
            build_entry(national_dex=490, home_id="00490_NORMAL_NONE"),
            build_entry(national_dex=491, home_id="00491_NORMAL_NONE"),
            build_entry(national_dex=492, home_id="00492_NORMAL_NONE"),
        ),
        rules,
    )

    assert mew.availability.is_available_in(GameColumn.BDSP) is True
    assert jirachi.availability.is_available_in(GameColumn.BDSP) is True
    assert arceus.availability.is_available_in(GameColumn.BDSP) is True
    assert celebi.availability.is_available_in(GameColumn.BDSP) is False
    assert manaphy.availability.is_available_in(GameColumn.BDSP) is False
    assert darkrai.availability.is_available_in(GameColumn.BDSP) is False
    assert shaymin.availability.is_available_in(GameColumn.BDSP) is False


def test_sv_complete_catalog_covers_three_regional_pokedexes() -> None:
    """SV covers Paldea, Kitakami, and Blueberry except event-only species."""
    rule = load_project_game_rules().games[GameColumn.SV]

    assert rule.complete is True
    assert rule.includes_national_dex(906) is True
    assert rule.includes_national_dex(1017) is True
    assert rule.includes_national_dex(1024) is True
    assert rule.includes_national_dex(1009) is False
    assert rule.includes_national_dex(1010) is False
    assert "01025_NORMAL_NONE" in rule.home_ids


def test_sv_keeps_supported_regional_and_special_forms() -> None:
    rules = load_project_game_rules()
    entries = apply_game_availability(
        (
            build_entry(national_dex=128, home_id="00128_PALDEA_COMBAT_BREED_NONE"),
            build_entry(national_dex=194, home_id="00194_PALDEA_NONE"),
            build_entry(national_dex=901, home_id="00901_BLOODMOON_NONE"),
            build_entry(national_dex=999, home_id="00999_NORMAL_NONE"),
        ),
        rules,
    )

    assert all(entry.availability.is_available_in(GameColumn.SV) for entry in entries)


def test_sv_keeps_pecharunt_mystery_gift_but_excludes_timed_events() -> None:
    """The permanent Pecharunt epilogue gift counts; timed raids do not."""
    rules = load_project_game_rules()
    walking_wake, iron_leaves, pecharunt = apply_game_availability(
        (
            build_entry(national_dex=1009, home_id="01009_NORMAL_NONE"),
            build_entry(national_dex=1010, home_id="01010_NORMAL_NONE"),
            build_entry(national_dex=1025, home_id="01025_NORMAL_NONE"),
        ),
        rules,
    )

    assert walking_wake.availability.is_available_in(GameColumn.SV) is False
    assert iron_leaves.availability.is_available_in(GameColumn.SV) is False
    assert pecharunt.availability.is_available_in(GameColumn.SV) is True


def test_za_catalog_covers_base_game_and_mega_dimension_species() -> None:
    """The audited Z-A set combines the Lumiose and Mega Dimension Pokédexes."""
    rule = load_project_game_rules().games[GameColumn.ZA]

    assert rule.complete is True
    assert rule.includes_national_dex(152) is True  # Chikorita, base game
    assert rule.includes_national_dex(718) is True  # Zygarde, base game
    assert rule.includes_national_dex(979) is True  # Annihilape, DLC
    assert rule.includes_national_dex(1000) is True  # Gholdengo, DLC
    assert rule.includes_national_dex(906) is False  # Not in either audited dex


def test_za_keeps_eternal_floette_and_mystery_gift_species() -> None:
    """Permanent Mystery Gift unlocks still count as obtainable in Z-A."""
    rules = load_project_game_rules()
    entries = apply_game_availability(
        (
            build_entry(national_dex=670, home_id="00670_ETERNAL_NONE"),
            build_entry(national_dex=150, home_id="00150_NORMAL_NONE"),
            build_entry(national_dex=719, home_id="00719_NORMAL_NONE"),
            build_entry(national_dex=807, home_id="00807_NORMAL_NONE"),
        ),
        rules,
    )

    assert all(entry.availability.is_available_in(GameColumn.ZA) for entry in entries)


def test_za_keeps_compatible_regional_forms() -> None:
    """Current HOME compatibility allows supported regional forms in Z-A."""
    rules = load_project_game_rules()
    entries = apply_game_availability(
        (
            build_entry(national_dex=26, home_id="00026_ALOLA_NONE"),
            build_entry(national_dex=79, home_id="00079_GALAR_NONE"),
            build_entry(national_dex=705, home_id="00705_HISUI_NONE"),
            build_entry(national_dex=713, home_id="00713_HISUI_NONE"),
        ),
        rules,
    )

    assert all(entry.availability.is_available_in(GameColumn.ZA) for entry in entries)


def test_za_keeps_storable_alternate_forms_from_audited_species() -> None:
    """Stored alternate forms remain available when no form exclusion applies."""
    rules = load_project_game_rules()
    entries = apply_game_availability(
        (
            build_entry(national_dex=479, home_id="00479_WASH_NONE"),
            build_entry(national_dex=710, home_id="00710_SUPER_NONE"),
            build_entry(national_dex=720, home_id="00720_UNBOUND_NONE"),
        ),
        rules,
    )

    assert all(entry.availability.is_available_in(GameColumn.ZA) for entry in entries)


def test_special_acquisition_comments_use_standard_terminology() -> None:
    """Treat acquisition comments as part of the catalog documentation contract."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "game_availability.yaml"
    )
    catalog_text = catalog_path.read_text(encoding="utf-8")

    required_phrases = (
        "# Method: QR Code",
        "Magearna is obtainable only through QR Code.",
        "# Method: Island Scan QR Code",
        "Island Scan species are obtainable only through Island Scan QR Codes.",
        "# Method: Mystery Gift",
        "# Method: Ultra Warp Ride",
        "# Method: Dynamax Adventures",
        "# Method: DexNav / Mirage Spots / Soaring",
    )

    for phrase in required_phrases:
        assert phrase in catalog_text

    # QR acquisition must not be described as ordinary or permanent availability.
    assert "permanent QR Code gift" not in catalog_text
    assert "permanent QR-based method" not in catalog_text
