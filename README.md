# Legacy Puyo Tools

A command line tool for modding older Puyo Puyo games (Yes, the name is using a
[reversed naming scheme](https://github.com/microsoft/WSL)).

This project is still in development, expect **major breaking changes** over its
lifetime.

## Why

[Puyo Text Editor](https://github.com/nickworonekin/puyo-text-editor),
[fntedit](https://github.com/exelotl/fntedit), and other tools already can
modify file formats used by older Puyo Puyo games. However, there are advantages
to rewrite them in Python:

- Better cross compatibility with Linux.
- Easier migration when upgrade away from end of life language versions.
- File formats are stored in an intermediate representation before conversion.

This project also aims to document how these formats work, so others can
reimplement them if needed.

## Support Progress

Current progress on implementing conversion and creation support for file
formats that are used by the older Puyo Puyo games. Includes regression testing
and documentation. Additional file formats may be added if there is a need to
modify other Puyo Puyo games.

-   Legend:
    - ✅ Fully Supported
    - ⚠️ Partially Supported
    - ❌ Unsupported

<table>
    <thead>
        <tr>
            <th scope="col">Format</th>
            <th scope="col">Conversion</th>
            <th scope="col">Creation</th>
            <th scope="col">Testing</th>
            <th scope="col">Documentation</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <th scope="row"><code>fmp</code></th>
            <td>✅</td>
            <td>✅</td>
            <td>✅</td>
            <td>✅</td>
        </tr>
        <tr>
            <th scope="row"><code>fnt</code></th>
            <td>❌</td>
            <td>❌</td>
            <td>❌</td>
            <td>❌</td>
        </tr>
        <tr>
            <th scope="row"><code>fpd</code></th>
            <td>✅</td>
            <td>✅</td>
            <td>✅</td>
            <td>✅</td>
        </tr>
        <tr>
            <th scope="row"><code>mtx</code></th>
            <td>⚠️</td>
            <td>❌</td>
            <td>❌</td>
            <td>❌</td>
        </tr>
    </tbody>
</table>
