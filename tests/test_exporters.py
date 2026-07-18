import csv
import json
from pathlib import Path

from pokedex.constants import OUTPUT_COLUMNS, Gender
from pokedex.exporter_csv import export_csv
from pokedex.exporter_json import export_json
from pokedex.models import GameAvailability, PokemonEntry


def build_entry() -> PokemonEntry:
    return PokemonEntry(
        national_dex=26,
        pokemon="Raichu",
        form="Alolan",
        name="Alolan Raichu",
        generation=7,
        home_id="00026_ALOLA",
        availability=GameAvailability(),
        legendary_mythical=False,
        obtainable_shiny=True,
        gender=Gender.NONE,
    )


def test_export_csv_creates_expected_columns(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "Pokedex.csv"

    result = export_csv(
        (build_entry(),),
        output_path,
    )

    assert result == output_path
    assert output_path.is_file()

    with output_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert list(rows[0]) == [column.value for column in OUTPUT_COLUMNS]
    assert rows[0]["Nat Dex"] == "26"
    assert rows[0]["Nombre"] == "Alolan Raichu"
    assert rows[0]["X/Y"] == "FALSE"
    assert rows[0]["Obtenible"] == "TRUE"


def test_export_json_preserves_native_booleans(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "Pokedex.json"

    result = export_json(
        (build_entry(),),
        output_path,
    )

    assert result == output_path

    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert len(payload) == 1
    assert payload[0]["Nat Dex"] == 26
    assert payload[0]["Nombre"] == "Alolan Raichu"
    assert payload[0]["X/Y"] is False
    assert payload[0]["Obtenible"] is True


def test_json_uses_unescaped_unicode(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "Pokedex.json"

    export_json(
        (build_entry(),),
        output_path,
    )

    content = output_path.read_text(encoding="utf-8")

    assert "Legendario/Mítico" in content
    assert "\\u00ed" not in content


def test_export_excel_creates_four_expected_sheets(tmp_path: Path) -> None:
    from openpyxl import load_workbook

    from pokedex.exporter_excel import export_excel

    output_path = tmp_path / "Pokedex.xlsx"
    result = export_excel((build_entry(),), output_path)

    assert result == output_path
    workbook = load_workbook(output_path, data_only=True)

    try:
        assert workbook.sheetnames == [
            "Pokédex",
            "Resumen",
            "Validación",
            "Metadatos",
        ]
        sheet = workbook["Pokédex"]
        assert sheet.freeze_panes == "A2"
        assert sheet["A1"].value == "Nat Dex"
        assert sheet["D2"].value == "Alolan Raichu"
        assert sheet["R2"].value is True
    finally:
        workbook.close()


def test_export_excel_summary_and_metadata(tmp_path: Path) -> None:
    from datetime import UTC, datetime

    from openpyxl import load_workbook

    from pokedex.exporter_excel import export_excel

    output_path = tmp_path / "Pokedex.xlsx"
    generated_at = datetime(2026, 7, 15, 12, 0, tzinfo=UTC)

    export_excel(
        (build_entry(),),
        output_path,
        generator_version="1.2.3",
        specification_version="1.0",
        generated_at=generated_at,
    )

    workbook = load_workbook(output_path, data_only=True)

    try:
        summary = workbook["Resumen"]
        metadata = workbook["Metadatos"]
        validation = workbook["Validación"]

        assert summary["B4"].value == 1
        assert summary["B5"].value == 1
        assert metadata["B4"].value == "1.2.3"
        assert metadata["B6"].value == generated_at.isoformat()
        assert validation["B4"].value == "OK"
    finally:
        workbook.close()
