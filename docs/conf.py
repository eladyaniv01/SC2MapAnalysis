# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('MapAnalyzer'))



# -- Project information -----------------------------------------------------

project = 'Sc2MapAnalyzer'
copyright = '2020, Elad Yaniv'
author = 'Elad Yaniv'

# The full version, including alpha/beta/rc tags
release = '0.0.53'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.


extensions = ['sphinx.ext.viewcode',
                "sphinx_rtd_theme",
              'sphinx.ext.napoleon',
              'sphinx.ext.autodoc',
              'easydev.copybutton',
              'sphinx.ext.autosummary',
              'sphinx.ext.coverage',
              'sphinx.ext.graphviz',
              'sphinx.ext.doctest',
              'sphinx.ext.intersphinx',
              'sphinx.ext.todo',
              'sphinx.ext.imgmath',
              'sphinx.ext.ifconfig',
              'matplotlib.sphinxext.plot_directive',
              'recommonmark'
              ]

import easydev
import shutil
jscopybutton_path = easydev.copybutton.get_copybutton_path()
if os.path.isdir('_static')==False:
    os.mkdir('_static')
shutil.copy(jscopybutton_path, '_static')

todo_include_todos=True
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}
# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

viewcode_follow_imported_members = True
# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'agogo'
html_theme = "sphinx_rtd_theme"
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']