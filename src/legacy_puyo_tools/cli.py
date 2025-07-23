"""A commandline interface for the conversion tools.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

# pyright: reportPossiblyUnboundVariable=false

from pathlib import Path
from typing import BinaryIO, Literal

import click
import cloup
from cloup import option, option_group
from cloup.constraints import require_one

from legacy_puyo_tools.fmp import Fmp, FmpSize
from legacy_puyo_tools.fpd import Fpd
from legacy_puyo_tools.io import get_file_name
from legacy_puyo_tools.mtx import Mtx

# TODO: When upgrading to Python 3.12, add type to the beginning of aliases
FmpSizeOption = Literal["8", "14"]

output_option = option(
    "--output",
    "-o",
    "output_file",
    help="Output file. Defaults to an appropriate filename and extension.",
    type=cloup.File("wb"),
)

mtx_options = option_group(
    "Character table options",
    option(
        "--fpd",
        help="Use a fpd file as the character table.",
        type=cloup.Path(exists=True, dir_okay=False, path_type=Path),
    ),
    option(
        "--unicode",
        help="Use a unicode text file as the character table.",
        type=cloup.Path(exists=True, dir_okay=False, path_type=Path),
    ),
    constraint=require_one.rephrased(
        "exactly 1 character table required for mtx files",
    ),
)


fmp_option = option_group(
    "Font options",
    option(
        "--size",
        help="Size of the characters in the font.",
        default=14,
        type=click.Choice(FmpSize, case_sensitive=False),
    ),
    option(
        "--padding",
        help="Size of padding around the characters.",
        default=1,
        type=cloup.IntRange(0, 4),
    ),
)


@cloup.group()
@cloup.version_option()
def app() -> None:
    """A conversion tool for files used by older Puyo games."""


@app.group()
def create() -> None:
    """Create files to used by older Puyo games."""


@create.command(name="fpd")
@cloup.argument(
    "input_file",
    help="Unicode text file encoded in UTF-16 little-endian.",
    type=cloup.File("rb"),
)
@output_option
def create_fpd(input_file: BinaryIO, output_file: BinaryIO) -> None:
    """Create a fpd file from a unicode text file."""
    path = output_file or Path(get_file_name(input_file)).with_suffix(".fpd")

    Fpd.read_unicode(input_file).write_fpd(path)


@create.command(name="mtx", show_constraints=True)
@cloup.argument(
    "input_file",
    help="XML file that contains markup text or dialog.",
    type=cloup.File("rb"),
)
@output_option
@mtx_options
def create_mtx(
    input_file: BinaryIO, output_file: BinaryIO, fpd: Path, unicode: Path
) -> None:
    """Create a mtx file from a XML file."""
    raise NotImplementedError("Creating MTX files is currently not implemented yet.")


@create.command(name="fmp", show_constraints=True)
@cloup.argument(
    "input_file",
    help="Image file that contains graphical font/character data.",
    type=cloup.File("rb"),
)
@output_option
@fmp_option
def create_fmp(
    input_file: BinaryIO, output_file: BinaryIO, size: FmpSize, padding: int
) -> None:
    """Create a mtx file from a image file."""
    raise NotImplementedError("Creating FMP files is currently not implemented yet.")


@app.group()
def convert() -> None:
    """Convert files used by older Puyo games to an editable format."""


@convert.command(name="fpd")
@cloup.argument(
    "input_file", help="Fpd file containing character data.", type=cloup.File("rb")
)
@output_option
def convert_fpd(input_file: BinaryIO, output_file: BinaryIO) -> None:
    """Convert a fpd file to a UTF-16 little-endian unicode text file."""
    path = output_file or Path(get_file_name(input_file)).with_suffix(".txt")

    Fpd.read_fpd(input_file).write_unicode(path)


@convert.command(name="fmp")
@cloup.argument(
    "input_file", help="Fmp file containing font data.", type=cloup.File("rb")
)
@output_option
@fmp_option
def convert_fmp(
    input_file: BinaryIO, output_file: BinaryIO, size: FmpSizeOption, padding: int
) -> None:
    """Convert a fmp file to an editable image file (Default is BMP)."""
    font_size: FmpSize = int(size)

    path = output_file or Path(get_file_name(input_file)).with_suffix(".bmp")

    Fmp.read_fmp(input_file, font_size=font_size).write_image(path, padding=padding)


@convert.command(name="mtx", show_constraints=True)
@cloup.argument(
    "input_file", help="Mtx file containing Manzai text.", type=cloup.File("rb")
)
@output_option
@mtx_options
def convert_mtx(
    input_file: BinaryIO, output_file: BinaryIO, fpd: Path, unicode: Path
) -> None:
    """Convert a mtx file to a XML file."""
    # pylint: disable=possibly-used-before-assignment
    if fpd:
        fpd_data = Fpd.read_fpd(fpd)

    if unicode:
        fpd_data = Fpd.read_unicode(unicode)

    path = output_file or Path(get_file_name(input_file)).with_suffix(".xml")

    Mtx.read_mtx(input_file).write_xml(path, fpd_data)


if __name__ == "__main__":
    app()
