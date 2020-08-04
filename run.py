import lzma
import os
import pickle
import random
from typing import List

from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import import_bot_instance


def get_random_point(minx, maxx, miny, maxy):
    return (random.randint(minx, maxx), random.randint(miny, maxy))


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


map_files = get_map_file_list()
for mf in map_files:
    if 'reef' in mf.lower():
        map_file = mf
        break

# noinspection PyUnboundLocalVariable
with lzma.open(map_file, "rb") as f:
    raw_game_data, raw_game_info, raw_observation = pickle.load(f)

bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
map_data = MapData(bot)

# get corner regions centers for start / end points
base = map_data.bot.townhalls[0]
reg_start = map_data.where(base.position_tuple)
reg_end = map_data.where(map_data.bot.enemy_start_locations[0].position)
p0 = reg_start.center
p1 = reg_end.center
for idx in range(8):
    """generate random points for added influence / cost """
    pts = []
    if idx > 0:
        NUM_POINTS = idx * 10
    else:
        NUM_POINTS = 35

    # generating random points for added influence
    for i in range(NUM_POINTS):
        pts.append(get_random_point(50, 130, 25, 175))

    """Requesting a grid and adding influence / cost"""
    # getting the base grid for pathing
    arr = map_data.get_pyastar_grid()
    r = 7 + idx
    # note that we use the default weight of 100,  we could pass custom weights for each point though
    for p in pts:
        arr = map_data.add_influence(p, r, arr, weight=-100)

    """Plot path on weighted grid"""
    map_data.plot_influenced_path(start=p0, goal=p1, weight_array=arr, name=f"Added {NUM_POINTS} of influence",
                                  save=True, plot=False)
