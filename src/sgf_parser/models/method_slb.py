from decimal import Decimal
from typing import Literal

from pydantic import Field

from sgf_parser.models import MethodType, MethodData, Method


class MethodSLBData(MethodData):
    """
    Method Impact sounding Data (Swedish "Slagsondering")
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    depth: Decimal | None = Field(None, alias="D", description="Depth (m)")
    penetration_rate: Decimal | None = Field(None, alias="B", description="Penetration rate (mm/s)")


class MethodSLB(Method):
    """
    Method Impact sounding (Swedish "Slagsondering")
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    name: str = "Slb"
    method_type: Literal[MethodType.SLB] = MethodType.SLB
    method_data_type: type[MethodSLBData] = MethodSLBData

    method_data: list[MethodSLBData] = []
