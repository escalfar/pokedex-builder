import pytest

from pokedex.exceptions import ValidationError
from pokedex.models import PokemonSpecies
from pokedex.pokeapi import SpeciesDetails, SpeciesVariety
from pokedex.varieties import (
    VarietyCandidate,
    build_home_id,
    build_variety_candidates,
    extract_form_slug,
    form_slug_to_name,
    validate_variety_candidates,
)


def build_species_details(
    *,
    national_dex: int,
    api_name: str,
    english_name: str,
    generation: int,
    varieties: tuple[SpeciesVariety, ...],
) -> SpeciesDetails:
    return SpeciesDetails(
        national_dex=national_dex,
        api_name=api_name,
        english_name=english_name,
        generation=generation,
        is_legendary=False,
        is_mythical=False,
        resource_url=("https://pokeapi.co/api/v2/" f"pokemon-species/{national_dex}/"),
        varieties=varieties,
    )


def build_species(
    *,
    national_dex: int,
    name: str,
    generation: int,
) -> PokemonSpecies:
    return PokemonSpecies(
        national_dex=national_dex,
        name=name,
        generation=generation,
    )


def test_extract_form_slug_returns_normal_for_default() -> None:
    result = extract_form_slug(
        species_api_name="raichu",
        variety_api_name="raichu",
        is_default=True,
    )

    assert result == "normal"


def test_extract_form_slug_removes_species_prefix() -> None:
    result = extract_form_slug(
        species_api_name="raichu",
        variety_api_name="raichu-alola",
        is_default=False,
    )

    assert result == "alola"


def test_extract_form_slug_preserves_unmatched_name() -> None:
    result = extract_form_slug(
        species_api_name="mr-mime",
        variety_api_name="mime-special",
        is_default=False,
    )

    assert result == "mime-special"


def test_form_slug_to_name() -> None:
    assert form_slug_to_name("normal") == "Normal"
    assert form_slug_to_name("white-striped") == "White Striped"
    assert form_slug_to_name("galar-standard") == "Galar Standard"


def test_build_home_id() -> None:
    assert (
        build_home_id(
            national_dex=26,
            form_slug="alola",
        )
        == "00026_ALOLA"
    )

    assert (
        build_home_id(
            national_dex=550,
            form_slug="white-striped",
        )
        == "00550_WHITE_STRIPED"
    )


def test_build_variety_candidates_orders_default_first() -> None:
    details = (
        build_species_details(
            national_dex=26,
            api_name="raichu",
            english_name="Raichu",
            generation=1,
            varieties=(
                SpeciesVariety(
                    api_name="raichu-alola",
                    resource_url=("https://pokeapi.co/api/v2/pokemon/10100/"),
                    is_default=False,
                ),
                SpeciesVariety(
                    api_name="raichu",
                    resource_url=("https://pokeapi.co/api/v2/pokemon/26/"),
                    is_default=True,
                ),
            ),
        ),
    )

    species = (
        build_species(
            national_dex=26,
            name="Raichu",
            generation=1,
        ),
    )

    candidates = build_variety_candidates(details, species)

    assert len(candidates) == 2
    assert candidates[0].is_default is True
    assert candidates[0].form_name == "Normal"
    assert candidates[0].display_name == "Raichu"
    assert candidates[0].home_id == "00026_NORMAL"

    assert candidates[1].is_default is False
    assert candidates[1].form_slug == "alola"
    assert candidates[1].form_name == "Alola"
    assert candidates[1].display_name == "Alola Raichu"
    assert candidates[1].home_id == "00026_ALOLA"


def test_build_variety_candidates_orders_by_dex() -> None:
    details = (
        build_species_details(
            national_dex=2,
            api_name="ivysaur",
            english_name="Ivysaur",
            generation=1,
            varieties=(
                SpeciesVariety(
                    api_name="ivysaur",
                    resource_url=("https://pokeapi.co/api/v2/pokemon/2/"),
                    is_default=True,
                ),
            ),
        ),
        build_species_details(
            national_dex=1,
            api_name="bulbasaur",
            english_name="Bulbasaur",
            generation=1,
            varieties=(
                SpeciesVariety(
                    api_name="bulbasaur",
                    resource_url=("https://pokeapi.co/api/v2/pokemon/1/"),
                    is_default=True,
                ),
            ),
        ),
    )

    species = (
        build_species(
            national_dex=1,
            name="Bulbasaur",
            generation=1,
        ),
        build_species(
            national_dex=2,
            name="Ivysaur",
            generation=1,
        ),
    )

    candidates = build_variety_candidates(details, species)

    assert [candidate.national_dex for candidate in candidates] == [1, 2]


def test_build_variety_candidates_rejects_unknown_species() -> None:
    details = (
        build_species_details(
            national_dex=26,
            api_name="raichu",
            english_name="Raichu",
            generation=1,
            varieties=(
                SpeciesVariety(
                    api_name="raichu",
                    resource_url=("https://pokeapi.co/api/v2/pokemon/26/"),
                    is_default=True,
                ),
            ),
        ),
    )

    with pytest.raises(
        ValidationError,
        match="not present in the domain collection",
    ):
        build_variety_candidates(details, ())


def test_validate_candidates_rejects_duplicate_home_id() -> None:
    candidate = VarietyCandidate(
        national_dex=26,
        pokemon="Raichu",
        species_api_name="raichu",
        variety_api_name="raichu",
        form_slug="normal",
        form_name="Normal",
        display_name="Raichu",
        generation=1,
        resource_url="https://pokeapi.co/api/v2/pokemon/26/",
        is_default=True,
        home_id="00026_NORMAL",
    )

    duplicate = VarietyCandidate(
        national_dex=26,
        pokemon="Raichu",
        species_api_name="raichu",
        variety_api_name="raichu-copy",
        form_slug="normal",
        form_name="Normal",
        display_name="Raichu",
        generation=1,
        resource_url="https://example.com/pokemon/26-copy/",
        is_default=False,
        home_id="00026_NORMAL",
    )

    with pytest.raises(
        ValidationError,
        match="Duplicate candidate HOME IDs",
    ):
        validate_variety_candidates((candidate, duplicate))


def test_validate_candidates_rejects_duplicate_resource_url() -> None:
    normal = VarietyCandidate(
        national_dex=26,
        pokemon="Raichu",
        species_api_name="raichu",
        variety_api_name="raichu",
        form_slug="normal",
        form_name="Normal",
        display_name="Raichu",
        generation=1,
        resource_url="https://pokeapi.co/api/v2/pokemon/26/",
        is_default=True,
        home_id="00026_NORMAL",
    )

    alola = VarietyCandidate(
        national_dex=26,
        pokemon="Raichu",
        species_api_name="raichu",
        variety_api_name="raichu-alola",
        form_slug="alola",
        form_name="Alola",
        display_name="Alola Raichu",
        generation=1,
        resource_url="https://pokeapi.co/api/v2/pokemon/26/",
        is_default=False,
        home_id="00026_ALOLA",
    )

    with pytest.raises(
        ValidationError,
        match="Duplicate variety resource URLs",
    ):
        validate_variety_candidates((normal, alola))


def test_validate_candidates_requires_one_default() -> None:
    candidate = VarietyCandidate(
        national_dex=26,
        pokemon="Raichu",
        species_api_name="raichu",
        variety_api_name="raichu-alola",
        form_slug="alola",
        form_name="Alola",
        display_name="Alola Raichu",
        generation=1,
        resource_url=("https://pokeapi.co/api/v2/pokemon/10100/"),
        is_default=False,
        home_id="00026_ALOLA",
    )

    with pytest.raises(
        ValidationError,
        match="exactly one default variety",
    ):
        validate_variety_candidates((candidate,))
