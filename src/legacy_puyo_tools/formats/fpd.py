# SPDX-FileCopyrightText: 2021 Nick Woronekin
# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Fpd conversion tool for older Puyo games.

This module supports the encoding and decoding of the fpd file format used by Puyo Puyo!
15th Anniversary and Puyo Puyo 7.
"""

from __future__ import annotations

import struct
from collections import OrderedDict
from io import StringIO
from typing import BinaryIO, TextIO

import attrs

from legacy_puyo_tools.exceptions import FileFormatError
from legacy_puyo_tools.formats._csv import (
    read_csv_character_table,
    write_csv_character_table,
)
from legacy_puyo_tools.formats.base import (
    BaseCharacterTable,
    BaseFileFormat,
)

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

    width: int = attrs.field(default=0x0, eq=False)
    """How wide should the character be, only used in the Nintendo DS versions of the
    games."""


@attrs.define
class Fpd(BaseFileFormat, BaseCharacterTable):
    """A fpd character table.

    The fpd stores a character table in which each entry is placed right next to each
    other and the indices is offset by multiples of `0x03`. I.e. The 1st character is at
    index `0x00`, the 2nd character is at index `0x03`, the 3rd character is at index
    `0x06`, etc.
    """

    entries: OrderedDict[str, FpdCharacter]
    """A ordered dictionary of fpd character entries."""

    character_list: list[str] = attrs.field(
        default=attrs.Factory(lambda self: list(self.entries), takes_self=True)
    )
    """A list of characters based on their insertion order."""

    def __getitem__(self, index: int) -> str:
        """Return a character from the fpd character table."""
        return self.character_list[index]

    def __str__(self) -> str:
        """Return all of the characters in the fpd character table as a string."""
        with StringIO() as string_buffer:
            for character in self.entries:
                string_buffer.write(character)

            return string_buffer.getvalue()

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
        character_table: OrderedDict[str, FpdCharacter] = OrderedDict()

        try:
            fpd_characters = struct.iter_unpack(FPD_CHARACTER_ENTRY_FORMAT, fp.read())
        except struct.error as e:
            raise FileFormatError(
                "The given fpd character table contains entries that does not "
                "conform to the fpd character format."
            ) from e

        for code_point, width in fpd_characters:
            character_table[chr(code_point)] = FpdCharacter(width)

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
        for code_point, character in self.entries.items():
            try:
                fp.write(
                    struct.pack(
                        FPD_CHARACTER_ENTRY_FORMAT, ord(code_point), character.width
                    )
                )
            except struct.error as e:
                raise FileFormatError(
                    f"Character '{code_point}' cannot be encoded to fpd."
                ) from e

    @classmethod
    def read_csv(cls, fp: TextIO) -> Fpd:
        """Read a formatted fpd character table from a CSV file.

        Arguments:
            fp:
                A file-like object in text mode to a CSV file that has a list of
                characters and widths.

        Returns:
            A fpd character table.
        """
        return cls(read_csv_character_table(fp, FpdCharacter))

    def write_csv(self, fp: TextIO) -> None:
        """Write the fpd character table to a file-like object.

        Arguments:
            fp:
                The file-like object to write the character table as a CSV file.
        """
        write_csv_character_table(fp, self.entries)
