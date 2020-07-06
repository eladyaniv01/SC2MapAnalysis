from typing import List

import matplotlib.pyplot as plt
import numpy as np
from sc2.position import Point2

from Polygon import Polygon


class Region:
    def __init__(self, map_data, array: np.ndarray, label: int, map_expansions: List[Point2]):
        self.map_data = map_data
        self.array = array
        self.label = label
        self.polygon = Polygon(self)
        self.bases = [base for base in map_expansions if self.polygon.is_inside((base.rounded[1], base.rounded[0]))]
        self.region_ramps = []  # will be set later by mapdata

    def plot_perimeter(self):
        # swap axes for aligned plot
        x, y = zip(*self.polygon.perimeter[:, [1, 0]])
        plt.scatter(x, y)
        plt.title(f"Region {self.label}")
        plt.grid()
        plt.show()

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
