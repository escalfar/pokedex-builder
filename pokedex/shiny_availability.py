from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import yaml

from pokedex.exceptions import ConfigurationError
from pokedex.models import PokemonEntry


@dataclass(frozen=True, slots=True)
class ShinyAvailabilityRules:
    """Curated rules for obtaining shiny Pokémon without event distribution.

    Species-level inclusions cover cases where every retained HOME variant can
    be obtained shiny through permanent gameplay. Inclusive National Dex ranges
    keep large audited tranches readable, while HOME IDs handle form-specific
    exceptions and explicit shiny locks.
    """

    complete: bool
    national_dex: frozenset[int]
    national_dex_ranges: tuple[tuple[int, int], ...]
    home_ids: frozenset[str]
    excluded_home_ids: frozenset[str]

    @classmethod
    def from_yaml(cls, path: Path) -> ShinyAvailabilityRules:
        """Load and validate the shiny availability catalog."""
        if not path.is_file():
            raise ConfigurationError(f"Shiny availability file does not exist: {path}")

        try:
            with path.open("r", encoding="utf-8") as file:
                payload: Any = yaml.safe_load(file)
        except (OSError, yaml.YAMLError) as error:
            raise ConfigurationError(
                f"Unable to load shiny availability rules: {path}"
            ) from error

        if not isinstance(payload, dict):
            raise ConfigurationError(
                "Shiny availability rules must contain a YAML object."
            )

        complete = payload.get("complete", False)
        if not isinstance(complete, bool):
            raise ConfigurationError(
                "Shiny availability field 'complete' must be boolean."
            )

        return cls(
            complete=complete,
            national_dex=_read_positive_integer_set(payload, "national_dex"),
            national_dex_ranges=_read_dex_ranges(payload, "national_dex_ranges"),
            home_ids=_read_string_set(payload, "home_ids"),
            excluded_home_ids=_read_string_set(payload, "excluded_home_ids"),
        )

    def includes_national_dex(self, national_dex: int) -> bool:
        """Return whether a species-level shiny rule includes this number."""
        return national_dex in self.national_dex or any(
            start <= national_dex <= end for start, end in self.national_dex_ranges
        )


def apply_shiny_availability(
    entries: tuple[PokemonEntry, ...],
    rules: ShinyAvailabilityRules,
) -> tuple[PokemonEntry, ...]:
    """Return entries with the ``Obtenible`` value calculated from rules."""
    return tuple(
        replace(
            entry,
            obtainable_shiny=_is_obtainable_shiny(entry, rules),
        )
        for entry in entries
    )


def _is_obtainable_shiny(
    entry: PokemonEntry,
    rules: ShinyAvailabilityRules,
) -> bool:
    # A form-specific exclusion always wins. This allows a broad species range
    # to remain readable while preserving explicit shiny-lock exceptions.
    obtainable = (
        rules.includes_national_dex(entry.national_dex)
        or entry.home_id in rules.home_ids
    )

    if entry.home_id in rules.excluded_home_ids:
        return False

    return obtainable


def _read_positive_integer_set(
    payload: dict[str, Any],
    key: str,
) -> frozenset[int]:
    value = payload.get(key, [])
    if not isinstance(value, list):
        raise ConfigurationError(f"Shiny rule '{key}' must contain a YAML list.")

    result: set[int] = set()
    for item in value:
        if isinstance(item, bool) or not isinstance(item, int) or item <= 0:
            raise ConfigurationError(
                f"Shiny rule '{key}' may contain only positive integers."
            )
        result.add(item)

    return frozenset(result)


def _read_dex_ranges(
    payload: dict[str, Any],
    key: str,
) -> tuple[tuple[int, int], ...]:
    """Read inclusive National Pokédex ranges from the shiny catalog."""
    value = payload.get(key, [])
    if not isinstance(value, list):
        raise ConfigurationError(f"Shiny rule '{key}' must contain a YAML list.")

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
                f"Shiny rule '{key}' must contain two-item positive integer ranges."
            )

        start, end = item
        if start > end:
            raise ConfigurationError(
                f"Shiny rule '{key}' contains a reversed range: {start}-{end}."
            )
        ranges.append((start, end))

    return tuple(ranges)


def _read_string_set(
    payload: dict[str, Any],
    key: str,
) -> frozenset[str]:
    value = payload.get(key, [])
    if not isinstance(value, list):
        raise ConfigurationError(f"Shiny rule '{key}' must contain a YAML list.")

    result: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ConfigurationError(
                f"Shiny rule '{key}' may contain only non-empty strings."
            )
        result.add(item.strip().upper())

    return frozenset(result)
