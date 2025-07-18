"""Miscellaneous tests that are not covered by other test files.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from legacy_puyo_tools.fpd import Fpd
from tests.conftest import SAMPLE_FPD_STRING


def test_get_fpd_character() -> None:
    """Test getting a character from an Fpd instance."""
    fpd_data = Fpd.decode_fpd(SAMPLE_FPD_STRING)

    # The 5th character in the sample fpd data should be "3"
    assert fpd_data[5] == "3"
