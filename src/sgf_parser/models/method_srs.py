from decimal import Decimal
from typing import Literal, Any

from pydantic import computed_field, Field, model_validator

from sgf_parser.models import MethodType, Method, MethodData
from sgf_parser.models.types import SoundingClass, StopCode, CommentCode


class MethodSRSData(MethodData):
    """
    Soil-Rock-Sounding (Swedish Jord-bergsondering)

    Sounding classes:

        12 (Jb-1)
        41 71 (Jb-2)
        42 72 (Jb-3)
        73 (Jb-tot)

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    depth: Decimal = Field(..., alias="D", description="Depth (m)")

    penetration_force: Decimal | None = Field(None, alias="A", description="Penetration force (kN)")
    penetration_rate: Decimal | None = Field(None, alias="B", description="Penetration rate (mm/s)")
    engine_pressure: Decimal | None = Field(None, alias="P", description="Engine pressure (MPa)")
    hammering_pressure: Decimal | None = Field(None, alias="AZ", description="Hammering pressure (MPa)")
    rotation_rate: Decimal | None = Field(None, alias="R", description="Rotation rate (rpm)")
    flushing_pressure: Decimal | None = Field(None, alias="I", description="Flushing pressure (MPa)")
    flushing_flow: Decimal | None = Field(None, alias="J", description="Flushing flow (l/min)")
    flushing: bool | None = Field(None, alias="AR")
    hammering: bool | None = Field(None, alias="AP")
    increased_rotation_rate: bool | None = Field(None, alias="AQ")
    torque: Decimal | None = Field(None, alias="V", description="Torque (kNm)")


class MethodSRS(Method):
    """
    Method SRS
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    name: str = "SRS"
    method_type: Literal[MethodType.SRS] = MethodType.SRS
    method_data_type: type[MethodSRSData] = MethodSRSData

    method_data: list[MethodSRSData] = []

    sounding_class: SoundingClass = SoundingClass.JBTOT

    @computed_field
    def depth_top(self) -> Decimal | None:
        if not self.method_data:
            return None

        return min(method_data.depth for method_data in self.method_data)

    @computed_field
    def depth_base(self) -> Decimal | None:
        if not self.method_data:
            return None

        return max(method_data.depth for method_data in self.method_data)

    @computed_field
    def stopcode(self) -> int | None:
        if not self.method_data:
            return None

        return self.method_data[-1].comment_code

    @model_validator(mode="before")
    @classmethod
    def set_sounding_class(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "HM" in data and data["HM"] is not None:
                data["sounding_class"] = {
                    "12": SoundingClass.JB1,
                    "41": SoundingClass.JB2,
                    "71": SoundingClass.JB2,
                    "42": SoundingClass.JB3,
                    "72": SoundingClass.JB3,
                    "73": SoundingClass.JBTOT,
                }[data["HM"]]

        return data

    def post_processing(self):
        """
        Post-processing

        """

        if not self.method_data:
            return

        # Update flushing, hammering and increased rotation
        self.flushing_update()
        self.hammering_update()
        self.rotation_update()

    @computed_field
    def depth_in_rock(self) -> Decimal | None:
        _rock_top_depth = None
        _rock_base_depth = None

        if not self.method_data:
            return None

        if self.stopcode not in (
            StopCode.STOP_AGAINST_STONE_BLOCK_OR_ROCK_93,
            StopCode.STOP_AGAINST_PRESUMED_ROCK_94,
            StopCode.SOUNDING_INTERRUPTED_95,
        ):
            return None

        for sample in self.method_data[::-1]:
            if sample.comment_code == CommentCode.ROCK_END_42:
                # 42 false positive
                break
            elif sample.comment_code in (
                CommentCode.ROCK_OR_BEDROCK_41,
                CommentCode.BEDROCK_43,
                CommentCode.ROCK_LEVEL_80,
                StopCode.STOP_AGAINST_PRESUMED_ROCK_94,
            ):
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
    def depth_in_soil(self) -> Decimal | None:
        if not self.method_data:
            return None

        if self.stopcode in (StopCode.INTERRUPTED_WITHOUT_STOP_90, StopCode.CANNOT_DRIVE_FURTHER_91):
            return self.method_data[-1].depth

        _depth_in_soil: Decimal | None = None

        for sample in self.method_data[::-1]:
            if sample.comment_code == CommentCode.ROCK_END_42:
                # 42 false positive
                if _depth_in_soil is None:
                    _depth_in_soil = sample.depth
                break
            elif sample.comment_code in (
                CommentCode.ROCK_OR_BEDROCK_41,
                CommentCode.BEDROCK_43,
                StopCode.STOP_AGAINST_PRESUMED_ROCK_94,
                CommentCode.ROCK_LEVEL_80,
            ):
                _depth_in_soil = sample.depth
                break
            elif _depth_in_soil is None:
                _depth_in_soil = sample.depth

        return _depth_in_soil

    @computed_field
    def bedrock_elevation(self) -> Decimal | None:
        # TODO: Unclear how to calculate bedrock elevation.
        #  Is it calculated in the same way as the norwegian total soundings?
        #  Does stop code 95 mean that the sounding was interrupted before reaching bedrock?
        #  Does stop code 80 mean that the sounding reached bedrock?

        if self.point_z is None:
            return None

        _depth_in_soil: Decimal | None = self.depth_in_soil

        if _depth_in_soil is None:
            return None

        if self.stopcode in (
            StopCode.STOP_AGAINST_STONE_BLOCK_OR_ROCK_93,
            StopCode.STOP_AGAINST_PRESUMED_ROCK_94,
            StopCode.SOUNDING_INTERRUPTED_95,  # TODO: Verify this ???
        ):
            return Decimal(self.point_z) - _depth_in_soil

        return None
