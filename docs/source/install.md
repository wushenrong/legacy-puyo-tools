# Installation

Install [Python](https://www.python.org/) 3.10 or later, preferably the latest
version.

`legacy-puyo-tools` is published on PyPI. It is recommended to install external
Python packages into a virtual environment so they do not conflict with each
other. There are several tools that can do this automatically for you like
[`pipx`](https://pipx.pypa.io) and [`uv`](https://docs.astral.sh/uv).

Or create a virtual Python environment yourself by using
[`virualenv`](https://virtualenv.pypa.io) or the built-in `venv` library, and
use [`pip`](https://pip.pypa.io/en/stable/) to install packages.

:::{tab} `pipx`

```bash
pipx install legacy-python-tools
# Or to run the cli without installing legacy-python-tools
pipx run legacy-python-tools
```

:::

:::{tab} `uv`

```bash
uv tool install legacy-python-tools
# Or to run the cli without installing legacy-python-tools
uvx legacy-python-tools
```

:::

:::{tab} `pip`

```bash
pip install -U legacy-python-tools
```

:::

## GitHub Releases

Packages are also published to
[GitHub Releases](https://github.com/wushenrong/legacy-puyo-tools/releases).

You can also directly install from the GitHub repository if you want the latest,
unstable version of `legacy-python-tools`.
