import logging
from functools import lru_cache
# from multiprocessing.dummy import Pool
from multiprocessing import log_to_stderr
from time import time
from typing import Dict, List, Optional, Set, Tuple, Union

import numpy as np
from numpy import float64, int64
from numpy.core._multiarray_umath import ndarray
from sc2.bot_ai import BotAI
from sc2.position import Point2
from scipy.ndimage import binary_fill_holes, center_of_mass, generate_binary_structure, label as ndlabel
from scipy.spatial import distance

from MapAnalyzer.constants import BINARY_STRUCTURE, MAX_REGION_AREA, MIN_REGION_AREA
from MapAnalyzer.constructs import ChokeArea, MDRamp, VisionBlockerArea
from MapAnalyzer.Region import Region
from .sc2pathlibp import Sc2Map

logger = log_to_stderr(level=logging.INFO)



class MapData:
    """
    MapData DocString
    """

    def __init__(self, bot: BotAI, pool: int = 4) -> None:
        self.i = 0
        self.pool = pool
        self.min_region_area = MIN_REGION_AREA
        self.max_region_area = MAX_REGION_AREA
        self.regions: dict = {}  # set later
        self.corners: list = []  # set later
        self.polygons: list = []  # set later
        # store relevant data from bot instance for later use
        self.bot = bot
        self.map_name: str = bot.game_info.map_name
        self.placement_arr: ndarray = bot.game_info.placement_grid.data_numpy
        self.path_arr: ndarray = bot.game_info.pathing_grid.data_numpy
        self.base_locations: list = bot.expansion_locations_list
        self.map_ramps: list = []
        self.terrain_height: ndarray = bot.game_info.terrain_height.data_numpy
        self._vision_blockers: Set[Point2] = bot.game_info.vision_blockers
        self.map_chokes: list = []  # set later  on compile
        self.map_vision_blockers: list = []  # set later  on compile
        self.vision_blockers_labels: list = []  # set later  on compile
        self.vision_blockers_grid: list = []  # set later  on compile
        self.region_grid: Union[ndarray, None] = None

        nonpathable_indices = np.where(bot.game_info.pathing_grid.data_numpy == 0)
        self.nonpathable_indices_stacked = np.column_stack(
                (nonpathable_indices[1], nonpathable_indices[0])
        )
        self.mineral_fields = bot.mineral_field
        self.normal_geysers = bot.vespene_geyser
        self.pathlib_map = None
        self._get_pathlib_map()
        self.compile_map()  # this is called on init, but allowed to be called again every step

    def _clean_polys(self):
        pols = self.polygons.copy()
        # print(len(self.polygons))
        for pol in pols:
            if pol.area > self.max_region_area:
                self.polygons.pop(self.polygons.index(pol))

    def compile_map(self) -> None:
        """user can call this to recompute"""
        st = time()
        self._calc_grid()
        ed = time()
        print(f"delta _calc_grid() {ed - st}")
        st = time()
        self._calc_regions()
        ed = time()
        print(f"delta _calc_regions() {ed - st}")
        st = time()
        self._calc_vision_blockers()
        ed = time()
        print(f"delta _calc_vision_blockers() {ed - st}")
        st = time()
        self._calc_chokes()
        ed = time()
        print(f"delta _calc_chokes() {ed - st}")
        st = time()
        self._clean_polys()
        ed = time()
        print(f"delta _clean_polys() {ed - st}")
        # return
        st = time()
        for poly in self.polygons:
            poly.calc_areas()
        num_pools = self.pool
        sc = set(self.map_chokes)
        assert (len(sc) == len(self.map_chokes)), "O.o"
        # def _do_calc(job):
        #     # log_to_stderr(20)
        #     # logger = get_logger()
        #     # logger.info(msg="hi")
        #     job.calc_areas()
        #
        # jobs = []
        # for poly in self.polygons:
        #     jobs.append(poly)
        # pool = Pool(processes=num_pools)
        # for job in jobs:
        #     pool.apply_async(job.calc_areas())
        # # pool.map(_do_calc, jobs)
        ed = time()
        # print(f"Pools {num_pools}, delta {ed - st}")
        print(f"no mp, delta {ed - st}")

    @property
    def vision_blockers(self) -> Set[Point2]:
        """
        compute Region
        """
        return self._vision_blockers



    def _get_pathlib_map(self) -> None:

        """
        Will initialize the sc2pathlib `SC2Map` object for future use
        """
        self.pathlib_map = Sc2Map(
                self.path_arr,
                self.placement_arr,
                self.terrain_height,
                self.bot.game_info.playable_area,
        )

    @lru_cache(200)
    def where_all(
            self, point: Union[Point2, tuple]
    ) -> Union[
        List[Union[MDRamp, VisionBlockerArea]],
        List[VisionBlockerArea],
        List[Union[Region, VisionBlockerArea]],
    ]:
        """
        Will query a point on the map and will return a list of all Area's that point belong to

        region query 21.5 µs ± 652 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
        choke query 18 µs ± 1.25 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        ramp query  22 µs ± 982 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
        """
        results = []
        if isinstance(point, Point2):
            point = point.rounded
        if isinstance(point, tuple):
            point = int(point[0]), int(point[1])

        for region in self.regions.values():
            if region.inside_p(point):
                results.append(region)
        for ramp in self.map_ramps:
            if ramp.is_inside_point(point):
                results.append(ramp)
        for vba in self.map_vision_blockers:
            if vba.is_inside_point(point):
                results.append(vba)
        return results

    @lru_cache(100)
    def where(
            self, point: Union[Point2, tuple]
    ) -> Union[Region, MDRamp, VisionBlockerArea]:
        """
        Will query a point on the map and will return the first result in the following order:
        Region,
        MDRamp,
        VisionBlockerArea

        region query 7.09 µs ± 329 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        ramp query 11.7 µs ± 1.13 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        choke query  17.9 µs ± 1.22 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        """
        if isinstance(point, Point2):
            point = point.rounded
        if isinstance(point, tuple):
            point = int(point[0]), int(point[1])

        for region in self.regions.values():
            if region.inside_p(point):
                return region
        for ramp in self.map_ramps:
            if ramp.is_inside_point(point):
                return ramp
        for vba in self.map_vision_blockers:
            if vba.is_inside_point(point):
                return vba

    @lru_cache(100)
    def in_region_p(self, point: Union[Point2, tuple]) -> Optional[Region]:
        """
        will query a if a point is in, and in which Region using Set of Points <fast>
        time benchmark 4.35 µs ± 27.5 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        as long as polygon points is of type set, not list
        """
        if isinstance(point, Point2):
            point = point.rounded
        if isinstance(point, tuple):
            point = int(point[0]), int(point[1])
        for region in self.regions.values():
            if region.inside_p(point):
                return region

    @lru_cache(100)
    def in_region_i(
            self, point: Union[Point2, tuple]
    ) -> Optional[Region]:  # pragma: no cover
        """
        will query a if a point is in, and in which Region using Indices <slow>
        time benchmark 18.6 µs ± 197 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        """
        if isinstance(point, Point2):
            point = point.rounded
        if isinstance(point, tuple):
            point = int(point[0]), int(point[1])
        for region in self.regions.values():
            if region.inside_i(point):
                return region

    @staticmethod
    def indices_to_points(
            indices: Union[ndarray, Tuple[ndarray, ndarray]]
    ) -> Set[Tuple[int64, int64]]:
        """
        convert indices to a set of points
        Will only work when both dimensions are of same length
        """

        return set([(indices[0][i], indices[1][i]) for i in range(len(indices[0]))])

    @staticmethod
    def points_to_indices(points: Set[Tuple[int, int]]) -> Tuple[ndarray, ndarray]:
        """
        convert points to a tuple of two 1d arrays
        """
        return np.array([p[0] for p in points]), np.array([p[1] for p in points])

    def points_to_numpy_array(
            self, points: Union[Set[Tuple[int64, int64]], List[Point2], Set[Point2]]
    ) -> ndarray:
        """
        convert points to numpy ndarray
        """
        rows, cols = self.path_arr.shape
        arr = np.zeros((rows, cols), dtype=np.uint8)
        indices = self.points_to_indices(points)
        arr[indices] = 1
        return arr

    @staticmethod
    def distance(p1: Point2, p2: Point2) -> float64:
        """
        euclidean distance
        """
        return abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])

    @staticmethod
    def closest_node_idx(
            node: Union[Point2, ndarray], nodes: Union[List[Tuple[int, int]], ndarray]
    ) -> int:
        """
        given a list of nodes `Ln`  and a single node `Nb`,
        will return the index of the closest node in the list to `Nb`
        """
        closest_index = distance.cdist([node], nodes).argmin()
        return closest_index

    def closest_towards_point(
            self, points: List[Point2], target: Union[Point2, tuple]
    ) -> Point2:
        """
        given a list/set of points, and a target,
        will return the point that is closest to that target
        Example usage would be to calculate a position for
        tanks in direction to the enemy forces
        passing in the Area's corners as points and enemy army's location as target
        """
        return points[self.closest_node_idx(node=target, nodes=points)]

    @staticmethod
    def _clean_ramps(region: Region) -> None:
        """ utility function to remove over populated ramps """
        for mramp in region.region_ramps:
            if len(mramp.regions) < 2:
                region.region_ramps.remove(mramp)

    def _calc_grid(self) -> None:
        """ converting the placement grid to our own kind of grid"""
        # cleaning the grid and then searching for 2x2 patterned regions
        grid = binary_fill_holes(self.placement_arr).astype(int)

        s = generate_binary_structure(BINARY_STRUCTURE, BINARY_STRUCTURE)
        labeled_array, num_features = ndlabel(grid, structure=s)

        # for some operations the array must have same numbers or rows and cols,  adding
        # zeros to fix that
        # rows, cols = labeled_array.shape
        # self.region_grid = np.append(labeled_array, np.zeros((abs(cols - rows), cols)), axis=0)
        self.region_grid = labeled_array.astype(int)
        self.regions_labels = np.unique(self.region_grid)
        vb_points = self._vision_blockers

        # some maps has no vision blockers
        if len(vb_points):
            vision_blockers_indices = self.points_to_indices(vb_points)
            vision_blockers_array = np.zeros(self.region_grid.shape, dtype="int")
            vision_blockers_array[vision_blockers_indices] = 1
            vb_labeled_array, vb_num_features = ndlabel(vision_blockers_array)
            self.vision_blockers_grid = vb_labeled_array
            self.vision_blockers_labels = np.unique(vb_labeled_array)

    def _calc_ramps(self, region) -> None:
        """
        probably the most expensive operation other than plotting ,  need to optimize
        """
        if len(self.map_ramps) == 0:
            self.map_ramps = [MDRamp(map_data=self,
                                     ramp=r,
                                     array=self.points_to_numpy_array(r.points))
                              for r in self.bot.game_info.map_ramps]

        ramp_nodes = [ramp.center for ramp in self.map_ramps]
        perimeter_nodes = region.polygon.perimeter[:, [1, 0]]
        result_ramp_indexes = list(
                set([self.closest_node_idx(n, ramp_nodes) for n in perimeter_nodes])
        )
        for rn in result_ramp_indexes:
            # and distance from perimeter is less than ?
            ramp = [r for r in self.map_ramps if r.center == ramp_nodes[rn]][0]
            """for ramp in map ramps  if ramp exists,  append the regions if not,  create new one"""
            if region not in ramp.areas:
                ramp.areas.append(region)
            region.region_ramps.append(ramp)
        ramps = []
        n = 8
        for ramp in region.region_ramps:
            for p in region.polygon.perimeter:
                if (
                        self.distance(p, ramp.bottom_center) < n
                        or self.distance(p, ramp.top_center) < n
                ):
                    ramps.append(ramp)
        ramps = list(set(ramps))

        region.region_ramps = ramps
        # self._clean_ramps(region)

    def _calc_vision_blockers(self) -> None:
        """
        compute VisionBlockerArea
        """
        for i in range(len(self.vision_blockers_labels)):
            indices = np.where(self.vision_blockers_grid == i)
            points = self.indices_to_points(indices)
            vb_arr = self.points_to_numpy_array(points)
            if len(indices[0]):
                vba = VisionBlockerArea(map_data=self, array=vb_arr)
                # region = self.in_region_p(vba.center)
                #
                # if region and 5 < vba.area:
                #     vba.areas.append(region)
                #     region.region_vision_blockers.append(vba)
                if vba.area <= 200:
                    self.map_vision_blockers.append(vba)
                    areas = self.where_all(vba.center)
                    if len(areas) > 0:
                        for area in areas:
                            if area is not vba:
                                vba.areas.append(area)

                else:
                    self.polygons.pop(self.polygons.index(vba))

    def _calc_chokes(self) -> None:
        """
        compute ChokeArea
        """
        chokes = self.pathlib_map.chokes
        self.map_chokes = self.map_ramps.copy()
        self.map_chokes.extend(self.map_vision_blockers.copy())
        for choke in chokes:
            points = [Point2(p) for p in choke.pixels]
            if len(points) > 0:
                new_choke_array = self.points_to_numpy_array(points)
                cm = center_of_mass(new_choke_array)
                cm = int(cm[0]), int(cm[1])
                areas = self.where_all(cm)
                if len(areas) > 0:
                    for area in areas:
                        if isinstance(area, (MDRamp, VisionBlockerArea)):  # we already have it so move on
                            continue
                    new_choke = ChokeArea(
                            map_data=self, array=new_choke_array, main_line=choke.main_line
                    )
                    for area in areas:
                        if isinstance(area, Region):
                            area.region_chokes.append(new_choke)
                        new_choke.areas.append(area)
                    self.map_chokes.append(new_choke)
                else:  # pragma: no cover
                    print(
                            f"<{self.bot.game_info.map_name}>: "
                            f"please report bug no area found for choke area"
                            f" with center {cm}"
                    )


    def _calc_regions(self) -> None:
        """
        compute Region
        """
        # some areas are with area of 1, 2 ,5   these are not what we want,
        # so we filter those out
        pre_regions = {}
        for i in range(len(self.regions_labels)):
            region = Region(
                    array=np.where(self.region_grid == i, 1, 0).T,
                    label=i,
                    map_data=self,
                    map_expansions=self.base_locations,
            )
            pre_regions[i] = region
            # gather the regions that are bigger than self.min_region_area
        j = 0
        for region in pre_regions.values():
            if self.max_region_area > region.get_area > self.min_region_area:
                region.label = j
                self.regions[j] = region
                self._calc_ramps(region=region)
                j += 1

    def save_plot(self) -> None:
        """
        Will save the plot to a file names after the map name
        """
        self.plot_map(save=True)

    def _plot_regions(self, fontdict: Dict[str, Union[str, int]]) -> None:
        """
        compute Region
        """
        import matplotlib.pyplot as plt

        for lbl, reg in self.regions.items():
            plt.text(
                    reg.center[0],
                    reg.center[1],
                    reg.label,
                    bbox=dict(fill=True, alpha=0.5, edgecolor="red", linewidth=2),
                    fontdict=fontdict,
            )
            # random color for each perimeter
            y, x = zip(*reg.polygon.perimeter)
            plt.scatter(x, y, cmap="accent", marker="1", s=300)
            for corner in reg.polygon.corner_points:
                plt.scatter(corner[0], corner[1], marker="v", c="red", s=150)

    def _plot_ramps(self) -> None:
        """
        compute Region
        """
        import matplotlib.pyplot as plt

        for ramp in self.map_ramps:
            plt.text(
                    ramp.top_center[0],
                    ramp.top_center[1],
                    f"R<{[r.label for r in ramp.regions]}>",
                    bbox=dict(fill=True, alpha=0.3, edgecolor="cyan", linewidth=8),
            )
            x, y = zip(*ramp.points)
            plt.scatter(x, y, color="w")

    def _plot_vision_blockers(self) -> None:
        """
        compute Region
        """
        import matplotlib.pyplot as plt

        for vb in self._vision_blockers:
            plt.text(vb[0], vb[1], "X")

        x, y = zip(*self._vision_blockers)
        plt.scatter(x, y, color="r")

    def _plot_normal_resources(self) -> None:
        """
        compute Region
        """
        import matplotlib.pyplot as plt

        for mfield in self.mineral_fields:
            plt.scatter(mfield.position[0], mfield.position[1], color="blue")

        for gasgeyser in self.normal_geysers:
            plt.scatter(
                    gasgeyser.position[0],
                    gasgeyser.position[1],
                    color="yellow",
                    marker=r"$\spadesuit$",
                    s=500,
                    edgecolors="g",
            )

    def _plot_chokes(self) -> None:
        """
        compute Region
        """
        import matplotlib.pyplot as plt

        for choke in self.map_chokes:
            x, y = zip(*choke.points)
            cm = choke.center
            plt.text(cm[0], cm[1], f"C<{choke.areas}>",
                     bbox=dict(fill=True, alpha=0.3, edgecolor="cyan", linewidth=8))
            # plt.text(cm[0], cm[1], f"C <{choke.areas}>")
            plt.scatter(x, y, marker=r"$\heartsuit$", s=100, edgecolors="g")


    def plot_map(
            self, fontdict: dict = None, save: bool = False, figsize: int = 20
    ) -> None:
        """
        compute Region
        """
        import matplotlib.pyplot as plt

        plt.style.use("ggplot")
        if not fontdict:
            fontdict = {"family": "serif", "weight": "bold", "size": 25}

        plt.figure(figsize=(figsize, figsize))
        plt.imshow(self.region_grid, origin="lower")
        plt.imshow(self.terrain_height, alpha=1, origin="lower", cmap="terrain")
        x, y = zip(*self.nonpathable_indices_stacked)
        plt.scatter(x, y, color="grey")

        self._plot_regions(fontdict=fontdict)
        # self._plot_ramps()
        # some maps has no vision blockers
        if len(self._vision_blockers) > 0:
            self._plot_vision_blockers()

        self._plot_normal_resources()
        self._plot_chokes()

        fontsize = 25
        ax = plt.gca()
        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(fontsize)
            tick.label1.set_fontweight("bold")
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(fontsize)
            tick.label1.set_fontweight("bold")
        plt.grid()
        if save:
            map_name = self.bot.game_info.map_name
            plt.savefig(f"{map_name}.png")
            plt.close()
        else:  # pragma: no cover
            plt.show()

    def __repr__(self):
        return f"MapData<{self.bot.game_info.map_name}> for bot {self.bot}"
