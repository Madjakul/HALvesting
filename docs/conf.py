# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath(".."))
# sys.path.insert(0, os.path.abspath("_ext"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "HALvesting: Harvests open scientific papers from HAL."
copyright = "2024, Madjakul"
author = "Madjakul, WissamAntoun"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.mathjax",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.githubpages",
]

source_suffix = [".rst", ".md"]

edit_on_github_project = "Madjakul/HALvesting"
edit_on_github_branch = "main"

# templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "piccolo_theme"
html_theme_options = {
    "source_url": "https://github.com/Madjakul/HALvesting",
    "source_icon": "github",
}
html_short_title = "HALvesting"
# html_theme_options = {"collapse_navigation": False}
# html_static_path = ["_static"]

autosummary_generate = True

master_doc = "index"


# -- Options for autodoc -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

# Automatically extract typehints when specified and place them in
# descriptions of the relevant function/method
autodoc_typehints = "both"  # description
# autodoc_typehints_format = "short"

# Don't show class signature with the class' name
autoclass_content = "class"
autodoc_class_signature = "mixed"

autodoc_member_order = "groupwise"
autodoc_default_flags = [
    "members",
    # "private-members",
    "special-members",
    "inherited-members",
    "show-inheritance",
]
