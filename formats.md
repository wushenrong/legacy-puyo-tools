# Formats

Below are the formats that are used by the older Puyo games. This includes how
each format is structured and the current progress on creating and converting
them.

## The `fpd` format

Both the creation and conversion of `fpd` are fully implemented.

The `fpd` format is a binary character table format used by the developers of
Puyo Puyo! 15th Anniversary and Puyo Puyo 7 to convert characters from UTF-16
little-endian into an index that can be used by the `mtx` for text. Each
character entry in the `fpd` is 3 bytes long and formatted as follows:
`XX XX YY`. Where `XX XX` is the character encoded in UTF-16 little-endian and
`YY` is the width of the character. The entries are placed next to each other,
creating a zero-based index that is offset by multiples of `0x03`. I.e. the 1st
character is at index `0x00`, the 2nd character is at index `0x03`, the 3rd
character is at index `0x06`, etc.

The `fpd` is not used by the games internally except for the Nintendo DS version
of the games.

## The `fmp` format

The `fmp` format is a bitmap format used by the Nintendo DS versions of Puyo
Puyo! 15th Anniversary and Puyo Puyo 7 to store the pixel data of the font
corresponding to the `fpd` file. Characters are stored in the same order as the
`fpd` file. Each character is either 14x14 pixels (in `puyo14.fmp` and
`test.fmp`) or 8x8 pixels (in `puyo8.fmp`). The image data is stored in a packed
format where each byte encodes two horizontal pixels, where the lower nibble
(4 bits) represent the left pixel and the higher nibble represent the right
one:

- `0x1` represents a visible pixel (on pixel)
- `0x0` represents an empty pixel (off pixel)

Pixels are stored row by row, in top-to-bottom and left-to-right order. There
are no headers or padding bytes in the file.

## The `mtx` format

The creation of `mtx` has not been implemented yet while conversion only has
partial support.

<!-- TODO: Finish the mtx format for PP15 and PP7 -->
<!-- TODO: Look at the mtx format for PP20 -->
The `mtx` format is a binary-encoded format used by older Puyo games for
storing character dialog and text.
