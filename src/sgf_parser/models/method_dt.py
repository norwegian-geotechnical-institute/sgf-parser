from decimal import Decimal
from typing import Literal

from pydantic import Field, computed_field

from sgf_parser.models import MethodType, MethodData, Method


class MethodDTData(MethodData):
    """
    Method Pore Pressure Dissipation Test (placeholder)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    elapsed_time: Decimal | None = Field(None, alias="AD", description="Elapsed time (s)")
    u2: Decimal | None = Field(None, alias="AG", description="Shoulder pressure (kPa)")
    depth: None = None

class MethodDT(Method):
    """
    Method Pore Pressure Dissipation Test (placeholder)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    name: str = "DT"
    method_type: Literal[MethodType.DT] = MethodType.DT
    method_data_type: type[MethodDTData] = MethodDTData

    method_data: list[MethodDTData] = []

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

    def post_processing(self):
        """
        Post-processing

        """

        if not self.method_data:
            return