# SC2MapAnalysis 

### Important - Ground pathing is broken on Map `DeathAuraLE` at the moment 

* ![build](https://github.com/eladyaniv01/SC2MapAnalysis/workflows/Build/badge.svg?branch=master) 
 [master](https://github.com/eladyaniv01/SC2MapAnalysis/tree/master) 

* ![](https://img.shields.io/github/package-json/v/eladyaniv01/SC2MapAnalysis?color=blue&logo=EladYaniv01&style=plastic) [Changelog](https://github.com/eladyaniv01/SC2MapAnalysis/blob/master/CHANGELOG.md)  

* ![](https://img.shields.io/badge/Documentation-latest-green?style=plastic&logo=appveyor)
   [Documentation](https://eladyaniv01.github.io/SC2MapAnalysis/)
   
Summary
-------
A standalone plugin for python SC2 api 


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


More Examples reside in the [Documentation](https://eladyaniv01.github.io/SC2MapAnalysis/)

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




