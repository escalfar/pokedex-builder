from pathlib import Path

import pytest

from pokedex.exceptions import ConfigurationError, ValidationError
from pokedex.form_overrides import (
    FormOverride,
    FormOverrides,
    RegionalFormOverride,
    apply_form_overrides,
    normalize_candidate,
)
from pokedex.varieties import VarietyCandidate


def build_candidate(
    *,
    variety_api_name: str = "raichu-alola",
    form_slug: str = "alola",
    form_name: str = "Alola",
    display_name: str = "Alola Raichu",
    generation: int = 1,
    is_default: bool = False,
    home_id: str = "00026_ALOLA",
) -> VarietyCandidate:
    return VarietyCandidate(
        national_dex=26,
        pokemon="Raichu",
        species_api_name="raichu",
        variety_api_name=variety_api_name,
        form_slug=form_slug,
        form_name=form_name,
        display_name=display_name,
        generation=generation,
        resource_url=("https://pokeapi.co/api/v2/" f"pokemon/{variety_api_name}/"),
        is_default=is_default,
        home_id=home_id,
    )


def test_regional_override_updates_name_and_generation() -> None:
    overrides = FormOverrides(
        regional_forms={
            "alola": RegionalFormOverride(
                form_name="Alolan",
                generation=7,
            )
        },
        forms={},
    )

    result = normalize_candidate(
        build_candidate(),
        overrides,
    )

    assert result.form_name == "Alolan"
    assert result.display_name == "Alolan Raichu"
    assert result.generation == 7


def test_exact_override_has_priority() -> None:
    overrides = FormOverrides(
        regional_forms={
            "alola": RegionalFormOverride(
                form_name="Alolan",
                generation=7,
            )
        },
        forms={
            "raichu-alola": FormOverride(
                form_name="Special Alolan",
                display_name="Special Alolan Raichu",
                generation=9,
            )
        },
    )

    result = normalize_candidate(
        build_candidate(),
        overrides,
    )

    assert result.form_name == "Special Alolan"
    assert result.display_name == "Special Alolan Raichu"
    assert result.generation == 9


def test_default_candidate_is_not_modified() -> None:
    candidate = build_candidate(
        variety_api_name="raichu",
        form_slug="normal",
        form_name="Normal",
        display_name="Raichu",
        generation=1,
        is_default=True,
        home_id="00026_NORMAL",
    )

    overrides = FormOverrides(
        regional_forms={
            "normal": RegionalFormOverride(
                form_name="Changed",
                generation=9,
            )
        },
        forms={
            "raichu": FormOverride(
                display_name="Changed Raichu",
            )
        },
    )

    result = normalize_candidate(
        candidate,
        overrides,
    )

    assert result == candidate


def test_apply_form_overrides_rejects_duplicate_names() -> None:
    first = build_candidate(
        variety_api_name="raichu-alola",
        home_id="00026_ALOLA",
    )
    second = build_candidate(
        variety_api_name="raichu-special",
        form_slug="special",
        home_id="00026_SPECIAL",
    )

    overrides = FormOverrides(
        regional_forms={},
        forms={
            "raichu-alola": FormOverride(
                display_name="Duplicate Raichu",
            ),
            "raichu-special": FormOverride(
                display_name="Duplicate Raichu",
            ),
        },
    )

    with pytest.raises(
        ValidationError,
        match="Duplicate normalized Pokémon names",
    ):
        apply_form_overrides(
            (first, second),
            overrides,
        )


def test_load_form_overrides(tmp_path: Path) -> None:
    path = tmp_path / "form_overrides.yaml"
    path.write_text(
        """
version: "1.0"
regional_forms:
  alola:
    form_name: "Alolan"
    generation: 7
forms:
  raichu-alola:
    form_name: "Alolan"
    display_name: "Alolan Raichu"
    generation: 7
""".strip(),
        encoding="utf-8",
    )

    overrides = FormOverrides.from_yaml(path)

    assert overrides.regional_forms["alola"].generation == 7
    assert overrides.forms["raichu-alola"].display_name == "Alolan Raichu"


def test_load_form_overrides_rejects_missing_file(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ConfigurationError,
        match="does not exist",
    ):
        FormOverrides.from_yaml(tmp_path / "missing.yaml")
