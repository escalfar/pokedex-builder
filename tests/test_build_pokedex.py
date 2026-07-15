import logging
from pathlib import Path
from unittest.mock import Mock

import pytest

import build_pokedex
from pokedex.config import Settings
from pokedex.pokeapi import PokeApiClient, SpeciesDetails, SpeciesVariety


def mock_species_details() -> tuple[SpeciesDetails, ...]:
    return (
        SpeciesDetails(
            national_dex=1,
            api_name="bulbasaur",
            english_name="Bulbasaur",
            generation=1,
            is_legendary=False,
            is_mythical=False,
            resource_url="https://pokeapi.co/api/v2/pokemon-species/1/",
            varieties=(
                SpeciesVariety(
                    api_name="bulbasaur",
                    resource_url="https://pokeapi.co/api/v2/pokemon/1/",
                    is_default=True,
                ),
            ),
        ),
    )


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        project_root=tmp_path,
        data_dir=tmp_path / "data",
        cache_dir=tmp_path / "cache",
        output_dir=tmp_path / "output",
        logs_dir=tmp_path / "logs",
    )


def test_argument_parser_defaults() -> None:
    parser = build_pokedex.build_argument_parser()

    arguments = parser.parse_args([])

    assert arguments.refresh_cache is False
    assert arguments.validate is False


def test_argument_parser_accepts_flags() -> None:
    parser = build_pokedex.build_argument_parser()

    arguments = parser.parse_args(
        [
            "--refresh-cache",
            "--validate",
        ]
    )

    assert arguments.refresh_cache is True
    assert arguments.validate is True


def test_initialize_application_creates_directories(
    settings: Settings,
) -> None:
    logger = build_pokedex.initialize_application(settings)

    assert settings.data_dir.is_dir()
    assert settings.cache_dir.is_dir()
    assert settings.output_dir.is_dir()
    assert settings.logs_dir.is_dir()
    assert logger.name == "pokedex_builder"


def test_run_returns_success(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        PokeApiClient,
        "get_species_details",
        lambda self, refresh_cache=False: mock_species_details(),
    )
    result = build_pokedex.run(settings)

    assert result == 0


def test_run_writes_log_file(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        PokeApiClient,
        "get_species_details",
        lambda self, refresh_cache=False: mock_species_details(),
    )
    result = build_pokedex.run(
        settings,
        refresh_cache=True,
        validate_only=True,
    )

    log_file = settings.logs_dir / "pokedex.log"
    content = log_file.read_text(encoding="utf-8")

    assert result == 0
    assert "Starting Pokédex Builder" in content
    assert "Refresh cache: True" in content
    assert "Validation only: True" in content


def test_main_passes_arguments_to_run(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
) -> None:
    run_mock = Mock(return_value=0)

    monkeypatch.setattr(
        build_pokedex,
        "get_settings",
        lambda: settings,
    )
    monkeypatch.setattr(
        build_pokedex,
        "run",
        run_mock,
    )

    result = build_pokedex.main(
        [
            "--refresh-cache",
            "--validate",
        ]
    )

    assert result == 0
    run_mock.assert_called_once_with(
        settings,
        refresh_cache=True,
        validate_only=True,
    )


def test_main_returns_error_for_os_error(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
) -> None:
    monkeypatch.setattr(
        build_pokedex,
        "get_settings",
        lambda: settings,
    )
    monkeypatch.setattr(
        build_pokedex,
        "run",
        Mock(side_effect=OSError("disk error")),
    )

    result = build_pokedex.main([])

    assert result == 1


def test_application_logger_is_not_propagated(
    settings: Settings,
) -> None:
    logger = build_pokedex.initialize_application(settings)

    assert logger.propagate is False
    assert logger.level == logging.INFO
