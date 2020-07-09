from typing import Tuple, List, Union, TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from sc2.position import Point2
from scipy.ndimage import center_of_mass

if TYPE_CHECKING:
    from .Region import Region


class Polygon:

    def __init__(self, region: "Region"):
        self.region = region
        self.array = region.array
        self.indices = np.where(self.array == 1)

    def plot(self):
        plt.imshow(self.array, origin="lower")
        plt.show()

    @property
    def center(self):
        cm = center_of_mass(self.array)
        return np.int(cm[1]), np.int(cm[0])

    def is_inside(self, point: Union[Point2, Tuple]) -> bool:
        if isinstance(point, Point2):
            point = point.rounded
        return point[0] in self.indices[1] and point[1] in self.indices[0]

    @property
    def perimeter(self) -> Tuple[np.ndarray, np.ndarray]:
        isolated_region = self.region.array
        xx, yy = np.gradient(isolated_region)
        edge_indices = np.argwhere(xx ** 2 + yy ** 2 > 0.1)[:, [1, 0]]
        return edge_indices

    @property
    def area(self):
        return len(self.indices[0])

    @property
    def get_holes(self) -> List[Tuple]:
        # fly zones inside the Polygon
        pass
