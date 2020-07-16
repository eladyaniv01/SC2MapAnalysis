import lzma
import pickle
from random import randint

from MapAnalyzer import ChokeArea, MDRamp, Polygon, Region
from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import import_bot_instance


# for merging pr from forks,  git push <pr-repo.git> <your-local-branch-name>:<pr-branch-name>
# pytest -v --disable-warnings
# radon cc . -a -nb  (will dump only complexity score of B and below)


class TestSuit:
    """
    Test DocString
    """


    def test_data_convertion(self):
        """
        Test that the manipulation of points indices and arrays is consistent
        """

        map_file = "AbyssalReefLE.xz"
        with lzma.open(f"MapAnalyzer/pickle_gameinfo/{map_file}", "rb") as f:
            raw_game_data, raw_game_info, raw_observation = pickle.load(f)

        bot = import_bot_instance(
                raw_game_data, raw_game_info, raw_observation
        )
        map_data = MapData(bot=bot)
        N = 1000
        points = [(i, j) for i in range(N) for j in range(N)]
        set_points = set(points)
        indices = map_data.points_to_indices(set_points)
        i = randint(0, 999)
        j = randint(0, 999)
        assert (i, j) in points
        assert (i, j) in set_points
        assert i in indices[0] and j in indices[1]
        new_points = map_data.indices_to_points(indices)
        assert new_points == set_points

    def test_sanity(self):
        """
        Test that every cell in the map is defined by an Area Object
        """
        maps = [
                "GoldenWallLE.xz",
                # "DeathAuraLE.xz",
                "SubmarineLE.xz",
                "AbyssalReefLE.xz",
                "IceandChromeLE.xz",
        ]
        for map_file in maps:
            with lzma.open(
                    f"MapAnalyzer/pickle_gameinfo/{map_file}", "rb"
            ) as f:
                raw_game_data, raw_game_info, raw_observation = pickle.load(f)

            bot = import_bot_instance(
                    raw_game_data, raw_game_info, raw_observation
            )
            map_data = MapData(bot=bot)

            for region in map_data.regions.values():
                assert isinstance(
                        map_data.where(region.center), Region
                ), f"<Map : {map_file}, Region : {region}, where :  {map_data.where(region.center)} point : {region.center}>"
            for choke in map_data.map_chokes:
                assert isinstance(
                        map_data.where(choke.center), (Region, Polygon, ChokeArea)
                ), f"<Map : {map_file}, Choke : {choke}, where :  {map_data.where(choke.center)} point : {choke.center}>"
            for mdramp in map_data.map_ramps:
                assert isinstance(
                        map_data.where(mdramp.center), (Region, Polygon, MDRamp)
                ), f"<Map : {map_file}, MDRamp : {mdramp}, where :  {map_data.where(mdramp.center)} point : {mdramp.center}>"
