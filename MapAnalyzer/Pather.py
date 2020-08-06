from typing import Optional, Tuple

import numpy as np
import pyastar.astar_wrapper as pyastar
from numpy import ndarray
from sc2.position import Point2
from skimage import draw as skdraw

from MapAnalyzer.exceptions import OutOfBoundsException
from .sc2pathlibp import Sc2Map


class MapAnalyzerPather:
    """"""

    def __init__(self, map_data):
        self.map_data = map_data
        self.pyastar = pyastar
        self.pathlib_map = None
        self._set_pathlib_map()
        nonpathable_indices = np.where(self.map_data.bot.game_info.pathing_grid.data_numpy == 0)
        self.nonpathable_indices_stacked = np.column_stack(
                (nonpathable_indices[1], nonpathable_indices[0])
        )

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

    def get_base_pathing_grid(self) -> ndarray:
        return np.fmax(self.map_data.path_arr, self.map_data.placement_arr).T

    def get_pyastar_grid(self, default_weight: int = 1, include_destructables: bool = True,
                         air_pathing: bool = False) -> ndarray:

        if air_pathing:
            return np.ones(shape=self.map_data.path_arr.shape)

        grid = self.map_data.pather.get_base_pathing_grid().copy()
        grid = np.where(grid != 0, default_weight, np.inf).astype(np.float32)
        nonpathables = self.map_data.bot.structures
        nonpathables.extend(self.map_data.bot.enemy_structures)
        nonpathables.extend(self.map_data.mineral_fields)
        for obj in nonpathables:
            radius = 0.8
            grid = self.add_influence(p=obj.position, r=radius * obj.radius, arr=grid, weight=np.inf)
        resource_blockers = self.map_data.resource_blockers
        for pos in resource_blockers:
            radius = 0.5
            # self.map_data.log(pos)
            grid = self.add_influence(p=pos, r=radius, arr=grid, weight=np.inf)
        if include_destructables:
            destructables_filtered = [d for d in self.map_data.bot.destructables if "plates" not in d.name.lower()]
            for rock in destructables_filtered:
                if "plates" not in rock.name.lower():
                    self.add_influence(p=rock.position, r=0.8 * rock.radius, arr=grid, weight=np.inf)
        return grid

    def pathfind(self, start: Tuple[int, int], goal: Tuple[int, int], grid: Optional[ndarray] = None,
                 allow_diagonal: bool = False, sensitivity: int = 1) -> ndarray:
        start = int(start[0]), int(start[1])
        goal = int(goal[0]), int(goal[1])
        if grid is None:
            grid = self.get_pyastar_grid()

        path = self.pyastar.astar_path(grid, start=start, goal=goal, allow_diagonal=allow_diagonal)
        if path is not None:
            return list(map(Point2, path))[::sensitivity]
        else:
            self.map_data.logger.debug(f"No Path found s{start}, g{goal}")
            return None

    def add_influence(self, p: Tuple[int, int], r: int, arr: ndarray, weight: int = 100, safe: bool = True) -> ndarray:
        ri, ci = skdraw.disk(center=(int(p[0]), int(p[1])), radius=r, shape=arr.shape)
        if len(ri) == 0 or len(ci) == 0:
            # this happens when the center point is near map edge, and the radius added goes beyond the edge
            self.map_data.logger.debug(OutOfBoundsException(p))
            return arr

        def in_bounds_ci(x):
            width = arr.shape[0] - 1
            if 0 < x < width:
                return x
            return 0

        def in_bounds_ri(y):
            height = arr.shape[1] - 1
            if 0 < y < height:
                return y
            return 0

        ci_vec = np.vectorize(in_bounds_ci)
        ri_vec = np.vectorize(in_bounds_ri)
        ci = ci_vec(ci)
        ri = ri_vec(ri)
        arr[ri, ci] += weight
        if np.any(arr < 1) and safe:
            self.map_data.logger.warning(
                    "You are attempting to set weights that are below 1. falling back to the minimum (1)")
            arr = np.where(arr < 1, 1, arr)
        return arr
