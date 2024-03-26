from io import StringIO

import pytest

from sgf_parser import Parser


class TestTotFlushing:
    """
    K - If K codes regulating flushing, then only look at K codes.
    AR - If no K codes present (regulating flushing), then look at AR code.
    I - If no K or AR code present (regulating flushing), then look at I code. If I > 0.1 then flushing is on.

    """

    test_data = {
        "D": "B=16.000",
        "AR_ON": "AR=1",
        "AR_OFF": "AR=0",
        "I_ON": "I=0.101",
        "I_OFF": "I=0.05",
        "K_72_ON": "K=72,T=Spyling begynner",
        "K_73_OFF": "K=73,T=Spyling slutter",
        "K_76_ON": "K=76,T=Slag og spyling begynner",
        "K_77_OFF": "K=77,T=Slag og spyling slutter",
        "K_74_HAMMER_ON": "K=74,T=Slag begynner",
        "K_75_HAMMER_OFF": "K=75,T=Slag slutter",
        "K_MULTI_ON": "K=72,T=Spyling begynner,K=74,T=Slag starter",
        "K_MULTI_ON_REVERSE": "K=74,T=Slag starter,K=72,T=Spyling begynner",
        "K_MULTI_OFF": "K=75,T=Slag slutter,K=73,T=Spyling slutter",
        "K_MULTI_OFF_REVERSE": "K=73,T=Spyling slutter,K=75,T=Slag slutter",
        "K_90": "K=90,T=Sondering avsluten uten stopp",
    }

    # fmt: off
    @pytest.mark.parametrize(
        "rows, expected_flushing",
        [
(  # Case #1: No K codes, Only AR codes
    ("AR_ON", "D", "AR_OFF", "D", "D", "AR_ON", "D", "AR_OFF"),
    (True,   True,  False, False, False, True, True, False),
),
(  # Case #2: No K codes (regulating flushing), No AR codes, Only I codes
    ("D", "I_ON", "D", "I_OFF", "D", "D",  "I_ON", "D", "I_OFF", "K_90"),
    (False, True, True, False, False, False, True, True, False, False),
),
(  # Case #3: K codes
    ("D", "K_72_ON", "D", "K_73_OFF", "D","K_74_HAMMER_ON", "K_75_HAMMER_OFF", "D", "K_76_ON", "D", "K_77_OFF", "D", "K_72_ON", "D", "K_77_OFF", "K_90",),
    (False, True,   True, False,    False,    False,           False,        False,  True,    True,   False,   False,  True,    True, False,  False),
),
(  # Case #4: K codes (overrides AR and I)
    ("D", "AR_ON", "I_ON", "K_72_ON", "I_OFF", "D", "I_OFF", "D", "D", "I_ON", "D", "I_OFF", "K_90"),
    (False, False, False, True, True, True, True, True, True, True, True, True, True),
),
(  # Case #5: No K codes, AR codes (overrides I)
    ("AR_ON", "I_OFF", "AR_OFF", "D", "I_ON", "I_OFF", "D", "AR_ON", "D", "AR_OFF"),
    (True,       True,   False, False, False, False, False, True,   True, False),
),
(  # Case #6: Multiple K codes on the same row (overrides AR and I)
    ("AR_ON", "I_ON", "AR_OFF", "D", "I_ON", "K_MULTI_ON", "D", "K_MULTI_ON", "D", "AR_OFF", "K_MULTI_OFF", "K_MULTI_ON_REVERSE", "D", "K_MULTI_OFF_REVERSE", "K_90"),
    (False,    False,   False, False, False, True,        True,  True,        True, True,    False,          True,                True, False,                 False),
),
        ],
    )
    # fmt: on
    def test_flushing(self, rows, expected_flushing):
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
