from typing import TYPE_CHECKING

import numpy as np
from sc2.game_info import Ramp as sc2Ramp
from scipy.ndimage import center_of_mass

if TYPE_CHECKING:
    from .MapData import MapData


class ChokeArea:
    def __init__(self, map_data: "MapData", points, main_line=None):
        self.map_data = map_data
        self.regions = []  # set by map_data
        self.points = points
        self.main_line = main_line

    def get_width(self):
        import math
        if self.main_line is not None:
            x1, y1 = self.main_line[0][0], self.main_line[0][1]
            x2, y2 = self.main_line[1][0], self.main_line[1][1]
            return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    @property
    def indices(self):
        return self.map_data.points_to_indices(self.points)

    @property
    def center(self):
        cm = center_of_mass(self.array)
        return np.int(cm[0]), np.int(cm[1])

    @property
    def array(self):
        mask = np.zeros(self.map_data.region_grid.shape, dtype='int')
        mask[self.indices] = 1
        return mask

    @property
    def area(self):
        return len(self.points)

    def __repr__(self):
        return f'<ChokeArea;{self.area}> of {[r for r in self.regions]}'


class MDRamp(ChokeArea):
    def __init__(self, map_data: "MapData", points, ramp: sc2Ramp):
        self.ramp = ramp
        super().__init__(map_data=map_data, points=points)

    @property
    def top_center(self):
        return self.ramp.top_center

    @property
    def bottom_center(self):
        return self.ramp.bottom_center

    def __repr__(self):
        return f'<MDRamp{self.ramp} of {self.regions}>'


class VisionBlockerArea(ChokeArea):
    def __init__(self, map_data: "MapData", points):
        super().__init__(map_data=map_data, points=points)

    def __repr__(self):
        return f'<VisionBlockerArea;{self.area}> of {[r for r in self.regions]}'
