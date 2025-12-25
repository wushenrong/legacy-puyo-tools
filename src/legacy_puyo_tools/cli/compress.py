# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""The cli to compress files used by the Nintendo DS and 3DS."""

import cloup


@cloup.group()
@cloup.version_option()
def app() -> None:
    """A tool to compress files used by the Nintendo DS and 3DS."""
