from pathlib import Path
from typing import cast
from unittest.mock import Mock

import pytest

from pokedex.cache import JsonCache
from pokedex.exceptions import DownloadError
from pokedex.http import HttpClient
from pokedex.pokeapi import (
    PokeApiClient,
    SPECIES_DETAILS_CACHE_KEY,
)


def build_http_client_mock() -> tuple[HttpClient, Mock]:
    mock = Mock()
    client = cast(
        HttpClient,
        cast(object, mock),
    )
    return client, mock


def build_species_payload() -> dict[str, object]:
    return {
        "name": "bulbasaur",
        "generation": {
            "name": "generation-i",
            "url": "https://pokeapi.co/api/v2/generation/1/",
        },
        "names": [
            {
                "language": {
                    "name": "ja",
                    "url": "https://pokeapi.co/api/v2/language/1/",
                },
                "name": "フシギダネ",
            },
            {
                "language": {
                    "name": "en",
                    "url": "https://pokeapi.co/api/v2/language/9/",
                },
                "name": "Bulbasaur",
            },
        ],
        "pokedex_numbers": [
            {
                "entry_number": 1,
                "pokedex": {
                    "name": "national",
                    "url": "https://pokeapi.co/api/v2/pokedex/1/",
                },
            }
        ],
        "is_legendary": False,
        "is_mythical": False,
        "varieties": [
            {
                "is_default": True,
                "pokemon": {
                    "name": "bulbasaur",
                    "url": "https://pokeapi.co/api/v2/pokemon/1/",
                },
            }
        ],
    }


def test_get_species_details_downloads_and_caches(
    tmp_path: Path,
) -> None:
    http_client, http_mock = build_http_client_mock()
    cache = JsonCache(tmp_path)

    http_mock.get_json.side_effect = [
        {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "name": "bulbasaur",
                    "url": ("https://pokeapi.co/api/v2/" "pokemon-species/1/"),
                }
            ],
        },
        build_species_payload(),
    ]

    client = PokeApiClient(
        http_client=http_client,
        cache=cache,
    )

    details = client.get_species_details()

    assert len(details) == 1
    assert details[0].national_dex == 1
    assert details[0].api_name == "bulbasaur"
    assert details[0].english_name == "Bulbasaur"
    assert details[0].generation == 1
    assert details[0].is_legendary is False
    assert details[0].is_mythical is False
    assert cache.exists(SPECIES_DETAILS_CACHE_KEY) is True


def test_get_species_details_uses_cache(
    tmp_path: Path,
) -> None:
    http_client, http_mock = build_http_client_mock()
    cache = JsonCache(tmp_path)

    cache.save(
        SPECIES_DETAILS_CACHE_KEY,
        [
            {
                "national_dex": 150,
                "api_name": "mewtwo",
                "english_name": "Mewtwo",
                "generation": 1,
                "is_legendary": True,
                "is_mythical": False,
                "resource_url": ("https://pokeapi.co/api/v2/" "pokemon-species/150/"),
                "varieties": [
                    {
                        "api_name": "mewtwo",
                        "resource_url": ("https://pokeapi.co/api/v2/pokemon/150/"),
                        "is_default": True,
                    }
                ],
            }
        ],
    )

    client = PokeApiClient(
        http_client=http_client,
        cache=cache,
    )

    details = client.get_species_details()

    assert details[0].english_name == "Mewtwo"
    assert details[0].is_legendary is True
    http_mock.get_json.assert_not_called()


@pytest.mark.parametrize(
    ("generation_name", "expected"),
    [
        ("generation-i", 1),
        ("generation-iv", 4),
        ("generation-vii", 7),
        ("generation-ix", 9),
        ("generation-x", 10),
    ],
)
def test_parse_generation(
    generation_name: str,
    expected: int,
) -> None:
    result = PokeApiClient._parse_generation(
        {
            "name": generation_name,
        }
    )

    assert result == expected


def test_parse_generation_rejects_unknown_value() -> None:
    with pytest.raises(
        DownloadError,
        match="Unsupported generation value",
    ):
        PokeApiClient._parse_generation(
            {
                "name": "generation-xi",
            }
        )


def test_parse_english_name() -> None:
    result = PokeApiClient._parse_english_name(
        [
            {
                "language": {"name": "fr"},
                "name": "Bulbizarre",
            },
            {
                "language": {"name": "en"},
                "name": "Bulbasaur",
            },
        ]
    )

    assert result == "Bulbasaur"


def test_parse_english_name_requires_english_entry() -> None:
    with pytest.raises(
        DownloadError,
        match="English name",
    ):
        PokeApiClient._parse_english_name(
            [
                {
                    "language": {"name": "fr"},
                    "name": "Bulbizarre",
                }
            ]
        )


def test_parse_national_dex() -> None:
    result = PokeApiClient._parse_national_dex(
        [
            {
                "entry_number": 1,
                "pokedex": {"name": "national"},
            }
        ]
    )

    assert result == 1


def test_parse_national_dex_rejects_missing_entry() -> None:
    with pytest.raises(
        DownloadError,
        match="National Pokédex number",
    ):
        PokeApiClient._parse_national_dex(
            [
                {
                    "entry_number": 1,
                    "pokedex": {"name": "kanto"},
                }
            ]
        )


def test_species_details_reject_invalid_legendary_value(
    tmp_path: Path,
) -> None:
    http_client, http_mock = build_http_client_mock()
    cache = JsonCache(tmp_path)
    payload = build_species_payload()
    payload["is_legendary"] = "false"

    http_mock.get_json.side_effect = [
        {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "name": "bulbasaur",
                    "url": ("https://pokeapi.co/api/v2/" "pokemon-species/1/"),
                }
            ],
        },
        payload,
    ]

    client = PokeApiClient(
        http_client=http_client,
        cache=cache,
    )

    with pytest.raises(
        DownloadError,
        match="legendary value",
    ):
        client.get_species_details()
