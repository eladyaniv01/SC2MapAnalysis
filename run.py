import lzma
import pickle

from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import import_bot_instance

if __name__ == "__main__":
    maps = ["GoldenWallLE.xz",
            "DeathAuraLE.xz",
            "SubmarineLE.xz",
            "AbyssalReefLE.xz",
            "IceandChromeLE.xz"]
    for map_file in maps:
        with lzma.open(f"MapAnalyzer/pickle_gameinfo/{map_file}", "rb") as f:
            raw_game_data, raw_game_info, raw_observation = pickle.load(f)

        bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
        map_data = MapData(bot=bot)

        for region in map_data.regions.values():
            print(
                f"<{map_data.bot.game_info.map_name}>: region center found in {region}: {region == map_data.in_region(region.center)}")

            # assert (region == map_data.in_region(region.center)), \
            #     f"<{map_data.bot.game_info.map_name}>: {region.center}  has not been found inside the Region {region}\n points {region.polygon.points}\n  the region we got is {map_data.in_region(region.center)}"

        # map_data.plot_map()
        # map_data.save_plot()
