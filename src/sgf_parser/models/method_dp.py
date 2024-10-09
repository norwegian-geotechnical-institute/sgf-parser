from decimal import Decimal
from typing import Literal, Any

from pydantic import Field, model_validator, computed_field, AliasChoices

from sgf_parser.models import MethodData, Method, MethodType
from sgf_parser.models.types import DPType


class MethodDPData(MethodData):
    """
    Dynamic Probing Data
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    depth: Decimal = Field(..., alias="D", description="Depth (m)")

    penetration_force: Decimal | None = Field(None, alias="A", description="Penetration force (kN)")
    penetration_rate: Decimal | None = Field(
        None,
        validation_alias=AliasChoices(
            "B",  # mm/s
            "C",  # s/0.2m
        ),
        description="Penetration rate (mm/s)",
    )
    torque: Decimal | None = Field(
        None,
        validation_alias=AliasChoices(
            "V",  # kNm
            "AB",  # Nm
        ),
        description="Torque (kNm)",
    )
    ramming: Decimal = Field(None, validation_alias=AliasChoices("S", "SA"), description="Ramming (Blow/0.2 m)")
    rotation_rate: Decimal | None = Field(None, alias="R", description="Rotation rate (rpm)")
    increased_rotation_rate: bool | None = Field(None, alias="AQ")


class MethodDP(Method):
    """
    Dynamic Probing (Swedish Hejarsondering)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    name: str = "DP"
    method_type: Literal[MethodType.DP] = MethodType.DP
    method_data_type: type[MethodDPData] = MethodDPData

    type: DPType

    predrilling_depth: Decimal = Field(Decimal("0"), alias="HO")

    cone_type: str | None = Field(
        None, validation_alias=AliasChoices("KonTyp", "HN", "HC"), description="Type of cone used."
    )
    cushion_type: str | None = Field(None, alias="DynTyp", description="Type of impact cushion used.")
    use_damper: bool | None = Field(None, alias="Gummi", description="Use of damper.")

    method_data: list[MethodDPData] = []

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

    @model_validator(mode="before")
    @classmethod
    def set_operation(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "HM" in data and data["HM"] is not None:
                data["type"] = {
                    "8": DPType.DPSH_A,
                    "108A": DPType.DPSH_A,
                    "108B": DPType.DPL,
                    "108C": DPType.DPM,
                    "108D": DPType.DPH,
                    "9": DPType.DPSH_B,
                    "108E": DPType.DPSH_B,
                }[data["HM"]]

        return data

    @computed_field
    def stopcode(self) -> int | None:
        if not self.method_data:
            return None

        return self.method_data[-1].comment_code
