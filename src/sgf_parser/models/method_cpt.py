from decimal import Decimal
from typing import Literal

from pydantic import Field, AliasChoices

from sgf_parser.models import MethodType, MethodData, Method
from sgf_parser.models.types import ApplicationClass


class MethodCPTData(MethodData):
    """
    Method CPT data
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    penetration_force: Decimal | None = Field(None, alias="A", description="Penetration force (kN)")
    penetration_rate: Decimal | None = Field(None, alias="B", description="Penetration rate (mm/s)")
    depth: Decimal = Field(..., alias="D", description="Depth (m)")

    # "F":  Envi format (non-standard)
    # "FS": SGF Standard and Geotech format
    fs: Decimal | None = Field(None, description="Friction (kPa)", validation_alias=AliasChoices("FS", "F"))

    # "M": "conductivity",  # "conductivity",
    conductivity: Decimal | None = Field(None, alias="M", description="Conductivity (S/m)")

    zero_value_resistance: Decimal | None = Field(
        None, description="Zero value resistance (MPa)", validation_alias=AliasChoices("NA", "NA2", "NA3")
    )
    zero_value_friction: Decimal | None = Field(
        None, description="Zero value friction (kPa)", validation_alias=AliasChoices("NB", "NB2", "NB3")
    )
    zero_value_pressure: Decimal | None = Field(
        None, description="Zero value pressure (kPa)", validation_alias=AliasChoices("NC", "NC2", "NC3")
    )

    temperature: Decimal | None = Field(None, alias="O", description="Temperature (degree C)")
    qc: Decimal | None = Field(None, description="Resistance (MPa)", validation_alias=AliasChoices("QC", "Q"))
    tilt: Decimal | None = Field(None, alias="TA", description="Inclination (degree)")

    u2: Decimal | None = Field(None, alias="U", description="Shoulder pressure (kPa)")


class MethodCPT(Method):
    """
    Method CPT
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    name: str = "CPT"
    method_type: Literal[MethodType.CPT] = MethodType.CPT
    method_data_type: type[MethodCPTData] = MethodCPTData

    method_data: list[MethodCPTData] = []

    application_class_depth: ApplicationClass = ApplicationClass.UNKNOWN
    application_class_resistance: ApplicationClass = ApplicationClass.UNKNOWN
    application_class_friction: ApplicationClass = ApplicationClass.UNKNOWN
    application_class_pressure: ApplicationClass = ApplicationClass.UNKNOWN

    def _patch_zero_values_from_header_text(self: "MethodCPT"):
        """
        Patch zero values on first data row, if present in the header field HT (remarks)
        """
        if not self.remarks:
            return

        remarks = self.remarks.split(" ")
        if len(remarks) != 6:
            return

        # NB: The values in the header are all in kPa, but we store NA in MPa.
        # The diff at the end are OK (NA MPa, NB kPa, NC kPa).
        # It is correct that the order is not A, B, C, ...:
        NC_str, NA_str, NB_str, _, _, _ = remarks

        try:
            NA: Decimal = Decimal(NA_str)
            NB: Decimal = Decimal(NB_str)
            NC: Decimal = Decimal(NC_str)
        except ValueError:
            return

        if self.method_data[0].zero_value_resistance:
            return

        if self.method_data[0].zero_value_friction:
            return

        if self.method_data[0].zero_value_pressure:
            return

        # self.method_data[0].zero_value_resistance = (NA * unit.kPa).to(unit.MPa).magnitude
        self.method_data[0].zero_value_resistance = NA * Decimal("0.001")
        self.method_data[0].zero_value_friction = NB
        self.method_data[0].zero_value_pressure = NC

    def _get_data_field_max_value(self, field: str) -> Decimal:
        """
        Return the max value for specified method data row field
        """
        return max([getattr(row, field) if getattr(row, field) else Decimal("0") for row in self.method_data])

    def _get_depth_delta(self) -> Decimal | None:
        """
        Return the delta dept between the two first method data rows.
        If no data rows, then return None
        """
        if not self.method_data or len(self.method_data) < 2:
            return None

        return self.method_data[1].depth - self.method_data[0].depth

    def _get_depth_class(self) -> ApplicationClass:
        """
        Return the method's application class depending on the delta depth (not looking at any other factors)

        Artificial Application Class 5 for returning error

        +---------------------------|-- Class 1 ---|- Class 2 -----|-- Class 3 ----|-- Class 4 ----+
        | delta Depth (delta D)  <= | 20 mm        | 20 mm         | 50mm          | 50mm          |

        """
        delta_depth = self._get_depth_delta()
        if not delta_depth:
            return ApplicationClass.UNKNOWN

        if delta_depth <= 0.02:
            return ApplicationClass.ONE
        elif delta_depth <= 0.05:
            return ApplicationClass.THREE

        return ApplicationClass.OUT_OF_BOUNDS

    def _get_zero_value_class(
        self, field: str, pressure_class_map: list[tuple[Decimal, ApplicationClass]]
    ) -> ApplicationClass:
        """
        Return the application class based on the absolute zero value from the last row of data form the pressure_class_map.

        If value out of range, then return OUT_OF_BOUNDS (5) as a marker for error/not defined state
        """
        if not self.method_data or len(self.method_data) < 2:
            return ApplicationClass.UNKNOWN

        value_last = getattr(self.method_data[-1], field)

        if value_last is None:
            return ApplicationClass.UNKNOWN

        diff = abs(value_last)

        for pressure, class_number in pressure_class_map:
            if diff <= pressure:
                return class_number

        return ApplicationClass.OUT_OF_BOUNDS

    def _calculate_application_class(
        self,
    ) -> tuple[ApplicationClass, ApplicationClass, ApplicationClass, ApplicationClass]:
        """
        Calculates the method's application class (also called quality class)

        +-----------------------------------------------|-- Class 1 ---|- Class 2 -----|-- Class 3 ----|-- Class 4 ----+
        | delta Depth (delta D)                      <= | 20 mm        | 20 mm         | 50mm          | 50mm          |
        | NA = delta QC [MPa] - Zero value resistance<= | 35 kPa or 5% | 100 kPa or 5% | 200 kPa or 5% | 500 kPa or 5% |
        | NB = delta fs [kPa] - Zero value friction  <= | 5 kPa or 10% | 15 kPa or 15% | 25 kPa or 15% | 50 kPa or 20% |
        | NC = delta u2 [kPa] - Zero value pressure  <= | 10 kPa or 2% | 25 kPa or 3%  | 50 kPa or 5%  |               |
        +--------------------------------------------------------------------------------------------------------------+
        """
        depth_class: ApplicationClass = self._get_depth_class()

        qc_max_data_value = self._get_data_field_max_value(field="qc")  # MPa
        # convert to kPa
        # qc_max_data_value = (qc_max_data_value * unit.MPa).to(unit.kPa).magnitude
        qc_max_data_value = qc_max_data_value * Decimal("1000")

        NA_class = self._get_zero_value_class(
            field="zero_value_resistance",
            pressure_class_map=[
                (max(Decimal("35"), qc_max_data_value * Decimal("0.05")) / Decimal("1000"), ApplicationClass.ONE),
                (max(Decimal("100"), qc_max_data_value * Decimal("0.05")) / Decimal("1000"), ApplicationClass.TWO),
                (max(Decimal("200"), qc_max_data_value * Decimal("0.05")) / Decimal("1000"), ApplicationClass.THREE),
                (max(Decimal("500"), qc_max_data_value * Decimal("0.05")) / Decimal("1000"), ApplicationClass.FOUR),
            ],
        )

        fs_max_data_value = self._get_data_field_max_value(field="fs")  # kPa
        NB_class = self._get_zero_value_class(
            field="zero_value_friction",
            pressure_class_map=[
                (max(Decimal("5"), fs_max_data_value * Decimal("0.1")), ApplicationClass.ONE),
                (max(Decimal("15"), fs_max_data_value * Decimal("0.15")), ApplicationClass.TWO),
                (max(Decimal("25"), fs_max_data_value * Decimal("0.15")), ApplicationClass.THREE),
                (max(Decimal("50"), fs_max_data_value * Decimal("0.2")), ApplicationClass.FOUR),
            ],
        )

        u2_max_data_value = self._get_data_field_max_value(field="u2")  # kPa
        NC_class = self._get_zero_value_class(
            field="zero_value_pressure",
            pressure_class_map=[
                (max(Decimal("10"), u2_max_data_value * Decimal("0.02")), ApplicationClass.ONE),
                (max(Decimal("25"), u2_max_data_value * Decimal("0.03")), ApplicationClass.TWO),
                (max(Decimal("50"), u2_max_data_value * Decimal("0.05")), ApplicationClass.THREE),
            ],
        )

        return depth_class, NA_class, NB_class, NC_class

    def post_processing(self):
        """
        Post-processing

        """

        if not self.method_data:
            return

        self._patch_zero_values_from_header_text()

        (
            self.application_class_depth,
            self.application_class_resistance,
            self.application_class_friction,
            self.application_class_pressure,
        ) = self._calculate_application_class()

    @property
    def application_class(self) -> ApplicationClass:
        """
        Return the application class based on the method's application class
        """
        if (
            self.application_class_depth
            and self.application_class_resistance
            and self.application_class_friction
            and self.application_class_pressure
        ):
            return max(
                self.application_class_depth,
                self.application_class_resistance,
                self.application_class_friction,
                self.application_class_pressure,
            )
        else:
            return ApplicationClass.UNKNOWN

    # "MA": "cone_area_ratio",  # same as header code IE
    # "IE": "cone_area_ratio",  # same as header code MA
    # "MB": "sleeve_area_ratio",  # same as header code IF
    # "IF": "sleeve_area_ratio",  # same as header code MB
