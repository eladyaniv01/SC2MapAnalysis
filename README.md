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

* `p`: center point (for example p could be an enemy units position)
* `r`: radius (for example  r ->  attack range)
* `weight`: how much cost to be added 

**the optimal cost will be 1**,  

**and the worst cost would be np.inf( for non pathable cells)**

so you should keep that in mind if you want to create a complex influence map with different weights

* An example you can try out yourself to get a feel for it:
```python
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

with lzma.open(map_files[0], "rb") as f:
    raw_game_data, raw_game_info, raw_observation = pickle.load(f)

bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
map_data = MapData(bot)

# get corner regions centers for start / end points
reg1 = map_data.regions[1]
reg7 = map_data.regions[7]
p0 = reg1.center
p1 = reg7.center

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

    r = 7 + idx  # radius is 10 for all points to make things simple
    plt.title(f"with {NUM_POINTS}  added points of influence with radius {r} and 100 default weight")
    # note that we use the default weight of 100,  we could pass custom weights for each point though
    for p in pts:
        arr = map_data.add_influence(p, r, arr)
        # plt.text(p[0], p[1], "*")  # transpose the points to fit the lower origin in our plot

    path = map_data.pathfind(p0, p1, grid=arr)

    print(f"p0 = {p0}  p1 = {p1}")
    # transpose the points to fit the lower origin in our plot
    p0_ = p0[1], p0[0]
    p1_ = p1[1], p1[0]
    arr = np.where(arr < np.inf, arr, 0)  # this is just a conversion to plot nicely

    # in some cases the path is impossible unless we lower the weights
    if path is not None:
        print("Found")
        org = "lower"
        plt.title(f"with {NUM_POINTS}  added points of influence with radius {r} and 100 default weight")
        x, y = zip(*path)
        plt.scatter(x, y)
    else:
        print("Not Found")
        org = "lower"
        plt.title(f"**No path found** pts: {NUM_POINTS}  radius: {r} , weight:  100 default")
        x, y = zip(*[p0, p1])
        plt.scatter(x, y)
    plt.text(p0_[0], p0_[1], f"Start {p0}")
    plt.text(p1_[0], p1_[1], f"End {p1}")
    plt.imshow(map_data.path_arr.T, alpha=0.8, origin=org, cmap='summer')
    plt.imshow(map_data.terrain_height.T, alpha=0.8, origin=org, cmap='Blues')
    plt.imshow(arr, origin=org, alpha=0.3, cmap='YlOrRd')
    plt.grid(False)
    plt.savefig(f"{idx}.png")
    plt.close()

```
Results from 5 runs:
--------------------
<img src="https://user-images.githubusercontent.com/40754127/89064773-488b2600-d373-11ea-83ef-c1ca81b4a45f.png"/>
<img src="https://user-images.githubusercontent.com/40754127/89064776-4923bc80-d373-11ea-9dc3-cefde61cc8aa.png"/>
<img src="https://user-images.githubusercontent.com/40754127/89064778-49bc5300-d373-11ea-9ffb-7a55144b2b0b.png"/>
<img src="https://user-images.githubusercontent.com/40754127/89064768-4628cc00-d373-11ea-8928-2090ed5b9c5f.png"/>
<img src="https://user-images.githubusercontent.com/40754127/89064772-47f28f80-d373-11ea-85cb-aaed6057e014.png"/>
