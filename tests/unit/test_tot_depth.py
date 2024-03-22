from io import StringIO

import pytest

from sgf_parser import models, Parser


point_z = 40.5


class TestMethodService:
    @pytest.mark.parametrize(
        "test_indices, expected_stopcode, expected_depth_top, expected_depth_base, expected_depth_in_soil, "
        "expected_depth_in_rock, expected_bedrock_elevation",
        [
            # Case #1: No codes
            (("D", "D", "D", "D"), None, 0, 3.0, 3.0, None, None),
            # Case #2: 41/43 followed by no other codes
            (("D", "D41", "D", "D"), None, 0, 3.0, 1, None, None),
            (("D", "D43", "D", "D"), None, 0, 3.0, 1, None, None),
            # Case #3: 41/43 followed by 42 (false positive)
            (("D", "D41", "D42", "D", "D"), None, 0, 4.0, 4, None, None),
            (("D", "D43", "D", "D42", "D"), None, 0, 4.0, 4, None, None),
            # Case #4: 41/43 followed by 42 (false positive), then new 41/43
            (("D", "D41", "D42", "D", "D", "D41", "D"), None, 0, 6.0, 5, None, None),
            (("D", "D43", "D", "D42", "D", "D41", "D"), None, 0, 6.0, 5, None, None),
            # Only depth in rock and bedrock elevation when end with code 93/94:
            # In case of 90 -> depth_base == depth_in_soil
            (
                ("D", "D43", "D", "D42", "D", "D41", "D", "D90"),
                models.StopCode.INTERRUPTED_WITHOUT_STOP_90,
                0,
                7.0,
                7,
                None,
                None,
            ),
            # In case of 91 -> depth_base == depth_in_soil
            (
                ("D", "D43", "D", "D42", "D", "D41", "D", "D91"),
                models.StopCode.CANNOT_DRIVE_FURTHER_91,
                0,
                7.0,
                7,
                None,
                None,
            ),
            (
                ("D", "D43", "D", "D42", "D", "D41", "D", "D93"),
                models.StopCode.STOP_AGAINST_STONE_BLOCK_OR_ROCK_93,
                0,
                7.0,
                5,
                2,
                point_z - 5,
            ),
            (("D", "D41", "D", "D93"), models.StopCode.STOP_AGAINST_STONE_BLOCK_OR_ROCK_93, 0, 3.0, 1, 2, point_z - 1),
            (
                ("D", "D", "D41", "D", "D", "D", "D94"),
                models.StopCode.STOP_AGAINST_PRESUMED_ROCK_94,
                0,
                6.0,
                2,
                4,
                point_z - 2,
            ),
        ],
    )
    def test_tot_depths(
        self,
        test_indices,
        expected_stopcode,
        expected_depth_top,
        expected_depth_base,
        expected_depth_in_soil,
        expected_depth_in_rock,
        expected_bedrock_elevation,
    ):
        """
        Test all possible variants of depth in soil/rock from/to

        Test variants:

        No comment codes
        only 41 or 43
        repeated [41 or 43 followed by 42 (false positive)], then nothing
        repeated [41 or 43 followed by 42 (false positive)], then followed by 41 or 43

        """
        test_data = {
            "D": "B=0.01,R=103,AQ=1,I=0.15,A=0.00,AR=1,AK=13:44:07.335",
            "D41": "B=0.01,R=103,AQ=1,I=0.15,A=0.00,AR=1,AK=13:44:07.335,K=41",
            "D42": "B=0.01,R=103,AQ=1,I=0.15,A=0.00,AR=1,AK=13:44:07.335,K=42",
            "D43": "B=0.01,R=103,AQ=1,I=0.15,A=0.00,AR=1,AK=13:44:07.335,K=43",
            "D90": "B=0.01,R=103,AQ=1,I=0.15,A=0.00,AR=1,AK=13:44:07.335,K=90",
            "D91": "B=0.01,R=103,AQ=1,I=0.15,A=0.00,AR=1,AK=13:44:07.335,K=91",
            "D92": "B=0.01,R=103,AQ=1,I=0.15,A=0.00,AR=1,AK=13:44:07.335,K=92",
            "D93": "B=0.01,R=103,AQ=1,I=0.15,A=0.00,AR=1,AK=13:44:07.335,K=93",
            "D94": "B=0.01,R=103,AQ=1,I=0.15,A=0.00,AR=1,AK=13:44:07.335,K=94",
        }

        # Header
        test_string = (
            f"$\r\nHA=1,HB=1122,HC=NGI-52CYSG2,HD=20200910,"
            f"HI=1343,HK=20,HM=24,HJ=20200291,HO=0.0,HQ=TOV,HZ={point_z}\r\n#\r\n"
        )

        # data_lines
        test_string += "".join([f"D={i}.0,{test_data[test_index]}\r\n" for i, test_index in enumerate(test_indices)])

        with StringIO(test_string) as file:
            [method] = Parser().parse(file)

        assert method.depth_top == expected_depth_top
        assert method.depth_base == expected_depth_base
        assert method.stopcode == expected_stopcode
        assert method.depth_in_rock == expected_depth_in_rock
        assert method.depth_in_soil == expected_depth_in_soil
        assert method.bedrock_elevation == expected_bedrock_elevation
