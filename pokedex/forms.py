from __future__ import annotations

from collections.abc import Iterable

from pokedex.exceptions import ValidationError
from pokedex.models import PokemonForm
from pokedex.varieties import VarietyCandidate


def build_pokemon_forms(
    candidates: Iterable[VarietyCandidate],
) -> tuple[PokemonForm, ...]:
    """Convert normalized variety candidates into domain form models."""
    forms = tuple(
        PokemonForm(
            national_dex=candidate.national_dex,
            pokemon=candidate.pokemon,
            form=candidate.form_name,
            name=candidate.display_name,
            generation=candidate.generation,
            home_id=candidate.home_id,
        )
        for candidate in candidates
    )

    ordered_forms = tuple(
        sorted(
            forms,
            key=lambda item: (
                item.national_dex,
                item.home_id != f"{item.national_dex:05d}_NORMAL",
                item.home_id,
            ),
        )
    )

    validate_pokemon_forms(ordered_forms)

    return ordered_forms


def validate_pokemon_forms(
    forms: tuple[PokemonForm, ...],
) -> None:
    """Validate integrity rules for the preliminary form collection."""
    if not forms:
        raise ValidationError("Pokémon form collection cannot be empty.")

    _validate_unique_home_ids(forms)
    _validate_unique_names(forms)
    _validate_species_consistency(forms)
    _validate_one_normal_form_per_species(forms)
    _validate_deterministic_order(forms)


def _validate_unique_home_ids(
    forms: tuple[PokemonForm, ...],
) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()

    for form in forms:
        if form.home_id in seen:
            duplicates.add(form.home_id)

        seen.add(form.home_id)

    if duplicates:
        values = ", ".join(sorted(duplicates))
        raise ValidationError(f"Duplicate Pokémon form HOME IDs found: {values}")


def _validate_unique_names(
    forms: tuple[PokemonForm, ...],
) -> None:
    names: dict[str, list[str]] = {}

    for form in forms:
        normalized_name = form.name.casefold()
        names.setdefault(normalized_name, []).append(form.home_id)

    duplicates = {
        name: home_ids for name, home_ids in names.items() if len(home_ids) > 1
    }

    if duplicates:
        details = "; ".join(
            f"{name}: {', '.join(home_ids)}"
            for name, home_ids in sorted(duplicates.items())
        )
        raise ValidationError(f"Duplicate Pokémon form names found: {details}")


def _validate_species_consistency(
    forms: tuple[PokemonForm, ...],
) -> None:
    pokemon_by_dex: dict[int, set[str]] = {}

    for form in forms:
        pokemon_by_dex.setdefault(
            form.national_dex,
            set(),
        ).add(form.pokemon)

    inconsistent = {
        national_dex: names
        for national_dex, names in pokemon_by_dex.items()
        if len(names) > 1
    }

    if inconsistent:
        details = "; ".join(
            f"{national_dex}: {', '.join(sorted(names))}"
            for national_dex, names in sorted(inconsistent.items())
        )
        raise ValidationError(
            "Forms with the same National Dex must share the same "
            f"Pokémon name: {details}"
        )


def _validate_one_normal_form_per_species(
    forms: tuple[PokemonForm, ...],
) -> None:
    counts: dict[int, int] = {}

    for form in forms:
        counts.setdefault(form.national_dex, 0)

        expected_normal_id = f"{form.national_dex:05d}_NORMAL"

        if form.home_id == expected_normal_id:
            counts[form.national_dex] += 1

    invalid = {
        national_dex: count for national_dex, count in counts.items() if count != 1
    }

    if invalid:
        details = ", ".join(
            f"{national_dex}={count}" for national_dex, count in sorted(invalid.items())
        )
        raise ValidationError(
            "Each species must contain exactly one normal form: " f"{details}"
        )


def _validate_deterministic_order(
    forms: tuple[PokemonForm, ...],
) -> None:
    expected = tuple(
        sorted(
            forms,
            key=lambda item: (
                item.national_dex,
                item.home_id != f"{item.national_dex:05d}_NORMAL",
                item.home_id,
            ),
        )
    )

    if forms != expected:
        raise ValidationError("Pokémon forms are not in deterministic order.")
