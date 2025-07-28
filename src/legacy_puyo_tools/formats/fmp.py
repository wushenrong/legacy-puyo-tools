# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Fmp conversion tool for older Puyo games.

This module supports the encoding and decoding of the fmp format in tandem with the fpd
format to show characters in Puyo Puyo! 15th Anniversary and Puyo Puyo 7.
"""

from __future__ import annotations

from io import BytesIO
from typing import BinaryIO

import attrs
import numpy as np
from PIL import Image

from legacy_puyo_tools.formats._io import get_file_name, write_file
from legacy_puyo_tools.formats._math import find_largest_proper_divisor_pair
from legacy_puyo_tools.formats.base import FileFormatError, Format, FormatError
from legacy_puyo_tools.typing import FmpCharacter, FmpSize, StrPath

FMP_DEFAULT_FONT_SIZE = 14
"""The default character graphics size used by manzais in pixels."""
FMP_DEFAULT_PADDING = 1
"""The default padding around character graphics during conversion in pixels."""
FMP_DEFAULT_MAX_TABLE_WIDTH = 32
"""The default maximum number of characters per row in an image."""

_BITS_PER_PIXEL = 4
_BITS_PER_BYTE = 8


@attrs.define
class Fmp(Format):
    """A fmp character graphics table.

    The fmp stores a bitmap graphic table in which each graphic correspond to a
    character entry in the fpd character table and it is stored right next to each other
    in the file.
    """

    font: list[FmpCharacter]
    """List of character graphics whose indices matches the character it represents in
    the fpd."""
    font_size: FmpSize
    """The width and height of the graphics in pixels, either 8 or 14 pixels."""

    @classmethod
    def read_fmp(
        cls,
        path_or_buf: StrPath | BinaryIO,
        *,
        font_size: FmpSize = FMP_DEFAULT_FONT_SIZE,
    ) -> Fmp:
        """Read and extract character graphics from a fmp file.

        :param path_or_buf: A string path or file-like object in binary mode to a fmp
            encoded file that contains a fmp character table.
        :param font_size: The size of the character graphics in pixels.

        :return: A fmp character graphics table.
        """
        return super()._decode_file(path_or_buf, font_size=font_size)

    @classmethod
    def decode(cls, data: bytes, *, font_size: FmpSize = FMP_DEFAULT_FONT_SIZE) -> Fmp:
        """Decode graphics from a fmp character graphics table from 4bpp to 8bpp.

        :param data: A fpd encoded stream that contains a fmp character graphics table.
        :param font_size: The size of the character graphics in pixels, defaults to
            FMP_DEFAULT_FONT_SIZE.

        :raises FormatError: The size of the fmp does not align to the size of the
            character graphics.

        :return: A fmp character graphics table.
        """
        bytes_width = font_size * _BITS_PER_PIXEL // _BITS_PER_BYTE

        # Accounting for the upper and lower half of the font
        character_size = (bytes_width**2) * 2

        if len(data) % character_size != 0:
            raise FormatError(
                "The size of the fmp does not match the given character graphics size"
            )

        graphics: list[FmpCharacter] = []

        for i in range(0, len(data), character_size):
            graphic: list[list[int]] = []

            for j in range(i, i + character_size, bytes_width):
                row: list[int] = []

                for byte in data[j : j + bytes_width]:
                    # Swap byte order as fmp is little endian
                    lower_nibble, upper_nibble = (byte >> _BITS_PER_PIXEL), byte & 0xF
                    row.extend((upper_nibble, lower_nibble))

                graphic.append(row)

            graphics.append(np.array(graphic, np.bool))

        return cls(graphics, font_size)

    def encode(self) -> bytes:
        """Encode the fmp character graphics table into a 4bpp fmp stream.

        :return: A fmp character graphics table encoded into a byte stream.
        """
        with BytesIO() as bytes_buffer:
            for graphics in self.font:
                graphic = graphics.reshape(-1)

                for i in range(0, graphic.size, _BITS_PER_BYTE // _BITS_PER_PIXEL):
                    pixels = graphic[i : i + _BITS_PER_BYTE // _BITS_PER_PIXEL]

                    # Swap byte order as fmp is little endian
                    lower_nubble, upper_nibble = pixels.tolist()
                    byte: int = (upper_nibble << _BITS_PER_PIXEL) | lower_nubble

                    # TODO: When updating Python to 3.11, remove for to_bytes
                    bytes_buffer.write(byte.to_bytes(1, "little"))

            return bytes_buffer.getvalue()

    def write_fmp(self, path_or_buf: StrPath | BinaryIO) -> None:
        """Write the fmp character graphics table to a fmp encoded file.

        :param path_or_buf: A string path or file-like object in binary mode to write
            the fmp character graphics table.
        """
        write_file(path_or_buf, self.encode())

    @classmethod
    def read_image(
        cls,
        path_or_buf: StrPath | BinaryIO,
        *,
        font_size: FmpSize = FMP_DEFAULT_FONT_SIZE,
        padding: int = FMP_DEFAULT_PADDING,
    ) -> Fmp:
        """Read and convert a character graphics table from an image.

        :param path_or_buf: A string path or file-like object in binary mode to an black
            and white image, preferably from BMP or PNG.
        :param font_size: The size of the character graphics in pixels, defaults to
            FMP_DEFAULT_FONT_SIZE.
        :param padding: The amount of padding around the characters in pixels, defaults
            to FMP_DEFAULT_PADDING.

        :raises FileFormatError: The image is not using a black and white palette.

        :return: A fmp character graphics table.
        """
        with Image.open(path_or_buf) as im:
            try:
                return cls.from_image(im, font_size=font_size, padding=padding)
            except FormatError as e:
                raise FileFormatError(
                    f"{get_file_name(path_or_buf)} is not using a black and white "
                    "palette"
                ) from e

    @classmethod
    def from_image(
        cls,
        im: Image.Image,
        *,
        font_size: FmpSize = FMP_DEFAULT_FONT_SIZE,
        padding: int = FMP_DEFAULT_PADDING,
    ) -> Fmp:
        """Read and convert a character graphics table from a Pillow Image to fmp.

        :param im: An image object from the Pillow library, must be in black and white
            mode.
        :param font_size: The size of the character graphics in pixels, defaults to
            FMP_DEFAULT_FONT_SIZE.
        :param padding: The amount of padding around the characters in pixels, defaults
            to FMP_DEFAULT_PADDING.

        :raises FormatError: The image is not using a black and white palette.
        :raises ValueError: The image does not align to the given size of the character
            graphics and padding padding.

        :return: A fmp character graphics table.
        """
        if im.mode != "1":
            raise FormatError("The image is not in black and white")

        graphic_size = font_size + (padding * 2)

        if im.width % graphic_size != 0 or im.height % graphic_size != 0:
            raise ValueError("The size of the character or padding is incorrect")

        graphics: list[FmpCharacter] = []

        for row in range(im.width // graphic_size):
            for col in range(im.height // graphic_size):
                graphic = im.crop((
                    col * graphic_size + padding,
                    row * graphic_size + padding,
                    (col + 1) * graphic_size - padding,
                    (row + 1) * graphic_size - padding,
                ))

                graphics.append(np.array(graphic, np.bool))

        return cls(graphics, font_size)

    def to_image(
        self,
        *,
        max_width: int = FMP_DEFAULT_MAX_TABLE_WIDTH,
        padding: int = FMP_DEFAULT_PADDING,
    ) -> Image.Image:
        """Encode the fmp character graphics table to a Pillow Image.

        :param max_width: The maximum amount of characters per columns in the image.
            Tries to find the best width to height ratio, defaults to
            FMP_DEFAULT_MAX_TABLE_WIDTH.
        :param padding: The amount of padding around the characters in pixels, defaults
            to FMP_DEFAULT_PADDING.

        :raises ValueError: There is no good width to height ratio below the given max
            width.

        :return: An image object that contains the fmp character graphics table.
        """
        # Find the optimal width and height of the character table by
        # calculating factors to put them into a rectangle or square.
        width, height = find_largest_proper_divisor_pair(
            len(self.font), lambda x: x <= max_width
        )

        if not width or not height:
            raise ValueError(
                "There is no good width to height ratio below the given max width, "
                "increase the max width or pad the fmp with empty characters."
            )

        # Scrolling down is easier than scrolling right
        if width > height:
            width, height = height, width

        graphic_size = self.font_size + (padding * 2)

        buf = Image.new("1", (graphic_size, graphic_size))
        img = Image.new("1", (graphic_size * width, graphic_size * height))

        for col in range(height):
            for row in range(width):
                # TODO: Remove ignore once python-pillow/Pillow#8029 and
                # python-pillow/Pillow#8362 gets resolved and merged
                buf.putdata(  # pyright: ignore[reportUnknownMemberType]
                    # A way that tries to flatten multidimensional arrays without making
                    # additional copies
                    np.pad(self.font[(col * width) + row], padding).reshape(-1)
                )
                img.paste(buf, (row * graphic_size, col * graphic_size))

        return img

    def write_image(
        self,
        path_or_buf: StrPath | BinaryIO,
        *,
        max_width: int = FMP_DEFAULT_MAX_TABLE_WIDTH,
        padding: int = FMP_DEFAULT_PADDING,
    ) -> None:
        """Write the fmp character graphics table to an image.

        :param path_or_buf: A string path or file-like object in binary mode to an
            image. Can be in any image format but preferably BMP or PNG.
        :param max_width: The maximum amount of characters per columns in the image.
            Tries to find the best width to height ratio, defaults to
            FMP_DEFAULT_MAX_TABLE_WIDTH.
        :param padding: The amount of padding around the characters in pixels, defaults
            to FMP_DEFAULT_PADDING.
        """
        self.to_image(max_width=max_width, padding=padding).save(path_or_buf)
