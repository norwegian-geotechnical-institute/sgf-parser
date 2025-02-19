from decimal import Decimal
from typing import Literal

from pydantic import Field

from sgf_parser.models import MethodType, MethodData, Method


class MethodStiData(MethodData):
    """
    Method Impact sounding Data (Swedish "Slagsondering")
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    depth: Decimal | None = Field(None, alias="D", description="Depth (m)")


class MethodSti(Method):
    """
    Method  Impact sounding (Swedish "Slagsondering")
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    name: str = "Sti"
    method_type: Literal[MethodType.STI] = MethodType.STI
    method_data_type: type[MethodStiData] = MethodStiData

    method_data: list[MethodStiData] = []
