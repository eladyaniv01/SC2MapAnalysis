"""todo  split debug / plot functions to here to lower the code lines in MapData.py"""
import inspect
import os
import sys
import warnings
from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING, Union

import numpy as np
from loguru import logger
from numpy import int64, ndarray

from .constants import COLORS, LOG_FORMAT

if TYPE_CHECKING:
    from MapAnalyzer.MapData import MapData


class LogFilter:
    def __init__(self, level: str) -> None:
        self.level = level

    def __call__(self, record: Dict[str, Any]) -> bool:
        levelno = logger.level(self.level).no
        return record["level"].no >= levelno


class MapAnalyzerDebugger:
    """"""

    def __init__(self, map_data: "MapData", loglevel: str = "ERROR") -> None:
        self.map_data = map_data
        self.warnings = warnings
        self.warnings.filterwarnings('ignore', category=DeprecationWarning)
        self.warnings.filterwarnings('ignore', category=RuntimeWarning)
        self.logger = logger
        self.log_filter = LogFilter(loglevel)
        self.logger.remove()
        self.log_format = LOG_FORMAT
        self.logger.add(sys.stderr, format=self.log_format, filter=self.log_filter)

    @staticmethod
    def show():
        import matplotlib.pyplot as plt
        plt.show()

    @staticmethod
    def close():
        import matplotlib.pyplot as plt
        plt.close(fig='all')

    def save(self, filename: str) -> bool:

        for i in inspect.stack():
            if 'test_suite.py' in str(i):
                self.logger.info(f"Skipping save operation on test runs")
                self.logger.debug(f"index = {inspect.stack().index(i)}  {i}")
                return True
        import matplotlib.pyplot as plt
        full_path = os.path.join(os.path.abspath("."), f"{filename}")
        plt.savefig(f"{filename}.png")
        self.logger.debug(f"Plot Saved to {full_path}")

    def plot_regions(self, fontdict: Dict[str, Union[str, int]]) -> None:
        """"""
        import matplotlib.pyplot as plt
        for lbl, reg in self.map_data.regions.items():
            c = COLORS[lbl]
            fontdict["color"] = c
            fontdict["backgroundcolor"] = 'black'
            if c == 'black':
                fontdict["backgroundcolor"] = 'white'
            plt.text(
                    reg.center[0],
                    reg.center[1],
                    reg.label,
                    bbox=dict(fill=True, alpha=0.9, edgecolor=fontdict["backgroundcolor"], linewidth=2),
                    fontdict=fontdict,
            )
            # random color for each perimeter
            x, y = zip(*reg.polygon.perimeter_points)
            plt.scatter(x, y, c=c, marker="1", s=300)
            for corner in reg.polygon.corner_points:
                plt.scatter(corner[0], corner[1], marker="v", c="red", s=150)

    def plot_vision_blockers(self) -> None:
        """
        plot vbs
        """
        import matplotlib.pyplot as plt

        for vb in self.map_data.vision_blockers:
            plt.text(vb[0], vb[1], "X")

        x, y = zip(*self.map_data.vision_blockers)
        plt.scatter(x, y, color="r")

    def plot_normal_resources(self) -> None:
        """
        # todo: account for gold minerals and rich gas
        """
        import matplotlib.pyplot as plt
        for mfield in self.map_data.mineral_fields:
            plt.scatter(mfield.position[0], mfield.position[1], color="blue")
        for gasgeyser in self.map_data.normal_geysers:
            plt.scatter(
                    gasgeyser.position[0],
                    gasgeyser.position[1],
                    color="yellow",
                    marker=r"$\spadesuit$",
                    s=500,
                    edgecolors="g",
            )

    def plot_chokes(self) -> None:
        """
        compute Chokes
        """
        import matplotlib.pyplot as plt
        for choke in self.map_data.map_chokes:
            x, y = zip(*choke.points)
            cm = choke.center
            if choke.is_ramp:
                fontdict = {"family": "serif", "weight": "bold", "size": 15}
                plt.text(cm[0], cm[1], f"R<{[r.label for r in choke.regions]}>", fontdict=fontdict,
                         bbox=dict(fill=True, alpha=0.4, edgecolor="cyan", linewidth=8))
                plt.scatter(x, y, color="w")
            elif choke.is_vision_blocker:

                fontdict = {"family": "serif", "size": 10}
                plt.text(cm[0], cm[1], f"VB<>", fontdict=fontdict,
                         bbox=dict(fill=True, alpha=0.3, edgecolor="red", linewidth=2))
                plt.scatter(x, y, marker=r"$\heartsuit$", s=100, edgecolors="b", alpha=0.3)

            else:
                fontdict = {"family": "serif", "size": 10}
                plt.text(cm[0], cm[1], f"C<{choke.id}>", fontdict=fontdict,
                         bbox=dict(fill=True, alpha=0.3, edgecolor="red", linewidth=2))
                plt.scatter(x, y, marker=r"$\heartsuit$", s=100, edgecolors="r", alpha=0.3)

    def plot_map(
            self, fontdict: dict = None, figsize: int = 20
    ) -> None:
        """
        Plot map
        """

        if not fontdict:
            fontdict = {"family": "serif", "weight": "bold", "size": 25}
        import matplotlib.pyplot as plt
        plt.figure(figsize=(figsize, figsize))
        self.plot_regions(fontdict=fontdict)
        # some maps has no vision blockers
        if len(self.map_data._vision_blockers) > 0:
            self.plot_vision_blockers()
        self.plot_normal_resources()
        self.plot_chokes()
        fontsize = 25

        plt.style.use("ggplot")
        plt.imshow(self.map_data.region_grid.astype(float), origin="lower")
        plt.imshow(self.map_data.terrain_height, alpha=1, origin="lower", cmap="terrain")
        x, y = zip(*self.map_data.nonpathable_indices_stacked)
        plt.scatter(x, y, color="grey")
        ax = plt.gca()
        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(fontsize)
            tick.label1.set_fontweight("bold")
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(fontsize)
            tick.label1.set_fontweight("bold")
        plt.grid()

    def plot_influenced_path(self, start: Tuple[int64, int64], goal: Tuple[int64, int64], weight_array: ndarray,
                             name: Optional[str] = None,
                             fontdict: dict = None) -> None:
        import matplotlib.pyplot as plt
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        from matplotlib.cm import ScalarMappable
        if not fontdict:
            fontdict = {"family": "serif", "weight": "bold", "size": 20}
        plt.style.use(["ggplot", "bmh"])
        org = "lower"
        if name is None:
            name = self.map_data.map_name
        arr = weight_array.copy()
        path = self.map_data.pathfind(start, goal,
                                      grid=arr,
                                      sensitivity=1)
        ax: plt.Axes = plt.subplot(1, 1, 1)
        if path is not None:
            path = np.flipud(path)  # for plot align
            self.map_data.logger.info("Found")
            x, y = zip(*path)
            ax.scatter(x, y, s=3, c='green')
        else:
            self.map_data.logger.info("Not Found")

            x, y = zip(*[start, goal])
            ax.scatter(x, y)

        influence_cmap = plt.cm.get_cmap("afmhot")
        ax.text(start[0], start[1], f"Start {start}")
        ax.text(goal[0], goal[1], f"Goal {goal}")
        ax.imshow(self.map_data.path_arr, alpha=0.5, origin=org)
        ax.imshow(self.map_data.terrain_height, alpha=0.5, origin=org, cmap='bone')
        arr = np.where(arr == np.inf, 0, arr).T
        ax.imshow(arr, origin=org, alpha=0.3, cmap=influence_cmap)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        sc = ScalarMappable(cmap=influence_cmap)
        sc.set_array(arr)
        sc.autoscale()
        cbar = plt.colorbar(sc, cax=cax)
        cbar.ax.set_ylabel('Pathing Cost', rotation=270, labelpad=25, fontdict=fontdict)
        plt.title(f"{name}", fontdict=fontdict, loc='right')
        plt.grid()
