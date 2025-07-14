# Formats

Older Puyo Puyo games used multiple formats to store manzai text and character
data. This document contains how each format is structured and encoded.

## The `fpd` format

The `fpd` format is a binary character table format used by the developers for
Puyo Puyo! 15th Anniversary and Puyo Puyo 7 to convert characters from UTF-16
little-endian into an index that is used by the `mtx` for text. Each character
entry in the `fpd` is 3 bytes long and formatted as follows: `XX XX YY`. Where
`XX XX` is the character encoded in UTF-16 little-endian and `YY` is the width
of the character. The entries are placed next to each other, creating a
zero-based index that is offset by multiples of `0x03`. I.e. the 1st character
is at index `0x00`, the 2nd character is at index `0x03`, the 3rd character is
at index `0x06`, etc.

The `fpd` is not used by the games internally except for the Nintendo DS version
of Puyo Puyo 7.

## The `mtx` format

<!-- TODO: Finish the mtx format for PP15 and PP7 -->
<!-- TODO: Look at the mtx format for PP20 -->
The `mtx` format is a binary-encoded format used by older Puyo games for
storing character dialog and text.
