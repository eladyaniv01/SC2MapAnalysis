from functools import lru_cache
from typing import List, Union

import numpy as np
from sc2.position import Point2

from . import MapData, Polygon


class Region:
    """
    Region DocString
    """

    def __init__(
            self,
            map_data: MapData,
            array: np.ndarray,
            label: int,
            map_expansions: List[Point2],
    ) -> None:
        self.map_data = map_data
        self.array = array
        self.label = label

        self.polygon = Polygon.Polygon(map_data=self.map_data, array=self.array)  # for constructor
        self.polygon.areas.append(self)
        self.polygon.is_region = True
        self.bases = [
                base
                for base in map_expansions
                if self.polygon.is_inside_point((base.rounded[0], base.rounded[1]))
        ]
        self.region_ramps = []  # will be set later by mapdata
        self.region_vision_blockers = []  # will be set later by mapdata
        self.region_vb = []
        self.region_chokes = []

    @property
    def center(self) -> Point2:
        """
        center
        """
        return self.polygon.center

    @property
    def corners(self) -> List[Point2]:
        """
        corners
        """
        return self.polygon.corner_points

    def plot_perimeter(self, self_only: bool = True) -> None:
        """
        plot_perimeter
        """
        import matplotlib.pyplot as plt

        plt.style.use("ggplot")

        y, x = zip(*self.polygon.perimeter)  # reversing for "lower" origin
        plt.scatter(x, y)
        plt.title(f"Region {self.label}")
        if self_only:  # pragma: no cover
            plt.grid()
            plt.show()

    def _plot_ramps(self) -> None:
        """
        plot_ramps
        """
        import matplotlib.pyplot as plt

        plt.style.use("ggplot")
        for r in self.region_ramps:
            x, y = zip(*r.points)
            plt.scatter(x, y, color="black", marker=r"$\diamondsuit$")

    def _plot_vision_blockers(self) -> None:
        """
        plot_vision_blockers
        """
        import matplotlib.pyplot as plt

        plt.style.use("ggplot")
        for vb in self.map_data.vision_blockers:
            if self.inside_p(point=vb):
                plt.text(vb[0], vb[1], "X", c="r")

    def _plot_minerals(self) -> None:
        """
        plot_minerals
        """
        import matplotlib.pyplot as plt

        plt.style.use("ggplot")
        for mineral_field in self.map_data.mineral_fields:
            if self.inside_p(mineral_field.position.rounded):
                plt.scatter(
                        mineral_field.position[0], mineral_field.position[1], color="blue"
                )

    def _plot_geysers(self) -> None:
        """
        plot_geysers
        """
        import matplotlib.pyplot as plt

        plt.style.use("ggplot")
        for gasgeyser in self.map_data.normal_geysers:
            if self.inside_p(gasgeyser.position.rounded):
                plt.scatter(
                        gasgeyser.position[0],
                        gasgeyser.position[1],
                        color="yellow",
                        marker=r"$\spadesuit$",
                        s=500,
                        edgecolors="g",
                )

    def plot(self, self_only: bool = True, testing: bool = False) -> None:
        """
            plot
        """
        import matplotlib.pyplot as plt

        plt.style.use("ggplot")

        self._plot_geysers()
        self._plot_minerals()
        self._plot_ramps()
        self._plot_vision_blockers()
        if testing:
            self.plot_perimeter(self_only=False)
            return
        if self_only:  # pragma: no cover
            self.plot_perimeter(self_only=True)
        else:  # pragma: no cover
            self.plot_perimeter(self_only=False)

    @lru_cache(100)
    def inside_p(self, point: Union[Point2, tuple]) -> bool:
        """
        inside_p
        """
        return self.polygon.is_inside_point(point)

    @lru_cache(100)
    def inside_i(self, point: Union[Point2, tuple]) -> bool:  # pragma: no cover
        """
        inside_i
        """
        return self.polygon.is_inside_indices(point)

    @property
    def base_locations(self) -> List[Point2]:
        """
        base_locations
        """
        return self.bases

    # @property
    # def is_reachable(self, areas):  # pragma: no cover
    #     """
    #     is connected to another areas directly
    #     :param areas:
    #     :type areas:
    #     :return:
    #     :rtype:
    #     """
    #     pass

    # @property
    # def get_reachable_regions(self):  # pragma: no cover
    #     """
    #
    #     :return:
    #     :rtype:
    #     """
    #     pass

    @property
    def get_area(self) -> int:
        """
        get_area
        """
        return self.polygon.area

    def __repr__(self):  # pragma: no cover
        """
        __repr__
        """
        return "Region " + str(self.label)
