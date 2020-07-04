from sc2.game_data import GameData
from sc2.game_info import GameInfo
from sc2.game_state import GameState
from sc2.player import BotAI


def import_bot_instance(raw_game_data, raw_game_info, raw_observation):
    bot = BotAI()
    game_data = GameData(raw_game_data.data)
    game_info = GameInfo(raw_game_info.game_info)
    game_state = GameState(raw_observation)
    # noinspection PyProtectedMember
    bot._initialize_variables()
    # noinspection PyProtectedMember
    bot._prepare_start(client=None, player_id=1, game_info=game_info, game_data=game_data)
    # noinspection PyProtectedMember
    bot._prepare_first_step()
    # noinspection PyProtectedMember
    bot._prepare_step(state=game_state, proto_game_info=raw_game_info)
    # noinspection PyProtectedMember
    bot._find_expansion_locations()
    return bot