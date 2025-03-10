from datetime import datetime
from decimal import Decimal

import pytest

from sgf_parser import Parser, models
from sgf_parser.models.types import SoundingClass

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
                    Decimal("0.01"): {"comment_code": 74, "remarks": "Slag starter", "hammering": True, "flushing": False},
                    Decimal("0.02"): {"comment_code": None, "remarks": None, "hammering": True, "flushing": False},
                    Decimal("1.33"): {"comment_code": 72, "hammering": True, "flushing": True},
                    Decimal("1.69"): {"comment_code": 73, "remarks": "75, Slag slutter, Spyling slutter", "hammering": False, "flushing": False},
                    Decimal("1.70"): {"comment_code": None, "hammering": False, "flushing": False},
                    Decimal("7.58"): {"comment_code": 72, "remarks": "Spyling begynner",  "hammering": False, "flushing": True},
                    Decimal("7.59"): {"comment_code": None, "remarks": None,  "hammering": False, "flushing": True},
                    Decimal("7.90"): {"comment_code": None, "remarks": None,  "hammering": False, "flushing": True},
                    Decimal("7.91"): {"comment_code": 74, "remarks": "Slag starter", "hammering": True, "flushing": True},
                    Decimal("45.03"): {"comment_code": None, "remarks": None, "hammering": True, "flushing": True},
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

    # fmt: off
    @pytest.mark.parametrize(
        "file_name, number_of_data_rows, stop_code, depth_top, depth_base, conducted_at, data_rows",
        (
(
    "tests/data/rp-test-1.std", 565, 90, Decimal("1.725"), Decimal("15.825"),
    datetime(2021, 1, 27, 14, 23, 23),
    {
        Decimal("1.725"): {"comment_code": None, "remarks": None, "flushing": False, "increased_rotation_rate": False, "penetration_rate": Decimal('24'), "torque": Decimal('0.495'), "rotation_rate": Decimal('0')},
        Decimal("13.950"): {"comment_code": None, "remarks": None, "flushing": False, "increased_rotation_rate": False, "penetration_rate": Decimal('52.5'), "torque": Decimal('0.153'), "rotation_rate": Decimal('27')},
        Decimal("15.825"): {"comment_code": 90,  "remarks": "Avbruten utan stopp", "penetration_rate": Decimal('0')},
    },
),
(
    "tests/data/rp-test-2.std", 1483, 95, Decimal("0.01"), Decimal("14.83"), 
    datetime(2018, 12, 7, 10, 20),
    {
        Decimal("0.01"): {"comment_code": 1, "remarks": None, "flushing": False, "increased_rotation_rate": False, "penetration_rate": Decimal('0.42'), "rotation_rate": Decimal('28')},
        Decimal("14.76"): {"comment_code": None, "remarks": None, "increased_rotation_rate": False, "penetration_rate": Decimal('64.03'), "rotation_rate": Decimal('81'), "penetration_force": Decimal("28.53")},
        Decimal("14.83"): {"comment_code": 95, "remarks": None},
    },
),
        ),
    )
    # fmt: on
    def test_parse_rp(
            self, file_name, number_of_data_rows, stop_code, depth_top, depth_base, conducted_at, data_rows
    ):
        with open(file_name, "r", encoding="utf-8") as file:
            [method] = Parser().parse(file)

        method.point_z = point_z

        assert method.method_type == models.MethodType.RP
        assert len(method.method_data) == number_of_data_rows
        assert stop_code == method.stopcode
        assert method.depth_base == pytest.approx(depth_base)
        assert method.depth_top == pytest.approx(depth_top)
        assert method.conducted_at == conducted_at

        for row in method.method_data:
            if row.depth in data_rows:
                for key in data_rows[row.depth]:
                    assert getattr(row, key) == pytest.approx(
                        data_rows[row.depth][key]), f"{key} {getattr(row, key)} != {data_rows[row.depth][key]}"

    # fmt: off
    @pytest.mark.parametrize(
        "file_name, sounding_class, number_of_data_rows, stop_code, depth_top, depth_base, "
        "depth_in_soil, depth_in_rock, bedrock_elevation, "
        "conducted_at, data_rows",
        (
(
    "tests/data/srs-test-1.jb3", SoundingClass.JB3, 664, 95, Decimal("0.025"), Decimal("16.6"),
    Decimal("16.6"), None, Decimal(point_z - 16.6),  # TODO: Is bedrock elevation correct K=95,
                                                     #       without bedrock indication
    datetime(2023, 3, 23, 17, 33, 1),
    {
        # D=0.025,A=0.043,W=0.043,AK=174217,AKZ=5028,H=8,B=7.2,C=27.7,V=0.000,AB=0,S=0,SM=0,AP=0,R=7,AQ=0,P=0.046,PR=0.000,I=0.908,AZ=0.000,J=6.822,VB=0.2,AD=4
        Decimal("0.025"): {"penetration_force": Decimal("0.043"), "penetration_rate": Decimal('7.2'),
                           "torque": Decimal('0'), "rotation_rate": Decimal('7'), "increased_rotation_rate": False,
                           "flushing_pressure": Decimal("0.908"), "flushing_flow": Decimal("6.822"), "flushing": True,
                           "hammering": False, "comment_code": None, "remarks": None},
        Decimal("0.05"): {"penetration_force": Decimal("-0.015"), "penetration_rate": Decimal('175'),
                          "torque": Decimal('0'),
                          "rotation_rate": Decimal('7'), "increased_rotation_rate": False,
                          "flushing_pressure": Decimal("0.332"), "flushing_flow": Decimal("17.948"), "flushing": True,
                          "hammering": False, "comment_code": None, "remarks": None},
        Decimal("16.575"): {"hammering": False, "flushing": True, "increased_rotation_rate": True, "penetration_rate": Decimal('5.1'), "rotation_rate": Decimal('73')},
        Decimal("16.6"): {"increased_rotation_rate": False, "comment_code": 95,  "remarks": "(JB) avbruten", "penetration_rate": Decimal('4.1')},
    },
),
(
    "tests/data/srs-test-2.jbt", SoundingClass.JBTOT, 445, 95, Decimal("0.025"), Decimal("11.125"),
    Decimal('8.125'), Decimal('11.125') - Decimal('8.125'), Decimal(point_z) - Decimal('8.125'),
    datetime(2023, 8, 8, 11, 0, 29),
    {
        Decimal("0.025"): {"comment_code": None, "remarks": None, "flushing": False, "increased_rotation_rate": False, "penetration_rate": Decimal('14.829'), "rotation_rate": Decimal('7')},
        Decimal("8.000"): {"comment_code": None, "remarks": None, "increased_rotation_rate": True, "penetration_rate": Decimal('15.106'), "rotation_rate": Decimal('24'), "penetration_force": Decimal("18.062")},
        Decimal("8.025"): {"remarks": "Uppdragning: Medelkraft=-0.45 kN; Rotationshastighet=86 RPM; Stighastighet=134 mm/sec",
                           "increased_rotation_rate": True, "penetration_rate": Decimal('0.302'),
                           "rotation_rate": Decimal('85'), "penetration_force": Decimal("1.864")},
        Decimal("8.125"): {"comment_code": 80, "remarks": "Bergnivå Berg", "increased_rotation_rate": True,
                           "penetration_rate": Decimal('6.059'), "rotation_rate": Decimal('84'),
                           "penetration_force": Decimal("4.893")},
        Decimal("11.100"): {"comment_code": None, "remarks": None, "increased_rotation_rate": True,
                            "penetration_rate": Decimal('4.781'), "rotation_rate": Decimal('86'),
                            "penetration_force": Decimal("4.646")},
        Decimal("11.125"): {"comment_code": 95, "remarks": "(JB) avbruten", "increased_rotation_rate": False},
    },
),
# A=penetration_force
# B=penetration_rate (mm/s),
# V=torque (kNm), AP=hammering (on/off),
# R=rotation rate (rpm), AQ=Rotation (on/off), P=engine_pressure (MPa), PR=?, I=flushing_pressure ,
# AZ=hammering_pressure, J=flushing_flow
(
    "tests/data/srs-test-3.jbt", SoundingClass.JBTOT, 888, 95, Decimal("0.025"), Decimal("22.2"),
    Decimal("22.2"), None, Decimal(point_z) - Decimal("22.2"),   # TODO: Is bedrock elevation correct K=95, but not bedrock indication
    datetime(2021, 5, 28, 8, 44, 43),
    {
        Decimal("0.025"): {"comment_code": None, "remarks": None, "flushing": False,
                           "increased_rotation_rate": False, "penetration_rate": Decimal('3.848'),
                           "rotation_rate": Decimal('7')},
        Decimal("20.500"): {"comment_code": None,
                            "remarks": "Uppdragning: Medelkraft=-0.45 kN; Rotationshastighet=57 RPM; Stighastighet= 3 mm/sec",
                            "increased_rotation_rate": True},
        Decimal("22.2"): {"comment_code": 95, "remarks": "(JB) avbruten", "increased_rotation_rate": True},
    },
),
(
        "tests/data/srs-test-4.jb2", SoundingClass.JB2, 221, 94, Decimal("0.025"), Decimal("5.525"),
        Decimal("5.525"), 0, Decimal(point_z) - Decimal("5.525"),
        datetime(2023, 7, 27, 15, 1, 41),
        {
            Decimal("0.025"): {"comment_code": None, "remarks": None, "flushing": False,
                               "increased_rotation_rate": True, "penetration_rate": Decimal('9.013'),
                               "rotation_rate": Decimal('90')},
            Decimal("4.250"): {"comment_code": None,
                                "remarks":None,
                                "increased_rotation_rate": True},
            Decimal("22.2"): {"comment_code": 94, "remarks": "Stopp mot förmodat berg", "increased_rotation_rate": False},
        },
),
(
        "tests/data/srs-test-5.jb3", SoundingClass.JB3, 664, 95, Decimal("0.025"), Decimal("16.6"),
        Decimal("16.6"), None, Decimal(point_z) - Decimal("16.6"),
        datetime(2023, 3, 23, 17, 33, 1),
        {
            Decimal("0.025"): {"comment_code": None, "remarks": None, "flushing": True,
                               "increased_rotation_rate": False, "penetration_rate": Decimal('7.2'),
                               "rotation_rate": Decimal('7')},
            Decimal("4.250"): {"comment_code": None,
                               "remarks": None, "flushing": True,
                               "increased_rotation_rate": True, "rotation_rate": Decimal('68'),
                               "penetration_rate": Decimal('145.2'),},
            Decimal("16.6"): {"comment_code": 95, "flushing": True, "remarks": "(JB) avbruten",
                              "increased_rotation_rate": False, "penetration_rate": Decimal('4.1'),
                              "rotation_rate": Decimal('0')},
        },
),
        ),
    )
    # fmt: on
    def test_parse_srs(
            self, file_name, sounding_class, number_of_data_rows, stop_code, depth_top, depth_base, 
            depth_in_soil, depth_in_rock, bedrock_elevation, 
            conducted_at, data_rows
    ):
        with open(file_name, "r", encoding="windows-1252") as file:
            [method] = Parser().parse(file)

        method.point_z = point_z

        assert method.method_type == models.MethodType.SRS
        assert method.sounding_class == sounding_class
        assert len(method.method_data) == number_of_data_rows
        assert stop_code == method.stopcode
        assert method.depth_top == pytest.approx(depth_top)
        assert method.depth_base == pytest.approx(depth_base)
        assert method.depth_in_soil == pytest.approx(depth_in_soil)
        assert method.depth_in_rock == pytest.approx(depth_in_rock)
        assert method.bedrock_elevation == pytest.approx(bedrock_elevation)
        assert method.conducted_at == conducted_at

        for row in method.method_data:
            if row.depth in data_rows:
                for key in data_rows[row.depth]:
                    assert getattr(row, key) == pytest.approx(
                        data_rows[row.depth][key]), f"depth {row.depth} {key} {getattr(row, key)} != {data_rows[row.depth][key]}"

    # fmt: off
    @pytest.mark.parametrize(
        "file_name, number_of_data_rows, depth_top, depth_base, "
        "conducted_at, data_rows",
        (
(
    "tests/data/svt-test-1.std", 7, Decimal("2"), Decimal("10"),
    datetime(2021, 6, 30, 9, 33),
    {
        # D=2.00,AS=13.008,SV=12.880
        Decimal("2"): {"comment_code": None, "remarks": None, "shear_strength": Decimal("13.008"), "sensitivity": Decimal("12.880")},
        Decimal("3"): {"shear_strength": Decimal("13.440"), "sensitivity": Decimal("10.5")},
        Decimal("4"): {"shear_strength": Decimal("15.359"), "sensitivity": Decimal("8.98")},
        Decimal("4.99"): {"shear_strength": Decimal("16.334"), "sensitivity": Decimal("6.92")},
        Decimal("6"): {"shear_strength": Decimal("16.750"), "sensitivity": Decimal("8.38")},
        Decimal("8"): {"shear_strength": Decimal("18.974"), "sensitivity": Decimal("7.67")},
        Decimal("10"): {"comment_code": None, "remarks": None, "shear_strength": Decimal("18.974"), "sensitivity": Decimal("5.3")},
    },
),
         ),
    )
    # fmt: on
    def test_parse_svt(
            self, file_name, number_of_data_rows, depth_top, depth_base,
            conducted_at, data_rows
    ):
        with open(file_name, "r", encoding="windows-1252") as file:
            [method] = Parser().parse(file)

        method.point_z = point_z

        assert method.method_type == models.MethodType.SVT
        assert len(method.method_data) == number_of_data_rows
        assert method.depth_top == pytest.approx(depth_top)
        assert method.depth_base == pytest.approx(depth_base)
        assert method.conducted_at == conducted_at

        for row in method.method_data:
            if row.depth in data_rows:
                for key in data_rows[row.depth]:
                    assert getattr(row, key) == pytest.approx(
                        data_rows[row.depth][key]), f"{key} {getattr(row, key)} != {data_rows[row.depth][key]}"

    # fmt: off
    @pytest.mark.parametrize(
        "file_name",
        ("tests/data/dt-test-1.std",
        ) 
    )
    # fmt: on
    def test_placeholder_dissipation_test(
            self, file_name
    ):
        with open(file_name, "r", encoding="windows-1252") as file:
            methods = Parser().parse(file)
        
        assert methods

    # fmt: off
    @pytest.mark.parametrize(
        "file_name",
        ("tests/data/cpt-dt-test-1.std",) 
    )
    # fmt: on
    def test_return_one_method_one_placeholder(
            self, file_name
    ):
        with open(file_name, "r", encoding="windows-1252") as file:
            methods = Parser().parse(file)
        
        assert len(methods) == 2

    # fmt: off
    @pytest.mark.parametrize(
        "file_name, number_of_data_rows, depth_top, depth_base, "
        "conducted_at, data_rows",
        (
(
    "tests/data/wst-test-1.vim", 65, Decimal("0.025"), Decimal("1.625"),
    datetime(2022, 11, 1, 11, 7,5),
    {
        # penetration rate=B, hammering=AP, load=W, turning=H, rotation_rate=R
        Decimal("0.025"): {"comment_code": None, "remarks": None, "penetration_rate": Decimal("0.3"), "hammering": False, "rotation_rate":Decimal("0")},
        Decimal("0.350"): {"penetration_rate": Decimal("2.2"), "hammering": False, "rotation_rate": Decimal("0"), "load": Decimal("-0.796"), "turning": Decimal("0")},
        Decimal("0.375"): {"penetration_rate": Decimal("0.2"), "hammering": False, "rotation_rate": Decimal("0"), "load": Decimal("1.02"), "turning": Decimal("1112")},
    },
),
(
        "tests/data/wst-test-2.vim", 7, Decimal("3.625"), Decimal("3.775"),
        datetime(2018, 11, 20, 10, 50,21),
        {
            # load=A, hammering=AP, load=W, turning=H, rotation_rate=R
            Decimal("3.625"): {"load":Decimal("1.020"),  "turning":Decimal("152"), "penetration_rate": Decimal("154.208"), "comment_code": None, "remarks": None, "hammering": None},
            Decimal("3.700"): {"load": Decimal("1.020"), "turning": Decimal("24"), "penetration_rate": Decimal("10.287"), "hammering": None,},
            Decimal("3.775"): {"load": Decimal("5.681"), "turning": Decimal("24"), "penetration_rate": Decimal("1.506"), "hammering": None, "comment_code": 91, "remarks": "Sond kan ej drivas normalt"},
        },
),
         ),
    )
    # fmt: on
    def test_parse_wst(
            self, file_name, number_of_data_rows, depth_top, depth_base,
            conducted_at, data_rows
    ):
        with open(file_name, "r", encoding="windows-1252") as file:
            [method] = Parser().parse(file)

        method.point_z = point_z

        assert method.method_type == models.MethodType.WST
        assert len(method.method_data) == number_of_data_rows
        assert method.depth_top == pytest.approx(depth_top)
        assert method.depth_base == pytest.approx(depth_base)
        assert method.conducted_at == conducted_at

        for row in method.method_data:
            if row.depth in data_rows:
                # print(f"===> depth={row.depth}")
                for key in data_rows[row.depth]:
                    assert getattr(row, key) == pytest.approx(
                        data_rows[row.depth][key]), f"{key} {getattr(row, key)} != {data_rows[row.depth][key]}"
                    # print(f"{key}: {getattr(row, key)} == {data_rows[row.depth][key]}")



    # fmt: off
    @pytest.mark.parametrize(
        "file_name, number_of_data_rows,stop_code, predrilling_depth, depth_top, depth_base, "
        "conducted_at, data_rows",
        (
(
    "tests/data/dp-test-1.hfa", 194, 93, 2, Decimal("2.025"), Decimal("6.850"),
    datetime(2023, 9, 7, 11, 48,17),
    {
        # penetration_force=A, penetration rate=B, torque=V, ramming=S, rotation_rate=R, increased_rotation_rate=AQ
        Decimal("2.025"): {"comment_code": None, "remarks": None, "penetration_force":Decimal("1.002"), "penetration_rate": Decimal("438.805"), "torque":Decimal("0"), "ramming":Decimal("8"), "rotation_rate":Decimal("0"), "increased_rotation_rate": False},
        Decimal("2.350"): {"penetration_force":Decimal("1.093"), "penetration_rate": Decimal("56.87"), "torque":Decimal("0"), "ramming":Decimal("8"), "rotation_rate":Decimal("0"), "increased_rotation_rate": False},
        Decimal("3.000"): {"remarks": "1,0 Nm", "penetration_force":Decimal("0.274"), "penetration_rate": Decimal("11.569"), "torque":Decimal("0"), "ramming":Decimal("8"), "rotation_rate":Decimal("0"), "increased_rotation_rate": False},
        Decimal("3.375"): {"penetration_force":Decimal("0.144"), "penetration_rate": Decimal("7.079"), "torque":Decimal("0"), "ramming":Decimal("16"), "rotation_rate":Decimal("0"), "increased_rotation_rate": False},
        Decimal("6.825"): {"comment_code": 40, "remarks": "Nm", "penetration_force": Decimal("0.638"),
                           "penetration_rate": Decimal("0.101"), "torque": Decimal("0"), "ramming": Decimal("800"),
                           "rotation_rate": Decimal("0"), "increased_rotation_rate": False},
        Decimal("6.850"): {"comment_code": 93, "remarks": "Stopp mot sten", "penetration_force": Decimal("0.391"),
                           "penetration_rate": Decimal("0.050"), "torque": Decimal("0"), "ramming": Decimal("800"),
                           "rotation_rate": Decimal("0"), "increased_rotation_rate": False},

    },
),
(
        "tests/data/dp-test-2.hfa", 287, 90, 0, Decimal("0.025"), Decimal("7.175"),
        datetime(2014, 1, 15, 0, 8, 40),
        {
            # penetration_force=A, penetration rate=B, torque=V, ramming=S, rotation_rate=R, increased_rotation_rate=AQ
            Decimal("0.025"): {"comment_code": None, "remarks": None, "penetration_force": Decimal("0.600"),
                               "penetration_rate": Decimal("8.486"), "torque": Decimal("0"), "ramming": Decimal("8"),
                               "rotation_rate": None, "increased_rotation_rate": False},
            Decimal("2.350"): {"penetration_force": Decimal("0.380"), "penetration_rate": Decimal("5.985"),
                               "torque": Decimal("0"), "ramming": Decimal("16"), "rotation_rate": None,
                               "increased_rotation_rate": False},
            Decimal("7.175"): {"comment_code": 90, "remarks": "Sondering avbruten utan stopp, 215 Nm", 
                               "penetration_force": Decimal("0.070"),
                               "penetration_rate": Decimal("0.132"), "torque": Decimal("0"), "ramming": Decimal("56"),
                               "rotation_rate": None, "increased_rotation_rate": True},

        },
),
(
        "tests/data/dp-test-3.hfa", 348, 94, 0, Decimal("0.025"), Decimal("8.70"),
        datetime(2014, 1, 14, 0, 15, 6),
        {
            # penetration_force=A, penetration rate=B, torque=V, ramming=S, rotation_rate=R, increased_rotation_rate=AQ
            Decimal("2.025"): {"comment_code": None, "remarks": "5 Nm", "penetration_force": Decimal("0.249"),
                               "penetration_rate": Decimal("2.464"), "torque": Decimal("0"), "ramming": Decimal("32"),
                               "rotation_rate": None, "increased_rotation_rate": False},
            Decimal("2.350"): {"penetration_force": Decimal("0.279"), "penetration_rate": Decimal("7.001"),
                               "torque": Decimal("0"), "ramming": Decimal("16"), "rotation_rate": None,
                               "increased_rotation_rate": False},
            Decimal("2.550"): {"remarks": None, "penetration_force": Decimal("-0.161"),
                               "penetration_rate": Decimal("8.282"), "torque": Decimal("0"), "ramming": Decimal("8"),
                               "rotation_rate": None, "increased_rotation_rate": False},
            Decimal("8.700"): {"comment_code": 94, "remarks": "Förmodligen berg, 160 Nm", 
                               "penetration_force": Decimal("0.219"),
                               "penetration_rate": Decimal("0.286"), "torque": Decimal("0"), "ramming": Decimal("200"),
                               "rotation_rate": None, "increased_rotation_rate": True},
        },
),
(
        "tests/data/dp-test-4.hfa", 416, 94, 0, Decimal("0.025"), Decimal("10.4"),
        datetime(2014, 1, 14, 3, 43, 39),
        {
            # penetration_force=A, penetration rate=B, torque=V, ramming=S, rotation_rate=R, increased_rotation_rate=AQ
            Decimal("2.025"): {"comment_code": None, "remarks": None, "penetration_force": Decimal("0.847"),
                               "penetration_rate": Decimal("3.413"), "torque": Decimal("0"), "ramming": Decimal("24"),
                               "rotation_rate": None, "increased_rotation_rate": False},
            Decimal("10.4"): {"comment_code": 94, "remarks": "Förmodligen berg, 45 Nm", 
                              "penetration_force": Decimal("0.187"),
                               "penetration_rate": Decimal("0.322"), "torque": Decimal("0"), "ramming": Decimal("256"),
                               "rotation_rate": None, "increased_rotation_rate": False},

        },
),
(
        #
        # This is a manually modified test file to check conversion of alternative data block codes (B and C, V and AB)
        #
        "tests/data/dp-test-modified-2.hfa", 6, 93, 2, Decimal("2.025"), Decimal("6.850"),
        datetime(2023, 9, 7, 11, 48, 17),
        {
            # penetration_force=A, penetration rate=B, torque=V | AB, ramming=S, rotation_rate=R, increased_rotation_rate=AQ
            Decimal("2.025"): {"comment_code": None, "remarks": None, "penetration_force": Decimal("1.002"),
                               "penetration_rate": Decimal("434.782"), "torque": Decimal("0.001"), "ramming": Decimal("8"),
                               "rotation_rate": Decimal("0"), "increased_rotation_rate": False},
            Decimal("2.350"): {"penetration_force": Decimal("1.093"), "penetration_rate": Decimal("56.87"),
                               "torque": Decimal("0.001"), "ramming": Decimal("8"), "rotation_rate": Decimal("0"),
                               "increased_rotation_rate": False},
            Decimal("3.000"): {"remarks": "1,0 Nm", "penetration_force": Decimal("0.274"),
                               "penetration_rate": Decimal("11.569"), "torque": Decimal("0"), "ramming": Decimal("8"),
                               "rotation_rate": Decimal("0"), "increased_rotation_rate": False},
            Decimal("3.375"): {"penetration_force": Decimal("0.144"), "penetration_rate": Decimal("7.079"),
                               "torque": Decimal("0"), "ramming": Decimal("16"), "rotation_rate": Decimal("0"),
                               "increased_rotation_rate": False},
            Decimal("6.825"): {"comment_code": 40, "remarks": "Nm", "penetration_force": Decimal("0.638"),
                               "penetration_rate": Decimal("0.1012"), "torque": Decimal("0"), "ramming": Decimal("800"),
                               "rotation_rate": Decimal("0"), "increased_rotation_rate": False},
            Decimal("6.850"): {"comment_code": 93, "remarks": "Stopp mot sten", "penetration_force": Decimal("0.391"),
                               "penetration_rate": Decimal("0.0496"), "torque": Decimal("0"), "ramming": Decimal("800"),
                               "rotation_rate": Decimal("0"), "increased_rotation_rate": False},

        },
),
        ),
    )
    # fmt: on
    def test_parse_dp(
            self, file_name, number_of_data_rows, stop_code, predrilling_depth, depth_top, depth_base,
            conducted_at, data_rows
    ):
        with open(file_name, "r", encoding="cp1250") as file:
            [method] = Parser().parse(file)

        method.point_z = point_z

        assert method.method_type == models.MethodType.DP
        assert len(method.method_data) == number_of_data_rows
        assert method.stopcode == stop_code
        assert method.predrilling_depth == predrilling_depth
        assert method.depth_top == pytest.approx(depth_top)
        assert method.depth_base == pytest.approx(depth_base)
        assert method.conducted_at == conducted_at

        for row in method.method_data:
            if row.depth in data_rows:
                for key in data_rows[row.depth]:
                    assert getattr(row, key) == pytest.approx(
                        data_rows[row.depth][key], rel=Decimal(1e-3)), f"{key} {getattr(row, key)} != {data_rows[row.depth][key]}"


def test_parse_file_with_text_in_K_code():
    file_name = "tests/data/tot-test-9.TOT"
    with open(file_name, "r", encoding="utf-8") as file:
        [method] = Parser().parse(file)

    assert method
