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
release = '0.53'


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
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None



import easydev
import shutil
jscopybutton_path = easydev.copybutton.get_copybutton_path()
if os.path.isdir('_static')==False:
    os.mkdir('_static')
shutil.copy(jscopybutton_path, '_static')

todo_include_todos=True
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'restructuredtext',
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
html_theme_options = {
    'canonical_url': '',
  #  Provided by Google in your dashboard
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    # 'style_nav_header_background': 'grey',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
autosummary_generate = True
autodoc_typehints = 'description'
texinfo_show_urls = 'footnote'
rst_prolog = """
.. _Changelog: https://github.com/eladyaniv01/SC2MapAnalysis/blob/master/CHANGELOG.md
.. |MasterBuildIMG| image:: https://github.com/eladyaniv01/SC2MapAnalysis/workflows/Build/badge.svg?branch-master
.. |VersionBuildIMG| image:: https://img.shields.io/github/package-json/v/eladyaniv01/SC2MapAnalysis?color-blue&logo-EladYaniv01&style-plastic
.. raw:: html

    <p><img style="display: block; margin-left: auto; margin-right: auto;" src="https://img.shields.io/github/package-json/v/eladyaniv01/SC2MapAnalysis?color-blue&amp;logo-EladYaniv01&amp;style-plastic" width="109" height="21" /></p>
    <p><a href="https://github.com/eladyaniv01/SC2MapAnalysis/tree/master" target="_"><img style="display: block; margin-left: auto; margin-right: auto;" src="https://github.com/eladyaniv01/SC2MapAnalysis/workflows/Build/badge.svg?branch-master" /></a></p>
    <script type="text/javascript">
    <!-- Adds target=_blank to external links -->

    $(document).ready(function () {
      $('a[href^="http://"], a[href^="https://"]').not('a[class*=internal]').attr('target', '_blank');
    });
  </script>
"""
# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']
# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
        'https://docs.python.org/': None,
        'https://burnysc2.github.io/python-sc2/docs/': None,
        'https://numpy.org/doc/stable/': None,
        'https://docs.scipy.org/doc/scipy/reference': None,
        'https://matplotlib.org': None,
        'https://docs.h5py.org/en/latest/': None,
        'https://www.sphinx-doc.org/en/stable/': None,
        # 'https://docs.djangoproject.com/en/dev/': None,
        'https://www.attrs.org/en/stable/': None,
        'https://sarge.readthedocs.io/en/latest/': None
                       }

def setup(app):
# app.add_stylesheet('custom.css') # remove line numbers
    app.add_js_file('copybutton.js') # show/hide prompt >>>
# use :numref: for references (instead of :ref:)
numfig = True
smart_quotes = True
html_use_smartypants = True

