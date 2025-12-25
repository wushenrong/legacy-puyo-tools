# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""The cli to decompress files used by the Nintendo DS and 3DS."""

from pathlib import Path

import cloup

from legacy_puyo_tools.cli._confopts import (
    get_output_path,
    input_argument,
    output_option,
)
from legacy_puyo_tools.compression import lz11


@cloup.group()
@cloup.version_option()
def app() -> None:
    """A tool to decompress files used by the Nintendo DS and 3DS."""


@app.command(name="lz11")
@input_argument("Path to a LZ11 compressed file.")
@output_option
def decompress_lz11(input_file: Path, output_file: Path | None) -> None:
    """Decompress a LZ11 compressed file."""
    with (
        input_file.open("rb") as in_fp,
        get_output_path(input_file, output_file, None).open("wb+") as out_fp,
    ):
        if in_fp.read(4) != lz11.COMP_LZ11_MAGIC_NUMBER:
            in_fp.seek(0)

        lz11.decompress_lz11(in_fp, out_fp)
