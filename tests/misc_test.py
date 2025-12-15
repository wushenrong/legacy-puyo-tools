# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Tests for internal miscellaneous modules."""

import io

import pytest

from legacy_puyo_tools._math import find_medium_divisors
from legacy_puyo_tools.formats.fmp import Fmp
from legacy_puyo_tools.formats.mtx import Mtx


def test_find_best_ratio_divisor_pair() -> None:
    """Test finding the best ratio devisor pairs."""
    assert find_medium_divisors(10) == (2, 5)
    assert find_medium_divisors(7) == (1, 7)

    with pytest.raises(ValueError, match=r"\d+ is not a natural number."):
        find_medium_divisors(0)

    with pytest.raises(ValueError, match=r"\d+ is not a natural number."):
        find_medium_divisors(-3)


def test_unseekable_streams() -> None:
    """Test rejecting streams that are not seekable."""

    class NonSeekableStream(io.BytesIO):
        def seekable(self) -> bool:
            return False

    with pytest.raises(io.UnsupportedOperation), NonSeekableStream() as fp:
        Fmp.decode(fp)

    with pytest.raises(io.UnsupportedOperation), NonSeekableStream() as fp:
        Mtx.decode(fp)
