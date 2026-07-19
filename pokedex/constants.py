from enum import StrEnum


class Gender(StrEnum):
    """Gender dimension used for visually distinct Pokémon variants."""

    NONE = "None"
    FEMALE = "Female"
    MALE = "Male"


GENDER_SORT_ORDER: dict[Gender, int] = {
    Gender.NONE: 0,
    Gender.FEMALE: 1,
    Gender.MALE: 2,
}


class GameColumn(StrEnum):
    """Supported game availability columns."""

    XY = "XY"
    ORAS = "ORAS"
    SM = "SM"
    USUM = "USUM"
    LGPE = "LGPE"
    SWSH = "SwSh"
    PLA = "Arceus"
    BDSP = "BDSP"
    SV = "ScVi"
    ZA = "ZA"


class OutputColumn(StrEnum):
    """Columns included in the generated Pokédex files."""

    NAT_DEX = "Nat Dex"
    POKEMON = "Pokemon"
    FORM = "Forma"
    GENERATION = "Gen"
    HOME_ID = "ID HOME"
    NAME = "Nombre"
    OBTAINED = "Obtenido"
    PRIORITY = "Prioridad"

    XY = GameColumn.XY
    ORAS = GameColumn.ORAS
    SM = GameColumn.SM
    USUM = GameColumn.USUM
    LGPE = GameColumn.LGPE
    SWSH = GameColumn.SWSH
    PLA = GameColumn.PLA
    BDSP = GameColumn.BDSP
    SV = GameColumn.SV
    ZA = GameColumn.ZA

    LEGENDARY_MYTHICAL = "Legendario/Mítico"
    OBTAINABLE_SHINY = "Obtenible"
    POSSIBLE = "Posibles"


class ExcelSheet(StrEnum):
    """Worksheet names used by the Excel exporter."""

    POKEDEX = "Pokédex"
    SUMMARY = "Resumen"
    VALIDATION = "Validación"
    METADATA = "Metadatos"


GAME_COLUMNS: tuple[GameColumn, ...] = tuple(GameColumn)

OUTPUT_COLUMNS: tuple[OutputColumn, ...] = tuple(OutputColumn)

DEFAULT_FORM_NAME = "Normal"
