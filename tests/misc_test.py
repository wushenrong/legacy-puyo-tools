# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Tests for internal miscellaneous modules."""

from legacy_puyo_tools._math import find_best_ratio_divisor_pair


def test_find_best_ratio_divisor_pair() -> None:
    """Test finding the best ratio devisor pairs."""
    assert find_best_ratio_divisor_pair(7) == (1, 7)
    assert find_best_ratio_divisor_pair(0) == (0, 0)
    assert find_best_ratio_divisor_pair(-3) == (1, -3)
