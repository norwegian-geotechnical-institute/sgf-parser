from io import StringIO

import pytest

from sgf_parser import Parser
from sgf_parser.models.types import ApplicationClass


def build_test_string(
    delta_depth: float,
    NA: float,
    NB: float,
    NC: float,
    NA_percent: float,
    NB_percent: float,
    NC_percent: float,
) -> str:
    """Generate a CPT std test file with passed values"""

    # Header
    test_string = (
        "$\r\n"
        "HA=1,HB=295,HC=TEST,HD=20190509,HI=1033,HM=7,HJ=TEST,HK=12,HO=3.8,HN=51819,HT=1321.0 25782.0 1727.7 1320.4 25682.0 1727.8,HQ=Jost\r\n"
        "#\r\n"
    )
    # The maximum values should be X % of the zero values. Add a 0.001 due to rounding happening in the string generation
    q = NA * 100.0 / NA_percent + 0.001  # MPa
    f = NB * 100.0 / NB_percent + 0.001  # kPa
    u = NC * 100.0 / NC_percent + 0.001  # kPa
    test_string += (
        f"D={delta_depth:0.2f},B=0.9,A=0.0,U={u},Q={q},F={f},O=6.2,NA={NA*2:0.3f},NB={NB*2:0.3f},NC={NC*2:0.3f}\r\n"
    )
    test_string += f"D={2 * delta_depth:0.2f},B=0.9,A=0.0,U={u},Q={q},F={f},O=6.2\r\n"
    test_string += f"D={3 * delta_depth:0.2f},B=0.9,A=0.0,U={u},Q={q},F={f},O=6.2\r\n"
    test_string += (
        f"D={4 * delta_depth:0.2f},B=0.9,A=0.0,U={u},Q={q},F={f},O=6.2,NA={NA:0.3f},NB={NB:0.3f},NC={NC:0.3f}\r\n"
    )

    return test_string


class TestCPTApplicationClass:
    @pytest.mark.parametrize(
        "delta_depth",
        [(0.02, ApplicationClass.ONE), (0.05, ApplicationClass.THREE), (0.06, ApplicationClass.OUT_OF_BOUNDS)],
    )
    @pytest.mark.parametrize(
        "NA",
        [
            (0.035, ApplicationClass.ONE),
            # (0.100, ApplicationClass.TWO),
            # (0.200, ApplicationClass.THREE),
            (0.500, ApplicationClass.FOUR),
            (0.501, ApplicationClass.OUT_OF_BOUNDS),
        ],
    )  # NA is in MPa (other in kPa)
    @pytest.mark.parametrize(
        "NB",
        [
            (5, ApplicationClass.ONE),
            # (15, ApplicationClass.TWO),
            # (25, ApplicationClass.THREE),
            # (50, ApplicationClass.FOUR),
            # (50.1, ApplicationClass.OUT_OF_BOUNDS),
        ],
    )
    @pytest.mark.parametrize(
        "NC",
        [
            (10, ApplicationClass.ONE),
            # (25, ApplicationClass.TWO),
            # (50, ApplicationClass.THREE),
            # (50.1, ApplicationClass.OUT_OF_BOUNDS),
        ],
    )
    @pytest.mark.parametrize("NA_percent", [(5, ApplicationClass.ONE), (5.1, ApplicationClass.OUT_OF_BOUNDS)])
    @pytest.mark.parametrize(
        "NB_percent",
        [
            (10, ApplicationClass.ONE),
            (15, ApplicationClass.TWO),
            (20, ApplicationClass.FOUR),
            # (20.1, ApplicationClass.OUT_OF_BOUNDS),
        ],
    )
    @pytest.mark.parametrize(
        "NC_percent",
        [
            (2, ApplicationClass.ONE),
            (3, ApplicationClass.TWO),
            (5, ApplicationClass.THREE),
            # (5.1, ApplicationClass.OUT_OF_BOUNDS),
        ],
    )
    def test_quality_class(
        self,
        delta_depth,
        NA,
        NB,
        NC,
        NA_percent,
        NB_percent,
        NC_percent,
    ):
        """
        Test calculation of CPT quality class

        +-----------------------------------------------|-- Class 1 ---|- Class 2 -----|-- Class 3 ----|-- Class 4 ----+
        | delta Depth (delta D)                      <= | 20 mm        | 20 mm         | 50mm          | 50mm          |
        | NA = delta QC [MPa] - Nollvärde spetstryck <= | 35 kPa or 5% | 100 kPa or 5% | 200 kPa or 5% | 500 kPa or 5% |
        | NB = delta fs [kPa] - Nollvärde friktion   <= | 5 kPa or 10% | 15 kPa or 15% | 25 kPa or 15% | 50 kPa or 20% |
        | NC = delta u2 [kPa] - Nollvärde portryck   <= | 10 kPa or 2% | 25 kPa or 3%  | 50 kPa or 5%  |               |
        +--------------------------------------------------------------------------------------------------------------+

        Test variants:
        Build test file from all combinations of testdata (by the parameterized values)
        Then check that the result class is equal to the expected class (the worst of all
        """
        # All parameters are tuples of (value, expected result class). Use special quality class of 5 that mean
        # None (no class). This makes it easy to use the min() function on the result
        value_index = 0
        class_index = 1

        test_string = build_test_string(
            delta_depth[value_index],
            NA[value_index],
            NB[value_index],
            NC[value_index],
            NA_percent[value_index],
            NB_percent[value_index],
            NC_percent[value_index],
        )

        expected_application_class = max(
            delta_depth[class_index],
            min(NA[class_index], NA_percent[class_index]),
            min(NB[class_index], NB_percent[class_index]),
            min(NC[class_index], NC_percent[class_index]),
        )

        with StringIO(test_string) as file:
            [method] = Parser().parse(file)

        assert method.application_class == expected_application_class
