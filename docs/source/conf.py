"""Configuration options for the Sphinx documentation builder."""

from __future__ import annotations

from sphinx_pyproject import SphinxConfig

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

config = SphinxConfig("../../pyproject.toml", globalns=globals())

project = config.name
author = config.author
release = version = config.version

# Links to other documentation
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "bidict": ("https://bidict.readthedocs.io/en/main/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pillow": ("https://pillow.readthedocs.io/en/stable/", None),
}
