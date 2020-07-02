# SC2MapAnalysis

Early Stage Draft, 
to get an idea of what the api can do,  check out "run.py" 
it is meant to be a tool(extension) for https://github.com/BurnySc2/python-sc2/

import GameInfo directly from the Api, 

Example:
```python
from sc2.game_info import GameInfo
import lzma, pickle
#if its from BurnySc2 it is compressed
# https://github.com/BurnySc2/python-sc2/tree/develop/test/pickle_data

with lzma.open(YOUR_FILE_PATH, "rb") as f:
    raw_game_data, raw_game_info, raw_observation = pickle.load(f)
    
game_info = GameInfo(raw_game_info.game_info)
# And then you can instantiate a MapData Object like so
map_name = "PillarsofGoldLE"
map_data = MapData(map_name, game_info)

# plot the entire labeled map
map_data.plot_regions_by_label()
```
<img src="https://user-images.githubusercontent.com/40754127/86403746-f6dd7600-bcb6-11ea-942d-52110ec285f2.png" width="90%"></img> 
```python
# plot each region in a closeup showing its relative placement on the map and perimeter
for label, region in map_data.regions.items():
    region.plot_perimeter()

# or, just plot one
map_data.regions[4].plot_perimeter()

```
<img src="https://user-images.githubusercontent.com/40754127/86403753-f93fd000-bcb6-11ea-9d2c-c929c1a8591b.png" width="90%"></img> 
