import lzma
import os
import pickle
import random
from typing import List

from sc2.position import Point2

from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import import_bot_instance


def get_random_point(minx, maxx, miny, maxy):
    return (random.randint(minx, maxx), random.randint(miny, maxy))


def _get_random_influence(n, r):
    pts = []
    for i in range(n):
        pts.append(
                (Point2(get_random_point(50, 130, 25, 175)), r))
    return pts
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
map_data = MapData(bot, loglevel="DEBUG")
logger = map_data.logger
base = map_data.bot.townhalls[0]
reg_start = map_data.where(base.position_tuple)
reg_end = map_data.where(map_data.bot.enemy_start_locations[0].position)
p0 = Point2(reg_start.center)
p1 = Point2(reg_end.center)
influence_grid = map_data.get_pyastar_grid()
ramps = reg_end.region_ramps
# logger.error(ramps)
if len(ramps) > 1:
    if map_data.distance(ramps[0].top_center, reg_end.center) < map_data.distance(ramps[1].top_center,
                                                                                  reg_end.center):
        ramp = ramps[0]
    else:
        ramp = ramps[1]
else:
    ramp = ramps[0]

# influence_points = [(ramp.top_center, 2), (Point2((66, 66)), 18)]

influence_points = _get_random_influence(25, 5)
# for tup in influence_points:
#     p = tup[0]
#     r = tup[1]
#     map_data.add_influence(p, r=r, arr=influence_grid)
map_data.plot_influenced_path(start=p0, goal=p1, weight_array=influence_grid)
map_data.show()
# map_data.plot_map()
# map_data.show()
# get corner regions centers for start / end points
# base = map_data.bot.townhalls[0]
# reg_start = map_data.where(base.position_tuple)
# reg_end = map_data.where(map_data.bot.enemy_start_locations[0].position)
# p0 = reg_start.center
# p1 = reg_end.center
# for idx in range(8):
#     """generate random points for added influence / cost """
#     pts = []
#     if idx > 0:
#         NUM_POINTS = idx * 10
#     else:
#         NUM_POINTS = 1
# 
#     # generating random points for added influence
#     for i in range(NUM_POINTS):
#         pts.append(get_random_point(50, 130, 25, 175))
# 
#     """Requesting a grid and adding influence / cost"""
#     # getting the base grid for pathing
#     if NUM_POINTS / 10 % 2 == 0:
#         # arr = map_data.get_air_vs_ground_grid()
#         arr = map_data.get_clean_air_grid()
#         grid_name = "AvG_Grid"
#     else:
#         arr = map_data.get_pyastar_grid(air_pathing=False)
#         grid_name = "NormalGrid"
#     r = 7 + idx
#     # note that we use the default weight of 100,  we could pass custom weights for each point though
#     for p in pts:
#         arr = map_data.add_influence(p, r, arr)
# 
#     """Plot path on weighted grid"""
#     map_data.plot_influenced_path(start=p0, goal=p1, weight_array=arr,
#                                   name=f"{grid_name}{NUM_POINTS} Points of influence")
#     map_data.show()
#     # map_data.close()
