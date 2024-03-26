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
        "I_ON": "I=0.101",
        "I_OFF": "I=0.05",
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
(  # Case #4: K codes (overrides AP)
    ("D", "AP_ON", "I_ON", "K_74_H_ON", "I_OFF", "D", "I_OFF", "AP_OFF", "AP_ON", "I_ON", "D", "I_OFF", "K_90"),
    (False, False, False,   True,       True,    True, True,   True,     True,     True, True,  True,    True),
),
(  # Case #5: No K codes, AP codes 
    ("AP_ON", "I_OFF", "AP_OFF", "D", "I_ON", "I_OFF", "D", "AP_ON", "D", "AP_OFF"),
    (True, True, False, False, False, False, False, True, True, False),
),
(  # Case #6: Multiple K codes on the same row (overrides AP)
    ("AP_ON", "D", "AP_OFF", "D", "I_ON", "K_MULTI_H_F_ON", "D", "K_MULTI_H_F_ON", "D", "AP_OFF", "K_MULTI_H_F_OFF", "K_MULTI_H_F_ON_REVERSE", "D", "K_MULTI_H_F_OFF_REVERSE", "K_90"),
    (False,  False, False, False, False,      True,         True,   True,          True, True,     False,             True,                   True,     False,                  False),
),
        ],
    )
    # fmt: on
    def test_hammering(self, rows, expected_hammering):
        """
        K - If K codes regulating flushing, then only look at K codes.
        AP - If no K codes present (regulating hammering), then look at the AP code.

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
(  # Case #4: K codes (overrides AR and I)
    ("D", "AR_ON", "I_ON", "K_72_F_ON", "I_OFF", "D", "I_OFF", "D", "D", "I_ON", "D", "I_OFF", "K_90"),
    (False, False, False, True, True, True, True, True, True, True, True, True, True),
),
(  # Case #5: No K codes, AR codes (overrides I)
    ("AR_ON", "I_OFF", "AR_OFF", "D", "I_ON", "I_OFF", "D", "AR_ON", "D", "AR_OFF"),
    (True,       True,   False, False, False, False, False, True,   True, False),
),
(  # Case #6: Multiple K codes on the same row (overrides AR and I)
    ("AR_ON", "I_ON", "AR_OFF", "D", "I_ON", "K_MULTI_H_F_ON", "D", "K_MULTI_H_F_ON", "D", "AR_OFF", "K_MULTI_H_F_OFF", "K_MULTI_H_F_ON_REVERSE", "D", "K_MULTI_H_F_OFF_REVERSE", "K_90"),
    (False,    False,   False, False, False, True,        True,  True,        True, True,    False,          True,                True, False,                 False),
),
        ],
    )
    # fmt: on
    def test_flushing(self, rows, expected_flushing):
        """
        K - If K codes regulating flushing, then only look at K codes.
        AR - If no K codes present (regulating flushing), then look at AR code.
        I - If no K or AR code present (regulating flushing), then look at the I code. If I > 0.1 MPa then flushing is on.

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
(  # Case #4: K codes (overrides AQ and R)
    ("D", "AQ_ON", "R_ON", "K_70_R_ON", "R_OFF", "D", "R_OFF", "I_OFF", "D", "R_ON", "D", "R_OFF", "K_71_R_OFF", "K_90"),
    (False, False, False,    True,       True,  True,  True,   True,   True,  True,  True, True,    False,        False),
),
(  # Case #5: No K codes, AQ codes (overrides R)
    ("AQ_ON", "R_OFF", "AQ_OFF", "D", "R_ON", "R_OFF", "D", "AQ_ON", "D", "AQ_OFF"),
    (True, True, False, False, False, False, False, True, True, False),
),
(  # Case #6: Multiple K codes on the same row (overrides AQ and R)
    ("AQ_ON", "R_ON", "AQ_OFF", "D", "R_ON", "K_MULTI_H_F_R_ON_REVERSE", "D", "K_MULTI_H_F_R_ON_REVERSE", "D", "AQ_OFF", "K_MULTI_H_F_R_OFF_REVERSE", "K_MULTI_H_F_R_ON", "D", "K_MULTI_H_F_R_OFF", "K_90"),
    (False,    False,  False, False,  False, True,                      True, True,                      True,     True,  False,                       True,             True, False,                False),
),
        ],
    )
    # fmt: on
    def test_rotation(self, rows, expected_rotation):
        """
        K - If K codes regulating increased rotation, then only look at K codes.
        AQ - If no K codes present (regulating increased rotation), then look at the AQ code.
        R - If no K or AQ code present (regulating increased rotation), then look at the R code.
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
