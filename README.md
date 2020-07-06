# SC2MapAnalysis

Early Stage Draft, 
to get an idea of what the api can do,  check out "run.py" 
it is meant to be a tool(extension) for https://github.com/BurnySc2/python-sc2/


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
```
<img src="https://user-images.githubusercontent.com/40754127/86649725-af265980-bfea-11ea-86ea-aa95a3afe0a3.png" width="90%"></img> 
```python
# isolate a region,  plot it's polygon
map_data.regions[9].polygon.plot()
```
<img src="https://user-images.githubusercontent.com/40754127/86603172-5768fd80-bfac-11ea-9104-21426531208e.png" width="90%"></img> 

```python
# you can also inspect the perimeter
map_data.regions[9].plot_perimeter()

```
<img src="https://user-images.githubusercontent.com/40754127/86603164-5637d080-bfac-11ea-94f5-9ab72cf59bcb.png" width="90%"></img> 
