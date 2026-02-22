# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Path setup --------------------------------------------------------------
# Add the src directory so autodoc can find the package.
sys.path.insert(0, os.path.abspath(os.path.join("..", "src")))

# Mock modules that may not be installed in the doc-build environment.
autodoc_mock_imports = ["pygame"]

# -- Project information -----------------------------------------------------
project = "escapy"
copyright = "2026, Matteo Zeccoli Marazzini"
author = "Matteo Zeccoli Marazzini"
release = "0.0.1"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "myst_parser",
]

# MyST (Markdown) settings
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
myst_heading_anchors = 3

# Napoleon settings (Google/NumPy style docstrings)
napoleon_google_docstrings = True
napoleon_numpy_docstrings = False
napoleon_include_init_with_doc = True

# Autodoc settings
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pygame": ("https://www.pygame.org/docs", None),
}

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "titles_only": False,
}
html_static_path = ["_static"]

# Suppress warnings about missing references to type aliases and pygame types
nitpicky = False

# Suppress duplicate object description warnings caused by re-exports
suppress_warnings = ["duplicate.object.description"]
