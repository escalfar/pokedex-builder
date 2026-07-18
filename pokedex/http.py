from __future__ import annotations

from collections.abc import Mapping
from typing import Final, cast

import requests
from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pokedex.cache import JsonValue
from pokedex.exceptions import DownloadError

DEFAULT_RETRY_STATUS_CODES: Final[tuple[int, ...]] = (
    429,
    500,
    502,
    503,
    504,
)

DEFAULT_ALLOWED_METHODS: Final[frozenset[str]] = frozenset(
    {
        "DELETE",
        "GET",
        "HEAD",
        "OPTIONS",
        "PUT",
    }
)


class HttpClient:
    """Reusable HTTP client with retries and centralized error handling."""

    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float = 30.0,
        retries: int = 3,
        user_agent: str = "pokedex-builder/0.1.0",
        backoff_factor: float = 0.5,
        session: Session | None = None,
    ) -> None:
        if not base_url.strip():
            raise ValueError("Base URL cannot be empty.")

        if timeout_seconds <= 0:
            raise ValueError("Timeout must be greater than zero.")

        if retries < 0:
            raise ValueError("Retries cannot be negative.")

        if backoff_factor < 0:
            raise ValueError("Backoff factor cannot be negative.")

        if not user_agent.strip():
            raise ValueError("User-Agent cannot be empty.")

        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._session = session or requests.Session()

        self._session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": user_agent,
            }
        )

        retry_strategy = Retry(
            total=retries,
            connect=retries,
            read=retries,
            status=retries,
            allowed_methods=DEFAULT_ALLOWED_METHODS,
            status_forcelist=DEFAULT_RETRY_STATUS_CODES,
            backoff_factor=backoff_factor,
            respect_retry_after_header=True,
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    @property
    def base_url(self) -> str:
        """Return the normalized base URL."""
        return self._base_url

    @property
    def timeout_seconds(self) -> float:
        """Return the request timeout."""
        return self._timeout_seconds

    def get(
        self,
        path: str,
        *,
        params: Mapping[str, str | int | float | bool] | None = None,
    ) -> Response:
        """Perform a GET request and return a successful response."""
        url = self._build_url(path)

        try:
            response = self._session.get(
                url,
                params=params,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
        except requests.Timeout as error:
            raise DownloadError(
                f"Request timed out after {self._timeout_seconds} seconds: {url}"
            ) from error
        except requests.ConnectionError as error:
            raise DownloadError(f"Unable to connect to: {url}") from error
        except requests.HTTPError as error:
            status_code = (
                error.response.status_code if error.response is not None else "unknown"
            )
            raise DownloadError(
                f"HTTP request failed with status {status_code}: {url}"
            ) from error
        except requests.RequestException as error:
            raise DownloadError(f"HTTP request failed: {url}") from error

        return response

    def get_json(
        self,
        path: str,
        *,
        params: Mapping[str, str | int | float | bool] | None = None,
    ) -> JsonValue:
        """Perform a GET request and deserialize its JSON body."""
        response = self.get(path, params=params)

        try:
            payload = response.json()
        except requests.JSONDecodeError as error:
            raise DownloadError(
                f"Response does not contain valid JSON: {response.url}"
            ) from error

        return cast(JsonValue, payload)

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> HttpClient:
        """Return the client when entering a context manager."""
        return self

    def __exit__(
        self,
        exception_type: object,
        exception_value: object,
        traceback: object,
    ) -> None:
        """Close the client when leaving a context manager."""
        self.close()

    def _build_url(self, path: str) -> str:
        """Build an absolute URL from a relative path."""
        normalized_path = path.strip()

        if not normalized_path:
            raise ValueError("Request path cannot be empty.")

        if normalized_path.startswith(("http://", "https://")):
            return normalized_path

        return f"{self._base_url}/{normalized_path.lstrip('/')}"
