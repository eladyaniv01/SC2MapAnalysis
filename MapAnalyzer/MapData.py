import inspect
import os
import sys
import warnings
from functools import lru_cache
# from multiprocessing.dummy import Pool
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pyastar.astar_wrapper as pyastar
from loguru import logger
from numpy import float64, int64, ndarray
from numpy.core._multiarray_umath import ndarray
from sc2.bot_ai import BotAI
from sc2.position import Point2
from scipy.ndimage import binary_fill_holes, center_of_mass, generate_binary_structure, label as ndlabel
from scipy.spatial import distance
from skimage import draw as skdraw

from MapAnalyzer.constructs import MDRamp, VisionBlockerArea
from MapAnalyzer.Region import Region
from .constants import BINARY_STRUCTURE, COLORS, LOG_FORMAT, MAX_REGION_AREA, MIN_REGION_AREA
from .constructs import ChokeArea, PathLibChoke
from .decorators import progress_wrapped
from .exceptions import OutOfBoundsException
from .sc2pathlibp import Sc2Map

WHITE = "\u001b[32m"


class LogFilter:
    def __init__(self, level: str) -> None:
        self.level = level

    def __call__(self, record: Dict[str, Any]) -> bool:
        levelno = logger.level(self.level).no
        return record["level"].no >= levelno


class MapData:
    """
    MapData DocString
    """

    def __init__(self, bot: BotAI, loglevel: str = "ERROR") -> None:
        self.warnings = warnings
        self.warnings.filterwarnings('ignore', category=DeprecationWarning)
        self.warnings.filterwarnings('ignore', category=RuntimeWarning)
        self.logger = logger
        self.log_filter = LogFilter(loglevel)
        self.logger.remove()
        self.log_format = LOG_FORMAT
        self.logger.add(sys.stderr, format=self.log_format, filter=self.log_filter)
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
        self.map_ramps: list = []  # set later  on compile
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
        self.resource_blockers = [Point2(m.position) for m in self.mineral_fields if "450" in m.name]
        # self.resource_blockers.extend(self.bot.vespene_geyser) # breaks the label function for some reason on goldenwall
        self.normal_geysers = bot.vespene_geyser
        self.pathlib_map = None
        self.pathlib_to_local_chokes = None
        self.overlapping_choke_ids = None
        self._set_pathlib_map()
        self.pyastar = pyastar
        self.logger.info(f"Compiling {self.map_name} " + WHITE)
        self.compile_map()  # this is called on init, but allowed to be called again every step

    @lru_cache()
    def _get_base_pathing_grid(self):
        return np.fmax(self.path_arr, self.placement_arr).T

    # dont cache this
    def get_pyastar_grid(self, default_weight: int = 1, destructables: bool = True, fly: bool = False) -> ndarray:
        if fly:
            return np.ones(shape=self.path_arr.shape)

        grid = self._get_base_pathing_grid()
        grid = np.where(grid != 0, default_weight, np.inf).astype(np.float32)
        # todo need to iterate and add radius + test  for path through mineral fields
        nonpathables = self.bot.structures.extend(self.bot.enemy_structures).extend(self.mineral_fields)
        for obj in nonpathables:
            self.add_influence(p=obj.position, r=0.8 * obj.radius, arr=grid, weight=np.inf)

        if destructables:
            destructables_filtered = [d for d in self.bot.destructables if "plates" not in d.name.lower()]
            # nonpathables.extend(destructables_filtered)
            for rock in destructables_filtered:
                if "plates" not in rock.name.lower():
                    self.add_influence(p=rock.position, r=0.8 * rock.radius, arr=grid, weight=np.inf)
        return grid

    def pathfind(self, start: Tuple[int, int], goal: Tuple[int, int], grid: Optional[ndarray] = None,
                 allow_diagonal: bool = False, sensitivity: int = 1) -> ndarray:
        start = int(start[0]), int(start[1])
        goal = int(goal[0]), int(goal[1])
        if grid is None:
            grid = self.get_pyastar_grid()

        path = pyastar.astar_path(grid, start=start, goal=goal, allow_diagonal=allow_diagonal)
        if path is not None:
            return list(map(Point2, path))[::sensitivity]
        else:
            self.logger.debug(f"No Path found s{start}, g{goal}")
            return None

    def log(self, msg):
        self.logger.debug(f"{msg}")

    def add_influence(self, p: Tuple[int, int], r: int, arr: ndarray, weight: int = 100, safe: bool = True) -> ndarray:
        ri, ci = skdraw.disk(center=(int(p[0]), int(p[1])), radius=r, shape=arr.shape)
        if len(ri) == 0 or len(ci) == 0:
            # this happens when the center point is near map edge, and the radius added goes beyond the edge
            self.logger.debug(OutOfBoundsException(p))
            return arr

        def in_bounds_ci(x):
            width = arr.shape[0] - 1
            if 0 < x < width:
                return x
            return 0

        def in_bounds_ri(y):
            height = arr.shape[1] - 1
            if 0 < y < height:
                return y
            return 0

        ci_vec = np.vectorize(in_bounds_ci)
        ri_vec = np.vectorize(in_bounds_ri)
        ci = ci_vec(ci)
        ri = ri_vec(ri)
        arr[ri, ci] += weight
        if np.any(arr < 1) and safe:
            self.logger.warning("You are attempting to set weights that are below 1. falling back to the minimum (1)")
            arr = np.where(arr < 1, 1, arr)
        return arr

    def _clean_plib_chokes(self) -> None:
        # needs to be called AFTER MDramp and VisionBlocker are populated
        raw_chokes = self.pathlib_map.chokes
        self.pathlib_to_local_chokes = []
        for i, c in enumerate(raw_chokes):
            self.pathlib_to_local_chokes.append(PathLibChoke(pathlib_choke=c, pk=i))
        areas = self.map_ramps.copy()
        areas.extend(self.map_vision_blockers)
        self.overlapping_choke_ids = self._get_overlapping_chokes(local_chokes=self.pathlib_to_local_chokes,
                                                                  areas=areas)

    def _get_overlapping_chokes(self, local_chokes: List[PathLibChoke],
                                areas: Union[List[MDRamp], List[Union[MDRamp, VisionBlockerArea]]]) -> Set[int]:
        li = []
        for area in areas:
            li.append(self._get_sets_with_mutual_elements(list_mdchokes=local_chokes, area=area))
        result = []
        for minili in li:
            result.extend(minili)
        return set(result)

    @staticmethod
    def _get_sets_with_mutual_elements(list_mdchokes: List[PathLibChoke],
                                       area: Optional[Union[MDRamp, VisionBlockerArea]] = None,
                                       base_choke: None = None) -> List[List]:
        li = []
        if area:
            s1 = area.points
        else:
            s1 = base_choke.pixels
        for c in list_mdchokes:
            s2 = c.pixels
            s3 = s1 ^ s2
            if len(s3) != (len(s1) + len(s2)):
                li.append(c.id)
        return li

    def _clean_polys(self) -> None:
        for pol in self.polygons:

            if pol.area > self.max_region_area:
                self.polygons.pop(self.polygons.index(pol))
            if pol.is_choke:

                for a in pol.areas:

                    if isinstance(a, MDRamp):
                        self.polygons.pop(self.polygons.index(pol))

    """ longest map compile is 1.9 s """

    # disabling until tqdm is available on aiarena
    @progress_wrapped(estimated_time=0, desc="\u001b[32m Map Compilation Progress \u001b[37m")
    def compile_map(self) -> None:
        """user can call this to recompute"""

        self._calc_grid()
        self._calc_regions()
        self._calc_vision_blockers()
        self._calc_chokes()
        self._clean_polys()
        for poly in self.polygons:
            poly.calc_areas()

    @property
    def vision_blockers(self) -> Set[Point2]:
        """
        Return the private method
        """
        return self._vision_blockers

    def _set_pathlib_map(self) -> None:

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
        for choke in self.map_chokes:
            if choke.is_inside_point(point):
                results.append(choke)
        # assert (len(list(set(results))) == len(results)), f"results{results},  list(set(results)){list(set(results))}"
        return results

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
        for choke in self.map_chokes:
            if choke.is_inside_point(point):
                return choke

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

        # for our grid,  mineral walls are considered as a barrier between regions
        # GOLDENWALL FIXED 18e7943cbac300afd686b4ceec40821a93692875r
        correct_blockers = []
        for resource_point2 in self.resource_blockers:
            for n in resource_point2.neighbors4:
                point = Point2((n.rounded[1], n.rounded[0]))
                if point[0] < grid.shape[0] and point[1] < grid.shape[1]:
                    grid[point[0]][point[1]] = 2
                    if point not in self.resource_blockers:
                        correct_blockers.append(point)
        correct_blockers = list(set(correct_blockers))
        self.resource_blockers.extend(correct_blockers)

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

    def _calc_ramps(self, region: Region) -> None:
        """
        probably the most expensive operation other than plotting ,  need to optimize
        """

        @lru_cache()
        def ramp_close_enough(ramp, p, n=8):
            return self.distance(p, ramp.bottom_center) < n or self.distance(p, ramp.top_center) < n

        @lru_cache()
        def get_ramp_nodes():
            return [ramp.center for ramp in self.map_ramps]

        @lru_cache(200)
        def get_ramp(node):
            return [r for r in self.map_ramps if r.center == node][0]

        if len(self.map_ramps) == 0:
            self.map_ramps = [MDRamp(map_data=self,
                                     ramp=r,
                                     array=self.points_to_numpy_array(r.points))
                              for r in self.bot.game_info.map_ramps]

        ramp_nodes = get_ramp_nodes()
        perimeter_nodes = region.polygon.perimeter_points
        result_ramp_indexes = list(set([self.closest_node_idx(n, ramp_nodes) for n in perimeter_nodes]))

        for rn in result_ramp_indexes:
            # and distance from perimeter is less than ?
            ramp = get_ramp(node=ramp_nodes[rn])

            """for ramp in map ramps  if ramp exists,  append the regions if not,  create new one"""
            if region not in ramp.areas:
                ramp.areas.append(region)
            region.region_ramps.append(ramp)
        ramps = []

        for ramp in region.region_ramps:
            for p in region.polygon.perimeter_points:
                if ramp_close_enough(ramp, p, n=8):
                    ramps.append(ramp)
        ramps = list(set(ramps))

        region.region_ramps.extend(ramps)
        region.region_ramps = list(set(region.region_ramps))
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
        self._clean_plib_chokes()
        chokes = [c for c in self.pathlib_to_local_chokes if c.id not in self.overlapping_choke_ids]
        self.map_chokes = self.map_ramps.copy()
        self.map_chokes.extend(self.map_vision_blockers)

        for choke in chokes:

            points = [Point2(p) for p in choke.pixels]
            if len(points) > 0:
                new_choke_array = self.points_to_numpy_array(points)
                cm = center_of_mass(new_choke_array)
                cm = int(cm[0]), int(cm[1])
                areas = self.where_all(cm)

                new_choke = ChokeArea(
                        map_data=self, array=new_choke_array, pathlibchoke=choke
                )
                for area in areas:

                    if isinstance(area, Region):
                        area.region_chokes.append(new_choke)
                    new_choke.areas.append(area)
                self.map_chokes.append(new_choke)
            else:  # pragma: no cover
                self.logger.debug(f" [{self.map_name}] Cant add {choke} with 0 points")

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

    def _plot_vision_blockers(self) -> None:
        """
        compute vbs
        """
        import matplotlib.pyplot as plt

        for vb in self._vision_blockers:
            plt.text(vb[0], vb[1], "X")

        x, y = zip(*self._vision_blockers)
        plt.scatter(x, y, color="r")

    def _plot_normal_resources(self) -> None:
        """
        # todo: account for gold minerals and rich gas
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
        compute Chokes
        """
        import matplotlib.pyplot as plt
        for choke in self.map_chokes:
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
            self, fontdict: dict = None, save: bool = False, figsize: int = 20
    ) -> None:
        """
        Plot map
        """

        if not fontdict:
            fontdict = {"family": "serif", "weight": "bold", "size": 25}
        import matplotlib.pyplot as plt
        plt.figure(figsize=(figsize, figsize))
        self._plot_regions(fontdict=fontdict)
        # some maps has no vision blockers
        if len(self._vision_blockers) > 0:
            self._plot_vision_blockers()
        self._plot_normal_resources()
        self._plot_chokes()
        fontsize = 25

        plt.style.use("ggplot")
        plt.imshow(self.region_grid, origin="lower")
        plt.imshow(self.terrain_height, alpha=1, origin="lower", cmap="terrain")
        x, y = zip(*self.nonpathable_indices_stacked)
        plt.scatter(x, y, color="grey")
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
            if 'test' in str(inspect.stack()[2][1]):
                logger.debug("Skipping saving map image")
                return True
            else:
                full_path = os.path.join(os.path.abspath("."), f"{self.map_name}.png")
                plt.savefig(f"{map_name}.png")
                logger.debug(f"Plot Saved to {full_path}")
                plt.close()
        else:  # pragma: no cover
            plt.show()

    def plot_influenced_path(self, start: Tuple[int64, int64], goal: Tuple[int64, int64], weight_array: ndarray,
                             plot: bool = True, save: bool = False, name: Optional[str] = None,
                             fontdict: dict = None) -> None:
        import matplotlib.pyplot as plt
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        from matplotlib.cm import ScalarMappable
        if not fontdict:
            fontdict = {"family": "serif", "weight": "bold", "size": 20}
        plt.style.use(["ggplot", "bmh"])
        org = "lower"
        if name is None:
            name = self.map_name
        arr = weight_array.copy()
        path = self.pathfind(start, goal,
                             grid=arr,
                             sensitivity=1)
        p0_ = start[1], start[0]
        p1_ = goal[1], goal[0]
        # noinspection PyUnboundLocalVariable
        ax: plt.Axes = plt.subplot(1, 1, 1)
        if path is not None:
            path = np.flip(np.flipud(path))  # for plot align
            self.logger.info("Found")
            x, y = zip(*path)
            ax.scatter(x, y, s=3, c='green')
        else:
            self.logger.info("Not Found")

            x, y = zip(*[start, goal])
            ax.scatter(x, y)

        influence_cmap = plt.cm.get_cmap("afmhot")
        ax.text(p0_[0], p0_[1], f"Start {p0_}")
        ax.text(p1_[0], p1_[1], f"End {p1_}")
        ax.imshow(self.path_arr.T, alpha=0.5, origin=org)
        ax.imshow(self.terrain_height.T, alpha=0.5, origin=org, cmap='bone')
        arr = np.where(arr == np.inf, 0, arr)
        ax.imshow(arr, origin=org, alpha=0.3, cmap=influence_cmap)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        sc = ScalarMappable(cmap=influence_cmap)
        sc.set_array(arr)
        sc.autoscale()
        cbar = plt.colorbar(sc, cax=cax)
        cbar.ax.set_ylabel('Pathing Cost', rotation=270, labelpad=25, fontdict=fontdict)
        # pts = self.indices_to_points(np.where(arr == arr.max()))
        # x, y = zip(*pts)
        # if len(pts) > 3:
        #     alpha = 0.0001
        #     size = 50
        # else:
        #     size = 75
        #     alpha = 0.08
        # ax.scatter(y, x, c="red",marker="v", s=size, alpha=alpha)
        plt.title(f"{name}", fontdict=fontdict, loc='right')
        plt.grid()
        if plot:
            plt.show()
        if save:
            plt.savefig(f"MA_INF_{name}.png")
            plt.close()

    def __repr__(self) -> str:
        return f"<MapData[{self.bot.game_info.map_name}][{self.bot}]>"
