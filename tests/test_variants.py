import pytest

from pokedex.constants import Gender
from pokedex.exceptions import ValidationError
from pokedex.models import PokemonSpecies, PokemonVariant
from pokedex.pokeapi import SpeciesDetails, SpeciesVariety
from pokedex.variants import (
    build_pokemon_variants,
    extract_form_slug,
    form_slug_to_name,
    sort_pokemon_variants,
    validate_pokemon_variants,
)


def build_variant(
    *,
    national_dex: int = 25,
    pokemon: str = "Pikachu",
    species_api_name: str = "pikachu",
    variety_api_name: str = "pikachu",
    form_slug: str = "normal",
    form_name: str = "Normal",
    display_name: str = "Pikachu",
    generation: int = 1,
    resource_url: str = ("https://pokeapi.co/api/v2/pokemon/25/"),
    is_default: bool = True,
    gender: Gender = Gender.NONE,
) -> PokemonVariant:
    return PokemonVariant(
        national_dex=national_dex,
        pokemon=pokemon,
        species_api_name=species_api_name,
        variety_api_name=variety_api_name,
        form_slug=form_slug,
        form_name=form_name,
        display_name=display_name,
        generation=generation,
        resource_url=resource_url,
        is_default=is_default,
        gender=gender,
    )


def test_extract_form_slug_returns_normal_for_default() -> None:
    assert (
        extract_form_slug(
            species_api_name="pikachu",
            variety_api_name="pikachu",
            is_default=True,
        )
        == "normal"
    )


def test_extract_form_slug_removes_species_prefix() -> None:
    assert (
        extract_form_slug(
            species_api_name="raichu",
            variety_api_name="raichu-alola",
            is_default=False,
        )
        == "alola"
    )


def test_form_slug_to_name() -> None:
    assert form_slug_to_name("normal") == "Normal"
    assert form_slug_to_name("white-striped") == "White Striped"


def test_build_variants_converts_species_varieties() -> None:
    details = (
        SpeciesDetails(
            national_dex=26,
            api_name="raichu",
            english_name="Raichu",
            generation=1,
            is_legendary=False,
            is_mythical=False,
            resource_url=("https://pokeapi.co/api/v2/" "pokemon-species/26/"),
            varieties=(
                SpeciesVariety(
                    api_name="raichu",
                    resource_url=("https://pokeapi.co/api/v2/" "pokemon/26/"),
                    is_default=True,
                ),
                SpeciesVariety(
                    api_name="raichu-alola",
                    resource_url=("https://pokeapi.co/api/v2/" "pokemon/10100/"),
                    is_default=False,
                ),
            ),
        ),
    )

    species = (
        PokemonSpecies(
            national_dex=26,
            name="Raichu",
            generation=1,
        ),
    )

    variants = build_pokemon_variants(
        details,
        species,
    )

    assert len(variants) == 2

    assert variants[0].home_id == "00026_NORMAL_NONE"
    assert variants[0].display_name == "Raichu"

    assert variants[1].home_id == "00026_ALOLA_NONE"
    assert variants[1].display_name == "Alola Raichu"


def test_build_variants_rejects_unknown_species() -> None:
    details = (
        SpeciesDetails(
            national_dex=26,
            api_name="raichu",
            english_name="Raichu",
            generation=1,
            is_legendary=False,
            is_mythical=False,
            resource_url=("https://pokeapi.co/api/v2/" "pokemon-species/26/"),
            varieties=(
                SpeciesVariety(
                    api_name="raichu",
                    resource_url=("https://pokeapi.co/api/v2/" "pokemon/26/"),
                    is_default=True,
                ),
            ),
        ),
    )

    with pytest.raises(
        ValidationError,
        match="not present in the domain collection",
    ):
        build_pokemon_variants(
            details,
            (),
        )


def test_sort_variants_orders_normal_before_other_forms() -> None:
    normal = build_variant()

    alolan = build_variant(
        national_dex=26,
        pokemon="Raichu",
        species_api_name="raichu",
        variety_api_name="raichu-alola",
        form_slug="alola",
        form_name="Alolan",
        display_name="Alolan Raichu",
        generation=7,
        resource_url=("https://pokeapi.co/api/v2/" "pokemon/10100/"),
        is_default=False,
    )

    ordered = sort_pokemon_variants(
        (
            alolan,
            normal,
        )
    )

    assert ordered == (
        normal,
        alolan,
    )


# def test_sort_variants_orders_gender_pair() -> None:
#     base = build_variant()
#
#     male = PokemonVariant(
#         **{
#             **base.__dict__,
#             "gender": Gender.MALE,
#         }
#     )


def test_sort_variants_orders_gender_pair() -> None:
    male = build_variant(
        gender=Gender.MALE,
        display_name="Male Pikachu",
    )

    female = build_variant(
        gender=Gender.FEMALE,
        display_name="Female Pikachu",
    )

    ordered = sort_pokemon_variants(
        (
            male,
            female,
        )
    )

    assert ordered == (
        female,
        male,
    )


def test_validation_accepts_ungendered_variant() -> None:
    validate_pokemon_variants((build_variant(),))


def test_validation_accepts_gender_pair() -> None:
    male = build_variant(
        gender=Gender.MALE,
        display_name="Male Pikachu",
    )

    female = build_variant(
        gender=Gender.FEMALE,
        display_name="Female Pikachu",
    )

    validate_pokemon_variants(
        (
            female,
            male,
        )
    )


def test_validation_rejects_incomplete_gender_pair() -> None:
    female = build_variant(
        gender=Gender.FEMALE,
        display_name="Female Pikachu",
    )

    with pytest.raises(
        ValidationError,
        match="male/female pair",
    ):
        validate_pokemon_variants((female,))


def test_validation_rejects_mixed_gender_representation() -> None:
    normal = build_variant()

    male = build_variant(
        gender=Gender.MALE,
        display_name="Male Pikachu",
    )

    female = build_variant(
        gender=Gender.FEMALE,
        display_name="Female Pikachu",
    )

    with pytest.raises(
        ValidationError,
        match="male/female pair",
    ):
        validate_pokemon_variants(
            (
                normal,
                male,
                female,
            )
        )


def test_validation_rejects_duplicate_home_ids() -> None:
    first = build_variant()

    duplicate = build_variant(
        variety_api_name="pikachu-copy",
        display_name="Copy Pikachu",
        resource_url=("https://example.com/pikachu-copy/"),
        is_default=False,
    )

    with pytest.raises(
        ValidationError,
        match="Duplicate Pokémon variant HOME IDs",
    ):
        validate_pokemon_variants(
            (
                first,
                duplicate,
            )
        )


def test_validation_rejects_duplicate_names() -> None:
    normal = build_variant()

    special = build_variant(
        form_slug="special",
        form_name="Special",
        variety_api_name="pikachu-special",
        display_name="PIKACHU",
        resource_url=("https://example.com/pikachu-special/"),
        is_default=False,
    )

    with pytest.raises(
        ValidationError,
        match="Duplicate Pokémon variant names",
    ):
        validate_pokemon_variants(
            (
                normal,
                special,
            )
        )


def test_validation_requires_default_variety() -> None:
    special = build_variant(
        form_slug="special",
        form_name="Special",
        variety_api_name="pikachu-special",
        display_name="Special Pikachu",
        resource_url=("https://example.com/pikachu-special/"),
        is_default=False,
    )

    with pytest.raises(
        ValidationError,
        match="exactly one default variety",
    ):
        validate_pokemon_variants((special,))


def test_validation_rejects_unordered_variants() -> None:
    normal = build_variant(
        national_dex=26,
        pokemon="Raichu",
        species_api_name="raichu",
        variety_api_name="raichu",
        form_slug="normal",
        form_name="Normal",
        display_name="Raichu",
        generation=1,
        resource_url=("https://pokeapi.co/api/v2/" "pokemon/26/"),
        is_default=True,
    )

    alolan = build_variant(
        national_dex=26,
        pokemon="Raichu",
        species_api_name="raichu",
        variety_api_name="raichu-alola",
        form_slug="alola",
        form_name="Alolan",
        display_name="Alolan Raichu",
        generation=7,
        resource_url=("https://pokeapi.co/api/v2/" "pokemon/10100/"),
        is_default=False,
    )

    with pytest.raises(
        ValidationError,
        match="deterministic order",
    ):
        validate_pokemon_variants(
            (
                alolan,
                normal,
            )
        )


def test_validation_rejects_empty_collection() -> None:
    with pytest.raises(
        ValidationError,
        match="cannot be empty",
    ):
        validate_pokemon_variants(())
