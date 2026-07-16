from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pokedex.constants import GAME_COLUMNS, GameColumn
from pokedex.exceptions import PokedexError
from pokedex.game_availability import GameAvailabilityRules
from pokedex.models import JsonValue, PokemonEntry
from pokedex.shiny_availability import ShinyAvailabilityRules


@dataclass(frozen=True, slots=True)
class CoverageCounts:
    """Coverage totals for one catalog or one supported game.

    ``verified_true`` and ``verified_false`` are explicit rule decisions.
    ``unknown`` means that the catalog has not yet classified the entry.
    """

    total: int
    verified_true: int
    verified_false: int
    unknown: int

    @property
    def verified(self) -> int:
        """Return the total number of explicitly classified entries."""
        return self.verified_true + self.verified_false

    @property
    def percent(self) -> float:
        """Return verified coverage as a percentage of all entries."""
        if self.total == 0:
            return 100.0
        return round((self.verified / self.total) * 100.0, 2)

    def to_dict(self) -> dict[str, JsonValue]:
        """Serialize the coverage totals for JSON output."""
        return {
            "total": self.total,
            "verified": self.verified,
            "verified_true": self.verified_true,
            "verified_false": self.verified_false,
            "unknown": self.unknown,
            "percent": self.percent,
        }


@dataclass(frozen=True, slots=True)
class CatalogCoverageReport:
    """Coverage report for game and non-event shiny catalogs."""

    games: dict[GameColumn, CoverageCounts]
    shiny: CoverageCounts

    @property
    def is_complete(self) -> bool:
        """Return whether every catalog classifies every generated entry."""
        return self.shiny.unknown == 0 and all(
            counts.unknown == 0 for counts in self.games.values()
        )

    def to_dict(self) -> dict[str, JsonValue]:
        """Serialize the full coverage report."""
        return {
            "complete": self.is_complete,
            "games": {game.value: self.games[game].to_dict() for game in GAME_COLUMNS},
            "shiny": self.shiny.to_dict(),
        }


def build_catalog_coverage_report(
    entries: tuple[PokemonEntry, ...],
    game_rules: GameAvailabilityRules,
    shiny_rules: ShinyAvailabilityRules,
) -> CatalogCoverageReport:
    """Calculate explicit-rule coverage for all generated entries.

    A species-level inclusion explicitly classifies all retained variants as
    available/obtainable unless a form-specific exclusion overrides it.
    Standalone exclusions also count as explicit ``FALSE`` decisions.
    """
    game_coverage = {
        game: _build_game_coverage(entries, game_rules, game) for game in GAME_COLUMNS
    }

    return CatalogCoverageReport(
        games=game_coverage,
        shiny=_build_shiny_coverage(entries, shiny_rules),
    )


def export_catalog_coverage_json(
    report: CatalogCoverageReport,
    output_path: Path,
) -> Path:
    """Write the coverage report atomically as formatted JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(f"{output_path.suffix}.tmp")

    try:
        with temporary_path.open("w", encoding="utf-8", newline="\n") as file:
            json.dump(report.to_dict(), file, ensure_ascii=False, indent=2)
            file.write("\n")
        temporary_path.replace(output_path)
    except (OSError, TypeError, ValueError) as error:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise PokedexError(
            f"Unable to export catalog coverage report: {output_path}"
        ) from error

    return output_path


def _build_game_coverage(
    entries: tuple[PokemonEntry, ...],
    rules: GameAvailabilityRules,
    game: GameColumn,
) -> CoverageCounts:
    rule = rules.games[game]
    verified_true = 0
    verified_false = 0

    for entry in entries:
        if entry.home_id in rule.excluded_home_ids:
            verified_false += 1
        elif (
            rule.includes_national_dex(entry.national_dex)
            or entry.home_id in rule.home_ids
        ):
            verified_true += 1
        elif rule.complete:
            # Once a game has been fully audited, omission from its positive
            # rules is an explicit unavailable decision rather than unknown.
            verified_false += 1

    return CoverageCounts(
        total=len(entries),
        verified_true=verified_true,
        verified_false=verified_false,
        unknown=len(entries) - verified_true - verified_false,
    )


def _build_shiny_coverage(
    entries: tuple[PokemonEntry, ...],
    rules: ShinyAvailabilityRules,
) -> CoverageCounts:
    verified_true = 0
    verified_false = 0

    for entry in entries:
        if entry.home_id in rules.excluded_home_ids:
            verified_false += 1
        elif (
            entry.national_dex in rules.national_dex or entry.home_id in rules.home_ids
        ):
            verified_true += 1

    return CoverageCounts(
        total=len(entries),
        verified_true=verified_true,
        verified_false=verified_false,
        unknown=len(entries) - verified_true - verified_false,
    )
