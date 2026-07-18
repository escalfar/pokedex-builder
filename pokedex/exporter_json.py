from __future__ import annotations

import json
from pathlib import Path

from pokedex.exceptions import PokedexError
from pokedex.models import JsonValue, PokemonEntry


def export_json(
    entries: tuple[PokemonEntry, ...],
    output_path: Path,
) -> Path:
    """Export Pokédex entries as formatted UTF-8 JSON."""
    if not entries:
        raise ValueError("Cannot export an empty Pokémon entry collection.")

    payload: list[JsonValue] = [entry.to_dict() for entry in entries]
    temporary_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
    try:
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with temporary_path.open(
            "w",
            encoding="utf-8",
            newline="\n",
        ) as file:
            json.dump(
                payload,
                file,
                ensure_ascii=False,
                indent=2,
            )
            file.write("\n")

        temporary_path.replace(output_path)
    except (OSError, TypeError, ValueError) as error:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise PokedexError(f"Unable to export JSON file: {output_path}") from error

    return output_path
