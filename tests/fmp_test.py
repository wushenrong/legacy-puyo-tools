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

from legacy_puyo_tools.cli import convert_fmp
from legacy_puyo_tools.formats.fmp import FmpTableOrientation


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

    sample_fmp = lazy_datadir / input_file
    expected_image_path = Path(input_file).with_suffix(".png")
    output_path = Path(output_file or input_file).with_suffix(".png")

    with (
        cli_runner.isolated_filesystem(),
        Image.open(lazy_datadir / expected_image_path) as expected_image,
    ):
        input_arguments = [
            str(sample_fmp),
            "--size",
            str(size),
            "--orientation",
            orientation,
        ]

        if output_file:
            input_arguments.extend(("--output", output_file))

        result = cli_runner.invoke(convert_fmp, input_arguments)

        assert result.exit_code == 0

        with Image.open(output_path) as converted_image:
            difference = ImageChops.difference(expected_image, converted_image)

            assert difference.getbbox() is None
