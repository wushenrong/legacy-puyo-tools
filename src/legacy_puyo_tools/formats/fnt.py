# SPDX-FileCopyrightText: 2021 Nick Woronekin
# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Fnt conversion tool for older Puyo games.

This module supports the encoding and decoding of the fnt format to show characters in
Puyo Puyo!! 20th Anniversary.
"""

from __future__ import annotations

import io
import struct
from collections import OrderedDict
from os import SEEK_END
from typing import BinaryIO

import attrs
import numpy as np
import numpy.typing as npt

from legacy_puyo_tools.formats._graphic import PIXELS_PER_BYTE, parse_4bpp_graphic
from legacy_puyo_tools.formats.base import BaseFileFormat, FileFormatError

FNT_HEADER_FORMAT = "<4sLLLL"
FNT_MAGIC_NUMBER = b"FNT\0"
FNT_MAGIC_NUMBER_LENGTH = 4
FNT_FONT_WIDTH_WORD_SIZE = 4
FNT_FONT_HEIGHT_WORD_SIZE = 4
FNT_CHARACTER_LENGTH_WORD_SIZE = 4
FNT_HEADER_LENGTH = (
    FNT_MAGIC_NUMBER_LENGTH
    + FNT_FONT_WIDTH_WORD_SIZE
    + FNT_FONT_HEIGHT_WORD_SIZE
    + FNT_CHARACTER_LENGTH_WORD_SIZE
)

FNT_CHARACTER_ENTRY_FORMAT = "<HH"
FNT_CHARACTER_WORD_SIZE = 2
FNT_CHARACTER_WIDTH_WORD_SIZE = 2
FNT_CHARACTER_ENTRY_FORMAT_LENGTH = (
    FNT_CHARACTER_WORD_SIZE + FNT_CHARACTER_WIDTH_WORD_SIZE
)

FNT_NDS_IDENTIFIER = b"\xe0\x03\xff\x7f\xc6\x18"
FNT_NDS_IDENTIFIER_LENGTH = 6
FNT_NDS_HEADER_LENGTH = 32

FNT_WII_IDENTIFIER = [b"GCIX", b"GVRT"]
FNT_WII_IDENTIFIER_LENGTH = 4

FNT_PSP_IDENTIFIER = b"MIG.00.1PSP"
FNT_PSP_IDENTIFIER_LENGTH = 11


@attrs.define
class FntCharacter:
    image: npt.NDArray[np.bool] | None
    width: int


type FntCharacterTable = OrderedDict[str, FntCharacter]


@attrs.define
class Fnt(BaseFileFormat):
    font: FntCharacterTable
    font_height: int
    font_width: int

    @classmethod
    def decode(cls, fp: BinaryIO) -> Fnt:
        if not fp.seekable():
            raise io.UnsupportedOperation(
                "Unable to perform seek operations on file handler."
            )

        magic_number, font_height, font_width, character_length = struct.unpack(
            FNT_HEADER_FORMAT, fp.read(FNT_HEADER_LENGTH)
        )

        if magic_number != FNT_MAGIC_NUMBER:
            raise FileFormatError(
                "The given magic number shows that the given data is not in the fnt "
                f"format.\nExpected: {FNT_MAGIC_NUMBER}\nActual: {magic_number}"
            )

        graphic_size = font_height * font_width / PIXELS_PER_BYTE
        parse_images = False

        if fp.read(FNT_NDS_IDENTIFIER_LENGTH) != FNT_NDS_IDENTIFIER:
            fnt_length = fp.seek(FNT_WII_IDENTIFIER_LENGTH * -1, SEEK_END)

            if fp.read(FNT_WII_IDENTIFIER_LENGTH) not in FNT_WII_IDENTIFIER:
                fnt_length = fp.seek(FNT_PSP_IDENTIFIER_LENGTH * -1, SEEK_END)

                if fp.read(FNT_PSP_IDENTIFIER_LENGTH) != FNT_PSP_IDENTIFIER:
                    raise FileFormatError()

            if fnt_length != FNT_HEADER_LENGTH + (
                character_length * (FNT_CHARACTER_ENTRY_FORMAT_LENGTH)
            ):
                raise FileFormatError()

            fp.seek(FNT_HEADER_LENGTH)
        else:
            parse_images = True

            if fp.seek(0, SEEK_END) != FNT_HEADER_LENGTH + FNT_NDS_HEADER_LENGTH + (
                character_length * (FNT_CHARACTER_ENTRY_FORMAT_LENGTH + graphic_size)
            ):
                raise FileFormatError()
            fp.seek(FNT_HEADER_LENGTH + FNT_NDS_HEADER_LENGTH)

        character_table: FntCharacterTable = OrderedDict()

        for _ in range(character_length):
            code_point, width = struct.unpack(
                FNT_CHARACTER_ENTRY_FORMAT, fp.read(FNT_CHARACTER_ENTRY_FORMAT_LENGTH)
            )

            graphic = None

            if parse_images:
                graphic = parse_4bpp_graphic(fp.read(graphic_size), font_width)

            character_table[chr(code_point)] = FntCharacter(graphic, width)

        return cls(character_table, font_height, font_width)

    def encode(self, fp: BinaryIO) -> None: ...
