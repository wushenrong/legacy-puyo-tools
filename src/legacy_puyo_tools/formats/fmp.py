"""Fmp conversion tool for older Puyo games.

This module supports the encoding and decoding of the fmp format in tandem with the fpd
format to show characters in Puyo Puyo! 15th Anniversary and Puyo Puyo 7.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from io import BytesIO
from typing import Literal

import attrs
import numpy as np
import numpy.typing as npt
from PIL import Image

from legacy_puyo_tools.formats._io import PathOrFile, get_file_name, write_file
from legacy_puyo_tools.formats._math import find_largest_proper_divisor_pair
from legacy_puyo_tools.formats.base import FileFormatError, Format, FormatError

FMP_DEFAULT_FONT_SIZE = 14
FMP_DEFAULT_PADDING = 1
FMP_DEFAULT_MAX_TABLE_WIDTH = 32

BITS_PER_PIXEL = 4
BITS_PER_BYTE = 8

# TODO: When upgrading to Python 3.12, add type to the beginning of aliases
FmpSize = Literal[8, 14]
"""The available font sizes for the fmp format: 8px or 14px."""

FmpCharacter = npt.NDArray[np.bool]
"""A fmp character graphic.

A fmp character graphic is a little-endian 4 bits per pixel (4bpp), black and white
bitmap that stores the graphical data of a character in the fpd character table. A `0x0`
and `0x1` encoding an off and on pixel respectively. Pixels are stored row by row, in
top-to-bottom and left-to-right order.

The graphic is stored in a multi-dimensional (usually 2D) numpy array for easier
conversion using Pillow. Remember to use the numpy library instead of the standard
library to not have a performance detriment.
"""


@attrs.define
class Fmp(Format):
    """A fmp character graphics table.

    The fmp stores a bitmap graphic table in which each graphic correspond to a
    character entry in the fpd character table and it is stored right next to each other
    in the file.

    Attributes:
        font:
            List of character graphics whose indices matches the character it represents
            in the fpd.
        font_size:
            The width and height of the graphics in pixels, either 8 or 14 pixels.
    """

    font: list[FmpCharacter]
    font_size: FmpSize

    @classmethod
    def read_fmp(
        cls, path_or_buf: PathOrFile, *, font_size: FmpSize = FMP_DEFAULT_FONT_SIZE
    ) -> Fmp:
        """Read and extract character graphics from a fmp file.

        Args:
            path_or_buf:
                A path or file-like object in binary mode to a fmp encoded file that
                contains a fmp character table.
            font_size:
                The size of the character graphics in pixels. Defaults to
                FMP_DEFAULT_FONT_SIZE.

        Returns:
            A fmp character graphics table.
        """
        return super()._decode_file(path_or_buf, font_size=font_size)

    @classmethod
    def decode(cls, data: bytes, *, font_size: FmpSize = FMP_DEFAULT_FONT_SIZE) -> Fmp:
        """Decode graphics from a fmp character graphics table from 4bpp to 8bpp.

        Args:
            data:
                A fpd encoded stream that contains a fmp character graphics table.
            font_size:
                The size of the character graphics in pixels. Defaults to
                FMP_DEFAULT_FONT_SIZE.

        Raises:
            FormatError:
                The size of the fmp does not align to the size of the character
                graphics.

        Returns:
            A fmp character graphics table.
        """
        bytes_width = font_size * BITS_PER_PIXEL // BITS_PER_BYTE

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
                    lower_nibble, upper_nibble = (byte >> BITS_PER_PIXEL), byte & 0xF
                    row.extend((upper_nibble, lower_nibble))

                graphic.append(row)

            graphics.append(np.array(graphic, np.bool))

        return cls(graphics, font_size)

    def encode(self) -> bytes:
        """Encode the fmp character graphics table into a 4bpp fmp stream.

        Returns:
            A fmp character graphics table encoded into a byte stream.
        """
        with BytesIO() as bytes_buffer:
            for graphics in self.font:
                graphic = graphics.reshape(-1)

                for i in range(0, graphic.size, BITS_PER_BYTE // BITS_PER_PIXEL):
                    pixels = graphic[i : i + BITS_PER_BYTE // BITS_PER_PIXEL]

                    # Swap byte order as fmp is little endian
                    lower_nubble, upper_nibble = pixels.tolist()
                    byte: int = (upper_nibble << BITS_PER_PIXEL) | lower_nubble

                    # TODO: When updating Python to 3.11, remove for to_bytes
                    bytes_buffer.write(byte.to_bytes(1, "little"))

            return bytes_buffer.getvalue()

    def write_fmp(self, path_or_buf: PathOrFile) -> None:
        """Write the fmp character graphics table to a fmp encoded file.

        Arguments:
            path_or_buf:
                A path or file-like object in binary mode to write the fmp
                character graphics table.
        """
        write_file(path_or_buf, self.encode())

    @classmethod
    def read_image(
        cls,
        path_or_buf: PathOrFile,
        *,
        font_size: FmpSize = FMP_DEFAULT_FONT_SIZE,
        padding: int = FMP_DEFAULT_PADDING,
    ) -> Fmp:
        """Reads and convert a character graphics table from an image.

        Args:
            path_or_buf:
                A path or file-like object in binary mode to an black and white image,
                preferably from BMP or PNG.
            font_size:
                The size of the character graphics in pixels. Defaults to
                FMP_DEFAULT_FONT_SIZE.
            padding:
                The amount of padding around the characters in pixels. Defaults to
                FMP_DEFAULT_PADDING.

        Raises:
            FileFormatError:
                The image is not in or saved as a black and white.

        Returns:
            A fmp character graphics table.
        """
        with Image.open(path_or_buf) as im:
            try:
                return cls.from_image(im, font_size=font_size, padding=padding)
            except FormatError as e:
                raise FileFormatError(
                    f"{get_file_name(path_or_buf)} is not in or saved as a black and "
                    "white image"
                ) from e

    @classmethod
    def from_image(
        cls,
        im: Image.Image,
        *,
        font_size: FmpSize = FMP_DEFAULT_FONT_SIZE,
        padding: int = FMP_DEFAULT_PADDING,
    ) -> Fmp:
        """Reads and convert a character graphics table from a Pillow Image to fmp.

        Args:
            im:
                An image object from the Pillow library, must be in black and white
                mode.
            font_size:
                The size of the character graphics in pixels. Defaults to
                FMP_DEFAULT_FONT_SIZE.
            padding:
                The amount of padding around the characters in pixels. Defaults to
                FMP_DEFAULT_PADDING.

        Raises:
            FormatError:
                The image is not in black and white.
            ValueError:
                The image does not align to the given size of the character graphics and
                padding padding.

        Returns:
            A fmp character graphics table.
        """
        if im.mode != "1":
            raise FormatError("The image is not in black and white")

        graphic_size = font_size + (padding * 2)

        if im.width % graphic_size != 0 or im.height % graphic_size != 0:
            raise ValueError("The size of the character or padding is incorrect")

        return cls(
            [
                np.array(
                    im.crop((
                        row * graphic_size + padding,
                        col * graphic_size + padding,
                        (row + 1) * graphic_size - padding,
                        (col + 1) * graphic_size - padding,
                    )),
                    np.bool,
                )
                for col in range(im.height // graphic_size)
                for row in range(im.width // graphic_size)
            ],
            font_size,
        )

    def to_image(
        self,
        *,
        max_width: int = FMP_DEFAULT_MAX_TABLE_WIDTH,
        padding: int = FMP_DEFAULT_PADDING,
    ) -> Image.Image:
        """Encode the fmp character graphics table to a Pillow Image.

        Args:
            max_width:
                The maximum amount of characters per columns in the image. Tries to find
                the best width to height ratio.
                Defaults to FMP_DEFAULT_MAX_TABLE_WIDTH.
            padding:
                The amount of padding around the characters in pixels. Defaults to
                FMP_DEFAULT_PADDING.

        Raises:
            ValueError:
                There is no good width to height ratio below the given max width.

        Returns:
            An image object that contains the fmp character graphics table.
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
        path_or_buf: PathOrFile,
        *,
        max_width: int = FMP_DEFAULT_MAX_TABLE_WIDTH,
        padding: int = FMP_DEFAULT_PADDING,
    ) -> None:
        """Write the fmp character graphics table to an image.

        Args:
            path_or_buf:
                A path or file-like object in binary mode to an image. Can be in any
                image format but preferably BMP or PNG.
            max_width:
                The maximum amount of characters per columns in the image. Tries to find
                the best width to height ratio.
                Defaults to FMP_DEFAULT_MAX_TABLE_WIDTH.
            padding:
                The amount of padding around the characters in pixels. Defaults to
                FMP_DEFAULT_PADDING.
        """
        self.to_image(max_width=max_width, padding=padding).save(path_or_buf)
