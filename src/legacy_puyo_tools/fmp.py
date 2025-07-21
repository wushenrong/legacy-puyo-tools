"""Fmp conversion tool for older Puyo games.

This module supports the encoding and decoding of the fmp format in tandem with the fpd
format to show characters in Puyo Puyo! 15th Anniversary and Puyo Puyo 7.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Literal

import attrs
import numpy as np

from legacy_puyo_tools.exceptions import FormatError

BITS_PER_PIXEL = 4
BITS_PER_BYTE = 8

# TODO: When upgrading to Python 3.12, add type to the beginning of the alias
FmpSize = Literal[8, 14]
FmpCharacter = np.ndarray[tuple[FmpSize, FmpSize], np.dtype[np.bool]]


@attrs.define
class Fmp:
    font: list[FmpCharacter]
    font_size: FmpSize

    @classmethod
    def decode(cls, data: bytes, font_size: FmpSize = 8) -> Fmp:
        bytes_width = font_size * BITS_PER_PIXEL // BITS_PER_BYTE

        # Accounting for the upper and lower half of the font
        character_size = (bytes_width**2) * 2

        if len(data) % character_size != 0:
            raise FormatError

        graphics: list[FmpCharacter] = []

        for i in range(0, len(data), character_size):
            graphic: list[list[int]] = []

            for j in range(i, i + character_size, bytes_width):
                row: list[int] = []

                for byte in data[j : j + bytes_width]:
                    # Swap byte order as fmp is little endian
                    lower_nibble, upper_nibble = (byte >> 4), byte & 0xF
                    row.extend((upper_nibble, lower_nibble))

                graphic.append(row)

            graphics.append(np.array(graphic, np.bool))

        return cls(graphics, font_size)

    # def write_bmp_to_path(self, path: str | PathLike[str]) -> None:
    #     with Image.new(s) as im:
    #         im.

    # def encode_bmp(self, width: int, padding: int):
    #     height = width // len(self.graphics)
    #     character_size = self.font_width + padding

    #     image_size = (character_size * width, character_size * height)

    #     img = Image.new("1", image_size)

    #     for character in self.graphics:
    #         img.
