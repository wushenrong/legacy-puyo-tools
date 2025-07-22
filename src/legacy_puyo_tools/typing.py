"""Type aliases that are used by modules in legacy-puyo-tools.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

import os
import typing

# TODO: When upgrading to Python 3.10, switch union syntax
# TODO: When upgrading to Python 3.12, add type to the beginning of aliases
PathOrFile = typing.Union[str, os.PathLike[str], typing.BinaryIO]
BinaryModes = typing.Literal["rb", "wb"]

MtxString = list[int]
