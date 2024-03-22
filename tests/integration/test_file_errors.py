import pytest
from pydantic import ValidationError

from sgf_parser import Parser


class TestFileErrors:
    @pytest.mark.parametrize(
        "file_name, expected_exception",
        [
            ("tests/data/cpt-test-malformed-data-1.cpt", ValidationError),
            ("tests/data/cpt-test-malformed-date-header.cpt", ValidationError),
            ("tests/data/cpt-test-wrong-type.cpt", ValueError),
        ],
    )
    def test_error_handling_malformed_files(self, file_name, expected_exception):
        with open(file_name, "r") as file:
            with pytest.raises(expected_exception):
                Parser().parse(file)
