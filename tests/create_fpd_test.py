"""Test creating fpd formats.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from codecs import BOM_UTF16_LE
from pathlib import Path

import pytest
from click.testing import CliRunner

from legacy_puyo_tools.cli import create_fpd
from legacy_puyo_tools.formats.base import FileFormatError
from legacy_puyo_tools.formats.fpd import FPD_ENCODING
from tests.conftest import SAMPLE_FPD_STRING, SAMPLE_UNICODE_STRING


@pytest.mark.parametrize(
    ("input_file", "output_file", "output"),
    [
        ("sample_data.txt", "sample_data.fpd", False),
        ("sample_data.txt", "custom_output.fpd", True),
    ],
)
def test_create_fpd(input_file: str, output_file: str, output: bool) -> None:
    """Test creating a fpd file."""
    cli_runner = CliRunner()

    with cli_runner.isolated_filesystem():
        with Path(input_file).open("w", encoding=FPD_ENCODING) as f:
            f.write(BOM_UTF16_LE.decode(FPD_ENCODING))
            f.write(SAMPLE_UNICODE_STRING)

        if output:
            result = cli_runner.invoke(
                create_fpd, [input_file, "--output", output_file]
            )
        else:
            result = cli_runner.invoke(create_fpd, [input_file])

        with Path(output_file).open("rb") as f:
            assert f.read() == SAMPLE_FPD_STRING

        assert result.exit_code == 0


def test_create_fpd_no_bom() -> None:
    """Test creating an FPD file without a Byte Order Mark."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        with Path("sample_data_no_bom.txt").open("w", encoding=FPD_ENCODING) as f:
            f.write(SAMPLE_UNICODE_STRING)

        result = runner.invoke(create_fpd, ["sample_data_no_bom.txt"])

        assert isinstance(result.exception, FileFormatError)
        assert result.exit_code == 1
