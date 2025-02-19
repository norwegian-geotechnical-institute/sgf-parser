from decimal import Decimal
from typing import Literal

from pydantic import Field

from sgf_parser.models import MethodType, MethodData, Method


class MethodRPData(MethodData):
    """
    Method RP data
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    depth: Decimal = Field(..., alias="D", description="Depth (m)")
    penetration_force: Decimal | None = Field(None, alias="A", description="Penetration force (kN)")
    penetration_rate: Decimal | None = Field(None, alias="B", description="Penetration rate (mm/s)")

    flushing: bool | None = Field(None, alias="AR")
    flushing_pressure: Decimal | None = Field(None, alias="I", description="Flushing pressure (MPa)")
    flushing_flow: Decimal | None = Field(None, alias="J", description="Flushing flow (l/min)")
    rotation_rate: Decimal | None = Field(None, alias="R", description="Rotation rate (rpm)")
    increased_rotation_rate: bool | None = Field(None, alias="AQ")
    torque: Decimal | None = Field(None, alias="V", description="Torque (kNm)")


class MethodRP(Method):
    """
    Method RP
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    name: str = "RP"
    method_type: Literal[MethodType.RP] = MethodType.RP
    method_data_type: type[MethodRPData] = MethodRPData

    method_data: list[MethodRPData] = []

    def post_processing(self):
        """
        Post-processing

        """

        if not self.method_data:
            return

        # Update flushing and increased rotation
        self.flushing_update()
        self.rotation_update()
