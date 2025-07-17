"""A commandline interface for the conversion tools.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from codecs import BOM_UTF16_LE
from pathlib import Path
from typing import BinaryIO

import cloup
from cloup import option, option_group
from cloup.constraints import require_one

from legacy_puyo_tools.exceptions import ArgumentError, FileFormatError
from legacy_puyo_tools.fpd import Fpd
from legacy_puyo_tools.mtx import Mtx

output_option = option(
    "--output",
    "-o",
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
        "exactly 1 character table must be specified",
    ),
)


@cloup.group()
@cloup.version_option()
def main() -> None:
    """A conversion tool for files used by older Puyo games."""


@main.group()
def create() -> None:
    """Create files to used by older Puyo games."""


@create.command(name="fpd")
@cloup.argument(
    "input_file",
    help="Unicode text file encoded in UTF-16 little-endian.",
    type=cloup.File("rb"),
)
@output_option
def create_fpd(input_file: BinaryIO, output: BinaryIO | None) -> None:
    """Create a fpd file from a unicode text file."""
    if input_file.read(2) != BOM_UTF16_LE:
        raise FileFormatError(
            f"{input_file.name} is not a UTF-16 little-endian encoded text file."
        )

    if output:
        Fpd.read_unicode(input_file).write_fpd(output)
        return

    path = Path(input_file.name).with_suffix("")

    if path.suffix != ".fpd":
        path = path.with_suffix(".fpd")

    Fpd.read_unicode(input_file).write_fpd_to_path(path)


@create.command(name="mtx", show_constraints=True)
@cloup.argument(
    "input_file",
    help="XML file that contains markup text or dialog.",
    type=cloup.File("rb"),
)
@output_option
@mtx_options
def create_mtx(
    input_file: BinaryIO, output: BinaryIO, fpd: Path | None, unicode: Path | None
) -> None:
    """Create a mtx file from a XML file."""
    raise NotImplementedError("Creating MTX files is currently not implemented yet.")


@main.group()
def convert() -> None:
    """Convert files used by older Puyo games to an editable format."""


@convert.command(name="fpd")
@cloup.argument(
    "input_file", help="Fpd file containing character data.", type=cloup.File("rb")
)
@output_option
def convert_fpd(input_file: BinaryIO, output_file: BinaryIO | None) -> None:
    """Convert a fpd file to a UTF-16 little-endian unicode text file."""
    if output_file:
        output_file.write(BOM_UTF16_LE)
        Fpd.read_fpd(input_file).write_fpd(output_file)
        return

    path = Path(input_file.name).with_suffix("")

    if path.suffix != ".fpd":
        path = path.with_suffix(".fpd")

    Fpd.read_fpd(input_file).write_unicode_to_path(path)


@convert.command(name="mtx", show_constraints=True)
@cloup.argument(
    "input_file", help="Mtx file containing Manzai text.", type=cloup.File("rb")
)
@output_option
@mtx_options
def convert_mtx(
    input_file: BinaryIO,
    output: BinaryIO | None,
    fpd: Path | None,
    unicode: Path | None,
) -> None:
    """Convert a mtx file to a XML file."""
    if fpd:
        fpd_data = Fpd.read_fpd_from_path(fpd)
    elif unicode:
        fpd_data = Fpd.read_unicode_from_path(unicode)
    else:
        raise ArgumentError(
            "You must specify a character table using --fpd or --unicode."
        )

    if output:
        Mtx.read_mtx(input_file).write_xml(output, fpd_data)
        return

    path = Path(input_file.name).with_suffix("")

    if path.suffix != ".xml":
        path = path.with_suffix(".xml")

    Mtx.read_mtx(input_file).write_xml_to_file(path, fpd_data)


if __name__ == "__main__":
    main()
