from functools import lru_cache
from typing import List, Union, Tuple

import numpy as np
from sc2.position import Point2

from MapAnalyzer.Polygon import Polygon


class Region:
    """
    Region DocString
    """
    def __init__(self, map_data, array: np.ndarray, label: int, map_expansions: List[Point2]):
        self.map_data = map_data
        self.array = array
        self.label = label
        self.polygon = Polygon(map_data=self.map_data, array=self.array)
        self.bases = [base for base in map_expansions if
                      self.polygon.is_inside_point((base.rounded[0], base.rounded[1]))]
        self.region_ramps = []  # will be set later by mapdata
        self.region_vision_blockers = []  # will be set later by mapdata
        self.region_vb = []
        self.region_chokes = []

    @property
    def center(self):
        """

        :return:
        :rtype:
        """
        return self.polygon.center

    @property
    def corners(self):
        """

        :return:
        :rtype:
        """
        return self.polygon.corner_points

    def plot_perimeter(self, self_only=True):
        """

        :return:
        :rtype:
        """
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')
        x, y = zip(*self.polygon.perimeter)
        plt.scatter(x, y)
        plt.title(f"Region {self.label}")
        if self_only:
            plt.grid()
            plt.show()

    def _plot_ramps(self):
        """

        :return:
        :rtype:
        """
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')
        for r in self.region_ramps:
            x, y = zip(*r.points)
            plt.scatter(x, y, color="black", marker=r'$\diamondsuit$')

    def _plot_vision_blockers(self):
        """

        :return:
        :rtype:
        """
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')
        for vb in self.map_data._vision_blockers:
            if self.inside_p(point=vb):
                plt.text(vb[0],
                         vb[1],
                         "X", c='r')

    def _plot_minerals(self):
        """

        :return:
        :rtype:
        """
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')
        for mineral_field in self.map_data.mineral_fields:
            if self.inside_p(mineral_field.position.rounded):
                plt.scatter(mineral_field.position[0], mineral_field.position[1], color="blue")

    def _plot_geysers(self):
        """

        :return:
        :rtype:
        """
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')
        for gasgeyser in self.map_data.normal_geysers:
            if self.inside_p(gasgeyser.position.rounded):
                plt.scatter(gasgeyser.position[0], gasgeyser.position[1], color="yellow", marker=r'$\spadesuit$', s=500,
                            edgecolors="g")

    def plot(self, self_only=True):
        """

        :param self_only:
        :type self_only:
        :return:
        :rtype:
        """
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')
        self._plot_geysers()
        self._plot_minerals()
        self._plot_ramps()
        self._plot_vision_blockers()
        if self_only:
            self.plot_perimeter(self_only=True)

        else:
            self.plot_perimeter(self_only=False)

    @lru_cache(100)
    def inside_p(self, point: Union[Point2, Tuple]):
        """

        :param point:
        :type point:
        :return:
        :rtype:
        """
        return self.polygon.is_inside_point(point)

    @lru_cache(100)
    def inside_i(self, point: Union[Point2, Tuple]):
        """

        :param point:
        :type point:
        :return:
        :rtype:
        """
        return self.polygon.is_inside_indices(point)

    @property
    def base_locations(self):
        """

        :return:
        :rtype:
        """
        return self.bases

    @property
    def is_reachable(self, region):  # is connected to another region directly ?
        """

        :param region:
        :type region:
        :return:
        :rtype:
        """
        pass

    @property
    def get_reachable_regions(self):
        """

        :return:
        :rtype:
        """
        pass

    @property
    def get_area(self):
        """

        :return:
        :rtype:
        """
        return self.polygon.area

    def __repr__(self):
        """

        :return:
        :rtype:
        """
        return "Region " + str(self.label)
