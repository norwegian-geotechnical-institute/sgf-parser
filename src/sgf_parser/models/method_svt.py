# # "VS": "vane_size",  # Vingstorlek mm/mm Diameter/höjd
# "IV": "vane_diameter",  # Not in speck, but seen in example files
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import computed_field, Field

from sgf_parser.models import MethodData, MethodType, Method


class MethodSVTData(MethodData):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    depth: Decimal = Field(..., alias="D", description="Depth (m)")

    maximum_measurement_torque: Decimal | None = Field(None, alias="AB", description="Maximum measurement torque (Nm)")
    maximum_measurement_torque_remoulded: Decimal | None = Field(
        None, alias="AB2", description="Maximum measurement torque (Nm)"
    )
    shear_strength: Decimal | None = Field(None, alias="AS", description="Shear strength (kPa)")
    shear_strength_remoulded: Decimal | None = Field(None, description="Shear strength (kPa)")
    sensitivity: Decimal | None = Field(None, alias="SV", description="Sensitivity (unitless)")


class MethodSVT(Method):
    """
    Method SVT
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    name: str = "SRS"
    method_type: Literal[MethodType.SRS] = MethodType.SVT
    method_data_type: type[MethodSVTData] = MethodSVTData

    method_data: list[MethodSVTData] = []

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

    vane_height: Decimal | None = Field(None, description="Height of the vane used (mm).")
    serial_number: str | None = Field(None, alias="HN", description="Serial number of the vane used.")
    calibration_date: datetime | None = Field(None, description="Date of calibration of the vane used.")
