# File Formats

Below are the formats that are used by the older Puyo Puyo games and how they
are structured.

:::{todo} Add formats that is out of scope for this project.
:::

## The `fmp` format

The `fmp` format is a 4 bits per pixel (4bpp) bitmap format used by the Nintendo
DS (NDS) versions of Puyo Puyo! 15th Anniversary and Puyo Puyo 7 to store the
graphical data of characters corresponding to the
[`fpd` format](#the-fpd-format). Each character is either 14x14 pixels
(in `puyo14.fmp` and `test.fmp`) or 8x8 pixels (in `puyo8.fmp`).

Although it uses a bit-depth that can encode 16 colors, the format is mainly
black and white with `0x0` and `0x1` encoding an off and on pixel respectively.
Each 4 bits or nibble, not byte, is stored in little-endian where the least
significant nibble is store first before the most significant nibble.

Pixels are stored row by row, in top-to-bottom and left-to-right order. There
are no headers or padding bytes in the file.

It can be expressed in the following C struct:

```c
struct Fmp {
    unsigned char /* uint8_t */
    graphics[NUMBER_OF_ENTRIES][FONT_WIDTH * FONT_WIDTH / 2];
};
```

## The `fnt` format

The `fnt` format is a binary character table format used by Puyo Puyo!! 20th
Anniversary to map indexes used by the [`mtx` format](#the-mtx-format) to
Unicode characters and graphic. This is essentially the [`fpd`](#the-fpd-format)
and [`fmp`](#the-fmp-format) formats combined. This format has three separate
versions for the NDS, Wii, and the PlayStation Portable (PSP). All three formats
start with the `fnt` header, starting with a magic number for identification
`FNT\0`, the height of the character graphics, the width of the character
graphics, and the number of character entries as a 32-bit unsigned integer. The
NDS version has a second header with a magic number
`0xE0 0x03 0xFF 0x7F 0xC6 0x18` then 26 zeros. While the Wii and PSP only have
their identification strings at the end of the file, `GCIX` or `GVRT` for the
Wii and `MIG.00.1PSP` for the PSP. Each character entry is 4 bytes long and
formatted as follows: `XX XX YY YY`. Where `XX XX` is the character's Unicode
code point in little-endian and `YY YY` is the width of the character. Then the
entry may have an optional character graphic, that is only used in the NDS
version, whose width and height is from the `fnt` header and in the same bitmap
format as the [`fmp` format](#the-fmp-format).

It can be expressed in the following C structs:

```c
struct FntHeader {
    const char magic_number[4]; // "FNT\0"
    uint32_t font_height;
    uint32_t font_width;
    uint32_t number_of_entries;
};

struct FntEntry {
    char16_t character;
    uint16_t width;
    // This only exists in the NDS version of Puyo Puyo!! 20th Anniversary
    unsigned char /* uint8_t */ graphic[FONT_WIDTH * FONT_HEIGHT / 2];
};

struct FntNDS {
    struct FntHeader header;
    // 0xe0, 0x03, 0xff, 0x7f, 0xc6, 0x18, 0x00... (26 times).
    const unsigned char nds_header[32];
    struct FntEntry entries[number_of_entries];
};

struct FntWII {
    struct FntHeader header;
    struct FntEntry entries[number_of_entries];
    const char wii_identification[4]; // "GCIX" or "GVRT"
};

struct FntPSP {
    struct FntHeader fnt_header;
    struct FntEntry entries[number_of_entries];
    const char psp_identification[11]; // "MIG.00.1PSP"
};
```

## The `fpd` format

The `fpd` format is a binary character table format used by the developers of
Puyo Puyo! 15th Anniversary and Puyo Puyo 7 to map indexes used by the
[`mtx` format](#the-mtx-format) to Unicode characters. Each character entry in
the `fpd` is 3 bytes long and formatted as follows: `XX XX YY`. Where `XX XX` is
the character's Unicode code point in little-endian and `YY` is the width of the
character. Due to only having two bytes to store the character, this format
cannot store surrogate pairs and only encodes the Basic Multilingual Plane which
goes from `U+0000` to `U+FFFF`.

:::{note} The character encoding is UTF-16 little-endian. But pedantically it is
the older UCS-2 encoding, which is deprecated.
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

It can be expressed as the following C structs:

```c
struct FpdEntry {
    char16_t character;
    uint8_t width;
};

struct Fpd {
    struct FpdEntry entries[NUMBER_OF_ENTRIES];
};
```

## The `mtx` format

The `mtx` format is a binary-encoded format used by older Puyo games for
storing character dialog and text.

:::{todo} Information about the mtx format for PP15, PP7 and PP20.
:::
