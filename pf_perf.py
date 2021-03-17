import lzma
import os
import pickle
import random
from typing import List
from platform import python_version
import time
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
map_file = ""
for mf in map_files:
    if 'goldenwall' in mf.lower():
        map_file = mf
        break

with lzma.open(map_file, "rb") as f:
    raw_game_data, raw_game_info, raw_observation = pickle.load(f)

bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
map_data = MapData(bot, loglevel="DEBUG")

base = map_data.bot.townhalls[0]
reg_start = map_data.where(base.position_tuple)
reg_end = map_data.where(map_data.bot.enemy_start_locations[0].position)
p0 = reg_start.center
p1 = reg_end.center
pts = []
r = 10
for i in range(50):
    pts.append(get_random_point(0, 200, 0, 200))

arr = map_data.get_pyastar_grid(100)
for p in pts:
    arr = map_data.add_cost(p, r, arr)

start = time.perf_counter()
path2 = map_data.pathfind(p0, p1, grid=arr)
ext_time = time.perf_counter() - start
print("extension astar time: {}".format(ext_time))

start = time.perf_counter()
nydus_path = map_data.pathfind_with_nyduses(p0, p1, grid=arr)
nydus_time = time.perf_counter() - start
print("nydus astar time: {}".format(nydus_time))
print("compare to without nydus: {}".format(nydus_time / ext_time))

map_data.plot_influenced_path(start=p0, goal=p1, weight_array=arr)
map_data.plot_influenced_path_nydus(start=p0, goal=p1, weight_array=arr)
