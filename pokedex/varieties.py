from __future__ import annotations

import re
from dataclasses import dataclass

from pokedex.exceptions import ValidationError
from pokedex.models import PokemonSpecies
from pokedex.pokeapi import SpeciesDetails, SpeciesVariety

NORMAL_FORM_NAME = "Normal"
NORMAL_FORM_SLUG = "normal"


@dataclass(frozen=True, slots=True)
class VarietyCandidate:
    """Intermediate candidate produced from a PokéAPI variety."""

    national_dex: int
    pokemon: str
    species_api_name: str
    variety_api_name: str
    form_slug: str
    form_name: str
    display_name: str
    generation: int
    resource_url: str
    is_default: bool
    home_id: str

    def __post_init__(self) -> None:
        if self.national_dex <= 0:
            raise ValueError("National Pokédex number must be greater than zero.")

        if self.generation <= 0:
            raise ValueError("Generation must be greater than zero.")

        for field_name, value in (
            ("pokemon", self.pokemon),
            ("species_api_name", self.species_api_name),
            ("variety_api_name", self.variety_api_name),
            ("form_slug", self.form_slug),
            ("form_name", self.form_name),
            ("display_name", self.display_name),
            ("resource_url", self.resource_url),
            ("home_id", self.home_id),
        ):
            if not value.strip():
                raise ValueError(f"{field_name} cannot be empty.")


def build_variety_candidates(
    details: tuple[SpeciesDetails, ...],
    species: tuple[PokemonSpecies, ...],
) -> tuple[VarietyCandidate, ...]:
    """Convert PokéAPI varieties into deterministic form candidates."""
    species_by_dex = {item.national_dex: item for item in species}

    candidates: list[VarietyCandidate] = []

    for detail in details:
        base_species = species_by_dex.get(detail.national_dex)

        if base_species is None:
            raise ValidationError(
                "Species details contain a National Pokédex number "
                f"not present in the domain collection: {detail.national_dex}"
            )

        candidates.extend(
            _build_species_candidates(
                detail=detail,
                species=base_species,
            )
        )

    ordered = tuple(
        sorted(
            candidates,
            key=lambda item: (
                item.national_dex,
                not item.is_default,
                item.form_slug,
                item.variety_api_name,
            ),
        )
    )

    validate_variety_candidates(ordered)

    return ordered


def _build_species_candidates(
    *,
    detail: SpeciesDetails,
    species: PokemonSpecies,
) -> tuple[VarietyCandidate, ...]:
    return tuple(
        _build_candidate(
            detail=detail,
            species=species,
            variety=variety,
        )
        for variety in detail.varieties
    )


def _build_candidate(
    *,
    detail: SpeciesDetails,
    species: PokemonSpecies,
    variety: SpeciesVariety,
) -> VarietyCandidate:
    form_slug = extract_form_slug(
        species_api_name=detail.api_name,
        variety_api_name=variety.api_name,
        is_default=variety.is_default,
    )

    form_name = form_slug_to_name(form_slug)

    if variety.is_default:
        display_name = species.name
    else:
        display_name = f"{form_name} {species.name}"

    return VarietyCandidate(
        national_dex=species.national_dex,
        pokemon=species.name,
        species_api_name=detail.api_name,
        variety_api_name=variety.api_name,
        form_slug=form_slug,
        form_name=form_name,
        display_name=display_name,
        generation=species.generation,
        resource_url=variety.resource_url,
        is_default=variety.is_default,
        home_id=build_home_id(
            national_dex=species.national_dex,
            form_slug=form_slug,
        ),
    )


def extract_form_slug(
    *,
    species_api_name: str,
    variety_api_name: str,
    is_default: bool,
) -> str:
    """Extract a stable form slug from PokéAPI resource names."""
    if is_default:
        return NORMAL_FORM_SLUG

    normalized_species = species_api_name.strip().casefold()
    normalized_variety = variety_api_name.strip().casefold()

    if not normalized_species:
        raise ValueError("Species API name cannot be empty.")

    if not normalized_variety:
        raise ValueError("Variety API name cannot be empty.")

    prefix = f"{normalized_species}-"

    if normalized_variety.startswith(prefix):
        form_slug = normalized_variety.removeprefix(prefix)
    else:
        form_slug = normalized_variety

    form_slug = _normalize_slug(form_slug)

    if not form_slug:
        raise ValidationError(
            f"Unable to determine form slug for variety: {variety_api_name}"
        )

    return form_slug


def form_slug_to_name(form_slug: str) -> str:
    """Convert an API form slug into a readable provisional name."""
    normalized = _normalize_slug(form_slug)

    if not normalized:
        raise ValueError("Form slug cannot be empty.")

    if normalized == NORMAL_FORM_SLUG:
        return NORMAL_FORM_NAME

    return " ".join(word.capitalize() for word in normalized.split("-"))


def build_home_id(
    *,
    national_dex: int,
    form_slug: str,
) -> str:
    """Build a deterministic internal HOME-style identifier."""
    if national_dex <= 0:
        raise ValueError("National Pokédex number must be greater than zero.")

    normalized_slug = _normalize_slug(form_slug)

    if not normalized_slug:
        raise ValueError("Form slug cannot be empty.")

    identifier_slug = normalized_slug.replace("-", "_").upper()

    return f"{national_dex:05d}_{identifier_slug}"


def validate_variety_candidates(
    candidates: tuple[VarietyCandidate, ...],
) -> None:
    """Validate uniqueness and default-variety rules."""
    if not candidates:
        raise ValidationError("Variety candidate collection cannot be empty.")

    _validate_unique_home_ids(candidates)
    _validate_unique_resource_urls(candidates)
    _validate_one_default_per_species(candidates)


def _validate_unique_home_ids(
    candidates: tuple[VarietyCandidate, ...],
) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()

    for candidate in candidates:
        if candidate.home_id in seen:
            duplicates.add(candidate.home_id)

        seen.add(candidate.home_id)

    if duplicates:
        values = ", ".join(sorted(duplicates))
        raise ValidationError(f"Duplicate candidate HOME IDs found: {values}")


def _validate_unique_resource_urls(
    candidates: tuple[VarietyCandidate, ...],
) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()

    for candidate in candidates:
        if candidate.resource_url in seen:
            duplicates.add(candidate.resource_url)

        seen.add(candidate.resource_url)

    if duplicates:
        values = ", ".join(sorted(duplicates))
        raise ValidationError(f"Duplicate variety resource URLs found: {values}")


def _validate_one_default_per_species(
    candidates: tuple[VarietyCandidate, ...],
) -> None:
    default_counts: dict[int, int] = {}

    for candidate in candidates:
        default_counts.setdefault(candidate.national_dex, 0)

        if candidate.is_default:
            default_counts[candidate.national_dex] += 1

    invalid = {
        national_dex: count
        for national_dex, count in default_counts.items()
        if count != 1
    }

    if invalid:
        values = ", ".join(
            f"{national_dex}={count}" for national_dex, count in sorted(invalid.items())
        )
        raise ValidationError(
            "Each species must contain exactly one default variety: " f"{values}"
        )


def _normalize_slug(value: str) -> str:
    normalized = value.strip().casefold().replace("_", "-")
    normalized = re.sub(r"[^a-z0-9-]+", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized)

    return normalized.strip("-")
