import lzma
import pickle

from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import import_bot_instance

if __name__ == "__main__":
    map_file = "GoldenWallLE.xz"
    map_file = "DeathAuraLE.xz"
    map_file = "SubmarineLE.xz"
    map_file = "AbyssalReefLE.xz"
    with lzma.open(f"MapAnalyzer/pickle_gameinfo/{map_file}", "rb") as f:

        raw_game_data, raw_game_info, raw_observation = pickle.load(f)

    bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
    map_data = MapData(bot=bot)

    for region in map_data.regions.values():
        print(region)
        print(region.polygon.center)
        print(map_data.in_region(region.polygon.center))
        assert (region == map_data.in_region(region.center)), \
            f"{region.center}  has not been found inside the Region {region}"

    map_data.plot_map()
    map_data.save_plot()
