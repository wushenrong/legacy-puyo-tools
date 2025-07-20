"""Fmp conversion tool for older Puyo games.

This module supports the encoding and decoding of the fmp format in tandem with the fpd
format to show characters in Puyo Puyo! 15th Anniversary and Puyo Puyo 7.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Literal

import attrs

from legacy_puyo_tools.exceptions import FormatError

BITS_PER_PIXEL = 4
BITS_PER_BYTE = 8

# TODO: When upgrading to Python 3.12, add type to the beginning of the alias
FmpCharacter = list[list[int]]


@attrs.define
class Fmp:
    graphics: list[FmpCharacter]
    font_width: Literal[8, 14]

    # TODO: Numpy the image array
    @classmethod
    def decode_fmp(
        cls, data: bytes, font_width: Literal[8, 14] = 8, padding: int = 2
    ) -> Fmp:
        bytes_width = font_width * BITS_PER_PIXEL // BITS_PER_BYTE

        graphics_size = bytes_width**2

        if len(data) % graphics_size != 0:
            raise FormatError

        graphics: list[FmpCharacter] = []

        for i in range(0, len(data), graphics_size):
            graphic: FmpCharacter = []

            for j in range(i, i + graphics_size, bytes_width):
                row: list[int] = []

                for byte in data[j : j + bytes_width]:
                    lower_nibble, upper_nibble = (byte >> 4), byte & 0xF
                    row.extend((upper_nibble, lower_nibble))

                row.extend([0] * padding)
                graphic.append(row)

            graphic.extend([[0] * (bytes_width + padding)] * padding)
            graphics.append(graphic)

        return cls(graphics, font_width)

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
