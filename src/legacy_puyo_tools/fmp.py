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
import numpy.typing as npt
from PIL import Image

from legacy_puyo_tools.exceptions import FormatError
from legacy_puyo_tools.io import PathOrFile

BITS_PER_PIXEL = 4
BITS_PER_BYTE = 8

# TODO: When upgrading to Python 3.12, add type to the beginning of aliases
FmpSize = Literal[8, 14]
FmpCharacter = npt.NDArray[np.bool]


@attrs.define
class Fmp:
    font: list[FmpCharacter]
    font_size: FmpSize

    @classmethod
    def decode(cls, data: bytes, *, font_size: FmpSize = 14) -> Fmp:
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

    def to_image(self, width: int = 16, *, padding: int = 1) -> Image.Image:
        num_of_characters = 0

        for character in self.font:
            if np.any(character):
                num_of_characters += 1

        # Add padding to the table so all of the characters gets printed out
        # if the number of characters does not evenly divides into the width
        # Also accounts for the space character that is all 0s
        num_of_characters += width - (num_of_characters % width)

        height = (num_of_characters) // width
        graphic_size = self.font_size + (padding * 2)

        buf = Image.new("1", (graphic_size, graphic_size))
        img = Image.new("1", (graphic_size * width, graphic_size * height))

        end_of_font = False

        for col in range(height):
            for row in range(width):
                character_index = (col * width) + row

                if character_index >= len(self.font):
                    end_of_font = True
                    break

                # TODO: Remove ignore once python-pillow/Pillow#8029 and
                # python-pillow/Pillow#8362 gets resolved and merged
                buf.putdata(  # pyright: ignore[reportUnknownMemberType]
                    np.pad(self.font[character_index], padding).flatten()
                )
                img.paste(buf, (row * graphic_size, col * graphic_size))

            if end_of_font:
                break

        return img

    def write_image(self, path_or_buf: PathOrFile) -> None:
        self.to_image().save(path_or_buf)
