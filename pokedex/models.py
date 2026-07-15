from dataclasses import dataclass, field
from typing import Any

from pokedex.constants import GAME_COLUMNS, GameColumn


@dataclass(frozen=True, slots=True)
class GameAvailability:
    """Availability of a Pokémon form in the supported games."""

    values: dict[GameColumn, bool] = field(
        default_factory=lambda: {game: False for game in GAME_COLUMNS}
    )

    def __post_init__(self) -> None:
        missing_games = set(GAME_COLUMNS) - set(self.values)
        unexpected_games = set(self.values) - set(GAME_COLUMNS)

        if missing_games:
            missing = ", ".join(sorted(game.value for game in missing_games))
            raise ValueError(f"Missing availability values for: {missing}")

        if unexpected_games:
            unexpected = ", ".join(str(game) for game in unexpected_games)
            raise ValueError(f"Unexpected availability keys: {unexpected}")

        if any(not isinstance(value, bool) for value in self.values.values()):
            raise TypeError("All game availability values must be boolean.")

    def is_available_in(self, game: GameColumn) -> bool:
        """Return whether the Pokémon is available in the selected game."""
        return self.values[game]

    def to_dict(self) -> dict[str, bool]:
        """Return availability using the final output column names."""
        return {game.value: self.values[game] for game in GAME_COLUMNS}


@dataclass(frozen=True, slots=True)
class PokemonSpecies:
    """Base information about a National Pokédex species."""

    national_dex: int
    name: str
    generation: int
    is_legendary: bool = False
    is_mythical: bool = False

    def __post_init__(self) -> None:
        if self.national_dex <= 0:
            raise ValueError("National Pokédex number must be greater than zero.")

        if not self.name.strip():
            raise ValueError("Species name cannot be empty.")

        if self.generation <= 0:
            raise ValueError("Generation must be greater than zero.")

    @property
    def is_legendary_or_mythical(self) -> bool:
        """Return whether the species is legendary or mythical."""
        return self.is_legendary or self.is_mythical


@dataclass(frozen=True, slots=True)
class PokemonForm:
    """A storable Pokémon form or variant."""

    national_dex: int
    pokemon: str
    form: str
    name: str
    generation: int
    home_id: str

    def __post_init__(self) -> None:
        if self.national_dex <= 0:
            raise ValueError("National Pokédex number must be greater than zero.")

        for field_name, value in (
            ("pokemon", self.pokemon),
            ("form", self.form),
            ("name", self.name),
            ("home_id", self.home_id),
        ):
            if not value.strip():
                raise ValueError(f"{field_name} cannot be empty.")

        if self.generation <= 0:
            raise ValueError("Generation must be greater than zero.")


@dataclass(frozen=True, slots=True)
class PokemonEntry:
    """Final row included in the generated Pokédex."""

    national_dex: int
    pokemon: str
    form: str
    name: str
    generation: int
    home_id: str
    availability: GameAvailability
    legendary_mythical: bool
    obtainable_shiny: bool

    def __post_init__(self) -> None:
        if self.national_dex <= 0:
            raise ValueError("National Pokédex number must be greater than zero.")

        if self.generation <= 0:
            raise ValueError("Generation must be greater than zero.")

        for field_name, value in (
            ("pokemon", self.pokemon),
            ("form", self.form),
            ("name", self.name),
            ("home_id", self.home_id),
        ):
            if not value.strip():
                raise ValueError(f"{field_name} cannot be empty.")

    def to_dict(self) -> dict[str, Any]:
        """Convert the entry to the final export structure."""
        row: dict[str, Any] = {
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
