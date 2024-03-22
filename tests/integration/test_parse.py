from datetime import datetime

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
                "tests/data/cpt-test-1.cpt", "windows-1252", 3741, 92, 39.4, 0.844, 
                "4568", datetime(2018, 11, 1),
                {
                    2.000: {"fs": 1.9, "u2": 449.5, "qc": 1.4216, "temperature": 6.3, "tilt": 1.39,
                            "penetration_force": 0.99, "penetration_rate": 0,
                            "zero_value_resistance": 7.5783, "zero_value_friction": 123.3,
                            "zero_value_pressure": 275.1,
                            "comment_code": None, "remarks": None},
                    2.350: {"fs": 53.4, "u2": 599.5, "qc": 2.1572, "temperature": 6.9, "tilt": 1.10,
                            "penetration_force": 20.16, "penetration_rate": 21,
                            "zero_value_resistance": None, "zero_value_friction": None,
                            "zero_value_pressure": None},
                    39.40: {"fs": 53.1, "u2": 882.1, "qc": 26.32, "temperature": 6.2, "tilt": 10.19,
                            "penetration_force": 29.59, "penetration_rate": 13, "comment_code": 92,
                            "zero_value_resistance": 0.0262, "zero_value_friction": -0.5,
                            "zero_value_pressure": -1.6,
                            "remarks": "Stop against a stone or a stone block."},
                },
            ),
            (
                "tests/data/cpt-test-2.cpt", "windows-1252", 1468, 91, 18.48, None,
                "5939319", datetime(2019, 5, 9, 10, 33),
                {
                    3.81: {"fs": 0.93, "u2": 132.4, "qc": 0.081, "temperature": 6.2, "tilt": 9.9,
                           "penetration_force": 0.0, "penetration_rate": 0.9,
                           "zero_value_resistance": 25.782, "zero_value_friction": 1727.7,
                           "zero_value_pressure": 1321.0
                           },
                    # D=18.09,B=18.8,A=11.6,U=537.29,Q=1.193,F=11.25,TA=10.3,O=8.0
                    18.09: {"fs": 11.25, "u2": 537.29, "qc": 1.193, "temperature": 8.0, "tilt": 10.3,
                            "penetration_force": 11.6, "penetration_rate": 18.8},
                    18.48: {"fs": 49.05, "u2": 216.8, "qc": 17.984, "temperature": 8, "tilt": 9.3,
                            "penetration_force": 33.6, "penetration_rate": 21.9,
                            "zero_value_resistance": -0.1, "zero_value_friction": 0.099,
                            "zero_value_pressure": -0.599,
                            "comment_code": 91, "remarks": None},
                },
            ),
            (
                "tests/data/cpt-test-3.cpt", "utf-8", 1200, 90, 24.98, 0.844,
                # datetime(2019, 5, 9, 11, 5),  # <- Correct
                "5349", datetime(2019, 9, 5, 11, 5),  # <-Wrong
                {}
            ),
            (
                "tests/data/cpt-test-4.cpt", "utf-8", 1370, 91, 15.427, None,
                "TEST", datetime(2012, 1, 5, 11, 30), 
                {
                    1.684: {'fs': 0, "u2": 0}
                }
            ),

            (
                "tests/data/cpt-test-with-method-block.cpt", "utf-8", 1592, 91, 33.82, 0.846,
                "4763", datetime(2021, 6, 30, 11, 39),
                {
                    2.00: {"fs": 12.66, "u2": 398.33, "qc": 0.553, "temperature": 25.24, "tilt": 1.16,
                           "penetration_force": 1.19, "penetration_rate": 0,
                           "zero_value_resistance": 5.8130, "zero_value_friction": 129.9,
                           "zero_value_pressure": 266.9},
                    2.22: {"fs": 47.34, "u2": 568.66, "qc": 0.873, "temperature": 11.51, "tilt": 1.83,
                           "penetration_force": 3.25, "penetration_rate": 20},
                    # D=33.720,QC=1.951,FS=10.83,U=1493.57,TA=1.96,B=15,O=5.78,A=25.14,M=0.00000,DatumTid=20210630124100115
                    33.720: {"fs": 10.83, "u2": 1493.57, "qc": 1.951, "temperature": 5.78, "tilt": 1.96,
                             "penetration_force": 25.14, "penetration_rate": 15},
                },
            ),
            (
                "tests/data/cpt-test-multi-line-header.cpt", "windows-1252",  2120, 90, 42.38, 0.861,
                "4354", datetime(2014, 6, 27),
                {}
            ),
            (
                "tests/data/cpt-test-two-lines-header.cpt", "windows-1252", 45, 90, 35.200, 0.833,
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
                "tests/data/tot-test-multiple-codes.tot", 33, 90, 45.04, None, None,
                datetime(2024, 2, 1, 9, 58),
                {
                    1.69: {"comment_code": 73, "remarks": "75, Slag slutter, Spyling slutter"},
                    7.58: {"comment_code": 72, "remarks": "Spyling begynner"},
                    7.59: {"comment_code": None, "remarks": None},
                    45.04: {
                        "comment_code": 90,
                        "remarks": "73, 75, Spyling slutter, Slag slutter, Sondering avsluten uten å ha oppnådd stopp",
                    },
                },
            ),
            (
                "tests/data/tot-test-1.tot", 365, 94, 6.125, 3, point_z - 6.125,
                datetime(2018, 6, 20, 12, 1, 15),
                {
                    0.775: {"comment_code": None, "remarks": None},
                    6.125: {"comment_code": 41, "remarks": "stein"},
                    9.125: {"comment_code": 94, "remarks": "Stopp mot antatt berg"},
                },
            ),
            (
                "tests/data/tot-test-2.tot", 520, 94, 10.15, 2.85, point_z - 10.15,
                datetime(2019, 10, 28, 10, 5, 24),
                {
                    0.775: {"comment_code": None, "remarks": None},
                    1.325: {"comment_code": 41, "remarks": "Bl Genomborrat block eller sten"},
                    10.15: {"comment_code": 41, "remarks": "Bl Genomborrat block eller sten"},
                    13: {"comment_code": 94, "remarks": "Stopp mot antatt berg"},
                },
            ),
            (
                "tests/data/tot-test-3.tot", 2313, 90, 57.825, None, None,
                datetime(2014, 9, 18, 7, 49, 11),
                {
                    0.775: {"comment_code": None, "remarks": None},
                    6.125: {"comment_code": None, "remarks": None},
                    57.825: {"comment_code": 90,
                             "remarks": "Sondering avbruten utan stopp, Avsl. på 57,8m i antatt fast leire."},
                },
            ),
            (
                "tests/data/tot-test-4.tot", 224, 93, 5.6, None, point_z - 5.6,
                datetime(2012, 10, 8, 10, 45, 17),
                {
                    1.6: {"comment_code": None, "remarks": None},
                    5.6: {"comment_code": 93, "remarks": " Sten"},
                },
            ),
            (
                "tests/data/tot-test-5.tot", 3350, 90, 83.75, None, None,
                datetime(2023, 1, 3, 9, 20, 38),
                {
                    25.750: {"comment_code": 42, "remarks": "Ej merkbara sprickor +"},
                    51.325: {"comment_code": 41, "remarks": "Bl Genomborrat block eller sten"},
                    83.750: {"comment_code": 90, "remarks": "Avbruten utan stopp"},
                },
            ),
            (
                "tests/data/tot-test-6.tot", 745, 94, 4.47, 2.98, point_z - 4.47,
                datetime(2020, 9, 10, 12, 39),
                {
                    4.47: {"comment_code": 41, "remarks": None},
                    7.45: {"comment_code": 94, "remarks": None},
                },
            ),
            (
                "tests/data/tot-test-7.tot", 2724, 90, 68.1, None, None,
                datetime(2012, 10, 30, 13, 1, 6),
                {
                    # 4.47: {"comment_code": 41, "remarks": None},
                    68.1: {"comment_code": 90, "remarks": "Sondering avbruten utan stopp"},
                },
            ),
            (
                "tests/data/tot-test-data-ending-with-comma.tot", 1, None, 10.5, None, None,
                datetime(2021, 3, 23, 1, 39, 38),
                {
                    
                    10.5: {"comment_code": None, "remarks": None},
                },
            ),
            (
                "tests/data/tot-malformed-code.tot", 1481, 94, 34.025, 3, point_z - 34.025,
                datetime(2021, 9, 21, 15, 9, 34),
                {

                    37.025: {"comment_code": 94, "remarks": "Stopp mot förmodat berg"},
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
