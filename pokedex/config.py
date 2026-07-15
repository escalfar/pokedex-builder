from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from pokedex.cache import JsonCache
from pokedex.http import HttpClient
from pokedex.pokeapi import PokeApiClient
from pokedex.form_rules import FormRules

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Validated application settings."""

    model_config = SettingsConfigDict(
        env_prefix="POKEDEX_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
    )

    project_root: Path = PROJECT_ROOT
    data_dir: Path = PROJECT_ROOT / "data"
    cache_dir: Path = PROJECT_ROOT / "cache"
    output_dir: Path = PROJECT_ROOT / "output"
    logs_dir: Path = PROJECT_ROOT / "logs"
    form_rules_path: Path = PROJECT_ROOT / "data" / "form_rules.yaml"

    pokeapi_base_url: str = "https://pokeapi.co/api/v2"
    request_timeout_seconds: float = Field(default=30.0, gt=0)
    request_retries: int = Field(default=3, ge=0)
    cache_ttl_hours: int = Field(default=168, ge=0)

    user_agent: str = "pokedex-builder/0.1.0"

    def create_directories(self) -> None:
        """Create the directories required by the application."""
        for directory in (
            self.data_dir,
            self.cache_dir,
            self.output_dir,
            self.logs_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def build_cache(self) -> "JsonCache":
        return JsonCache(
            directory=self.cache_dir,
            ttl_hours=self.cache_ttl_hours,
        )

    def build_http_client(self) -> "HttpClient":
        return HttpClient(
            base_url=self.pokeapi_base_url,
            timeout_seconds=self.request_timeout_seconds,
            retries=self.request_retries,
            user_agent=self.user_agent,
        )

    def build_pokeapi_client(self) -> "PokeApiClient":
        return PokeApiClient(
            http_client=self.build_http_client(),
            cache=self.build_cache(),
        )

    def load_form_rules(self) -> "FormRules":
        return FormRules.from_yaml(self.form_rules_path)


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
