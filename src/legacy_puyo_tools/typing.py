# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Custom primitive types and aliases used by modules in legacy-puyo-tools."""

from typing import Literal, NewType

import numpy as np
import numpy.typing as npt

type ImageOrientation = Literal["portrait", "landscape"]
"""How the image can be orientated."""

type BitmapGraphic = npt.NDArray[np.bool]
"""A 4 bits per pixel (4bpp), black and white, little-endian bitmap that stores the
graphical data of a character. Pixels are stored row by row, in top-to-bottom and
left-to-right order.

This is a numpy type, so use numpy functions and operation to not have performance
determinate.
"""

# Fmp

FmpCharacterGraphic = NewType("FmpCharacterGraphic", BitmapGraphic)

type FmpFontSize = Literal[8, 14]
"""The available font sizes that the fmp format supports in pixels."""

# Fnt

FntCharacterGraphic = NewType("FntCharacterGraphic", BitmapGraphic)

type FntFormatVersion = Literal["PTE", "NDS", "GCIX", "GVRT", "PSP"]
"""The available format versions that the fnt supports.

The PTE version is how the Puyo Text Editor encodes fnt.
"""

# Mtx

type MtxString = list[int]
"""A list of indexes that points to a character in the fpd character table."""

type MtxOffsetSize = Literal[32, 64]
"""The size of the section and string offsets. Either 32 or 64 bits."""
