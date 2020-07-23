from functools import lru_cache
from multiprocessing.util import log_to_stderr
from typing import List, TYPE_CHECKING, Union

import numpy as np
from numpy import ndarray
from sc2.position import Point2
from scipy.ndimage import center_of_mass

from MapAnalyzer.Region import Region

if TYPE_CHECKING:  # pragma: no cover
    from MapAnalyzer.MapData import MapData

import logging

logger = log_to_stderr(level=logging.INFO)
class Polygon:
    """
    Polygon DocString
    """

    def __init__(self, map_data: "MapData", array: ndarray) -> None:
        self.is_choke = False
        self.is_ramp = False
        self.is_vision_blocker = False
        self.is_region = False
        self.map_data = map_data
        self.array = array
        self.areas = []  # set by map_data / Region
        self.indices = np.where(self.array == 1)
        points = map_data.indices_to_points(self.indices)
        self.points = set([Point2(p) for p in points])
        self.map_data.polygons.append(self)

    @property
    @lru_cache()
    def regions(self):
        if len(self.areas) > 0:
            return [r for r in self.areas if isinstance(r, Region)]
        return []

    def calc_areas(self):
        if self.is_ramp:
            return

        if self.is_choke and self.main_line:
            print(f"going deep! {self}")
            prlist = list(self.perimeter_points)
            crlist = list(self.corner_points)
            points = set(prlist + crlist + list(self.points))
            points = self.main_line
            # print(self)
            # print(f"len(points) {len(points)}")
            areas = self.areas
            # print(f"len areas before {len(self.areas)}")
            for point in points:
                point = int(point[0]), int(point[1])
                new_areas = self.map_data.where_all(point)

                print(f"point = {point} new_areas = {new_areas}")
                if self in new_areas:
                    new_areas.pop(new_areas.index(self))
                # print(f"len(new_areas) {len(new_areas)}")
                areas.extend(new_areas)

            self.areas = list(set(areas))
            # print(f"len areas after {len(self.areas)}")
            # print(self)

    def plot(self, testing: bool = False) -> None:  # pragma: no cover
        """
        plot
        """
        import matplotlib.pyplot as plt
        plt.style.use("ggplot")
        if testing:
            return
        plt.imshow(self.array, origin="lower")
        plt.show()

    @property
    @lru_cache()
    def nodes(self) -> List[Point2]:
        """
        nodes
        """
        return [p for p in self.points]

    @property
    @lru_cache()
    def corner_array(self) -> ndarray:
        """
        corner_array
        """
        from skimage.feature import corner_harris, corner_peaks

        array = corner_peaks(
                corner_harris(self.array), min_distance=3, threshold_rel=0.01
        )
        return array

    @property
    @lru_cache()
    def corner_points(self) -> List[Point2]:
        """
        corner_points
        """
        points = [Point2(p) for p in self.corner_array if self.is_inside_point(Point2(p))]
        return points

    @property
    def center(self) -> Point2:
        """
        since the center is always going to be a float,
        and for performance considerations we use integer coordinates
        we will return the closest point registered
        :return:
        :rtype:
        """
        cm = center_of_mass(self.array)
        return self.map_data.closest_towards_point(points=self.nodes, target=cm)

    @lru_cache(100)
    def is_inside_point(self, point: Union[Point2, tuple]) -> bool:
        """
        is_inside_point
        """
        if point in self.points:
            return True
        if isinstance(point, Point2):
            point = point.rounded
        if point in self.points or point in self.perimeter_points:
            return True
        return False

    @lru_cache(100)
    def is_inside_indices(
            self, point: Union[Point2, tuple]
    ) -> bool:  # pragma: no cover
        """
        is_inside_indices
        """
        if isinstance(point, Point2):
            point = point.rounded
        return point[0] in self.indices[0] and point[1] in self.indices[1]

    @property
    def perimeter(self) -> np.ndarray:
        """
        perimeter
        """
        isolated_region = self.array
        xx, yy = np.gradient(isolated_region)
        edge_indices = np.argwhere(xx ** 2 + yy ** 2 > 0.1)[:, [1, 0]]
        return edge_indices

    @property
    def perimeter_points(self):
        """
        perimeter points
        """
        li = [(p[0], p[1]) for p in self.perimeter]
        return set(li)

    @property
    def area(self) -> int:
        """
        area
        """
        return len(self.points)

    # @property
    # def get_holes(self) -> List[tuple]:  # pragma: no cover
    #     """
    #     :return:
    #     :rtype:
    #     """
    #     # fly zones inside the Polygon
    #     pass
    def __repr__(self):
        return f"<Polygon[size={self.area}]: {self.areas}>"
