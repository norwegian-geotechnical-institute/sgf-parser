from typing import Literal

from pydantic import BaseModel

from sgf_parser.models import MethodType


class MethodRPData(BaseModel):
    """
    Method RP data
    """


class MethodRP(BaseModel):
    """
    Method RP
    """

    method_type: Literal[MethodType.RP] = MethodType.RP

    method_data: list[MethodRPData] = []
