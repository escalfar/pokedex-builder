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


def test_extract_form_slug_simplifies_galarian_darmanitan_standard_mode() -> None:
    assert (
        extract_form_slug(
            species_api_name="darmanitan",
            variety_api_name="darmanitan-galar-standard",
            is_default=False,
        )
        == "galar"
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


def test_build_variants_adds_home_persistent_cosmetic_forms() -> None:
    details = (
        SpeciesDetails(
            national_dex=412,
            api_name="burmy",
            english_name="Burmy",
            generation=4,
            is_legendary=False,
            is_mythical=False,
            resource_url="https://pokeapi.co/api/v2/pokemon-species/412/",
            varieties=(
                SpeciesVariety(
                    api_name="burmy",
                    resource_url="https://pokeapi.co/api/v2/pokemon/412/",
                    is_default=True,
                ),
            ),
        ),
    )
    species = (PokemonSpecies(national_dex=412, name="Burmy", generation=4),)

    variants = build_pokemon_variants(details, species)

    assert [variant.home_id for variant in variants] == [
        "00412_NORMAL_NONE",
        "00412_SANDY_CLOAK_NONE",
        "00412_TRASH_CLOAK_NONE",
    ]
    assert variants[0].form_name == "Plant Cloak"


def test_build_variants_adds_all_vivillon_patterns() -> None:
    details = (
        SpeciesDetails(
            national_dex=666,
            api_name="vivillon",
            english_name="Vivillon",
            generation=6,
            is_legendary=False,
            is_mythical=False,
            resource_url="https://pokeapi.co/api/v2/pokemon-species/666/",
            varieties=(
                SpeciesVariety(
                    api_name="vivillon",
                    resource_url="https://pokeapi.co/api/v2/pokemon/666/",
                    is_default=True,
                ),
            ),
        ),
    )
    species = (PokemonSpecies(national_dex=666, name="Vivillon", generation=6),)

    variants = build_pokemon_variants(details, species)

    assert len(variants) == 20
    assert variants[0].form_name == "Meadow Pattern"
    assert variants[-2].form_name == "Fancy Pattern"
    assert variants[-1].form_name == "Poké Ball Pattern"
    assert {variant.form_name for variant in variants} >= {
        "Fancy Pattern",
        "Poké Ball Pattern",
        "Tundra Pattern",
    }


@pytest.mark.parametrize(
    ("national_dex", "api_name", "english_name"),
    [
        (669, "flabebe", "Flabébé"),
        (670, "floette", "Floette"),
        (671, "florges", "Florges"),
    ],
)
def test_build_variants_adds_all_flower_colors(
    national_dex: int, api_name: str, english_name: str
) -> None:
    details = (
        SpeciesDetails(
            national_dex=national_dex,
            api_name=api_name,
            english_name=english_name,
            generation=6,
            is_legendary=False,
            is_mythical=False,
            resource_url=f"https://pokeapi.co/api/v2/pokemon-species/{national_dex}/",
            varieties=(
                SpeciesVariety(
                    api_name=api_name,
                    resource_url=f"https://pokeapi.co/api/v2/pokemon/{national_dex}/",
                    is_default=True,
                ),
            ),
        ),
    )
    species = (
        PokemonSpecies(national_dex=national_dex, name=english_name, generation=6),
    )

    variants = build_pokemon_variants(details, species)

    assert {variant.form_name for variant in variants} == {
        "Red Flower",
        "Blue Flower",
        "Orange Flower",
        "White Flower",
        "Yellow Flower",
    }


def test_build_variants_adds_all_unown_forms_in_home_order() -> None:
    details = (
        SpeciesDetails(
            national_dex=201,
            api_name="unown",
            english_name="Unown",
            generation=2,
            is_legendary=False,
            is_mythical=False,
            resource_url="https://pokeapi.co/api/v2/pokemon-species/201/",
            varieties=(
                SpeciesVariety(
                    api_name="unown",
                    resource_url="https://pokeapi.co/api/v2/pokemon/201/",
                    is_default=True,
                ),
            ),
        ),
    )
    species = (PokemonSpecies(national_dex=201, name="Unown", generation=2),)

    variants = build_pokemon_variants(details, species)

    expected_names = [*"ABCDEFGHIJKLMNOPQRSTUVWXYZ", "!", "?"]

    assert len(variants) == 28
    assert [variant.form_name for variant in variants] == expected_names
    assert [variant.display_name for variant in variants] == [
        f"Unown ({form_name})" for form_name in expected_names
    ]
    assert variants[0].home_id == "00201_NORMAL_NONE"
    assert variants[-2].home_id == "00201_EXCLAMATION_NONE"
    assert variants[-1].home_id == "00201_QUESTION_NONE"
    assert sum(variant.is_default for variant in variants) == 1


def test_build_variants_adds_alcremie_forms_by_sweet_only() -> None:
    details = (
        SpeciesDetails(
            national_dex=869,
            api_name="alcremie",
            english_name="Alcremie",
            generation=8,
            is_legendary=False,
            is_mythical=False,
            resource_url="https://pokeapi.co/api/v2/pokemon-species/869/",
            varieties=(
                SpeciesVariety(
                    api_name="alcremie",
                    resource_url="https://pokeapi.co/api/v2/pokemon/869/",
                    is_default=True,
                ),
            ),
        ),
    )
    species = (PokemonSpecies(national_dex=869, name="Alcremie", generation=8),)

    variants = build_pokemon_variants(details, species)

    expected_sweets = [
        "Strawberry Sweet",
        "Berry Sweet",
        "Love Sweet",
        "Star Sweet",
        "Clover Sweet",
        "Flower Sweet",
        "Ribbon Sweet",
    ]

    assert len(variants) == 7
    assert [variant.form_name for variant in variants] == expected_sweets
    assert [variant.display_name for variant in variants] == [
        f"Alcremie ({sweet})" for sweet in expected_sweets
    ]
    assert [variant.home_id for variant in variants] == [
        "00869_NORMAL_NONE",
        "00869_BERRY_SWEET_NONE",
        "00869_LOVE_SWEET_NONE",
        "00869_STAR_SWEET_NONE",
        "00869_CLOVER_SWEET_NONE",
        "00869_FLOWER_SWEET_NONE",
        "00869_RIBBON_SWEET_NONE",
    ]
    assert all("cream" not in variant.form_slug for variant in variants)
    assert sum(variant.is_default for variant in variants) == 1


@pytest.mark.parametrize(
    (
        "national_dex",
        "api_name",
        "english_name",
        "generation",
        "expected_forms",
    ),
    (
        (422, "shellos", "Shellos", 4, ("normal", "east-sea")),
        (423, "gastrodon", "Gastrodon", 4, ("normal", "east-sea")),
        (
            585,
            "deerling",
            "Deerling",
            5,
            ("normal", "summer", "autumn", "winter"),
        ),
        (
            586,
            "sawsbuck",
            "Sawsbuck",
            5,
            ("normal", "summer", "autumn", "winter"),
        ),
        (
            676,
            "furfrou",
            "Furfrou",
            6,
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
            ),
        ),
        (854, "sinistea", "Sinistea", 8, ("normal", "antique")),
        (855, "polteageist", "Polteageist", 8, ("normal", "antique")),
        (
            1012,
            "poltchageist",
            "Poltchageist",
            9,
            ("normal", "artisan"),
        ),
        (
            1013,
            "sinistcha",
            "Sinistcha",
            9,
            ("normal", "masterpiece"),
        ),
    ),
)
def test_build_variants_adds_home_persistent_forms(
    national_dex: int,
    api_name: str,
    english_name: str,
    generation: int,
    expected_forms: tuple[str, ...],
) -> None:
    details = (
        SpeciesDetails(
            national_dex=national_dex,
            api_name=api_name,
            english_name=english_name,
            generation=generation,
            is_legendary=False,
            is_mythical=False,
            resource_url=(f"https://pokeapi.co/api/v2/pokemon-species/{national_dex}/"),
            varieties=(
                SpeciesVariety(
                    api_name=api_name,
                    resource_url=(f"https://pokeapi.co/api/v2/pokemon/{national_dex}/"),
                    is_default=True,
                ),
            ),
        ),
    )
    species = (
        PokemonSpecies(
            national_dex=national_dex,
            name=english_name,
            generation=generation,
        ),
    )

    variants = build_pokemon_variants(details, species)

    assert tuple(variant.form_slug for variant in variants) == expected_forms
    assert variants[0].is_default is True
    assert all(variant.generation == generation for variant in variants)
    assert len({variant.home_id for variant in variants}) == len(expected_forms)
