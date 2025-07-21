"""Type aliases that are used by modules in legacy-puyo-tools.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

import os
import typing

# TODO: When upgrading to Python 3.12, add type to the beginning of the alias

PathOrFile = str | os.PathLike[str] | typing.BinaryIO
BinaryModes = typing.Literal["rb", "wb"]

MtxString = list[int]
