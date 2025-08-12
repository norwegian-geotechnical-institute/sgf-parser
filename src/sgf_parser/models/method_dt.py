from decimal import Decimal
from typing import Literal

from pydantic import Field, AliasChoices

from sgf_parser.models import MethodType, MethodData, Method


class MethodDTData(MethodData):
    """
    Method Pore Pressure Dissipation Test (placeholder)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    time: Decimal | None = Field(None, alias="AD", description="Elapsed time (s)")
    u2: Decimal | None = Field(None, description="Shoulder pressure (kPa)", validation_alias=AliasChoices("U", "AG"))
    fs: Decimal | None = Field(None, description="Friction (kPa)", validation_alias=AliasChoices("FS", "F"))
    qc: Decimal | None = Field(None, description="Resistance (MPa)", validation_alias=AliasChoices("QC", "Q"))
    depth: Decimal | None = Field(None, alias="D", description="Depth (m)")

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.time}>"


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
