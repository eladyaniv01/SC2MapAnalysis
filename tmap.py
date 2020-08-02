import lzma
import os
import pickle
import random
from typing import List

from MapAnalyzer.constructs import ChokeArea, MDRamp, VisionBlockerArea
from MapAnalyzer.MapData import MapData
from MapAnalyzer.Polygon import Polygon
from MapAnalyzer.Region import Region
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
map_data = MapData(bot)

for i, choke in enumerate(map_data.map_chokes):
    print(choke.center == (65, 146))
    print(choke.center)
    assert isinstance(
            map_data.where(choke.center), (Region, Polygon, ChokeArea, MDRamp, VisionBlockerArea)
    ), map_data.logger.error(f"<Map : {map_data}, Choke : {choke},"
                             f" where :  {map_data.where(choke.center)} point : {choke.center}>")
