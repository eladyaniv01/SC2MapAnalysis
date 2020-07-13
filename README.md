# SC2MapAnalysis

Early Stage development,

**you will need to have 64 bit python installed** 


to get an idea of what the api can do,  check out "run.py" 



it is meant to be a tool(extension) for [BurnySc2](https://github.com/BurnySc2/python-sc2/)

Thanks A lot to [DrInfy](https://github.com/DrInfy) for solving one of the biggest challenges,  finding rare choke points,
check out his sc2 python framework, [Sharpy](https://github.com/DrInfy/sharpy-sc2) for rapid bot development,   
check out [sc2pathlib](https://github.com/DrInfy/sc2-pathlib)  a high performant rust module with python interface for pathfinding 



Example:
```python
import pickle
import lzma
from MapData import MapData
from utils import import_bot_instance


#if its from BurnySc2 it is compressed
# https://github.com/BurnySc2/python-sc2/tree/develop/test/pickle_data

with lzma.open(YOUR_FILE_PATH, "rb") as f:
    raw_game_data, raw_game_info, raw_observation = pickle.load(f)

# mocking a bot object to initalize the map,  this is for when you want to do this while not in a game,  
# if you want to use it in a game just pass in the bot object like shown below 

bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)


# And then you can instantiate a MapData Object like so
map_data = MapData(bot)


# plot the entire labeled map
map_data.plot_map()

# red dots or X are vision blockers,
# ramps are marked with white dots 
# ramp top center is marked with '^'
# gas geysers are yellow spades 
# ramps are marked with R<region_label>
# height span is with respect to :   light = high , dark = low
# choke area's are marked with green heart suites
```
<img src="https://user-images.githubusercontent.com/40754127/87227966-db552800-c3a6-11ea-93d6-7d252becbda2.png" width="90%"></img> 
```python
# isolate a region,  plot it
>>>map_data.regions[8].plot()
```
<img src="https://user-images.githubusercontent.com/40754127/86950267-a0f64b80-c158-11ea-968c-773483fd3a7a.png" width="90%"></img> 

```python
# you can also inspect the perimeter
>>>map_data.regions[8].plot_perimeter()

```
<img src="https://user-images.githubusercontent.com/40754127/86950274-a2277880-c158-11ea-9f07-fdeec300abae.png" width="90%"></img> 

```python
#query a point with respect to region
>>>p = (130,100)
>>>map_data.in_region(p)
Region 8
```

