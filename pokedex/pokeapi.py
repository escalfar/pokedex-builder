from __future__ import annotations

from dataclasses import dataclass

from pokedex.cache import JsonCache, JsonValue
from pokedex.exceptions import DownloadError
from pokedex.http import HttpClient

SPECIES_CACHE_KEY = "pokemon_species"
SPECIES_ENDPOINT = "pokemon-species"
DEFAULT_PAGE_SIZE = 100


@dataclass(frozen=True, slots=True)
class NamedApiResource:
    """Named resource returned by PokéAPI."""

    name: str
    url: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Resource name cannot be empty.")

        if not self.url.strip():
            raise ValueError("Resource URL cannot be empty.")


@dataclass(frozen=True, slots=True)
class ResourcePage:
    """Paginated response returned by PokéAPI."""

    count: int
    next_url: str | None
    previous_url: str | None
    results: tuple[NamedApiResource, ...]

    def __post_init__(self) -> None:
        if self.count < 0:
            raise ValueError("Resource count cannot be negative.")


class PokeApiClient:
    """High-level client for downloading structured PokéAPI data."""

    def __init__(
        self,
        *,
        http_client: HttpClient,
        cache: JsonCache,
    ) -> None:
        self._http_client = http_client
        self._cache = cache

    def get_species_resources(
        self,
        *,
        refresh_cache: bool = False,
    ) -> tuple[NamedApiResource, ...]:
        """Return every National Pokédex species resource."""
        if not refresh_cache and self._cache.is_valid(SPECIES_CACHE_KEY):
            return self._load_species_cache()

        resources = self._download_all_named_resources(
            endpoint=SPECIES_ENDPOINT,
        )

        serialized: list[JsonValue] = [
            {
                "name": resource.name,
                "url": resource.url,
            }
            for resource in resources
        ]

        self._cache.save(SPECIES_CACHE_KEY, serialized)

        return resources

    def _download_all_named_resources(
        self,
        *,
        endpoint: str,
    ) -> tuple[NamedApiResource, ...]:
        resources: list[NamedApiResource] = []
        next_path: str | None = endpoint
        params: dict[str, int] | None = {
            "limit": DEFAULT_PAGE_SIZE,
            "offset": 0,
        }

        while next_path is not None:
            payload = self._http_client.get_json(
                next_path,
                params=params,
            )
            page = self._parse_resource_page(payload)

            resources.extend(page.results)

            next_path = page.next_url
            params = None

        if len(resources) != page.count:
            raise DownloadError(
                "PokéAPI returned an inconsistent species count: "
                f"expected {page.count}, received {len(resources)}."
            )

        return tuple(resources)

    def _load_species_cache(self) -> tuple[NamedApiResource, ...]:
        payload = self._cache.load(SPECIES_CACHE_KEY)

        if not isinstance(payload, list):
            raise DownloadError("Cached species data must contain a JSON list.")

        resources: list[NamedApiResource] = []

        for item in payload:
            if not isinstance(item, dict):
                raise DownloadError("Cached species entries must contain JSON objects.")

            name = item.get("name")
            url = item.get("url")

            if not isinstance(name, str) or not isinstance(url, str):
                raise DownloadError(
                    "Cached species entries must include string name and URL values."
                )

            resources.append(
                NamedApiResource(
                    name=name,
                    url=url,
                )
            )

        return tuple(resources)

    @staticmethod
    def _parse_resource_page(payload: JsonValue) -> ResourcePage:
        if not isinstance(payload, dict):
            raise DownloadError("PokéAPI resource page must contain a JSON object.")

        count = payload.get("count")
        next_url = payload.get("next")
        previous_url = payload.get("previous")
        results = payload.get("results")

        if not isinstance(count, int):
            raise DownloadError("PokéAPI resource page is missing a valid count.")

        if next_url is not None and not isinstance(next_url, str):
            raise DownloadError("PokéAPI resource page contains an invalid next URL.")

        if previous_url is not None and not isinstance(previous_url, str):
            raise DownloadError(
                "PokéAPI resource page contains an invalid previous URL."
            )

        if not isinstance(results, list):
            raise DownloadError(
                "PokéAPI resource page is missing a valid results list."
            )

        parsed_results: list[NamedApiResource] = []

        for item in results:
            if not isinstance(item, dict):
                raise DownloadError(
                    "PokéAPI resource results must contain JSON objects."
                )

            name = item.get("name")
            url = item.get("url")

            if not isinstance(name, str) or not isinstance(url, str):
                raise DownloadError(
                    "PokéAPI resource entries must include string name and URL values."
                )

            parsed_results.append(
                NamedApiResource(
                    name=name,
                    url=url,
                )
            )

        return ResourcePage(
            count=count,
            next_url=next_url,
            previous_url=previous_url,
            results=tuple(parsed_results),
        )
