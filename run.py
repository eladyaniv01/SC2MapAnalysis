import os
import lzma
import pickle
import random
from typing import List
fname = "AbyssalReefLE"


from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import import_bot_instance


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

with lzma.open(map_files[0], "rb") as f:
    raw_game_data, raw_game_info, raw_observation = pickle.load(f)

bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
map_data = MapData(bot)
map_data.save_plot()


reg1 = map_data.regions[1]
reg7 = map_data.regions[7]
p0 = reg1.center
p1 = reg7.center


def get_random_point(minr, maxr):
    return (random.randint(minr, maxr), random.randint(minr, maxr))


# pts = [(90,100) , (110,40)]
pts = []
r = 10
for i in range(50):
    pts.append(get_random_point(-20, 220))

arr = map_data.get_pyastar_grid()

for p in pts:
    arr = map_data.add_influence(p, r, arr)

# ro, co = draw.circle(100, 100, radius=outer_radius, shape=arr.shape)
# arr[ro, co] = 2
import matplotlib.pyplot as plt

path = map_data.pathfind(p0, p1, grid=arr)
plt.text(p0[1], p0[0], f"Start {p0}")
plt.text(p1[1], p1[0], f"End {p1}")
x, y = zip(*path)
plt.imshow(map_data.path_arr.T, alpha=0.8, origin='lower', cmap='summer')
plt.imshow(map_data.terrain_height.T, alpha=0.8, origin='lower', cmap='Blues')
# this is just a conversion to plot nicely
import numpy as np

arr = np.where(arr < np.inf, arr, 0)
plt.imshow(arr, origin="lower", alpha=0.3, cmap='YlOrRd')
plt.scatter(x, y)
plt.grid(False)
plt.show()
