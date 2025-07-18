"""Test creating fpd formats.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from codecs import BOM_UTF16_LE
from pathlib import Path

import pytest
from click.testing import CliRunner

from legacy_puyo_tools.cli import create_fpd
from legacy_puyo_tools.exceptions import FileFormatError
from legacy_puyo_tools.fpd import ENCODING, Fpd
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
        with Path(input_file).open("w", encoding=ENCODING) as f:
            f.write(BOM_UTF16_LE.decode(ENCODING))
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
        with Path("sample_data_no_bom.txt").open("w", encoding=ENCODING) as f:
            f.write(SAMPLE_UNICODE_STRING)

        result = runner.invoke(create_fpd, ["sample_data_no_bom.txt"])

        assert isinstance(result.exception, FileFormatError)
        assert result.exit_code == 1


def test_manual_fpd_creation(tmp_path: Path) -> None:
    """Test creating a fpd from unicode file manually."""
    unicode_file = tmp_path / "sample_data.txt"

    with unicode_file.open("w", encoding=ENCODING) as f:
        f.write(BOM_UTF16_LE.decode(ENCODING))
        f.write(SAMPLE_UNICODE_STRING)

    assert Fpd.read_unicode_from_path(unicode_file).encode_fpd() == SAMPLE_FPD_STRING


def test_missing_bom_in_file(tmp_path: Path) -> None:
    """Test getting an error when the unicode text file does not have a BOM."""
    invalid_unicode_file = tmp_path / "invalid_data.txt"

    with invalid_unicode_file.open("w", encoding=ENCODING) as f:
        f.write(SAMPLE_UNICODE_STRING)

    with pytest.raises(FileFormatError):
        Fpd.read_unicode_from_path(invalid_unicode_file)
