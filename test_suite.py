import logging
import os
import random
from random import randint
from typing import Iterable, List

from _pytest.python import Metafunc
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


def get_map_file_list() -> List[str]:
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


#
@given(st.integers(min_value=1, max_value=100), st.integers(min_value=1, max_value=100))
@settings(max_examples=5, deadline=None, verbosity=3, print_blob=True)
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
def pytest_generate_tests(metafunc: Metafunc) -> None:
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

    def test_mapdata(self, map_data: MapData) -> None:
        # test methods
        # logger.info(msg=f"Loaded Map : {map_data.bot.game_info.map_name}, n,m = {n}, {m}")
        # coverage
        map_data.save_plot()

    def test_polygon(self, map_data: MapData) -> None:
        for region in map_data.regions.values():
            region.polygon.plot(testing=True)

            for point in region.polygon.points:
                assert (region.polygon.is_inside_indices(point) is True)
                assert (region.polygon.is_inside_point(point) is True)

            assert (region in region.polygon.regions)

            for point in region.polygon.corner_points:
                assert (region in map_data.where_all(point))
                assert (point in region.polygon.corner_array)

            assert (region.polygon.nodes == list(region.polygon.points))

            for point in region.polygon.perimeter_points:
                assert (region.polygon.is_inside_point(point) is True), f"point {point}"

    def test_regions(self, map_data: MapData) -> None:
        for region in map_data.regions.values():
            assert isinstance(
                    map_data.where(region.center), Region
            ), f"<MD : {map_data}, Region : {region}," \
                f" where :  {map_data.where(region.center)} point : {region.center}>"

            # todo  test these,   currently here for cov
            assert (region in map_data.where_all(region.center))
            region.plot(testing=True)
            assert (region.corners is region.polygon.corner_points)
            # noinspection PyStatementEffect
            region.base_locations

    def test_chokes(self, map_data: MapData) -> None:
        for choke in map_data.map_chokes:
            assert isinstance(
                    map_data.where(choke.center), (Region, Polygon, ChokeArea)
            ), f"<Map : {map_data}, Choke : {choke}," \
                f" where :  {map_data.where(choke.center)} point : {choke.center}>"
            map_data.where_all(choke.center)
            # ChokeArea
            assert (choke.get_width() > 0)

    def test_ramps(self, map_data: MapData) -> None:
        for mdramp in map_data.map_ramps:
            assert isinstance(
                    map_data.where(mdramp.center), (Region, Polygon, MDRamp)
            ), f"<Map : {map_data}, MDRamp : {mdramp}," \
                f" where :  {map_data.where(mdramp.center)} point : {mdramp.center}>"
            map_data.where_all(mdramp.center)
            # MDRamp
