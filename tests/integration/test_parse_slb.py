from datetime import datetime
from decimal import Decimal

import pytest

from sgf_parser import Parser, models

point_z = 40.5


@pytest.mark.parametrize(
    "file_name, number_of_data_rows, stop_code, depth_top, depth_base, conducted_at",
    (
        (
            "tests/data/slb-test-1.slb",
            55,
            91,
            Decimal("0.025"),
            Decimal("1.375"),
            datetime(2023, 8, 15, 13, 9, 46),
        ),
        (
            "tests/data/slb-test-2.slb",
            55,
            91,
            Decimal("0.025"),
            Decimal("1.375"),
            datetime(2023, 8, 15, 13, 9, 46),
        ),
        (
            "tests/data/slb-test-3.slb",
            123,
            93,
            Decimal("0.025"),
            Decimal("3.075"),
            datetime(2024, 4, 27, 8, 32, 30),
        ),
    ),
)
def test_parse_slb(
    file_name,
    number_of_data_rows,
    stop_code,
    depth_top,
    depth_base,
    conducted_at,  # data_rows,
):
    with open(file_name, "r", encoding="cp1250") as file:
        [method] = Parser().parse(file)

    method.point_z = point_z

    assert method.method_type == models.MethodType.SLB
    assert len(method.method_data) == number_of_data_rows
    assert method.stopcode == stop_code
    assert method.depth_top == pytest.approx(depth_top)
    assert method.depth_base == pytest.approx(depth_base)
    assert method.conducted_at == conducted_at
