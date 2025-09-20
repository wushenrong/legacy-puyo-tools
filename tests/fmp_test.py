# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Tests for creating and converting fmp formats.

The sample data is the following string sectioned off by language:
ABC, 123, bo fo mo fo, 123, A, ' ', ra ri ru re ro (hiragana and katakana), A".
"""

from pathlib import Path

import pytest
from click.testing import CliRunner
from PIL import Image, ImageChops

from legacy_puyo_tools.cli.convert import convert_fmp
from legacy_puyo_tools.cli.create import create_fmp
from legacy_puyo_tools.formats.fmp import Fmp, FmpTableOrientation


@pytest.mark.parametrize(
    ("input_file", "output_file", "size", "orientation"),
    [
        ("ark.fmp", None, 14, "portrait"),
        ("fusion.fmp", "custom_table.png", 8, "landscape"),
    ],
)
def test_fmp_conversion(
    lazy_datadir: Path,
    input_file: str,
    output_file: str | None,
    size: int,
    orientation: FmpTableOrientation,
) -> None:
    """Test converting a fmp file."""
    cli_runner = CliRunner()

    expected_image_path = Path(input_file).with_suffix(".png")

    with (
        cli_runner.isolated_filesystem(),
        Image.open(lazy_datadir / expected_image_path) as expected_image,
    ):
        input_arguments = [
            str(lazy_datadir / input_file),
            "--size",
            str(size),
            "--orientation",
            orientation,
        ]

        if output_file:
            output_path = Path(output_file)
            input_arguments.extend(("--output", output_file))
        else:
            output_path = expected_image_path

        result = cli_runner.invoke(convert_fmp, input_arguments)

        assert result.exit_code == 0

        with Image.open(output_path) as converted_image:
            difference = ImageChops.difference(expected_image, converted_image)

            assert difference.getbbox() is None


@pytest.mark.parametrize(
    ("input_file", "output_file", "size"),
    [
        ("ark.png", None, 14),
        ("fusion.png", "custom_table.fmp", 8),
        ("colored_ark.png", None, 14),
    ],
)
def test_fmp_creation(
    lazy_datadir: Path, input_file: str, output_file: str | None, size: int
) -> None:
    """Test creating a fmp file."""
    cli_runner = CliRunner()

    expected_fmp_path = Path(input_file).with_suffix(".fmp")
    expected_fmp = (lazy_datadir / expected_fmp_path).read_bytes()

    with cli_runner.isolated_filesystem():
        input_arguments = [
            str(lazy_datadir / input_file),
            "--size",
            str(size),
        ]

        if output_file:
            output_path = Path(output_file)
            input_arguments.extend(("--output", output_file))
        else:
            output_path = expected_fmp_path

        result = cli_runner.invoke(create_fmp, input_arguments)

        assert result.exit_code == 0

        converted_fmp = output_path.read_bytes()

        assert converted_fmp == expected_fmp


def test_fmp_exceptions(lazy_datadir: Path) -> None:
    """Test rasing exceptions when the inputs are incorrect."""
    test_image = lazy_datadir / "colored_ark.png"

    with (
        pytest.raises(
            ValueError, match="The size of the character or padding is incorrect"
        ),
        Image.open(test_image) as im,
    ):
        Fmp.read_image(im, font_size=8)
