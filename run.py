import lzma
import pickle

from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import import_bot_instance

if __name__ == "__main__":
    map_file = "GoldenWallLE.xz"
    map_file = "DeathAuraLE.xz"
    with lzma.open(f"MapAnalyzer/pickle_gameinfo/{map_file}", "rb") as f:

        raw_game_data, raw_game_info, raw_observation = pickle.load(f)

    bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
    map_data = MapData(bot=bot)
    map_data.plot_map()
    # for label, region in map_data.regions.items():
    #     region.plot_perimeter()
    #     region.polygon.plot()
    #     region.plot()
