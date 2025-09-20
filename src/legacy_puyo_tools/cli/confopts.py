# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Options that are used by the cli tools."""

from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

import cloup
from cloup.constraints import require_one

from legacy_puyo_tools.formats.fmp import FMP_DEFAULT_FONT_SIZE, FMP_DEFAULT_PADDING

_T = TypeVar("_T", bound=Callable[..., Any])


def input_argument(help_text: str) -> Callable[[_T], _T]:
    """Return an argument that gets file from a path."""
    return cloup.argument(
        "input_file", help=help_text, type=cloup.Path(path_type=Path, dir_okay=False)
    )


output_option = cloup.option(
    "--output",
    "-o",
    "output_file",
    help="Output file. Defaults to the input filename with an appropriate extension.",
    type=cloup.Path(path_type=Path, dir_okay=False, writable=True),
)

fmp_option = cloup.option_group(
    "Font options",
    cloup.option(
        "--size",
        help="Size of the characters in the font.",
        default=FMP_DEFAULT_FONT_SIZE,
        type=cloup.Choice([8, 14], case_sensitive=False),
        show_default=True,
    ),
    cloup.option(
        "--padding",
        help="Size of the padding around the characters.",
        default=FMP_DEFAULT_PADDING,
        type=cloup.IntRange(0, 4),
        show_default=True,
    ),
)

mtx_options = cloup.option_group(
    "Character table options",
    cloup.option(
        "--fpd",
        help="Use a fpd file as the character table.",
        type=cloup.Path(exists=True, dir_okay=False, path_type=Path),
    ),
    cloup.option(
        "--csv",
        help="Use a CSV file as the character table.",
        type=cloup.Path(exists=True, dir_okay=False, path_type=Path),
    ),
    constraint=require_one.rephrased(
        "exactly 1 character table required for mtx files",
    ),
)
