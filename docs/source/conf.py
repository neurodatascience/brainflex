"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

from datetime import UTC, datetime

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "brainflex"
copyright = f"{datetime.now(tz=UTC).year}, NeuroDataScience-ORIGAMI Lab"
author = "NeuroDataScience-ORIGAMI Lab"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_togglebutton",
]

exclude_patterns = ["_includes"]

nitpicky = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_title = "brainflex"

# -- Furo configuration ------------------------------------------------------
#  https://pradyunsg.me/furo/customisation/#customisation

html_css_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/fontawesome.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/solid.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/brands.min.css",
]

html_theme_options = {
    "source_repository": "https://github.com/neurodatascience/brainflex",
    "source_branch": "main",
    "source_directory": "docs/source",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/neurodatascience/brainflex",
            "html": "",
            "class": "fa-brands fa-solid fa-github fa-2x",
        },
    ],
}

# -- MyST configuration -------------------------------------------------------

myst_enable_extensions = ["fieldlist", "substitution", "colon_fence"]

myst_heading_anchors = 5

# -- Copybutton configuration -------------------------------------------------
copybutton_exclude = ".linenos, .gp"
copybutton_selector = "div:not(.no-copybutton) > div.highlight > pre"

# -- Version substitution -----------------------------------------------------
# Replaced in all source and included files, including inside code blocks

node_version = "v0.1.1"
_SUBSTITUTIONS = {"|node_version|": node_version}


def _substitute(content: list[str]) -> None:
    """Replace substitution tokens in raw source content (in place)."""
    for token, value in _SUBSTITUTIONS.items():
        content[0] = content[0].replace(token, value)


def _on_source_read(app, docname, content) -> None:
    _substitute(content)


def _on_include_read(app, relative_path, parent_docname, content) -> None:
    _substitute(content)


def setup(app) -> None:
    """Register source substitution hooks."""
    app.connect("source-read", _on_source_read)
    app.connect("include-read", _on_include_read)
