from collections.abc import Generator
from typing import BinaryIO

import numpy as np
import numpy.typing as npt

BITS_PER_PIXEL = 4
BITS_PER_BYTE = 8
PIXELS_PER_BYTE = BITS_PER_BYTE // BITS_PER_PIXEL


def read_graphic(fp: BinaryIO, character_size: int) -> Generator[bytes]:
    while graphic := fp.read(character_size):
        yield graphic


def parse_4bpp_graphic(graphic_data: bytes, graphic_width: int) -> npt.NDArray[np.bool]:
    graphic: list[list[int]] = []

    for row in range(0, len(graphic_data), graphic_width):
        graphic_row: list[int] = []

        for byte in graphic_data[row : row + graphic_width]:
            # Swap byte order as the graphics data is little endian
            lower_nibble, upper_nibble = (byte >> BITS_PER_PIXEL), byte & 0xF
            graphic_row.extend((upper_nibble, lower_nibble))

        graphic.append(graphic_row)

    return np.array(graphic, np.bool)


def write_4bpp_graphic(fp: BinaryIO, graphic: npt.NDArray[np.bool]) -> None:
    for i in range(0, graphic.size, PIXELS_PER_BYTE):
        pixels = graphic[i : i + PIXELS_PER_BYTE]

        # Swap byte order as fmp is little endian
        lower_nubble, upper_nibble = pixels.tolist()
        byte: int = (upper_nibble << BITS_PER_PIXEL) | lower_nubble

        fp.write(byte.to_bytes())
