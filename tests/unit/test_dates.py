import datetime

import pytest

from sgf_parser.parser import Parser


class TestDates:
    @pytest.mark.parametrize(
        "row, expected_result",
        [
            # ("HM=7,AK=200208221132", datetime.datetime(2002, 8, 22, 11, 32)),
            ("HM=24,KD=200208221132", datetime.datetime(2002, 8, 22, 11, 32)),
            ("HM=24,HD=20120105", datetime.datetime(2012, 1, 5)),
            ("HM=24,HD=09/04/99", datetime.datetime(1999, 4, 9)),
            ("HM=24,HD=27.06.2014", datetime.datetime(2014, 6, 27)),
            ("HM=24,KD=27.06.2014", datetime.datetime(2014, 6, 27)),
            # ("HM=24,KD=2019 05 09 1105", datetime.datetime(2019, 5, 9, 11, 5)),  # <- Not handled correctly
            ("HM=24,KD=01.11.2018", datetime.datetime(2018, 11, 1)),
            ("HM=24,HD=20230323,HI=173301,", datetime.datetime(2023, 3, 23, 17, 33, 1)),
        ],
    )
    def test_dates(self, row, expected_result):
        parser = Parser()

        method = parser.parse_header(parser._convert_str_to_dict(row))
        assert expected_result == method.conducted_at
