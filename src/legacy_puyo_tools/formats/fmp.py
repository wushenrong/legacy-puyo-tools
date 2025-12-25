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
from typing import BinaryIO

import attrs
from PIL import Image

from legacy_puyo_tools.exceptions import FileFormatError
from legacy_puyo_tools.formats._graphics import (
    PIXELS_PER_BYTE,
    parse_4bpp_graphic,
    parse_graphics_from_image,
    write_4bpp_graphic,
    write_graphics_to_image,
)
from legacy_puyo_tools.formats.base import BaseFileFormat
from legacy_puyo_tools.typing import FmpCharacterGraphic, FmpFontSize, ImageOrientation


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
    font_size: FmpFontSize
    """The width and height of the graphics in pixels, either 8 or 14 pixels."""

    @classmethod
    def decode(cls, fp: BinaryIO, *, font_size: FmpFontSize = 14) -> Fmp:
        """Decode fmp character graphics table from a file-like object.

        Arguments:
            fp:
                A file-like object in binary mode containing a fpd character table.
            font_size:
                The size of the character graphics in pixels, defaults to `14`.

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
            graphics.append(
                FmpCharacterGraphic(parse_4bpp_graphic(graphic, graphic_width))
            )

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
        font_size: FmpFontSize = 14,
        padding: int = 1,
    ) -> Fmp:
        """Write the fmp character graphics table from a Pillow `Image` to fmp.

        Arguments:
            im:
                An `Image` object from the Pillow library, non-black and white images
                will be converted using Pillow's default dithering options.
            font_size:
                The size of the character graphics in pixels, defaults to `14`.
            padding:
                The amount of padding around the characters in pixels, defaults to `1`.

        Returns:
            A fmp character graphics table.
        """
        return cls(
            parse_graphics_from_image(
                im, font_size, font_size, padding, FmpCharacterGraphic
            ),
            font_size,
        )

    def write_image(
        self,
        *,
        padding: int = 1,
        orientation: ImageOrientation = "portrait",
    ) -> Image.Image:
        """Write the fmp character graphics table to a Pillow Image.

        Arguments:
            padding:
                The amount of padding around the characters in pixels, defaults to `1`.
            orientation:
                Orientation of the character table, defaults to `"portrait"`.

        Returns:
            An image object that contains the fmp character graphics table.
        """
        return write_graphics_to_image(
            self.font, self.font_size, self.font_size, padding, orientation
        )
