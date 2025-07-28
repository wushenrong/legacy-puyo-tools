# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Type aliases as containers types, plain objects or literals."""

# TODO: When upgrading to Python 3.12, add type to the beginning of aliases
import os
from typing import Literal, TypeAlias

import numpy as np
import numpy.typing as npt

StrPath: TypeAlias = str | os.PathLike[str]
"""A string like path."""

FmpSize: TypeAlias = Literal[8, 14]
"""The available font sizes for the fmp format in pixels."""

FmpCharacter: TypeAlias = npt.NDArray[np.bool]
"""A fmp character graphic.

A fmp character graphic is a little-endian 4 bits per pixel (4bpp), black and white
bitmap that stores the graphical data of a character in the fpd character table. A `0x0`
and `0x1` encoding an off and on pixel respectively. Pixels are stored row by row, in
top-to-bottom and left-to-right order.

The graphic is stored in a multi-dimensional (usually 2D) numpy array for easier
conversion using Pillow. Remember to use the numpy library instead of the standard
library to not have a performance detriment.
"""

MtxString: TypeAlias = list[int]
