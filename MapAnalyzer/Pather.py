from functools import lru_cache

import numpy as np
import pyastar
from mapanalyzer import Sc2Map
from numpy import ndarray


class MapAnalyzerPather:
    """"""

    def __init__(self, map_data):
        self.map_data = map_data
        self.pyastar = pyastar
        self.pathlib_map = None
        self._set_pathlib_map()

    def _set_pathlib_map(self) -> None:
        """
        Will initialize the sc2pathlib `SC2Map` object for future use
        """
        self.pathlib_map = Sc2Map(
                self.map_data.path_arr,
                self.map_data.placement_arr,
                self.map_data.terrain_height,
                self.map_data.bot.game_info.playable_area,
        )

    @lru_cache()
    def get_base_pathing_grid(self) -> ndarray:
        return np.fmax(self.map_data.path_arr, self.map_data.placement_arr).T
