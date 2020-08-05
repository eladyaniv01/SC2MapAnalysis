import lzma
import os
import pickle
from typing import List

from s2clientprotocol.sc2api_pb2 import Response, ResponseObservation
from sc2.bot_ai import BotAI
from sc2.game_data import GameData
from sc2.game_info import GameInfo
from sc2.game_state import GameState

from MapAnalyzer.MapData import MapData


def mock_map_data(map_file: str) -> MapData:
    print(map_file)
    with lzma.open(f"{map_file}", "rb") as f:
        raw_game_data, raw_game_info, raw_observation = pickle.load(f)

    bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
    return MapData(bot=bot)


def import_bot_instance(
        raw_game_data: Response,
        raw_game_info: Response,
        raw_observation: ResponseObservation,
) -> BotAI:
    """
    import_bot_instance DocString
    """
    bot = BotAI()
    game_data = GameData(raw_game_data.data)
    game_info = GameInfo(raw_game_info.game_info)
    game_state = GameState(raw_observation)
    # noinspection PyProtectedMember
    bot._initialize_variables()
    # noinspection PyProtectedMember
    bot._prepare_start(
            client=None, player_id=1, game_info=game_info, game_data=game_data
    )
    # noinspection PyProtectedMember
    bot._prepare_first_step()
    # noinspection PyProtectedMember
    bot._prepare_step(state=game_state, proto_game_info=raw_game_info)
    # noinspection PyProtectedMember
    bot._find_expansion_locations()
    return bot


def get_map_files_folder() -> str:
    folder = os.path.abspath(".")
    if 'MapAnalyzer' in folder:
        subfolder = "pickle_gameinfo"
    else:
        subfolder = "MapAnalyzer"
        subfolder2 = "pickle_gameinfo"
        subfolder = os.path.join(subfolder, subfolder2)

    return os.path.join(folder, subfolder)


def get_map_file_list() -> List[str]:
    """
    easy way to produce less than all maps,  for example if we want to test utils, we only need one MapData object
    """
    map_files_folder = get_map_files_folder()
    map_files = os.listdir(map_files_folder)
    li = []
    for map_file in map_files:
        li.append(os.path.join(map_files_folder, map_file))
    return li
