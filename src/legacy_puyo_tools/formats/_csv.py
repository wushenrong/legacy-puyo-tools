# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

import csv
from collections import OrderedDict
from collections.abc import Callable
from typing import Any, TextIO

from legacy_puyo_tools.exceptions import FileFormatError

CSV_TABLE_HEADER = ["code_point", "width"]


def read_csv_character_table[T](
    fp: TextIO, cast: Callable[[Any], T]
) -> OrderedDict[str, T]:
    csv_reader = csv.DictReader(fp)

    if csv_reader.fieldnames != CSV_TABLE_HEADER:
        raise FileFormatError(
            "The given csv does not match the following header: "
            + ",".join(CSV_TABLE_HEADER)
        )

    character_table: OrderedDict[str, T] = OrderedDict()

    for entry in csv_reader:
        code_point, width = entry.values()
        character_table[code_point] = cast(width)

    return character_table


def write_csv_character_table(
    fp: TextIO, character_table: OrderedDict[str, Any]
) -> None:
    csv_writer = csv.DictWriter(fp, CSV_TABLE_HEADER)
    csv_writer.writeheader()

    csv_writer.writerows([
        {
            "code_point": code_point,
            "width": hex(character.width),
        }
        for code_point, character in character_table.items()
    ])
