from __future__ import annotations

import csv
from pathlib import Path

from pokedex.constants import OUTPUT_COLUMNS
from pokedex.exceptions import PokedexError
from pokedex.models import PokemonEntry


def export_csv(
    entries: tuple[PokemonEntry, ...],
    output_path: Path,
) -> Path:
    """Export Pokédex entries as a UTF-8 CSV file."""
    if not entries:
        raise ValueError("Cannot export an empty Pokémon entry collection.")

    try:
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_path.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[column.value for column in OUTPUT_COLUMNS],
                extrasaction="raise",
            )

            writer.writeheader()

            for entry in entries:
                writer.writerow(_prepare_csv_row(entry))
    except (OSError, csv.Error, ValueError) as error:
        raise PokedexError(f"Unable to export CSV file: {output_path}") from error

    return output_path


def _prepare_csv_row(
    entry: PokemonEntry,
) -> dict[str, object]:
    return {key: _convert_csv_value(value) for key, value in entry.to_dict().items()}


def _convert_csv_value(value: object) -> object:
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"

    return value
