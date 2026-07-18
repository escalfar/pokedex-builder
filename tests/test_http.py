from pathlib import Path
from typing import cast
from unittest.mock import Mock

import pytest
import requests
from requests import Response, Session

from pokedex.exceptions import DownloadError
from pokedex.http import HttpClient


def build_response(
    *,
    status_code: int = 200,
    json_data: object | None = None,
    url: str = "https://pokeapi.co/api/v2/pokemon",
) -> Response:
    response = Mock(spec=Response)
    response.status_code = status_code
    response.url = url
    response.raise_for_status.return_value = None
    response.json.return_value = json_data
    return response


def build_session() -> tuple[Session, Mock]:
    """Create a mocked requests session with its instance attributes."""
    session_mock = Mock()
    session_mock.headers = {}

    session = cast(
        Session,
        cast(object, session_mock),
    )

    return session, session_mock


def test_client_normalizes_base_url() -> None:
    client = HttpClient(
        base_url="https://pokeapi.co/api/v2/",
    )

    assert client.base_url == "https://pokeapi.co/api/v2"


def test_client_rejects_empty_base_url() -> None:
    with pytest.raises(ValueError, match="Base URL cannot be empty"):
        HttpClient(base_url="   ")


@pytest.mark.parametrize(
    ("argument", "value", "message"),
    [
        ("timeout_seconds", 0, "Timeout must be greater than zero"),
        ("retries", -1, "Retries cannot be negative"),
        ("backoff_factor", -1, "Backoff factor cannot be negative"),
    ],
)
def test_client_rejects_invalid_numeric_configuration(
    argument: str,
    value: int,
    message: str,
) -> None:
    arguments: dict[str, object] = {
        "base_url": "https://pokeapi.co/api/v2",
        argument: value,
    }

    with pytest.raises(ValueError, match=message):
        HttpClient(**arguments)  # type: ignore[arg-type]


def test_get_builds_relative_url() -> None:
    session, session_mock = build_session()
    response = build_response()
    session_mock.get.return_value = response

    client = HttpClient(
        base_url="https://pokeapi.co/api/v2",
        session=session,
    )

    result = client.get("pokemon")

    assert result is response
    session_mock.get.assert_called_once_with(
        "https://pokeapi.co/api/v2/pokemon",
        params=None,
        timeout=30.0,
    )


def test_get_accepts_absolute_url() -> None:
    session, session_mock = build_session()
    response = build_response()
    session_mock.get.return_value = response

    client = HttpClient(
        base_url="https://pokeapi.co/api/v2",
        session=session,
    )

    client.get("https://example.com/data")

    session_mock.get.assert_called_once_with(
        "https://example.com/data",
        params=None,
        timeout=30.0,
    )


def test_get_passes_query_parameters() -> None:
    session, session_mock = build_session()
    response = build_response()
    session_mock.get.return_value = response

    client = HttpClient(
        base_url="https://pokeapi.co/api/v2",
        session=session,
    )

    client.get(
        "pokemon",
        params={"limit": 100, "offset": 0},
    )

    session_mock.get.assert_called_once_with(
        "https://pokeapi.co/api/v2/pokemon",
        params={"limit": 100, "offset": 0},
        timeout=30.0,
    )


def test_get_json_returns_deserialized_payload() -> None:
    session, session_mock = build_session()
    response = build_response(
        json_data={
            "count": 1,
            "results": [{"name": "bulbasaur"}],
        }
    )
    session_mock.get.return_value = response

    client = HttpClient(
        base_url="https://pokeapi.co/api/v2",
        session=session,
    )

    result = client.get_json("pokemon")

    assert result == {
        "count": 1,
        "results": [{"name": "bulbasaur"}],
    }


def test_get_converts_timeout_to_download_error() -> None:
    session, session_mock = build_session()
    session_mock.get.side_effect = requests.Timeout("timeout")

    client = HttpClient(
        base_url="https://pokeapi.co/api/v2",
        session=session,
    )

    with pytest.raises(DownloadError, match="timed out"):
        client.get("pokemon")


def test_get_converts_connection_error() -> None:
    session, session_mock = build_session()
    session_mock.get.side_effect = requests.ConnectionError("connection failed")

    client = HttpClient(
        base_url="https://pokeapi.co/api/v2",
        session=session,
    )

    with pytest.raises(DownloadError, match="Unable to connect"):
        client.get("pokemon")


def test_get_converts_http_error() -> None:
    session, session_mock = build_session()
    response = build_response(status_code=404)

    http_error = requests.HTTPError("not found")
    http_error.response = response

    raise_for_status_mock = cast(
        Mock,
        cast(object, response.raise_for_status),
    )
    raise_for_status_mock.side_effect = http_error
    session_mock.get.return_value = response

    client = HttpClient(
        base_url="https://pokeapi.co/api/v2",
        session=session,
    )

    with pytest.raises(DownloadError, match="status 404"):
        client.get("pokemon")


def test_get_json_rejects_invalid_json() -> None:
    session, session_mock = build_session()
    response = build_response()

    json_mock = cast(
        Mock,
        cast(object, response.json),
    )
    json_mock.side_effect = requests.JSONDecodeError(
        "invalid",
        "invalid",
        0,
    )
    session_mock.get.return_value = response

    client = HttpClient(
        base_url="https://pokeapi.co/api/v2",
        session=session,
    )

    with pytest.raises(DownloadError, match="valid JSON"):
        client.get_json("pokemon")


def test_get_rejects_empty_path() -> None:
    client = HttpClient(
        base_url="https://pokeapi.co/api/v2",
    )

    with pytest.raises(ValueError, match="path cannot be empty"):
        client.get("   ")


def test_context_manager_closes_session() -> None:
    session, session_mock = build_session()

    with HttpClient(
        base_url="https://pokeapi.co/api/v2",
        session=session,
    ):
        pass

    session_mock.close.assert_called_once()


def test_settings_build_http_client(tmp_path: Path) -> None:
    from pokedex.config import Settings

    settings = Settings(
        project_root=tmp_path,
        data_dir=tmp_path / "data",
        cache_dir=tmp_path / "cache",
        output_dir=tmp_path / "output",
        logs_dir=tmp_path / "logs",
        pokeapi_base_url="https://example.com/api",
        request_timeout_seconds=12.5,
        request_retries=2,
    )

    client = settings.build_http_client()

    assert client.base_url == "https://example.com/api"
    assert client.timeout_seconds == 12.5

    client.close()
