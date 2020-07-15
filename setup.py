from setuptools import setup

setup(
        name='Sc2MapAnalyzer',
        version='0.1',
        py_modules=['sc2ma'],
        install_requires=[
                'Click',
        ],
        entry_points="""
        [console_scripts]
        sc2ma=sc2macli:cli
        """,
)
