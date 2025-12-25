# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Tests for creating and converting fpd formats.

The sample data is the following string sectioned off by language:
ABC, 123, bo fo mo fo, 123, A, ' ', ra ri ru re ro (hiragana and katakana), A".
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from legacy_puyo_tools.cli.convert import convert_fpd
from legacy_puyo_tools.cli.create import create_fpd
from legacy_puyo_tools.exceptions import FileFormatError
from legacy_puyo_tools.formats.fpd import Fpd


@pytest.mark.parametrize(("output_file"), [(None), ("custom.csv")])
def test_fpd_conversion(
    lazy_shared_datadir: Path, lazy_datadir: Path, output_file: str | None
) -> None:
    """Test converting a fpd file."""
    cli_runner = CliRunner()

    fpd_file = "sample.fpd"

    expected_csv_path = Path(fpd_file).with_suffix(".csv")
    expected_csv = (lazy_shared_datadir / expected_csv_path).read_text(encoding="utf-8")

    with cli_runner.isolated_filesystem():
        input_arguments = [str(lazy_datadir / fpd_file)]

        if output_file:
            output_path = Path(output_file)
            input_arguments.extend(("--output", output_file))
        else:
            output_path = expected_csv_path

        result = cli_runner.invoke(convert_fpd, input_arguments)

        assert result.exit_code == 0

        converted_csv = output_path.read_text(encoding="utf-8")

        assert converted_csv == expected_csv


@pytest.mark.parametrize(("output_file"), [(None), ("custom.fpd")])
def test_fpd_creation(
    lazy_shared_datadir: Path, lazy_datadir: Path, output_file: str
) -> None:
    """Test creating a fpd file."""
    cli_runner = CliRunner()

    csv_file = "sample.csv"

    expected_fpd_path = Path(csv_file).with_suffix(".fpd")
    expected_fpd = (lazy_datadir / expected_fpd_path).read_bytes()

    with cli_runner.isolated_filesystem():
        input_arguments = [str(lazy_shared_datadir / csv_file)]

        if output_file:
            output_path = Path(output_file)
            input_arguments.extend(("--output", output_file))
        else:
            output_path = expected_fpd_path

        result = cli_runner.invoke(create_fpd, input_arguments)

        assert result.exit_code == 0

        converted_fpd = output_path.read_bytes()

        assert converted_fpd == expected_fpd


def test_fpd_to_string(lazy_datadir: Path) -> None:
    """Test converting to a string from a fpd character table."""
    fpd_file = lazy_datadir / "sample.fpd"
    sample_string = "ABC123波泼摸佛一二三A らりるれろラリルレロA"

    with fpd_file.open("rb") as fp:
        assert str(Fpd.decode(fp)) == sample_string


def test_fpd_lookup(lazy_datadir: Path) -> None:
    """Test looking up a character and index from a fpd character table."""
    fpd_file = lazy_datadir / "sample.fpd"

    with fpd_file.open("rb") as fp:
        fpd_data = Fpd.decode(fp)

    # The 6th index in the sample fpd data should be '3'
    assert fpd_data[5] == "3"

    # The 13th index in the sample fpd data should be the "second" 'A'
    assert fpd_data[13] == "A"


def test_fpd_exceptions(lazy_shared_datadir: Path, lazy_datadir: Path) -> None:
    """Test rasing exceptions when the input files are in the invalid format."""
    invalid_fpd = lazy_datadir / "invalid.fpd"
    invalid_csv = lazy_shared_datadir / "invalid.csv"
    surrogate_csv = lazy_shared_datadir / "surrogate.csv"
    surrogate_fpd = lazy_datadir / "surrogate.fpd"

    with invalid_fpd.open("rb") as fpd_fp, pytest.raises(FileFormatError):
        Fpd.decode(fpd_fp)

    with (
        invalid_csv.open("r", encoding="utf-8", newline="") as invalid_csv_fp,
        pytest.raises(FileFormatError),
    ):
        Fpd.read_csv(invalid_csv_fp)

    with (
        surrogate_csv.open("r", encoding="utf-8", newline="") as surrogate_csv_fp,
        surrogate_fpd.open("wb") as surrogate_fpd_fp,
        pytest.raises(FileFormatError) as exc_info,
    ):
        Fpd.read_csv(surrogate_csv_fp).encode(surrogate_fpd_fp)

    assert isinstance(exc_info.value.__cause__, UnicodeEncodeError)
