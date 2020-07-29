# f = "EverDreamLE"
import os
from typing import List

f = "GoldenWallLE"
# f = "EphemeronLE"
f = "AbyssalReefLE"
import lzma
import pickle

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
for file in map_files:
    with lzma.open(file, "rb") as f:
        raw_game_data, raw_game_info, raw_observation = pickle.load(f)

    bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
    map_data = MapData(bot)
    map_data.save_plot()
    break

# pystar fast with influence
import pyastar
import matplotlib.pyplot as plt
import random
from skimage import draw

path_grid = m_d.bot.game_info.pathing_grid
placement_grid = m_d.bot.game_info.placement_grid


def get_random_point(minr, maxr):
    return (random.randint(minr, maxr), random.randint(minr, maxr))


def add_influence(p, r, arr):
    radius = r
    ri, ci = draw.circle(p[0], p[1], radius=radius, shape=arr.shape)
    arr[ci, ri] = r

    return arr


plt.figure(figsize=(20, 20))

# pts = [(90,100) , (110,40)]
pts = []
for i in range(20):
    pts.append(get_random_point(25, 170))

arr = m_d.path_arr.copy()
r = 9
for p in pts:
    arr = add_influence(p, r, arr)

# ro, co = draw.circle(100, 100, radius=outer_radius, shape=arr.shape)
# arr[ro, co] = 2


_data = np.zeros((m_d.path_arr.shape[1], m_d.path_arr.shape[0]))
_data = np.fmax(m_d.path_arr, m_d.placement_arr).T
_data = np.where(_data != 0, 1, np.inf).astype(np.float32)
xi, yi = np.where(arr > 0)
_data[yi, xi] = arr[xi, yi]
print(f"from {p0} to {p1}")
path = np.flip(pyastar.astar_path(_data, p0, p1, allow_diagonal=False))
plt.text(p0[0], p0[1], f"Start {p0}")
plt.text(p1[0], p1[1], f"End {p1}")
x, y = zip(*path)
plt.imshow(m_d.path_arr, alpha=0.3, origin='lower')
plt.imshow(arr, origin="lower", alpha=0.3)
plt.scatter(y, x)
plt.grid(False)
plt.show()
