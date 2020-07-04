# SC2MapAnalysis

Early Stage Draft, 
to get an idea of what the api can do,  check out "run.py" 
it is meant to be a tool(extension) for https://github.com/BurnySc2/python-sc2/

import GameInfo directly from the Api, 

Example:
```python
import pickle
import lzma
from MapData import MapData
from sc2.game_data import GameData
from sc2.game_info import GameInfo
from sc2.game_state import GameState
from sc2.player import BotAI

#if its from BurnySc2 it is compressed
# https://github.com/BurnySc2/python-sc2/tree/develop/test/pickle_data

with lzma.open(YOUR_FILE_PATH, "rb") as f:
    raw_game_data, raw_game_info, raw_observation = pickle.load(f)


bot = BotAI()
game_data = GameData(raw_game_data.data)
game_info = GameInfo(raw_game_info.game_info)
game_state = GameState(raw_observation)
# noinspection PyProtectedMember
bot._initialize_variables()
# noinspection PyProtectedMember
bot._prepare_start(client=None, player_id=1, game_info=game_info, game_data=game_data)
# noinspection PyProtectedMember
bot._prepare_step(state=game_state, proto_game_info=raw_game_info)
# noinspection PyProtectedMember
bot._find_expansion_locations()
game_info = GameInfo(raw_game_info.game_info)
map_name = game_info.map_name



# And then you can instantiate a MapData Object like so
map_data = MapData(
    map_name=map_name,
    game_info=game_info,
    base_locations=bot.expansion_locations_list
)


# plot the entire labeled map
map_data.plot_regions_by_label()
```
<img src="https://user-images.githubusercontent.com/40754127/86516033-2068df80-be26-11ea-94d7-5c0be1b497a6.png" width="90%"></img> 
```python
# plot each region in a closeup showing its relative placement on the map and perimeter
for label, region in map_data.regions.items():
    region.plot_perimeter()

# or, just plot one
map_data.regions[4].plot_perimeter()

```
<img src="https://user-images.githubusercontent.com/40754127/86403753-f93fd000-bcb6-11ea-9d2c-c929c1a8591b.png" width="90%"></img> 
