from decimal import Decimal
from typing import Literal

from pydantic import Field

from sgf_parser.models import MethodData, Method, MethodType


class MethodWSTData(MethodData):
    """
    Weight Sounding Test (Swedish Viktsondering) Data
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    depth: Decimal = Field(..., alias="D", description="Depth (m)")
    penetration_rate: Decimal | None = Field(None, alias="B", description="Penetration rate (mm/s)")

    hammering: bool | None = Field(None, alias="AP")
    rotation_rate: Decimal | None = Field(None, alias="R", description="Rotation rate (rpm)")

class MethodWST(Method):
    """
    Weight Sounding Test (Swedish Viktsondering)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    name: str = "WST"
    method_type: Literal[MethodType.WST] = MethodType.WST
    method_data_type: type[MethodWSTData] = MethodWSTData

    method_data: list[MethodWSTData] = []
