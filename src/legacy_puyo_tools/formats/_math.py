"""Functions to deal with math operations.

Some of the following code is generated by ChatGPT with modifications, and it is based
on equations or is generic enough that a public domain equivalent license can be
applied.

SPDX-FileCopyrightText: 2025 Samuel Wu
SPDX-License-Identifier: MIT-0
"""

from collections.abc import Callable
from math import isqrt


def find_largest_proper_divisor_pair(
    n: int, condition: Callable[[int], bool] = lambda _: True
) -> tuple[int | None, int | None]:
    """Return the largest proper divisor pair of a number with an optional condition."""
    for i in range(isqrt(n), 1, -1):
        if n % i != 0:
            continue

        d = n // i

        if condition(i) or condition(d):
            return d, i

    return None, None
