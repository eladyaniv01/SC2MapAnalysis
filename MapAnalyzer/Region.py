from functools import lru_cache
from typing import List, TYPE_CHECKING

import numpy as np
from sc2.position import Point2

from MapAnalyzer.Polygon import Polygon
from MapAnalyzer.constructs import MDRamp

if TYPE_CHECKING:
    from MapAnalyzer import MapData


class Region(Polygon):
    def __init__(
            self,
            map_data: 'MapData',
            array: np.ndarray,
            label: int,
            map_expansions: List[Point2],
    ) -> None:
        super().__init__(map_data=map_data, array=array)
        self.map_data = map_data
        self.array = array
        self.label = label
        self.is_region = True
        self.bases = [
                base
                for base in map_expansions
                if self.is_inside_point((base.rounded[0], base.rounded[1]))
        ]  # will be set later by mapdata
        self.region_vision_blockers = []  # will be set later by mapdata
        self.region_vb = []
        self.region_chokes = []

    @property
    def region_ramps(self) -> List[MDRamp]:
        return [r for r in self.areas if r.is_ramp]

    @property
    @lru_cache()
    def connected_regions(self):
        connected_regions = []
        for ramp in self.region_ramps:
            for region in ramp.regions:
                if region is not self and region not in connected_regions:
                    connected_regions.append(region)
        return connected_regions

    @property
    def corners(self) -> List[Point2]:
        """
        corners
        """
        return self.corner_points

    def plot_perimeter(self, self_only: bool = True) -> None:
        """
        plot_perimeter
        """
        import matplotlib.pyplot as plt

        plt.style.use("ggplot")

        x, y = zip(*self.perimeter)
        plt.scatter(x, y)
        plt.title(f"Region {self.label}")
        if self_only:  # pragma: no cover
            plt.grid()

    def _plot_corners(self) -> None:
        import matplotlib.pyplot as plt
        plt.style.use("ggplot")
        for corner in self.corner_points:
            plt.scatter(corner[0], corner[1], marker="v", c="red", s=150)

    def _plot_ramps(self) -> None:
        """
        plot_ramps
        """
        import matplotlib.pyplot as plt
        plt.style.use("ggplot")
        for ramp in self.region_ramps:
            plt.text(
                    # fixme make ramp attr compatible and not reversed
                    ramp.top_center[0],
                    ramp.top_center[1],
                    f"R<{[r.label for r in ramp.regions]}>",
                    bbox=dict(fill=True, alpha=0.3, edgecolor="cyan", linewidth=8),
            )
            # ramp.plot(testing=True)
            x, y = zip(*ramp.points)
            plt.scatter(x, y, color="w")

    def _plot_vision_blockers(self) -> None:
        """
        plot_vision_blockers
        """
        import matplotlib.pyplot as plt

        plt.style.use("ggplot")
        for vb in self.map_data.vision_blockers:
            if self.is_inside_point(point=vb):
                plt.text(vb[0], vb[1], "X", c="r")

    def _plot_minerals(self) -> None:
        """
        plot_minerals
        """
        import matplotlib.pyplot as plt

        plt.style.use("ggplot")
        for mineral_field in self.map_data.mineral_fields:
            if self.is_inside_point(mineral_field.position.rounded):
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
            if self.is_inside_point(gasgeyser.position.rounded):
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
        self._plot_corners()
        if testing:
            self.plot_perimeter(self_only=False)
            return
        if self_only:  # pragma: no cover
            self.plot_perimeter(self_only=True)
        else:  # pragma: no cover
            self.plot_perimeter(self_only=False)

    @property
    def base_locations(self) -> List[Point2]:
        """
        base_locations
        """
        return self.bases

    @property
    def get_area(self) -> int:
        """
        get_area
        """
        return self.area

    def __repr__(self) -> str:  # pragma: no cover
        """
        __repr__
        """
        return "Region " + str(self.label)
