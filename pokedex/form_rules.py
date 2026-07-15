from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from pokedex.exceptions import ConfigurationError, ValidationError
from pokedex.varieties import VarietyCandidate


@dataclass(frozen=True, slots=True)
class FormRules:
    """Validated inclusion and exclusion rules for Pokémon forms."""

    exact_slugs: frozenset[str]
    slug_prefixes: tuple[str, ...]
    slug_suffixes: tuple[str, ...]
    api_name_contains: tuple[str, ...]
    species_single_row: frozenset[str]
    excluded_api_names: frozenset[str]

    @classmethod
    def from_yaml(cls, path: Path) -> FormRules:
        """Load and validate form rules from a YAML file."""
        if not path.is_file():
            raise ConfigurationError(f"Form rules file does not exist: {path}")

        try:
            with path.open("r", encoding="utf-8") as file:
                payload: Any = yaml.safe_load(file)
        except (OSError, yaml.YAMLError) as error:
            raise ConfigurationError(f"Unable to load form rules: {path}") from error

        if not isinstance(payload, dict):
            raise ConfigurationError("Form rules must contain a YAML object.")

        exclusion_payload = payload.get("exclude")

        if not isinstance(exclusion_payload, dict):
            raise ConfigurationError("Form rules must contain an 'exclude' object.")

        return cls(
            exact_slugs=_read_string_set(
                exclusion_payload,
                "exact_slugs",
            ),
            slug_prefixes=_read_string_tuple(
                exclusion_payload,
                "slug_prefixes",
            ),
            slug_suffixes=_read_string_tuple(
                exclusion_payload,
                "slug_suffixes",
            ),
            api_name_contains=_read_string_tuple(
                exclusion_payload,
                "api_name_contains",
            ),
            species_single_row=_read_string_set(
                exclusion_payload,
                "species_single_row",
            ),
            excluded_api_names=_read_string_set(
                exclusion_payload,
                "excluded_api_names",
            ),
        )


@dataclass(frozen=True, slots=True)
class ExclusionResult:
    """Result of evaluating a variety candidate against form rules."""

    excluded: bool
    reason: str | None = None


def evaluate_candidate(
    candidate: VarietyCandidate,
    rules: FormRules,
) -> ExclusionResult:
    """Determine whether a candidate must be excluded."""
    api_name = candidate.variety_api_name.casefold()
    species_name = candidate.species_api_name.casefold()
    form_slug = candidate.form_slug.casefold()

    if candidate.is_default:
        return ExclusionResult(excluded=False)

    if species_name in rules.species_single_row:
        return ExclusionResult(
            excluded=True,
            reason="Species configured to use a single row.",
        )

    if api_name in rules.excluded_api_names:
        return ExclusionResult(
            excluded=True,
            reason="API name explicitly excluded.",
        )

    if form_slug in rules.exact_slugs:
        return ExclusionResult(
            excluded=True,
            reason=f"Form slug explicitly excluded: {form_slug}",
        )

    if any(form_slug.startswith(prefix) for prefix in rules.slug_prefixes):
        return ExclusionResult(
            excluded=True,
            reason=f"Form slug uses an excluded prefix: {form_slug}",
        )

    if any(form_slug.endswith(suffix) for suffix in rules.slug_suffixes):
        return ExclusionResult(
            excluded=True,
            reason=f"Form slug uses an excluded suffix: {form_slug}",
        )

    if any(fragment in api_name for fragment in rules.api_name_contains):
        return ExclusionResult(
            excluded=True,
            reason=f"API name contains an excluded fragment: {api_name}",
        )

    return ExclusionResult(excluded=False)


def filter_variety_candidates(
    candidates: tuple[VarietyCandidate, ...],
    rules: FormRules,
) -> tuple[VarietyCandidate, ...]:
    """Remove excluded candidates while preserving deterministic order."""
    included = tuple(
        candidate
        for candidate in candidates
        if not evaluate_candidate(candidate, rules).excluded
    )

    if not included:
        raise ValidationError("All variety candidates were excluded by the form rules.")

    _validate_each_species_is_represented(
        original=candidates,
        filtered=included,
    )

    return included


def _validate_each_species_is_represented(
    *,
    original: tuple[VarietyCandidate, ...],
    filtered: tuple[VarietyCandidate, ...],
) -> None:
    original_species = {candidate.national_dex for candidate in original}
    filtered_species = {candidate.national_dex for candidate in filtered}

    missing_species = sorted(original_species - filtered_species)

    if missing_species:
        values = ", ".join(str(value) for value in missing_species)
        raise ValidationError(
            "Form rules removed every candidate for National Dex: " f"{values}"
        )


def _read_string_set(
    payload: dict[str, Any],
    key: str,
) -> frozenset[str]:
    return frozenset(_read_strings(payload, key))


def _read_string_tuple(
    payload: dict[str, Any],
    key: str,
) -> tuple[str, ...]:
    return tuple(_read_strings(payload, key))


def _read_strings(
    payload: dict[str, Any],
    key: str,
) -> list[str]:
    value = payload.get(key, [])

    if not isinstance(value, list):
        raise ConfigurationError(f"Form rule '{key}' must contain a YAML list.")

    normalized: list[str] = []

    for item in value:
        if not isinstance(item, str):
            raise ConfigurationError(f"Form rule '{key}' may contain only strings.")

        cleaned = item.strip().casefold()

        if not cleaned:
            raise ConfigurationError(f"Form rule '{key}' may not contain empty values.")

        normalized.append(cleaned)

    return normalized
