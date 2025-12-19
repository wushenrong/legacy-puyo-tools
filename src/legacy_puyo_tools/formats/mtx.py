# SPDX-FileCopyrightText: 2021 Nick Woronekin
# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Manzai text conversion tool for older Puyo Puyo games.

This module converts mtx files to and from XML for modding Puyo games. Currently
supports Puyo Puyo 7 and might support Puyo Puyo! 15th Anniversary.

:::{todo} Complete full support for Puyo Puyo 7, tutorials and voiced manzais.
:::

:::{todo} Complete documentation of mtx.
:::
"""

from __future__ import annotations

import io
from io import StringIO
from itertools import pairwise
from os import SEEK_END
from typing import BinaryIO

import attrs
from lxml import etree

from legacy_puyo_tools.formats.base import (
    BaseCharacterTable,
    BaseFileFormat,
    FileFormatError,
)
from legacy_puyo_tools.typing import MtxOffsetSize, MtxString

MTX_ENDIAN = "little"
MTX_LENGTH_WORD_SIZE = 4
MTX_CHARACTER_WORD_SIZE = 2

MTX32_IDENTIFIER = 8
MTX32_IDENTIFIER_WORD_SIZE = 4
MTX32_OFFSET_WORD_SIZE = 4

MTX64_IDENTIFIER = 16
MTX64_IDENTIFIER_WORD_SIZE = 8
MTX64_OFFSET_WORD_SIZE = 8


@attrs.define
class Mtx(BaseFileFormat):
    strings: list[MtxString]

    @classmethod
    def decode(cls, fp: BinaryIO) -> Mtx:
        if not fp.seekable():
            raise io.UnsupportedOperation(
                "Unable to perform seek operations on the file handler."
            )

        mtx_length = int.from_bytes(fp.read(MTX_LENGTH_WORD_SIZE), MTX_ENDIAN)

        if fp.seek(0, SEEK_END) % mtx_length != 0:
            raise FileFormatError(
                f"The size of the mtx is incorrect.\nExpected: {mtx_length}\nActual: "
                f"{fp.tell()}"
            )

        fp.seek(MTX_LENGTH_WORD_SIZE)

        identifier_word = fp.read(MTX32_IDENTIFIER_WORD_SIZE)
        identifier = int.from_bytes(identifier_word, MTX_ENDIAN)

        # Check if the mtx uses 32 bit offsets or 64 bit offsets. Since the format is
        # little endian and the known values are 8 or 16 for 32 and 64 respectively,
        # we can check that the identifier is still 16 if the offset is 64 bits.
        if identifier == MTX32_IDENTIFIER:
            offset_word_size = MTX32_OFFSET_WORD_SIZE
        elif (
            identifier
            == int.from_bytes(
                identifier_word
                + fp.read(MTX64_IDENTIFIER_WORD_SIZE - MTX32_IDENTIFIER_WORD_SIZE),
                MTX_ENDIAN,
            )
            == MTX64_IDENTIFIER
        ):
            offset_word_size = MTX64_OFFSET_WORD_SIZE
        else:
            raise FileFormatError("The given data is not in a valid mtx format.")

        def read_bytes(word_size: int) -> int:
            return int.from_bytes(fp.read(word_size), MTX_ENDIAN)

        section_table_offset = read_bytes(offset_word_size)
        string_table_offset = read_bytes(offset_word_size)

        sections: list[int] = [string_table_offset]

        sections.extend(
            read_bytes(offset_word_size)
            for _ in range(
                ((string_table_offset - section_table_offset) // offset_word_size) - 1
            )
        )

        # Add the mtx length to the sections so we can read to end of stream
        sections.append(mtx_length)

        strings: list[MtxString] = []

        for current_string_offset, next_string_offset in pairwise(sections):
            strings.append([
                read_bytes(MTX_CHARACTER_WORD_SIZE)
                for _ in range(
                    (next_string_offset - current_string_offset)
                    // MTX_CHARACTER_WORD_SIZE
                )
            ])

        return cls(strings)

    def encode(self, fp: BinaryIO, *, offset_size: MtxOffsetSize = 32) -> None:
        if offset_size == 64:
            offset_word_size = MTX64_OFFSET_WORD_SIZE
            offset_identifier = MTX64_IDENTIFIER
        else:
            offset_word_size = MTX32_OFFSET_WORD_SIZE
            offset_identifier = MTX32_IDENTIFIER

        # mtx_length, mtx_identifier, mtx_section_offset
        header_widths = [MTX_LENGTH_WORD_SIZE, offset_word_size, offset_word_size]
        header_length = sum(header_widths)

        # mtx_string_offsets
        mtx_length = header_length + (offset_word_size * len(self.strings))

        string_offsets: list[int] = []
        string_lengths = [
            len(string) * MTX_CHARACTER_WORD_SIZE for string in self.strings
        ]

        for string_length in string_lengths:
            string_offsets.append(mtx_length)
            mtx_length += string_length

        def write_bytes(data: int, length: int) -> None:
            fp.write(data.to_bytes(length, MTX_ENDIAN))

        write_bytes(mtx_length, MTX_LENGTH_WORD_SIZE)
        write_bytes(offset_identifier, offset_word_size)
        write_bytes(header_length, offset_word_size)

        for offset in string_offsets:
            write_bytes(offset, offset_word_size)

        for string in self.strings:
            for character in string:
                write_bytes(character, MTX_CHARACTER_WORD_SIZE)

    def write_xml(self, font: BaseCharacterTable) -> bytes:
        root = etree.Element("mtx")
        sheet = etree.SubElement(root, "sheet")

        for string in self.strings:
            dialog = etree.SubElement(sheet, "text")

            with StringIO() as str_buf:
                for character in string:
                    match character:
                        case 0xF813:
                            dialog.append(etree.Element("arrow"))
                        # TODO: Figure out what this control character does
                        case 0xF883:
                            str_buf.write("0xF883")
                        case 0xFFFD:
                            str_buf.write("\n")
                        case 0xFFFF:
                            break
                        case _:
                            str_buf.write(font[character])

                dialog.text = str_buf.getvalue()

        return etree.tostring(root, encoding="utf-8", xml_declaration=True)
