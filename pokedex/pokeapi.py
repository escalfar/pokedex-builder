from __future__ import annotations

from dataclasses import dataclass

from pokedex.cache import JsonCache, JsonValue
from pokedex.exceptions import DownloadError
from pokedex.http import HttpClient

SPECIES_CACHE_KEY = "pokemon_species"
SPECIES_ENDPOINT = "pokemon-species"
DEFAULT_PAGE_SIZE = 100

SPECIES_DETAILS_CACHE_KEY = "pokemon_species_details"
ENGLISH_LANGUAGE_NAME = "en"
NATIONAL_POKEDEX_NAME = "national"


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


@dataclass(frozen=True, slots=True)
class SpeciesDetails:
    """Normalized Pokémon species data from PokéAPI."""

    national_dex: int
    api_name: str
    english_name: str
    generation: int
    is_legendary: bool
    is_mythical: bool
    resource_url: str

    def __post_init__(self) -> None:
        if self.national_dex <= 0:
            raise ValueError("National Pokédex number must be greater than zero.")

        if self.generation <= 0:
            raise ValueError("Generation must be greater than zero.")

        for field_name, value in (
            ("api_name", self.api_name),
            ("english_name", self.english_name),
            ("resource_url", self.resource_url),
        ):
            if not value.strip():
                raise ValueError(f"{field_name} cannot be empty.")


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

    def get_species_details(
        self,
        *,
        refresh_cache: bool = False,
    ) -> tuple[SpeciesDetails, ...]:
        """Return normalized details for every Pokémon species."""
        if not refresh_cache and self._cache.is_valid(SPECIES_DETAILS_CACHE_KEY):
            return self._load_species_details_cache()

        resources = self.get_species_resources(
            refresh_cache=refresh_cache,
        )

        details = tuple(
            self._download_species_details(resource) for resource in resources
        )

        serialized: list[JsonValue] = [
            {
                "national_dex": item.national_dex,
                "api_name": item.api_name,
                "english_name": item.english_name,
                "generation": item.generation,
                "is_legendary": item.is_legendary,
                "is_mythical": item.is_mythical,
                "resource_url": item.resource_url,
            }
            for item in details
        ]

        self._cache.save(
            SPECIES_DETAILS_CACHE_KEY,
            serialized,
        )

        return details

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

    def _download_species_details(
        self,
        resource: NamedApiResource,
    ) -> SpeciesDetails:
        payload = self._http_client.get_json(resource.url)

        return self._parse_species_details(
            payload,
            resource_url=resource.url,
        )

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

    def _load_species_details_cache(
        self,
    ) -> tuple[SpeciesDetails, ...]:
        payload = self._cache.load(SPECIES_DETAILS_CACHE_KEY)

        if not isinstance(payload, list):
            raise DownloadError("Cached species details must contain a JSON list.")

        details: list[SpeciesDetails] = []

        for item in payload:
            if not isinstance(item, dict):
                raise DownloadError(
                    "Cached species detail entries must be JSON objects."
                )

            national_dex = item.get("national_dex")
            api_name = item.get("api_name")
            english_name = item.get("english_name")
            generation = item.get("generation")
            is_legendary = item.get("is_legendary")
            is_mythical = item.get("is_mythical")
            resource_url = item.get("resource_url")

            if not isinstance(national_dex, int):
                raise DownloadError(
                    "Cached species details contain an invalid "
                    "National Pokédex number."
                )

            if not isinstance(api_name, str):
                raise DownloadError(
                    "Cached species details contain an invalid API name."
                )

            if not isinstance(english_name, str):
                raise DownloadError(
                    "Cached species details contain an invalid English name."
                )

            if not isinstance(generation, int):
                raise DownloadError(
                    "Cached species details contain an invalid generation."
                )

            if not isinstance(is_legendary, bool):
                raise DownloadError(
                    "Cached species details contain an invalid " "legendary value."
                )

            if not isinstance(is_mythical, bool):
                raise DownloadError(
                    "Cached species details contain an invalid mythical value."
                )

            if not isinstance(resource_url, str):
                raise DownloadError(
                    "Cached species details contain an invalid resource URL."
                )

            details.append(
                SpeciesDetails(
                    national_dex=national_dex,
                    api_name=api_name,
                    english_name=english_name,
                    generation=generation,
                    is_legendary=is_legendary,
                    is_mythical=is_mythical,
                    resource_url=resource_url,
                )
            )

        return tuple(details)

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

    @staticmethod
    def _parse_species_details(
        payload: JsonValue,
        *,
        resource_url: str,
    ) -> SpeciesDetails:
        if not isinstance(payload, dict):
            raise DownloadError("PokéAPI species details must contain a JSON object.")

        api_name = payload.get("name")
        generation_data = payload.get("generation")
        names = payload.get("names")
        pokedex_numbers = payload.get("pokedex_numbers")
        is_legendary = payload.get("is_legendary")
        is_mythical = payload.get("is_mythical")

        if not isinstance(api_name, str):
            raise DownloadError("PokéAPI species details are missing a valid name.")

        generation = PokeApiClient._parse_generation(
            generation_data,
        )
        english_name = PokeApiClient._parse_english_name(
            names,
        )
        national_dex = PokeApiClient._parse_national_dex(
            pokedex_numbers,
        )

        if not isinstance(is_legendary, bool):
            raise DownloadError(
                "PokéAPI species details contain an invalid " "legendary value."
            )

        if not isinstance(is_mythical, bool):
            raise DownloadError(
                "PokéAPI species details contain an invalid mythical value."
            )

        return SpeciesDetails(
            national_dex=national_dex,
            api_name=api_name,
            english_name=english_name,
            generation=generation,
            is_legendary=is_legendary,
            is_mythical=is_mythical,
            resource_url=resource_url,
        )

    @staticmethod
    def _parse_generation(payload: JsonValue | None) -> int:
        if not isinstance(payload, dict):
            raise DownloadError("PokéAPI species generation must be a JSON object.")

        generation_name = payload.get("name")

        if not isinstance(generation_name, str):
            raise DownloadError("PokéAPI species generation is missing a valid name.")

        prefix = "generation-"

        if not generation_name.startswith(prefix):
            raise DownloadError(f"Unsupported generation name: {generation_name}")

        roman_value = generation_name.removeprefix(prefix)

        roman_numerals: dict[str, int] = {
            "i": 1,
            "ii": 2,
            "iii": 3,
            "iv": 4,
            "v": 5,
            "vi": 6,
            "vii": 7,
            "viii": 8,
            "ix": 9,
            "x": 10,
        }

        try:
            return roman_numerals[roman_value]
        except KeyError as error:
            raise DownloadError(
                f"Unsupported generation value: {generation_name}"
            ) from error

    @staticmethod
    def _parse_english_name(
        payload: JsonValue | None,
    ) -> str:
        if not isinstance(payload, list):
            raise DownloadError("PokéAPI species names must contain a JSON list.")

        for item in payload:
            if not isinstance(item, dict):
                continue

            language = item.get("language")
            name = item.get("name")

            if not isinstance(language, dict):
                continue

            language_name = language.get("name")

            if (
                language_name == ENGLISH_LANGUAGE_NAME
                and isinstance(name, str)
                and name.strip()
            ):
                return name

        raise DownloadError("PokéAPI species details do not contain an English name.")

    @staticmethod
    def _parse_national_dex(
        payload: JsonValue | None,
    ) -> int:
        if not isinstance(payload, list):
            raise DownloadError("PokéAPI Pokédex numbers must contain a JSON list.")

        for item in payload:
            if not isinstance(item, dict):
                continue

            pokedex = item.get("pokedex")
            entry_number = item.get("entry_number")

            if not isinstance(pokedex, dict):
                continue

            pokedex_name = pokedex.get("name")

            if (
                pokedex_name == NATIONAL_POKEDEX_NAME
                and isinstance(entry_number, int)
                and entry_number > 0
            ):
                return entry_number

        raise DownloadError(
            "PokéAPI species details do not contain a National Pokédex number."
        )
