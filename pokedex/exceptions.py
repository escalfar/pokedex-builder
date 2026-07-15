class PokedexError(Exception):
    """Base exception for all Pokédex Builder errors."""


class ConfigurationError(PokedexError):
    """Raised when the application configuration is invalid."""


class DownloadError(PokedexError):
    """Raised when data cannot be downloaded."""


class CacheError(PokedexError):
    """Raised when cached data cannot be read or written."""


class ValidationError(PokedexError):
    """Raised when generated Pokédex data fails validation."""
