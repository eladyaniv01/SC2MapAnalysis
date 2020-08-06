# SC2MapAnalysis 

Builds:
-------

* [master](https://github.com/eladyaniv01/SC2MapAnalysis/tree/master) 

* ![build](https://github.com/eladyaniv01/SC2MapAnalysis/workflows/Build/badge.svg?branch=master) ![](https://img.shields.io/github/package-json/v/eladyaniv01/SC2MapAnalysis?style=plastic)

* <details><summary>Latest Changes</summary>
<p>


moved plot functions to outside Debugger class
reordered the mess in map_data init,  moved set pathlib to Pather
moved `get_sets_with_mutual_elements` to utils
reordered mapdata code
no breaking changes, everything is backwards compatible

Testing both installations (setup.py and requirements.txt)
fix circular import bug on utils


* fixes, test pass locally
Debugger: now inspects stack and will not save on tests
debugger will no longer circular call map_data for plotting
MapData: resource_blockers are now calculated with original coords
removed usage of neighbores ,  instead  adding influence with radius
Pather:
radius for resource blockers is now 2, this passes all tests
Tests:
every tests  will now use the MapAnalyzer.util functions when it can
removed redundant test_map_data from TestSanity,  and put it in its right place,  test_mapdata
</p>
</details>

A standalone plugin for python SC2 api 

Early Stage development,

- [Getting Started](#getting-started)
- [Pathfinding](#Pathfinding)
- [How to plug it on your bot](#How-to-plug-it-on-your-bot)

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

`pip install .`

or if you want to contribute, or run tests locally 

`pip install -e .[dev]`

or just with 

`pip install -r requirements.txt`

to get an idea of what the api can do,  check out "run.py" and "dummybot.py"  both should run to verify the installation and demosntrate some of the capabilites  

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

`def pathfind(self, start: Tuple[int, int], goal: Tuple[int, int], grid: Optional[ndarray] = None,allow_diagonal=False, sensitivity: int = 1) -> ndarray:`

* `start`: start coordinates
* `goal`: goal coordinates
* `grid`: the weighted array to path through
* `allow_diagonal`: diagonal moves -> if set to True will perforce slightly worst
* `sensitivity`: default is 1,  what gaps between points is desired (in many use cases you will want to get every nth point of the path because its pointless to recompute every single point unless extensive micro is called for)

* An example you can try out yourself to get a feel for it:
```python
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
    if 'reef' in mf.lower():
        map_file = mf
        break


with lzma.open(map_file, "rb") as f:
    raw_game_data, raw_game_info, raw_observation = pickle.load(f)

bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
map_data = MapData(bot)

# get corner regions centers for start / end points
base = map_data.bot.townhalls[0]
reg_start = map_data.where(base.position_tuple)
reg_end = map_data.where(map_data.bot.enemy_start_locations[0].position)
p0 = reg_start.center
p1 = reg_end.center
for idx in range(8):
    """generate random points for added influence / cost """
    pts = []
    if idx > 0:
        NUM_POINTS = idx * 10
    else:
        NUM_POINTS = 35

    # generating random points for added influence
    for i in range(NUM_POINTS):
        pts.append(get_random_point(50, 130, 25, 175))

    """Requesting a grid and adding influence / cost"""
    # getting the base grid for pathing
    arr = map_data.get_pyastar_grid()
    r = 7 + idx
    # note that we use the default weight of 100,  we could pass custom weights for each point though
    for p in pts:
        arr = map_data.add_influence(p, r, arr, weight=-100)

    """Plot path on weighted grid"""
    map_data.plot_influenced_path(start=p0, goal=p1, weight_array=arr, name=f"Added {NUM_POINTS} of influence",
                                  save=True, plot=False)

```
Results from 8 runs On AbysalReefLE:
--------------------
![MA_INF_Added 10 of influence](https://user-images.githubusercontent.com/40754127/89323316-299bd500-d68e-11ea-8f98-24e7d9e78e1e.png)
![MA_INF_Added 20 of influence](https://user-images.githubusercontent.com/40754127/89323320-299bd500-d68e-11ea-8b89-d59d1387adca.png)
![MA_INF_Added 30 of influence](https://user-images.githubusercontent.com/40754127/89323322-2a346b80-d68e-11ea-8de6-996565e40c6b.png)
![MA_INF_Added 35 of influence](https://user-images.githubusercontent.com/40754127/89323304-24d72100-d68e-11ea-9ffc-8e835ea8c505.png)
![MA_INF_Added 40 of influence](https://user-images.githubusercontent.com/40754127/89323308-26a0e480-d68e-11ea-9e8f-e93e7edb21b3.png)
![MA_INF_Added 50 of influence](https://user-images.githubusercontent.com/40754127/89323311-27d21180-d68e-11ea-97c4-99d6acd3cfa3.png)
![MA_INF_Added 60 of influence](https://user-images.githubusercontent.com/40754127/89323312-286aa800-d68e-11ea-854b-cfbb7beb261a.png)
![MA_INF_Added 70 of influence](https://user-images.githubusercontent.com/40754127/89323315-29033e80-d68e-11ea-97cb-17957ee9675c.png)

# How to plug it on your bot
* The example below will get your main base, and enemy main base locations and plot the path between with no influence
* MapData objects should be called `on_start` and is required only the bot object
* it is recommended to set it to `None` on init(because its before `on_start`), and then set it on_start as shown below
    
```python


from typing import List

import sc2
from sc2.player import Bot, Computer
from sc2.position import Point3

from MapAnalyzer import MapData, Point2

GREEN = Point3((0, 255, 0))
RED = Point3((255, 0, 0))
BLUE = Point3((0, 0, 255))
BLACK = Point3((0, 0, 0))


class MATester(sc2.BotAI):

    def __init__(self):
        super().__init__()
        self.map_data = None
        self.logger = None

    async def on_start(self):
        self.map_data = MapData(self)
        self.logger = self.map_data.logger

    async def on_step(self, iteration: int):

        base = self.townhalls[0]
        reg_start = self.map_data.where(base.position_tuple)
        # self.logger.info(regstart)
        reg_end = self.map_data.where(self.enemy_start_locations[0].position)
        # self.logger.info(regend)
        p0 = reg_start.center
        p1 = reg_end.center
        path = self.map_data.pathfind(start=p0, goal=p1)
        self.client.debug_text_world(
                "\n".join([f"start {p0}", ]), Point2(p0), color=RED, size=30,
        )
        self.client.debug_text_world(
                "\n".join([f"end {p1}", ]), Point2(p1), color=RED, size=30,
        )
        self._draw_point_list(path, text='*')

    def _draw_point_list(self, point_list: List = None, color=None, text=None, box_r=None) -> bool:
        if not color:
            color = GREEN
        for p in point_list:
            p = Point2(p)
            h = self.get_terrain_z_height(p)
            pos = Point3((p.x, p.y, h))
            if box_r:
                p0 = Point3((pos.x - box_r, pos.y - box_r, pos.z + box_r)) + Point2((0.5, 0.5))
                p1 = Point3((pos.x + box_r, pos.y + box_r, pos.z - box_r)) + Point2((0.5, 0.5))
                self.client.debug_box_out(p0, p1, color=color)
            if text:
                self.client.debug_text_world(
                        "\n".join([f"{text}", ]), pos, color=color, size=30,
                )


def main():
    map = "AutomatonLE"
    sc2.run_game(
            sc2.maps.get(map),
            [Bot(sc2.Race.Terran, MATester()), Computer(sc2.Race.Zerg, sc2.Difficulty.VeryEasy)],
            realtime=False
    )

if __name__ == "__main__":
    main()

```
