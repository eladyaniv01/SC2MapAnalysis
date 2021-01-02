from .mocksetup import *
from MapAnalyzer.utils import get_map_files_folder
from MapAnalyzer.settings import ROOT_DIR
import doctest

goldenwall = os.path.join(get_map_files_folder(), 'GoldenWallLE.xz')
map_data = mock_map_data(goldenwall)


"""
uncomment and run the function below to test doc strings without running the entire test suite 
"""

# def test_docstrings() -> None:
#     test_files = []
#     for root, dirs, files in os.walk(ROOT_DIR):
#         for f in files:
#             if f.endswith('.py'):
#                 test_files.append(os.path.join(root, f))
#     for f in test_files:
#         print(f)
#         doctest.testfile(f"{f}", extraglobs={'self': map_data}, verbose=True)
