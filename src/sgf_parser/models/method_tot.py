from decimal import Decimal
from typing import Literal

from pydantic import Field, computed_field

from sgf_parser.models import MethodType, Method, MethodData, StopCode
from sgf_parser.models.types import CommentCode


class MethodTOTData(MethodData):
    """
    Method TOT data
    """

    # "A": "penetration_force",  # "feed_force",
    penetration_force: Decimal | None = Field(None, alias="A", description="Penetration force (kN)")

    # "AB": "maximum_measurement_torque",
    # "AB2": "maximum_measurement_torque_remoulded",
    # "AP": "hammering",
    hammering: bool | None = Field(None, alias="AP")

    # "AZ": "hammering_pressure",
    hammering_pressure: Decimal | None = Field(None, alias="AZ")

    # "AQ": "increased_rotation_rate",
    # "AR": "flushing",  # flushing
    # "AS": "shear_strength",
    # "B": "penetration_rate",  # "penetration_rate",
    penetration_rate: Decimal | None = Field(None, alias="B", description="Penetration rate (mm/s)")

    # # "C": "penetration_resistance",  # B = 200/C  (unit: s/0.2m)
    # penetration_resistance: Decimal | None = Field(None, alias="C")

    # "D": "depth",  # "depth",
    depth: Decimal = Field(..., alias="D", description="Depth (m)")

    # # "F": "fs",  # "friction"  Envi format
    # # "FS": "fs",  # "friction" Geotech format
    # "I": "flushing_pressure",
    flushing_pressure: Decimal | None = Field(None, alias="I")

    # "J": "flushing_flow",
    flushing_flow: Decimal | None = Field(None, alias="J")

    # "K": "comment_code",  # "comment_code"
    comment_code: int | None = Field(None, alias="K")

    # "M": "conductivity",  # "conductivity",
    # "NA": "zero_value_resistance",  # "zero_value_resistance",
    # "NB": "zero_value_friction",  # "zero_value_friction",
    # "NC": "zero_value_pressure",  # "zero_value_pressure",
    # "O": "temperature",  # "temperature",

    # "P": "engine_pressure",
    engine_pressure: Decimal | None = Field(None, alias="P")

    # # "Q": "qc",  # "resistance" Envi format
    # # "QC": "qc",  # "resistance" Geotech format
    # "R": "rotation_rate",
    rotation_rate: Decimal | None = Field(None, alias="R")

    # "SV": "sensitivity",
    # "T": "remarks",  # "text",
    remarks: str | None = Field(None, alias="T")

    # "TA": "tilt",  # "tilt",
    # "U": "u2",  # "shoulder_pressure",

    # "V": "torque",  # Vridmoment
    torque: Decimal | None = Field(None, alias="V")


class MethodTOT(Method):
    """
    Method TOT
    """

    name: str = "TOT"

    method_type: Literal[MethodType.TOT] = MethodType.TOT
    method_data_type: type[MethodTOTData] = MethodTOTData
    method_data: list[MethodTOTData] = []

    @computed_field
    @property
    def depth_top(self) -> Decimal | None:
        if not self.method_data:
            return None

        return min(method_data.depth for method_data in self.method_data)

    @computed_field
    @property
    def depth_base(self) -> Decimal | None:
        if not self.method_data:
            return None

        return max(method_data.depth for method_data in self.method_data)

    @computed_field
    @property
    def stopcode(self) -> int | None:
        if not self.method_data:
            return None

        return self.method_data[-1].comment_code

    @computed_field
    @property
    def depth_in_rock(self) -> Decimal | None:
        _rock_top_depth = None
        _rock_base_depth = None

        if not self.method_data:
            return None

        if self.stopcode not in (
            StopCode.STOP_AGAINST_STONE_BLOCK_OR_ROCK_93,
            StopCode.STOP_AGAINST_PRESUMED_ROCK_94,
        ):
            return None

        for sample in self.method_data[::-1]:
            if sample.comment_code == CommentCode.ROCK_END_42:
                # 42 false positive
                break
            elif sample.comment_code in (CommentCode.ROCK_OR_BEDROCK_41, CommentCode.BEDROCK_43):
                _rock_top_depth = sample.depth
                if _rock_base_depth is None:
                    _rock_base_depth = sample.depth
                break
            elif _rock_base_depth is None:
                _rock_base_depth = sample.depth

        if _rock_top_depth is None or _rock_base_depth is None:
            depth_in_rock = None
        else:
            depth_in_rock = _rock_base_depth - _rock_top_depth

        return depth_in_rock

    @computed_field
    @property
    def depth_in_soil(self) -> Decimal | None:
        _depth_in_soil = None

        if not self.method_data:
            return None

        if self.stopcode in (StopCode.INTERRUPTED_WITHOUT_STOP_90, StopCode.CANNOT_DRIVE_FURTHER_91):
            return self.method_data[-1].depth

        for sample in self.method_data[::-1]:
            if sample.comment_code == CommentCode.ROCK_END_42:
                # 42 false positive
                if _depth_in_soil is None:
                    _depth_in_soil = sample.depth
                break
            elif sample.comment_code in (CommentCode.ROCK_OR_BEDROCK_41, CommentCode.BEDROCK_43):
                _depth_in_soil = sample.depth
                break
            elif _depth_in_soil is None:
                _depth_in_soil = sample.depth

        return _depth_in_soil

    @computed_field
    @property
    def bedrock_elevation(self) -> Decimal | None:
        if self.depth_in_soil is None:
            return None

        if self.point_z is None:
            return None

        if self.stopcode in (StopCode.STOP_AGAINST_STONE_BLOCK_OR_ROCK_93, StopCode.STOP_AGAINST_PRESUMED_ROCK_94):
            return Decimal(self.point_z) - self.depth_in_soil

        return None
