from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import yaml

from pokedex.exceptions import ConfigurationError, ValidationError
from pokedex.varieties import VarietyCandidate


@dataclass(frozen=True, slots=True)
class RegionalFormOverride:
    """Shared naming and generation rules for a regional form."""

    form_name: str
    generation: int

    def __post_init__(self) -> None:
        if not self.form_name.strip():
            raise ValueError("Regional form name cannot be empty.")

        if self.generation <= 0:
            raise ValueError("Regional form generation must be positive.")


@dataclass(frozen=True, slots=True)
class FormOverride:
    """Corrections applied to one specific PokéAPI variety."""

    form_name: str | None = None
    display_name: str | None = None
    generation: int | None = None

    def __post_init__(self) -> None:
        if self.form_name is not None and not self.form_name.strip():
            raise ValueError("Override form name cannot be empty.")

        if self.display_name is not None and not self.display_name.strip():
            raise ValueError("Override display name cannot be empty.")

        if self.generation is not None and self.generation <= 0:
            raise ValueError("Override generation must be positive.")


@dataclass(frozen=True, slots=True)
class FormOverrides:
    """Collection of regional and exact form corrections."""

    regional_forms: dict[str, RegionalFormOverride]
    forms: dict[str, FormOverride]

    @classmethod
    def from_yaml(cls, path: Path) -> FormOverrides:
        """Load form overrides from a YAML file."""
        if not path.is_file():
            raise ConfigurationError(f"Form overrides file does not exist: {path}")

        try:
            with path.open("r", encoding="utf-8") as file:
                payload: Any = yaml.safe_load(file)
        except (OSError, yaml.YAMLError) as error:
            raise ConfigurationError(
                f"Unable to load form overrides: {path}"
            ) from error

        if not isinstance(payload, dict):
            raise ConfigurationError("Form overrides must contain a YAML object.")

        return cls(
            regional_forms=_parse_regional_forms(payload.get("regional_forms", {})),
            forms=_parse_form_overrides(payload.get("forms", {})),
        )


def apply_form_overrides(
    candidates: tuple[VarietyCandidate, ...],
    overrides: FormOverrides,
) -> tuple[VarietyCandidate, ...]:
    """Apply exact and regional corrections to variety candidates."""
    normalized = tuple(
        normalize_candidate(candidate, overrides) for candidate in candidates
    )

    validate_normalized_candidates(normalized)

    return normalized


def normalize_candidate(
    candidate: VarietyCandidate,
    overrides: FormOverrides,
) -> VarietyCandidate:
    """Return a candidate with corrected naming and generation."""
    if candidate.is_default:
        return candidate

    exact_override = overrides.forms.get(candidate.variety_api_name.casefold())

    if exact_override is not None:
        return _apply_exact_override(
            candidate,
            exact_override,
        )

    regional_override = _find_regional_override(
        candidate,
        overrides,
    )

    if regional_override is not None:
        return _apply_regional_override(
            candidate,
            regional_override,
        )

    return candidate


def _apply_exact_override(
    candidate: VarietyCandidate,
    override: FormOverride,
) -> VarietyCandidate:
    form_name = override.form_name or candidate.form_name
    display_name = override.display_name or candidate.display_name
    generation = override.generation or candidate.generation

    return replace(
        candidate,
        form_name=form_name,
        display_name=display_name,
        generation=generation,
    )


def _apply_regional_override(
    candidate: VarietyCandidate,
    override: RegionalFormOverride,
) -> VarietyCandidate:
    display_name = f"{override.form_name} {candidate.pokemon}"

    return replace(
        candidate,
        form_name=override.form_name,
        display_name=display_name,
        generation=override.generation,
    )


def _find_regional_override(
    candidate: VarietyCandidate,
    overrides: FormOverrides,
) -> RegionalFormOverride | None:
    slug_parts = candidate.form_slug.casefold().split("-")

    for regional_slug, override in overrides.regional_forms.items():
        if regional_slug in slug_parts:
            return override

    return None


def validate_normalized_candidates(
    candidates: tuple[VarietyCandidate, ...],
) -> None:
    """Validate uniqueness after applying naming corrections."""
    names: dict[str, list[str]] = {}

    for candidate in candidates:
        normalized_name = candidate.display_name.casefold()
        names.setdefault(normalized_name, []).append(candidate.home_id)

    duplicated_names = {
        name: home_ids for name, home_ids in names.items() if len(home_ids) > 1
    }

    if duplicated_names:
        details = "; ".join(
            f"{name}: {', '.join(home_ids)}"
            for name, home_ids in sorted(duplicated_names.items())
        )
        raise ValidationError(f"Duplicate normalized Pokémon names found: {details}")


def _parse_regional_forms(
    payload: object,
) -> dict[str, RegionalFormOverride]:
    if not isinstance(payload, dict):
        raise ConfigurationError("'regional_forms' must contain a YAML object.")

    result: dict[str, RegionalFormOverride] = {}

    for raw_slug, raw_override in payload.items():
        if not isinstance(raw_slug, str):
            raise ConfigurationError("Regional form keys must be strings.")

        if not isinstance(raw_override, dict):
            raise ConfigurationError(f"Regional form '{raw_slug}' must be an object.")

        form_name = raw_override.get("form_name")
        generation = raw_override.get("generation")

        if not isinstance(form_name, str):
            raise ConfigurationError(f"Regional form '{raw_slug}' requires form_name.")

        if not isinstance(generation, int):
            raise ConfigurationError(f"Regional form '{raw_slug}' requires generation.")

        result[raw_slug.casefold()] = RegionalFormOverride(
            form_name=form_name,
            generation=generation,
        )

    return result


def _parse_form_overrides(
    payload: object,
) -> dict[str, FormOverride]:
    if not isinstance(payload, dict):
        raise ConfigurationError("'forms' must contain a YAML object.")

    result: dict[str, FormOverride] = {}

    for raw_api_name, raw_override in payload.items():
        if not isinstance(raw_api_name, str):
            raise ConfigurationError("Form override keys must be strings.")

        if not isinstance(raw_override, dict):
            raise ConfigurationError(
                f"Form override '{raw_api_name}' must be an object."
            )

        form_name = raw_override.get("form_name")
        display_name = raw_override.get("display_name")
        generation = raw_override.get("generation")

        if form_name is not None and not isinstance(form_name, str):
            raise ConfigurationError(
                f"Override '{raw_api_name}' has invalid form_name."
            )

        if display_name is not None and not isinstance(
            display_name,
            str,
        ):
            raise ConfigurationError(
                f"Override '{raw_api_name}' has invalid display_name."
            )

        if generation is not None and not isinstance(generation, int):
            raise ConfigurationError(
                f"Override '{raw_api_name}' has invalid generation."
            )

        result[raw_api_name.casefold()] = FormOverride(
            form_name=form_name,
            display_name=display_name,
            generation=generation,
        )

    return result
