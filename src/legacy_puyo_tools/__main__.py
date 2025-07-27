# SPDX-FileCopyrightText: 2025 Samuel Wu
#
# SPDX-License-Identifier: MIT

"""Allow the cli to be run from runpy or using `python -m legacy_puyo_tools`."""

if __name__ == "__main__":
    from legacy_puyo_tools.cli import app

    app()
