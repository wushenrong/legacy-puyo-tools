# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

import csv
from typing import TextIO

from legacy_puyo_tools.formats.base import FileFormatError

CSV_TABLE_HEADER = ["code_point", "width"]


def get_csv_reader(fp: TextIO) -> csv.DictReader[str]:
    csv_reader = csv.DictReader(fp)

    if csv_reader.fieldnames != CSV_TABLE_HEADER:
        raise FileFormatError(
            "The given csv does not match the following header: "
            + ",".join(CSV_TABLE_HEADER)
        )

    return csv_reader
