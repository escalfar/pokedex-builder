from pathlib import Path

import pytest

from pokedex.constants import Gender
from pokedex.exceptions import ConfigurationError, ValidationError
from pokedex.gender_differences import (
    GenderDifferenceRules,
    SourceGenderVariety,
    expand_gender_differences,
)
from pokedex.models import PokemonVariant


def build_variant(
    *,
    national_dex: int = 25,
    pokemon: str = "Pikachu",
    variety_api_name: str = "pikachu",
    form_slug: str = "normal",
    form_name: str = "Normal",
    display_name: str = "Pikachu",
    generation: int = 1,
    is_default: bool = True,
    gender: Gender = Gender.NONE,
) -> PokemonVariant:
    return PokemonVariant(
        national_dex=national_dex,
        pokemon=pokemon,
        species_api_name=pokemon.casefold().replace(" ", "-"),
        variety_api_name=variety_api_name,
        form_slug=form_slug,
        form_name=form_name,
        display_name=display_name,
        generation=generation,
        resource_url=f"https://example.com/pokemon/{variety_api_name}",
        is_default=is_default,
        gender=gender,
    )


def build_rules(
    *,
    forms_by_dex: dict[int, frozenset[str]] | None = None,
    source_gender_varieties: dict[str, SourceGenderVariety] | None = None,
) -> GenderDifferenceRules:
    return GenderDifferenceRules(
        forms_by_dex=forms_by_dex or {},
        source_gender_varieties=source_gender_varieties or {},
    )


def test_expand_normal_variant_female_first() -> None:
    variants = expand_gender_differences(
        (build_variant(),),
        build_rules(forms_by_dex={25: frozenset({"normal"})}),
    )

    assert [variant.gender for variant in variants] == [
        Gender.FEMALE,
        Gender.MALE,
    ]
    assert [variant.form_name for variant in variants] == ["Female", "Male"]
    assert [variant.display_name for variant in variants] == [
        "Female Pikachu",
        "Male Pikachu",
    ]
    assert [variant.home_id for variant in variants] == [
        "00025_NORMAL_FEMALE",
        "00025_NORMAL_MALE",
    ]


def test_expand_regional_variant_preserves_form_name() -> None:
    hisuian = build_variant(
        national_dex=215,
        pokemon="Sneasel",
        variety_api_name="sneasel-hisui",
        form_slug="hisui",
        form_name="Hisuian",
        display_name="Hisuian Sneasel",
        generation=8,
        is_default=False,
    )
    normal = build_variant(
        national_dex=215,
        pokemon="Sneasel",
        variety_api_name="sneasel",
        display_name="Sneasel",
    )

    variants = expand_gender_differences(
        (normal, hisuian),
        build_rules(forms_by_dex={215: frozenset({"normal", "hisui"})}),
    )

    assert [variant.display_name for variant in variants] == [
        "Female Sneasel",
        "Male Sneasel",
        "Female Hisuian Sneasel",
        "Male Hisuian Sneasel",
    ]
    assert [variant.form_name for variant in variants] == [
        "Female",
        "Male",
        "Hisuian Female",
        "Hisuian Male",
    ]


def test_unlisted_regional_form_remains_ungendered() -> None:
    normal = build_variant(
        national_dex=26,
        pokemon="Raichu",
        variety_api_name="raichu",
        display_name="Raichu",
    )
    alolan = build_variant(
        national_dex=26,
        pokemon="Raichu",
        variety_api_name="raichu-alola",
        form_slug="alola",
        form_name="Alolan",
        display_name="Alolan Raichu",
        generation=7,
        is_default=False,
    )

    variants = expand_gender_differences(
        (normal, alolan),
        build_rules(forms_by_dex={26: frozenset({"normal"})}),
    )

    assert [variant.home_id for variant in variants] == [
        "00026_NORMAL_FEMALE",
        "00026_NORMAL_MALE",
        "00026_ALOLA_NONE",
    ]


def test_source_gender_varieties_are_normalized() -> None:
    male = build_variant(
        national_dex=678,
        pokemon="Meowstic",
        variety_api_name="meowstic-male",
        display_name="Meowstic",
    )
    female = build_variant(
        national_dex=678,
        pokemon="Meowstic",
        variety_api_name="meowstic-female",
        form_slug="female",
        form_name="Female",
        display_name="Female Meowstic",
        is_default=False,
    )
    rules = build_rules(
        forms_by_dex={678: frozenset({"normal"})},
        source_gender_varieties={
            "meowstic-male": SourceGenderVariety(Gender.MALE, "normal"),
            "meowstic-female": SourceGenderVariety(Gender.FEMALE, "normal"),
        },
    )

    variants = expand_gender_differences((male, female), rules)

    assert [variant.home_id for variant in variants] == [
        "00678_NORMAL_FEMALE",
        "00678_NORMAL_MALE",
    ]
    assert [variant.display_name for variant in variants] == [
        "Female Meowstic",
        "Male Meowstic",
    ]


def test_default_source_variety_can_represent_male_gender() -> None:
    # PokéAPI names the male default varieties simply ``frillish``,
    # ``jellicent`` and ``pyroar`` instead of using a ``-male`` suffix.
    male = build_variant(
        national_dex=592,
        pokemon="Frillish",
        variety_api_name="frillish",
        display_name="Frillish",
    )
    female = build_variant(
        national_dex=592,
        pokemon="Frillish",
        variety_api_name="frillish-female",
        form_slug="female",
        form_name="Female",
        display_name="Female Frillish",
        is_default=False,
    )
    rules = build_rules(
        forms_by_dex={592: frozenset({"normal"})},
        source_gender_varieties={
            "frillish": SourceGenderVariety(Gender.MALE, "normal"),
            "frillish-female": SourceGenderVariety(Gender.FEMALE, "normal"),
        },
    )

    variants = expand_gender_differences((male, female), rules)

    assert [variant.home_id for variant in variants] == [
        "00592_NORMAL_FEMALE",
        "00592_NORMAL_MALE",
    ]


def test_missing_configured_form_is_rejected() -> None:
    normal = build_variant(
        national_dex=215,
        pokemon="Sneasel",
        variety_api_name="sneasel",
        display_name="Sneasel",
    )

    with pytest.raises(
        ValidationError,
        match="Configured gender-difference forms are missing",
    ):
        expand_gender_differences(
            (normal,),
            build_rules(forms_by_dex={215: frozenset({"normal", "hisui"})}),
        )


def test_load_gender_rules(tmp_path: Path) -> None:
    path = tmp_path / "gender.yaml"
    path.write_text(
        """
gender_differences:
  25: [normal]
source_gender_varieties:
  meowstic-female:
    gender: female
    form_slug: normal
""".strip(),
        encoding="utf-8",
    )

    rules = GenderDifferenceRules.from_yaml(path)

    assert rules.forms_by_dex[25] == frozenset({"normal"})
    assert rules.source_gender_varieties["meowstic-female"] == (
        SourceGenderVariety(Gender.FEMALE, "normal")
    )


def test_load_gender_rules_rejects_invalid_gender(tmp_path: Path) -> None:
    path = tmp_path / "gender.yaml"
    path.write_text(
        """
gender_differences: {}
source_gender_varieties:
  meowstic-female:
    gender: unknown
    form_slug: normal
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="invalid gender"):
        GenderDifferenceRules.from_yaml(path)
