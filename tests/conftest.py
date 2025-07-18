"""Sample data and fixures for testing.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from pathlib import Path

import pytest

# ABC, 123, bo fo mo fo, 123, ra ri ru re ro (hiragana and katakana)
SAMPLE_UNICODE_STRING = "ABC123波泼摸佛一二三らりるれろラリルレロ"
SAMPLE_FPD_STRING = (
    b"A\x00\x00B\x00\x00C\x00\x001\x00\x002\x00\x003\x00\x00"
    b"\xe2l\x00\xfcl\x00xd\x00[O\x00\x00N\x00\x8cN\x00\tN\x00"
    b"\x890\x00\x8a0\x00\x8b0\x00\x8c0\x00\x8d0\x00"
    b"\xe90\x00\xea0\x00\xeb0\x00\xec0\x00\xed0\x00"
)


@pytest.fixture(scope="session")
def sample_fpd_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Fixture to create a temporary FPD file for testing.

    Returns:
        A Path object pointing to a temporary FPD file.
    """
    sample_file = tmp_path_factory.mktemp("data") / "sample.fpd"

    with sample_file.open("wb") as f:
        f.write(SAMPLE_FPD_STRING)

    return sample_file
