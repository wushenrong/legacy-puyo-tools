"""Manzai text conversion tool for older Puyo Puyo games.

This module converts mtx files to and from XML for modding Puyo games. Currently
supports Puyo Puyo 7 and might support Puyo Puyo! 15th Anniversary.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from os import PathLike
from pathlib import Path
from typing import BinaryIO, Literal

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


CHARACTER_WIDTH = 2
ENDIAN = "little"

INT32_OFFSET = 8
INT32_SIZE = 4
INT64_OFFSET = 16
INT64_SIZE = 8


def _read_character(data: bytes, i: int) -> int:
    return int.from_bytes(data[i : i + CHARACTER_WIDTH], ENDIAN)


def _create_offset_reader(width: int) -> Callable[[bytes, int], int]:
    def offset_reader(data: bytes, i: int) -> int:
        return int.from_bytes(data[i : i + width], ENDIAN)

    return offset_reader


def _identify_mtx(data: bytes) -> tuple[Literal[8, 16], Literal[4, 8]]:
    if int.from_bytes(data[:4], ENDIAN) == INT32_OFFSET:
        return (INT32_OFFSET, INT32_SIZE)

    if int.from_bytes(data[8:16], ENDIAN) == INT64_OFFSET:
        return (INT64_OFFSET, INT64_SIZE)

    raise FormatError("The given data is not in a valid `mtx` format")


# TODO: When upgrading to Python 3.12, add type to the beginning of the alias
MtxString = list[int]


@attrs.define
class Mtx:
    strings: list[MtxString]

    @classmethod
    def read_mtx_from_file(cls, path: str | PathLike[str]) -> Mtx:
        with Path(path).open("rb") as fp:
            try:
                return cls.read_mtx(fp)
            except FormatError as e:
                raise FileFormatError(f"{path} is not a valid `mtx` file") from e

    @classmethod
    def read_mtx(cls, fp: BinaryIO) -> Mtx:
        return cls.decode_mtx(fp.read())

    @classmethod
    def decode_mtx(cls, data: bytes) -> Mtx:
        length = int.from_bytes(data[:4], ENDIAN)

        if length != len(data):
            raise FormatError("The size of the given data does not match")

        section_table_index_offset, int_width = _identify_mtx(data[4:16])
        read_offset = _create_offset_reader(int_width)

        section_table_offset = read_offset(data, section_table_index_offset)
        string_table_offset = read_offset(data, section_table_offset)

        sections = [
            read_offset(data, section_table_offset + (i * int_width))
            for i in range((string_table_offset - section_table_offset) // int_width)
        ]

        # Add the length to the sections so we can read to end of stream
        sections.append(length)

        strings: list[MtxString] = []

        for current_string_offset, next_string_offset in pairwise(sections):
            strings.append([
                _read_character(data, current_string_offset + (i * CHARACTER_WIDTH))
                for i in range(next_string_offset - current_string_offset)
            ])

        return cls(strings)

    def write_xml_to_file(self, path: str | PathLike[str], fpd: Fpd) -> None:
        with Path(path).open("wb") as fp:
            self.write_xml(fp, fpd)

    def write_xml(self, fp: BinaryIO, fpd: Fpd) -> None:
        fp.write(self.encode_xml(fpd))

    def encode_xml(self, fpd: Fpd) -> bytes:
        root = etree.Element("mtx")
        sheet = etree.SubElement(root, "sheet")

        for string in self.strings:
            dialog = etree.SubElement(sheet, "text")
            dialog.text = "\n"

            for character in string:
                # TODO: When upgrading to Python 3.10, use `match` statements
                if character == 0xF813:
                    dialog.append(etree.Element("arrow"))
                # TODO: Figure out what this control character does
                elif character == 0xF883:
                    dialog.text += "0xF883"
                elif character == 0xFFFD:
                    dialog.text += "\n"
                elif character == 0xFFFF:
                    break
                else:
                    dialog.text += fpd[character]

        etree.indent(root)

        return etree.tostring(
            root, encoding="utf-8", xml_declaration=True, pretty_print=True
        )
