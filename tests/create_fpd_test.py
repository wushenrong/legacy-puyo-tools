"""Test creating fpd formats."""

from pathlib import Path

from click.testing import CliRunner

from legacy_puyo_tools.cli import create_fpd
from legacy_puyo_tools.exceptions import FileFormatError
from legacy_puyo_tools.fpd import BOM_UTF16_LE, ENCODING
from tests.samples import FPD_SAMPLE_STRING, UNICODE_SAMPLE_STRING


def test_create_fpd() -> None:
    """Test creating a fpd file."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        with Path("sample_data.txt").open("w", encoding=ENCODING) as f:
            f.write(BOM_UTF16_LE.decode(ENCODING))
            f.write(UNICODE_SAMPLE_STRING)

        result = runner.invoke(create_fpd, ["sample_data.txt"])

        with Path("sample_data.fpd").open("rb") as f:
            assert f.read() == FPD_SAMPLE_STRING

        assert result.exit_code == 0


def test_create_fpd_with_output() -> None:
    """Test creating a fpd file."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        with Path("sample_data.txt").open("w", encoding=ENCODING) as f:
            f.write(BOM_UTF16_LE.decode(ENCODING))
            f.write(UNICODE_SAMPLE_STRING)

        result = runner.invoke(
            create_fpd, ["sample_data.txt", "--output", "sample.fpd"]
        )

        with Path("sample.fpd").open("rb") as f:
            assert f.read() == FPD_SAMPLE_STRING

        assert result.exit_code == 0


def test_create_fpd_no_bom() -> None:
    """Test creating an FPD file without a Byte Order Mark."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        with Path("sample_data.txt").open("w", encoding=ENCODING) as f:
            f.write(UNICODE_SAMPLE_STRING)

        result = runner.invoke(create_fpd, ["sample_data.txt"])

        assert isinstance(result.exception, FileFormatError)
        assert result.exit_code == 1
