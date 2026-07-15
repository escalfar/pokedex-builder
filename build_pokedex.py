from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence

from pokedex.config import Settings, get_settings
from pokedex.exceptions import PokedexError
from pokedex.logger import configure_logger
from pokedex.pokeapi import PokeApiClient


def build_argument_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="pokedex-builder",
        description="Generate the National Pokédex datasets.",
    )

    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Ignore cached data and download fresh source data.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run validations without generating output files.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="pokedex-builder 0.1.0",
    )

    return parser


def initialize_application(settings: Settings) -> logging.Logger:
    """Create required directories and configure application logging."""
    settings.create_directories()

    return configure_logger(
        logs_directory=settings.logs_dir,
    )


def run(
    settings: Settings,
    *,
    refresh_cache: bool = False,
    validate_only: bool = False,
) -> int:
    """Run the application.

    The current implementation only initializes the project infrastructure.
    Data downloading and export generation will be added in later milestones.
    """
    logger = initialize_application(settings)

    logger.info("Starting Pokédex Builder")
    logger.info("Project root: %s", settings.project_root)
    logger.info("Cache directory: %s", settings.cache_dir)
    logger.info("Output directory: %s", settings.output_dir)
    logger.info("Refresh cache: %s", refresh_cache)
    logger.info("Validation only: %s", validate_only)

    with settings.build_http_client() as http_client:
        pokeapi_client = PokeApiClient(
            http_client=http_client,
            cache=settings.build_cache(),
        )

        species = pokeapi_client.get_species_details(
            refresh_cache=refresh_cache,
        )

    logger.info(
        "Loaded %s normalized Pokémon species",
        len(species),
    )

    if validate_only:
        logger.info("Validation mode initialized")
    else:
        logger.info("Generation mode initialized")

    logger.info("Application infrastructure initialized successfully")

    return 0


def main(arguments: Sequence[str] | None = None) -> int:
    """Parse command-line arguments and execute the application."""
    parser = build_argument_parser()
    parsed_arguments = parser.parse_args(arguments)
    settings = get_settings()

    try:
        return run(
            settings,
            refresh_cache=parsed_arguments.refresh_cache,
            validate_only=parsed_arguments.validate,
        )
    except PokedexError as error:
        logging.getLogger("pokedex_builder").exception(
            "Pokédex Builder failed: %s",
            error,
        )
        return 1
    except OSError as error:
        logging.getLogger("pokedex_builder").exception(
            "System error: %s",
            error,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
