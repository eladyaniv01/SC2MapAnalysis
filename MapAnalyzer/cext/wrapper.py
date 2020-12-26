import numpy as np
import mapanalyzerext as ext
from typing import Optional, Tuple, Union, List, Set
from sc2.position import Point2, Rect


class CMapChoke:
    """
    CMapChoke holds the choke data coming from c extension
    main_line pair of floats representing the middle points of the sides of the choke
    lines all the lines from side to side
    side1 points on side1
    side2 points on side2
    pixels all the points inside the choke area, should include the sides and the points inside
    min_length minimum distance between the sides of the choke
    id an integer to represent the choke
    """
    main_line: Tuple[Tuple[float, float], Tuple[float, float]]
    lines: List[Tuple[Tuple[int, int], Tuple[int, int]]]
    side1: List[Tuple[int, int]]
    side2: List[Tuple[int, int]]
    pixels: Set[Tuple[int, int]]
    min_length: float
    id: int

    def __init__(self, choke_id, main_line, lines, side1, side2, pixels, min_length):
        self.id = choke_id
        self.main_line = main_line
        self.lines = lines
        self.side1 = side1
        self.side2 = side2
        self.pixels = set(pixels)
        self.min_length = min_length

    def __repr__(self) -> str:
        return f"[{self.id}]CMapChoke; {len(self.pixels)}"


def astar_path(
        weights: np.ndarray,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        smoothing: bool) -> Union[np.ndarray, None]:
    # For the heuristic to be valid, each move must have a positive cost.
    # Demand costs above 1 so floating point inaccuracies aren't a problem
    # when comparing costs
    if weights.min(axis=None) < 1:
        raise ValueError("Minimum cost to move must be above or equal to 1, but got %f" % (
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
        weights.flatten(), height, width, start_idx, goal_idx, smoothing
    )
    return path


class CMapInfo:
    climber_grid: np.ndarray
    overlord_spots: Optional[List[Point2]]
    chokes: List[CMapChoke]

    def __init__(self, walkable_grid: np.ndarray, height_map: np.ndarray, playable_area: Rect):
        """
        walkable_grid and height_map are matrices of type uint8
        """

        # grids are transposed and the c extension atm calls the y axis the x axis and vice versa
        # so switch the playable area limits around
        c_start_y = int(playable_area.x)
        c_end_y = int(playable_area.x + playable_area.width)
        c_start_x = int(playable_area.y)
        c_end_x = int(playable_area.y + playable_area.height)

        self.climber_grid, overlord_data, choke_data = self._get_map_data(walkable_grid, height_map,
                                                                          c_start_y,
                                                                          c_end_y,
                                                                          c_start_x,
                                                                          c_end_x)

        self.overlord_spots = list(map(Point2, overlord_data))
        self.chokes = []
        id_counter = 0
        for c in choke_data:
            self.chokes.append(CMapChoke(id_counter, c[0], c[1], c[2], c[3], c[4], c[5]))
            id_counter += 1

    @staticmethod
    def _get_map_data(walkable_grid: np.ndarray, height_map: np.ndarray,
                      start_y: int,
                      end_y: int,
                      start_x: int,
                      end_x: int):
        height, width = walkable_grid.shape
        return ext.get_map_data(walkable_grid.flatten(), height_map.flatten(), height, width,
                                start_y, end_y, start_x, end_x)

