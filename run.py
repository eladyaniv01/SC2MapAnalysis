import pickle
import lzma
from MapData import MapData
from utils import import_bot_instance

if __name__ == "__main__":
    with lzma.open("pickle_gameinfo/AbyssalReefLE.xz", "rb") as f:
        raw_game_data, raw_game_info, raw_observation = pickle.load(f)

    bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
    map_data = MapData(bot=bot)
    map_data.plot_map()
    for label, region in map_data.regions.items():
        if label == 3:
            region.plot_perimeter()
