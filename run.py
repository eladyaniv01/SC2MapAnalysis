import lzma
import os
import pickle
import random
from typing import List

import matplotlib.pyplot as plt
import numpy as np

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
    if 'Abyssal' in mf:
        map_file = mf
        break

with lzma.open(map_file, "rb") as f:
    raw_game_data, raw_game_info, raw_observation = pickle.load(f)

bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
map_data = MapData(bot)

# get corner regions centers for start / end points
reg1 = map_data.regions[1]
reg7 = map_data.regions[7]
p1 = reg1.center[0] + 0.5, reg1.center[1]
p0 = reg7.center
doh = map_data.where_all(reg7.center)
for idx in range(5):
    pts = []
    if idx > 0:
        NUM_POINTS = idx * 10
    else:
        NUM_POINTS = 10

    # generating random points for added influence
    for i in range(NUM_POINTS):
        pts.append(get_random_point(50, 130, 25, 175))

    # getting the base grid for pathing
    arr = map_data.get_pyastar_grid()

    r = 7 + idx

    # note that we use the default weight of 100,  we could pass custom weights for each point though
    for p in pts:
        arr = map_data.add_influence(p, r, arr)
    # plt.text(p[0], p[1], "*")  # transpose the points to fit the lower origin in our plot

    path = np.flip(np.flipud(map_data.pathfind(p0, p1,
                                               grid=arr,
                                               sensitivity=5)))  # flipping the path here to align with plot, dont do this for your bot

    print(f"p0 = {p0}  p1 = {p1}")
    # transpose the points to fit the lower origin in our plot
    p0_ = p0[1], p0[0]
    p1_ = p1[1], p1[0]
    # arr = np.where(arr < np.inf, arr, 0)  # this is just a conversion to plot nicely

    # in some cases the path is impossible unless we lower the weights
    if path is not None:
        map_data.logger.info("Found")
        org = "lower"
        plt.title(
            f"{map_data.map_name} with {NUM_POINTS}  added points of influence with radius {r} and 100 default weight")
        x, y = zip(*path)
        plt.scatter(x, y, s=1)
    else:
        map_data.logger.info("Not Found")
        org = "lower"
        plt.title(f"**No path found** pts: {NUM_POINTS}  radius: {r} , weight:  100 default")
        x, y = zip(*[p0, p1])
        plt.scatter(x, y)
    plt.text(p0_[0], p0_[1], f"Start {p0_}")
    plt.text(p1_[0], p1_[1], f"End {p1_}")
    plt.imshow(map_data.path_arr.T, alpha=0.8, origin=org, cmap='summer')
    plt.imshow(map_data.terrain_height.T, alpha=0.8, origin=org, cmap='Blues')
    plt.imshow(arr, origin=org, alpha=0.3, cmap='YlOrRd')
    plt.grid(False)
    plt.savefig(f"{idx}.png")
    plt.close()
