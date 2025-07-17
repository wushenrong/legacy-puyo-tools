"""Manzai text conversion tool for older Puyo Puyo games.

This module converts mtx files to and from XML for modding Puyo games. Currently
supports Puyo Puyo 7 and might support Puyo Puyo! 15th Anniversary.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

from collections.abc import Callable
from itertools import pairwise
from pathlib import Path
from typing import BinaryIO, Literal, Self

from attrs import define
from lxml import etree

from legacy_puyo_tools.exceptions import FileFormatError, FormatError
from legacy_puyo_tools.fpd import Fpd

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


type MtxString = list[int]


@define
class Mtx:
    strings: list[MtxString]

    @classmethod
    def read_mtx_from_file(cls, path: Path) -> Self:
        with Path(path).open("rb") as fp:
            try:
                return cls.read_mtx(fp)
            except FormatError as e:
                raise FileFormatError(f"{path} is not a valid `mtx` file") from e

    @classmethod
    def read_mtx(cls, fp: BinaryIO) -> Self:
        return cls.decode_mtx(fp.read())

    @classmethod
    def decode_mtx(cls, data: bytes) -> Self:
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

    def write_xml_to_file(self, path: Path, fpd: Fpd) -> None:
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
                match character:
                    case 0xF813:
                        dialog.append(etree.Element("arrow"))
                    # TODO: Figure out what this control character does
                    case 0xF883:
                        dialog.text += "0xF883"
                    case 0xFFFD:
                        dialog.text += "\n"
                    case 0xFFFF:
                        break
                    case _:
                        dialog.text += fpd[character]

        etree.indent(root)

        return etree.tostring(
            root, encoding="utf-8", xml_declaration=True, pretty_print=True
        )
