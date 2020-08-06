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
    if 'goldenwall' in mf.lower():
        map_file = mf
        break

with lzma.open(map_file, "rb") as f:
    raw_game_data, raw_game_info, raw_observation = pickle.load(f)

bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
map_data = MapData(bot, loglevel="DEBUG")

start = (110, 95)
goal = (110, 40)
grid = map_data.get_pyastar_grid()
# grid = map_data.add_influence((170, 140), r=20, arr=grid, weight=np.inf)
# resource_blockers = [Point2(m.position) for m in map_data.mineral_fields if "rich" in m.name.lower()]
# for pos in resource_blockers:
# radius = 1
# map_data.log(pos)
# grid = map_data.add_influence(p=pos, r=radius, arr=grid, weight=np.inf)
path = map_data.pathfind(start=start, goal=goal, grid=grid)

map_data.plot_influenced_path(start=start, goal=goal, weight_array=grid)
map_data.show()
# map_data.plot_map()
# map_data.show()
# map_data.log(map_data.resource_blockers)
assert (path is None), f"{path}"

#
# # map_data.plot_map()
# base = map_data.bot.townhalls[0]
# reg_start = map_data.where(base.position_tuple)
# reg_end = map_data.where(map_data.bot.enemy_start_locations[0].position)
# start = reg_start.center
# goal = reg_end.center
# pts = []
# r = 10
# for i in range(50):
#     pts.append(get_random_point(-500, -250, -500, -250))
#
# arr = map_data.get_pyastar_grid()
# for p in pts:
#     arr = map_data.add_influence(p, r, arr)
# path = map_data.pathfind(start, goal, grid=arr)
# # assert (path is not None), f"path = {path}"
# map_data.plot_influenced_path(start=start, goal=goal, weight_array=arr)
# map_data.show()
# map_data.plot_influenced_path(start=start, goal=goal, weight_array=map_data.get_pyastar_grid())
# map_data.show()
# start = (110, 95)
# goal = (110, 40)
# map_data.plot_influenced_path(start=start, goal=goal, weight_array=map_data.get_pyastar_grid())
# path = map_data.pathfind(start, goal, map_data.get_pyastar_grid())
# map_data.logger.info(path)
# map_data.show()
