import lzma
import os
import pickle
import random
from typing import List

from sc2.position import Point2
from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import import_bot_instance

import matplotlib.pyplot as plt

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
    if 'subm' in mf.lower():
        # if 1==1:
        #     mf = random.choice(map_files)
        # if 'abys' in mf.lower():
        with lzma.open(mf, "rb") as f:
            raw_game_data, raw_game_info, raw_observation = pickle.load(f)
        bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
        map_data = MapData(bot, loglevel="DEBUG")
        base = map_data.bot.townhalls[0]
        reg_start = map_data.where_all(base.position_tuple)[0]
        reg_end = map_data.where_all(map_data.bot.enemy_start_locations[0].position)[0]
        p0 = Point2(reg_start.center)
        p1 = Point2(reg_end.center)
        influence_grid = map_data.get_air_vs_ground_grid(default_weight=50)
        # influence_grid = map_data.get_pyastar_grid()
        cost_point = (50, 130)
        influence_grid = map_data.add_cost(position=cost_point, radius=7, grid=influence_grid)
        safe_points = map_data.find_lowest_cost_points(from_pos=cost_point, radius=14, grid=influence_grid)

        # logger.info(safe_points)

        x, y = zip(*safe_points)
        plt.scatter(x, y, s=1)
        map_data.plot_influenced_path(start=p0, goal=p1, weight_array=influence_grid, allow_diagonal=False)
        # map_data.save(filename=f"{mf}")
        # plt.close()
        map_data.show()
        # break
