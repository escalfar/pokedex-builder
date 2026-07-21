from __future__ import annotations

import re
from collections.abc import Iterable

from pokedex.constants import Gender, GENDER_SORT_ORDER
from pokedex.exceptions import ValidationError
from pokedex.models import PokemonSpecies, PokemonVariant
from pokedex.pokeapi import SpeciesDetails, SpeciesVariety

NORMAL_FORM_NAME = "Normal"
NORMAL_FORM_SLUG = "normal"

# PokéAPI exposes these HOME-persistent cosmetic forms through the forms
# endpoint rather than the species varieties list.  The project models them
# explicitly so every form stored independently by Pokémon HOME receives its
# own catalog row.
_SUPPLEMENTAL_FORMS: dict[str, tuple[tuple[str, str], ...]] = {
    "unown": tuple(
        [(letter.casefold(), letter) for letter in "BCDEFGHIJKLMNOPQRSTUVWXYZ"]
        + [("exclamation", "!"), ("question", "?")]
    ),
    "burmy": (
        ("sandy-cloak", "Sandy Cloak"),
        ("trash-cloak", "Trash Cloak"),
    ),
    "shellos": (("east-sea", "East Sea"),),
    "gastrodon": (("east-sea", "East Sea"),),
    "deerling": (
        ("summer", "Summer Form"),
        ("autumn", "Autumn Form"),
        ("winter", "Winter Form"),
    ),
    "sawsbuck": (
        ("summer", "Summer Form"),
        ("autumn", "Autumn Form"),
        ("winter", "Winter Form"),
    ),
    "furfrou": (
        ("heart-trim", "Heart Trim"),
        ("star-trim", "Star Trim"),
        ("diamond-trim", "Diamond Trim"),
        ("debutante-trim", "Debutante Trim"),
        ("matron-trim", "Matron Trim"),
        ("dandy-trim", "Dandy Trim"),
        ("la-reine-trim", "La Reine Trim"),
        ("kabuki-trim", "Kabuki Trim"),
        ("pharaoh-trim", "Pharaoh Trim"),
    ),
    "sinistea": (("antique", "Antique Form"),),
    "polteageist": (("antique", "Antique Form"),),
    "poltchageist": (("artisan", "Artisan Form"),),
    "sinistcha": (("masterpiece", "Masterpiece Form"),),
    "vivillon": (
        ("archipelago-pattern", "Archipelago Pattern"),
        ("continental-pattern", "Continental Pattern"),
        ("elegant-pattern", "Elegant Pattern"),
        ("fancy-pattern", "Fancy Pattern"),
        ("garden-pattern", "Garden Pattern"),
        ("high-plains-pattern", "High Plains Pattern"),
        ("icy-snow-pattern", "Icy Snow Pattern"),
        ("jungle-pattern", "Jungle Pattern"),
        ("marine-pattern", "Marine Pattern"),
        ("modern-pattern", "Modern Pattern"),
        ("monsoon-pattern", "Monsoon Pattern"),
        ("ocean-pattern", "Ocean Pattern"),
        ("poke-ball-pattern", "Poké Ball Pattern"),
        ("polar-pattern", "Polar Pattern"),
        ("river-pattern", "River Pattern"),
        ("sandstorm-pattern", "Sandstorm Pattern"),
        ("savanna-pattern", "Savanna Pattern"),
        ("sun-pattern", "Sun Pattern"),
        ("tundra-pattern", "Tundra Pattern"),
    ),
    "flabebe": (
        ("blue-flower", "Blue Flower"),
        ("orange-flower", "Orange Flower"),
        ("white-flower", "White Flower"),
        ("yellow-flower", "Yellow Flower"),
    ),
    "floette": (
        ("blue-flower", "Blue Flower"),
        ("orange-flower", "Orange Flower"),
        ("white-flower", "White Flower"),
        ("yellow-flower", "Yellow Flower"),
    ),
    "florges": (
        ("blue-flower", "Blue Flower"),
        ("orange-flower", "Orange Flower"),
        ("white-flower", "White Flower"),
        ("yellow-flower", "Yellow Flower"),
    ),
    "alcremie": (
        ("berry-sweet", "Berry Sweet"),
        ("love-sweet", "Love Sweet"),
        ("star-sweet", "Star Sweet"),
        ("clover-sweet", "Clover Sweet"),
        ("flower-sweet", "Flower Sweet"),
        ("ribbon-sweet", "Ribbon Sweet"),
    ),
}

_DEFAULT_FORM_PRESENTATION: dict[str, tuple[str, str]] = {
    "unown": ("A", "Unown (A)"),
    "burmy": ("Plant Cloak", "Plant Cloak Burmy"),
    "shellos": ("West Sea", "West Sea Shellos"),
    "gastrodon": ("West Sea", "West Sea Gastrodon"),
    "deerling": ("Spring Form", "Spring Form Deerling"),
    "sawsbuck": ("Spring Form", "Spring Form Sawsbuck"),
    "furfrou": ("Natural Form", "Natural Form Furfrou"),
    "sinistea": ("Phony Form", "Phony Form Sinistea"),
    "polteageist": ("Phony Form", "Phony Form Polteageist"),
    "poltchageist": ("Counterfeit Form", "Counterfeit Form Poltchageist"),
    "sinistcha": ("Unremarkable Form", "Unremarkable Form Sinistcha"),
    "vivillon": ("Meadow Pattern", "Meadow Pattern Vivillon"),
    "flabebe": ("Red Flower", "Red Flower Flabébé"),
    "floette": ("Red Flower", "Red Flower Floette"),
    "florges": ("Red Flower", "Red Flower Florges"),
    "alcremie": ("Strawberry Sweet", "Alcremie (Strawberry Sweet)"),
}


_SPECIAL_FORM_ORDER: dict[int, dict[str, int]] = {
    201: {
        "normal": 0,
        **{
            letter.casefold(): index
            for index, letter in enumerate("BCDEFGHIJKLMNOPQRSTUVWXYZ", start=1)
        },
        "exclamation": 26,
        "question": 27,
    },
    422: {"normal": 0, "east-sea": 1},
    423: {"normal": 0, "east-sea": 1},
    585: {"normal": 0, "summer": 1, "autumn": 2, "winter": 3},
    586: {"normal": 0, "summer": 1, "autumn": 2, "winter": 3},
    676: {
        slug: index
        for index, slug in enumerate(
            (
                "normal",
                "heart-trim",
                "star-trim",
                "diamond-trim",
                "debutante-trim",
                "matron-trim",
                "dandy-trim",
                "la-reine-trim",
                "kabuki-trim",
                "pharaoh-trim",
            )
        )
    },
    854: {"normal": 0, "antique": 1},
    855: {"normal": 0, "antique": 1},
    1012: {"normal": 0, "artisan": 1},
    1013: {"normal": 0, "masterpiece": 1},
    869: {
        slug: index
        for index, slug in enumerate(
            (
                "normal",
                "berry-sweet",
                "love-sweet",
                "star-sweet",
                "clover-sweet",
                "flower-sweet",
                "ribbon-sweet",
            )
        )
    },
}


def build_pokemon_variants(
    details: Iterable[SpeciesDetails],
    species: Iterable[PokemonSpecies],
) -> tuple[PokemonVariant, ...]:
    """Convert PokéAPI varieties into provisional Pokémon variants."""
    species_by_dex = {item.national_dex: item for item in species}

    variants: list[PokemonVariant] = []

    for detail in details:
        base_species = species_by_dex.get(detail.national_dex)

        if base_species is None:
            raise ValidationError(
                "Species details contain a National Pokédex number "
                "not present in the domain collection: "
                f"{detail.national_dex}"
            )

        variants.extend(
            _build_species_variants(
                detail=detail,
                species=base_species,
            )
        )

    ordered = sort_pokemon_variants(variants)

    validate_pokemon_variants(ordered)

    return ordered


def sort_pokemon_variants(
    variants: Iterable[PokemonVariant],
) -> tuple[PokemonVariant, ...]:
    """Return Pokémon variants in deterministic order."""
    return tuple(
        sorted(
            variants,
            key=_variant_sort_key,
        )
    )


def validate_pokemon_variants(
    variants: tuple[PokemonVariant, ...],
) -> None:
    """Validate integrity rules for Pokémon variants."""
    if not variants:
        raise ValidationError("Pokémon variant collection cannot be empty.")

    _validate_unique_home_ids(variants)
    _validate_unique_logical_keys(variants)
    _validate_unique_names(variants)
    _validate_one_default_variety_per_species(variants)
    _validate_one_normal_form_per_species(variants)
    _validate_gender_representation(variants)
    _validate_deterministic_order(variants)


def extract_form_slug(
    *,
    species_api_name: str,
    variety_api_name: str,
    is_default: bool,
) -> str:
    """Extract a stable form slug from PokéAPI resource names."""
    if is_default:
        return NORMAL_FORM_SLUG

    normalized_species = _normalize_slug(species_api_name)
    normalized_variety = _normalize_slug(variety_api_name)

    if not normalized_species:
        raise ValueError("Species API name cannot be empty.")

    if not normalized_variety:
        raise ValueError("Variety API name cannot be empty.")

    prefix = f"{normalized_species}-"

    if normalized_variety.startswith(prefix):
        form_slug = normalized_variety.removeprefix(prefix)
    else:
        form_slug = normalized_variety

    if not form_slug:
        raise ValidationError(
            "Unable to determine form slug for variety: " f"{variety_api_name}"
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


def _build_species_variants(
    *,
    detail: SpeciesDetails,
    species: PokemonSpecies,
) -> tuple[PokemonVariant, ...]:
    api_variants = tuple(
        _build_variant(
            detail=detail,
            species=species,
            variety=variety,
        )
        for variety in detail.varieties
    )

    supplemental = tuple(
        PokemonVariant(
            national_dex=species.national_dex,
            pokemon=species.name,
            species_api_name=detail.api_name,
            variety_api_name=f"{detail.api_name}-{form_slug}",
            form_slug=form_slug,
            form_name=form_name,
            display_name=_supplemental_display_name(
                species_api_name=detail.api_name,
                species_name=species.name,
                form_name=form_name,
            ),
            generation=species.generation,
            resource_url=f"synthetic://pokemon-form/{detail.api_name}-{form_slug}",
            is_default=False,
            gender=Gender.NONE,
        )
        for form_slug, form_name in _SUPPLEMENTAL_FORMS.get(detail.api_name, ())
    )

    return api_variants + supplemental


def _supplemental_display_name(
    *,
    species_api_name: str,
    species_name: str,
    form_name: str,
) -> str:
    if species_api_name in {"unown", "alcremie"}:
        return f"{species_name} ({form_name})"

    return f"{form_name} {species_name}"


def _build_variant(
    *,
    detail: SpeciesDetails,
    species: PokemonSpecies,
    variety: SpeciesVariety,
) -> PokemonVariant:
    form_slug = extract_form_slug(
        species_api_name=detail.api_name,
        variety_api_name=variety.api_name,
        is_default=variety.is_default,
    )

    form_name = form_slug_to_name(form_slug)

    if variety.is_default:
        default_presentation = _DEFAULT_FORM_PRESENTATION.get(detail.api_name)
        if default_presentation is None:
            display_name = species.name
        else:
            form_name, display_name = default_presentation
    else:
        display_name = f"{form_name} {species.name}"

    return PokemonVariant(
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
        gender=Gender.NONE,
    )


def _variant_sort_key(
    variant: PokemonVariant,
) -> tuple[int, int, int, str, int, str]:
    form_slug = variant.form_slug.casefold()
    special_order = _SPECIAL_FORM_ORDER.get(variant.national_dex)

    if special_order is None:
        group = 0 if variant.is_normal_form else 1
        rank = 0
    else:
        group = 0
        rank = special_order.get(form_slug, len(special_order))

    return (
        variant.national_dex,
        group,
        rank,
        form_slug,
        GENDER_SORT_ORDER[variant.gender],
        variant.variety_api_name.casefold(),
    )


def _validate_unique_home_ids(
    variants: tuple[PokemonVariant, ...],
) -> None:
    home_ids: dict[str, int] = {}

    for variant in variants:
        home_ids[variant.home_id] = home_ids.get(variant.home_id, 0) + 1

    duplicates = sorted(home_id for home_id, count in home_ids.items() if count > 1)

    if duplicates:
        raise ValidationError(
            "Duplicate Pokémon variant HOME IDs found: " f"{', '.join(duplicates)}"
        )


def _validate_unique_logical_keys(
    variants: tuple[PokemonVariant, ...],
) -> None:
    keys: dict[tuple[int, str, Gender], int] = {}

    for variant in variants:
        key = variant.logical_key
        keys[key] = keys.get(key, 0) + 1

    duplicates = sorted(
        (
            national_dex,
            form_slug,
            gender,
        )
        for (
            national_dex,
            form_slug,
            gender,
        ), count in keys.items()
        if count > 1
    )

    if duplicates:
        details = ", ".join(
            (f"{national_dex}:" f"{form_slug}:" f"{gender.value}")
            for national_dex, form_slug, gender in duplicates
        )

        raise ValidationError(
            "Duplicate Pokémon variant logical keys found: " f"{details}"
        )


def _validate_unique_names(
    variants: tuple[PokemonVariant, ...],
) -> None:
    names: dict[str, list[str]] = {}

    for variant in variants:
        normalized_name = variant.display_name.casefold()
        names.setdefault(
            normalized_name,
            [],
        ).append(variant.home_id)

    duplicates = {
        name: home_ids for name, home_ids in names.items() if len(home_ids) > 1
    }

    if duplicates:
        details = "; ".join(
            f"{name}: {', '.join(home_ids)}"
            for name, home_ids in sorted(duplicates.items())
        )

        raise ValidationError("Duplicate Pokémon variant names found: " f"{details}")


def _validate_one_default_variety_per_species(
    variants: tuple[PokemonVariant, ...],
) -> None:
    default_varieties: dict[int, set[str]] = {}

    for variant in variants:
        default_varieties.setdefault(
            variant.national_dex,
            set(),
        )

        if variant.is_default:
            default_varieties[variant.national_dex].add(variant.variety_api_name)

    invalid = {
        national_dex: names
        for national_dex, names in default_varieties.items()
        if len(names) != 1
    }

    if invalid:
        details = "; ".join(
            (f"{national_dex}=" f"{','.join(sorted(names)) or 'missing'}")
            for national_dex, names in sorted(invalid.items())
        )

        raise ValidationError(
            "Each species must contain exactly one default variety: " f"{details}"
        )


def _validate_one_normal_form_per_species(
    variants: tuple[PokemonVariant, ...],
) -> None:
    """Require every species to expose exactly one logical normal form.

    A visible default presentation (for example West Sea Shellos) may keep its
    user-facing name, but its stable HOME identifier must still use NORMAL.
    Gender differences count as one logical form because they share the slug.
    """
    normal_forms: dict[int, set[str]] = {}
    for variant in variants:
        normal_forms.setdefault(variant.national_dex, set())
        if variant.is_normal_form:
            # Male/female rows are two representations of the same logical form.
            normal_forms[variant.national_dex].add(variant.form_slug.casefold())

    invalid = {dex: slugs for dex, slugs in normal_forms.items() if len(slugs) != 1}
    if invalid:
        details = "; ".join(
            f"{dex}={','.join(sorted(slugs)) or 'missing'}"
            for dex, slugs in sorted(invalid.items())
        )
        raise ValidationError(
            "Each species must contain exactly one normal form: " + details
        )


def _validate_gender_representation(
    variants: tuple[PokemonVariant, ...],
) -> None:
    genders_by_form: dict[
        tuple[int, str],
        set[Gender],
    ] = {}

    for variant in variants:
        key = (
            variant.national_dex,
            variant.form_slug.casefold(),
        )

        genders_by_form.setdefault(
            key,
            set(),
        ).add(variant.gender)

    invalid: dict[
        tuple[int, str],
        set[Gender],
    ] = {}

    for key, genders in genders_by_form.items():
        is_ungendered = genders == {Gender.NONE}
        is_gender_pair = genders == {
            Gender.MALE,
            Gender.FEMALE,
        }

        if not is_ungendered and not is_gender_pair:
            invalid[key] = genders

    if invalid:
        details = "; ".join(
            (
                f"{national_dex}:{form_slug}="
                f"{','.join(sorted(gender.value for gender in genders))}"
            )
            for (
                national_dex,
                form_slug,
            ), genders in sorted(invalid.items())
        )

        raise ValidationError(
            "Each form must be represented by either one ungendered "
            "variant or one male/female pair: "
            f"{details}"
        )


def _validate_deterministic_order(
    variants: tuple[PokemonVariant, ...],
) -> None:
    expected = tuple(
        sorted(
            variants,
            key=_variant_sort_key,
        )
    )

    if variants != expected:
        raise ValidationError("Pokémon variants are not in deterministic order.")


def _normalize_slug(value: str) -> str:
    normalized = value.strip().casefold().replace("_", "-")
    normalized = re.sub(
        r"[^a-z0-9-]+",
        "-",
        normalized,
    )
    normalized = re.sub(
        r"-{2,}",
        "-",
        normalized,
    )

    return normalized.strip("-")
