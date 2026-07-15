from pathlib import Path

import pytest

from pokedex.exceptions import ConfigurationError, ValidationError
from pokedex.form_rules import (
    FormRules,
    evaluate_candidate,
    filter_variety_candidates,
)
from pokedex.varieties import VarietyCandidate


def build_candidate(
    *,
    national_dex: int = 6,
    species_api_name: str = "charizard",
    variety_api_name: str = "charizard",
    form_slug: str = "normal",
    is_default: bool = True,
) -> VarietyCandidate:
    return VarietyCandidate(
        national_dex=national_dex,
        pokemon="Charizard",
        species_api_name=species_api_name,
        variety_api_name=variety_api_name,
        form_slug=form_slug,
        form_name=form_slug.replace("-", " ").title(),
        display_name="Charizard",
        generation=1,
        resource_url=(
            "https://pokeapi.co/api/v2/"
            f"pokemon/{national_dex}/"
            f"{variety_api_name}"
        ),
        is_default=is_default,
        home_id=(f"{national_dex:05d}_" f"{form_slug.replace('-', '_').upper()}"),
    )


def write_rules(path: Path) -> None:
    path.write_text(
        """
version: "1.0"
exclude:
  exact_slugs:
    - battle-bond
  slug_prefixes:
    - mega
  slug_suffixes:
    - gmax
  api_name_contains:
    - "-totem"
  species_single_row:
    - arceus
  excluded_api_names:
    - floette-eternal
""".strip(),
        encoding="utf-8",
    )


def test_load_form_rules(tmp_path: Path) -> None:
    path = tmp_path / "form_rules.yaml"
    write_rules(path)

    rules = FormRules.from_yaml(path)

    assert "battle-bond" in rules.exact_slugs
    assert rules.slug_prefixes == ("mega",)
    assert "arceus" in rules.species_single_row


def test_load_form_rules_rejects_missing_file(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ConfigurationError,
        match="does not exist",
    ):
        FormRules.from_yaml(tmp_path / "missing.yaml")


def test_default_candidate_is_included() -> None:
    rules = FormRules(
        exact_slugs=frozenset({"normal"}),
        slug_prefixes=(),
        slug_suffixes=(),
        api_name_contains=(),
        species_single_row=frozenset(),
        excluded_api_names=frozenset(),
    )
    candidate = build_candidate()

    result = evaluate_candidate(candidate, rules)

    assert result.excluded is False


def test_excludes_exact_slug() -> None:
    rules = FormRules(
        exact_slugs=frozenset({"battle-bond"}),
        slug_prefixes=(),
        slug_suffixes=(),
        api_name_contains=(),
        species_single_row=frozenset(),
        excluded_api_names=frozenset(),
    )
    candidate = build_candidate(
        variety_api_name="greninja-battle-bond",
        form_slug="battle-bond",
        is_default=False,
    )

    result = evaluate_candidate(candidate, rules)

    assert result.excluded is True
    assert result.reason is not None


def test_excludes_species_configured_as_single_row() -> None:
    rules = FormRules(
        exact_slugs=frozenset(),
        slug_prefixes=(),
        slug_suffixes=(),
        api_name_contains=(),
        species_single_row=frozenset({"arceus"}),
        excluded_api_names=frozenset(),
    )
    candidate = build_candidate(
        national_dex=493,
        species_api_name="arceus",
        variety_api_name="arceus-fire",
        form_slug="fire",
        is_default=False,
    )

    result = evaluate_candidate(candidate, rules)

    assert result.excluded is True


def test_filter_preserves_default_candidate() -> None:
    rules = FormRules(
        exact_slugs=frozenset({"mega-x"}),
        slug_prefixes=(),
        slug_suffixes=(),
        api_name_contains=(),
        species_single_row=frozenset(),
        excluded_api_names=frozenset(),
    )

    normal = build_candidate()
    mega = build_candidate(
        variety_api_name="charizard-mega-x",
        form_slug="mega-x",
        is_default=False,
    )

    filtered = filter_variety_candidates(
        (normal, mega),
        rules,
    )

    assert filtered == (normal,)


def test_filter_rejects_when_species_disappears() -> None:
    rules = FormRules(
        exact_slugs=frozenset({"special"}),
        slug_prefixes=(),
        slug_suffixes=(),
        api_name_contains=(),
        species_single_row=frozenset(),
        excluded_api_names=frozenset(),
    )

    candidate = build_candidate(
        form_slug="special",
        is_default=False,
    )

    with pytest.raises(
        ValidationError,
        match="All variety candidates were excluded",
    ):
        filter_variety_candidates(
            (candidate,),
            rules,
        )
