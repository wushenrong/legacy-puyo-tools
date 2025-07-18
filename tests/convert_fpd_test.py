"""Test converting fpd formats."""

from pathlib import Path

from click.testing import CliRunner

from legacy_puyo_tools.cli import convert_fpd
from legacy_puyo_tools.fpd import BOM_UTF16_LE, ENCODING
from tests.samples import FPD_SAMPLE_STRING, UNICODE_SAMPLE_STRING


def test_convert_fpd() -> None:
    """Test converting a fpd file."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        with Path("sample_data.fpd").open("wb") as f:
            f.write(FPD_SAMPLE_STRING)

        result = runner.invoke(convert_fpd, ["sample_data.fpd"])

        with Path("sample_data.txt").open("r", encoding=ENCODING) as f:
            assert f.read(1) == BOM_UTF16_LE.decode(ENCODING)
            assert f.read() == UNICODE_SAMPLE_STRING

        assert result.exit_code == 0


def test_convert_fpd_with_output() -> None:
    """Test converting a fpd file."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        with Path("sample_data.fpd").open("wb") as f:
            f.write(FPD_SAMPLE_STRING)

        result = runner.invoke(
            convert_fpd, ["sample_data.fpd", "--output", "sample.txt"]
        )

        with Path("sample.txt").open("r", encoding=ENCODING) as f:
            assert f.read(1) == BOM_UTF16_LE.decode(ENCODING)
            assert f.read() == UNICODE_SAMPLE_STRING

        assert result.exit_code == 0
