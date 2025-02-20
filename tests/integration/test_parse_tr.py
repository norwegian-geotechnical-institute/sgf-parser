from datetime import datetime
from decimal import Decimal

import pytest

from sgf_parser import Parser, models

point_z = 40.5


@pytest.mark.parametrize(
    "file_name, number_of_data_rows, stop_code, predrilling_depth, depth_top, depth_base, conducted_at",
    (
        (
            "tests/data/tr-test-1.trt",
            613,
            91,
            Decimal("1.80"),
            Decimal("1.825"),
            Decimal("17.125"),
            datetime(2023, 2, 2, 15, 1, 31),
        ),
        (
            "tests/data/tr-test-2.trt",
            449,
            91,
            Decimal("0"),
            Decimal("0.025"),
            Decimal("11.225"),
            datetime(2023, 1, 17, 12, 8, 15),
        ),
        (
            "tests/data/tr-test-3.trt",
            633,
            91,
            Decimal("0"),
            Decimal("0.025"),
            Decimal("15.825"),
            datetime(2023, 1, 17, 10, 10, 17),
        ),
    ),
)
def test_parse_tr(
    file_name,
    number_of_data_rows,
    stop_code,
    predrilling_depth,
    depth_top,
    depth_base,
    conducted_at,  # data_rows,
):
    with open(file_name, "r", encoding="cp1250") as file:
        [method] = Parser().parse(file)

    method.point_z = point_z

    assert method.method_type == models.MethodType.TR
    assert len(method.method_data) == number_of_data_rows
    assert method.stopcode == stop_code
    assert method.predrilling_depth == predrilling_depth
    assert method.depth_top == pytest.approx(depth_top)
    assert method.depth_base == pytest.approx(depth_base)
    assert method.conducted_at == conducted_at
