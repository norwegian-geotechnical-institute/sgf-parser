import abc
import re
from datetime import datetime, time
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, AliasChoices, model_validator

from sgf_parser.datetime_parser import convert_str_to_datetime, convert_str_to_time
from sgf_parser.models import MethodType


class MethodData(BaseModel, abc.ABC):
    @classmethod
    def _fix_malformed_data(cls, code: str) -> str | None:
        return re.sub("[^0-9]", "", code)

    @classmethod
    def _extract_comment_code(cls, data: dict[str, Any]) -> tuple[int, str | None]:
        """
        If more than one code, prioritize the codes in the following order:
        Range 40-43 before any other code
        Store the first code that matches the priority in `K` and move the rest to `T` as string
        """
        if ", " in data["K"]:
            codes = data["K"].split(", ")
            sorted_codes = sorted(
                codes,
                key=lambda code: "0"
                if code in ("40", "41", "42", "43")
                else (" " if code in ("90", "91", "92", "93", "94", "95", "96", "97", "98", "99") else code),
                reverse=False,
            )
            code = sorted_codes[0]
            rest = ", ".join(sorted_codes[1:]) if len(sorted_codes) > 1 else None
        elif data["K"].isdecimal():
            code = data["K"]
            rest = None
        else:
            code = cls._fix_malformed_data(data["K"])
            rest = None

        return int(code), rest

    @model_validator(mode="before")
    @classmethod
    def comment_code_format(cls, data: Any) -> Any:
        """
        The comment code we return should be an integer.
        But there are string variants of the codes that we need to convert to integers.
        Sometimes we get more than one code on a data row, then we need to prioritize what code to keep.
        """
        if isinstance(data, dict):
            # Detect string variants of the comment code and convert them to integers
            if "K" in data and data["K"] is not None:
                _code, _rest = cls._extract_comment_code(data)
                data["K"] = _code
                if _rest:
                    if data["T"]:
                        data["T"] = f"{_rest}, {data['T']}"
                    else:
                        data["T"] = _rest

        return data


class Method(BaseModel, abc.ABC):
    def post_processing(self):
        pass

    @model_validator(mode="before")
    @classmethod
    def guess_date_format(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "HI" in data and data["HI"] is not None:
                data["HI"] = convert_str_to_time(data["HI"])

            if "KD" in data and data["KD"] is not None and "HD" not in data:
                # If KD is present, but HD is not, set HD since it is the same as KD
                data["HD"] = convert_str_to_datetime(data["KD"])

            if "HD" in data and data["HD"] is not None:
                data["HD"] = convert_str_to_datetime(data["HD"])

            if "HI" in data and data["HI"] is not None and "HD" in data and data["HD"] is not None:
                data["HD"] = datetime.combine(data["HD"], data["HI"])

        return data

    method_type: MethodType
    method_data_type: type[MethodData]

    # name: str | None = None

    location_name: str | None = Field(None, alias="KP")
    project_number: str | None = Field(None, alias="HJ")
    method_type_string: str | None = Field(None, alias="HM")

    # HX, HY, HZ
    point_x: float | None = Field(None, alias="HX")
    point_y: float | None = Field(None, alias="HY")
    point_z: float | None = Field(None, alias="HZ")

    # "HD": "conducted_at",  # Date
    # # "KD": "conducted_at",  # Date
    conducted_at: datetime | None = Field(None, validation_alias=AliasChoices("HD", "KD"))
    conducted_time: time | None = Field(None, alias="HI")
    # "HC": "serial_number",
    serial_number: str | None = Field(None, alias="HC")

    # "HO": "predrilling_depth",
    predrilling_depth: Decimal = Field(0, alias="HO")

    # "HQ": "conducted_by",
    conducted_by: str | None = Field(None, alias="HQ")

    # "HN": "cone_reference",
    cone_reference: str | None = Field(None, alias="HN")

    # # "HG": "groundwater_level",
    # "HP": "water_depth",

    # "HT": "remarks",
    remarks: str | None = Field(None, alias="HT")

    # "MA": "cone_area_ratio",  # same as header code IE
    # "IE": "cone_area_ratio",  # same as header code MA
    cone_area_ratio: Decimal | None = Field(None, validation_alias=AliasChoices("IE", "MA"))

    # "MB": "sleeve_area_ratio",  # same as header code IF
    # "IF": "sleeve_area_ratio",  # same as header code MB
    sleeve_area_ratio: Decimal | None = Field(None, validation_alias=AliasChoices("IF", "MB"))

    # "IV": "vane_diameter",  # Not in spec, but seen in example files
    vane_diameter: Decimal | None = Field(None, alias="IV")

    method_data: list[MethodData]
