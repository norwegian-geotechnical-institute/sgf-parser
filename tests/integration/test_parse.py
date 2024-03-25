from datetime import datetime
from decimal import Decimal

import pytest

from sgf_parser import Parser, models

point_z = 40.5


class TestParse:
    # fmt: off
    @pytest.mark.parametrize(
        "file_name, encoding, number_of_data_rows, stop_code, depth_base, cone_area_ratio, "
        "cone_reference, conducted_at, data_rows",
        (
            (  # Geotech format
                "tests/data/cpt-test-1.cpt", "windows-1252", 3741, 92, Decimal("39.4"), Decimal("0.844"), 
                "4568", datetime(2018, 11, 1),
                {
                    Decimal("2"): {"fs": Decimal("1.9"), "u2": Decimal("449.5"), "qc": Decimal("1.4216"), "temperature": Decimal("6.3"), "tilt": Decimal("1.39"),
                            "penetration_force": Decimal("0.99"), "penetration_rate": Decimal("0"),
                            "zero_value_resistance": Decimal("7.5783"), "zero_value_friction": Decimal("123.3"),
                            "zero_value_pressure": Decimal("275.1"),
                            "comment_code": None, "remarks": None},
                    Decimal("2.350"): {"fs": Decimal("53.4"), "u2": Decimal("599.5"), "qc": Decimal("2.1572"), "temperature": Decimal("6.9"), "tilt": Decimal("1.10"),
                            "penetration_force": Decimal("20.16"), "penetration_rate": Decimal("21"),
                            "zero_value_resistance": None, "zero_value_friction": None,
                            "zero_value_pressure": None},
                    Decimal("39.40"): {"fs": Decimal("53.1"), "u2": Decimal("882.1"), "qc": Decimal("26.32"), "temperature": Decimal("6.2"), "tilt": Decimal("10.19"),
                            "penetration_force": Decimal("29.59"), "penetration_rate": Decimal("13"), "comment_code": 92,
                            "zero_value_resistance": Decimal("0.0262"), "zero_value_friction": Decimal("-0.5"),
                            "zero_value_pressure": Decimal("-1.6"),
                            "remarks": "Stop against a stone or a stone block."},
                },
            ),
            (
                "tests/data/cpt-test-2.cpt", "windows-1252", 1468, 91, Decimal("18.48"), None,
                "5939319", datetime(2019, 5, 9, 10, 33),
                {
                    Decimal("3.81"): {"fs": Decimal("0.93"), "u2": Decimal("132.4"), "qc": Decimal("0.081"), "temperature": Decimal("6.2"), "tilt": Decimal("9.9"),
                           "penetration_force": Decimal("0.0"), "penetration_rate": Decimal("0.9"),
                           "zero_value_resistance": Decimal("25.782"), "zero_value_friction": Decimal("1727.7"),
                           "zero_value_pressure": Decimal("1321.0")
                           },
                    # D=18.09,B=18.8,A=11.6,U=537.29,Q=1.193,F=11.25,TA=10.3,O=8.0
                    Decimal("18.09"): {"fs": Decimal("11.25"), "u2": Decimal("537.29"), "qc": Decimal("1.193"), "temperature": Decimal("8.0"), "tilt": Decimal("10.3"),
                            "penetration_force": Decimal("11.6"), "penetration_rate": Decimal("18.8")},
                    Decimal("18.48"): {"fs": Decimal("49.05"), "u2": Decimal("216.8"), "qc": Decimal("17.984"), "temperature": Decimal("8"), "tilt": Decimal("9.3"),
                            "penetration_force": Decimal("33.6"), "penetration_rate": Decimal("21.9"),
                            "zero_value_resistance": Decimal("-0.1"), "zero_value_friction": Decimal("0.099"),
                            "zero_value_pressure": Decimal("-0.599"),
                            "comment_code": 91, "remarks": None},
                },
            ),
            (
                "tests/data/cpt-test-3.cpt", "utf-8", 1200, 90, Decimal("24.98"), Decimal("0.844"),
                # datetime(2019, 5, 9, 11, 5),  # <- Correct
                "5349", datetime(2019, 9, 5, 11, 5),  # <-Wrong
                {}
            ),
            (
                "tests/data/cpt-test-4.cpt", "utf-8", 1370, 91, Decimal("15.427"), None,
                "TEST", datetime(2012, 1, 5, 11, 30), 
                {
                    Decimal("1.684"): {'fs': Decimal("0"), "u2": Decimal("0")}
                }
            ),

            (
                "tests/data/cpt-test-with-method-block.cpt", "utf-8", 1592, 91, Decimal("33.82"), Decimal("0.846"),
                "4763", datetime(2021, 6, 30, 11, 39),
                {
                    Decimal("2"): {"fs": Decimal("12.66"), "u2": Decimal("398.33"), "qc": Decimal("0.553"), "temperature": Decimal("25.24"), "tilt": Decimal("1.16"),
                           "penetration_force": Decimal("1.19"), "penetration_rate": Decimal("0"),
                           "zero_value_resistance": Decimal("5.8130"), "zero_value_friction": Decimal("129.9"),
                           "zero_value_pressure": Decimal("266.9")},
                    Decimal("2.22"): {"fs": Decimal("47.34"), "u2": Decimal("568.66"), "qc": Decimal("0.873"), "temperature": Decimal("11.51"), "tilt": Decimal("1.83"),
                           "penetration_force": Decimal("3.25"), "penetration_rate": Decimal("20")},
                    # D=33.720,QC=1.951,FS=10.83,U=1493.57,TA=1.96,B=15,O=5.78,A=25.14,M=0.00000,DatumTid=20210630124100115
                    Decimal("33.720"): {"fs": Decimal("10.83"), "u2": Decimal("1493.57"), "qc": Decimal("1.951"), "temperature": Decimal("5.78"), "tilt": Decimal("1.96"),
                             "penetration_force": Decimal("25.14"), "penetration_rate": Decimal("15")},
                },
            ),
            (
                "tests/data/cpt-test-multi-line-header.cpt", "windows-1252",  2120, 90, Decimal("42.38"), Decimal("0.861"),
                "4354", datetime(2014, 6, 27),
                {}
            ),
            (
                "tests/data/cpt-test-two-lines-header.cpt", "windows-1252", 45, 90, Decimal("35.200"), Decimal("0.833"),
                "2244", datetime(2022, 1, 5),
                {}
            ),
        ),
    )
    # fmt: on
    def test_parse_cpt(
            self, file_name, encoding, number_of_data_rows, stop_code, depth_base, cone_area_ratio,
            cone_reference, conducted_at, data_rows
    ):
        with open(file_name, "r", encoding=encoding) as file:
            [method] = Parser().parse(file)

        method.point_z = point_z

        assert method.method_type == models.MethodType.CPT
        assert len(method.method_data) == number_of_data_rows
        assert method.stopcode == stop_code
        assert method.conducted_at == conducted_at
        assert method.depth_base == pytest.approx(depth_base)
        assert method.cone_area_ratio == pytest.approx(cone_area_ratio)
        assert method.cone_reference == cone_reference
        
        for row in method.method_data:
            if row.depth in data_rows:
                for key in data_rows[row.depth]:
                    assert getattr(row, key) == pytest.approx(data_rows[row.depth][key]), f"At depth={row.depth} did not expect {key!r} {getattr(row, key)} != {data_rows[row.depth][key]}"

    # fmt: off
    @pytest.mark.parametrize(
        "file_name, number_of_data_rows, stop_code, depth_in_soil, depth_in_rock, bedrock_elevation, conducted_at, data_rows",
        (
            (
                "tests/data/tot-test-multiple-codes.tot", 33, 90, Decimal("45.04"), None, None,
                datetime(2024, 2, 1, 9, 58),
                {
                    Decimal("1.69"): {"comment_code": 73, "remarks": "75, Slag slutter, Spyling slutter"},
                    Decimal("7.58"): {"comment_code": 72, "remarks": "Spyling begynner"},
                    Decimal("7.59"): {"comment_code": None, "remarks": None},
                    Decimal("45.04"): {
                        "comment_code": 90,
                        "remarks": "73, 75, Spyling slutter, Slag slutter, Sondering avsluten uten å ha oppnådd stopp",
                    },
                },
            ),
            (
                "tests/data/tot-test-1.tot", 365, 94, Decimal("6.125"), Decimal("3"), Decimal(point_z - 6.125),
                datetime(2018, 6, 20, 12, 1, 15),
                {
                    Decimal("0.775"): {"comment_code": None, "remarks": None},
                    Decimal("6.125"): {"comment_code": 41, "remarks": "stein"},
                    Decimal("9.125"): {"comment_code": 94, "remarks": "Stopp mot antatt berg"},
                },
            ),
            (
                "tests/data/tot-test-2.tot", 520, 94, Decimal("10.15"), Decimal("2.85"), Decimal(point_z - 10.15),
                datetime(2019, 10, 28, 10, 5, 24),
                {
                    Decimal("0.775"): {"comment_code": None, "remarks": None},
                    Decimal("1.325"): {"comment_code": 41, "remarks": "Bl Genomborrat block eller sten"},
                    Decimal("10.15"): {"comment_code": 41, "remarks": "Bl Genomborrat block eller sten"},
                    Decimal("13"): {"comment_code": 94, "remarks": "Stopp mot antatt berg"},
                },
            ),
            (
                "tests/data/tot-test-3.tot", 2313, 90, Decimal("57.825"), None, None,
                datetime(2014, 9, 18, 7, 49, 11),
                {
                    Decimal("0.775"): {"comment_code": None, "remarks": None},
                    Decimal("6.125"): {"comment_code": None, "remarks": None},
                    Decimal("57.825"): {"comment_code": 90,
                             "remarks": "Sondering avbruten utan stopp, Avsl. på 57,8m i antatt fast leire."},
                },
            ),
            (
                "tests/data/tot-test-4.tot", 224, 93, Decimal("5.6"), None, Decimal(point_z - 5.6),
                datetime(2012, 10, 8, 10, 45, 17),
                {
                    Decimal("1.6"): {"comment_code": None, "remarks": None},
                    Decimal("5.6"): {"comment_code": 93, "remarks": " Sten"},
                },
            ),
            (
                "tests/data/tot-test-5.tot", 3350, 90, Decimal("83.75"), None, None,
                datetime(2023, 1, 3, 9, 20, 38),
                {
                    Decimal("25.750"): {"comment_code": 42, "remarks": "Ej merkbara sprickor +"},
                    Decimal("51.325"): {"comment_code": 41, "remarks": "Bl Genomborrat block eller sten"},
                    Decimal("83.750"): {"comment_code": 90, "remarks": "Avbruten utan stopp"},
                },
            ),
            (
                "tests/data/tot-test-6.tot", 745, 94, Decimal("4.47"), Decimal("2.98"), Decimal(point_z - 4.47),
                datetime(2020, 9, 10, 12, 39),
                {
                    Decimal("4.47"): {"comment_code": 41, "remarks": None},
                    Decimal("7.45"): {"comment_code": 94, "remarks": None},
                },
            ),
            (
                "tests/data/tot-test-7.tot", 2724, 90, Decimal("68.1"), None, None,
                datetime(2012, 10, 30, 13, 1, 6),
                {
                    # 4.47: {"comment_code": 41, "remarks": None},
                    Decimal("68.1"): {"comment_code": 90, "remarks": "Sondering avbruten utan stopp"},
                },
            ),
            (
                "tests/data/tot-test-data-ending-with-comma.tot", 1, None, Decimal("10.5"), None, None,
                datetime(2021, 3, 23, 1, 39, 38),
                {
                    
                    Decimal("10.5"): {"comment_code": None, "remarks": None},
                },
            ),
            (
                "tests/data/tot-malformed-code.tot", 1481, 94, Decimal("34.025"), 3, Decimal(point_z - 34.025),
                datetime(2021, 9, 21, 15, 9, 34),
                {

                    Decimal("37.025"): {"comment_code": 94, "remarks": "Stopp mot förmodat berg"},
                },
            ),

        ),
    )
    # fmt: on
    def test_parse_tot(
            self, file_name, number_of_data_rows, stop_code, depth_in_soil, depth_in_rock,
            bedrock_elevation, conducted_at, data_rows
    ):
        with open(file_name, "r", encoding="utf-8") as file:
            [method] = Parser().parse(file)

        method.point_z = point_z

        assert method.method_type == models.MethodType.TOT
        assert len(method.method_data) == number_of_data_rows
        assert stop_code == method.stopcode
        assert method.depth_in_soil == pytest.approx(depth_in_soil)
        assert method.depth_in_rock == pytest.approx(depth_in_rock)
        assert method.bedrock_elevation == pytest.approx(bedrock_elevation)
        assert method.conducted_at == conducted_at

        for row in method.method_data:
            if row.depth in data_rows:
                for key in data_rows[row.depth]:
                    assert getattr(row, key) == pytest.approx(
                        data_rows[row.depth][key]), f"{key} {getattr(row, key)} != {data_rows[row.depth][key]}"
