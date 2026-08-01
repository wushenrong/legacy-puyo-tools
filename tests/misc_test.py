# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Tests for internal miscellaneous modules."""

import io

import pytest

from legacy_puyo_tools.formats.fmp import Fmp
from legacy_puyo_tools.formats.mtx import Mtx


def test_unseekable_streams() -> None:
    """Test rejecting streams that are not seekable."""

    class NonSeekableStream(io.BytesIO):
        def seekable(self) -> bool:
            return False

    with pytest.raises(io.UnsupportedOperation), NonSeekableStream() as fp:
        Fmp.decode(fp)

    with pytest.raises(io.UnsupportedOperation), NonSeekableStream() as fp:
        Mtx.decode(fp)
