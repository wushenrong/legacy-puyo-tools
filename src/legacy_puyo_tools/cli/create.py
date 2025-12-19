# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""The cli to create files used by older Puyo Puyo games."""

from pathlib import Path

import cloup
from PIL import Image

from legacy_puyo_tools.cli.confopts import (
    fmp_option,
    input_argument,
    mtx_options,
    output_option,
)
from legacy_puyo_tools.formats.fmp import Fmp, FmpFontSize
from legacy_puyo_tools.formats.fpd import FPD_CSV_HEADER, Fpd


@cloup.group()
@cloup.version_option()
def app() -> None:
    """A tool to create files used by older Puyo Puyo games."""


@app.command(name="fmp")
@input_argument("Image file that contains graphical font/character data.")
@output_option
@fmp_option
def create_fmp(
    input_file: Path,
    output_file: Path | None,
    size: FmpFontSize,
    padding: int,
) -> None:
    """Create a fmp file from a image file, preferably from BMP or PNG."""
    out_path = output_file or Path(input_file.name).with_suffix(".fmp")

    with Image.open(input_file) as im, out_path.open("wb") as out_fp:
        Fmp.read_image(im, font_size=size, padding=padding).encode(out_fp)


@app.command(name="fpd")
@input_argument(f"CSV file with the following header: {','.join(FPD_CSV_HEADER)}")
@output_option
def create_fpd(input_file: Path, output_file: Path | None) -> None:
    """Create a fpd file from a CSV file."""
    out_path = output_file or Path(input_file.name).with_suffix(".fpd")

    with (
        input_file.open("r", encoding="utf-8", newline="") as in_fp,
        out_path.open("wb") as out_fp,
    ):
        Fpd.read_csv(in_fp).encode(out_fp)


@app.command(name="mtx", show_constraints=True)
@input_argument("XML file that contains markup text or dialog.")
@output_option
@mtx_options
def create_mtx(
    input_file: Path, output_file: Path | None, fpd: Path, csv: Path
) -> None:
    """Create a mtx file from a XML file."""
    raise NotImplementedError("Creating MTX files is currently not implemented yet.")


if __name__ == "__main__":
    app()
