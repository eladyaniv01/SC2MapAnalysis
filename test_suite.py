import logging
import lzma
import os
import pickle
import time
from random import randint

from MapAnalyzer import ChokeArea, MDRamp, Polygon, Region
from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import import_bot_instance, mock_map_data

logger = logging.getLogger(__name__)


# for merging pr from forks,  git push <pr-repo.git> <your-local-branch-name>:<pr-branch-name>
# pytest -v --disable-warnings
# mutmut run --paths-to-mutate test_suite.py --runner pytest
# radon cc . -a -nb  (will dump only complexity score of B and below)
# monkeytype run monkeytest.py
# monkeytype list-modules
# mutmut run --paths-to-mutate MapAnalyzer/MapData.py

class TestSuit:
    """
    Test DocString
    """

    def test_data_conversion(self) -> None:
        """
        Test that the manipulation of points indices and arrays is consistent
        """

        map_file = "AbyssalReefLE.xz"
        with lzma.open(f"MapAnalyzer/pickle_gameinfo/{map_file}", "rb") as f:
            raw_game_data, raw_game_info, raw_observation = pickle.load(f)

        bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
        map_data = MapData(bot=bot)
        n = 1000
        points = [(i, j) for i in range(n) for j in range(n)]
        set_points = set(points)
        indices = map_data.points_to_indices(set_points)
        i = randint(0, 999)
        j = randint(0, 999)
        assert (i, j) in points
        assert (i, j) in set_points
        assert i in indices[0] and j in indices[1]
        new_points = map_data.indices_to_points(indices)
        assert new_points == set_points

    def test_sanity(self) -> None:
        """
        Test that every cell in the map is defined by an Area Object
        """
        subfolder = "MapAnalyzer"
        subfolder2 = "pickle_gameinfo"
        subfolder = os.path.join(subfolder, subfolder2)
        folder = os.path.abspath(".")
        map_files_folder = os.path.join(folder, subfolder)
        map_files = os.listdir(map_files_folder)
        for map_file in map_files:
            file_path = os.path.join(map_files_folder, map_file)
            map_data = mock_map_data(map_file=file_path)
            logger.info(msg=f"Loaded Map : {map_data.bot.game_info.map_name}")
            start = time.time()
            map_data.save_plot()
            for region in map_data.regions.values():
                assert isinstance(
                        map_data.where(region.center), Region
                ), f"<Map : {map_file}, Region : {region}," \
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

            for choke in map_data.map_chokes:
                assert isinstance(
                        map_data.where(choke.center), (Region, Polygon, ChokeArea)
                ), f"<Map : {map_file}, Choke : {choke}," \
                    f" where :  {map_data.where(choke.center)} point : {choke.center}>"

                # ChokeArea
                choke.get_width()

            for mdramp in map_data.map_ramps:
                assert isinstance(
                        map_data.where(mdramp.center), (Region, Polygon, MDRamp)
                ), f"<Map : {map_file}, MDRamp : {mdramp}," \
                    f" where :  {map_data.where(mdramp.center)} point : {mdramp.center}>"
                # MDRamp
            end = time.time()

            logger.info(
                    msg=f"Finished Testing Map : {map_data.bot.game_info.map_name} [{end - start}]"
            )
