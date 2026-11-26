from io import StringIO

import pytest

from sgf_parser import Parser


class TestTotKCodes:
    test_data = {
        "D": "B=16.000",
        "AP_ON": "AP=1",
        "AP_OFF": "AP=0",
        "AQ_ON": "AQ=1",
        "AQ_OFF": "AQ=0",
        "AR_ON": "AR=1",
        "AR_OFF": "AR=0",
        "I_ON": "I=0.251",
        "I_OFF": "I=0.250",
        "R_ON": "R=35.101",
        "R_OFF": "R=12.05",
        "K_70_R_ON": "K=70,T=Økt rotasjon begynner",
        "K_71_R_OFF": "K=71,T=Økt rotasjon slutter",
        "K_72_F_ON": "K=72,T=Spyling begynner",
        "K_73_F_OFF": "K=73,T=Spyling slutter",
        "K_76_H_F_ON": "K=76,T=Slag og spyling begynner",
        "K_77_H_F_OFF": "K=77,T=Slag og spyling slutter",
        "K_74_H_ON": "K=74,T=Slag begynner",
        "K_75_H_OFF": "K=75,T=Slag slutter",
        "K_MULTI_H_F_ON": "K=72,T=Spyling begynner,K=74,T=Slag starter",
        "K_MULTI_H_F_ON_REVERSE": "K=74,T=Slag starter,K=72,T=Spyling begynner",
        "K_MULTI_H_F_R_ON": "K=72,T=Spyling begynner,K=74,T=Slag starter,K=70,T=Økt rotasjon begynner",
        "K_MULTI_H_F_R_ON_REVERSE": "K=70,T=Økt rotasjon begynner,K=74,T=Slag starter,K=72,T=Spyling begynner",
        "K_MULTI_H_F_OFF": "K=75,T=Slag slutter,K=73,T=Spyling slutter",
        "K_MULTI_H_F_OFF_REVERSE": "K=73,T=Spyling slutter,K=75,T=Slag slutter",
        "K_MULTI_H_F_R_OFF": "K=75,T=Slag slutter,K=73,T=Spyling slutter,K=71,T=Økt rotasjon slutter",
        "K_MULTI_H_F_R_OFF_REVERSE": "K=71,T=Økt rotasjon slutter,K=73,T=Spyling slutter,K=75,T=Slag slutter",
        "K_90": "K=90,T=Sondering avsluten uten stopp",
    }

    # fmt: off
    @pytest.mark.parametrize(
        "rows, expected_hammering",
        [
(  # Case #1: Nothing regulating hammering, expect all to be False
    ("AR_ON", "D", "AR_OFF", "D", "D", "AR_ON", "D", "AR_OFF"),
    (False, False, False, False, False, False, False, False),
),
(  # Case #2: No K codes, Only AP codes
    ("AP_ON", "D", "AP_OFF", "D", "D", "AP_ON", "D", "AP_OFF"),
    (True,   True,  False, False, False, True, True, False),
),
(  # Case #3: K codes
    ("D", "K_72_F_ON", "D", "K_73_F_OFF", "D", "K_74_H_ON", "K_75_H_OFF", "D", "K_76_H_F_ON", "D", "K_77_H_F_OFF", "D", "K_72_F_ON", "D", "K_77_H_F_OFF", "K_90",),
    (False, False,   False,    False,   False,    True,       False,     False,   True,      True,    False,     False,   False,   False,      False,     False),
),
(  # Case #4: K code ON override AP until a K code OFF
    ("D", "AP_ON", "I_ON", "K_74_H_ON", "I_OFF", "D", "I_OFF", "AP_OFF", "AP_ON", "I_ON", "D", "I_OFF", "K_90"),
    (False, True, True,   True,       True,    True, True,   True,      True,     True, True, True,    True),
),
(  # Case #5: No K codes, AP codes 
    ("AP_ON", "I_OFF", "AP_OFF", "D", "I_ON", "I_OFF", "D", "AP_ON", "D", "AP_OFF"),
    (True, True, False, False, False, False, False, True, True, False),
),
(  # Case #6: Multiple K code ON codes override AP until a K code OFF code
    ("AP_ON", "D", "AP_OFF", "D", "I_ON", "K_MULTI_H_F_ON", "D", "K_MULTI_H_F_ON", "D", "AP_OFF", "K_MULTI_H_F_OFF", "K_MULTI_H_F_ON_REVERSE", "D", "K_MULTI_H_F_OFF_REVERSE", "K_90"),
    (True,  True, False, False, False,      True,         True,   True,          True, True,      False,             True,                   True,     False,                  False),
),
        ],
    )
    # fmt: on
    def test_hammering(self, rows, expected_hammering):
        """
        K - An ON code overrides measurements until an OFF code.
        AP - When not enabled by K, use the AP code.

        """
        # Header
        test_string = (
            "$\r\nHA=1,HB=1122,HC=NGI-52CYSG2,HD=20200910,HI=1343,HK=20,HM=24,HJ=20200291,HO=0.0,HQ=JOST\r\n#\r\n"
        )

        # data_lines
        test_string += "".join([f"D={i}.0,{self.test_data[test_index]}\r\n" for i, test_index in enumerate(rows)])

        with StringIO(test_string) as file:
            [method] = Parser().parse(file)

        assert len(expected_hammering) == len(method.method_data), "Length mismatch"

        for i, method_data in enumerate(method.method_data):
            assert method_data.hammering == expected_hammering[i], f"Failed at index {i}"

    # fmt: off
    @pytest.mark.parametrize(
        "rows, expected_flushing",
        [
(  # Case #1: No K codes, Only AR codes
    ("AR_ON", "D", "AR_OFF", "AQ_ON", "D", "AR_ON", "D", "AR_OFF"),
    (True,   True,  False, False, False, True, True, False),
),
(  # Case #2: No K codes (regulating flushing), No AR codes, Only I codes
    ("D", "I_ON", "D", "I_OFF", "D", "D",  "I_ON", "D", "I_OFF", "K_90"),
    (False, True, True, False, False, False, True, True, False, False),
),
(  # Case #3: K codes
    ("D", "K_72_F_ON", "D", "K_73_F_OFF", "D","K_74_H_ON", "K_75_H_OFF", "D", "K_76_H_F_ON", "D", "K_77_H_F_OFF", "D", "K_72_F_ON", "D", "K_77_H_F_OFF", "K_90",),
    (False, True,   True, False,    False,    False,           False,        False,  True,    True,   False,   False,  True,    True, False,  False),
),
(  # Case #4: K code ON override AR until a K code OFF
    ("D", "AR_ON", "I_ON", "K_72_F_ON", "I_OFF", "D", "I_OFF", "D", "D", "I_ON", "D", "I_OFF", "K_90"),
    (False, True, True, True, True, True, True, True, True, True, True, True, True),
),
(  # Case #5: No K codes, only AR codes and I codes
    ("AR_ON", "I_OFF", "AR_OFF", "D", "I_ON", "I_OFF", "D", "AR_ON", "D", "AR_OFF"),
    (True,       False,   False, False, True, False, False, True,   True, False),
),
(  # Case #6: Multiple K code ON codes override AR and I until a K OFF code
    ("AR_ON", "I_ON", "AR_OFF", "D", "I_ON", "K_MULTI_H_F_ON", "D", "K_MULTI_H_F_ON", "D", "AR_OFF", "K_MULTI_H_F_OFF", "K_MULTI_H_F_ON_REVERSE", "D", "K_MULTI_H_F_OFF_REVERSE", "K_90"),
    (True,    True,   False, False, True   , True,            True,  True,           True, True,     False,               True,                  True,   False,                 False),
),
        ],
    )
    # fmt: on
    def test_flushing(self, rows, expected_flushing):
        """
        K - An K code ON overrides measurements until an OFF code.
        AR - When no K code is turned on, use the AR code.
        I - If AR is absent and no K code is turned on, flushing is on when I > 0.25 MPa.

        """
        # Header
        test_string = (
            "$\r\nHA=1,HB=1122,HC=NGI-52CYSG2,HD=20200910,HI=1343,HK=20,HM=24,HJ=20200291,HO=0.0,HQ=JOST\r\n#\r\n"
        )

        # data_lines
        test_string += "".join([f"D={i}.0,{self.test_data[test_index]}\r\n" for i, test_index in enumerate(rows)])

        with StringIO(test_string) as file:
            [method] = Parser().parse(file)

        assert len(expected_flushing) == len(method.method_data), "Length mismatch"
        
        for i, method_data in enumerate(method.method_data):
            assert method_data.flushing == expected_flushing[i], f"Failed at index {i}"

    # fmt: off
    @pytest.mark.parametrize(
        "rows, expected_rotation",
        [
(  # Case #1: No K codes, Only AQ codes
    ("AQ_ON", "D", "AQ_OFF", "D", "D", "AQ_ON", "D", "AQ_OFF"),
    (True, True, False, False, False, True, True, False),
),
(  # Case #2: No K codes (regulating flushing), No AQ codes, Only R codes
    ("D", "R_ON", "D", "R_OFF", "D", "D", "R_ON", "D", "R_OFF", "K_90"),
    (False, True, True, False, False, False, True, True, False, False),
),
(  # Case #3: K codes
    ("D", "K_70_R_ON", "D", "K_71_R_OFF", "D", "K_74_H_ON", "K_75_H_OFF", "D", "K_76_H_F_ON", "D", "K_70_R_ON", "D", "K_72_F_ON", "D", "K_70_R_ON", "K_90",),
    (False, True,     True,    False,   False,   False,         False,  False,     False,    False,    True,   True,      True,  True,  True,        True),
),
(  # Case #4: K code ON override AQ and R until a K code OFF
    ("D", "AQ_ON", "R_ON", "K_70_R_ON", "R_OFF", "D", "R_OFF", "I_OFF", "D", "R_ON", "D", "R_OFF", "K_71_R_OFF", "K_90"),
    (False, True, True,    True,       True,   True,   True,    True,    True,   True,  True, True,     False,        False),
),
(  # Case #5: No K codes, AQ codes do not override R
    ("AQ_ON", "R_OFF", "AQ_OFF", "D", "R_ON", "R_OFF", "D", "AQ_ON", "D", "AQ_OFF"),
    (True, False, False, False, True, False, False, True, True, False),
),
(  # Case #6: Multiple K code ON override AQ and R until a K code OFF
    ("AQ_ON", "R_ON", "AQ_OFF", "D", "R_ON", "K_MULTI_H_F_R_ON_REVERSE", "D", "K_MULTI_H_F_R_ON_REVERSE", "D", "AQ_OFF", "K_MULTI_H_F_R_OFF_REVERSE", "K_MULTI_H_F_R_ON", "D", "K_MULTI_H_F_R_OFF", "K_90"),
    (True,    True,  False, False,  True, True,                      True, True,                      True,     True,   False,                       True,             True, False,                False),
),
        ],
    )
    # fmt: on
    def test_rotation(self, rows, expected_rotation):
        """
        K - An ON code overrides measurements until an OFF code.
        AQ - When no K code is turned on, use the AQ code.
        R - If AQ is absent and no K code is turned on, look at the R code.
            If R > 35 rpm then increased rotation is on.
        """
        # Header
        test_string = (
            "$\r\nHA=1,HB=1122,HC=NGI-52CYSG2,HD=20200910,HI=1343,HK=20,HM=24,HJ=20200291,HO=0.0,HQ=JOST\r\n#\r\n"
        )

        # data_lines
        test_string += "".join([f"D={i}.0,{self.test_data[test_index]}\r\n" for i, test_index in enumerate(rows)])

        with StringIO(test_string) as file:
            [method] = Parser().parse(file)

        assert len(expected_rotation) == len(method.method_data), "Length mismatch"

        for i, method_data in enumerate(method.method_data):
            assert method_data.increased_rotation_rate == expected_rotation[i], f"Failed at index {i}"

    @pytest.mark.parametrize(
        "on_code, off_code, fields",
        [
            (70, 71, ("increased_rotation_rate",)),
            (72, 73, ("flushing",)),
            (74, 75, ("hammering",)),
            (76, 77, ("flushing", "hammering")),
        ],
    )
    def test_k_code_override(self, on_code, off_code, fields):
        rows = [
            f"K={on_code}",
            "AR=0,AP=0,AQ=0",
            "I=0.250,R=35",
            "K=90",
            f"K={off_code},AR=1,AP=1,AQ=1,I=1,R=40",
            "",
            "AR=1,AP=1,AQ=1",
            "AR=0,AP=0,AQ=0",
            "I=1,R=40,AP=1",
            "I=0.250,R=35,AP=0",
            f"K={on_code}",
            "AR=0,AP=0,AQ=0",
        ]
        text = "$\nHM=24\n#\n" + "".join(f"D={i},{row}\n" for i, row in enumerate(rows))

        with StringIO(text) as file:
            [method] = Parser().parse(file)

        expected = [True, True, True, True, False, False, True, False, True, False, True, True]
        for field in fields:
            assert [getattr(row, field) for row in method.method_data] == expected

    @pytest.mark.parametrize(
        "codes",
        [
            "K=70,K=71,K=72,K=73,K=74,K=75",
            "K=75,K=74,K=73,K=72,K=71,K=70",
            "K=76,K=77,K=70,K=71",
        ],
    )
    def test_off_codes_override_on_codes_on_same_row(self, codes):
        text = f"$\nHM=24\n#\nD=0,{codes},AR=1,AP=1,AQ=1\nD=1\n"

        with StringIO(text) as file:
            [method] = Parser().parse(file)

        assert [(row.flushing, row.hammering, row.increased_rotation_rate) for row in method.method_data] == [
            (False, False, False),
            (False, False, False),
        ]

    @pytest.mark.parametrize("ending", ["", "#$\nD=99\n", "$\nHM=24\n"])
    def test_runtime_states_reset_after_file_loop(self, ending):
        parser = Parser()
        text = "$\nHM=24\n#\nD=0,K=70,K=76\n#\nD=1\n$\nHM=24\n#\nD=2,K=70,K=76\n" + ending

        with StringIO(text) as file:
            methods = parser.parse(file)

        assert len(methods) == 3
        for method in methods:
            row = method.method_data[0]
            assert (row.flushing, row.hammering, row.increased_rotation_rate) == (True, True, True)
            blank_row = parser.parse_data(method, "D=100")
            assert (blank_row.flushing, blank_row.hammering, blank_row.increased_rotation_rate) == (
                False,
                False,
                False,
            )
            measured_row = parser.parse_data(method, "D=101,AR=0,AP=0,AQ=0")
            assert (measured_row.flushing, measured_row.hammering, measured_row.increased_rotation_rate) == (
                False,
                False,
                False,
            )
