from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias

from pokedex.constants import GAME_COLUMNS, Gender, GameColumn

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


@dataclass(frozen=True, slots=True)
class GameAvailability:
    """Availability of a Pokémon variant in the supported games."""

    values: dict[GameColumn, bool] = field(
        default_factory=lambda: {game: False for game in GAME_COLUMNS}
    )

    def __post_init__(self) -> None:
        expected_games = set(GAME_COLUMNS)
        actual_games = set(self.values)

        missing_games = expected_games - actual_games
        unexpected_games = actual_games - expected_games

        if missing_games:
            missing = ", ".join(sorted(game.value for game in missing_games))
            raise ValueError(f"Missing availability values for: {missing}")

        if unexpected_games:
            unexpected = ", ".join(sorted(str(game) for game in unexpected_games))
            raise ValueError(f"Unexpected availability keys: {unexpected}")

        if any(not isinstance(value, bool) for value in self.values.values()):
            raise TypeError("All game availability values must be boolean.")

    def is_available_in(
        self,
        game: GameColumn,
    ) -> bool:
        """Return whether the variant is available in a game."""
        return self.values[game]

    def to_dict(self) -> dict[str, bool]:
        """Return availability using final output column names."""
        return {game.value: self.values[game] for game in GAME_COLUMNS}


@dataclass(frozen=True, slots=True)
class PokemonSpecies:
    """Base information about one National Pokédex species."""

    national_dex: int
    name: str
    generation: int
    is_legendary: bool = False
    is_mythical: bool = False

    def __post_init__(self) -> None:
        _validate_positive_integer(
            self.national_dex,
            "National Pokédex number",
        )
        _validate_non_empty_text(
            self.name,
            "Species name",
        )
        _validate_positive_integer(
            self.generation,
            "Generation",
        )
        _validate_boolean(
            self.is_legendary,
            "is_legendary",
        )
        _validate_boolean(
            self.is_mythical,
            "is_mythical",
        )

    @property
    def is_legendary_or_mythical(self) -> bool:
        """Return whether the species is legendary or mythical."""
        return self.is_legendary or self.is_mythical


@dataclass(frozen=True, slots=True)
class PokemonVariant:
    """One Pokémon form and gender combination stored by the project."""

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
    gender: Gender = Gender.NONE

    def __post_init__(self) -> None:
        _validate_positive_integer(
            self.national_dex,
            "National Pokédex number",
        )
        _validate_non_empty_text(
            self.pokemon,
            "Pokemon",
        )
        _validate_non_empty_text(
            self.species_api_name,
            "Species API name",
        )
        _validate_non_empty_text(
            self.variety_api_name,
            "Variety API name",
        )
        _validate_non_empty_text(
            self.form_slug,
            "Form slug",
        )
        _validate_non_empty_text(
            self.form_name,
            "Form name",
        )
        _validate_non_empty_text(
            self.display_name,
            "Display name",
        )
        _validate_positive_integer(
            self.generation,
            "Generation",
        )
        _validate_non_empty_text(
            self.resource_url,
            "Resource URL",
        )
        _validate_boolean(
            self.is_default,
            "is_default",
        )

        if not isinstance(self.gender, Gender):
            raise TypeError("gender must be a Gender value.")

    @property
    def home_id(self) -> str:
        """Return the deterministic identifier for this variant."""
        normalized_form = self.form_slug.strip().casefold().replace("-", "_").upper()

        return (
            f"{self.national_dex:05d}_"
            f"{normalized_form}_"
            f"{self.gender.value.upper()}"
        )

    @property
    def logical_key(self) -> tuple[int, str, Gender]:
        """Return the dimensions that uniquely identify the variant."""
        return (
            self.national_dex,
            self.form_slug.casefold(),
            self.gender,
        )

    @property
    def is_normal_form(self) -> bool:
        """Return whether the variant belongs to the normal form."""
        return self.form_slug.casefold() == "normal"


@dataclass(frozen=True, slots=True)
class PokemonEntry:
    """Final row exported to CSV, JSON, and Excel."""

    national_dex: int
    pokemon: str
    form: str
    name: str
    generation: int
    home_id: str
    gender: Gender
    availability: GameAvailability
    legendary_mythical: bool
    obtainable_shiny: bool

    def __post_init__(self) -> None:
        _validate_positive_integer(
            self.national_dex,
            "National Pokédex number",
        )
        _validate_non_empty_text(
            self.pokemon,
            "Pokemon",
        )
        _validate_non_empty_text(
            self.form,
            "Form",
        )
        _validate_non_empty_text(
            self.name,
            "Name",
        )
        _validate_positive_integer(
            self.generation,
            "Generation",
        )
        _validate_non_empty_text(
            self.home_id,
            "HOME ID",
        )
        _validate_boolean(
            self.legendary_mythical,
            "legendary_mythical",
        )
        _validate_boolean(
            self.obtainable_shiny,
            "obtainable_shiny",
        )

        if not isinstance(self.gender, Gender):
            raise TypeError("gender must be a Gender value.")

        if not isinstance(
            self.availability,
            GameAvailability,
        ):
            raise TypeError("availability must be a GameAvailability instance.")

    def to_dict(self) -> dict[str, JsonValue]:
        """Convert the entry to the final export structure."""
        row: dict[str, JsonValue] = {
            "Nat Dex": self.national_dex,
            "Pokemon": self.pokemon,
            "Forma": self.form,
            "Nombre": self.name,
            "Gen": self.generation,
            "ID HOME": self.home_id,
        }

        row.update(self.availability.to_dict())
        row["Legendario/Mítico"] = self.legendary_mythical
        row["Obtenible"] = self.obtainable_shiny

        return row


def _validate_positive_integer(
    value: int,
    field_name: str,
) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer.")

    if value <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")


def _validate_non_empty_text(
    value: str,
    field_name: str,
) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string.")

    if not value.strip():
        raise ValueError(f"{field_name} cannot be empty.")


def _validate_boolean(
    value: bool,
    field_name: str,
) -> None:
    if not isinstance(value, bool):
        raise TypeError(f"{field_name} must be boolean.")
