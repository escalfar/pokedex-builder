import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

# from typing import Any

import pytest

from pokedex.cache import JsonCache, JsonValue
from pokedex.exceptions import CacheError


def test_cache_saves_and_loads_json(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path)
    # data: dict[str, Any] = {
    data: dict[str, JsonValue] = {
        "name": "Alolan Raichu",
        "generation": 7,
        "available": True,
    }

    written_path = cache.save("raichu_alolan", data)

    assert written_path == tmp_path / "raichu_alolan.json"
    assert cache.load("raichu_alolan") == data


def test_cache_writes_utf8_characters(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path)

    path = cache.save(
        "metadata",
        {
            "sheet": "Pokédex",
            "legendary": "Legendario/Mítico",
        },
    )

    content = path.read_text(encoding="utf-8")

    assert "Pokédex" in content
    assert "Legendario/Mítico" in content
    assert "\\u00e9" not in content


def test_cache_normalizes_key(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path)

    assert cache.path_for("Pokemon Species") == tmp_path / "pokemon_species.json"


@pytest.mark.parametrize(
    "key",
    [
        "",
        "   ",
        "../species",
        "forms.json",
        "pokemon/forms",
    ],
)
def test_cache_rejects_invalid_keys(tmp_path: Path, key: str) -> None:
    cache = JsonCache(tmp_path)

    with pytest.raises(ValueError):
        cache.path_for(key)


def test_cache_reports_missing_file(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path)

    with pytest.raises(CacheError, match="does not exist"):
        cache.load("missing")


def test_cache_reports_invalid_json(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path)
    path = cache.path_for("invalid")
    path.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(CacheError, match="invalid JSON"):
        cache.load("invalid")


def test_cache_exists_and_is_valid(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path, ttl_hours=24)
    cache.save("species", {"count": 1})

    assert cache.exists("species") is True
    assert cache.is_expired("species") is False
    assert cache.is_valid("species") is True


def test_missing_cache_is_expired(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path)

    assert cache.is_expired("missing") is True
    assert cache.is_valid("missing") is False


def test_zero_ttl_always_expires(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path, ttl_hours=0)
    cache.save("species", {"count": 1})

    assert cache.is_expired("species") is True


def test_old_cache_is_expired(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path, ttl_hours=24)
    path = cache.save("species", {"count": 1})

    old_time = datetime.now(UTC) - timedelta(days=2)
    timestamp = old_time.timestamp()
    os.utime(path, (timestamp, timestamp))

    assert cache.is_expired("species") is True


def test_cache_delete(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path)
    cache.save("species", {"count": 1})

    assert cache.delete("species") is True
    assert cache.exists("species") is False
    assert cache.delete("species") is False


def test_cache_clear_only_removes_json_files(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path)
    cache.save("species", {"count": 1})
    cache.save("forms", {"count": 2})
    preserved_file = tmp_path / ".gitkeep"
    preserved_file.write_text("", encoding="utf-8")

    removed = cache.clear()

    assert removed == 2
    assert preserved_file.exists()
    assert list(tmp_path.glob("*.json")) == []


def test_cache_rejects_negative_ttl(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        JsonCache(tmp_path, ttl_hours=-1)


def test_cache_output_is_valid_json(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path)
    path = cache.save("sample", {"value": [1, 2, 3]})

    parsed = json.loads(path.read_text(encoding="utf-8"))

    assert parsed == {"value": [1, 2, 3]}
