import logging

from setuptools import setup

logger = logging.getLogger(__name__)


requirements = [  # pragma: no cover
        "Cython",
        "pyastar @ git+git://github.com/hjweide/pyastar.git@master#egg=pyastar",
        "burnysc2==4.11.16",
        "click==7.1.2",
        "matplotlib==3.2.2",
        "mpyq==0.2.5",
        "numpy==1.19.0",
        "scikit-image==0.17.2",
        "scipy==1.5.1",
        "six==1.15.0",
        "tifffile==2020.7.4",
        "yarl==1.4.2",
        "loguru==0.5.1",
        "tqdm"

]
setup(  # pragma: no cover
        name="sc2mapanalysis",
        version="0.0.1",
        install_requires=requirements,
        setup_requires=["wheel", "numpy"],
        extras_require={
                "dev": [
                        "pytest",
                        "pytest-html",
                        "monkeytype",
                        "mypy",
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
