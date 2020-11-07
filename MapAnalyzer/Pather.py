from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import pyastar.astar_wrapper as pyastar
from loguru import logger
from numpy import ndarray
from sc2.ids.unit_typeid import UnitTypeId as UnitID
from sc2.position import Point2
from skimage import draw as skdraw

from MapAnalyzer.constants import GEYSER_RADIUS_FACTOR, NONPATHABLE_RADIUS_FACTOR, RESOURCE_BLOCKER_RADIUS_FACTOR
from MapAnalyzer.exceptions import OutOfBoundsException, PatherNoPointsException
from MapAnalyzer.Region import Region
from .sc2pathlibp import Sc2Map

if TYPE_CHECKING:
    from MapAnalyzer.MapData import MapData


class MapAnalyzerPather:
    """"""

    def __init__(self, map_data: "MapData") -> None:
        self.map_data = map_data
        self.pyastar = pyastar
        self.pathlib_map = None
        self._set_pathlib_map()
        if self.pathlib_map:
            # noinspection PyProtectedMember
            self._climber_grid = np.array(self.pathlib_map._map.reaper_pathing).astype(np.float32)
        else:
            logger.error('Could not set Pathlib Map')
        nonpathable_indices = np.where(self.map_data.bot.game_info.pathing_grid.data_numpy == 0)
        self.nonpathable_indices_stacked = np.column_stack(
                (nonpathable_indices[1], nonpathable_indices[0])
        )
        self.connectivity_graph = None  # set later by MapData

    def set_connectivity_graph(self):
        connectivity_graph = {}
        for region in self.map_data.regions.values():
            if connectivity_graph.get(region) is None:
                connectivity_graph[region] = []
            for connected_region in region.connected_regions:
                if connected_region not in connectivity_graph.get(region):
                    connectivity_graph[region].append(connected_region)
        self.connectivity_graph = connectivity_graph

    def find_all_paths(self, start: Region, goal: Region, path: Optional[List[Region]] = None) -> List[List[Region]]:
        if path is None:
            path = []
        graph = self.connectivity_graph
        path = path + [start]
        if start == goal:
            return [path]
        if start not in graph:
            return []
        paths = []
        for node in graph[start]:
            if node not in path:
                newpaths = self.find_all_paths(node, goal, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths

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

    def _add_non_pathables_ground(self, grid: ndarray, include_destructables: bool = True) -> ndarray:
        nonpathables = self.map_data.bot.structures.not_flying
        nonpathables.extend(self.map_data.bot.enemy_structures.not_flying)
        nonpathables.extend(self.map_data.mineral_fields)
        nonpathables.extend(self.map_data.normal_geysers)
        nonpathables = nonpathables.exclude_type(UnitID.SUPPLYDEPOTLOWERED)
        for obj in nonpathables:
            radius = NONPATHABLE_RADIUS_FACTOR
            if 'geyser' in obj.name.lower():
                radius = NONPATHABLE_RADIUS_FACTOR * GEYSER_RADIUS_FACTOR
            grid = self.add_cost(position=obj.position.rounded, radius=radius * obj.radius, arr=grid, weight=np.inf)
        for pos in self.map_data.resource_blockers:
            radius = RESOURCE_BLOCKER_RADIUS_FACTOR
            grid = self.add_cost(position=pos.rounded, radius=radius, arr=grid, weight=np.inf)
        if include_destructables:
            destructables_filtered = [d for d in self.map_data.bot.destructables if "plates" not in d.name.lower()]
            for rock in destructables_filtered:
                if "plates" not in rock.name.lower():
                    self.add_cost(position=rock.position.rounded, radius=1 * rock.radius, arr=grid, weight=np.inf)
        return grid

    def find_lowest_cost_points(self, from_pos: Point2, radius: int, grid: np.ndarray) -> List[Point2]:
        ri, ci = skdraw.disk(center=(int(from_pos[0]), int(from_pos[1])), radius=radius, shape=grid.shape)
        if len(ri) == 0 or len(ci) == 0:
            # this happens when the center point is near map edge, and the radius added goes beyond the edge
            logger.debug(OutOfBoundsException(from_pos))
            # self.map_data.logger.trace()
            return None
        points = self.map_data.indices_to_points((ci, ri))
        arr = self.map_data.points_to_numpy_array(points)
        # Transpose must be done here on the newly generated array,
        # since the original grid can use this function many times per frame,
        # and we dont want to transpose it more than once
        arr = np.where(arr.T == 1, grid, np.inf)
        lowest_points = self.map_data.indices_to_points(np.where(arr == np.min(arr)))
        return list(map(Point2, lowest_points))

    def get_base_pathing_grid(self) -> ndarray:

        grid = np.fmax(self.map_data.path_arr, self.map_data.placement_arr).T

        #  steps  - convert list of coords to np array ,  then do grid[[*converted.T]] = val
        if len(self.map_data.bot.game_info.vision_blockers) > 0:
            vbs = np.array(list(self.map_data.bot.game_info.vision_blockers))
            # faster way to do :
            # for point in self.map_data.bot.game_info.vision_blockers:
            #         #     grid[point] = 1

            # some maps dont have vbs
            grid[tuple(vbs.T)] = 1  # <-

        return grid

    def get_climber_grid(self, default_weight: int = 1, include_destructables: bool = True) -> ndarray:
        """Grid for units like reaper / colossus """
        grid = self._climber_grid.copy()
        grid = np.where(grid != 0, default_weight, np.inf).astype(np.float32)
        grid = self._add_non_pathables_ground(grid=grid, include_destructables=include_destructables)
        return grid

    def get_clean_air_grid(self, default_weight: int = 1) -> ndarray:
        clean_air_grid = np.ones(shape=self.map_data.path_arr.shape).astype(np.float32).T
        if default_weight == 1:
            return clean_air_grid.copy()
        else:
            return np.where(clean_air_grid == 1, default_weight, np.inf).astype(np.float32)

    def get_air_vs_ground_grid(self, default_weight: int) -> ndarray:
        grid = np.fmax(self.map_data.path_arr, self.map_data.placement_arr).T
        air_vs_ground_grid = np.where(grid == 0, 1, default_weight).astype(np.float32)
        return air_vs_ground_grid

    def get_pyastar_grid(self, default_weight: int = 1, include_destructables: bool = True) -> ndarray:
        grid = self.map_data.pather.get_base_pathing_grid().copy()
        grid = np.where(grid != 0, default_weight, np.inf).astype(np.float32)
        grid = self._add_non_pathables_ground(grid=grid, include_destructables=include_destructables)
        return grid

    def pathfind(self, start: Tuple[int, int], goal: Tuple[int, int], grid: Optional[ndarray] = None,
                 allow_diagonal: bool = False, sensitivity: int = 1) -> ndarray:
        if start is not None and goal is not None:
            start = int(start[0]), int(start[1])
            goal = int(goal[0]), int(goal[1])
        else:
            logger.warning(PatherNoPointsException(start=start, goal=goal))
            return None
        if grid is None:
            logger.warning("Using the default pyastar grid as no grid was provided.")
            grid = self.get_pyastar_grid()

        path = self.pyastar.astar_path(grid, start=start, goal=goal, allow_diagonal=allow_diagonal)
        if path is not None:
            path = list(map(Point2, path))[::sensitivity]
            """
            Edge case
            EverDreamLE,  (81, 29) is considered in map bounds,  but it is not.
            """
            # `if point` is checking with burnysc2 that the point is in map bounds
            if 'everdream' in self.map_data.map_name.lower():
                legal_path = [point for point in path if point and point.x != 81 and point.y != 29]
            else:  # normal case
                legal_path = [point for point in path if point]

            legal_path.pop(0)
            return legal_path
        else:
            logger.debug(f"No Path found s{start}, g{goal}")
            return None

    @staticmethod
    def add_cost(position: Tuple[int, int], radius: int, arr: ndarray, weight: int = 100,
                 safe: bool = True, initial_default_weights: int = 0) -> ndarray:

        ri, ci = skdraw.disk(center=(int(position[0]), int(position[1])), radius=radius, shape=arr.shape)
        if len(ri) == 0 or len(ci) == 0:
            if safe:
                # this happens when the center point is near map edge, and the radius added goes beyond the edge
                logger.debug(OutOfBoundsException(position))
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
        if initial_default_weights > 0:
            arr[ri, ci] = np.where(arr[ri, ci] == 1, initial_default_weights, arr[ri, ci])

        arr[ri, ci] += weight
        if np.any(arr < 1) and safe:
            logger.warning(
                    "You are attempting to set weights that are below 1. falling back to the minimum (1)")
            arr = np.where(arr < 1, 1, arr)
        return arr
