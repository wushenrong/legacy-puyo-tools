"""A commandline interface for the conversion tools.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from codecs import BOM_UTF16_LE
from pathlib import Path
from typing import BinaryIO

import cloup
from cloup import option, option_group
from cloup.constraints import require_one

from legacy_puyo_tools.exceptions import FileFormatError
from legacy_puyo_tools.fpd import Fpd
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
        "exactly 1 character table must be specified",
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
def create_fpd(input_file: BinaryIO, output_file: BinaryIO | None) -> None:
    """Create a fpd file from a unicode text file."""  # noqa: DOC501
    if input_file.read(2) != BOM_UTF16_LE:
        raise FileFormatError(
            f"{input_file.name} is not a UTF-16 little-endian encoded text file."
        )

    if output_file:
        Fpd.read_unicode(input_file).write_fpd(output_file)
        return

    path = Path(input_file.name).with_suffix(".fpd")

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
    input_file: BinaryIO, output_file: BinaryIO, fpd: Path | None, unicode: Path | None
) -> None:
    """Create a mtx file from a XML file."""
    raise NotImplementedError("Creating MTX files is currently not implemented yet.")


@app.group()
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
        Fpd.read_fpd(input_file).write_unicode(output_file)
        return

    path = Path(input_file.name).with_suffix(".txt")

    Fpd.read_fpd(input_file).write_unicode_to_path(path)


@convert.command(name="mtx", show_constraints=True)
@cloup.argument(
    "input_file", help="Mtx file containing Manzai text.", type=cloup.File("rb")
)
@output_option
@mtx_options
def convert_mtx(
    input_file: BinaryIO,
    output_file: BinaryIO | None,
    fpd: Path,
    unicode: Path,
) -> None:
    """Convert a mtx file to a XML file."""
    if fpd:
        fpd_data = Fpd.read_fpd_from_path(fpd)

    if unicode:
        fpd_data = Fpd.read_unicode_from_path(unicode)

    if output_file:
        Mtx.read_mtx(input_file).write_xml(output_file, fpd_data)  # type: ignore[reportPossiblyUnboundVariable]
        return

    path = Path(input_file.name).with_suffix(".xml")

    Mtx.read_mtx(input_file).write_xml_to_file(path, fpd_data)  # type: ignore[reportPossiblyUnboundVariable]


if __name__ == "__main__":
    app()
