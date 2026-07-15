from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from pokedex.cache import JsonCache
from pokedex.form_overrides import FormOverrides
from pokedex.form_rules import FormRules
from pokedex.game_availability import GameAvailabilityRules
from pokedex.gender_differences import GenderDifferenceRules
from pokedex.http import HttpClient
from pokedex.pokeapi import PokeApiClient
from pokedex.shiny_availability import ShinyAvailabilityRules

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Validated application settings and dependency factories."""

    model_config = SettingsConfigDict(
        env_prefix="POKEDEX_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
    )

    project_root: Path = PROJECT_ROOT
    data_dir: Path = PROJECT_ROOT / "data"
    output_dir: Path = PROJECT_ROOT / "output"
    cache_dir: Path = PROJECT_ROOT / "cache"
    logs_dir: Path = PROJECT_ROOT / "logs"

    form_rules_path: Path = PROJECT_ROOT / "data" / "form_rules.yaml"
    form_overrides_path: Path = PROJECT_ROOT / "data" / "form_overrides.yaml"
    gender_differences_path: Path = PROJECT_ROOT / "data" / "gender_differences.yaml"
    game_availability_path: Path = PROJECT_ROOT / "data" / "game_availability.yaml"
    shiny_availability_path: Path = PROJECT_ROOT / "data" / "shiny_availability.yaml"

    csv_output_path: Path = PROJECT_ROOT / "output" / "Pokedex.csv"
    json_output_path: Path = PROJECT_ROOT / "output" / "Pokedex.json"
    excel_output_path: Path = PROJECT_ROOT / "output" / "Pokedex.xlsx"
    catalog_coverage_output_path: Path = (
        PROJECT_ROOT / "output" / "Catalog_Coverage.json"
    )

    pokeapi_base_url: str = "https://pokeapi.co/api/v2"
    request_timeout_seconds: float = Field(default=30.0, gt=0)
    request_retries: int = Field(default=3, ge=0)
    cache_ttl_hours: int = Field(default=168, ge=0)

    user_agent: str = "pokedex-builder/0.1.0"

    def create_directories(self) -> None:
        """Create every directory required by the application."""
        for directory in (
            self.data_dir,
            self.cache_dir,
            self.output_dir,
            self.logs_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def build_cache(self) -> JsonCache:
        """Create the configured JSON cache."""
        return JsonCache(
            directory=self.cache_dir,
            ttl_hours=self.cache_ttl_hours,
        )

    def build_http_client(self) -> HttpClient:
        """Create the configured reusable HTTP client."""
        return HttpClient(
            base_url=self.pokeapi_base_url,
            timeout_seconds=self.request_timeout_seconds,
            retries=self.request_retries,
            user_agent=self.user_agent,
        )

    def build_pokeapi_client(self) -> PokeApiClient:
        """Create the high-level PokéAPI client."""
        return PokeApiClient(
            http_client=self.build_http_client(),
            cache=self.build_cache(),
        )

    def load_form_rules(self) -> FormRules:
        """Load form inclusion and exclusion rules."""
        return FormRules.from_yaml(self.form_rules_path)

    def load_form_overrides(self) -> FormOverrides:
        """Load naming and generation overrides for forms."""
        return FormOverrides.from_yaml(self.form_overrides_path)

    def load_gender_difference_rules(self) -> GenderDifferenceRules:
        """Load the catalog of visible gender differences."""
        return GenderDifferenceRules.from_yaml(self.gender_differences_path)

    def load_game_availability_rules(self) -> GameAvailabilityRules:
        """Load the curated availability catalog for supported games."""
        return GameAvailabilityRules.from_yaml(self.game_availability_path)

    def load_shiny_availability_rules(self) -> ShinyAvailabilityRules:
        """Load the curated non-event shiny availability catalog."""
        return ShinyAvailabilityRules.from_yaml(self.shiny_availability_path)


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()
