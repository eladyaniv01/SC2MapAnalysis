import lzma
import pickle

from MapAnalyzer import ChokeArea, MDRamp, Polygon, Region
from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import import_bot_instance

# for merging pr from forks,  git push <pr-repo.git> <your-local-branch-name>:<pr-branch-name>

if __name__ == "__main__":  # pragma: no cover
    maps = [
            # "GoldenWallLE.xz",
            # "DeathAuraLE.xz",
            # "SubmarineLE.xz",
            "AbyssalReefLE.xz",
            # "IceandChromeLE.xz",
    ]
    for map_file in maps:
        with lzma.open(f"MapAnalyzer/pickle_gameinfo/{map_file}", "rb") as f:
            raw_game_data, raw_game_info, raw_observation = pickle.load(f)

        bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
        map_data = MapData(bot=bot)

        for region in map_data.regions.values():
            print(region.corners)
            # print(f"{map_file} <Region>   {map_data.where_all(region.center)}")
            assert isinstance(
                    map_data.where(region.center), Region
            ), f"<Map : {map_file}, Region : {region}, where :  {map_data.where(region.center)} point : {region.center}>"
        for choke in map_data.map_chokes:
            # print(f"{map_file} <Choke>   {map_data.where_all(choke.center)}")
            assert isinstance(
                    map_data.where(choke.center), (Region, Polygon, ChokeArea)
            ), f"<Map : {map_file}, Choke : {choke}, where :  {map_data.where(choke.center)} point : {choke.center}>"
        for mdramp in map_data.map_ramps:
            # print(f"{map_file} <MDRamp>   {map_data.where_all(mdramp.center)}")
            assert isinstance(
                    map_data.where(mdramp.center), (Region, Polygon, MDRamp)
            ), f"<Map : {map_file}, MDRamp : {mdramp}, where :  {map_data.where(mdramp.center)} point : {mdramp.center}>"
        map_data.plot_map()
        # map_data.save_plot()
