import logging
import os
import random
from random import randint
from typing import Iterable

from hypothesis import given, settings, strategies as st

from MapAnalyzer import ChokeArea, MDRamp, Polygon, Region
from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import mock_map_data

# for merging pr from forks,  git push <pr-repo.git> <your-local-branch-name>:<pr-branch-name>
# pytest -v --disable-warnings
# mutmut run --paths-to-mutate test_suite.py --runner pytest
# radon cc . -a -nb  (will dump only complexity score of B and below)
# monkeytype run monkeytest.py
# monkeytype list-modules
# mutmut run --paths-to-mutate MapAnalyzer/MapData.py
logger = logging.getLogger(__name__)


def get_map_file_list():
    """
    easy way to produce less than all maps,  for example if we want to test utils, we only need one MapData object
    """
    subfolder = "MapAnalyzer"
    subfolder2 = "pickle_gameinfo"
    subfolder = os.path.join(subfolder, subfolder2)
    folder = os.path.abspath(".")
    map_files_folder = os.path.join(folder, subfolder)
    map_files = os.listdir(map_files_folder)
    li = []
    for map_file in map_files:
        li.append(os.path.join(map_files_folder, map_file))
    return li


def get_map_datas() -> Iterable[MapData]:
    subfolder = "MapAnalyzer"
    subfolder2 = "pickle_gameinfo"
    subfolder = os.path.join(subfolder, subfolder2)
    folder = os.path.abspath(".")
    map_files_folder = os.path.join(folder, subfolder)
    map_files = os.listdir(map_files_folder)
    # yield mock_map_data(map_file=os.path.join(map_files_folder, map_files[0]))
    for map_file in map_files:
        yield mock_map_data(map_file=os.path.join(map_files_folder, map_file))


@given(st.integers(min_value=1, max_value=100), st.integers(min_value=1, max_value=100))
@settings(max_examples=10, deadline=None, verbosity=3, print_blob=True)
def test_mapdata(n, m):
    map_files = get_map_file_list()
    map_data = mock_map_data(random.choice(map_files))
    # test methods
    # logger.info(msg=f"Loaded Map : {map_data.bot.game_info.map_name}, n,m = {n}, {m}")
    points = [(i, j) for i in range(n + 1) for j in range(m + 1)]
    set_points = set(points)
    indices = map_data.points_to_indices(set_points)
    i = randint(0, n)
    j = randint(0, m)
    assert (i, j) in points
    assert (i, j) in set_points
    assert i in indices[0] and j in indices[1]
    new_points = map_data.indices_to_points(indices)
    assert new_points == set_points


# From https://docs.pytest.org/en/latest/example/parametrize.html#a-quick-port-of-testscenarios
def pytest_generate_tests(metafunc):
    idlist = []
    argvalues = []
    if metafunc.cls is not None:
        for scenario in metafunc.cls.scenarios:
            idlist.append(scenario[0])
            items = scenario[1].items()
            argnames = [x[0] for x in items]
            argvalues.append(([x[1] for x in items]))
        metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


class TestSuit:
    """
    Test DocString
    """
    scenarios = [(f"Testing {md.bot.game_info.map_name}", {"map_data": md}) for md in get_map_datas()]

    def test_mapdata(self, map_data: MapData):
        # test methods
        # logger.info(msg=f"Loaded Map : {map_data.bot.game_info.map_name}, n,m = {n}, {m}")
        # coverage
        map_data.save_plot()

    def test_region_polygon(self, map_data: MapData):
        for region in map_data.regions.values():
            assert isinstance(
                    map_data.where(region.center), Region
            ), f"<MD : {map_data}, Region : {region}," \
                f" where :  {map_data.where(region.center)} point : {region.center}>"

            # todo  test these,   currently here for cov

            # polygon
            region.polygon.plot(testing=True)

            # noinspection PyStatementEffect
            region.polygon.is_inside_indices

            # noinspection PyStatementEffect
            region.polygon.is_inside_point

            # noinspection PyStatementEffect
            region.polygon.region

            # noinspection PyStatementEffect
            region.polygon.corner_points

            # noinspection PyStatementEffect
            region.polygon.corner_array

            # noinspection PyStatementEffect
            region.polygon.nodes

            # noinspection PyStatementEffect
            region.polygon.perimeter

            # region
            region.plot(testing=True)

            # noinspection PyStatementEffect
            region.corners

            # noinspection PyStatementEffect
            region.base_locations

    def test_chokes(self, map_data: MapData):
        for choke in map_data.map_chokes:
            assert isinstance(
                    map_data.where(choke.center), (Region, Polygon, ChokeArea)
            ), f"<Map : {map_data}, Choke : {choke}," \
                f" where :  {map_data.where(choke.center)} point : {choke.center}>"

            # ChokeArea
            choke.get_width()

    def test_ramps(self, map_data: MapData):
        for mdramp in map_data.map_ramps:
            assert isinstance(
                    map_data.where(mdramp.center), (Region, Polygon, MDRamp)
            ), f"<Map : {map_data}, MDRamp : {mdramp}," \
                f" where :  {map_data.where(mdramp.center)} point : {mdramp.center}>"

            # MDRamp

# map_files = get_map_file_list()
#
# for file in map_files:
#     MD = mock_map_data(file)
#     regress_map(MD)


# class TestSuit:
#     """
#     Test DocString
#     """
#
#     @pytest.mark.hypothesis
#     def test_example(self, x):
# def test_data_conversion(self) -> None:
#     """
#     Test that the manipulation of points indices and arrays is consistent
#     """
#
#     map_file = "AbyssalReefLE.xz"
#     with lzma.open(f"MapAnalyzer/pickle_gameinfo/{map_file}", "rb") as f:
#         raw_game_data, raw_game_info, raw_observation = pickle.load(f)
#
#     bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
#     map_data = MapData(bot=bot)
#     n = randint(0, 999)
#     m = randint(0, 999)
#     points = [(i, j) for i in range(n) for j in range(m)]
#     set_points = set(points)
#     indices = map_data.points_to_indices(set_points)
#     i = randint(0, n)
#     j = randint(0, m)
#     assert (i, j) in points
#     assert (i, j) in set_points
#     assert i in indices[0] and j in indices[1]
#     new_points = map_data.indices_to_points(indices)
#     assert new_points == set_points

# def test_sanity(self) -> None:
#     """
#     Test that every cell in the map is defined by an Area Object
#     """
#     subfolder = "MapAnalyzer"
#     subfolder2 = "pickle_gameinfo"
#     subfolder = os.path.join(subfolder, subfolder2)
#     folder = os.path.abspath(".")
#     map_files_folder = os.path.join(folder, subfolder)
#     map_files = os.listdir(map_files_folder)
#
#     for map_file in map_files:
#         count = 0
#         file_path = os.path.join(map_files_folder, map_file)
#         map_data = mock_map_data(map_file=file_path)
#         logger.info(msg=f"Loaded Map : {map_data.bot.game_info.map_name}")
#         start = time.time()
#         map_data.save_plot()
#         for region in map_data.regions.values():
#             assert isinstance(
#                     map_data.where(region.center), Region
#             ), f"<Map : {map_file}, Region : {region}," \
#                 f" where :  {map_data.where(region.center)} point : {region.center}>"
#
#             # todo  test these,   currently here for cov
#
#             # polygon
#             region.polygon.plot(testing=True)
#
#             # noinspection PyStatementEffect
#             region.polygon.is_inside_indices
#
#             # noinspection PyStatementEffect
#             region.polygon.is_inside_point
#
#             # noinspection PyStatementEffect
#             region.polygon.region
#
#             # noinspection PyStatementEffect
#             region.polygon.corner_points
#
#             # noinspection PyStatementEffect
#             region.polygon.corner_array
#
#             # noinspection PyStatementEffect
#             region.polygon.nodes
#
#             # noinspection PyStatementEffect
#             region.polygon.perimeter
#
#
#             # region
#             region.plot(testing=True)
#
#             # noinspection PyStatementEffect
#             region.corners
#
#             # noinspection PyStatementEffect
#             region.base_locations
#
#
#         for choke in map_data.map_chokes:
#             assert isinstance(
#                     map_data.where(choke.center), (Region, Polygon, ChokeArea)
#             ), f"<Map : {map_file}, Choke : {choke}," \
#                 f" where :  {map_data.where(choke.center)} point : {choke.center}>"
#
#             # ChokeArea
#             choke.get_width()
#
#         for mdramp in map_data.map_ramps:
#             assert isinstance(
#                     map_data.where(mdramp.center), (Region, Polygon, MDRamp)
#             ), f"<Map : {map_file}, MDRamp : {mdramp}," \
#                 f" where :  {map_data.where(mdramp.center)} point : {mdramp.center}>"
#
#             # MDRamp
#         end = time.time()
#
#         logger.info(
#                 msg=f"Finished {map_data.bot.game_info.map_name},  {count} Queries in [{end - start}]"
#                 f"<avg query = {(end - start) / count}>"
#         )
