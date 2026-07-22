import pytest

from pokedex.constants import Gender
from pokedex.entries import (
    build_pokemon_entries,
    sort_pokemon_entries,
    validate_pokemon_entries,
)
from pokedex.exceptions import ValidationError
from pokedex.models import (
    GameAvailability,
    PokemonEntry,
    PokemonSpecies,
    PokemonVariant,
)


def build_species(
    *,
    national_dex: int = 25,
    name: str = "Pikachu",
    generation: int = 1,
    is_legendary: bool = False,
    is_mythical: bool = False,
) -> PokemonSpecies:
    return PokemonSpecies(
        national_dex=national_dex,
        name=name,
        generation=generation,
        is_legendary=is_legendary,
        is_mythical=is_mythical,
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


def build_entry(
    *,
    national_dex: int = 25,
    pokemon: str = "Pikachu",
    form: str = "Normal",
    name: str = "Pikachu",
    generation: int = 1,
    home_id: str = "00025_NORMAL_NONE",
    gender: Gender = Gender.NONE,
) -> PokemonEntry:
    return PokemonEntry(
        national_dex=national_dex,
        pokemon=pokemon,
        form=form,
        name=name,
        generation=generation,
        home_id=home_id,
        gender=gender,
        availability=GameAvailability(),
        legendary_mythical=False,
        obtainable_shiny=False,
    )


def test_build_entries_converts_variant() -> None:
    entries = build_pokemon_entries(
        (build_variant(),),
        (build_species(),),
    )

    assert len(entries) == 1

    entry = entries[0]

    assert entry.national_dex == 25
    assert entry.pokemon == "Pikachu"
    assert entry.form == "Normal"
    assert entry.name == "Pikachu"
    assert entry.generation == 1
    assert entry.home_id == "00025_NORMAL_NONE"
    assert entry.gender == Gender.NONE
    assert entry.legendary_mythical is False
    assert entry.obtainable_shiny is False


def test_build_entries_preserves_variant_generation() -> None:
    variant = build_variant(
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

    species = build_species(
        national_dex=26,
        name="Raichu",
        generation=1,
    )

    entries = build_pokemon_entries(
        (variant,),
        (species,),
    )

    assert entries[0].generation == 7


def test_build_entries_preserves_legendary_flag() -> None:
    entries = build_pokemon_entries(
        (
            build_variant(
                national_dex=150,
                pokemon="Mewtwo",
                species_api_name="mewtwo",
                variety_api_name="mewtwo",
                display_name="Mewtwo",
                resource_url=("https://pokeapi.co/api/v2/" "pokemon/150/"),
            ),
        ),
        (
            build_species(
                national_dex=150,
                name="Mewtwo",
                is_legendary=True,
            ),
        ),
    )

    assert entries[0].legendary_mythical is True


def test_build_entries_rejects_unknown_species() -> None:
    with pytest.raises(
        ValidationError,
        match="no matching species",
    ):
        build_pokemon_entries(
            (build_variant(),),
            (),
        )


def test_build_entries_rejects_species_name_mismatch() -> None:
    with pytest.raises(
        ValidationError,
        match="names do not match",
    ):
        build_pokemon_entries(
            (build_variant(),),
            (
                build_species(
                    name="Different",
                ),
            ),
        )


def test_sort_entries_orders_by_national_dex() -> None:
    pikachu = build_entry()

    raichu = build_entry(
        national_dex=26,
        pokemon="Raichu",
        name="Raichu",
        home_id="00026_NORMAL_NONE",
    )

    ordered = sort_pokemon_entries(
        (
            raichu,
            pikachu,
        )
    )

    assert ordered == (
        pikachu,
        raichu,
    )


def test_sort_entries_orders_normal_before_other_forms() -> None:
    normal = build_entry(
        national_dex=26,
        pokemon="Raichu",
        name="Raichu",
        home_id="00026_NORMAL_NONE",
    )

    alolan = build_entry(
        national_dex=26,
        pokemon="Raichu",
        form="Alolan",
        name="Alolan Raichu",
        generation=7,
        home_id="00026_ALOLA_NONE",
    )

    ordered = sort_pokemon_entries(
        (
            alolan,
            normal,
        )
    )

    assert ordered == (
        normal,
        alolan,
    )


def test_sort_entries_orders_female_before_male() -> None:
    male = build_entry(
        form="Male",
        name="Male Pikachu",
        home_id="00025_NORMAL_MALE",
        gender=Gender.MALE,
    )

    female = build_entry(
        form="Female",
        name="Female Pikachu",
        home_id="00025_NORMAL_FEMALE",
        gender=Gender.FEMALE,
    )

    ordered = sort_pokemon_entries(
        (
            female,
            male,
        )
    )

    assert ordered == (
        female,
        male,
    )


def test_sort_entries_places_unown_a_first() -> None:
    unown_a = build_entry(
        national_dex=201,
        pokemon="Unown",
        form="A",
        name="Unown (A)",
        generation=2,
        home_id="00201_NORMAL_NONE",
    )
    unown_b = build_entry(
        national_dex=201,
        pokemon="Unown",
        form="B",
        name="Unown (B)",
        generation=2,
        home_id="00201_B_NONE",
    )

    ordered = sort_pokemon_entries((unown_b, unown_a))

    assert ordered == (unown_a, unown_b)


def test_sort_entries_places_special_vivillon_patterns_last() -> None:
    meadow = build_entry(
        national_dex=666,
        pokemon="Vivillon",
        form="Meadow Pattern",
        name="Meadow Pattern Vivillon",
        generation=6,
        home_id="00666_NORMAL_NONE",
    )
    tundra = build_entry(
        national_dex=666,
        pokemon="Vivillon",
        form="Tundra Pattern",
        name="Tundra Pattern Vivillon",
        generation=6,
        home_id="00666_TUNDRA_PATTERN_NONE",
    )
    fancy = build_entry(
        national_dex=666,
        pokemon="Vivillon",
        form="Fancy Pattern",
        name="Fancy Pattern Vivillon",
        generation=6,
        home_id="00666_FANCY_PATTERN_NONE",
    )
    poke_ball = build_entry(
        national_dex=666,
        pokemon="Vivillon",
        form="Poké Ball Pattern",
        name="Poké Ball Pattern Vivillon",
        generation=6,
        home_id="00666_POKE_BALL_PATTERN_NONE",
    )

    ordered = sort_pokemon_entries((poke_ball, fancy, tundra, meadow))

    assert ordered == (meadow, tundra, fancy, poke_ball)


def test_validate_entries_accepts_ungendered_entry() -> None:
    validate_pokemon_entries((build_entry(),))


def test_validate_entries_accepts_gender_pair() -> None:
    male = build_entry(
        form="Male",
        name="Male Pikachu",
        home_id="00025_NORMAL_MALE",
        gender=Gender.MALE,
    )

    female = build_entry(
        form="Female",
        name="Female Pikachu",
        home_id="00025_NORMAL_FEMALE",
        gender=Gender.FEMALE,
    )

    validate_pokemon_entries(
        (
            female,
            male,
        )
    )


def test_validate_entries_rejects_incomplete_gender_pair() -> None:
    female = build_entry(
        form="Female",
        name="Female Pikachu",
        home_id="00025_NORMAL_FEMALE",
        gender=Gender.FEMALE,
    )

    with pytest.raises(
        ValidationError,
        match="male/female pair",
    ):
        validate_pokemon_entries((female,))


def test_validate_entries_rejects_duplicate_home_ids() -> None:
    first = build_entry()

    duplicate = build_entry(
        name="Copy Pikachu",
    )

    with pytest.raises(
        ValidationError,
        match="Duplicate Pokémon entry HOME IDs",
    ):
        validate_pokemon_entries(
            (
                first,
                duplicate,
            )
        )


def test_validate_entries_rejects_duplicate_names() -> None:
    first = build_entry()

    second = build_entry(
        national_dex=26,
        pokemon="Raichu",
        name="PIKACHU",
        home_id="00026_NORMAL_NONE",
    )

    with pytest.raises(
        ValidationError,
        match="Duplicate Pokémon entry names",
    ):
        validate_pokemon_entries(
            (
                first,
                second,
            )
        )


def test_validate_entries_rejects_inconsistent_species_name() -> None:
    first = build_entry(
        national_dex=26,
        pokemon="Raichu",
        name="Raichu",
        home_id="00026_NORMAL_NONE",
    )

    second = build_entry(
        national_dex=26,
        pokemon="Different",
        form="Alolan",
        name="Alolan Raichu",
        generation=7,
        home_id="00026_ALOLA_NONE",
    )

    with pytest.raises(
        ValidationError,
        match="must share the same Pokémon name",
    ):
        validate_pokemon_entries(
            (
                first,
                second,
            )
        )


def test_validate_entries_rejects_unordered_collection() -> None:
    pikachu = build_entry()

    raichu = build_entry(
        national_dex=26,
        pokemon="Raichu",
        name="Raichu",
        home_id="00026_NORMAL_NONE",
    )

    with pytest.raises(
        ValidationError,
        match="deterministic order",
    ):
        validate_pokemon_entries(
            (
                raichu,
                pikachu,
            )
        )


def test_validate_entries_rejects_empty_collection() -> None:
    with pytest.raises(
        ValidationError,
        match="cannot be empty",
    ):
        validate_pokemon_entries(())


def test_sort_entries_keeps_alcremie_normal_first() -> None:
    """The logical NORMAL HOME ID must not move Strawberry Sweet to the end."""
    entries = (
        build_entry(
            national_dex=869,
            pokemon="Alcremie",
            form="Berry Sweet",
            name="Alcremie (Berry Sweet)",
            generation=8,
            home_id="00869_BERRY_SWEET_NONE",
        ),
        build_entry(
            national_dex=869,
            pokemon="Alcremie",
            form="Strawberry Sweet",
            name="Alcremie (Strawberry Sweet)",
            generation=8,
            home_id="00869_NORMAL_NONE",
        ),
        build_entry(
            national_dex=869,
            pokemon="Alcremie",
            form="Ribbon Sweet",
            name="Alcremie (Ribbon Sweet)",
            generation=8,
            home_id="00869_RIBBON_SWEET_NONE",
        ),
    )

    ordered = sort_pokemon_entries(entries)

    assert [entry.form for entry in ordered] == [
        "Strawberry Sweet",
        "Berry Sweet",
        "Ribbon Sweet",
    ]
