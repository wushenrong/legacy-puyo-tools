# Formats

Below are the formats that are used by the older Puyo Puyo games and how they
are structured.

:::{todo} Add formats that is out of scope for this project.
:::

## The `fpd` format

The `fpd` format is a binary character table format used by the developers of
Puyo Puyo! 15th Anniversary and Puyo Puyo 7 to convert Unicode characters into
an index that can be used by the `mtx` for text. Each character entry in the
`fpd` is 3 bytes long and formatted as follows: `XX XX YY`. Where `XX XX` is the
character's Unicode code point in little-endian and `YY` is the width of the
character. Or the following struct:

```c
{
    char16_t character;
    uint8_t width;
}
```

:::{note} The character encoding can be considered to be UTF-16 little-endian.
However, the `fpd` only can only store characters from the Basic Multilingual
Plane or `U+0000` to `U+FFFF` due to the format having a fixed width of 16 bits
per code point. So it is more accurately to say the encoding is the older UCS-2,
the predecessor to UTF-16.
:::

The entries are placed next to each other, creating a zero-based index that is
offset by multiples of `0x03`. For example, the 1st character is at index
`0x00`, the 2nd character is at index `0x03`, the 3rd character is at index
`0x06`, etc.

:::{warning} If there are multiple entries that maps to the same code point in
the `fpd`, then all other entries will be eventually be mapped to the first
entry in the ordered bidirectional dictionary.

This will lead to the loss of accuracy if the character graphics in the `fmp`
are different for the duplicate entries.
:::

The `fpd` is not used by the games internally except for the Nintendo DS version
of the games.

## The `fmp` format

The `fmp` format is a 4 bits per pixel (4bpp) bitmap format used by the Nintendo
DS versions of Puyo Puyo! 15th Anniversary and Puyo Puyo 7 to store the
graphical data of characters corresponding to the `fpd` file. Each character is
either 14x14 pixels (in `puyo14.fmp` and `test.fmp`) or 8x8 pixels
(in `puyo8.fmp`).

Although it uses a bit-depth that can encode 16 colors, the format is mainly
black and white with `0x0` and `0x1` encoding an off and on pixel respectively.
Each 4 bits or nibble, not byte, is stored in little-endian where the least
significant nibble is store first before the most significant nibble.

Pixels are stored row by row, in top-to-bottom and left-to-right order. There
are no headers or padding bytes in the file.

## The `mtx` format

The `mtx` format is a binary-encoded format used by older Puyo games for
storing character dialog and text.

:::{todo} Information about the mtx format for PP15 and PP7
:::

:::{todo} Look at the mtx format for PP20
:::
