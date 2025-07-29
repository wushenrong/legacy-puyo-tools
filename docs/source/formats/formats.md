# Formats

Below are the formats that are used by the older Puyo Puyo games and how they
are structured.

```{todo} Add formats that is out of scope for this project.
```

## The `fpd` format

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

The `fmp` format is a 4 bits per pixel (4bpp) bitmap format used by the Nintendo
DS versions of Puyo Puyo! 15th Anniversary and Puyo Puyo 7 to store the
graphical data of characters corresponding to the
`fpd` file. Each character is either 14x14 pixels (in `puyo14.fmp` and
`test.fmp`) or 8x8 pixels (in `puyo8.fmp`).

Although it uses a bit-depth that can encode 16 colors, the format is mainly
black and white with `0x0` and `0x1` encoding an off and on pixel respectively.
Each nibble, not byte, is also stored in little-endian where the least
significant nibble is store first before the most significant nibble.

Pixels are stored row by row, in top-to-bottom and left-to-right order. There
are no headers or padding bytes in the file.

## The `mtx` format

The `mtx` format is a binary-encoded format used by older Puyo games for
storing character dialog and text.

```{todo} Information about the mtx format for PP15 and PP7
```

```{todo} Look at the mtx format for PP20
```
