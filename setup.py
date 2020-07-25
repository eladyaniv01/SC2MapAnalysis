from setuptools import setup  # pragma: no cover

requirements = [  # pragma: no cover
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
]
setup(  # pragma: no cover
        name="sc2mapanalysis",
        install_requires=requirements,
        extras_require={
                "dev": [
                        "pytest==5.4.3",
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
                        "loguru ",
                        "mutmut",
                        "radon",
                ]
        },
)
