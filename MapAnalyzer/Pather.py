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
from .cext import astar_path

if TYPE_CHECKING:
    from MapAnalyzer.MapData import MapData


class MapAnalyzerPather:
    """"""

    def __init__(self, map_data: "MapData") -> None:
        self.map_data = map_data
        self.pyastar = pyastar

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

    def _add_non_pathables_ground(self, grid: ndarray, include_destructables: bool = True) -> ndarray:
        nonpathables = self.map_data.bot.structures.not_flying
        nonpathables.extend(self.map_data.bot.enemy_structures.not_flying)
        nonpathables.extend(self.map_data.mineral_fields)
        nonpathables.extend(self.map_data.normal_geysers)
        nonpathables = nonpathables.exclude_type(UnitID.SUPPLYDEPOTLOWERED)
        for obj in nonpathables:
            radius = NONPATHABLE_RADIUS_FACTOR
            if 'geyser' in obj.name.lower():
                radius = GEYSER_RADIUS_FACTOR
            grid = self.add_cost(position=obj.position.rounded, radius=radius * obj.radius, arr=grid, weight=np.inf, safe=False)
        for pos in self.map_data.resource_blockers:
            radius = RESOURCE_BLOCKER_RADIUS_FACTOR
            grid = self.add_cost(position=pos.rounded, radius=radius, arr=grid, weight=np.inf, safe=False)
        if include_destructables:
            destructables_filtered = [d for d in self.map_data.bot.destructables if "plates" not in d.name.lower()]
            for rock in destructables_filtered:
                if "plates" not in rock.name.lower():
                    self.add_cost(position=rock.position.rounded, radius=1 * rock.radius, arr=grid, weight=np.inf, safe=False)
        return grid

    def find_lowest_cost_points(self, from_pos: Point2, radius: float, grid: np.ndarray) -> List[Point2]:
        # Add 0.01 to radius to find a closed disk
        ri, ci = skdraw.disk(center=(from_pos[0], from_pos[1]), radius=radius + 0.01, shape=grid.shape)
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

    def get_climber_grid(self, default_weight: float = 1, include_destructables: bool = True) -> ndarray:
        """Grid for units like reaper / colossus """
        grid = self.get_base_pathing_grid()
        grid = np.where(grid != 0, default_weight, np.inf).astype(np.float32)
        grid = np.where(self.map_data.c_ext_map.climber_grid != 0, default_weight, grid).astype(np.float32)
        grid = self._add_non_pathables_ground(grid=grid, include_destructables=include_destructables)

        return grid

    def get_clean_air_grid(self, default_weight: float = 1) -> ndarray:
        clean_air_grid = np.ones(shape=self.map_data.path_arr.shape).astype(np.float32).T
        if default_weight == 1:
            return clean_air_grid.copy()
        else:
            return np.where(clean_air_grid == 1, default_weight, np.inf).astype(np.float32)

    def get_air_vs_ground_grid(self, default_weight: float) -> ndarray:
        grid = np.fmax(self.map_data.path_arr, self.map_data.placement_arr).T
        air_vs_ground_grid = np.where(grid == 0, 1, default_weight).astype(np.float32)
        return air_vs_ground_grid

    def get_pyastar_grid(self, default_weight: float = 1, include_destructables: bool = True) -> ndarray:
        grid = self.get_base_pathing_grid()
        grid = np.where(grid != 0, default_weight, np.inf).astype(np.float32)
        grid = self._add_non_pathables_ground(grid=grid, include_destructables=include_destructables)
        return grid

    def pathfind(self, start: Tuple[float, float], goal: Tuple[float, float], grid: Optional[ndarray] = None,
                 allow_diagonal: bool = False, sensitivity: int = 1) -> ndarray:
        if start is not None and goal is not None:
            start = int(round(start[0])), int(round(start[1]))
            goal = int(round(goal[0])), int(round(goal[1]))
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

    def pathfind_c(self, start: Tuple[float, float], goal: Tuple[float, float], grid: Optional[ndarray] = None,
                   smoothing: bool = False,
                   sensitivity: int = 1) -> ndarray:
        if start is not None and goal is not None:
            start = int(round(start[0])), int(round(start[1]))
            goal = int(round(goal[0])), int(round(goal[1]))
        else:
            logger.warning(PatherNoPointsException(start=start, goal=goal))
            return None
        if grid is None:
            logger.warning("Using the default pyastar grid as no grid was provided.")
            grid = self.get_pyastar_grid()

        path = astar_path(grid, start, goal, smoothing)

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
    def add_cost(position: Tuple[float, float], radius: float, arr=ndarray, weight: float = 100,
                 safe: bool = True, initial_default_weights: float = 0) -> ndarray:
        # Add 0.01 to change from open to closed disk
        ri, ci = skdraw.disk(center=position, radius=radius + 0.01, shape=arr.shape)

        if initial_default_weights > 0:
            arr[ri, ci] = np.where(arr[ri, ci] == 1, initial_default_weights, arr[ri, ci])

        arr[ri, ci] += weight
        if safe and np.any(arr < 1):
            logger.warning(
                    "You are attempting to set weights that are below 1. falling back to the minimum (1)")
            arr = np.where(arr < 1, 1, arr)

        return arr
