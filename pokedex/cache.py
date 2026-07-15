import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

# from typing import Any

from pokedex.exceptions import CacheError

from typing import TypeAlias, cast

JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]


class JsonCache:
    """Read and write JSON data in a local cache directory."""

    def __init__(self, directory: Path, ttl_hours: int = 168) -> None:
        if ttl_hours < 0:
            raise ValueError("Cache TTL cannot be negative.")

        self._directory = directory
        self._ttl = timedelta(hours=ttl_hours)

    @property
    def directory(self) -> Path:
        """Return the cache directory."""
        return self._directory

    def ensure_directory(self) -> None:
        """Create the cache directory when it does not exist."""
        try:
            self._directory.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise CacheError(
                f"Unable to create cache directory: {self._directory}"
            ) from error

    def path_for(self, key: str) -> Path:
        """Return the JSON file path for a cache key."""
        normalized_key = self._normalize_key(key)
        return self._directory / f"{normalized_key}.json"

    def exists(self, key: str) -> bool:
        """Return whether a cached JSON file exists."""
        return self.path_for(key).is_file()

    def is_expired(self, key: str) -> bool:
        """Return whether a cached file has exceeded its TTL."""
        path = self.path_for(key)

        if not path.is_file():
            return True

        if self._ttl == timedelta(0):
            return True

        try:
            modified_at = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
        except OSError as error:
            raise CacheError(f"Unable to inspect cache file: {path}") from error

        return datetime.now(UTC) - modified_at > self._ttl

    def is_valid(self, key: str) -> bool:
        """Return whether a cache entry exists and has not expired."""
        return self.exists(key) and not self.is_expired(key)

    # def save(self, key: str, data: Any) -> Path:
    def save(self, key: str, data: JsonValue) -> Path:
        """Serialize data as UTF-8 JSON and return the written path."""
        self.ensure_directory()
        path = self.path_for(key)
        temporary_path = path.with_suffix(".json.tmp")

        try:
            with temporary_path.open("w", encoding="utf-8", newline="\n") as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                file.write("\n")

            temporary_path.replace(path)
        except (OSError, TypeError, ValueError) as error:
            self._remove_temporary_file(temporary_path)
            raise CacheError(f"Unable to write cache file: {path}") from error

        return path

    # def load(self, key: str) -> Any:
    def load(self, key: str) -> JsonValue:
        """Load and deserialize a cached JSON file."""
        path = self.path_for(key)

        if not path.is_file():
            raise CacheError(f"Cache file does not exist: {path}")

        try:
            with path.open("r", encoding="utf-8") as file:
                return cast(JsonValue, json.load(file))
        except json.JSONDecodeError as error:
            raise CacheError(f"Cache file contains invalid JSON: {path}") from error
        except OSError as error:
            raise CacheError(f"Unable to read cache file: {path}") from error

    def delete(self, key: str) -> bool:
        """Delete a cache entry and return whether a file was removed."""
        path = self.path_for(key)

        if not path.exists():
            return False

        try:
            path.unlink()
        except OSError as error:
            raise CacheError(f"Unable to delete cache file: {path}") from error

        return True

    def clear(self) -> int:
        """Delete every JSON cache file and return the number removed."""
        if not self._directory.exists():
            return 0

        removed = 0

        try:
            for path in self._directory.glob("*.json"):
                path.unlink()
                removed += 1
        except OSError as error:
            raise CacheError(
                f"Unable to clear cache directory: {self._directory}"
            ) from error

        return removed

    @staticmethod
    def _normalize_key(key: str) -> str:
        normalized = key.strip().lower().replace(" ", "_")

        if not normalized:
            raise ValueError("Cache key cannot be empty.")

        if not all(
            character.isalnum() or character in {"_", "-"} for character in normalized
        ):
            raise ValueError(
                "Cache key may contain only letters, numbers, hyphens, and underscores."
            )

        return normalized

    @staticmethod
    def _remove_temporary_file(path: Path) -> None:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
