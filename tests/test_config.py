from pathlib import Path

from pokedex.config import Settings, get_settings


def test_default_settings_use_project_directories() -> None:
    settings = Settings()

    assert isinstance(settings.project_root, Path)
    assert settings.data_dir == settings.project_root / "data"
    assert settings.cache_dir == settings.project_root / "cache"
    assert settings.output_dir == settings.project_root / "output"


def test_default_http_settings_are_valid() -> None:
    settings = Settings()

    assert settings.request_timeout_seconds > 0
    assert settings.request_retries >= 0
    assert settings.pokeapi_base_url.startswith("https://")


def test_get_settings_returns_cached_instance() -> None:
    first = get_settings()
    second = get_settings()

    assert first is second


def test_create_directories(tmp_path: Path) -> None:
    settings = Settings(
        project_root=tmp_path,
        data_dir=tmp_path / "data",
        cache_dir=tmp_path / "cache",
        output_dir=tmp_path / "output",
        logs_dir=tmp_path / "logs",
    )

    settings.create_directories()

    assert settings.data_dir.is_dir()
    assert settings.cache_dir.is_dir()
    assert settings.output_dir.is_dir()
    assert settings.logs_dir.is_dir()


def test_settings_build_cache(tmp_path: Path) -> None:
    settings = Settings(
        project_root=tmp_path,
        data_dir=tmp_path / "data",
        cache_dir=tmp_path / "cache",
        output_dir=tmp_path / "output",
        logs_dir=tmp_path / "logs",
    )

    cache = settings.build_cache()

    assert cache.directory == tmp_path / "cache"
