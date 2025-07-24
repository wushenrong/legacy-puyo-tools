"""A commandline interface for the conversion tools.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

# pyright: reportPossiblyUnboundVariable=false

from pathlib import Path
from typing import BinaryIO

import cloup
from cloup import option, option_group
from cloup.constraints import require_one

from legacy_puyo_tools.fmp import Fmp, FmpSize
from legacy_puyo_tools.fpd import Fpd
from legacy_puyo_tools.io import get_file_name
from legacy_puyo_tools.mtx import Mtx

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
        type=cloup.Choice([8, 14], case_sensitive=False),
    ),
    option(
        "--padding",
        help="Size of padding around the characters.",
        default=1,
        type=cloup.IntRange(0, 4),
    ),
    option(
        "--width",
        help="Number of characters per column.",
        default=16,
        type=cloup.IntRange(0, min_open=True),
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
    input_file: BinaryIO, output_file: BinaryIO, size: FmpSize, width: int, padding: int
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
    input_file: BinaryIO, output_file: BinaryIO, size: FmpSize, padding: int, width: int
) -> None:
    """Convert a fmp file to an editable image file (Default is BMP)."""
    path = output_file or Path(get_file_name(input_file)).with_suffix(".bmp")

    Fmp.read_fmp(input_file, font_size=size).write_image(
        path, width=width, padding=padding
    )


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
