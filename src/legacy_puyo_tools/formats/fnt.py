# SPDX-FileCopyrightText: 2021 Nick Woronekin
# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Fnt conversion tool for older Puyo games.

This module supports the encoding and decoding of the fnt format to show characters in
Puyo Puyo!! 20th Anniversary.
"""

from __future__ import annotations

import csv
import io
import struct
from collections import OrderedDict
from os import SEEK_END
from typing import BinaryIO, TextIO

import attrs
import numpy as np
from PIL import Image

from legacy_puyo_tools.formats._csv import CSV_TABLE_HEADER, get_csv_reader
from legacy_puyo_tools.formats._graphics import (
    PIXELS_PER_BYTE,
    parse_4bpp_graphic,
    parse_graphics_from_image,
    write_4bpp_graphic,
    write_graphics_to_image,
)
from legacy_puyo_tools.formats.base import (
    BaseCharacterTable,
    FileFormatError,
)
from legacy_puyo_tools.typing import (
    FntCharacterGraphic,
    FntFormatVersion,
    ImageOrientation,
)

FNT_HEADER_FORMAT = "<4sLLL"
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


def _get_fnt_graphics(
    character: FntCharacter, graphic_size: int
) -> FntCharacterGraphic:
    return character.graphic or FntCharacterGraphic(
        np.array([0] * graphic_size, np.bool)
    )


@attrs.define
class FntCharacter:
    graphic: FntCharacterGraphic | None
    width: int


@attrs.define
class Fnt(BaseCharacterTable):
    font: OrderedDict[str, FntCharacter]
    font_height: int
    font_width: int
    graphic_size: int = attrs.field(
        default=attrs.Factory(
            lambda self: self.font_height * self.font_width // PIXELS_PER_BYTE,
            takes_self=True,
        )
    )

    def __getitem__(self, index: int) -> str:
        """Return a character from the fnt character table."""
        return list(self.font)[index]

    def __str__(self) -> str:
        """Return all of the characters in the fnt character table as a string."""
        with io.StringIO() as str_buf:
            for character in self.font:
                str_buf.write(character)

            return str_buf.getvalue()

    @classmethod
    def decode(cls, fp: BinaryIO) -> Fnt:
        if not fp.seekable():
            raise io.UnsupportedOperation(
                "Unable to perform seek operations on the file handler."
            )

        magic_number, font_height, font_width, character_length = struct.unpack(
            FNT_HEADER_FORMAT, fp.read(FNT_HEADER_LENGTH)
        )

        if magic_number != FNT_MAGIC_NUMBER:
            raise FileFormatError(
                "The given magic number shows that the given data is not in the fnt "
                f"format.\nExpected: {FNT_MAGIC_NUMBER}\nActual: {magic_number}"
            )

        graphic_size = font_height * font_width // PIXELS_PER_BYTE
        parse_graphics = False

        if fp.read(FNT_NDS_IDENTIFIER_LENGTH) != FNT_NDS_IDENTIFIER:
            fnt_length = fp.seek(FNT_WII_IDENTIFIER_LENGTH * -1, SEEK_END)

            if fp.read(FNT_WII_IDENTIFIER_LENGTH) not in FNT_WII_IDENTIFIER:
                fnt_length = fp.seek(FNT_PSP_IDENTIFIER_LENGTH * -1, SEEK_END)

                # The fnt might be created by Puyo Text Editor without an identifier
                if fp.read(FNT_PSP_IDENTIFIER_LENGTH) != FNT_PSP_IDENTIFIER:
                    fnt_length = fp.seek(0, SEEK_END)

            if fnt_length != FNT_HEADER_LENGTH + (
                character_length * (FNT_CHARACTER_ENTRY_FORMAT_LENGTH)
            ):
                raise FileFormatError(
                    "The size of the fnt is incorrect based on the fnt version"
                )

            fp.seek(FNT_HEADER_LENGTH)
        else:
            parse_graphics = True

            if fp.seek(0, SEEK_END) != FNT_HEADER_LENGTH + FNT_NDS_HEADER_LENGTH + (
                character_length * (FNT_CHARACTER_ENTRY_FORMAT_LENGTH + graphic_size)
            ):
                raise FileFormatError(
                    "The size of the fnt is incorrect based on the fnt version"
                )

            fp.seek(FNT_HEADER_LENGTH + FNT_NDS_HEADER_LENGTH)

        character_table: OrderedDict[str, FntCharacter] = OrderedDict()

        for _ in range(character_length):
            code_point, width = struct.unpack(
                FNT_CHARACTER_ENTRY_FORMAT, fp.read(FNT_CHARACTER_ENTRY_FORMAT_LENGTH)
            )

            graphic = None

            if parse_graphics:
                graphic = FntCharacterGraphic(
                    parse_4bpp_graphic(fp.read(graphic_size), font_width)
                )

            character_table[chr(code_point)] = FntCharacter(graphic, width)

        return cls(character_table, font_height, font_width)

    def encode(self, fp: BinaryIO, *, version: FntFormatVersion = "PTE") -> None:
        fp.write(
            struct.pack(
                FNT_HEADER_FORMAT,
                FNT_MAGIC_NUMBER,
                self.font_height,
                self.font_width,
                len(self.font),
            )
        )

        write_graphics = False

        if version == "NDS" or (version == "PTE" and self.has_graphics()):
            write_graphics = True
            fp.write(FNT_NDS_IDENTIFIER)

            fp.writelines(
                b"\0" for _ in range(FNT_NDS_HEADER_LENGTH - FNT_NDS_IDENTIFIER_LENGTH)
            )

        for code_point, character in self.font.items():
            fp.write(
                struct.pack(
                    FNT_CHARACTER_ENTRY_FORMAT, ord(code_point), character.width
                )
            )

            if write_graphics:
                write_4bpp_graphic(
                    fp,
                    _get_fnt_graphics(character, self.graphic_size).reshape(-1),
                )

        if version == "PSP":
            fp.write(FNT_PSP_IDENTIFIER)
            return

        encoded_version = version.encode()
        if encoded_version in FNT_WII_IDENTIFIER:
            fp.write(encoded_version)

    def has_graphics(self) -> bool:
        return any(character.graphic for character in self.font.values())

    @classmethod
    def read_csv(
        cls,
        fp: TextIO,
        *,
        font_height: int = 11,
        font_width: int = 16,
    ) -> Fnt:
        if font_width % 2 != 0:
            raise ValueError(
                "The font width of the external font needs to be a multiples of 2."
            )

        character_table: OrderedDict[str, FntCharacter] = OrderedDict()

        for entry in get_csv_reader(fp):
            code_point, width = entry.values()

            character_table[code_point] = FntCharacter(None, int(width, base=16))

        return cls(character_table, font_height, font_width)

    def write_csv(self, fp: TextIO) -> None:
        csv_writer = csv.DictWriter(fp, CSV_TABLE_HEADER)

        csv_writer.writeheader()

        csv_writer.writerows([
            {
                "code_point": code_point,
                "width": hex(character.width),
            }
            for code_point, character in self.font.items()
        ])

    def add_graphics(
        self,
        im: Image.Image,
        *,
        font_height: int = 11,
        font_width: int = 16,
        padding: int = 1,
    ) -> None:
        characters = list(self.font)
        graphics = parse_graphics_from_image(
            im, font_height, font_width, padding, FntCharacterGraphic
        )

        for character, graphic in zip(characters, graphics, strict=True):
            self.font[character].graphic = graphic

    def write_image(
        self,
        *,
        padding: int = 1,
        orientation: ImageOrientation = "portrait",
    ) -> Image.Image:
        font = [
            _get_fnt_graphics(character, self.graphic_size)
            for character in self.font.values()
        ]

        return write_graphics_to_image(
            font, self.font_height, self.font_width, padding, orientation
        )
