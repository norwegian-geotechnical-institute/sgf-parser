from decimal import Decimal
from typing import Literal, Any

from pydantic import Field, model_validator, computed_field

from sgf_parser.models import MethodData, Method, MethodType
from sgf_parser.models.types import Operation


class MethodWSTData(MethodData):
    """
    Weight Sounding Test (Swedish Viktsondering) Data
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    depth: Decimal = Field(..., alias="D", description="Depth (m)")
    turning: Decimal = Field(..., alias="H", description="Turning (half revolution/0.2 m)")
    load: Decimal = Field(..., alias="W", description="Load (kN)")
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

    operation: Operation = Operation.MECHANICAL

    method_data: list[MethodWSTData] = []

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
                data["operation"] = {
                    "101": Operation.MANUAL,
                    "102": Operation.MECHANICAL,
                }[data["HM"]]

        return data
