import logging

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext

# https://stackoverflow.com/a/21621689/
class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())


mapping_module = Extension(
    'mapanalyzerext', sources=['MapAnalyzer/cext/src/ma_ext.c'], extra_compile_args=["-DNDEBUG", "-O2"]
)
logger = logging.getLogger(__name__)

requirements = [  # pragma: no cover
        "wheel",
        "numpy",
        "Cython",
        "burnysc2",
        "matplotlib",
        "scipy",
        "loguru",
        "tqdm",
        "scikit-image",
]
setup(  # pragma: no cover
        name="sc2mapanalyzer",
        # version=f"{__version__}",
        version="0.0.82",
        install_requires=requirements,
        setup_requires=["wheel", "numpy"],
        cmdclass={"build_ext": build_ext},
        ext_modules=[mapping_module],
        packages=["MapAnalyzer", "MapAnalyzer.cext"],
        extras_require={
                "dev": [
                        "pytest",
                        "pytest-html",
                        "monkeytype",
                        "mypy",
                        "mpyq",
                        "pytest-asyncio",
                        "hypothesis",
                        "pytest-benchmark",
                        "sphinx",
                        "sphinx-autodoc-typehints",
                        "pytest-cov",
                        "coverage",
                        "codecov",
                        "mutmut",
                        "radon",
                ]
        },
)
