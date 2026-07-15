from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence

from pokedex.config import Settings, get_settings
from pokedex.catalog_coverage import (
    build_catalog_coverage_report,
    export_catalog_coverage_json,
)
from pokedex.exceptions import PokedexError
from pokedex.logger import configure_logger
from pokedex.pokeapi import PokeApiClient
from pokedex.species import build_species
from pokedex.variants import build_pokemon_variants
from pokedex.form_rules import filter_pokemon_variants
from pokedex.form_overrides import apply_form_overrides
from pokedex.entries import build_pokemon_entries
from pokedex.game_availability import apply_game_availability
from pokedex.shiny_availability import apply_shiny_availability
from pokedex.gender_differences import expand_gender_differences
from pokedex.exporter_csv import export_csv
from pokedex.exporter_json import export_json
from pokedex.exporter_excel import export_excel


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

    if validate_only:
        logger.info("Validation mode initialized")
    else:
        logger.info("Generation mode initialized")

    with settings.build_http_client() as http_client:
        pokeapi_client = PokeApiClient(
            http_client=http_client,
            cache=settings.build_cache(),
        )

        species_details = pokeapi_client.get_species_details(
            refresh_cache=refresh_cache,
        )

    species = build_species(species_details)

    logger.info(
        "Loaded and validated %s Pokémon species",
        len(species),
    )

    logger.info(
        "National Pokédex range: %s–%s",
        species[0].national_dex,
        species[-1].national_dex,
    )

    legendary_count = sum(item.is_legendary for item in species)

    mythical_count = sum(item.is_mythical for item in species)

    logger.info(
        "Legendary species: %s",
        legendary_count,
    )

    logger.info(
        "Mythical species: %s",
        mythical_count,
    )

    pokemon_variants = build_pokemon_variants(
        species_details,
        species,
    )

    logger.info(
        "Built and validated %s Pokémon variants",
        len(pokemon_variants),
    )

    non_default_count = sum(not candidate.is_default for candidate in pokemon_variants)

    logger.info(
        "Non-default Pokémon variants: %s",
        non_default_count,
    )

    form_rules = settings.load_form_rules()

    filtered_variants = filter_pokemon_variants(
        pokemon_variants,
        form_rules,
    )

    excluded_count = len(pokemon_variants) - len(filtered_variants)

    logger.info(
        "Included Pokémon variants: %s",
        len(filtered_variants),
    )

    logger.info(
        "Excluded Pokémon variants: %s",
        excluded_count,
    )

    form_overrides = settings.load_form_overrides()

    normalized_variants = apply_form_overrides(
        filtered_variants,
        form_overrides,
    )

    logger.info(
        "Normalized %s included Pokémon variants",
        len(normalized_variants),
    )

    gender_rules = settings.load_gender_difference_rules()
    gender_expanded_variants = expand_gender_differences(
        normalized_variants,
        gender_rules,
    )

    logger.info(
        "Expanded variants to %s rows after gender differences",
        len(gender_expanded_variants),
    )

    variant_counts: dict[int, int] = {}

    for variant in gender_expanded_variants:
        variant_counts[variant.national_dex] = (
            variant_counts.get(
                variant.national_dex,
                0,
            )
            + 1
        )

    species_with_multiple_variants = sum(count > 1 for count in variant_counts.values())

    logger.info(
        "Species with multiple included variants: %s",
        species_with_multiple_variants,
    )

    pokemon_entries = build_pokemon_entries(
        gender_expanded_variants,
        species,
    )

    logger.info(
        "Built %s preliminary export entries",
        len(pokemon_entries),
    )

    availability_rules = settings.load_game_availability_rules()
    pokemon_entries = apply_game_availability(
        pokemon_entries,
        availability_rules,
    )

    if not availability_rules.complete:
        # The catalog starts conservative: unknown values remain FALSE
        # instead of being inferred from incomplete public data.
        logger.warning(
            "Game availability catalog is incomplete; " "unlisted variants remain FALSE"
        )

    shiny_rules = settings.load_shiny_availability_rules()
    pokemon_entries = apply_shiny_availability(
        pokemon_entries,
        shiny_rules,
    )

    if not shiny_rules.complete:
        # Unknown shiny status stays FALSE until the variant is verified.
        logger.warning(
            "Shiny availability catalog is incomplete; "
            "unlisted variants remain FALSE"
        )

    coverage_report = build_catalog_coverage_report(
        pokemon_entries,
        availability_rules,
        shiny_rules,
    )

    for game, counts in coverage_report.games.items():
        logger.info(
            "Catalog coverage for %s: %.2f%% (%s/%s verified)",
            game.value,
            counts.percent,
            counts.verified,
            counts.total,
        )

    logger.info(
        "Catalog coverage for shiny availability: %.2f%% (%s/%s verified)",
        coverage_report.shiny.percent,
        coverage_report.shiny.verified,
        coverage_report.shiny.total,
    )

    if validate_only:
        logger.info("Validation completed; output generation skipped")
    else:
        csv_path = export_csv(
            pokemon_entries,
            settings.csv_output_path,
        )

        json_path = export_json(
            pokemon_entries,
            settings.json_output_path,
        )

        coverage_path = export_catalog_coverage_json(
            coverage_report,
            settings.catalog_coverage_output_path,
        )

        excel_path = export_excel(
            pokemon_entries,
            settings.excel_output_path,
        )

        logger.info(
            "CSV exported to: %s",
            csv_path,
        )

        logger.info(
            "JSON exported to: %s",
            json_path,
        )

        logger.info(
            "Catalog coverage exported to: %s",
            coverage_path,
        )

        logger.info(
            "Excel exported to: %s",
            excel_path,
        )

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
