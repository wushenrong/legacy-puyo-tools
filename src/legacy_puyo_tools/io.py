"""Functions to deal with file operations.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT
"""

import contextlib
import os
import pathlib
from collections.abc import Generator
from typing import BinaryIO

from legacy_puyo_tools.typing import BinaryModes, PathOrFile


@contextlib.contextmanager
def get_file_handle(
    path_or_buf: PathOrFile, mode: BinaryModes = "rb"
) -> Generator[BinaryIO, None, None]:
    """Context manager that opens a path or pass a file-like object in binary mode.

    Args:
        path_or_buf:
            A string path, path-like object, or a file-like object in binary mode.
        mode:
            Should we read or write to the file. Defaults to "rb".

    Yields:
        A file-like object in binary mode.
    """
    if isinstance(path_or_buf, (str, os.PathLike)):
        # pylint: disable=unspecified-encoding
        with pathlib.Path(path_or_buf).open(mode) as fp:
            yield fp
    else:
        yield path_or_buf


def get_file_name(path_or_buf: PathOrFile) -> str:
    """Get the name of the file from a path or a file-like object in binary mode.

    Args:
        path_or_buf:
            A string path, path-like object, or a file-like object in binary mode.

    Returns:
        The name of the file.
    """
    if isinstance(path_or_buf, (str, os.PathLike)):
        return pathlib.Path(os.fspath(path_or_buf)).name

    return pathlib.Path(os.fspath(path_or_buf.name)).name
