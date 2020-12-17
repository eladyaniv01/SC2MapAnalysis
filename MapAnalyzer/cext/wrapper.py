import numpy as np
import mapanalyzerext as ext
from typing import Optional, Tuple, Union, List
from sc2.position import Point2


def astar_path(
        weights: np.ndarray,
        start: Tuple[int, int],
        goal: Tuple[int, int]) -> Union[np.ndarray, None]:
    # For the heuristic to be valid, each move must have a positive cost.
    if weights.min(axis=None) <= 0:
        raise ValueError("Minimum cost to move must be above 0, but got %f" % (
            weights.min(axis=None)))
    # Ensure start is within bounds.
    if (start[0] < 0 or start[0] >= weights.shape[0] or
            start[1] < 0 or start[1] >= weights.shape[1]):
        raise ValueError(f"Start of {start} lies outside grid.")
    # Ensure goal is within bounds.
    if (goal[0] < 0 or goal[0] >= weights.shape[0] or
            goal[1] < 0 or goal[1] >= weights.shape[1]):
        raise ValueError(f"Goal of {goal} lies outside grid.")

    height, width = weights.shape
    start_idx = np.ravel_multi_index(start, (height, width))
    goal_idx = np.ravel_multi_index(goal, (height, width))
    path = ext.astar(
        weights.flatten(), height, width, start_idx, goal_idx
    )
    return path


class CMapInfo:
    climber_grid: np.ndarray
    overlord_spots: Optional[List[Point2]]

    def __init__(self, walkable_grid: np.ndarray, height_map: np.ndarray):
        self.climber_grid, overlord_data = self._get_map_data(walkable_grid, height_map)
        self.overlord_spots = list(map(Point2, overlord_data))

    @staticmethod
    def _get_map_data(walkable_grid: np.ndarray, height_map: np.ndarray):
        height, width = walkable_grid.shape
        return ext.get_map_data(walkable_grid.flatten(), height_map.flatten(), height, width)

