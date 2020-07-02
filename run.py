import pickle, lzma
from MapData import MapData
from sc2.game_info import GameInfo

if __name__ == "__main__":
    # with open("pickle_gameinfo/placement_gridPillarsofGoldLE", "rb") as f:
    #     #     placement_arr = pickle.load(f)
    #     # with open("pickle_gameinfo/pathing_gridPillarsofGoldLE", "rb") as f:
    #     #     path_arr = pickle.load(f)
    #     # with open("pickle_gameinfo/terrain_heightPillarsofGoldLE", "rb") as f:
    #     #     terrain_height = pickle.load(f)
    with lzma.open("pickle_gameinfo/AbyssalReefLE.xz", "rb") as f:
        raw_game_data, raw_game_info, raw_observation = pickle.load(f)

    game_info = GameInfo(raw_game_info.game_info)
    map_name = "PillarsofGoldLE"
    map_data = MapData(map_name, game_info)
    map_data.plot_regions_by_label()
    for label, region in map_data.regions.items():
        region.plot_perimeter()