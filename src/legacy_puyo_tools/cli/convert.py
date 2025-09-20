# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""The cli to convert files used by older Puyo games to an editable format."""

# pyright: reportPossiblyUnboundVariable=false

from pathlib import Path

import cloup

from legacy_puyo_tools.cli.confopts import (
    fmp_option,
    input_argument,
    mtx_options,
    output_option,
)
from legacy_puyo_tools.formats.fmp import Fmp, FmpSize, FmpTableOrientation
from legacy_puyo_tools.formats.fpd import Fpd
from legacy_puyo_tools.formats.mtx import Mtx

table_options = cloup.option_group(
    "Table options",
    cloup.option(
        "--orientation",
        help="The orientation of the character table.",
        default="portrait",
        type=cloup.Choice(["portrait", "landscape"], case_sensitive=False),
        show_default=True,
    ),
)


@cloup.group()
@cloup.version_option()
def app() -> None:
    """A tool to convert files used by older Puyo games to an editable format."""


@app.command(name="fmp")
@input_argument("Fmp file containing font data.")
@output_option
@fmp_option
@table_options
def convert_fmp(
    input_file: Path,
    output_file: Path | None,
    size: FmpSize,
    padding: int,
    orientation: FmpTableOrientation,
) -> None:
    """Convert a fmp file to an editable image file (Default is PNG)."""
    out_path = output_file or Path(input_file.name).with_suffix(".png")

    with input_file.open("rb") as in_fp:
        Fmp.decode(in_fp, font_size=size).write_image(
            padding=padding, orientation=orientation
        ).save(out_path)


@app.command(name="fpd")
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


@app.command(name="mtx", show_constraints=True)
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
