# SPDX-FileCopyrightText: 2021 Nick Woronekin
# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Tests for creating and converting fpd formats.

The sample data is the following string sectioned off by language:
ABC, 123, bo fo mo fo, 123, A, ra ri ru re ro (hiragana and katakana), A".
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from legacy_puyo_tools.cli import convert_fpd, create_fpd
from legacy_puyo_tools.formats.base import FormatError
from legacy_puyo_tools.formats.fpd import Fpd


@pytest.mark.parametrize(("custom_output"), [(None), ("custom_output.csv")])
def test_fpd_conversion(lazy_datadir: Path, custom_output: str | None) -> None:
    """Test converting a fpd file."""
    cli_runner = CliRunner()

    default_output = "sample.csv"

    sample_fpd = lazy_datadir / "sample.fpd"
    expected_csv = (lazy_datadir / default_output).read_text(encoding="utf-8")

    with cli_runner.isolated_filesystem():
        input_arguments = [str(sample_fpd)]

        if custom_output:
            input_arguments.extend(["--output", custom_output])

        result = cli_runner.invoke(convert_fpd, input_arguments)

        converted_csv = Path(custom_output or default_output).read_text(
            encoding="utf-8"
        )

        assert converted_csv == expected_csv

        assert result.exit_code == 0


@pytest.mark.parametrize(("custom_output"), [(None), ("custom_output.fpd")])
def test_fpd_creation(lazy_datadir: Path, custom_output: str) -> None:
    """Test creating a fpd file."""
    cli_runner = CliRunner()

    default_output = "sample.fpd"

    sample_csv = lazy_datadir / "sample.csv"
    expected_fpd = (lazy_datadir / default_output).read_bytes()

    with cli_runner.isolated_filesystem():
        input_arguments = [str(sample_csv)]

        if custom_output:
            input_arguments.extend(["--output", custom_output])

        result = cli_runner.invoke(create_fpd, input_arguments)

        converted_fpd = Path(custom_output or default_output).read_bytes()

        assert converted_fpd == expected_fpd

        assert result.exit_code == 0


def test_fpd_to_string(lazy_datadir: Path) -> None:
    """Test converting to a string from a fpd character table."""
    fpd_file = lazy_datadir / "sample.fpd"

    with fpd_file.open("rb") as fp:
        fpd_data = Fpd.decode(fp)

    assert str(fpd_data) == "ABC123波泼摸佛一二三AらりるれろラリルレロA"


def test_fpd_lookup(lazy_datadir: Path) -> None:
    """Test looking up a character and index from a fpd character table."""
    fpd_file = lazy_datadir / "sample.fpd"

    with fpd_file.open("rb") as fp:
        fpd_data = Fpd.decode(fp)

    # The 6th index in the sample fpd data should be '3'
    assert fpd_data[5] == "3"

    # The character '佛' in the sample fpd data should be the 9th index
    assert fpd_data.get_index("佛") == 9

    # The 13th index in the sample fpd data should be the "second" 'A'
    assert fpd_data[13] == "A"


def test_fpd_format_error(lazy_datadir: Path) -> None:
    """Test rasing an error when the input files are in the invalid format."""
    invalid_fpd = lazy_datadir / "invalid.fpd"
    invalid_csv = lazy_datadir / "invalid.csv"

    with invalid_fpd.open("rb") as fpd_fp, pytest.raises(FormatError):
        Fpd.decode(fpd_fp)

    with (
        invalid_csv.open("r", encoding="utf-8", newline="") as csv_fp,
        pytest.raises(FormatError),
    ):
        Fpd.read_csv(csv_fp)
