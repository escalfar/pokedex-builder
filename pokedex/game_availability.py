from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import yaml

from pokedex.constants import GAME_COLUMNS, GameColumn
from pokedex.exceptions import ConfigurationError
from pokedex.models import GameAvailability, PokemonEntry

# YAML uses short, stable identifiers instead of the user-facing column labels.
GAME_RULE_KEYS: dict[str, GameColumn] = {
    "xy": GameColumn.XY,
    "oras": GameColumn.ORAS,
    "sm": GameColumn.SM,
    "usum": GameColumn.USUM,
    "lgpe": GameColumn.LGPE,
    "swsh": GameColumn.SWSH,
    "pla": GameColumn.PLA,
    "bdsp": GameColumn.BDSP,
    "sv": GameColumn.SV,
    "za": GameColumn.ZA,
}


@dataclass(frozen=True, slots=True)
class GameRule:
    """Availability rules for one supported game pair.

    ``national_dex`` is useful when every retained variant of a species can be
    obtained in the game. ``home_ids`` and ``excluded_home_ids`` provide the
    form-level precision required for regional and special variants.
    """

    national_dex: frozenset[int]
    national_dex_ranges: tuple[tuple[int, int], ...]
    home_ids: frozenset[str]
    excluded_home_ids: frozenset[str]
    complete: bool = False

    def includes_national_dex(self, national_dex: int) -> bool:
        """Return whether a species-level rule includes this Pokédex number.

        Explicit numbers and inclusive ranges are intentionally supported at
        the same time. Ranges keep large regional Pokédex rules readable, while
        individual numbers remain useful for isolated additions.
        """
        return national_dex in self.national_dex or any(
            start <= national_dex <= end for start, end in self.national_dex_ranges
        )


@dataclass(frozen=True, slots=True)
class GameAvailabilityRules:
    """Validated game-availability catalog loaded from YAML."""

    complete: bool
    games: dict[GameColumn, GameRule]

    @classmethod
    def from_yaml(cls, path: Path) -> GameAvailabilityRules:
        """Load and validate the availability catalog."""
        if not path.is_file():
            raise ConfigurationError(f"Game availability file does not exist: {path}")

        try:
            with path.open("r", encoding="utf-8") as file:
                payload: Any = yaml.safe_load(file)
        except (OSError, yaml.YAMLError) as error:
            raise ConfigurationError(
                f"Unable to load game availability rules: {path}"
            ) from error

        if not isinstance(payload, dict):
            raise ConfigurationError(
                "Game availability rules must contain a YAML object."
            )

        complete = payload.get("complete", False)
        if not isinstance(complete, bool):
            raise ConfigurationError(
                "Game availability field 'complete' must be boolean."
            )

        games_payload = payload.get("games")
        if not isinstance(games_payload, dict):
            raise ConfigurationError(
                "Game availability rules must contain a 'games' object."
            )

        parsed_games: dict[GameColumn, GameRule] = {}
        unexpected_keys = sorted(set(games_payload) - set(GAME_RULE_KEYS))
        if unexpected_keys:
            raise ConfigurationError(
                "Unsupported game availability keys: "
                f"{', '.join(str(key) for key in unexpected_keys)}"
            )

        for yaml_key, game in GAME_RULE_KEYS.items():
            raw_rule = games_payload.get(yaml_key)
            if not isinstance(raw_rule, dict):
                raise ConfigurationError(
                    f"Game availability rule '{yaml_key}' must be an object."
                )

            parsed_games[game] = GameRule(
                national_dex=_read_positive_integer_set(
                    raw_rule,
                    "national_dex",
                    yaml_key,
                ),
                national_dex_ranges=_read_dex_ranges(
                    raw_rule,
                    "national_dex_ranges",
                    yaml_key,
                ),
                home_ids=_read_string_set(raw_rule, "home_ids", yaml_key),
                excluded_home_ids=_read_string_set(
                    raw_rule,
                    "excluded_home_ids",
                    yaml_key,
                ),
                complete=_read_optional_bool(raw_rule, "complete", yaml_key),
            )

        return cls(complete=complete, games=parsed_games)


def apply_game_availability(
    entries: tuple[PokemonEntry, ...],
    rules: GameAvailabilityRules,
) -> tuple[PokemonEntry, ...]:
    """Return entries with availability values calculated from the catalog."""
    return tuple(
        replace(
            entry,
            availability=_build_entry_availability(entry, rules),
        )
        for entry in entries
    )


def _build_entry_availability(
    entry: PokemonEntry,
    rules: GameAvailabilityRules,
) -> GameAvailability:
    values: dict[GameColumn, bool] = {}

    for game in GAME_COLUMNS:
        rule = rules.games[game]

        # A form-specific exclusion always wins over species-level inclusion.
        available = (
            rule.includes_national_dex(entry.national_dex)
            or entry.home_id in rule.home_ids
        )
        if entry.home_id in rule.excluded_home_ids:
            available = False

        values[game] = available

    return GameAvailability(values=values)


def _read_positive_integer_set(
    payload: dict[str, Any],
    key: str,
    game_key: str,
) -> frozenset[int]:
    value = payload.get(key, [])
    if not isinstance(value, list):
        raise ConfigurationError(
            f"Game rule '{game_key}.{key}' must contain a YAML list."
        )

    result: set[int] = set()
    for item in value:
        if isinstance(item, bool) or not isinstance(item, int) or item <= 0:
            raise ConfigurationError(
                f"Game rule '{game_key}.{key}' may contain only " "positive integers."
            )
        result.add(item)

    return frozenset(result)


def _read_string_set(
    payload: dict[str, Any],
    key: str,
    game_key: str,
) -> frozenset[str]:
    value = payload.get(key, [])
    if not isinstance(value, list):
        raise ConfigurationError(
            f"Game rule '{game_key}.{key}' must contain a YAML list."
        )

    result: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ConfigurationError(
                f"Game rule '{game_key}.{key}' may contain only " "non-empty strings."
            )
        result.add(item.strip().upper())

    return frozenset(result)


def _read_dex_ranges(
    payload: dict[str, Any],
    key: str,
    game_key: str,
) -> tuple[tuple[int, int], ...]:
    """Read inclusive National Pokédex ranges from YAML.

    Each range is represented as a two-item list, for example ``[1, 150]``.
    Rejecting reversed or malformed ranges prevents silent over-classification.
    """
    value = payload.get(key, [])
    if not isinstance(value, list):
        raise ConfigurationError(
            f"Game rule '{game_key}.{key}' must contain a YAML list."
        )

    ranges: list[tuple[int, int]] = []
    for item in value:
        if (
            not isinstance(item, list)
            or len(item) != 2
            or any(
                isinstance(bound, bool) or not isinstance(bound, int) or bound <= 0
                for bound in item
            )
        ):
            raise ConfigurationError(
                f"Game rule '{game_key}.{key}' must contain two-item "
                "positive integer ranges."
            )

        start, end = item
        if start > end:
            raise ConfigurationError(
                f"Game rule '{game_key}.{key}' contains a reversed range: "
                f"{start}-{end}."
            )
        ranges.append((start, end))

    return tuple(ranges)


def _read_optional_bool(
    payload: dict[str, Any],
    key: str,
    game_key: str,
) -> bool:
    """Read an optional boolean field from one game rule.

    Per-game completeness lets an audited game classify every rule omission as
    an explicit ``FALSE`` without requiring thousands of negative HOME IDs.
    """
    value = payload.get(key, False)
    if not isinstance(value, bool):
        raise ConfigurationError(f"Game rule '{game_key}.{key}' must be boolean.")
    return value
