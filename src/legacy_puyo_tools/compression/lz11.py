# SPDX-FileCopyrightText: Barubary
# SPDX-FileCopyrightText: magical
# SPDX-FileCopyrightText: 2020 Nick Woronekin
# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""LZ11, LZSS-based compression algorithm used by Nintendo on the DS and 3DS."""

import io
from os import SEEK_END
from typing import BinaryIO

from legacy_puyo_tools.exceptions import DecompressionError

_BITS_IN_BYTES = 8

DECOMPRESSION_SIZE_ENDIAN = "little"

LZ11_MAGIC_NUMBER = b"\x11"
COMP_LZ11_MAGIC_NUMBER = b"COMP"


def decompress_lz11(in_fp: BinaryIO, out_fp: BinaryIO) -> None:
    """Decompress a LZ11 compressed file.

    Args:
        in_fp:
            The file handler of the LZ11 compressed file.
        out_fp:
            The file handler of the outgoing uncompressed data stream.

    Raises:
        io.UnsupportedOperation:
            Unable to perform seek or read operations on the file handlers.
        DecompressionError:
            The input file is not a LZ11 compressed file.
        DecompressionError:
            The decompressed file size is not the same as the expected file size.
    """
    if not in_fp.seekable() or not out_fp.readable():
        raise io.UnsupportedOperation(
            "Unable to perform seek or read operations on the file handlers."
        )

    if in_fp.read(1) != LZ11_MAGIC_NUMBER:
        raise DecompressionError("Not a LZ11 compressed data stream.", "LZ11")

    decompressed_size_indicator = int.from_bytes(
        in_fp.read(3), DECOMPRESSION_SIZE_ENDIAN
    )

    decompressed_size = (
        decompressed_size_indicator
        if decompressed_size_indicator != 0
        else int.from_bytes(in_fp.read(4), DECOMPRESSION_SIZE_ENDIAN)
    )

    def read_byte() -> int:
        return int.from_bytes(in_fp.read(1))

    while out_fp.tell() < decompressed_size:
        flag = read_byte()

        for _ in range(_BITS_IN_BYTES):
            # Not compressed
            if flag & (1 << 7) == 0:
                out_fp.write(in_fp.read(1))
            # Compressed
            else:
                byte = read_byte()
                indicator = byte >> 4

                match indicator:
                    case 0:
                        # 8 bit count, 12 bit disp
                        # indicator is 0, don't need to mask b
                        count = byte << 4
                        byte = read_byte()
                        count += byte >> 4
                        count += 0x11
                    case 1:
                        # 16 bit count, 12 bit disp
                        count = ((byte & 0xF) << 12) + (read_byte() << 4)
                        byte = read_byte()
                        count += byte >> 4
                        count += 0x111
                    case _:
                        # indicator is count (4 bits), 12 bit disp
                        count = indicator
                        count += 1

                disp = ((byte & 0xF) << 8) + read_byte()
                disp += 1

                # Needs a for loop to account that there are no bytes are written at the
                # beginning
                for _ in range(count):
                    out_fp.seek(-disp, SEEK_END)
                    repeat_byte = out_fp.read(1)
                    out_fp.seek(0, SEEK_END)
                    out_fp.write(repeat_byte)

            if out_fp.tell() >= decompressed_size:
                break

            flag <<= 1

    if out_fp.tell() != decompressed_size:
        raise DecompressionError(
            "Decompressed size does not match the expected size.\n"
            f"Expected: {decompressed_size}\nActual: {out_fp.tell()}",
            "LZ11",
        )
