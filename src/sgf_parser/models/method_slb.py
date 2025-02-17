from decimal import Decimal
from typing import Literal

from pydantic import Field, computed_field

from sgf_parser.models import MethodType, MethodData, Method


class MethodSlbData(MethodData):
    """
    Method Impact sounding Data (Swedish "Slagsondering")
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    depth: Decimal | None = Field(None, alias="D", description="Depth (m)")
    penetration_rate: Decimal | None = Field(None, alias="B", description="Penetration rate (mm/s)")


class MethodSlb(Method):
    """
    Method  Impact sounding (Swedish "Slagsondering")
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    name: str = "Slb"
    method_type: Literal[MethodType.SLB] = MethodType.SLB
    method_data_type: type[MethodSlbData] = MethodSlbData

    method_data: list[MethodSlbData] = []

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
