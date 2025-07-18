"""Tests for converting fpd formats."""

from codecs import BOM_UTF16_LE
from pathlib import Path

import pytest
from click.testing import CliRunner

from legacy_puyo_tools.cli import convert_fpd
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
