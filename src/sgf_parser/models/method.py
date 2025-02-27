import abc
import re
from datetime import datetime, time
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, AliasChoices, model_validator, computed_field

from sgf_parser.datetime_parser import convert_str_to_datetime, convert_str_to_time
from sgf_parser.models import MethodType
from sgf_parser.models.types import FlushingVariant, HammeringVariant, RotationVariant


class MethodData(BaseModel, abc.ABC):
    @classmethod
    def _fix_malformed_data(cls, code: str) -> str | None:
        """Wrong K codes as "4,0" will be converted to "40"."""
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
            if "K" in data and data["K"] is not None:
                # We want to interpret K as a stop code (with integer value)
                # sometimes K is a string with e.g. "SAND", in that case we move it to T
                K_is_digit = any(char.isdigit() for char in data["K"])

                if not K_is_digit:
                    # move it to T (remarks column)
                    if "T" not in data:
                        data["T"] = data["K"]
                    else:
                        data["T"] = f"{data['K']}, {data['T']}"

                    del data["K"]

                else:
                    # we identify the most important stop code, and move the rest to T
                    _code, _rest = cls._extract_comment_code(data)
                    data["K"] = _code
                    if _rest:
                        if "T" not in data:
                            data["T"] = _rest
                        else:
                            data["T"] = f"{_rest}, {data['T']}"

        return data

    # "K": "comment_code",  # "comment_code"
    comment_code: int | None = Field(None, alias="K")
    remarks: str | None = Field(None, alias="T")

    @model_validator(mode="before")
    @classmethod
    def penetration_rate_validator(cls, data: Any) -> Any:
        """
        If the penetration rate (B mm/s) is not set, but C is (s/0.2m) then convert C to B and set B.
        """
        if isinstance(data, dict):
            if ("B" not in data or data["B"] is None) and "C" in data and data["C"] is not None:
                # B is not set, but C is, convert C to B
                try:
                    data["B"] = 200 / float(data["C"])
                except (ZeroDivisionError, ValueError):
                    data["B"] = None

        return data

    @model_validator(mode="before")
    @classmethod
    def torque_validator(cls, data: Any) -> Any:
        """
        If the torque V (kNm) is not set, but AB is (Nm) then convert AB to V and set V.
        """
        if isinstance(data, dict):
            if ("V" not in data or data["V"] is None) and "AB" in data and data["AB"] is not None:
                try:
                    data["V"] = float(data["AB"]) / 1000
                except ValueError:
                    data["V"] = None

        return data

    @model_validator(mode="before")
    @classmethod
    def ramming_validator(cls, data: Any) -> Any:
        """
        If the ramming S (blows/0.2m) is not set, but SA is (blows/0.1m) then convert SA to S and set S.
        """
        if isinstance(data, dict):
            if ("S" not in data or data["S"] is None) and "SA" in data and data["SA"] is not None:
                try:
                    data["S"] = float(data["SA"]) * 2
                except ValueError:
                    data["S"] = None

        return data

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.depth}>"


# class Method(BaseModel, abc.ABC):
class Method(BaseModel):
    _flushing_variant: FlushingVariant | None = None
    _current_flushing_active_state: bool = False
    _hammering_variant: HammeringVariant | None = None
    _current_hammer_active_state: bool = False
    _rotation_variant: RotationVariant | None = None
    _current_increased_rotation_state: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def post_processing(self):
        pass

    def detect_flushing_rule(self) -> FlushingVariant:
        """
        Call this with the method data before parsing the method data.

        The result of calling this method will set the self.detected_flushing_variant to either use the "K" code if any
        regulating the flushing are present, the "AR" (flushing on/off) code or the "I" (flushing pressure) code.
        """
        if self._flushing_variant:
            return self._flushing_variant

        if any(
            [
                row.comment_code in (72, 73, 76, 77)
                or any(x in (72, 73, 76, 77) for x in self.extract_codes(row.remarks))
                for row in self.method_data
            ]
        ):
            self._flushing_variant = FlushingVariant.CODE_K
        elif any([getattr(row, "flushing") is not None for row in self.method_data]):
            self._flushing_variant = FlushingVariant.CODE_AR
        else:
            self._flushing_variant = FlushingVariant.CODE_I

        return self._flushing_variant

    @classmethod
    def extract_codes(cls, remarks: str | None) -> tuple[int, ...]:
        """
        Extract any two-digit codes from the remarks string.

        Must be on the format "
        """
        if not remarks:
            return tuple()

        result = re.findall(r"(?:^| )(\d\d)(?:,|$)", remarks)
        return tuple(int(r) for r in result)

    def is_flushing_active(
        self,
        data_row,  #: "MethodCPTData" | "MethodTOTData" | "MethodRPData",
    ) -> bool:
        """
        Indicate if flushing is active at given depth.

        The following priority should be used to figure out if flushing is active:

        1. Check K (kode) regulating flushing in file, use only K codes
        2. If no K codes present in file, then check if "AR" code is present and has
           a value (0 or 0.0 = off, 1 or 1.0 = on)
        3. If no "AR" code is present in the file, then check if "I" (flushing pressure) > 0.1
        4. Otherwise, return False

        Codes used:
        Kode 72 (flushing on)
        Kode 73 (flushing off)
        Kode 76 (hammer and flushing on)
        Kode 77 (hammer and flushing off)
        """
        if self._flushing_variant == FlushingVariant.CODE_K:
            if data_row.comment_code in (72, 76) or any(x in (72, 76) for x in self.extract_codes(data_row.remarks)):
                self._current_flushing_active_state = True
            # TODO: check remark for extra codes
            elif data_row.comment_code in (73, 77) or any(x in (73, 77) for x in self.extract_codes(data_row.remarks)):
                self._current_flushing_active_state = False

        elif self._flushing_variant == FlushingVariant.CODE_AR:
            if data_row.flushing is not None:
                self._current_flushing_active_state = data_row.flushing

        elif self._flushing_variant == FlushingVariant.CODE_I:
            if data_row.flushing_pressure is not None:
                if data_row.flushing_pressure > Decimal("0.1"):
                    self._current_flushing_active_state = True
                else:
                    self._current_flushing_active_state = False

        return self._current_flushing_active_state

    def detect_hammering_rule(self) -> HammeringVariant | None:
        """
        Call this with the method data loaded before parsing the hammering in the method data.

        The result of calling this method will set the self._hammering_variant to either use the "K" code if
        any regulating the hammering are present, the "AP" (hammering on/off) code.
        """
        if self._hammering_variant:
            return self._hammering_variant

        if any(
            [
                row.comment_code in (74, 75, 76, 77)
                or any(x in (74, 75, 76, 77) for x in self.extract_codes(row.remarks))
                for row in self.method_data
            ]
        ):
            self._hammering_variant = HammeringVariant.K
        else:
            self._hammering_variant = HammeringVariant.AP

        return self._hammering_variant

    def is_hammer_active(
        self,
        data_row,  #: models.MethodCPTData| models.MethodTOTData| models.MethodRPData| models.MethodSRSData,
    ) -> bool:
        """
        Indicate if hammer is active at given depth.

        The following priority should be used to figure out if the hammer is active:

        1. Check K (kode)
        2. Check "AP" value (0 or 0.0 = off, 1 or 1.0 = on)
        3. Otherwise, return False

        Codes used:
        Kode 74 (hammer on)
        Kode 75 (hammer off)
        Kode 76 (hammer and flushing on)
        Kode 77 (hammer and flushing off)
        """
        if self._hammering_variant == HammeringVariant.K:
            if data_row.comment_code in (74, 76) or any(x in (74, 76) for x in self.extract_codes(data_row.remarks)):
                self._current_hammer_active_state = True
                return self._current_hammer_active_state
            elif data_row.comment_code in (75, 77) or any(x in (75, 77) for x in self.extract_codes(data_row.remarks)):
                self._current_hammer_active_state = False
                return self._current_hammer_active_state

        elif self._hammering_variant == HammeringVariant.AP:
            if data_row.hammering is not None:
                self._current_hammer_active_state = data_row.hammering
                return self._current_hammer_active_state

        return self._current_hammer_active_state

    def detect_increased_rotation_rule(self) -> RotationVariant | None:
        """
        Call this with the method data before updating the increased rotation in the method data.

        The result of calling this method will set the self._increased_rotation_variant to either use the
        "K" code if any regulating the increased rotation are present, the "AQ" (increased rotation on/off) code
        or the "R" (rotation rate) code.
        """

        if self._rotation_variant:
            return self._rotation_variant

        if any(
            [
                row.comment_code in (70, 71) or any(x in (70, 71) for x in self.extract_codes(row.remarks))
                for row in self.method_data
            ]
        ):
            self._rotation_variant = RotationVariant.K
        elif any([row.increased_rotation_rate is not None for row in self.method_data]):
            self._rotation_variant = RotationVariant.AQ
        else:
            self._rotation_variant = RotationVariant.R

        return self._rotation_variant

    def is_increased_rotation_active(
        self,
        data_row,  #: models.MethodCPTData | models.MethodTOTData | models.MethodRPData,
    ) -> bool:
        """
        Indicate if increased rotation speed is active at a given depth.

        The following priority should be used to figure out if increased rotation speed is active:

        1. Check K (kode)
        2. Check "AQ" value (0 or 0.0 = off, 1 or 1.0 = on)
        3. If rotation (R) > 35 rpm set increased rotation
        4. Otherwise, return False

        Codes used:
        Kode 70 (increased rotation speed on)
        Kode 71 (increased rotation speed off)
        """
        if self._rotation_variant == RotationVariant.K:
            if data_row.comment_code == 70:
                self._current_increased_rotation_state = True
            elif data_row.comment_code == 71:
                self._current_increased_rotation_state = False
        elif self._rotation_variant == RotationVariant.AQ:
            if data_row.increased_rotation_rate is not None:
                self._current_increased_rotation_state = data_row.increased_rotation_rate
        else:
            if data_row.rotation_rate is not None:
                if data_row.rotation_rate > 35:
                    self._current_increased_rotation_state = True
                else:
                    self._current_increased_rotation_state = False

        return self._current_increased_rotation_state

    def flushing_update(self):
        """
        Update flushing

        """
        self._flushing_variant = self.detect_flushing_rule()

        for data in self.method_data:
            data.flushing = self.is_flushing_active(data)

    def hammering_update(self):
        """
        Update hammering

        """
        self._hammering_variant = self.detect_hammering_rule()

        for data in self.method_data:
            data.hammering = self.is_hammer_active(data)

    def rotation_update(self):
        """
        Update rotation

        """
        self._rotation_variant = self.detect_increased_rotation_rule()

        for data in self.method_data:
            data.increased_rotation_rate = self.is_increased_rotation_active(data)

    @model_validator(mode="before")
    @classmethod
    def guess_date_format(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "HI" in data and data["HI"] is not None:
                data["HI"] = convert_str_to_time(data["HI"])

            if "KD" in data and data["KD"] is not None and "HD" not in data:
                # If KD is present, but HD is not, set HD since it is the same as KD
                data["HD"] = convert_str_to_datetime(data["KD"])

            elif "HD" in data and data["HD"] is not None:
                data["HD"] = convert_str_to_datetime(data["HD"])

            if "HI" in data and data["HI"] is not None and "HD" in data and data["HD"] is not None:
                data["HD"] = datetime.combine(data["HD"], data["HI"])

        return data

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

    method_type: MethodType
    method_data_type: type[MethodData]

    # name: str | None = None

    location_name: str | None = Field(None, alias="KP")
    project_number: str | None = Field(None, alias="HJ")
    borehole_name: str | None = Field(None, alias="HK", description="Investigation point/Borehole name")
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
    predrilling_depth: Decimal = Field(Decimal("0"), alias="HO")

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
    vane_diameter: Decimal | None = Field(None, alias="IV", description="Diameter of the vane used (mm).")

    method_data: list[MethodData]

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.method_type} method_data={self.method_data!r}>"
