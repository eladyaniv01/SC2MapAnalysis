import pickle
import lzma
from MapData import MapData
from sc2.game_data import GameData
from sc2.game_info import GameInfo
from sc2.game_state import GameState
from sc2.player import BotAI

if __name__ == "__main__":
    with lzma.open("pickle_data/PillarsofGoldLE.xz", "rb") as f:
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
    map_data = MapData(
        map_name=map_name,
        game_info=game_info,
        base_locations=bot.expansion_locations_list
    )
    map_data.plot_regions_by_label()
    for label, region in map_data.regions.items():
        region.plot_perimeter()
