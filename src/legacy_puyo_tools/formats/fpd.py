# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Fpd conversion tool for older Puyo games.

This module supports the encoding and decoding of the fpd format used by Puyo Puyo! 15th
Anniversary and Puyo Puyo 7.
"""

from __future__ import annotations

import csv
from io import BytesIO, StringIO
from struct import iter_unpack, pack
from typing import Any, BinaryIO

import attrs
from bidict import OrderedBidict

from legacy_puyo_tools.exceptions import FileFormatError
from legacy_puyo_tools.formats._io import get_file_name, read_file, write_file
from legacy_puyo_tools.formats.base import Format, FormatError
from legacy_puyo_tools.typing import StrPath

FPD_ENTRY_LENGTH = 3
"""The length of a fpd character entry."""

FPD_CSV_HEADER = ["character", "width"]


@attrs.frozen
class FpdCharacter:
    """A fpd character entry.

    A fpd character is a binary entry that is 3 bytes long and formatted as follows:
    `XX XX YY`. Where `XX XX` is the character encoded in UTF-16 little-endian and `YY`
    is the width of the character.
    """

    character: str
    """A string that stores a single character."""
    width: int = attrs.field(default=0x0, eq=False)
    """How wide should the character be, only used in the Nintendo DS versions of the
    games."""

    def __str__(self) -> str:
        """Return the underlying character as a string."""
        return self.character

    def encode(self) -> bytes:
        """Encode the character to a fpd character entry.

        :return: The character in UTF-16 LE format and its width.
        """
        return pack("<HB", ord(self.character), self.width)


@attrs.define
class Fpd(Format):
    """A fpd character table.

    The fpd stores a character table in which each entry is placed right next to each
    other and the indices is offset by multiples of `0x03`. I.e. The 1st character is at
    index `0x00`, the 2nd character is at index `0x03`, the 3rd character is at index
    `0x06`, etc.
    """

    entries: OrderedBidict[int, int | FpdCharacter]
    """A ordered bidirectional dictionary of fpd character entries."""

    def __getitem__(self, index: int) -> str:
        """Return a character from the fpd character table."""
        character = self.entries[index]

        while isinstance(character, int):
            character = self.entries[character]

        return str(character)

    def __str__(self) -> str:
        """Return a string representation of the fpd character table."""
        with StringIO() as string_buffer:
            for character in self.entries.inverse:
                while isinstance(character, int):
                    character = self.entries[character]

                string_buffer.write(str(character))

            return string_buffer.getvalue()

    def get_index(self, character: str) -> int:
        """Return the index of a character from the fpd character table."""
        return self.entries.inverse[FpdCharacter(character)]

    @classmethod
    def read_fpd(cls, path_or_buf: StrPath | BinaryIO) -> Fpd:
        """Read and decode the fpd character table from a fpd file.

        :param path_or_buf: A string path or file-like object in binary mode to
            a fpd encoded file that contains a fpd character table.

        :return: A fpd character table.
        """
        return super()._decode_file(path_or_buf)

    @classmethod
    def decode(cls, data: bytes) -> Fpd:
        """Decode the fpd character table from a fpd encoded stream.

        :param data: A fpd encoded stream that contains a fpd character table.

        :return: A fpd character table.
        """
        if len(data) % FPD_ENTRY_LENGTH != 0:
            raise FormatError("The given data is not a valid fpd character table")

        character_table: OrderedBidict[int, int | FpdCharacter] = OrderedBidict()

        for i, (code_point, width) in enumerate(iter_unpack("<HB", data)):
            character = FpdCharacter(chr(code_point), width)

            if (character_index := character_table.inverse.get(character, -1)) != -1:
                while character_table.inverse.get(character_index, -1) != -1:
                    character_index = character_table.inverse.get(character_index, -1)

                character_table.put(i, character_index)
            else:
                character_table.put(i, character)

        return cls(character_table)

    def encode(self) -> bytes:
        """Encode the fpd character table into a fpd encoded stream.

        :return: A fpd character table encoded into a byte stream.
        """
        with BytesIO() as bytes_buffer:
            for character in self.entries.inverse:
                while isinstance(character, int):
                    character = self.entries[character]

                bytes_buffer.write(character.encode())

            return bytes_buffer.getvalue()

    def write_fpd(self, path_or_buf: StrPath | BinaryIO) -> None:
        """Write the fpd character table to a fpd encoded file.

        :param path_or_buf: A string path or file-like object in binary mode to write
            the fpd character table.
        """
        write_file(path_or_buf, self.encode())

    @classmethod
    def read_csv(cls, path_or_buf: StrPath | BinaryIO) -> Fpd:
        """Read a fpd character table from a CSV file.

        :param path_or_buf: A string path or file-like object to a CSV file.

        :return: A fpd character table.
        """
        try:
            return cls.from_csv(read_file(path_or_buf))
        except FormatError as e:
            raise FileFormatError(
                f"{get_file_name(path_or_buf)} is not in the correct format"
            ) from e

    @classmethod
    def from_csv(cls, csv_data: bytes) -> Fpd:
        """Turn a CSV data stream to into a fpd character table.

        :param csv_data: A CSV data stream with a list of characters and widths.

        :raises FormatError: The CSV data does not have FPD_CSV_HEADER as it's headers.

        :return: A fpd character table.
        """
        character_table: OrderedBidict[int, int | FpdCharacter] = OrderedBidict()

        with StringIO(csv_data.decode(), newline="") as string_buffer:
            csv_reader = csv.DictReader(string_buffer)

            if csv_reader.fieldnames != FPD_CSV_HEADER:
                raise FormatError(
                    "The given csv does not match the following header: "
                    + ",".join(FPD_CSV_HEADER)
                )

            for i, entry in enumerate(csv_reader):
                character, width = entry.values()

                fpd_character = FpdCharacter(character, int(width, base=16))

                if (
                    character_index := character_table.inverse.get(fpd_character, -1)
                ) != -1:
                    while character_table.inverse.get(character_index, -1) != -1:
                        character_index = character_table.inverse.get(
                            character_index, -1
                        )

                    character_table.put(i, character_index)
                else:
                    character_table.put(i, fpd_character)

        return cls(character_table)

    def to_csv(self) -> bytes:
        """Encode the fpd character table into a CSV data stream.

        :return: A CSV data stream with characters and widths from a fpd character
            table.
        """

        def fmp_serializer(_: type, __: attrs.Attribute[Any], value: str | int) -> str:
            if isinstance(value, int):
                return hex(value)

            return value

        with StringIO(newline="") as string_buffer:
            csv_writer = csv.DictWriter(string_buffer, FPD_CSV_HEADER)

            csv_writer.writeheader()

            for character in self.entries.inverse:
                while isinstance(character, int):
                    character = self.entries[character]

                csv_writer.writerow(
                    attrs.asdict(character, value_serializer=fmp_serializer)
                )

            return string_buffer.getvalue().encode()

    def write_csv(self, path_or_buf: StrPath | BinaryIO) -> None:
        """Write the fpd character table to a csv file.

        :param path_or_buf: A string path or file-like object to a CSV file.
        """
        write_file(path_or_buf, self.to_csv())
