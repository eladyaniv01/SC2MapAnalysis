from functools import lru_cache
from typing import Dict, List, Optional, Set, Tuple, Union

import numpy as np
from numpy import float64, int64, ndarray
from sc2.bot_ai import BotAI
from sc2.position import Point2
from scipy.ndimage import binary_fill_holes, center_of_mass, generate_binary_structure, label as ndlabel
from scipy.spatial import distance

from MapAnalyzer.constructs import MDRamp, VisionBlockerArea
from MapAnalyzer.Debugger import MapAnalyzerDebugger
from MapAnalyzer.Pather import MapAnalyzerPather
from MapAnalyzer.Region import Region
from MapAnalyzer.utils import get_sets_with_mutual_elements
from .constants import BINARY_STRUCTURE, MAX_REGION_AREA, MIN_REGION_AREA
from .constructs import ChokeArea, PathLibChoke
from .decorators import progress_wrapped
from .exceptions import CustomDeprecationWarning

WHITE = "\u001b[32m"


class MapData:
    """
    MapData DocString
    """

    # todo goldenwall big region is not found
    def __init__(self, bot: BotAI, loglevel: str = "ERROR") -> None:
        # store relevant data from api
        self.bot = bot
        self.map_name: str = bot.game_info.map_name
        self.placement_arr: ndarray = bot.game_info.placement_grid.data_numpy
        self.path_arr: ndarray = bot.game_info.pathing_grid.data_numpy
        self.mineral_fields = bot.mineral_field
        self.normal_geysers = bot.vespene_geyser
        self.terrain_height: ndarray = bot.game_info.terrain_height.data_numpy
        self._vision_blockers: Set[Point2] = bot.game_info.vision_blockers
        self.base_locations: list = bot.expansion_locations_list

        # data that will be generated and cached
        self.min_region_area = MIN_REGION_AREA
        self.max_region_area = MAX_REGION_AREA
        self.regions: dict = {}  # set later
        self.region_grid: Union[ndarray, None] = None
        self.corners: list = []  # set later
        self.polygons: list = []  # set later
        self.map_chokes: list = []  # set later  on compile
        self.map_ramps: list = []  # set later  on compile
        self.map_vision_blockers: list = []  # set later  on compile
        self.vision_blockers_labels: list = []  # set later  on compile
        self.vision_blockers_grid: list = []  # set later  on compile
        self.resource_blockers = [Point2((m.position[0], m.position[1])) for m in self.bot.all_units if
                                  any(x in m.name.lower() for x in {"rich", "450"})]
        # self.resource_blockers = [Point2((m.position[1], m.position[0])) for m in self.bot.all_units]
        # self.resource_blockers.extend(self.bot.vespene_geyser) # breaks the label function for some reason on goldenwall
        self.pathlib_to_local_chokes = None
        self.overlapping_choke_ids = None

        # plugins
        self.log_level = loglevel
        self.debugger = MapAnalyzerDebugger(self, loglevel=self.log_level)
        self.logger = self.debugger.logger
        self.pather = MapAnalyzerPather(self)
        self.pathlib_map = self.pather.pathlib_map
        self.pyastar = self.pather.pyastar
        self.nonpathable_indices_stacked = self.pather.nonpathable_indices_stacked

        # compile
        self.logger.info(f"Compiling {self.map_name} " + WHITE)
        self.compile_map()  # this is called on init, but allowed to be called again every step

    """Properties"""

    @property
    def vision_blockers(self) -> Set[Point2]:
        """
        Return the private method
        """
        return self._vision_blockers

    """ Pathing methods"""

    # dont cache this
    def get_pyastar_grid(self, default_weight: int = 1, include_destructables: bool = True,
                         air_pathing: bool = False) -> ndarray:
        return self.pather.get_pyastar_grid(default_weight=default_weight, include_destructables=include_destructables,
                                            air_pathing=air_pathing)

    def get_climber_grid(self, default_weight: int = 1):
        return self.pather.get_climber_grid(default_weight)

    def pathfind(self, start: Tuple[int, int], goal: Tuple[int, int], grid: Optional[ndarray] = None,
                 allow_diagonal: bool = False, sensitivity: int = 1) -> ndarray:
        return self.pather.pathfind(start=start, goal=goal, grid=grid, allow_diagonal=allow_diagonal,
                                    sensitivity=sensitivity)

    def add_influence(self, p: Tuple[int, int], r: int, arr: ndarray, weight: int = 100, safe: bool = True) -> ndarray:
        """when safe is off will not adjust values below 1 which could result in a crash"""
        return self.pather.add_influence(p=p, r=r, arr=arr, weight=weight, safe=safe)

    """Utility methods"""

    def log(self, msg):
        self.logger.debug(f"{msg}")

    def save(self, filename):
        """"""
        self.debugger.save(filename=filename)

    def show(self):
        """"""
        self.debugger.show()

    def close(self):
        """"""
        self.debugger.close()

    def save_plot(self) -> None:
        """
        Will save the plot to a file names after the map name
        """
        self.plot_map()
        self.debugger.save(filename=f"{self.map_name}")

    @lru_cache()
    def ramp_close_enough(self, ramp, p, n=8):
        if self.distance(p, ramp.bottom_center) < n or self.distance(p, ramp.top_center) < n:
            return True
        return False

    @lru_cache()
    def get_ramp_nodes(self):
        return [ramp.center for ramp in self.map_ramps]

    @lru_cache(200)
    def get_ramp(self, node):
        return [r for r in self.map_ramps if r.center == node][0]

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

    """Query methods"""

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

    """ longest map compile is 1.9 s """
    """Compile methods"""

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

    @staticmethod
    def _get_overlapping_chokes(local_chokes: List[PathLibChoke],
                                areas: Union[List[MDRamp], List[Union[MDRamp, VisionBlockerArea]]]) -> Set[int]:
        li = []
        for area in areas:
            li.append(get_sets_with_mutual_elements(list_mdchokes=local_chokes, area=area))
        result = []
        for minili in li:
            result.extend(minili)
        return set(result)

    def _clean_polys(self) -> None:
        for pol in self.polygons:

            if pol.area > self.max_region_area:
                self.polygons.pop(self.polygons.index(pol))
            if pol.is_choke:

                for a in pol.areas:

                    if isinstance(a, MDRamp):
                        self.polygons.pop(self.polygons.index(pol))

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
        for point in self.resource_blockers:
            grid[int(point[0])][int(point[1])] = 0
            if point not in self.resource_blockers:
                correct_blockers.append(point)

        # for resource_point2 in self.resource_blockers:
        #     for n in resource_point2.neighbors4:
        #         point = Point2((n.rounded[0], n.rounded[1]))
        #         if point[0] < grid.shape[0] and point[1] < grid.shape[1]:
        #             grid[point[1]][point[0]] = 0
        #             if point not in self.resource_blockers:
        #                 correct_blockers.append(point)
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

    def _set_map_ramps(self):
        self.map_ramps = [MDRamp(map_data=self,
                                 ramp=r,
                                 array=self.points_to_numpy_array(r.points))
                          for r in self.bot.game_info.map_ramps]

    def _calc_ramps(self, region: Region) -> None:
        """
        probably the most expensive operation other than plotting ,  need to optimize
        """
        if len(self.map_ramps) == 0:
            self._set_map_ramps()

        ramp_nodes = self.get_ramp_nodes()
        perimeter_nodes = region.polygon.perimeter_points
        result_ramp_indexes = list(set([self.closest_node_idx(n, ramp_nodes) for n in perimeter_nodes]))

        for rn in result_ramp_indexes:
            # and distance from perimeter is less than ?
            ramp = self.get_ramp(node=ramp_nodes[rn])

            """for ramp in map ramps  if ramp exists,  append the regions if not,  create new one"""
            if region not in ramp.areas:
                ramp.areas.append(region)
            region.region_ramps.append(ramp)
        ramps = []

        for ramp in region.region_ramps:
            for p in region.polygon.perimeter_points:
                if self.ramp_close_enough(ramp, p, n=8):
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

    """Plot methods"""

    def plot_map(
            self, fontdict: dict = None, save=None, figsize: int = 20
    ) -> None:
        """
        Plot map
        """
        if save is not None:
            self.logger.warning(CustomDeprecationWarning(oldarg='save', newarg='self.save()'))
        self.debugger.plot_map(fontdict=fontdict, figsize=figsize)

    def plot_influenced_path(self, start: Tuple[int64, int64], goal: Tuple[int64, int64], weight_array: ndarray,
                             plot=None, save=None, name: Optional[str] = None,
                             fontdict: dict = None) -> None:
        if save is not None:
            self.logger.warning(CustomDeprecationWarning(oldarg='save', newarg='self.save()'))
        if plot is not None:
            self.logger.warning(CustomDeprecationWarning(oldarg='plot', newarg='self.show()'))

        self.debugger.plot_influenced_path(start=start, goal=goal, weight_array=weight_array, name=name,
                                           fontdict=fontdict)

    def _plot_regions(self, fontdict: Dict[str, Union[str, int]]) -> None:
        """
        plot Region
        """
        return self.debugger.plot_regions(fontdict=fontdict)

    def _plot_vision_blockers(self) -> None:
        """
        plot vbs
        """
        self.debugger.plot_vision_blockers()

    def _plot_normal_resources(self) -> None:
        """
        # todo: account for gold minerals and rich gas
        """
        self.debugger.plot_normal_resources()

    def _plot_chokes(self) -> None:
        """
        compute Chokes
        """
        self.debugger.plot_chokes()

    def __repr__(self) -> str:
        return f"<MapData[{self.bot.game_info.map_name}][{self.bot}]>"
