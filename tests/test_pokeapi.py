from pathlib import Path
from unittest.mock import Mock, call

import pytest

from pokedex.cache import JsonCache
from pokedex.exceptions import DownloadError
from pokedex.http import HttpClient
from pokedex.pokeapi import (
    PokeApiClient,
    SPECIES_CACHE_KEY,
)


def build_http_client_mock() -> Mock:
    return Mock(spec=HttpClient)


def test_get_species_resources_downloads_and_caches(
    tmp_path: Path,
) -> None:
    http_client = build_http_client_mock()
    cache = JsonCache(tmp_path)

    http_client.get_json.side_effect = [
        {
            "count": 3,
            "next": "https://pokeapi.co/api/v2/pokemon-species?offset=2&limit=2",
            "previous": None,
            "results": [
                {
                    "name": "bulbasaur",
                    "url": "https://pokeapi.co/api/v2/pokemon-species/1/",
                },
                {
                    "name": "ivysaur",
                    "url": "https://pokeapi.co/api/v2/pokemon-species/2/",
                },
            ],
        },
        {
            "count": 3,
            "next": None,
            "previous": (
                "https://pokeapi.co/api/v2/" "pokemon-species?offset=0&limit=2"
            ),
            "results": [
                {
                    "name": "venusaur",
                    "url": "https://pokeapi.co/api/v2/pokemon-species/3/",
                }
            ],
        },
    ]

    client = PokeApiClient(
        http_client=http_client,
        cache=cache,
    )

    resources = client.get_species_resources()

    assert [resource.name for resource in resources] == [
        "bulbasaur",
        "ivysaur",
        "venusaur",
    ]

    assert cache.exists(SPECIES_CACHE_KEY) is True
    assert http_client.get_json.call_args_list == [
        call(
            "pokemon-species",
            params={"limit": 100, "offset": 0},
        ),
        call(
            "https://pokeapi.co/api/v2/" "pokemon-species?offset=2&limit=2",
            params=None,
        ),
    ]


def test_get_species_resources_uses_valid_cache(
    tmp_path: Path,
) -> None:
    http_client = build_http_client_mock()
    cache = JsonCache(tmp_path)

    cache.save(
        SPECIES_CACHE_KEY,
        [
            {
                "name": "bulbasaur",
                "url": "https://pokeapi.co/api/v2/pokemon-species/1/",
            }
        ],
    )

    client = PokeApiClient(
        http_client=http_client,
        cache=cache,
    )

    resources = client.get_species_resources()

    assert len(resources) == 1
    assert resources[0].name == "bulbasaur"
    http_client.get_json.assert_not_called()


def test_refresh_cache_forces_download(
    tmp_path: Path,
) -> None:
    http_client = build_http_client_mock()
    cache = JsonCache(tmp_path)

    cache.save(
        SPECIES_CACHE_KEY,
        [
            {
                "name": "old-entry",
                "url": "https://example.com/old-entry",
            }
        ],
    )

    http_client.get_json.return_value = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "name": "bulbasaur",
                "url": "https://pokeapi.co/api/v2/pokemon-species/1/",
            }
        ],
    }

    client = PokeApiClient(
        http_client=http_client,
        cache=cache,
    )

    resources = client.get_species_resources(
        refresh_cache=True,
    )

    assert resources[0].name == "bulbasaur"
    http_client.get_json.assert_called_once()


def test_resource_page_rejects_non_object_payload(
    tmp_path: Path,
) -> None:
    http_client = build_http_client_mock()
    cache = JsonCache(tmp_path)

    http_client.get_json.return_value = []

    client = PokeApiClient(
        http_client=http_client,
        cache=cache,
    )

    with pytest.raises(
        DownloadError,
        match="must contain a JSON object",
    ):
        client.get_species_resources()


def test_resource_page_rejects_invalid_count(
    tmp_path: Path,
) -> None:
    http_client = build_http_client_mock()
    cache = JsonCache(tmp_path)

    http_client.get_json.return_value = {
        "count": "invalid",
        "next": None,
        "previous": None,
        "results": [],
    }

    client = PokeApiClient(
        http_client=http_client,
        cache=cache,
    )

    with pytest.raises(
        DownloadError,
        match="valid count",
    ):
        client.get_species_resources()


def test_resource_page_rejects_invalid_results(
    tmp_path: Path,
) -> None:
    http_client = build_http_client_mock()
    cache = JsonCache(tmp_path)

    http_client.get_json.return_value = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": "invalid",
    }

    client = PokeApiClient(
        http_client=http_client,
        cache=cache,
    )

    with pytest.raises(
        DownloadError,
        match="valid results list",
    ):
        client.get_species_resources()


def test_resource_page_rejects_invalid_resource_entry(
    tmp_path: Path,
) -> None:
    http_client = build_http_client_mock()
    cache = JsonCache(tmp_path)

    http_client.get_json.return_value = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "name": 123,
                "url": None,
            }
        ],
    }

    client = PokeApiClient(
        http_client=http_client,
        cache=cache,
    )

    with pytest.raises(
        DownloadError,
        match="string name and URL",
    ):
        client.get_species_resources()


def test_inconsistent_count_raises_error(
    tmp_path: Path,
) -> None:
    http_client = build_http_client_mock()
    cache = JsonCache(tmp_path)

    http_client.get_json.return_value = {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
                "name": "bulbasaur",
                "url": "https://pokeapi.co/api/v2/pokemon-species/1/",
            }
        ],
    }

    client = PokeApiClient(
        http_client=http_client,
        cache=cache,
    )

    with pytest.raises(
        DownloadError,
        match="inconsistent species count",
    ):
        client.get_species_resources()
