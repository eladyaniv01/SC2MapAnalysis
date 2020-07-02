import pickle
from MapData import MapData


if __name__ == "__main__":
    with open("pickle_gameinfo/placement_gridPillarsofGoldLE", "rb") as f:
        placement_arr = pickle.load(f)
    with open("pickle_gameinfo/pathing_gridPillarsofGoldLE", "rb") as f:
        path_arr = pickle.load(f)
    with open("pickle_gameinfo/terrain_heightPillarsofGoldLE", "rb") as f:
        terrain_height = pickle.load(f)
    map_name = "PillarsofGoldLE"
    map_data = MapData(map_name, placement_arr, path_arr, terrain_height)
    map_data.plot_regions_by_label()
    for label, region in map_data.regions.items():
        region.plot_perimeter()