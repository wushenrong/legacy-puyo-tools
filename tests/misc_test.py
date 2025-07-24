"""Miscellaneous tests that are not covered by other test files.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from legacy_puyo_tools.formats.fpd import Fpd
from tests.conftest import SAMPLE_FPD_STRING


def test_misc_fpd() -> None:
    """Test getting a character and index from a fpd character table."""
    fpd_data = Fpd.decode(SAMPLE_FPD_STRING)
    # The 6th index in the sample fpd data should be "3"
    assert fpd_data[5] == "3"

    # The character 佛 in the sample fpd data should be the 9th index
    assert fpd_data.get_index("佛") == 9
