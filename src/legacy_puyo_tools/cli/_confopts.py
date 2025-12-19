# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Options that are used by the cli tools."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import cloup
from cloup.constraints import Equal, If, all_or_none, mutually_exclusive


def get_output_path(input_file: Path, output_file: Path | None, extension: str) -> Path:
    return output_file or Path(input_file.name).with_suffix(extension)


def input_argument[T: Callable[..., Any]](help_text: str) -> Callable[[T], T]:
    return cloup.argument(
        "input_file", help=help_text, type=cloup.Path(path_type=Path, dir_okay=False)
    )


output_option = cloup.option(
    "--output",
    "-o",
    "output_file",
    help="Output file. Defaults to the input filename with an appropriate extension.",
    type=cloup.Path(dir_okay=False, writable=True, path_type=Path),
)

graphics_options = cloup.OptionGroup("Graphics Options")
padding_option = graphics_options.option(
    "--padding",
    help="Size of the padding around the graphics.",
    default=1,
    type=cloup.IntRange(0, 4),
    show_default=True,
)

table_options = cloup.option_group(
    "Character Table Options",
    cloup.option(
        "--orientation",
        help="The orientation of the character table.",
        default="portrait",
        type=cloup.Choice(["portrait", "landscape"], case_sensitive=False),
        show_default=True,
    ),
)

fmp_options = cloup.option_group(
    "Fmp Font Options",
    cloup.option(
        "--font-size",
        help="Size of the font.",
        default=14,
        type=cloup.Choice([8, 14], case_sensitive=False),
        show_default=True,
    ),
)

fnt_options = cloup.option_group(
    "Fnt Font Options",
    cloup.option(
        "--fnt-version",
        help="The version of the fnt to create.",
        default="PTE",
        type=cloup.Choice(["PTE", "NDS", "GCIX", "GVRT", "PSP"], case_sensitive=False),
        show_default=True,
    ),
    cloup.option(
        "--fnt-graphic",
        help="Path to the image file to add character graphics.",
        type=cloup.Path(exists=True, dir_okay=False, path_type=Path),
    ),
    cloup.option(
        "--font-height",
        help="The height of the font.",
        default=11,
        type=int,
        show_default=True,
    ),
    cloup.option(
        "--font-width",
        help="The width of the font.",
        default=16,
        type=int,
        show_default=True,
    ),
)

fnt_constraint = cloup.constraint(
    If(
        Equal("fnt_version", "NDS"),
        all_or_none.rephrased(
            help="a character graphic is required",
            error="a character graphic is required",
        ),
        If(
            Equal("fnt_version", "GCIX")
            | Equal("fnt_version", "GVRT")
            | Equal("fnt_version", "PSP"),
            mutually_exclusive,
        ),
    ),
    ["fnt_version", "fnt_graphic"],
)

mtx_options = cloup.option_group(
    "Character Table Options",
    cloup.option(
        "--table",
        help="The file that contains the character table.",
        type=cloup.Path(exists=True, dir_okay=False, path_type=Path),
        required=True,
    ),
    cloup.option(
        "--table-format",
        help="The character table format to use for creation and conversion.",
        default="CSV",
        type=cloup.Choice(["FNT", "FPD", "CSV"], case_sensitive=False),
        show_default=True,
    ),
    cloup.option(
        "--font-format",
        help=(
            "The font format to use for creation and conversion, inferred from "
            "--table-format."
        ),
        type=cloup.Choice(["FNT", "FPD"], case_sensitive=False),
    ),
)

mtx_constraint = cloup.constraint(
    If(
        Equal("table_format", "CSV"),
        all_or_none.rephrased(
            help="a font format is required", error="a font format is required"
        ),
    ),
    ["table_format", "font_format"],
)
