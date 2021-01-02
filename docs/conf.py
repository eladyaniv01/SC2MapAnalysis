# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import easydev
import shutil

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('MapAnalyzer'))

# -- Project information -----------------------------------------------------

project = 'Sc2MapAnalyzer'
copyright = '2020, Elad Yaniv'
author = 'Elad Yaniv'

# The full version, including alpha/beta/rc tags
from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution('sc2mapanalyzer').version
except DistributionNotFound:
    __version__ = 'dev'

release = __version__
html_theme = "sphinx_rtd_theme"
# html_theme = 'yummy_sphinx_theme'
# html_theme = 'trstyle'
# html_theme = 'sphinxjp.themes.trstyle'

# import caktus_theme
# html_theme = 'caktus'
# html_theme_path = [caktus_theme.get_theme_dir()]
# html_sidebars = caktus_theme.default_sidebars()

# html_theme = 'sphinxdoc'
# html_theme = 'groundwork'
# -- General configuration ---------------------------------------------------

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
              'recommonmark',
              'rinoh.frontend.sphinx',
              'sphinxjp.themecore']

autodoc_mock_imports = ["sc2pathlibp"]

extensions.append('autoapi.extension')
autoapi_options =[ 'members',
                   'show-inheritance',
                   'inherited-member',
                   'show-module-summary',
                   'imported-members']
autoapi_type = 'python'
autoapi_dirs = ['D:\proj\SC2MapAnalysis\MapAnalyzer']

autoapi_root = 'source'
autoapi_ignore = ["*sc2pathlibp*"]

autoapi_keep_files = True
autoapi_generate_api_docs = True
# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
# exclude_patterns = ['technical']

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

jscopybutton_path = easydev.copybutton.get_copybutton_path()
if os.path.isdir('_static') == False:
    os.mkdir('_static')
shutil.copy(jscopybutton_path, '_static')

todo_include_todos = False
source_suffix = {
        '.rst': 'restructuredtext',
        '.txt': 'restructuredtext',
        '.md' : 'markdown',
}
# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']



viewcode_follow_imported_members = True
# -- Options for HTML output -------------------------------------------------


html_theme_options = {
        'canonical_url'             : '',
        #  Provided by Google in your dashboard
        'logo_only'                 : False,
        'display_version'           : True,
        'prev_next_buttons_location': 'bottom',
        'style_external_links'      : True,
        # 'style_nav_header_background': 'grey',
        # Toc options
        'collapse_navigation'       : True,
        'sticky_navigation'         : True,
        'navigation_depth'          : 4,
        'includehidden'             : False,
        'titles_only'               : False,
        'vcs_pageview_mode': 'view',
        'github_url': 'https://github.com/eladyaniv01/SC2MapAnalysis'
}
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
autosummary_generate = True
autodoc_typehints = 'description'
autodoc_default_options = {
        'autosummary': True,
}
texinfo_show_urls = 'footnote'

rst_epilog = """

**Indices and tables**

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`

"""

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
        ' https://docs.python.org/3/'                : None,
        'https://burnysc2.github.io/python-sc2/docs/': None,
        'https://numpy.org/doc/stable/'              : None,
        'https://docs.scipy.org/doc/scipy/reference' : None,
        'https://matplotlib.org'                     : None,
        'https://docs.h5py.org/en/latest/'           : None,
        ' https://www.sphinx-doc.org/en/master/'     : None,
        # 'https://docs.djangoproject.com/en/dev/': None,
        'https://www.attrs.org/en/stable/'           : None,
        'https://sarge.readthedocs.io/en/latest/'    : None
}


def setup(app):
    # app.add_stylesheet('custom.css') # remove line numbers
    app.add_js_file('copybutton.js')  # show/hide prompt >>>


# use :numref: for references (instead of :ref:)
numfig = True
smart_quotes = True
html_use_smartypants = True
latex_elements = {
    'fontpkg': r'''
\setmainfont{DejaVu Serif}
\setsansfont{DejaVu Sans}
\setmonofont{DejaVu Sans Mono}
''',
    'preamble': r'''
\usepackage[titles]{tocloft}
\cftsetpnumwidth {1.25cm}\cftsetrmarg{1.5cm}
\setlength{\cftchapnumwidth}{0.75cm}
\setlength{\cftsecindent}{\cftchapnumwidth}
\setlength{\cftsecnumwidth}{1.25cm}
''',
    'fncychap': r'\usepackage[Bjornstrup]{fncychap}',
    'printindex': r'\footnotesize\raggedright\printindex',
}
latex_show_urls = 'footnote'