"""Test converting fpd formats.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from codecs import BOM_UTF16_LE
from pathlib import Path

import pytest
from click.testing import CliRunner

from legacy_puyo_tools.cli import convert_fpd
from legacy_puyo_tools.exceptions import FileFormatError
from legacy_puyo_tools.fpd import ENCODING, Fpd
from tests.conftest import SAMPLE_FPD_STRING, SAMPLE_UNICODE_STRING


@pytest.mark.parametrize(
    ("input_file", "output_file", "output"),
    [
        ("sample_data.fpd", "sample_data.txt", False),
        ("sample_data.fpd", "custom_output.txt", True),
    ],
)
def test_convert_fpd(input_file: str, output_file: str, output: bool) -> None:
    """Test converting a fpd file."""
    cli_runner = CliRunner()

    with cli_runner.isolated_filesystem():
        with Path(input_file).open("wb") as f:
            f.write(SAMPLE_FPD_STRING)

        if output:
            result = cli_runner.invoke(
                convert_fpd, [input_file, "--output", output_file]
            )
        else:
            result = cli_runner.invoke(convert_fpd, [input_file])

        with Path(output_file).open("r", encoding=ENCODING) as f:
            assert f.read(1) == BOM_UTF16_LE.decode(ENCODING)
            assert f.read() == SAMPLE_UNICODE_STRING

        assert result.exit_code == 0


def test_convert_fpd_from_path(sample_fpd_file: Path) -> None:
    """Test converting a fpd file from a path instead of a file object."""
    assert str(Fpd.read_fpd_from_path(sample_fpd_file)) == SAMPLE_UNICODE_STRING


def test_fpd_format_error(tmp_path: Path) -> None:
    """Test getting an error when fpd is not in the correct format."""
    invalid_fpd = tmp_path / "invalid.fpd"

    with invalid_fpd.open("wb") as f:
        f.write(b"Not a multiple of 3 bytes long.")

    with pytest.raises(FileFormatError):
        Fpd.read_fpd_from_path(invalid_fpd)
