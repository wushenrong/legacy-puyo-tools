# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""The cli to convert files used by older Puyo games to an editable format."""

# pyright: reportPossiblyUnboundVariable=false

from pathlib import Path

import click
import cloup

from legacy_puyo_tools.cli._confopts import (
    fmp_options,
    get_output_path,
    graphics_options,
    input_argument,
    mtx_constraint,
    mtx_options,
    output_option,
    padding_option,
    table_options,
)
from legacy_puyo_tools.formats.fmp import Fmp
from legacy_puyo_tools.formats.fnt import Fnt
from legacy_puyo_tools.formats.fpd import Fpd
from legacy_puyo_tools.formats.mtx import Mtx
from legacy_puyo_tools.typing import (
    FmpFontSize,
    FontFormat,
    ImageOrientation,
    TableFormat,
)


@cloup.group()
@cloup.version_option()
def app() -> None:
    """A tool to convert files used by older Puyo games to an editable format."""


@app.command(name="fmp")
@input_argument("Path to the fmp file containing graphics data.")
@output_option
@fmp_options
@padding_option
@table_options
def convert_fmp(
    input_file: Path,
    output_file: Path | None,
    font_size: FmpFontSize,
    padding: int,
    orientation: ImageOrientation,
) -> None:
    """Extract character graphics from a fmp file to an image.

    Image format defaults to PNG.
    """
    with input_file.open("rb") as in_fp:
        Fmp.decode(in_fp, font_size=font_size).write_image(
            padding=padding, orientation=orientation
        ).save(get_output_path(input_file, output_file, ".png"))


@app.command(name="fnt")
@input_argument("Path to the fnt file containing character and graphics data.")
@output_option
@cloup.option(
    "--extract-graphics",
    help="Extract character graphics if they are available.",
    default=False,
    type=bool,
    show_default=True,
    group=graphics_options,
)
@padding_option
@table_options
def convert_fnt(
    input_file: Path,
    output_file: Path | None,
    extract_graphics: bool,
    padding: int,
    orientation: ImageOrientation,
) -> None:
    """Extract characters from a fnt file to a CSV table.

    Optionally character graphics can also be extract to an image if available.
    Image format defaults to PNG.
    """
    with input_file.open("rb") as in_fp:
        fnt = Fnt.decode(in_fp)

    with get_output_path(input_file, output_file, ".csv").open(
        "w", encoding="utf-8", newline=""
    ) as out_fp:
        fnt.write_csv(out_fp)

    if not extract_graphics:
        return

    if fnt.has_graphics():
        fnt.write_image(padding=padding, orientation=orientation).save(
            get_output_path(input_file, output_file, ".png")
        )
    else:
        click.echo("No graphics found. Not extracting graphics.", err=True)


@app.command(name="fpd")
@input_argument("Path to the fpd file containing character data.")
@output_option
def convert_fpd(input_file: Path, output_file: Path | None) -> None:
    """Extract characters from a fpd file to a CSV table."""
    with (
        input_file.open("rb") as in_fp,
        get_output_path(input_file, output_file, ".csv").open(
            "w", encoding="utf-8", newline=""
        ) as out_fp,
    ):
        Fpd.decode(in_fp).write_csv(out_fp)


@app.command(name="mtx", show_constraints=True)
@input_argument("Path to the mtx file.")
@output_option
@mtx_options
@mtx_constraint
def convert_mtx(
    input_file: Path,
    output_file: Path | None,
    table: Path,
    table_format: TableFormat,
    font_format: FontFormat,
) -> None:
    """Extract text from a mtx file."""
    if table_format == "CSV":
        with table.open("r", encoding="utf-8", newline="") as table_fp:
            if font_format == "FNT":
                font = Fnt.read_csv(table_fp)
            elif font_format == "FPD":
                font = Fpd.read_csv(table_fp)
    else:
        with table.open("rb") as table_fp:
            if table_format == "FNT":
                font = Fnt.decode(table_fp)
            elif table_format == "FPD":
                font = Fpd.decode(table_fp)

    with (
        input_file.open("rb") as in_fp,
        get_output_path(input_file, output_file, ".xml").open("wb") as out_fp,
    ):
        out_fp.write(Mtx.decode(in_fp).write_xml(font))
