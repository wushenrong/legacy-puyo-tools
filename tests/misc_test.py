"""Miscellaneous tests that are not covered by other test files.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from legacy_puyo_tools.fpd import Fpd
from tests.conftest import SAMPLE_FPD_STRING


def test_get_fpd_character() -> None:
    """Test getting a character from a fpd character table."""
    fpd_data = Fpd.decode_fpd(SAMPLE_FPD_STRING)

    # The 6th index in the sample fpd data should be "3"
    assert fpd_data[5] == "3"


def test_lookup_fpd_character() -> None:
    """Test looking up the index of a fpd character."""
    lookup_table = Fpd.decode_fpd(SAMPLE_FPD_STRING).create_lookup_table()

    # The character 佛 in the sample fpd data should be the 9th index
    assert lookup_table["佛"] == 9
