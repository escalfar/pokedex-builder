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
