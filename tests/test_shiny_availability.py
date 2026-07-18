from pathlib import Path

import pytest

from pokedex.constants import Gender
from pokedex.exceptions import ConfigurationError
from pokedex.models import GameAvailability, PokemonEntry
from pokedex.shiny_availability import (
    ShinyAvailabilityRules,
    apply_shiny_availability,
)


def build_entry(
    *,
    national_dex: int = 25,
    home_id: str = "00025_NORMAL_NONE",
    obtainable_shiny: bool = False,
) -> PokemonEntry:
    return PokemonEntry(
        national_dex=national_dex,
        pokemon="Pikachu",
        form="Normal",
        name="Pikachu",
        generation=1,
        home_id=home_id,
        gender=Gender.NONE,
        availability=GameAvailability(),
        legendary_mythical=False,
        obtainable_shiny=obtainable_shiny,
    )


def write_rules(path: Path) -> None:
    path.write_text(
        """
version: "1.1"
complete: false
national_dex: [25]
national_dex_ranges:
  - [1, 10]
home_ids: ["00026_ALOLA_NONE"]
excluded_home_ids: ["00025_SPECIAL_NONE"]
""".strip(),
        encoding="utf-8",
    )


def test_load_shiny_availability_rules(tmp_path: Path) -> None:
    path = tmp_path / "shiny_availability.yaml"
    write_rules(path)

    rules = ShinyAvailabilityRules.from_yaml(path)

    assert rules.complete is False
    assert 25 in rules.national_dex
    assert rules.national_dex_ranges == ((1, 10),)
    assert "00026_ALOLA_NONE" in rules.home_ids


def test_species_rule_applies_to_every_variant() -> None:
    rules = ShinyAvailabilityRules(
        complete=False,
        national_dex=frozenset({25}),
        national_dex_ranges=(),
        home_ids=frozenset(),
        excluded_home_ids=frozenset(),
    )

    normal, special = apply_shiny_availability(
        (
            build_entry(),
            build_entry(home_id="00025_SPECIAL_NONE"),
        ),
        rules,
    )

    assert normal.obtainable_shiny is True
    assert special.obtainable_shiny is True


def test_national_dex_range_applies_to_every_retained_variant() -> None:
    rules = ShinyAvailabilityRules(
        complete=False,
        national_dex=frozenset(),
        national_dex_ranges=((1, 150),),
        home_ids=frozenset(),
        excluded_home_ids=frozenset(),
    )

    normal, regional, outside = apply_shiny_availability(
        (
            build_entry(national_dex=26, home_id="00026_NORMAL_NONE"),
            build_entry(national_dex=26, home_id="00026_ALOLA_NONE"),
            build_entry(national_dex=151, home_id="00151_NORMAL_NONE"),
        ),
        rules,
    )

    assert normal.obtainable_shiny is True
    assert regional.obtainable_shiny is True
    assert outside.obtainable_shiny is False


def test_home_id_rule_can_include_one_specific_variant() -> None:
    rules = ShinyAvailabilityRules(
        complete=False,
        national_dex=frozenset(),
        national_dex_ranges=(),
        home_ids=frozenset({"00026_ALOLA_NONE"}),
        excluded_home_ids=frozenset(),
    )

    normal, alolan = apply_shiny_availability(
        (
            build_entry(national_dex=26, home_id="00026_NORMAL_NONE"),
            build_entry(national_dex=26, home_id="00026_ALOLA_NONE"),
        ),
        rules,
    )

    assert normal.obtainable_shiny is False
    assert alolan.obtainable_shiny is True


def test_form_exclusion_overrides_species_inclusion() -> None:
    rules = ShinyAvailabilityRules(
        complete=False,
        national_dex=frozenset({25}),
        national_dex_ranges=(),
        home_ids=frozenset(),
        excluded_home_ids=frozenset({"00025_SPECIAL_NONE"}),
    )

    normal, special = apply_shiny_availability(
        (
            build_entry(),
            build_entry(home_id="00025_SPECIAL_NONE"),
        ),
        rules,
    )

    assert normal.obtainable_shiny is True
    assert special.obtainable_shiny is False


def test_apply_shiny_preserves_order_and_other_fields() -> None:
    entries = (
        build_entry(home_id="00025_NORMAL_FEMALE"),
        build_entry(home_id="00025_NORMAL_MALE"),
    )
    rules = ShinyAvailabilityRules(
        complete=False,
        national_dex=frozenset({25}),
        national_dex_ranges=(),
        home_ids=frozenset(),
        excluded_home_ids=frozenset(),
    )

    result = apply_shiny_availability(entries, rules)

    assert [entry.home_id for entry in result] == [
        "00025_NORMAL_FEMALE",
        "00025_NORMAL_MALE",
    ]
    assert result[0].availability == entries[0].availability
    assert all(entry.obtainable_shiny for entry in result)


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
        ShinyAvailabilityRules.from_yaml(path)


def test_load_rules_rejects_reversed_range(tmp_path: Path) -> None:
    path = tmp_path / "invalid.yaml"
    write_rules(path)
    content = path.read_text(encoding="utf-8").replace(
        "  - [1, 10]",
        "  - [10, 1]",
    )
    path.write_text(content, encoding="utf-8")

    with pytest.raises(
        ConfigurationError,
        match="reversed range",
    ):
        ShinyAvailabilityRules.from_yaml(path)


def test_load_rules_rejects_empty_home_id(tmp_path: Path) -> None:
    path = tmp_path / "invalid.yaml"
    write_rules(path)
    content = path.read_text(encoding="utf-8").replace(
        'home_ids: ["00026_ALOLA_NONE"]',
        'home_ids: [""]',
    )
    path.write_text(content, encoding="utf-8")

    with pytest.raises(
        ConfigurationError,
        match="non-empty strings",
    ):
        ShinyAvailabilityRules.from_yaml(path)


def test_kanto_catalog_documents_go_only_galarian_bird_exception() -> None:
    """GO is documented only where it is the sole permanent shiny source."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    content = catalog_path.read_text(encoding="utf-8")

    assert "only permanent, non-event legitimate source" in content
    assert "00144_GALAR_NONE" in content
    assert "00145_GALAR_NONE" in content
    assert "00146_GALAR_NONE" in content


def test_johto_catalog_includes_normal_regional_and_mythical_variants() -> None:
    """The Johto tranche covers retained forms and the VC Crystal Celebi."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    rules = ShinyAvailabilityRules.from_yaml(catalog_path)

    typhlosion, hisuian_typhlosion, paldean_wooper, celebi = apply_shiny_availability(
        (
            build_entry(national_dex=157, home_id="00157_NORMAL_NONE"),
            build_entry(national_dex=157, home_id="00157_HISUI_NONE"),
            build_entry(national_dex=194, home_id="00194_PALDEA_NONE"),
            build_entry(national_dex=251, home_id="00251_NORMAL_NONE"),
        ),
        rules,
    )

    assert typhlosion.obtainable_shiny is True
    assert hisuian_typhlosion.obtainable_shiny is True
    assert paldean_wooper.obtainable_shiny is True
    assert celebi.obtainable_shiny is True


def test_johto_catalog_documents_celebi_legacy_method() -> None:
    """Celebi's non-event shiny route must remain explicitly documented."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    content = catalog_path.read_text(encoding="utf-8")

    assert "GS Ball encounter" in content
    assert "legacy installation" in content
    assert "Pokémon GO is therefore not" in content
    assert "used for Celebi under the project's source-priority rule" in content


def test_hoenn_catalog_includes_regional_mythical_and_all_deoxys_formes() -> None:
    """The Hoenn tranche covers retained regional and mythical variants."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    rules = ShinyAvailabilityRules.from_yaml(catalog_path)

    treecko, galarian_zigzagoon, jirachi, normal, attack, defense, speed = (
        apply_shiny_availability(
            (
                build_entry(national_dex=252, home_id="00252_NORMAL_NONE"),
                build_entry(national_dex=263, home_id="00263_GALAR_NONE"),
                build_entry(national_dex=385, home_id="00385_NORMAL_NONE"),
                build_entry(national_dex=386, home_id="00386_NORMAL_NONE"),
                build_entry(national_dex=386, home_id="00386_ATTACK_NONE"),
                build_entry(national_dex=386, home_id="00386_DEFENSE_NONE"),
                build_entry(national_dex=386, home_id="00386_SPEED_NONE"),
            ),
            rules,
        )
    )

    assert treecko.obtainable_shiny is True
    assert galarian_zigzagoon.obtainable_shiny is True
    assert jirachi.obtainable_shiny is True
    assert all(entry.obtainable_shiny for entry in (normal, attack, defense, speed))


def test_hoenn_catalog_documents_legacy_jirachi_and_switch_deoxys_methods() -> None:
    """Special Hoenn shiny routes must remain explicit and avoid GO."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    content = catalog_path.read_text(encoding="utf-8")

    assert "Pokémon Colosseum" in content
    assert "Bonus Disc or Pokémon Channel" in content
    assert "AuroraTicket encounter" in content
    assert "all retained Deoxys forms are covered" in content
    assert content.count("Pokémon GO is not used.") >= 2


def test_sinnoh_catalog_classifies_permanent_and_event_only_methods() -> None:
    """Sinnoh keeps permanent methods and excludes event-only mythicals."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    rules = ShinyAvailabilityRules.from_yaml(catalog_path)

    turtwig, manaphy, phione, darkrai, shaymin, sky_shaymin, arceus = (
        apply_shiny_availability(
            (
                build_entry(national_dex=387, home_id="00387_NORMAL_NONE"),
                build_entry(national_dex=490, home_id="00490_NORMAL_NONE"),
                build_entry(national_dex=489, home_id="00489_NORMAL_NONE"),
                build_entry(national_dex=491, home_id="00491_NORMAL_NONE"),
                build_entry(national_dex=492, home_id="00492_NORMAL_NONE"),
                build_entry(national_dex=492, home_id="00492_SKY_NONE"),
                build_entry(national_dex=493, home_id="00493_NORMAL_NONE"),
            ),
            rules,
        )
    )

    assert turtwig.obtainable_shiny is True
    assert manaphy.obtainable_shiny is True
    assert phione.obtainable_shiny is True
    assert darkrai.obtainable_shiny is False
    assert shaymin.obtainable_shiny is False
    assert sky_shaymin.obtainable_shiny is False
    assert arceus.obtainable_shiny is True


def test_sinnoh_catalog_documents_special_shiny_methods() -> None:
    """Special Sinnoh shiny routes must remain explicit and auditable."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    content = catalog_path.read_text(encoding="utf-8")

    assert "permanent Pokémon HOME gift" in content
    assert "Hall of Origin encounter" in content
    assert "limited-time Member Card" in content
    assert "limited-time Oak's Letter" in content


def test_unova_catalog_classifies_home_rewards_and_shiny_locked_mythicals() -> None:
    """Unova keeps permanent HOME rewards and excludes event-only mythicals."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    rules = ShinyAvailabilityRules.from_yaml(catalog_path)

    victini, keldeo, resolute_keldeo, meloetta, genesect = apply_shiny_availability(
        (
            build_entry(national_dex=494, home_id="00494_NORMAL_NONE"),
            build_entry(national_dex=647, home_id="00647_NORMAL_NONE"),
            build_entry(national_dex=647, home_id="00647_RESOLUTE_NONE"),
            build_entry(national_dex=648, home_id="00648_NORMAL_NONE"),
            build_entry(national_dex=649, home_id="00649_NORMAL_NONE"),
        ),
        rules,
    )

    assert victini.obtainable_shiny is False
    assert keldeo.obtainable_shiny is True
    assert resolute_keldeo.obtainable_shiny is True
    assert meloetta.obtainable_shiny is True
    assert genesect.obtainable_shiny is False


def test_unova_catalog_documents_permanent_home_rewards_and_exclusions() -> None:
    """Special Unova shiny routes must remain explicit and auditable."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    content = catalog_path.read_text(encoding="utf-8")

    assert "Galar, Isle of Armor, and Crown Tundra Pokédexes" in content
    assert "Paldea, Kitakami, and Blueberry Pokédexes" in content
    assert "Victini has no permanent legitimate shiny" in content
    assert "rotating/event Pokémon GO availability" in content
    assert "Pokémon GO is therefore not used" in content


def test_kalos_catalog_classifies_permanent_methods_and_exclusions() -> None:
    """Kalos keeps permanent methods and excludes unreleased/event-only forms."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    rules = ShinyAvailabilityRules.from_yaml(catalog_path)

    (
        chespin,
        eternal_floette,
        hisuian_goodra,
        zygarde,
        zygarde_10,
        diancie,
        hoopa,
        unbound_hoopa,
        volcanion,
    ) = apply_shiny_availability(
        (
            build_entry(national_dex=650, home_id="00650_NORMAL_NONE"),
            build_entry(national_dex=670, home_id="00670_ETERNAL_NONE"),
            build_entry(national_dex=706, home_id="00706_HISUI_NONE"),
            build_entry(national_dex=718, home_id="00718_NORMAL_NONE"),
            build_entry(national_dex=718, home_id="00718_10_NONE"),
            build_entry(national_dex=719, home_id="00719_NORMAL_NONE"),
            build_entry(national_dex=720, home_id="00720_NORMAL_NONE"),
            build_entry(national_dex=720, home_id="00720_UNBOUND_NONE"),
            build_entry(national_dex=721, home_id="00721_NORMAL_NONE"),
        ),
        rules,
    )

    assert chespin.obtainable_shiny is True
    assert eternal_floette.obtainable_shiny is False
    assert hisuian_goodra.obtainable_shiny is True
    assert zygarde.obtainable_shiny is True
    assert zygarde_10.obtainable_shiny is True
    assert diancie.obtainable_shiny is False
    assert hoopa.obtainable_shiny is False
    assert unbound_hoopa.obtainable_shiny is False
    assert volcanion.obtainable_shiny is True


def test_kalos_catalog_documents_home_reward_and_special_exclusions() -> None:
    """Special Kalos shiny decisions must remain explicit and auditable."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    content = catalog_path.read_text(encoding="utf-8")

    assert "permanent Dynamax Adventures encounters" in content
    assert "Lumiose, Hyperspace, and Mega Evolution Pokédexes" in content
    assert "Eternal Flower Floette has never been legitimately released" in content
    assert "permanent Legends: Z-A encounter is shiny-locked" in content
    assert "Hoopa has no permanent legitimate shiny" in content


def test_alola_catalog_classifies_permanent_methods_and_exclusions() -> None:
    """Alola keeps permanent hunts and excludes locked or event-only species."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    rules = ShinyAvailabilityRules.from_yaml(catalog_path)

    (
        rowlet,
        cosmog,
        solgaleo,
        lunala,
        necrozma,
        magearna,
        marshadow,
        zeraora,
        meltan,
        melmetal,
    ) = apply_shiny_availability(
        (
            build_entry(national_dex=722, home_id="00722_NORMAL_NONE"),
            build_entry(national_dex=789, home_id="00789_NORMAL_NONE"),
            build_entry(national_dex=791, home_id="00791_NORMAL_NONE"),
            build_entry(national_dex=792, home_id="00792_NORMAL_NONE"),
            build_entry(national_dex=800, home_id="00800_NORMAL_NONE"),
            build_entry(national_dex=801, home_id="00801_NORMAL_NONE"),
            build_entry(national_dex=802, home_id="00802_NORMAL_NONE"),
            build_entry(national_dex=807, home_id="00807_NORMAL_NONE"),
            build_entry(national_dex=808, home_id="00808_NORMAL_NONE"),
            build_entry(national_dex=809, home_id="00809_NORMAL_NONE"),
        ),
        rules,
    )

    assert rowlet.obtainable_shiny is True
    assert cosmog.obtainable_shiny is False
    assert solgaleo.obtainable_shiny is True
    assert lunala.obtainable_shiny is True
    assert necrozma.obtainable_shiny is True
    assert magearna.obtainable_shiny is False
    assert marshadow.obtainable_shiny is False
    assert zeraora.obtainable_shiny is False
    assert meltan.obtainable_shiny is True
    assert melmetal.obtainable_shiny is False


def test_alola_catalog_documents_home_reward_and_event_exclusions() -> None:
    """Special Alola shiny decisions must remain explicit and auditable."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    content = catalog_path.read_text(encoding="utf-8")

    assert "permanent Pokémon HOME Pokédex-completion reward" in content
    assert "Pokémon received in HOME cannot be transferred back to GO" in content
    assert (
        "Solgaleo and\n  # Lunala remain included through permanent Dynamax Adventures"
        in content
    )
    assert "time-limited Pokémon HOME Mystery" in content
    assert "Shiny Melmetal requires evolving Shiny Meltan in Pokémon GO" in content


def test_galar_hisui_catalog_classifies_permanent_methods_and_exclusions() -> None:
    """Galar and Hisui keep permanent hunts and exclude locked species."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    rules = ShinyAvailabilityRules.from_yaml(catalog_path)

    (
        grookey,
        zacian,
        eternatus,
        kubfu,
        single_strike_urshifu,
        dada_zarude,
        regieleki,
        glastrier,
        shadow_rider_calyrex,
        wyrdeer,
        enamorus,
    ) = apply_shiny_availability(
        (
            build_entry(national_dex=810, home_id="00810_NORMAL_NONE"),
            build_entry(national_dex=888, home_id="00888_NORMAL_NONE"),
            build_entry(national_dex=890, home_id="00890_NORMAL_NONE"),
            build_entry(national_dex=891, home_id="00891_NORMAL_NONE"),
            build_entry(national_dex=892, home_id="00892_SINGLE_STRIKE_NONE"),
            build_entry(national_dex=893, home_id="00893_DADA_NONE"),
            build_entry(national_dex=894, home_id="00894_NORMAL_NONE"),
            build_entry(national_dex=896, home_id="00896_NORMAL_NONE"),
            build_entry(national_dex=898, home_id="00898_SHADOW_NONE"),
            build_entry(national_dex=899, home_id="00899_NORMAL_NONE"),
            build_entry(national_dex=905, home_id="00905_NORMAL_NONE"),
        ),
        rules,
    )

    assert grookey.obtainable_shiny is True
    assert zacian.obtainable_shiny is False
    assert eternatus.obtainable_shiny is False
    assert kubfu.obtainable_shiny is False
    assert single_strike_urshifu.obtainable_shiny is False
    assert dada_zarude.obtainable_shiny is False
    assert regieleki.obtainable_shiny is True
    assert glastrier.obtainable_shiny is False
    assert shadow_rider_calyrex.obtainable_shiny is False
    assert wyrdeer.obtainable_shiny is True
    assert enamorus.obtainable_shiny is True


def test_galar_hisui_catalog_documents_home_reward_and_shiny_locks() -> None:
    """Special Galar and Hisui decisions must remain explicit and auditable."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    content = catalog_path.read_text(encoding="utf-8")

    assert "Regieleki and Regidrago remain included" in content
    assert "permanent Pokémon HOME gift for completing the Hisui Pokédex" in content
    assert "limited-time shiny" in content
    assert "briefly shiny raid-boss Urshifu" in content
    assert "Calyrex are shiny-locked" in content


def test_paldea_dlc_catalog_classifies_permanent_methods_and_exclusions() -> None:
    """Generation IX keeps ordinary shiny hunts and excludes event-only locks."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    rules = ShinyAvailabilityRules.from_yaml(catalog_path)

    (
        sprigatito,
        family_three_maushold,
        shiny_gimmighoul,
        gholdengo,
        wo_chien,
        koraidon,
        miraidon_drive,
        walking_wake,
        dipplin,
        okidogi,
        ogerpon,
        archaludon,
        gouging_fire,
        terapagos,
        pecharunt,
    ) = apply_shiny_availability(
        (
            build_entry(national_dex=906, home_id="00906_NORMAL_NONE"),
            build_entry(national_dex=925, home_id="00925_FAMILY_OF_THREE_NONE"),
            build_entry(national_dex=999, home_id="00999_NORMAL_NONE"),
            build_entry(national_dex=1000, home_id="01000_NORMAL_NONE"),
            build_entry(national_dex=1001, home_id="01001_NORMAL_NONE"),
            build_entry(national_dex=1007, home_id="01007_NORMAL_NONE"),
            build_entry(national_dex=1008, home_id="01008_DRIVE_MODE_NONE"),
            build_entry(national_dex=1009, home_id="01009_NORMAL_NONE"),
            build_entry(national_dex=1011, home_id="01011_NORMAL_NONE"),
            build_entry(national_dex=1014, home_id="01014_NORMAL_NONE"),
            build_entry(national_dex=1017, home_id="01017_NORMAL_NONE"),
            build_entry(national_dex=1018, home_id="01018_NORMAL_NONE"),
            build_entry(national_dex=1020, home_id="01020_NORMAL_NONE"),
            build_entry(national_dex=1024, home_id="01024_NORMAL_NONE"),
            build_entry(national_dex=1025, home_id="01025_NORMAL_NONE"),
        ),
        rules,
    )

    assert sprigatito.obtainable_shiny is True
    assert family_three_maushold.obtainable_shiny is True
    assert shiny_gimmighoul.obtainable_shiny is True
    assert gholdengo.obtainable_shiny is True
    assert wo_chien.obtainable_shiny is False
    assert koraidon.obtainable_shiny is False
    assert miraidon_drive.obtainable_shiny is False
    assert walking_wake.obtainable_shiny is False
    assert dipplin.obtainable_shiny is True
    assert okidogi.obtainable_shiny is False
    assert ogerpon.obtainable_shiny is False
    assert archaludon.obtainable_shiny is True
    assert gouging_fire.obtainable_shiny is False
    assert terapagos.obtainable_shiny is False
    assert pecharunt.obtainable_shiny is False


def test_paldea_dlc_catalog_documents_event_only_and_shiny_locked_species() -> None:
    """Generation IX exclusions must remain explicit and auditable."""
    catalog_path = (
        Path(__file__).resolve().parents[1] / "data" / "shiny_availability.yaml"
    )
    content = catalog_path.read_text(encoding="utf-8")

    assert "Treasures of Ruin received shiny distributions" in content
    assert "limited 2025 serial-code" in content
    assert "Walking Wake, Iron Leaves, the Loyal Three, Ogerpon" in content
    assert "Terapagos, and Pecharunt have no permanent" in content
