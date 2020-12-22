import lzma
import os
import pickle
import numpy as np
from skimage import draw as skdraw

from typing import List, Optional, TYPE_CHECKING, Union

from s2clientprotocol.sc2api_pb2 import Response, ResponseObservation
from sc2.bot_ai import BotAI
from sc2.game_data import GameData
from sc2.game_info import GameInfo, Ramp
from sc2.game_state import GameState
from sc2.position import Point2

from MapAnalyzer.constructs import MDRamp, VisionBlockerArea
from .cext import CMapChoke
from .settings import ROOT_DIR

if TYPE_CHECKING:
    from MapAnalyzer.MapData import MapData

# following https://github.com/BurnySc2/python-sc2/blob/ffb9bd43dcbeb923d848558945a8c59c9662f435/sc2/game_info.py#L246
# to fix burnysc2 ramp objects by removing destructables
def fix_map_ramps(bot: BotAI):
    pathing_grid = bot.game_info.pathing_grid.data_numpy.T
    for dest in bot.destructables:
        ri, ci = skdraw.disk(center=dest.position, radius=dest.radius, shape=pathing_grid.shape)
        pathing_grid[ri, ci] = 1

    pathing = np.ndenumerate(pathing_grid.T)

    def equal_height_around(tile):
        sliced = bot.game_info.terrain_height.data_numpy[tile[1] - 1: tile[1] + 2, tile[0] - 1: tile[0] + 2]
        return len(np.unique(sliced)) == 1

    map_area = bot.game_info.playable_area
    points = [
        Point2((a, b))
        for (b, a), value in pathing
        if value == 1
           and map_area.x <= a < map_area.x + map_area.width
           and map_area.y <= b < map_area.y + map_area.height
           and bot.game_info.placement_grid[(a, b)] == 0
    ]
    ramp_points = [point for point in points if not equal_height_around(point)]
    vision_blockers = set(point for point in points if equal_height_around(point))
    ramps = [Ramp(group, bot.game_info) for group in bot.game_info._find_groups(ramp_points)]
    return ramps, vision_blockers


def get_sets_with_mutual_elements(list_mdchokes: List[CMapChoke],
                                  area: Optional[Union[MDRamp, VisionBlockerArea]] = None,
                                  base_choke: CMapChoke = None) -> List[List]:
    li = []
    if area:
        s1 = area.points
    else:
        s1 = base_choke.pixels
    for c in list_mdchokes:
        s2 = c.pixels
        s3 = s1 ^ s2
        if len(s3) <= 0.95*(len(s1) + len(s2)):
            li.append(c.id)
    return li


def mock_map_data(map_file: str) -> "MapData":
    from MapAnalyzer.MapData import MapData
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
    folder = ROOT_DIR
    subfolder = "pickle_gameinfo"
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
