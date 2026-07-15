from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import yaml

from pokedex.constants import Gender
from pokedex.exceptions import ConfigurationError, ValidationError
from pokedex.models import PokemonVariant
from pokedex.variants import sort_pokemon_variants, validate_pokemon_variants


@dataclass(frozen=True, slots=True)
class SourceGenderVariety:
    """How a gender-specific PokéAPI variety maps to project dimensions."""

    gender: Gender
    form_slug: str

    def __post_init__(self) -> None:
        if self.gender is Gender.NONE:
            raise ValueError("Source gender variety must use Female or Male.")
        if not self.form_slug.strip():
            raise ValueError("Source gender variety form slug cannot be empty.")


@dataclass(frozen=True, slots=True)
class GenderDifferenceRules:
    """Catalog of forms whose appearances differ by gender."""

    forms_by_dex: dict[int, frozenset[str]]
    source_gender_varieties: dict[str, SourceGenderVariety]

    @classmethod
    def from_yaml(cls, path: Path) -> GenderDifferenceRules:
        """Load and validate the gender-difference catalog."""
        if not path.is_file():
            raise ConfigurationError(f"Gender differences file does not exist: {path}")

        try:
            with path.open("r", encoding="utf-8") as file:
                payload: Any = yaml.safe_load(file)
        except (OSError, yaml.YAMLError) as error:
            raise ConfigurationError(
                f"Unable to load gender differences: {path}"
            ) from error

        if not isinstance(payload, dict):
            raise ConfigurationError("Gender differences must contain a YAML object.")

        return cls(
            forms_by_dex=_parse_gender_differences(
                payload.get("gender_differences", {})
            ),
            source_gender_varieties=_parse_source_gender_varieties(
                payload.get("source_gender_varieties", {})
            ),
        )

    def applies_to(self, variant: PokemonVariant) -> bool:
        """Return whether a variant must be represented by a gender pair."""
        form_slugs = self.forms_by_dex.get(variant.national_dex, frozenset())
        return variant.form_slug.casefold() in form_slugs


def expand_gender_differences(
    variants: tuple[PokemonVariant, ...],
    rules: GenderDifferenceRules,
) -> tuple[PokemonVariant, ...]:
    """Replace configured ungendered variants with Female and Male rows."""
    if not variants:
        raise ValidationError("Pokémon variant collection cannot be empty.")

    normalized = tuple(
        _normalize_source_gender_variety(variant, rules) for variant in variants
    )

    _validate_configured_forms_are_present(normalized, rules)

    expanded: list[PokemonVariant] = []

    for variant in normalized:
        if variant.gender is not Gender.NONE or not rules.applies_to(variant):
            expanded.append(variant)
            continue

        expanded.extend(
            (
                _with_gender(variant, Gender.FEMALE),
                _with_gender(variant, Gender.MALE),
            )
        )

    ordered = sort_pokemon_variants(expanded)
    validate_pokemon_variants(ordered)
    _validate_catalog_representation(ordered, rules)

    return ordered


def _normalize_source_gender_variety(
    variant: PokemonVariant,
    rules: GenderDifferenceRules,
) -> PokemonVariant:
    source_rule = rules.source_gender_varieties.get(variant.variety_api_name.casefold())

    if source_rule is None:
        return variant

    form_name = _gendered_form_name(
        base_form_name=(
            "Normal" if source_rule.form_slug == "normal" else variant.form_name
        ),
        gender=source_rule.gender,
        is_normal=source_rule.form_slug == "normal",
    )

    return replace(
        variant,
        form_slug=source_rule.form_slug,
        form_name=form_name,
        display_name=f"{source_rule.gender.value} {variant.pokemon}",
        gender=source_rule.gender,
    )


def _with_gender(
    variant: PokemonVariant,
    gender: Gender,
) -> PokemonVariant:
    return replace(
        variant,
        form_name=_gendered_form_name(
            base_form_name=variant.form_name,
            gender=gender,
            is_normal=variant.is_normal_form,
        ),
        display_name=f"{gender.value} {variant.display_name}",
        gender=gender,
    )


def _gendered_form_name(
    *,
    base_form_name: str,
    gender: Gender,
    is_normal: bool,
) -> str:
    if gender is Gender.NONE:
        raise ValueError("Gendered form name requires Female or Male.")

    if is_normal:
        return gender.value

    return f"{base_form_name} {gender.value}"


def _validate_configured_forms_are_present(
    variants: tuple[PokemonVariant, ...],
    rules: GenderDifferenceRules,
) -> None:
    present_species = {variant.national_dex for variant in variants}
    present_forms = {
        (variant.national_dex, variant.form_slug.casefold()) for variant in variants
    }

    missing = sorted(
        (national_dex, form_slug)
        for national_dex, form_slugs in rules.forms_by_dex.items()
        if national_dex in present_species
        for form_slug in form_slugs
        if (national_dex, form_slug) not in present_forms
    )

    if missing:
        details = ", ".join(
            f"{national_dex}:{form_slug}" for national_dex, form_slug in missing
        )
        raise ValidationError(
            f"Configured gender-difference forms are missing: {details}"
        )


def _validate_catalog_representation(
    variants: tuple[PokemonVariant, ...],
    rules: GenderDifferenceRules,
) -> None:
    genders_by_form: dict[tuple[int, str], set[Gender]] = {}

    for variant in variants:
        key = (variant.national_dex, variant.form_slug.casefold())
        genders_by_form.setdefault(key, set()).add(variant.gender)

    invalid = sorted(
        (national_dex, form_slug, genders_by_form.get((national_dex, form_slug), set()))
        for national_dex, form_slugs in rules.forms_by_dex.items()
        if any(variant.national_dex == national_dex for variant in variants)
        for form_slug in form_slugs
        if genders_by_form.get((national_dex, form_slug), set())
        != {Gender.FEMALE, Gender.MALE}
    )

    if invalid:
        details = "; ".join(
            f"{national_dex}:{form_slug}="
            f"{','.join(sorted(gender.value for gender in genders)) or 'missing'}"
            for national_dex, form_slug, genders in invalid
        )
        raise ValidationError(
            "Gender-difference catalog was not expanded into complete pairs: "
            f"{details}"
        )


def _parse_gender_differences(payload: object) -> dict[int, frozenset[str]]:
    if not isinstance(payload, dict):
        raise ConfigurationError("'gender_differences' must contain a YAML object.")

    result: dict[int, frozenset[str]] = {}

    for raw_dex, raw_forms in payload.items():
        try:
            national_dex = int(raw_dex)
        except (TypeError, ValueError) as error:
            raise ConfigurationError(
                "Gender-difference National Dex keys must be integers."
            ) from error

        if national_dex <= 0:
            raise ConfigurationError(
                "Gender-difference National Dex keys must be positive."
            )

        if not isinstance(raw_forms, list) or not raw_forms:
            raise ConfigurationError(
                f"Gender differences for {national_dex} must be a non-empty list."
            )

        forms: set[str] = set()
        for raw_form in raw_forms:
            if not isinstance(raw_form, str) or not raw_form.strip():
                raise ConfigurationError(
                    f"Gender-difference forms for {national_dex} must be strings."
                )
            forms.add(raw_form.strip().casefold())

        result[national_dex] = frozenset(forms)

    return result


def _parse_source_gender_varieties(
    payload: object,
) -> dict[str, SourceGenderVariety]:
    if not isinstance(payload, dict):
        raise ConfigurationError(
            "'source_gender_varieties' must contain a YAML object."
        )

    result: dict[str, SourceGenderVariety] = {}

    for raw_api_name, raw_rule in payload.items():
        if not isinstance(raw_api_name, str) or not raw_api_name.strip():
            raise ConfigurationError(
                "Source gender variety keys must be non-empty strings."
            )
        if not isinstance(raw_rule, dict):
            raise ConfigurationError(
                f"Source gender variety '{raw_api_name}' must be an object."
            )

        raw_gender = raw_rule.get("gender")
        raw_form_slug = raw_rule.get("form_slug")

        if not isinstance(raw_gender, str):
            raise ConfigurationError(
                f"Source gender variety '{raw_api_name}' requires gender."
            )
        if not isinstance(raw_form_slug, str):
            raise ConfigurationError(
                f"Source gender variety '{raw_api_name}' requires form_slug."
            )

        try:
            gender = Gender(raw_gender.strip().title())
        except ValueError as error:
            raise ConfigurationError(
                f"Source gender variety '{raw_api_name}' has invalid gender."
            ) from error

        result[raw_api_name.strip().casefold()] = SourceGenderVariety(
            gender=gender,
            form_slug=raw_form_slug.strip().casefold(),
        )

    return result
