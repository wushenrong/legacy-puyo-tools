# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Tests for internal miscellaneous modules."""

import pytest

from legacy_puyo_tools._math import find_medium_divisors


def test_find_best_ratio_divisor_pair() -> None:
    """Test finding the best ratio devisor pairs."""
    assert find_medium_divisors(10) == (2, 5)
    assert find_medium_divisors(7) == (1, 7)

    with pytest.raises(ValueError, match=r"\d+ is not a natural number."):
        find_medium_divisors(0)

    with pytest.raises(ValueError, match=r"\d+ is not a natural number."):
        find_medium_divisors(-3)
