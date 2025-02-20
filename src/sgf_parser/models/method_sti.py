from decimal import Decimal
from typing import Literal

from pydantic import Field

from sgf_parser.models import MethodType, MethodData, Method


class MethodSTIData(MethodData):
    """
    Method Light sounding Data (Swedish "Sticksondering")
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    depth: Decimal | None = Field(None, alias="D", description="Depth (m)")


class MethodSTI(Method):
    """
    Method Light sounding (Swedish "Sticksondering")
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    name: str = "Sti"
    method_type: Literal[MethodType.STI] = MethodType.STI
    method_data_type: type[MethodSTIData] = MethodSTIData

    method_data: list[MethodSTIData] = []
