# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Fpd conversion tool for older Puyo games.

This module supports the encoding and decoding of the fpd file format used by Puyo Puyo!
15th Anniversary and Puyo Puyo 7.
"""

from __future__ import annotations

import csv
import struct
from io import StringIO
from typing import BinaryIO, TextIO

import attrs
from bidict import OrderedBidict

from legacy_puyo_tools.formats.base import BaseFileFormat, FileFormatError

FPD_CSV_HEADER = ["code_point", "width"]
"""The required header for a CSV file to be considered a fpd character table."""

FPD_CHARACTER_ENTRY_FORMAT = "<HB"
"""The format of a fpd character entry. Two bytes for character's Unicode code point and
one byte for character width."""


@attrs.frozen
class FpdCharacter:
    """A fpd character entry.

    A fpd character is a binary entry that is 3 bytes long and formatted as follows
    `XX XX YY`. Where `XX XX` is the character's Unicode code point in little-endian and
    `YY` is the width of the character. Or the following struct:

    ```
    {
        char16_t character;
        uint8_t width;
    }
    ```

    The character encoding can be considered to be UTF-16 little-endian. However, the
    `fpd` only can only store characters from the Basic Multilingual Plane or `U+0000`
    to `U+FFFF` due to the format having a fixed width of 16 bits per code point. So it
    is more accurately to say the encoding is the older UCS-2, the predecessor to
    UTF-16.
    """

    code_point: str
    """A string that stores a single character."""
    width: int = attrs.field(default=0x0, eq=False)
    """How wide should the character be, only used in the Nintendo DS versions of the
    games."""

    def __str__(self) -> str:
        """Return the underlying character as a string."""
        return self.code_point

    def encode(self) -> bytes:
        """Encode the character to a fpd character entry.

        Raises:
            UnicodeEncodeError:
                The character is not in the Basic Multilingual Plane, or a code point
                from `U+0000` to `U+FFFF`.

        Returns:
            The character's Unicode code point in little-endian and its width.
        """
        try:
            return struct.pack(
                FPD_CHARACTER_ENTRY_FORMAT, ord(self.code_point), self.width
            )
        except struct.error as e:
            raise UnicodeEncodeError(
                "UTF-16",
                self.code_point,
                0,
                1,
                "Character is not in the BMP or a code point from U+0000 to U+FFFF",
            ) from e


@attrs.define
class Fpd(BaseFileFormat):
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
        with StringIO() as str_buf:
            for character in self.entries.inverse:
                while isinstance(character, int):
                    character = self.entries[character]

                str_buf.write(str(character))

            return str_buf.getvalue()

    def get_index(self, character: str) -> int:
        """Return the index of a character from the fpd character table."""
        return self.entries.inverse[FpdCharacter(character)]

    @classmethod
    def decode(cls, fp: BinaryIO) -> Fpd:
        """Decode fpd character table from a file-like object.

        Arguments:
            fp:
                A file-like object in binary mode containing a fpd character table.

        Raises:
            FileFormatError:
                The given fpd character table contains entries that does not conform to
                the fpd character format.

        Returns:
            A fpd character table.
        """
        character_table: OrderedBidict[int, int | FpdCharacter] = OrderedBidict()

        try:
            fpd_characters = struct.iter_unpack(FPD_CHARACTER_ENTRY_FORMAT, fp.read())
        except struct.error as e:
            raise FileFormatError(
                "The given fpd character table contains entries that does not "
                "conform to the fpd character format."
            ) from e

        for i, (code_point, width) in enumerate(fpd_characters):
            code_point = FpdCharacter(chr(code_point), width)

            if (character_index := character_table.inverse.get(code_point, -1)) != -1:
                while character_table.inverse.get(character_index, -1) != -1:
                    character_index = character_table.inverse.get(character_index, -1)

                character_table.put(i, character_index)
            else:
                character_table.put(i, code_point)

        return cls(character_table)

    def encode(self, fp: BinaryIO) -> None:
        """Encode the fpd character table to a file-like object.

        Arguments:
            fp:
                The file-like object in binary mode that fpd character table will be
                encoded to.

        Raises:
            FileFormatError:
                A character in the fpd character table cannot be encoded to fmp because
                the character is not in the Basic Multilingual Plane.
        """
        for character in self.entries.inverse:
            while isinstance(character, int):
                character = self.entries[character]

            try:
                fp.write(character.encode())
            except UnicodeEncodeError as e:
                raise FileFormatError(
                    f"Character '{character}' cannot be encoded to fpd"
                ) from e

    @classmethod
    def read_csv(cls, fp: TextIO) -> Fpd:
        """Read a formatted fpd character table from a CSV file.

        Arguments:
            fp:
                A file-like object in text mode to a CSV file that has a list of
                characters and widths.

        Raises:
            FileFormatError:
                The CSV data does not have `character,width` as it's headers.

        Returns:
            A fpd character table.
        """
        character_table: OrderedBidict[int, int | FpdCharacter] = OrderedBidict()

        csv_reader = csv.DictReader(fp)

        if csv_reader.fieldnames != FPD_CSV_HEADER:
            raise FileFormatError(
                "The given csv does not match the following header: "
                + ",".join(FPD_CSV_HEADER)
            )

        for i, entry in enumerate(csv_reader):
            code_point, width = entry.values()

            fpd_character = FpdCharacter(code_point, int(width, base=16))

            if (
                character_index := character_table.inverse.get(fpd_character, -1)
            ) != -1:
                while character_table.inverse.get(character_index, -1) != -1:
                    character_index = character_table.inverse.get(character_index, -1)

                character_table.put(i, character_index)
            else:
                character_table.put(i, fpd_character)

        return cls(character_table)

    def write_csv(self, fp: TextIO) -> None:
        """Write the fpd character table to a file-like object.

        Arguments:
            fp:
                The file-like object to write the character table as a CSV file.
        """
        csv_writer = csv.DictWriter(fp, FPD_CSV_HEADER)

        csv_writer.writeheader()

        for character in self.entries.inverse:
            while isinstance(character, int):
                character = self.entries[character]

            csv_writer.writerow(
                attrs.asdict(
                    character,
                    value_serializer=lambda _, __, value: (
                        hex(value) if isinstance(value, int) else value
                    ),
                )
            )
