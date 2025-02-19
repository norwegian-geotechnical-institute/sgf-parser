from decimal import Decimal
from typing import Literal

from pydantic import Field

from sgf_parser.models import MethodType, MethodData, Method


class MethodTRData(MethodData):
    """
    Method Pressure Sounding Data (Swedish "Trycksondering")
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    depth: Decimal | None = Field(None, alias="D", description="Depth (m)")
    penetration_force: Decimal | None = Field(None, alias="A", description="Penetration force (kN)")
    penetration_rate: Decimal | None = Field(None, alias="B", description="Penetration rate (mm/s)")
    rotation_rate: Decimal | None = Field(None, alias="R", description="Rotation rate (rpm)")
    rod_friction: Decimal | None = Field(None, alias="N", description="Rod friction (kN)")
    increased_rotation_rate: bool | None = Field(None, alias="AQ")


class MethodTR(Method):
    """
    Method Pressure Sounding (Swedish "Trycksondering")
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    name: str = "Tr"
    method_type: Literal[MethodType.TR] = MethodType.TR
    method_data_type: type[MethodTRData] = MethodTRData

    method_data: list[MethodTRData] = []
