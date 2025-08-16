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

from io import StringIO
from itertools import pairwise
from typing import BinaryIO, TypeAlias

import attrs
from lxml import etree

from legacy_puyo_tools.formats.base import BaseFormat, FormatError
from legacy_puyo_tools.formats.fpd import Fpd

MTX_ENDIAN = "little"
MTX_IDENTIFIER = 8
MTX_INT32_WIDTH = 4
MTX_CHARACTER_WIDTH = 2

MTX_SIZE_WIDTH = MTX_INT32_WIDTH
MTX_IDENTIFIER_WIDTH = MTX_INT32_WIDTH
MTX_OFFSET_WIDTH = MTX_INT32_WIDTH
MTX_SECTION_WIDTH = MTX_INT32_WIDTH


MtxString: TypeAlias = list[int]


@attrs.define
class Mtx(BaseFormat):
    strings: list[MtxString]

    @classmethod
    def decode(cls, fp: BinaryIO) -> Mtx:
        def read_bytes(size: int) -> int:
            return int.from_bytes(fp.read(size), MTX_ENDIAN)

        length = read_bytes(MTX_SIZE_WIDTH)

        if read_bytes(MTX_OFFSET_WIDTH) != MTX_IDENTIFIER:
            raise FormatError(
                "The given data is not in a valid mtx format, it might be a 64bit mtx"
            )

        section_table_offset = read_bytes(MTX_IDENTIFIER_WIDTH)
        string_table_offset = read_bytes(MTX_OFFSET_WIDTH)

        sections = [
            read_bytes(i * MTX_INT32_WIDTH)
            for i in range(
                (string_table_offset - section_table_offset) // MTX_INT32_WIDTH
            )
        ]

        # Add the length to the sections so we can read to end of stream
        sections.append(length)

        strings: list[MtxString] = []

        for current_string_offset, next_string_offset in pairwise(sections):
            strings.append([
                read_bytes(MTX_CHARACTER_WIDTH)
                for _ in range(
                    (next_string_offset - current_string_offset) // MTX_CHARACTER_WIDTH
                )
            ])

        return cls(strings)

    def encode(self, fp: BinaryIO) -> None:
        def write_bytes(data: int, length: int) -> None:
            fp.write(data.to_bytes(length, MTX_ENDIAN))

        header_widths = [MTX_SIZE_WIDTH, MTX_IDENTIFIER_WIDTH, MTX_OFFSET_WIDTH]
        header_length = sum(header_widths)

        mtx_length = header_length + MTX_SECTION_WIDTH * (len(self.strings))

        string_offsets: list[int] = []
        string_lengths = [len(string) * MTX_CHARACTER_WIDTH for string in self.strings]

        for string_length in string_lengths:
            string_offsets.append(mtx_length)
            mtx_length += string_length

        write_bytes(mtx_length, MTX_SIZE_WIDTH)
        write_bytes(MTX_IDENTIFIER, MTX_IDENTIFIER_WIDTH)
        write_bytes(header_length, MTX_OFFSET_WIDTH)

        for offset in string_offsets:
            write_bytes(offset, MTX_SECTION_WIDTH)

        for string in self.strings:
            for character in string:
                write_bytes(character, MTX_CHARACTER_WIDTH)

    def write_xml(self, fpd: Fpd) -> bytes:
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
                            str_buf.write(fpd[character])

                dialog.text = str_buf.getvalue()

        return etree.tostring(root, encoding="utf-8", xml_declaration=True)
