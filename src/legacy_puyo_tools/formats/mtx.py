"""Manzai text conversion tool for older Puyo Puyo games.

This module converts mtx files to and from XML for modding Puyo games. Currently
supports Puyo Puyo 7 and might support Puyo Puyo! 15th Anniversary.

SPDX-FileCopyrightText: 2021 Nick Woronekin
SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from io import BytesIO, StringIO
from itertools import pairwise

import attrs
from lxml import etree

from legacy_puyo_tools.formats.base import Format, FormatError
from legacy_puyo_tools.formats.fpd import Fpd
from legacy_puyo_tools.io import PathOrFile, get_file_handle

ENDIAN = "little"

MTX_IDENTIFIER = 8
MTX_INT32_WIDTH = 4
MTX_CHARACTER_WIDTH = 2

MTX_SIZE_WIDTH = MTX_INT32_WIDTH
MTX_IDENTIFIER_WIDTH = MTX_INT32_WIDTH
MTX_OFFSET_WIDTH = MTX_INT32_WIDTH
MTX_SECTION_WIDTH = MTX_INT32_WIDTH

# TODO: When upgrading to Python 3.12, add type to the beginning of aliases
MtxString = list[int]


@attrs.define
class Mtx(Format):
    strings: list[MtxString]

    @classmethod
    def read_mtx(cls, path_or_buf: PathOrFile) -> Mtx:
        return super()._decode_file(path_or_buf)

    @classmethod
    def decode(cls, data: bytes) -> Mtx:
        def read_bytes(i: int, width: int) -> int:
            return int.from_bytes(data[i : i + width], ENDIAN)

        length = read_bytes(0, MTX_SIZE_WIDTH)

        if length != len(data):
            raise FormatError("The size of the given mtx does not match")

        if read_bytes(MTX_SIZE_WIDTH, MTX_OFFSET_WIDTH) != MTX_IDENTIFIER:
            raise FormatError(
                "The given data is not in a valid mtx format, it might be a 64bit mtx"
            )

        section_table_offset = read_bytes(MTX_IDENTIFIER, MTX_IDENTIFIER_WIDTH)
        string_table_offset = read_bytes(section_table_offset, MTX_OFFSET_WIDTH)

        sections = [
            read_bytes(section_table_offset + (i * MTX_INT32_WIDTH), MTX_INT32_WIDTH)
            for i in range(
                (string_table_offset - section_table_offset) // MTX_INT32_WIDTH
            )
        ]

        # Add the length to the sections so we can read to end of stream
        sections.append(length)

        strings: list[MtxString] = []

        for current_string_offset, next_string_offset in pairwise(sections):
            strings.append([
                int.from_bytes(
                    data[
                        current_string_offset
                        + (i * MTX_CHARACTER_WIDTH) : current_string_offset
                        + (i * MTX_CHARACTER_WIDTH)
                        + MTX_CHARACTER_WIDTH
                    ],
                    ENDIAN,
                )
                for i in range(
                    (next_string_offset - current_string_offset) // MTX_CHARACTER_WIDTH
                )
            ])

        return cls(strings)

    def encode(self) -> bytes:
        def write_character(fp: BytesIO, i: int, length: int) -> None:
            fp.write(i.to_bytes(length, ENDIAN))

        header_widths = [MTX_SIZE_WIDTH, MTX_IDENTIFIER_WIDTH, MTX_OFFSET_WIDTH]

        mtx_length = sum(header_widths) + MTX_SECTION_WIDTH * (len(self.strings))

        string_offsets: list[int] = []
        string_lengths = [len(string) * MTX_CHARACTER_WIDTH for string in self.strings]

        for string_length in string_lengths:
            string_offsets.append(mtx_length)
            mtx_length += string_length

        with BytesIO() as bytes_buffer:
            write_character(bytes_buffer, mtx_length, MTX_SIZE_WIDTH)
            write_character(bytes_buffer, MTX_IDENTIFIER, MTX_IDENTIFIER_WIDTH)
            write_character(
                bytes_buffer,
                MTX_SIZE_WIDTH + MTX_IDENTIFIER_WIDTH + MTX_OFFSET_WIDTH,
                MTX_OFFSET_WIDTH,
            )

            for offset in string_offsets:
                write_character(bytes_buffer, offset, MTX_SECTION_WIDTH)

            for string in self.strings:
                for character in string:
                    write_character(bytes_buffer, character, MTX_CHARACTER_WIDTH)

            return bytes_buffer.getvalue()

    def write_mtx(self, path_or_buf: PathOrFile) -> None:
        with get_file_handle(path_or_buf, "wb") as fp:
            fp.write(self.encode())

    def to_xml(self, fpd: Fpd) -> bytes:
        root = etree.Element("mtx")
        sheet = etree.SubElement(root, "sheet")

        for string in self.strings:
            dialog = etree.SubElement(sheet, "text")

            with StringIO() as string_buffer:
                for character in string:
                    match character:
                        case 0xF813:
                            dialog.append(etree.Element("arrow"))
                        # TODO: Figure out what this control character does
                        case 0xF883:
                            string_buffer.write("0xF883")
                        case 0xFFFD:
                            string_buffer.write("\n")
                        case 0xFFFF:
                            break
                        case _:
                            string_buffer.write(fpd[character])

                dialog.text = string_buffer.getvalue()

        return etree.tostring(root, encoding="utf-8", xml_declaration=True)

    def write_xml(self, path_or_buf: PathOrFile, fpd: Fpd) -> None:
        with get_file_handle(path_or_buf, "wb") as fp:
            fp.write(self.to_xml(fpd))
