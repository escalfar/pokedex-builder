import pytest

from pokedex.exceptions import ValidationError
from pokedex.forms import build_pokemon_forms, validate_pokemon_forms
from pokedex.models import PokemonForm
from pokedex.varieties import VarietyCandidate


def build_candidate(
    *,
    national_dex: int = 26,
    pokemon: str = "Raichu",
    form_name: str = "Normal",
    display_name: str = "Raichu",
    generation: int = 1,
    home_id: str = "00026_NORMAL",
    is_default: bool = True,
) -> VarietyCandidate:
    form_slug = home_id.split("_", maxsplit=1)[1].casefold().replace("_", "-")

    return VarietyCandidate(
        national_dex=national_dex,
        pokemon=pokemon,
        species_api_name=pokemon.casefold().replace(" ", "-"),
        variety_api_name=(
            pokemon.casefold().replace(" ", "-")
            if is_default
            else f"{pokemon.casefold().replace(' ', '-')}-{form_slug}"
        ),
        form_slug=form_slug,
        form_name=form_name,
        display_name=display_name,
        generation=generation,
        resource_url=f"https://example.com/pokemon/{home_id}",
        is_default=is_default,
        home_id=home_id,
    )


def test_build_pokemon_forms_converts_candidates() -> None:
    candidates = (
        build_candidate(),
        build_candidate(
            form_name="Alolan",
            display_name="Alolan Raichu",
            generation=7,
            home_id="00026_ALOLA",
            is_default=False,
        ),
    )

    forms = build_pokemon_forms(candidates)

    assert len(forms) == 2

    assert forms[0].national_dex == 26
    assert forms[0].pokemon == "Raichu"
    assert forms[0].form == "Normal"
    assert forms[0].name == "Raichu"
    assert forms[0].generation == 1
    assert forms[0].home_id == "00026_NORMAL"

    assert forms[1].form == "Alolan"
    assert forms[1].name == "Alolan Raichu"
    assert forms[1].generation == 7


def test_build_pokemon_forms_orders_normal_first() -> None:
    candidates = (
        build_candidate(
            form_name="Alolan",
            display_name="Alolan Raichu",
            generation=7,
            home_id="00026_ALOLA",
            is_default=False,
        ),
        build_candidate(),
    )

    forms = build_pokemon_forms(candidates)

    assert [form.home_id for form in forms] == [
        "00026_NORMAL",
        "00026_ALOLA",
    ]


def test_build_pokemon_forms_orders_by_national_dex() -> None:
    candidates = (
        build_candidate(
            national_dex=26,
            pokemon="Raichu",
            home_id="00026_NORMAL",
        ),
        build_candidate(
            national_dex=25,
            pokemon="Pikachu",
            display_name="Pikachu",
            home_id="00025_NORMAL",
        ),
    )

    forms = build_pokemon_forms(candidates)

    assert [form.national_dex for form in forms] == [25, 26]


def test_validate_forms_rejects_empty_collection() -> None:
    with pytest.raises(
        ValidationError,
        match="cannot be empty",
    ):
        validate_pokemon_forms(())


def test_validate_forms_rejects_duplicate_home_ids() -> None:
    normal = PokemonForm(
        national_dex=26,
        pokemon="Raichu",
        form="Normal",
        name="Raichu",
        generation=1,
        home_id="00026_NORMAL",
    )

    duplicate = PokemonForm(
        national_dex=26,
        pokemon="Raichu",
        form="Duplicate",
        name="Duplicate Raichu",
        generation=1,
        home_id="00026_NORMAL",
    )

    with pytest.raises(
        ValidationError,
        match="Duplicate Pokémon form HOME IDs",
    ):
        validate_pokemon_forms((normal, duplicate))


def test_validate_forms_rejects_duplicate_names() -> None:
    normal = PokemonForm(
        national_dex=26,
        pokemon="Raichu",
        form="Normal",
        name="Raichu",
        generation=1,
        home_id="00026_NORMAL",
    )

    duplicate_name = PokemonForm(
        national_dex=27,
        pokemon="Sandshrew",
        form="Normal",
        name="RAICHU",
        generation=1,
        home_id="00027_NORMAL",
    )

    with pytest.raises(
        ValidationError,
        match="Duplicate Pokémon form names",
    ):
        validate_pokemon_forms((normal, duplicate_name))


def test_validate_forms_rejects_inconsistent_species_name() -> None:
    normal = PokemonForm(
        national_dex=26,
        pokemon="Raichu",
        form="Normal",
        name="Raichu",
        generation=1,
        home_id="00026_NORMAL",
    )

    inconsistent = PokemonForm(
        national_dex=26,
        pokemon="Different Pokémon",
        form="Alolan",
        name="Alolan Raichu",
        generation=7,
        home_id="00026_ALOLA",
    )

    with pytest.raises(
        ValidationError,
        match="must share the same Pokémon name",
    ):
        validate_pokemon_forms((normal, inconsistent))


def test_validate_forms_requires_normal_form() -> None:
    alolan = PokemonForm(
        national_dex=26,
        pokemon="Raichu",
        form="Alolan",
        name="Alolan Raichu",
        generation=7,
        home_id="00026_ALOLA",
    )

    with pytest.raises(
        ValidationError,
        match="exactly one normal form",
    ):
        validate_pokemon_forms((alolan,))


def test_validate_forms_rejects_unordered_collection() -> None:
    alolan = PokemonForm(
        national_dex=26,
        pokemon="Raichu",
        form="Alolan",
        name="Alolan Raichu",
        generation=7,
        home_id="00026_ALOLA",
    )

    normal = PokemonForm(
        national_dex=26,
        pokemon="Raichu",
        form="Normal",
        name="Raichu",
        generation=1,
        home_id="00026_NORMAL",
    )

    with pytest.raises(
        ValidationError,
        match="deterministic order",
    ):
        validate_pokemon_forms((alolan, normal))


def test_validate_forms_accepts_valid_collection() -> None:
    forms = (
        PokemonForm(
            national_dex=26,
            pokemon="Raichu",
            form="Normal",
            name="Raichu",
            generation=1,
            home_id="00026_NORMAL",
        ),
        PokemonForm(
            national_dex=26,
            pokemon="Raichu",
            form="Alolan",
            name="Alolan Raichu",
            generation=7,
            home_id="00026_ALOLA",
        ),
    )

    validate_pokemon_forms(forms)
