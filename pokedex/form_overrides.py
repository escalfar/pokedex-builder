from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import yaml

from pokedex.exceptions import ConfigurationError, ValidationError
from pokedex.models import PokemonVariant
from pokedex.variants import sort_pokemon_variants


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
    """Collection of regional and exact variant corrections."""

    regional_forms: dict[str, RegionalFormOverride]
    forms: dict[str, FormOverride]

    @classmethod
    def from_yaml(cls, path: Path) -> FormOverrides:
        """Load variant overrides from YAML."""
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
    variants: tuple[PokemonVariant, ...],
    overrides: FormOverrides,
) -> tuple[PokemonVariant, ...]:
    """Apply exact and regional corrections to variants."""
    normalized = tuple(normalize_variant(variant, overrides) for variant in variants)

    ordered = sort_pokemon_variants(normalized)

    validate_normalized_variants(ordered)

    return ordered


def normalize_variant(
    variant: PokemonVariant,
    overrides: FormOverrides,
) -> PokemonVariant:
    """Return a variant with corrected naming and generation."""
    if variant.is_default:
        return variant

    exact_override = overrides.forms.get(variant.variety_api_name.casefold())

    if exact_override is not None:
        return _apply_exact_override(
            variant,
            exact_override,
        )

    regional_override = _find_regional_override(
        variant,
        overrides,
    )

    if regional_override is not None:
        return _apply_regional_override(
            variant,
            regional_override,
        )

    return variant


def _apply_exact_override(
    variant: PokemonVariant,
    override: FormOverride,
) -> PokemonVariant:
    return replace(
        variant,
        form_name=(override.form_name or variant.form_name),
        display_name=(override.display_name or variant.display_name),
        generation=(override.generation or variant.generation),
    )


def _apply_regional_override(
    variant: PokemonVariant,
    override: RegionalFormOverride,
) -> PokemonVariant:
    return replace(
        variant,
        form_name=override.form_name,
        display_name=(f"{override.form_name} {variant.pokemon}"),
        generation=override.generation,
    )


def _find_regional_override(
    variant: PokemonVariant,
    overrides: FormOverrides,
) -> RegionalFormOverride | None:
    slug_parts = variant.form_slug.casefold().split("-")

    for regional_slug, override in overrides.regional_forms.items():
        if regional_slug in slug_parts:
            return override

    return None


def validate_normalized_variants(
    variants: tuple[PokemonVariant, ...],
) -> None:
    """Validate uniqueness after applying corrections."""
    names: dict[str, list[str]] = {}

    for variant in variants:
        normalized_name = variant.display_name.casefold()

        names.setdefault(
            normalized_name,
            [],
        ).append(variant.home_id)

    duplicated_names = {
        name: home_ids for name, home_ids in names.items() if len(home_ids) > 1
    }

    if duplicated_names:
        details = "; ".join(
            f"{name}: {', '.join(home_ids)}"
            for name, home_ids in sorted(duplicated_names.items())
        )

        raise ValidationError(
            "Duplicate normalized Pokémon variant names found: " f"{details}"
        )


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

        if display_name is not None and not isinstance(display_name, str):
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
