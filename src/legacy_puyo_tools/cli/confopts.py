# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Options that are used by the cli tools."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import cloup


def input_argument[T: Callable[..., Any]](help_text: str) -> Callable[[T], T]:
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
        default=14,
        type=cloup.Choice([8, 14], case_sensitive=False),
        show_default=True,
    ),
    cloup.option(
        "--padding",
        help="Size of the padding around the characters.",
        default=1,
        type=cloup.IntRange(0, 4),
        show_default=True,
    ),
)

mtx_options = cloup.option_group(
    "Character table options",
    cloup.option(
        "--font-format",
        help="The font format to use to covert mtx.",
        type=cloup.Path(exists=True, dir_okay=False, path_type=Path),
    ),
    cloup.option(
        "--table-format",
        help="Use a CSV file as the character table.",
        type=cloup.Path(exists=True, dir_okay=False, path_type=Path),
    ),
)
