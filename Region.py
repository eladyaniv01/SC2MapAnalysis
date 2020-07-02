from Polygon import Polygon
import matplotlib.pyplot as plt
import numpy as np
from sc2.position import Point2
from typing import List


class Region:
    def __init__(self, array: np.ndarray, label: int, map_expansions: List[Point2]):
        self.array = array
        self.label = label
        self.polygon = Polygon(self)
        self.bases = [base for base in map_expansions if self.polygon.is_inside((base.rounded[1], base.rounded[0]))]

    def plot_perimeter(self):
        x, y = zip(*self.polygon.perimeter)
        plt.scatter(x, y)
        plt.title(f"Region {self.label}")
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

