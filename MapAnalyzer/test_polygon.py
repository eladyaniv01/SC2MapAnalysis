# import os
# from typing import List
#
# from MapAnalyzer.utils import mock_map_data
#
#
# def get_map_file_list() -> List[str]:
#     """
#     easy way to produce less than all maps,  for example if we want to test utils, we only need one MapData object
#     """
#     subfolder = "MapAnalyzer"
#     subfolder2 = "pickle_gameinfo"
#     subfolder = os.path.join(subfolder, subfolder2)
#     folder = os.path.abspath(".")
#     map_files_folder = os.path.join(folder, subfolder)
#     map_files = os.listdir(map_files_folder)
#     li = []
#     for map_file in map_files:
#         li.append(os.path.join(map_files_folder, map_file))
#     return li

#
# class TestPolygon:
#
#     def __init__(self, map_file):
#         self.map_file = map_file
#         self.map_data = mock_map_data(map_file=map_file)
#
#     def test_plot(self):
#         self.fail()
#
#     def test_nodes(self):
#         self.fail()
#
#     def test_corner_array(self):
#         self.fail()
#
#     def test_corner_points(self):
#         self.fail()
#
#     def test_center(self):
#         self.fail()
#
#     def test_is_inside_point(self):
#         self.fail()
#
#     def test_is_inside_indices(self):
#         self.fail()
#
#     def test_perimeter(self):
#         self.fail()
#
#     def test_perimeter_points(self):
#         self.fail()
#
#     def test_area(self):
#         self.fail()
