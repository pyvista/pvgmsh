"""
Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

from __future__ import annotations

import datetime
from importlib.metadata import version as get_version
import os
from pathlib import Path

import pyvista
from pyvista.plotting.utilities.sphinx_gallery import DynamicScraper

pyvista.set_error_output_file("errors.txt")
pyvista.OFF_SCREEN = True  # Not necessary - simply an insurance policy
pyvista.set_plot_theme("document")
pyvista.BUILDING_GALLERY = True
os.environ["PYVISTA_BUILDING_GALLERY"] = "true"

if os.environ.get("READTHEDOCS") or os.environ.get("CI"):
    pyvista.start_xvfb()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "scikit-gmsh"
copyright_years = f"2024 - {datetime.datetime.now(datetime.UTC).year}"
copyright = "2024, Tetsuo Koyama"  # noqa: A001
author = f"{project} Contributors"
on_rtd = os.environ.get("READTHEDOCS")

if on_rtd:
    # https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#including-content-based-on-tags
    # https://www.sphinx-doc.org/en/master/usage/configuration.html#conf-tags
    tags.add("on_rtd")  # noqa: F821

# The full version, including alpha/beta/rc tags
release = get_version("scikit-gmsh")
release = release.removesuffix("+dirty")

# docs src directory
src_dir = Path(__file__).absolute().parent
root_dir = src_dir.parents[1]
package_dir = root_dir / "src"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser", "pyvista.ext.plot_directive", "pyvista.ext.viewer_directive", "sphinx_design", "sphinx_gallery.gen_gallery"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_logo = "_static/small_logo.svg"

html_context = {
    "github_url": "https://github.com",
    "github_user": "pyvista",
    "github_repo": "scikit-gmsh",
    "github_version": "main",
    "doc_path": "docs/src",
}

html_theme_options = {
    "home_page_in_toc": True,
    "icon_links": [
        {
            "name": "GitHub Discussions",
            "url": "https://github.com/pyvista/scikit-gmsh/discussions",
            "icon": "fa fa-comments fa-fw",
        },
        {
            "name": "GitHub Issues",
            "url": "https://github.com/pyvista/scikit-gmsh/issues",
            "icon": "fa-brands fa-square-github fa-fw",
        },
        {
            "name": "GitHub Pulls",
            "url": "https://github.com/pyvista/scikit-gmsh/pulls",
            "icon": "fa-brands fa-github-alt fa-fw",
        },
    ],
    "navigation_with_keys": False,
    "path_to_docs": "docs/src",
    "repository_branch": "main",
    "repository_url": "https://github.com/pyvista/scikit-gmsh",
    "show_prev_next": True,
    "show_toc_level": 4,
    "toc_title": "On this page",
    "use_download_button": True,
    "use_edit_page_button": False,
    "use_fullscreen_button": True,
    "use_issues_button": False,
    "use_repository_button": True,
    "use_sidenotes": True,
    "use_source_button": False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = [
    "_static",
]
html_css_files = [
    "style.css",
    "theme_overrides.css",
]

# -- MyST settings -----------------------------------------------------------

myst_enable_extensions = [
    "amsmath",
    "attrs_block",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# -- sphinx_gallery settings -------------------------------------------------

sphinx_gallery_conf = {
    "backreferences_dir": None,
    "doc_module": "pyvista",
    "download_all_examples": False,
    "examples_dirs": ["../examples/"],
    "filename_pattern": r"\.py",
    "first_notebook_cell": ("%matplotlib inline\nfrom pyvista import set_plot_theme\nset_plot_theme('document')\n"),
    "gallery_dirs": ["./examples"],
    "image_scrapers": (DynamicScraper(), "matplotlib"),
    "pypandoc": True,
    "remove_config_comments": True,
    "reset_modules_order": "both",
}
