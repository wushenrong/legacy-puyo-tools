# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Fmp conversion tool for older Puyo games.

This module supports the encoding and decoding of the fmp file format in tandem with the
fpd file format to show characters in Puyo Puyo! 15th Anniversary and Puyo Puyo 7.
"""

from __future__ import annotations

import io
from os import SEEK_END
from typing import BinaryIO, Literal, NewType

import attrs
import numpy as np
from PIL import Image

from legacy_puyo_tools._math import find_medium_divisors
from legacy_puyo_tools.formats.base import BaseFileFormat, FileFormatError
from legacy_puyo_tools.formats.graphic import (
    PIXELS_PER_BYTE,
    BitmapGraphic,
    parse_4bpp_graphic,
    write_4bpp_graphic,
)

FMP_DEFAULT_FONT_SIZE = 14
"""The default character graphics size used by manzais in pixels."""
FMP_DEFAULT_PADDING = 1
"""The default padding around character graphics during conversion in pixels."""

type FmpSize = Literal[8, 14]
"""The available font sizes for the fmp format in pixels."""

FmpCharacterGraphic = NewType("FmpCharacterGraphic", BitmapGraphic)
"""A fmp character graphic is a little-endian 4 bits per pixel (4bpp), black and white
bitmap that stores the graphical data of a character in the fpd character table. A `0x0`
and `0x1` encoding an off and on pixel respectively. Pixels are stored row by row, in
top-to-bottom and left-to-right order.
"""

type FmpTableOrientation = Literal["portrait", "landscape"]
"""How the fmp character table can be orientated."""


@attrs.define
class Fmp(BaseFileFormat):
    """A fmp character graphics table.

    The fmp stores a bitmap graphic table in which each graphic correspond to a
    character entry in the fpd character table and it is stored right next to each other
    in the file.
    """

    font: list[FmpCharacterGraphic]
    """List of character graphics whose indices matches the character it represents in
    the fpd."""
    font_size: FmpSize
    """The width and height of the graphics in pixels, either 8 or 14 pixels."""

    @classmethod
    def decode(cls, fp: BinaryIO, *, font_size: FmpSize = FMP_DEFAULT_FONT_SIZE) -> Fmp:
        """Decode fmp character graphics table from a file-like object.

        Arguments:
            fp:
                A file-like object in binary mode containing a fpd character table.
            font_size:
                The size of the character graphics in pixels, defaults to
                `FMP_DEFAULT_FONT_SIZE`.

        Raises:
            io.UnsupportedOperation:
                The file handler does not support seek operations.
            FileFormatError:
                The size of the fmp is not correct for the given font size.

        Returns:
            A fmp character graphics table.
        """
        if not fp.seekable():
            raise io.UnsupportedOperation(
                "Unable to perform seek operations on the file handler."
            )

        graphic_width = font_size // PIXELS_PER_BYTE

        # Accounting for the upper and lower half of the font
        graphic_size = graphic_width**2 * 2

        if fp.seek(0, SEEK_END) % graphic_size != 0:
            raise FileFormatError(
                "The size of the fmp is incorrect for the given font size."
            )

        fp.seek(0)

        graphics: list[FmpCharacterGraphic] = []

        while graphic := fp.read(graphic_size):
            FmpCharacterGraphic(parse_4bpp_graphic(graphic, graphic_width))

        return cls(graphics, font_size)

    def encode(self, fp: BinaryIO) -> None:
        """Encode the fmp character graphics table to a file-like object.

        Arguments:
            fp: The file-like object in binary mode that fmp character graphics table
                will be encoded to.
        """
        for graphic in self.font:
            write_4bpp_graphic(fp, graphic.reshape(-1))

    @classmethod
    def read_image(
        cls,
        im: Image.Image,
        *,
        font_size: FmpSize = FMP_DEFAULT_FONT_SIZE,
        padding: int = FMP_DEFAULT_PADDING,
    ) -> Fmp:
        """Write the fmp character graphics table from a Pillow `Image` to fmp.

        Arguments:
            im:
                An `Image` object from the Pillow library, non-black and white images
                will be converted using Pillow's default dithering options.
            font_size:
                The size of the character graphics in pixels, defaults to
                `FMP_DEFAULT_FONT_SIZE`.
            padding:
                The amount of padding around the characters in pixels, defaults to
                `FMP_DEFAULT_PADDING`.

        Raises:
            ValueError:
                The image does not align to the given size of the character graphics or
                padding.

        Returns:
            A fmp character graphics table.
        """
        if im.mode != "1":
            im = im.convert("1", dither=Image.Dither.NONE)

        graphic_size = font_size + (padding * 2)

        wd, wr = divmod(im.width, graphic_size)
        hd, hr = divmod(im.height, graphic_size)

        if wr != 0 or hr != 0:
            raise ValueError("The size of the character or padding is incorrect")

        graphics: list[FmpCharacterGraphic] = []

        for row in range(hd):
            for col in range(wd):
                graphic = im.crop((
                    col * graphic_size + padding,
                    row * graphic_size + padding,
                    (col + 1) * graphic_size - padding,
                    (row + 1) * graphic_size - padding,
                ))

                graphics.append(FmpCharacterGraphic(np.array(graphic, np.bool)))

        return cls(graphics, font_size)

    def write_image(
        self,
        *,
        padding: int = FMP_DEFAULT_PADDING,
        orientation: FmpTableOrientation = "portrait",
    ) -> Image.Image:
        """Write the fmp character graphics table to a Pillow Image.

        Arguments:
            padding:
                The amount of padding around the characters in pixels, defaults to
                `FMP_DEFAULT_PADDING`.
            orientation:
                Orientation of the character table, defaults to `"portrait"`.

        Returns:
            An image object that contains the fmp character graphics table.
        """
        # Find the optimal width and height of the character table by calculating the
        # first factors whose ratio is equal to or close to 1
        # So the character table is arranged into a square or rectangle.
        width, height = find_medium_divisors(len(self.font))

        if (orientation == "portrait" and width > height) or (
            orientation == "landscape" and width < height
        ):
            width, height = height, width

        graphic_size = self.font_size + (padding * 2)

        buf = Image.new("1", (graphic_size, graphic_size))
        img = Image.new("1", (graphic_size * width, graphic_size * height))

        for row in range(height):
            for col in range(width):
                # A way that tries to flatten multidimensional arrays without making
                # additional copies
                buf.putdata(np.pad(self.font[(row * width) + col], padding).reshape(-1))
                img.paste(buf, (col * graphic_size, row * graphic_size))

        return img
