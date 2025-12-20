# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Functions to convert font graphics to and from the fmp and fnt formats."""

from collections.abc import Callable, Sequence
from typing import BinaryIO

import numpy as np
from PIL import Image

from legacy_puyo_tools._math import find_medium_divisors
from legacy_puyo_tools.typing import BitmapGraphic, ImageOrientation

BITS_PER_PIXEL = 4
BITS_PER_BYTE = 8
PIXELS_PER_BYTE = BITS_PER_BYTE // BITS_PER_PIXEL


def parse_4bpp_graphic(graphic_data: bytes, graphic_width: int) -> BitmapGraphic:
    graphic: list[list[int]] = []

    for row in range(0, len(graphic_data), graphic_width):
        graphic_row: list[int] = []

        for byte in graphic_data[row : row + graphic_width]:
            # Swap byte order as the graphics data is little endian
            lower_nibble, upper_nibble = (byte >> BITS_PER_PIXEL), byte & 0xF
            graphic_row.extend((upper_nibble, lower_nibble))

        graphic.append(graphic_row)

    return np.array(graphic, dtype=bool)


def write_4bpp_graphic(fp: BinaryIO, graphic: BitmapGraphic) -> None:
    for i in range(0, graphic.size, PIXELS_PER_BYTE):
        pixels = graphic[i : i + PIXELS_PER_BYTE]

        # Swap byte order as fmp is little endian
        lower_nubble, upper_nibble = pixels.tolist()
        byte: int = (upper_nibble << BITS_PER_PIXEL) | lower_nubble

        fp.write(byte.to_bytes())


def parse_graphics_from_image[T: BitmapGraphic](
    im: Image.Image,
    font_height: int,
    font_width: int,
    padding: int,
    cast: Callable[[BitmapGraphic], T],
) -> list[T]:
    if im.mode != "1":
        im = im.convert("1", dither=Image.Dither.NONE)

    graphic_height = font_height + (padding * 2)
    graphic_width = font_width + (padding * 2)

    hd, hr = divmod(im.height, graphic_height)
    wd, wr = divmod(im.width, graphic_width)

    if hr != 0 or wr != 0:
        raise ValueError(
            "The size of the character or padding is incorrect for the given image."
        )

    return [
        cast(
            np.array(
                im.crop((
                    col * graphic_width + padding,
                    row * graphic_height + padding,
                    (col + 1) * graphic_width - padding,
                    (row + 1) * graphic_height - padding,
                )),
                dtype=bool,
            )
        )
        for row in range(hd)
        for col in range(wd)
    ]


def write_graphics_to_image(
    font: Sequence[BitmapGraphic],
    font_height: int,
    font_width: int,
    padding: int,
    orientation: ImageOrientation,
) -> Image.Image:
    # Find the optimal width and height of the character table by calculating the
    # first factors whose ratio is equal to or close to 1
    # So the character table is arranged into a square or rectangle.
    width, height = find_medium_divisors(len(font))

    if (orientation == "portrait" and width > height) or (
        orientation == "landscape" and width < height
    ):
        width, height = height, width

    graphic_height = font_height + (padding * 2)
    graphic_width = font_width + (padding * 2)

    buffer = Image.new("1", (graphic_width, graphic_height))
    image = Image.new("1", (graphic_width * width, graphic_height * height))

    for row in range(height):
        for col in range(width):
            # A way that tries to flatten multidimensional arrays without making
            # additional copies
            buffer.putdata(np.pad(font[(row * width) + col], padding).reshape(-1))
            image.paste(buffer, (col * graphic_width, row * graphic_height))

    return image
