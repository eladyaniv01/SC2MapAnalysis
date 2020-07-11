from typing import List, Union, Tuple

import numpy as np
from sc2.position import Point2

from MapAnalyzer.Polygon import Polygon


class Region:
    def __init__(self, map_data, array: np.ndarray, label: int, map_expansions: List[Point2]):
        self.map_data = map_data
        self.array = array
        self.label = label
        self.polygon = Polygon(self)
        self.bases = [base for base in map_expansions if self.polygon.is_inside((base.rounded[1], base.rounded[0]))]
        self.region_ramps = []  # will be set later by mapdata
        self.region_vision_blockers = []  # will be set later by mapdata
        self.region_vb = []
        self.region_chokes = []

    def plot_perimeter(self, self_only=True):
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')
        x, y = zip(*self.polygon.perimeter)
        plt.scatter(x, y)
        plt.title(f"Region {self.label}")
        if self_only:
            plt.grid()
            plt.show()

    def _plot_ramps(self):
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')
        for r in self.region_ramps:
            x, y = zip(*r.points)
            plt.scatter(x, y, color="black", marker=r'$\diamondsuit$')

    def _plot_vision_blockers(self):
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')
        for vb in self.map_data.vision_blockers:
            if self.inside(point=vb):
                plt.text(vb[0],
                         vb[1],
                         "X", c='r')

    def _plot_minerals(self):
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')
        for mineral_field in self.map_data.mineral_fields:
            if self.inside(mineral_field.position.rounded):
                plt.scatter(mineral_field.position[0], mineral_field.position[1], color="blue")

    def _plot_geysers(self):
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')
        for gasgeyser in self.map_data.normal_geysers:
            if self.inside(gasgeyser.position.rounded):
                plt.scatter(gasgeyser.position[0], gasgeyser.position[1], color="yellow", marker=r'$\spadesuit$', s=500,
                            edgecolors="g")

    def plot(self, self_only=True):
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

    def inside(self, point: Union[Point2, Tuple]):
        return self.polygon.is_inside(point)

    @property
    def choke_points(self):
        pass

    @property
    def base_locations(self):
        return self.bases

    @property
    def is_reachable(self, region):  # is connected to another region directly ?
        pass

    @property
    def get_reachable_regions(self):
        pass

    @property
    def get_area(self):
        return self.polygon.area

    def __repr__(self):
        return "Region " + str(self.label)
