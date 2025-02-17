from decimal import Decimal
from typing import Literal

from pydantic import Field, computed_field

from sgf_parser.models import MethodType, MethodData, Method


class MethodTrData(MethodData):
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


class MethodTr(Method):
    """
    Method Pressure Sounding (Swedish "Trycksondering")
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    name: str = "Tr"
    method_type: Literal[MethodType.TR] = MethodType.TR
    method_data_type: type[MethodTrData] = MethodTrData

    method_data: list[MethodTrData] = []

    @computed_field
    def stopcode(self) -> int | None:
        if not self.method_data:
            return None

        return self.method_data[-1].comment_code

    def post_processing(self):
        """
        Post-processing

        """

        if not self.method_data:
            return
