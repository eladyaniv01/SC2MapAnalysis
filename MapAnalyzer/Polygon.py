from functools import lru_cache
from typing import List, TYPE_CHECKING, Union

import numpy as np
from numpy import ndarray
from sc2.position import Point2
from scipy.ndimage import center_of_mass

if TYPE_CHECKING:  # pragma: no cover
    from MapAnalyzer.MapData import MapData
    from MapAnalyzer.Region import Region


class Polygon:
    """
    Polygon DocString
    """

    def __init__(self, map_data: "MapData", array: ndarray) -> None:
        self.map_data = map_data
        self.array = array
        self.indices = np.where(self.array == 1)
        points = map_data.indices_to_points(self.indices)
        self.points = set([Point2(p) for p in points])

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
        points = [Point2(p) for p in self.corner_array]
        return points

    @property
    @lru_cache()
    def region(self) -> "Region":
        """
        region
        """
        return self.map_data.in_region_p(self.center)

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
        return point in self.points

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
        edge_indices = np.argwhere(xx ** 2 + yy ** 2 > 0.1)
        return edge_indices

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
