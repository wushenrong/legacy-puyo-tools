# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""The cli to create files used by older Puyo Puyo games."""

from pathlib import Path

import cloup
from PIL import Image

from legacy_puyo_tools.cli._confopts import (
    fmp_options,
    fnt_constraint,
    fnt_options,
    get_output_path,
    input_argument,
    mtx_constraint,
    mtx_options,
    output_option,
    padding_option,
)
from legacy_puyo_tools.formats._csv import CSV_TABLE_HEADER
from legacy_puyo_tools.formats.fmp import Fmp
from legacy_puyo_tools.formats.fnt import Fnt
from legacy_puyo_tools.formats.fpd import Fpd
from legacy_puyo_tools.typing import (
    FmpFontSize,
    FntFormatVersion,
    FontFormat,
    TableFormat,
)


@cloup.group()
@cloup.version_option()
def app() -> None:
    """A tool to create files used by older Puyo Puyo games."""


@app.command(name="fmp")
@input_argument("Path to the image file containing character graphics.")
@output_option
@fmp_options
@padding_option
def create_fmp(
    input_file: Path,
    output_file: Path | None,
    font_size: FmpFontSize,
    padding: int,
) -> None:
    """Create a fmp file from an image."""
    with (
        Image.open(input_file) as im,
        get_output_path(input_file, output_file, ".fmp").open("wb") as out_fp,
    ):
        Fmp.read_image(im, font_size=font_size, padding=padding).encode(out_fp)


@app.command(name="fnt", show_constraints=True)
@input_argument(
    f"Path to CSV file with the following header: {','.join(CSV_TABLE_HEADER)}"
)
@output_option
@fnt_options
@padding_option
@fnt_constraint
def create_fnt(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    input_file: Path,
    output_file: Path | None,
    fnt_version: FntFormatVersion,
    fnt_graphic: Path,
    font_height: int,
    font_width: int,
    padding: int,
) -> None:
    """Create a fnt file from a CSV table containing character and width.

    Able to create multiple versions used by the Nintendo DS, Wii, or the
    PlayStation Portable.
    """
    with input_file.open("r", encoding="utf-8", newline="") as in_fp:
        fnt = Fnt.read_csv(in_fp, font_height=font_height, font_width=font_width)

    if fnt_graphic:
        with Image.open(fnt_graphic) as im:
            fnt.add_graphics(
                im, font_height=font_height, font_width=font_width, padding=padding
            )

    with get_output_path(input_file, output_file, ".fnt").open("wb") as out_fp:
        fnt.encode(out_fp, version=fnt_version)


@app.command(name="fpd")
@input_argument(
    f"Path to CSV file with the following header: {','.join(CSV_TABLE_HEADER)}"
)
@output_option
def create_fpd(input_file: Path, output_file: Path | None) -> None:
    """Create a fpd file from a CSV table containing character and width."""
    with (
        input_file.open("r", encoding="utf-8", newline="") as in_fp,
        get_output_path(input_file, output_file, ".fpd").open("wb") as out_fp,
    ):
        Fpd.read_csv(in_fp).encode(out_fp)


@app.command(name="mtx", show_constraints=True)
@input_argument("Path to the XML file that contains manzai dialog.")
@output_option
@mtx_options
@mtx_constraint
def create_mtx(
    input_file: Path,
    output_file: Path | None,
    table: Path,
    table_format: TableFormat,
    font_format: FontFormat,
) -> None:
    """Create a mtx file from a XML file."""
    raise NotImplementedError("Creating MTX files is currently not implemented yet.")


if __name__ == "__main__":
    app()
