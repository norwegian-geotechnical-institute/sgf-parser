import enum


class ApplicationClass(enum.IntEnum):
    """
    (
    ONE=1,
    TWO=2,
    THREE=3,
    FOUR=4,
    OUT_OF_BOUNDS=10,
    UNKNOWN=100,
    )
    """

    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    OUT_OF_BOUNDS = 10
    UNKNOWN = 100


class StopCode(enum.IntEnum):
    """
    SGF stop codes

    # Different descriptions found in different documents:
    # 90: Sondering avsluttet uten å ha oppnådd stopp
    # 90: Avbruten utan stopp
    # 91: Fast grunn. Sondering kan ikke drives videre etter normal prosedyre
    # 91: Kan ej neddrivas ytterligare
    # 92  Antatt stein eller blokk
    # 92: Stopp mot sten eller block
    # 93: Antatt berg
    # 93: Stopp mot sten, block eller berg
    # 94: Avsluttet etter boret ønsket dybde i fjell
    # 94: Stopp mot förmodat berg
    # 95: Brudd i borestenger eller spiss
    # 95: Jordbergsondering avbruten
    # 96: Annen material eller maskinfeil
    # 96: Förutbestämt djup (Ny stoppkod enl. Europeiska fältstandarden för CPT-sondering)
    # 97: Boring avsluttet (årsak notert)
    # 97: Max kapacitet (Ny stoppkod enl. Europeiska fältstandarden för CPT-sondering)
    # 98: Max lutning (Ny stoppkod enl. Europeiska fältstandarden för CPT-sondering)
    # 99: Utrustning skadad
    """

    INTERRUPTED_WITHOUT_STOP_90 = 90
    CANNOT_DRIVE_FURTHER_91 = 91
    STOP_AGAINST_STONE_OR_BLOCK_92 = 92
    STOP_AGAINST_STONE_BLOCK_OR_ROCK_93 = 93
    STOP_AGAINST_PRESUMED_ROCK_94 = 94
    SOUNDING_INTERRUPTED_95 = 95
    PREDETERMINED_DEPTH_96 = 96
    MAX_CAPACITY_97 = 97
    MAX_INCLINATION_98 = 98
    EQUIPMENT_DAMAGED_99 = 99


class CommentCode(enum.IntEnum):
    """
    Selected SGF comment codes
    """

    SOIL_END_40 = 40
    ROCK_OR_BEDROCK_41 = 41
    ROCK_END_42 = 42
    BEDROCK_43 = 43
    ROCK_LEVEL_80 = 80


class ParseState(enum.Enum):
    """
    Parse state
    """

    HEADER = 0
    METHOD = 1
    DATA = 2
    QUIT = 3


class FlushingVariant(enum.StrEnum):
    """
    Flushing variants
    """

    CODE_K = "K"
    CODE_AR = "AR"
    CODE_I = "I"


class HammeringVariant(enum.StrEnum):
    """
    Hammering variants
    """

    K = "K"
    AP = "AP"


class RotationVariant(enum.StrEnum):
    """
    Rotation variants
    """

    K = "K"
    AQ = "AQ"
    R = "R"


class SoundingClass(enum.StrEnum):
    """
    Soil-Rock-Sounding (Swedish Jord-bergsondering) classes
    (
    JB1 = Jb-1,
    JB2 = Jb-2,
    JB3 = Jb-3,
    JBTOT = Jb-tot,
    )
    """

    JB1 = "JB1"
    JB2 = "JB2"
    JB3 = "JB3"
    JBTOT = "JBTOT"


class Operation(enum.StrEnum):
    """
    Operation
    """

    MANUAL = "MANUAL"
    MECHANICAL = "MECHANICAL"


class DPType(enum.StrEnum):
    """
    DP Type (Dynamic Probing)

    """

    DPSHA = "DPSHA"
    DPL = "DPL"
    DPM = "DPM"
    DPH = "DPH"
    DPSHB = "DPSHB"
