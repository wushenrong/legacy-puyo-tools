# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""A commandline interface for the conversion tools."""

# pyright: reportPossiblyUnboundVariable=false

from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

import cloup
from cloup import option, option_group
from cloup.constraints import require_one
from PIL import Image

from legacy_puyo_tools.formats.fmp import (
    FMP_DEFAULT_FONT_SIZE,
    FMP_DEFAULT_MAX_TABLE_WIDTH,
    FMP_DEFAULT_PADDING,
    Fmp,
    FmpSize,
    FmpTableOrientation,
)
from legacy_puyo_tools.formats.fpd import FPD_CSV_HEADER, Fpd
from legacy_puyo_tools.formats.mtx import Mtx

_T = TypeVar("_T", bound=Callable[..., Any])


def input_argument(help_text: str) -> Callable[[_T], _T]:
    return cloup.argument(
        "input_file", help=help_text, type=cloup.Path(path_type=Path, dir_okay=False)
    )


output_option = option(
    "--output",
    "-o",
    "output_file",
    help="Output file. Defaults to an appropriate filename and extension.",
    type=cloup.Path(path_type=Path, dir_okay=False, writable=True),
)

fmp_option = option_group(
    "Font options",
    option(
        "--size",
        help="Size of the characters in the font.",
        default=FMP_DEFAULT_FONT_SIZE,
        type=cloup.Choice([8, 14], case_sensitive=False),
        show_default=True,
    ),
    option(
        "--padding",
        help="Size of the padding around the characters.",
        default=FMP_DEFAULT_PADDING,
        type=cloup.IntRange(0, 4),
        show_default=True,
    ),
)

table_options = option_group(
    "Table options",
    option(
        "--max-width",
        help="Maximum number of characters per column in the image.",
        default=FMP_DEFAULT_MAX_TABLE_WIDTH,
        type=cloup.IntRange(2, 64),
        show_default=True,
    ),
    option(
        "--orientation",
        help="The orientation of the character table.",
        default="portrait",
        type=cloup.Choice(["portrait", "landscape"], case_sensitive=False),
        show_default=True,
    ),
)

mtx_options = option_group(
    "Character table options",
    option(
        "--fpd",
        help="Use a fpd file as the character table.",
        type=cloup.Path(exists=True, dir_okay=False, path_type=Path),
    ),
    option(
        "--csv",
        help="Use a CSV file as the character table.",
        type=cloup.Path(exists=True, dir_okay=False, path_type=Path),
    ),
    constraint=require_one.rephrased(
        "exactly 1 character table required for mtx files",
    ),
)


@cloup.group()
@cloup.version_option()
def app() -> None:
    """Tools to create and convert files used by older Puyo Puyo games."""


@app.group()
def convert() -> None:
    """Convert files used by older Puyo games to an editable format."""


@convert.command(name="fmp")
@input_argument("Fmp file containing font data.")
@output_option
@fmp_option
@table_options
def convert_fmp(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    input_file: Path,
    output_file: Path | None,
    size: FmpSize,
    padding: int,
    max_width: int,
    orientation: FmpTableOrientation,
) -> None:
    """Convert a fmp file to an editable image file (Default is PNG)."""
    out_path = output_file or Path(input_file.name).with_suffix(".png")

    with input_file.open("rb") as in_fp:
        Fmp.decode(in_fp, font_size=size).write_image(
            padding=padding, max_width=max_width, orientation=orientation
        ).save(out_path)


@convert.command(name="fpd")
@input_argument("Fpd file containing character data.")
@output_option
def convert_fpd(input_file: Path, output_file: Path | None) -> None:
    """Convert a fpd file to a CSV file."""
    out_path = output_file or Path(input_file.name).with_suffix(".csv")

    with (
        input_file.open("rb") as in_fp,
        out_path.open("w", encoding="utf-8", newline="") as out_fp,
    ):
        Fpd.decode(in_fp).write_csv(out_fp)


@convert.command(name="mtx", show_constraints=True)
@input_argument("Mtx file containing Manzai text.")
@output_option
@mtx_options
def convert_mtx(
    input_file: Path, output_file: Path | None, fpd: Path, csv: Path
) -> None:
    """Convert a mtx file to a XML file."""
    # pylint: disable=possibly-used-before-assignment
    if fpd:
        with fpd.open("rb") as fp:
            fpd_data = Fpd.decode(fp)

    if csv:
        with csv.open("r", encoding="utf-8", newline="") as fp:
            fpd_data = Fpd.read_csv(fp)

    out_path = output_file or Path(input_file.name).with_suffix(".xml")

    with input_file.open("rb") as in_fp, out_path.open("wb") as out_fp:
        out_fp.write(Mtx.decode(in_fp).write_xml(fpd_data))


@app.group()
def create() -> None:
    """Create files to used by older Puyo games."""


@create.command(name="fmp")
@input_argument("Image file that contains graphical font/character data.")
@output_option
@fmp_option
def create_fmp(
    input_file: Path,
    output_file: Path | None,
    size: FmpSize,
    padding: int,
) -> None:
    """Create a fmp file from a image file, preferably from BMP or PNG."""
    out_path = output_file or Path(input_file.name).with_suffix(".fmp")

    with Image.open(input_file) as im, out_path.open("wb") as out_fp:
        Fmp.read_image(im, font_size=size, padding=padding).encode(out_fp)


@create.command(name="fpd")
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


@create.command(name="mtx", show_constraints=True)
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
