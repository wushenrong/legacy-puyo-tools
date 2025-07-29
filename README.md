# Legacy Puyo Tools

A command line tool for modding older Puyo Puyo games (Yes, the name is using a
[reversed naming scheme](https://github.com/microsoft/WSL)).

## Why

[Puyo Text Editor](https://github.com/nickworonekin/puyo-text-editor),
[fntedit](https://github.com/exelotl/fntedit), and other tools already can
modify formats used by older Puyo Puyo games. However, there are advantages to
rewrite them in Python:

- Better cross compatibility with Linux.
- Easier migration when upgrade away from end of life language versions.
- Formats are stored in an intermediate representation before conversion.

This project also aims to document how these formats work, so others can
reimplement them if needed.

## Progress Report

Current progress on implementing conversion and creation support for formats
that are used by the older Puyo Puyo games. Includes regression testing and
documentation. Additional formats may be added if there is a need to modify
other Puyo Puyo games.

-   Legend:
    - ✅ Fully Complete
    - ⚠️ Partially Complete
    - ❌ Incomplete

| Format | Conversion | Creation | Testing | Documentation |
| ------ | ---------- | -------- | ------- | ------------- |
| `fmp`  | ✅        | ✅       | ❌      | ✅           |
| `fnt`  | ❌        | ❌       | ❌      | ❌           |
| `fpd`  | ✅        | ✅       | ✅      | ✅           |
| `mtx`  | ⚠️        | ❌       | ❌      | ❌           |
