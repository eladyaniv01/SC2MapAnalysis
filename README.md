# SC2MapAnalysis 

Builds:
-------

* [master](https://github.com/eladyaniv01/SC2MapAnalysis/tree/master)  ![build](https://github.com/eladyaniv01/SC2MapAnalysis/workflows/build/badge.svg?branch=master)

A standalone plugin for python SC2 api 

Early Stage development,

- [Getting Started](#getting-started)
- [Pathfinding](#Pathfinding)


Why Do we need this ? 
=====================

This module is inspired by plays like this one [TY map positioning](https://www.youtube.com/watch?v=NUQsAWIBTSk&start=458)
(notice how the army splits into groups, covering different areas,  tanks are tucked in corners, and so on) 

Hopefully with the interface provided here, you will be able to build plays like that one!

it is meant to be a tool(extension) for [BurnySc2](https://github.com/BurnySc2/python-sc2/)

Thanks A lot to [DrInfy](https://github.com/DrInfy) for solving one of the biggest challenges,  finding rare choke points.

check out his work 

* [Sharpy](https://github.com/DrInfy/sharpy-sc2) for rapid bot development.

* [sc2pathlib](https://github.com/DrInfy/sc2-pathlib)  a high performance rust module with python interface for pathfinding 




Example:
```python
import pickle
import lzma
from MapData import MapData
from utils import import_bot_instance


#if its from BurnySc2 it is compressed
# https://github.com/BurnySc2/python-sc2/tree/develop/test/pickle_data
YOUR_FILE_PATH = 'some_directory/map_file'
with lzma.open(YOUR_FILE_PATH, "rb") as f:
    raw_game_data, raw_game_info, raw_observation = pickle.load(f)

# mocking a bot object to initalize the map,  this is for when you want to do this while not in a game,  
# if you want to use it in a game just pass in the bot object like shown below 

bot = import_bot_instance(raw_import_bot_instancegame_data, raw_game_info, raw_observation)


# And then you can instantiate a MapData Object like so
map_data = MapData(bot)


# plot the entire labeled map
map_data.plot_map()

# red dots or X are vision blockers,
# ramps are marked with white dots 
# ramp top center is marked with '^'
# gas geysers are yellow spades 
# MDRampss are marked with R<region_label>
# height span is with respect to :   light = high , dark = low
# ChokeArea is marked with green heart suites
# Corners are marked with a red 'V' 
```
<img src="https://user-images.githubusercontent.com/40754127/88463402-3fa1dc80-cebb-11ea-9da9-f80a219f1083.png"/>


- access a Region like so(region_label is of type int):

    **`region = map_data.regions[region_label]`**

- get a region by querying a point ( for example the position of the enemy ) 

    if the point is not inside a region, will return None
    
    **`region = map_data.in_region_p(point)`**

- get an area by querying a point ( for example the position of the enemy ) 

    will always return Area
    
    **`region = map_data.where(point)`**

- get all constructs by querying a point ( for example the position of the enemy ) 

    will a list of area's the point is in ( for example a MDRampArea and a Region could have mutual points )
    
    **`region = map_data.where_all(point)`**

- other handy objects available through our interface

    **`region.region_chokes`**

    **`region.region_ramps`**

    **`region.region_vision_blockers`**

    **`region.bases`**

    **`region.corners`**
    
- util methods 

    will return the closest point out of a list/ set of points , towards another point
    useful for calculating which corner you would want to put static defense on,  or siege 
    
    **`MapData.closest_towards_point(self, points: List[Point2], target: Point2) -> Point2`** 

# Getting Started

**you will need to have 64 bit python installed** 

create a virtual environment,  and clone the repo into it

`python install.py`

or if you want to contribute, or run tests locally 

`python install_dev.py`

to get an idea of what the api can do,  check out "run.py" 

Tested Maps ( [AiArena](https://ai-arena.net/) and [SC2ai](https://sc2ai.net/) ladder map pool) :
```
['AbyssalReefLE.xz',
 'AutomatonLE.xz',
 'DeathAuraLE.xz',
 'EphemeronLE.xz',
 'EternalEmpireLE.xz',
 'EverDreamLE.xz',
 'GoldenWallLE.xz',
 'IceandChromeLE.xz',
 'NightshadeLE.xz',
 'PillarsofGoldLE.xz',
 'SimulacrumLE.xz',
 'SubmarineLE.xz',
 'Triton.xz',
 'WorldofSleepersLE.xz',
 'ZenLE.xz']
```

# Pathfinding
====================
getting the basic pathing grid :

 `map_data.get_pyastar_grid()`

Adding influence :
------------------
`def add_influence(p: Tuple[int, int], r: int, arr: ndarray, weight: int = 100) -> ndarray:`

Usage:

`map_data.add_influence(p, r, arr, weight)`

here p is the center point,  r is a radius (for example p could be units position, and r - its attack range)
weight is the cost to be added to the cell, 
the optimal cost will be 1,  and the worst cost would be np.inf( for non pathable cells)
so you should keep that in mind if you want to create a complex influence map with different weights

* An example you can try out yourself to get a feel for it:
```python
import lzma
import os
import pickle
import random
from typing import List

fname = "AbyssalReefLE"


from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import import_bot_instance

def get_random_point(minr, maxr):
    return (random.randint(minr, maxr), random.randint(minr, maxr))
    
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

fname = "AbyssalReefLE"
map_files = get_map_file_list()
map_files = get_map_file_list()

with lzma.open(map_files[0], "rb") as f:
    raw_game_data, raw_game_info, raw_observation = pickle.load(f)

bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
map_data = MapData(bot)

reg1 = map_data.regions[1]
reg7 = map_data.regions[7]
p0 = reg1.center
p1 = reg7.center
pts = []
r = 10
for i in range(50):
    pts.append(get_random_point(-20, 220))

arr = map_data.get_pyastar_grid()

for p in pts:
    arr = map_data.add_influence(p, r, arr)

import matplotlib.pyplot as plt

path = map_data.pathfind(p0, p1, grid=arr)
print(f"p0 = {p0}  p1 = {p1}")
plt.text(p0[1], p0[0], f"Start {p0}")
plt.text(p1[1], p1[0], f"End {p1}")
x, y = zip(*path)
plt.imshow(map_data.path_arr.T, alpha=0.8, origin='lower', cmap='summer')
plt.imshow(map_data.terrain_height.T, alpha=0.8, origin='lower', cmap='Blues')

arr = np.where(arr < np.inf, arr, 0) # this is just a for plotting
plt.imshow(arr, origin="lower", alpha=0.3, cmap='YlOrRd')
plt.scatter(x, y)
plt.grid(False)
plt.show()
```
Results from 5 runs:
--------------------
<img src="https://user-images.githubusercontent.com/40754127/89039068-2204c500-d34a-11ea-9597-0245cdccfc06.png"/>
<img src="https://user-images.githubusercontent.com/40754127/89039072-2335f200-d34a-11ea-868a-0d524bf193f3.png"/>
<img src="https://user-images.githubusercontent.com/40754127/89039076-23ce8880-d34a-11ea-9f4d-826dfb403435.png"/>
<img src="https://user-images.githubusercontent.com/40754127/89039079-25984c00-d34a-11ea-9750-99360cb4cb52.png"/>
<img src="https://user-images.githubusercontent.com/40754127/89039084-2630e280-d34a-11ea-8d63-51106c082b02.png"/>
