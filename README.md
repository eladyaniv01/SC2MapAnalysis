# SC2MapAnalysis ![](https://github.com/eladyaniv01/SC2MapAnalysis/workflows/.github/workflows/python-app.yml/badge.svg)
A standalone plugin for python SC2 api 

Early Stage development,

- [Getting Started](#getting-started)


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
<img src="https://user-images.githubusercontent.com/40754127/87425708-cbc42200-c5e6-11ea-928f-213375371da1.png"/>


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

create a virtual enviroment,  and clone the repo into it

`pip install .`

or if you dont want to install it as a package, run

`pip install -r requirements.txt`

or if you want to contribute, or run tests locally 

`pip install -e .[dev]`

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
