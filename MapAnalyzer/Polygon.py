from functools import lru_cache
from typing import List, Set, Tuple, TYPE_CHECKING, Union

import numpy as np
from numpy import int64, ndarray
from sc2.position import Point2
from scipy.ndimage import center_of_mass

if TYPE_CHECKING:
    from MapAnalyzer import MapData, Region


class BuildablePoints:
    """

    Represents the Buildable Points in a :class:`.Polygon`,

    "Lazy" class that will only update information when it is needed

    Tip:
        :class:`.BuildablePoints` that belong to a :class:`.ChokeArea`  are always the edges, this is useful for walling off

    """

    def __init__(self, polygon):
        self.polygon = polygon
        self.points = None

    @property
    def free_pct(self) -> float:
        """

        A simple method for knowing what % of the points is left available out of the total

        """
        if self.points is None:
            self.polygon.map_data.logger.warning("BuildablePoints needs to update first")
            self.update()
        return len(self.points) / len(self.polygon.points)

    def update(self) -> None:
        """

        To be called only by :class:`.Polygon`, this ensures that updates are done in a lazy fashion,

        the update is evaluated only when there is need for the information, otherwise it is ignored

        """
        parr = self.polygon.map_data.points_to_numpy_array(self.polygon.points)
        [self.polygon.map_data.add_cost(position=(unit.position.x, unit.position.y), radius=unit.radius, grid=parr,
                                        safe=False)
         for unit in
         self.polygon.map_data.bot.all_units]
        buildable_indices = np.where(parr == 1)
        buildable_points = []
        _points = list(self.polygon.map_data.indices_to_points(buildable_indices))
        placement_grid = self.polygon.map_data.placement_arr.T
        for p in _points:
            if p[0] < placement_grid.shape[0] and p[1] < placement_grid.shape[1]:
                if placement_grid[p] == 1:
                    buildable_points.append(p)
        self.points = buildable_points


class Polygon:
    """

    Base Class for "Area"

    """

    # noinspection PyProtectedMember
    def __init__(self, map_data: "MapData", array: ndarray) -> None:  # pragma: no cover
        self.id = None  # TODO
        self.is_choke = False
        self.is_ramp = False
        self.is_vision_blocker = False
        self.is_region = False
        self.map_data = map_data
        self.array = array
        self.areas = []  # set by map_data / Region
        self.indices = np.where(self.array == 1)
        self._set_points()
        self.map_data.polygons.append(self)
        self._buildable_points = BuildablePoints(polygon=self)

    def _set_points(self):
        self._clean_points = self.map_data.indices_to_points(self.indices)
        self.points = set([Point2((int(p[0]), int(p[1]))) for p in self._clean_points])
        self.points = set([Point2(p) for p in self._clean_points])
        points = [p for p in self.map_data.indices_to_points(self.indices)]
        points.extend(self.corner_points)
        points.extend(self.perimeter_points)
        self.points = set([Point2((int(p[0]), int(p[1]))) for p in points])
        self.indices = self.map_data.points_to_indices(self.points)

    @property
    def buildable_points(self) -> BuildablePoints:
        """

        :rtype: :class:`.BuildablePoints`

        Is a responsible for holding and updating the buildable points of it's respected :class:`.Polygon`

        """
        self._buildable_points.update()
        return self._buildable_points

    @property
    def regions(self) -> List["Region"]:
        """

        :rtype: List[:class:`.Region`]

        Filters out every Polygon that is not a region, and is inside / bordering with ``self``

        """
        from MapAnalyzer.Region import Region
        if len(self.areas) > 0:
            return [r for r in self.areas if isinstance(r, Region)]
        return []

    def calc_areas(self) -> None:
        # This is called by MapData, at a specific point in the sequence of compiling the map
        # this method uses where_all which means
        # it should be called at the end of the map compilation when areas are populated
        points = self.perimeter_points
        areas = self.areas
        for point in points:
            point = int(point[0]), int(point[1])
            new_areas = self.map_data.where_all(point)
            if self in new_areas:
                new_areas.pop(new_areas.index(self))
            areas.extend(new_areas)
        self.areas = list(set(areas))

    def plot(self, testing: bool = False) -> None:  # pragma: no cover
        """

        plot

        """
        import matplotlib.pyplot as plt
        plt.style.use("ggplot")

        plt.imshow(self.array, origin="lower")
        if testing:
            return
        plt.show()

    @property
    @lru_cache()
    def nodes(self) -> List[Point2]:
        """

        List of :class:`.Point2`

        """
        return [p for p in self.points]

    @property
    @lru_cache()
    def corner_array(self) -> ndarray:
        """

        This is how the corners are calculated

        TODO
            make this adjustable to the user

        """
        from skimage.feature import corner_harris, corner_peaks

        array = corner_peaks(
                corner_harris(self.array), min_distance=3, threshold_rel=0.01
        )
        return array

    @property
    @lru_cache()
    def width(self) -> float:
        """

        Lazy width calculation,   will be approx 0.5 < x < 1.5 of real width

        """
        pl = list(self.perimeter_points)
        s1 = min(pl)
        s2 = max(pl)
        x1, y1 = s1[0], s1[1]
        x2, y2 = s2[0], s2[1]
        return np.math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    @property
    @lru_cache()
    def corner_points(self) -> List[Point2]:
        """

        :rtype: List[:class:`.Point2`]

        """
        points = [Point2((int(p[0]), int(p[1]))) for p in self.corner_array if self.is_inside_point(Point2(p))]
        return points

    @property
    def _clean_points(self) -> List[Tuple[int64, int64]]:
        # For internal usage

        return list(self._clean_points)  # needs to be array-like for numpy calcs

    @property
    def center(self) -> Point2:
        """

        Since the center is always going to be a ``float``,

        and for performance considerations we use integer coordinates.

        We will return the closest point registered

        """

        cm = self.map_data.closest_towards_point(points=self._clean_points, target=center_of_mass(self.array))
        return cm

    @lru_cache()
    def is_inside_point(self, point: Union[Point2, tuple]) -> bool:
        """

        Query via Set(Point2)  ''fast''

        """
        if isinstance(point, Point2):
            point = point.rounded
        if point in self.points:
            return True
        return False

    @lru_cache()
    def is_inside_indices(
            self, point: Union[Point2, tuple]
    ) -> bool:  # pragma: no cover
        """

        Query via 2d np.array  ''slower''

        """
        if isinstance(point, Point2):
            point = point.rounded
        return point[0] in self.indices[0] and point[1] in self.indices[1]

    @property
    def perimeter(self) -> np.ndarray:
        """

        The perimeter is interpolated between inner and outer cell-types using broadcasting

        """
        isolated_region = self.array
        xx, yy = np.gradient(isolated_region)
        edge_indices = np.argwhere(xx ** 2 + yy ** 2 > 0.1)
        return edge_indices

    @property
    def perimeter_points(self) -> Set[Tuple[int64, int64]]:
        """

        Useful method for getting  perimeter points

        """
        li = [Point2((int(p[0]), int(p[1]))) for p in self.perimeter]
        return set(li)

    @property
    def area(self) -> int:
        """

        Sum of all points

        """
        return len(self.points)

    def __repr__(self) -> str:
        return f"<Polygon[size={self.area}]: {self.areas}>"
