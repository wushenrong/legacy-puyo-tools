# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Tests for creating and converting fnt formats.

The sample data is the following string sectioned off by language:
ABC, 123, bo fo mo fo, 123, A, ' ', ra ri ru re ro (hiragana and katakana), A".
"""

from pathlib import Path

import pytest
from click.testing import CliRunner
from PIL import Image, ImageChops

from legacy_puyo_tools.cli.convert import convert_fnt
from legacy_puyo_tools.typing import ImageOrientation


@pytest.mark.parametrize(
    ("input_file", "output_file", "extract_graphics", "orientation"),
    [("ark.fnt", None, True, "portrait")],
)
def test_fnt_conversion(
    lazy_shared_datadir: Path,
    lazy_datadir: Path,
    input_file: str,
    output_file: str | None,
    extract_graphics: bool,
    orientation: ImageOrientation,
) -> None:
    """Test converting a fnt file."""
    cli_runner = CliRunner()

    expected_csv_path = Path("ark.csv")
    expected_image_path = Path(input_file).with_suffix(".png")
    expected_csv = (lazy_shared_datadir / "sample.csv").read_text(encoding="utf-8")

    with (
        cli_runner.isolated_filesystem(),
        Image.open(lazy_datadir / expected_image_path) as expected_image,
    ):
        input_arguments = [
            str(lazy_datadir / input_file),
            "--extract-graphics",
            str(extract_graphics),
            "--orientation",
            orientation,
        ]

        if output_file:
            output_path = Path(output_file)
            input_arguments.extend(("--output", output_file))
        else:
            output_path = expected_image_path

        result = cli_runner.invoke(convert_fnt, input_arguments)

        assert result.exit_code == 0

        converted_csv = expected_csv_path.read_text(encoding="utf-8")

        assert converted_csv == expected_csv

        with Image.open(output_path) as converted_image:
            difference = ImageChops.difference(expected_image, converted_image)

            assert difference.getbbox() is None
