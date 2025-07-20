"""Manzai text conversion tool for older Puyo Puyo games.

This module converts mtx files to and from XML for modding Puyo games. Currently
supports Puyo Puyo 7 and might support Puyo Puyo! 15th Anniversary.

SPDX-FileCopyrightText: 2021 Nick Woronekin
SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from io import BytesIO, StringIO
from os import PathLike
from pathlib import Path
from typing import BinaryIO

import attrs
from lxml import etree

from legacy_puyo_tools.exceptions import FileFormatError, FormatError
from legacy_puyo_tools.fpd import Fpd

# TODO: When updating to Python 3.10, remove the stub implementation of pairwise
# from the python documentation:
# https://docs.python.org/3/library/itertools.html#itertools.pairwise
if sys.version_info >= (3, 10):
    from itertools import pairwise
else:
    from collections.abc import Iterable
    from itertools import tee
    from typing import TypeVar

    T = TypeVar("T")

    def pairwise(iterable: Iterable[T]) -> Iterable[tuple[T, T]]:
        """Simple pairwise implementation for Python < 3.10."""  # noqa: DOC201
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)


ENDIAN = "little"

MTX_IDENTIFIER = 8
MTX_INT32_WIDTH = 4
MTX_CHARACTER_WIDTH = 2

MTX_SIZE_WIDTH = MTX_INT32_WIDTH
MTX_IDENTIFIER_WIDTH = MTX_INT32_WIDTH
MTX_OFFSET_WIDTH = MTX_INT32_WIDTH
MTX_SECTION_WIDTH = MTX_INT32_WIDTH


# TODO: When upgrading to Python 3.12, add type to the beginning of the alias
MtxString = list[int]


@attrs.define
class Mtx:
    strings: list[MtxString]

    @classmethod
    def read_mtx_from_path(cls, path: str | PathLike[str]) -> Mtx:
        with Path(path).open("rb") as fp:
            try:
                return cls.read_mtx(fp)
            except FormatError as e:
                raise FileFormatError(
                    f"{path} is not a valid mtx file, it might be a 64bit mtx file"
                ) from e

    @classmethod
    def read_mtx(cls, fp: BinaryIO) -> Mtx:
        return cls.decode_mtx(fp.read())

    @classmethod
    def decode_mtx(cls, data: bytes) -> Mtx:
        def read_bytes(i: int, width: int) -> int:
            return int.from_bytes(data[i : i + width], ENDIAN)

        length = read_bytes(0, MTX_SIZE_WIDTH)

        if length != len(data):
            raise FormatError("The size of the given data does not match")

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

    def write_mtx_from_path(self, path: str | PathLike[str]) -> None:
        with Path(path).open("rb") as fp:
            self.write_mtx(fp)

    def write_mtx(self, fp: BinaryIO) -> None:
        fp.write(self.encode_mtx())

    def encode_mtx(self) -> bytes:
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

    def write_xml_to_path(self, path: str | PathLike[str], fpd: Fpd) -> None:
        with Path(path).open("wb") as fp:
            self.write_xml(fp, fpd)

    def write_xml(self, fp: BinaryIO, fpd: Fpd) -> None:
        fp.write(self.encode_xml(fpd))

    def encode_xml(self, fpd: Fpd) -> bytes:
        root = etree.Element("mtx")
        sheet = etree.SubElement(root, "sheet")

        for string in self.strings:
            dialog = etree.SubElement(sheet, "text")

            with StringIO() as string_buffer:
                for character in string:
                    # TODO: When upgrading to Python 3.10, use `match` statements
                    if character == 0xF813:
                        dialog.append(etree.Element("arrow"))
                    # TODO: Figure out what this control character does
                    elif character == 0xF883:
                        string_buffer.write("0xF883")
                    elif character == 0xFFFD:
                        string_buffer.write("\n")
                    elif character == 0xFFFF:
                        break
                    else:
                        string_buffer.write(fpd[character])

                dialog.text = string_buffer.getvalue()

        return etree.tostring(root, encoding="utf-8", xml_declaration=True)
