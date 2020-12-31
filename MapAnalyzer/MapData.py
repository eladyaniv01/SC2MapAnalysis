import math
from functools import lru_cache
from typing import Dict, List, Optional, Set, Tuple, Union

import numpy as np
from loguru import logger
from numpy import float64, int64, ndarray
from pkg_resources import DistributionNotFound, get_distribution
from sc2.bot_ai import BotAI
from sc2.position import Point2
from scipy.ndimage import binary_fill_holes, center_of_mass, generate_binary_structure, label as ndlabel
from scipy.spatial import distance

from MapAnalyzer.Debugger import MapAnalyzerDebugger
from MapAnalyzer.Pather import MapAnalyzerPather
from MapAnalyzer.Region import Region
from MapAnalyzer.utils import get_sets_with_mutual_elements, fix_map_ramps

from .constants import BINARY_STRUCTURE, CORNER_MIN_DISTANCE, MAX_REGION_AREA, MIN_REGION_AREA

from .decorators import progress_wrapped
from .exceptions import CustomDeprecationWarning
from MapAnalyzer.constructs import ChokeArea, MDRamp, VisionBlockerArea, RawChoke
from .cext import CMapInfo, CMapChoke

try:
    __version__ = get_distribution('sc2mapanalyzer')
except DistributionNotFound:
    __version__ = 'dev'

WHITE = "\u001b[32m"


class MapData:
    """

    Entry point for the user

    """

    def __init__(self, bot: BotAI, loglevel: str = "ERROR", arcade: bool = False,
                 corner_distance: int = CORNER_MIN_DISTANCE) -> None:
        # store relevant data from api
        self.bot = bot
        # temporary fix to set ramps correctly if they are broken in burnysc2 due to having
        # destructables on them. ramp sides don't consider the destructables now,
        # should update them during the game
        self.bot.game_info.map_ramps, self.bot.game_info.vision_blockers = fix_map_ramps(self.bot)

        self.corner_distance = corner_distance  # the lower this value is,  the sharper the corners will be
        self.arcade = arcade
        self.version = __version__
        self.map_name: str = bot.game_info.map_name
        self.placement_arr: ndarray = bot.game_info.placement_grid.data_numpy
        self.path_arr: ndarray = bot.game_info.pathing_grid.data_numpy
        self.mineral_fields = bot.mineral_field
        self.normal_geysers = bot.vespene_geyser
        self.terrain_height: ndarray = bot.game_info.terrain_height.data_numpy
        self._vision_blockers: Set[Point2] = bot.game_info.vision_blockers

        # data that will be generated and cached
        self.min_region_area = MIN_REGION_AREA
        self.max_region_area = MAX_REGION_AREA
        self.regions: dict = {}  # set later
        self.region_grid: Optional[ndarray] = None
        self.corners: list = []  # set later
        self.polygons: list = []  # set later
        self.map_chokes: list = []  # set later  on compile
        self.map_ramps: list = []  # set later  on compile
        self.map_vision_blockers: list = []  # set later  on compile
        self.vision_blockers_labels: list = []  # set later  on compile
        self.vision_blockers_grid: list = []  # set later  on compile
        self.overlord_spots: list = []
        self.resource_blockers = [Point2((m.position[0], m.position[1])) for m in self.bot.all_units if
                                  any(x in m.name.lower() for x in {"rich", "450"})]
        self.overlapping_choke_ids = None

        pathing_grid = np.fmax(self.path_arr, self.placement_arr)
        self.c_ext_map = CMapInfo(pathing_grid.T, self.terrain_height.T, self.bot.game_info.playable_area)
        self.overlord_spots = self.c_ext_map.overlord_spots

        # plugins
        self.log_level = loglevel
        self.debugger = MapAnalyzerDebugger(self, loglevel=self.log_level)
        self.pather = MapAnalyzerPather(self)

        self.connectivity_graph = None  # set by pather
        self.pyastar = self.pather.pyastar
        self.nonpathable_indices_stacked = self.pather.nonpathable_indices_stacked

        # compile
        if not self.arcade:
            self.base_locations: list = bot.expansion_locations_list
        else:
            logger.info(f" {__version__} Starting in Arcade mode")
            self.base_locations: list = []

        logger.info(f"{__version__} Compiling {self.map_name} " + WHITE)
        self._compile_map()

    """Properties"""

    @property
    def vision_blockers(self) -> Set[Point2]:
        """
        Exposing the computed method

            ``vision_blockers`` are not to be confused with :data:`self.map_vision_blockers`
            ``vision_blockers`` are the raw data received from ``burnysc2`` and will be processed later on.

        """
        return self._vision_blockers

    """ Pathing methods"""

    # dont cache this
    def get_pyastar_grid(self,
                         default_weight: float = 1,
                         include_destructables: bool = True) -> ndarray:
        """
        :rtype: numpy.ndarray
        Note:
            To query what is the cost in a certain point, simple do ``my_grid[certain_point]`` where `certain_point`

            is a :class:`tuple` or a :class:`sc2.position.Point2`


        Requests a new pathing grid.

        This grid will have all non pathable cells set to :class:`numpy.inf`.

        pathable cells will be set to the ``default_weight`` which it's default is ``1``.

        After you get the grid, you can add your own ``cost`` (also known as ``weight`` or ``influence``)

        This grid can, and **should** be reused in the duration of the frame,
        and should be regenerated(**once**) on each frame.

        Note:
            destructables that has been destroyed will be updated by default,

            the only known use case for ``include_destructables`` usage is illustrated in the first example below

        Example:
            We want to check if breaking the destructables in our path will make it better,

            so we treat destructables as if they were pathable

            >>> # 1
            >>> no_destructables_grid = self.get_pyastar_grid(default_weight = 1, include_destructables= False)

            >>> # 2 set up a grid with default weight of 300
            >>> custom_weight_grid = self.get_pyastar_grid(default_weight = 300)

        See Also:
            * :meth:`.MapData.get_climber_grid`
            * :meth:`.MapData.get_air_vs_ground_grid`
            * :meth:`.MapData.get_clean_air_grid`
            * :meth:`.MapData.add_cost`
            * :meth:`.MapData.pathfind`
            * :meth:`.MapData.find_lowest_cost_points`

        """
        return self.pather.get_pyastar_grid(default_weight=default_weight,
                                            include_destructables=include_destructables,
                                            )

    def find_lowest_cost_points(self, from_pos: Point2, radius: float, grid: np.ndarray) -> List[Point2]:
        """
        :rtype:  Union[List[:class:`sc2.position.Point2`], None]

        Given an origin point and a radius,  will return a list containing the lowest cost points
        (if there are more than one)

        Example:
             >>> my_grid = self.get_air_vs_ground_grid()
             >>> position = (100, 80)
             >>> my_radius = 10
             >>> self.find_lowest_cost_points(from_pos=position, radius=my_radius, grid=my_grid)
             [(105, 77), (108, 79), (107, 81), (91, 79), (106, 80),
             (108, 83), (106, 78), (107, 84), (109, 82), (107, 79),
             (107, 80), (106, 75), (107, 75), (91, 78), (106, 81),
             (109, 77), (108, 76), (91, 80), (106, 79), (109, 81),
             (107, 78), (108, 80), (105, 82), (107, 83), (107, 74),
             (108, 84), (102, 71), (109, 76), (105, 79), (108, 77),
             (106, 76), (107, 86), (106, 82), (109, 80), (108, 81),
             (105, 81), (107, 82), (109, 84), (106, 73), (107, 77),
             (108, 85), (105, 78), (108, 78), (106, 77), (107, 73),
             (106, 83), (108, 82), (105, 80), (108, 75), (107, 85),
             (109, 83), (107, 76)]

        See Also:
            * :meth:`.MapData.get_pyastar_grid`
            * :meth:`.MapData.get_climber_grid`
            * :meth:`.MapData.get_air_vs_ground_grid`
            * :meth:`.MapData.get_clean_air_grid`
            * :meth:`.MapData.add_cost`
            * :meth:`.MapData.pathfind`

        """
        return self.pather.find_lowest_cost_points(from_pos=from_pos, radius=radius, grid=grid)

    def lowest_cost_points_np(self, from_pos: Point2, radius: float, grid: np.ndarray) -> ndarray:
        """
        :rtype:    Union[:class:`numpy.ndarray`, None]

        Same as find_lowest_cost_points, but returns points in ndarray for use
        with methods such as .closest_towards_point
        """
        return self.pather.lowest_cost_points_np(from_pos=from_pos, radius=radius, grid=grid)

    def get_climber_grid(self, default_weight: float = 1, include_destructables: bool = True) -> ndarray:
        """
        :rtype: numpy.ndarray
        Climber grid is a grid modified by the c extension, and is used for units that can climb,

        such as Reaper, Colossus

        This grid can be reused in the duration of the frame,

        and should be regenerated(once) on each frame.

        This grid also gets updated with all nonpathables when requested

        such as structures, and destructables

        Example:
                >>> updated_climber_grid = self.get_climber_grid(default_weight = 1)

        See Also:
            * :meth:`.MapData.get_pyastar_grid`
            * :meth:`.MapData.get_air_vs_ground_grid`
            * :meth:`.MapData.get_clean_air_grid`
            * :meth:`.MapData.add_cost`
            * :meth:`.MapData.pathfind`
            * :meth:`.MapData.find_lowest_cost_points`
        """
        return self.pather.get_climber_grid(default_weight, include_destructables=include_destructables)

    def get_air_vs_ground_grid(self, default_weight: float = 100) -> ndarray:
        """
        :rtype: numpy.ndarray
        ``air_vs_ground`` grid is computed in a way that lowers the cost of nonpathable terrain,

         making air units naturally "drawn" to it.

        Caution:
            Requesting a grid with a ``default_weight`` of 1 is pointless,

            and  will result in a :meth:`.MapData.get_clean_air_grid`

        Example:
                >>> air_vs_ground_grid = self.get_air_vs_ground_grid()

        See Also:
            * :meth:`.MapData.get_pyastar_grid`
            * :meth:`.MapData.get_climber_grid`
            * :meth:`.MapData.get_clean_air_grid`
            * :meth:`.MapData.add_cost`
            * :meth:`.MapData.pathfind`
            * :meth:`.MapData.find_lowest_cost_points`

        """
        return self.pather.get_air_vs_ground_grid(default_weight=default_weight)

    def get_clean_air_grid(self, default_weight: float = 1) -> ndarray:
        """

        :rtype: numpy.ndarray

        Will return a grid marking every cell as pathable with ``default_weight``

        See Also:
            * :meth:`.MapData.get_air_vs_ground_grid`

        """
        return self.pather.get_clean_air_grid(default_weight=default_weight)

    def pathfind_pyastar(self, start: Union[Tuple[float, float], Point2], goal: Union[Tuple[float, float], Point2],
                         grid: Optional[ndarray] = None,
                         allow_diagonal: bool = False, sensitivity: int = 1) -> Optional[List[Point2]]:

        """
        :rtype: Union[List[:class:`sc2.position.Point2`], None]
        Will return the path with lowest cost (sum) given a weighted array (``grid``), ``start`` , and ``goal``.


        **IF NO** ``grid`` **has been provided**, will request a fresh grid from :class:`.Pather`

        If no path is possible, will return ``None``

        Tip:
            ``sensitivity`` indicates how to slice the path,
            just like doing: ``result_path = path[::sensitivity]``
                where ``path`` is the return value from this function

            this is useful since in most use cases you wouldn't want
            to get each and every single point,

            getting every  n-``th`` point works better in practice


        Caution:
            ``allow_diagonal=True`` will result in a slight performance penalty.

            `However`, if you don't over-use it, it will naturally generate shorter paths,

            by converting(for example) ``move_right + move_up`` into ``move_top_right`` etc.

        TODO:
            more examples for different usages available

        Example:
            >>> my_grid = self.get_pyastar_grid()
            >>> # start / goal could be any tuple / Point2
            >>> path = self.pathfind(start=start,goal=goal,grid=my_grid,allow_diagonal=True, sensitivity=3)

        See Also:
            * :meth:`.MapData.get_pyastar_grid`
            * :meth:`.MapData.find_lowest_cost_points`

        """
        return self.pather.pathfind_pyastar(start=start, goal=goal, grid=grid, allow_diagonal=allow_diagonal,
                                            sensitivity=sensitivity)

    def pathfind(self, start: Union[Tuple[float, float], Point2], goal: Union[Tuple[float, float], Point2],
                 grid: Optional[ndarray] = None, smoothing: bool = False,
                 sensitivity: int = 1) -> Optional[List[Point2]]:
        """
        :rtype: Union[List[:class:`sc2.position.Point2`], None]
        Will return the path with lowest cost (sum) given a weighted array (``grid``), ``start`` , and ``goal``.


        **IF NO** ``grid`` **has been provided**, will request a fresh grid from :class:`.Pather`

        If no path is possible, will return ``None``

        ``sensitivity`` indicates how to slice the path,
        just like doing: ``result_path = path[::sensitivity]``
            where ``path`` is the return value from this function

        this is useful since in most use cases you wouldn't want
        to get each and every single point,

        getting every  n-``th`` point works better in practice

        ``smoothing`` tries to do a similar thing on the c side but to the maximum extent possible.
        it will skip all the waypoints it can if taking the straight line forward is better
        according to the influence grid

        Example:
            >>> my_grid = self.get_pyastar_grid()
            >>> # start / goal could be any tuple / Point2
            >>> path = self.pathfind(start=start,goal=goal,grid=my_grid,allow_diagonal=True, sensitivity=3)

        See Also:
            * :meth:`.MapData.get_pyastar_grid`
            * :meth:`.MapData.find_lowest_cost_points`

        """
        return self.pather.pathfind(start=start, goal=goal, grid=grid, smoothing=smoothing,
                                    sensitivity=sensitivity)

    def add_cost(self, position: Tuple[float, float], radius: float, grid: ndarray, weight: float = 100, safe: bool = True,
                 initial_default_weights: float = 0) -> ndarray:
        """
        :rtype: numpy.ndarray

        Will add cost to a `circle-shaped` area with a center ``position`` and radius ``radius``

        weight of 100

        Warning:
            When ``safe=False`` the Pather will not adjust illegal values below 1 which could result in a crash`

        """
        return self.pather.add_cost(position=position, radius=radius, arr=grid, weight=weight, safe=safe,
                                    initial_default_weights=initial_default_weights)

    """Utility methods"""

    def save(self, filename):
        """

        Save Plot to a file, much like ``plt.save(filename)``

        """
        self.debugger.save(filename=filename)

    def show(self):
        """

        Calling debugger to show, just like ``plt.show()``  but in case there will be changes in debugger,

        This method will always be compatible

        """
        self.debugger.show()

    def close(self):
        """
        Close an opened plot, just like ``plt.close()``  but in case there will be changes in debugger,

        This method will always be compatible

        """
        self.debugger.close()

    @staticmethod
    def indices_to_points(
            indices: Union[ndarray, Tuple[ndarray, ndarray]]
    ) -> Set[Union[Tuple[float, float], Point2]]:
        """
        :rtype: :class:`.set` (Union[:class:`.tuple` (:class:`.int`, :class:`.int`), :class:`sc2.position.Point2`)

        Convert indices to a set of points(``tuples``, not ``Point2`` )

        Will only work when both dimensions are of same length

        """

        return set([(indices[0][i], indices[1][i]) for i in range(len(indices[0]))])

    @staticmethod
    def points_to_indices(points: Set[Tuple[float, float]]) -> Tuple[np.ndarray, np.ndarray]:
        """
        :rtype: Tuple[numpy.ndarray, numpy.ndarray]

        Convert a set / list of points to a tuple of two 1d numpy arrays

        """
        return np.array([p[0] for p in points]), np.array([p[1] for p in points])

    def points_to_numpy_array(
            self, points: Union[Set[Tuple[int64, int64]], List[Point2], Set[Point2]]
            , default_value: int = 1) -> ndarray:
        """
        :rtype: numpy.ndarray

        Convert points to numpy ndarray

        Caution:
                Will handle safely(by ignoring) points that are ``out of bounds``, without warning
        """
        rows, cols = self.path_arr.shape
        arr = np.zeros((rows, cols), dtype=np.uint8)
        if isinstance(points, set):
            points = list(points)

        def in_bounds_x(x_):
            width = arr.shape[0] - 1
            if 0 < x_ < width:
                return x_
            return 0

        def in_bounds_y(y_):
            height = arr.shape[1] - 1
            if 0 < y_ < height:
                return y_
            return 0

        x_vec = np.vectorize(in_bounds_x)
        y_vec = np.vectorize(in_bounds_y)
        indices = self.points_to_indices(points)
        x = x_vec(indices[0])
        y = y_vec(indices[1])
        arr[x, y] = default_value
        return arr

    @staticmethod
    def distance(p1: Point2, p2: Point2) -> float64:
        """
        :rtype: float64

        Euclidean distance

        """
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[0] - p1[0]) ** 2)

    @staticmethod
    def distance_squared(p1: Point2, p2: Point2) -> float64:
        """
        :rtype: float64

        Euclidean distance squared

        """
        return (p2[0] - p1[0]) ** 2 + (p2[0] - p1[0]) ** 2

    @staticmethod
    def closest_node_idx(
            node: Union[Point2, ndarray], nodes: ndarray
    ) -> int:
        """
        :rtype: int

        Given a list of ``nodes``  and a single ``node`` ,

        will return the index of the closest node in the list to ``node``

        """
        closest_index = distance.cdist([node], nodes).argmin()
        return closest_index

    def closest_towards_point(
            self, points: Union[List[Point2], ndarray], target: Union[Point2, tuple]
    ) -> Union[ndarray, Point2]:
        """
        :rtype: :class:`sc2.position.Point2`

        Given a list/set of points, and a target,

        will return the point that is closest to that target

        Example:
                Calculate a position for tanks in direction to the enemy forces
                passing in the Area's corners as points and enemy army's location as target

                >>> enemy_army_position = Point2((50,50)) # random point for this example
                >>> my_base_location = self.bot.townhalls[0]
                >>> my_region = self.where_all(my_base_location)[0]
                >>> corners = my_region.corner_points
                >>> best_siege_spot = self.closest_towards_point(points=corners, target=enemy_army_position)
                (57,120)
        """
        if isinstance(points[0], Point2):
            # Converting to ndarray is much slower
            return sorted(points,
                          key=lambda p: self.distance_squared(p, target))[0]

        if not isinstance(points, (list, ndarray)):
            logger.warning(type(points))

        return points[self.closest_node_idx(node=target, nodes=points)]

    """Query methods"""

    def region_connectivity_all_paths(self, start_region: Region, goal_region: Region,
                                      not_through: Optional[List[Region]] = None) -> List[List[Region]]:
        """
        :param start_region: :mod:`.Region`
        :param goal_region: :mod:`.Region`
        :param not_through: Optional[List[:mod:`.Region`]]
        :rtype: List[List[:mod:`.Region`]]

        Returns all possible paths through all :mod:`.Region` (via ramps),

        can exclude a region by passing it in a not_through list

        """
        all_paths = self.pather.find_all_paths(start=start_region, goal=goal_region)
        filtered_paths = all_paths.copy()
        if not_through is not None:
            for path in all_paths:
                if any([x in not_through for x in path]):
                    filtered_paths.remove(path)
            all_paths = filtered_paths
        return all_paths

    @lru_cache(200)
    def where_all(
            self, point: Union[Point2, tuple]
    ) -> List[Union[Region, ChokeArea, VisionBlockerArea, MDRamp]]:
        """
        :rtype: List[Union[:class:`.Region`, :class:`.ChokeArea`, :class:`.VisionBlockerArea`, :class:`.MDRamp`]]

        Will return a list containing all :class:`.Polygon` that occupy the given point.

        If a :class:`.Region` exists in that list, it will be the first item

        Caution:
                Not all points on the map belong to a :class:`.Region` ,
                some are in ``border`` polygons such as :class:`.MDRamp`


        Example:
                >>> # query in which region is the enemy main
                >>> position = self.bot.enemy_start_locations[0].position
                >>> all_polygon_areas_in_position = self.where_all(position)
                [Region 0]

                >>> enemy_main_base_region = all_polygon_areas_in_position[0]
                >>> enemy_main_base_region
                Region 0

                >>> # now it is very easy to know which region is the enemy's natural
                >>> # connected_regions is a property of a Region
                >>> enemy_natural_region = enemy_main_base_region.connected_regions[0]
                >>> enemy_natural_region
                Region 3

        Tip:

            *avg performance*

            * :class:`.Region` query 21.5 µs ± 652 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
            * :class:`.ChokeArea` ``query 18 µs`` ± 1.25 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)
            * :class:`.MDRamp` query  22 µs ± 982 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)


        """
        results = []
        if isinstance(point, Point2):
            point = point.rounded
        if isinstance(point, tuple):
            point = int(point[0]), int(point[1])

        for region in self.regions.values():
            if region.is_inside_point(point):
                results.append(region)
        for choke in self.map_chokes:
            if choke.is_inside_point(point):
                results.append(choke)
        # assert (len(list(set(results))) == len(results)), f"results{results},  list(set(results)){list(set(results))}"
        return results

    def where(
            self, point: Union[Point2, tuple]
    ) -> Union[Region, MDRamp, ChokeArea, VisionBlockerArea]:
        """
        :rtype: Union[:mod:`.Region`, :class:`.ChokeArea`, :class:`.VisionBlockerArea`, :class:`.MDRamp`]

        Will query a point on the map and will return the first result in the following order:

            * :class:`.Region`
            * :class:`.MDRamp`
            * :class:`.ChokeArea`

        Tip:

            *avg performance*

            * :class:`.Region` query 7.09 µs ± 329 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
            * :class:`.ChokeArea` query  17.9 µs ± 1.22 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)
            * :class:`.MDRamp` ``query 11.7 µs`` ± 1.13 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)

        """
        if isinstance(point, Point2):
            point = point.rounded
        if isinstance(point, tuple):
            point = int(point[0]), int(point[1])

        for region in self.regions.values():
            if region.is_inside_point(point):
                return region
        for choke in self.map_chokes:
            if choke.is_inside_point(point):
                return choke

    @lru_cache(100)
    def in_region_p(self, point: Union[Point2, tuple]) -> Optional[Region]:
        """
        :rtype: Optional[:class:`.Region`]

        Will query if a point is in, and in which Region using Set of Points <fast>

        Tip:
            time benchmark 4.35 µs ± 27.5 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

            as long as polygon points is of type :class:`.set`, not :class:`.list`

        """
        if isinstance(point, Point2):
            point = point.rounded
        if isinstance(point, tuple):
            point = int(point[0]), int(point[1])
        for region in self.regions.values():
            if region.is_inside_point(point):
                return region

    """ longest map compile is 1.9 s """
    """Compile methods"""

    def _clean_plib_chokes(self) -> None:
        # needs to be called AFTER MDramp and VisionBlocker are populated
        areas = self.map_ramps.copy()
        areas.extend(self.map_vision_blockers)
        self.overlapping_choke_ids = self._get_overlapping_chokes(local_chokes=self.c_ext_map.chokes,
                                                                  areas=areas)

    @staticmethod
    def _get_overlapping_chokes(local_chokes: List[CMapChoke],
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

    @progress_wrapped(estimated_time=0, desc=f"\u001b[32m Version {__version__} Map Compilation Progress \u001b[37m")
    def _compile_map(self) -> None:

        self._calc_grid()
        self._calc_regions()
        self._calc_vision_blockers()
        self._set_map_ramps()

        self._clean_polys()

        self._calc_chokes()
        for poly in self.polygons:
            poly.calc_areas()
        for ramp in self.map_ramps:
            ramp.set_regions()

        self.pather.set_connectivity_graph()
        self.connectivity_graph = self.pather.connectivity_graph

    def _calc_grid(self) -> None:
        # converting the placement grid to our own kind of grid
        # cleaning the grid and then searching for 2x2 patterned regions
        grid = binary_fill_holes(self.placement_arr).astype(int)
        # for our grid,  mineral walls are considered as a barrier between regions
        for point in self.resource_blockers:
            grid[int(point[0])][int(point[1])] = 0
            for n in point.neighbors4:
                point_ = Point2((n.rounded[0], n.rounded[1]))
                if point_[0] < grid.shape[1] and point_[1] < grid.shape[0]:
                    grid[int(point_[1])][int(point_[0])] = 0

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
        # some ramps coming from burnysc2 have broken data and the bottom_center and top_center
        # may even be the same. by removing them they should be tagged as chokes in the c extension
        # if they really are ones
        viable_ramps = list(filter(lambda x: x.bottom_center.distance_to(x.top_center) >= 1,
                            self.bot.game_info.map_ramps))
        self.map_ramps = [MDRamp(map_data=self,
                                 ramp=r,
                                 array=self.points_to_numpy_array(r.points))
                          for r in viable_ramps]

    def _calc_vision_blockers(self) -> None:
        # compute VisionBlockerArea

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
        # compute ChokeArea

        self._clean_plib_chokes()
        chokes = [c for c in self.c_ext_map.chokes if c.id not in self.overlapping_choke_ids]
        self.map_chokes = self.map_ramps.copy()
        self.map_chokes.extend(self.map_vision_blockers)

        for choke in chokes:

            points = [Point2(p) for p in choke.pixels]
            if len(points) > 0:
                new_choke_array = self.points_to_numpy_array(points)
                cm = center_of_mass(new_choke_array)
                cm = int(cm[0]), int(cm[1])
                areas = self.where_all(cm)

                new_choke = RawChoke(
                        map_data=self, array=new_choke_array, raw_choke=choke
                )
                for area in areas:

                    if isinstance(area, Region):
                        area.region_chokes.append(new_choke)
                        new_choke.areas.append(area)
                    if area.is_choke and not area.is_ramp and not area.is_vision_blocker:
                        self.polygons.remove(new_choke)
                        area.points.update(new_choke.points)
                        new_choke = None

                if new_choke:
                    self.map_chokes.append(new_choke)
            else:  # pragma: no cover
                logger.debug(f" [{self.map_name}] Cant add {choke} with 0 points")

    def _calc_regions(self) -> None:
        # compute Region

        # some areas are with area of 1, 2 ,5   these are not what we want,
        # so we filter those out
        # if len(self.map_ramps) == 0:
        #     self._set_map_ramps()
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

            if self.max_region_area > region.area > self.min_region_area:
                region.label = j
                self.regions[j] = region
                # region.calc_ramps()
                j += 1

    """Plot methods"""

    def draw_influence_in_game(self, grid: ndarray,
                               lower_threshold: int = 1,
                               upper_threshold: int = 1000,
                               color: Tuple[int, int, int] = (201, 168, 79),
                               size: int = 13) -> None:
        """
        :rtype: None
        Draws influence (cost) values of a grid in game.

        Caution:
            Setting the lower threshold too low impacts performance since almost every value will get drawn.

            It's recommended that this is set to the relevant grid's default weight value.

        Example:
                >>> self.ground_grid = self.get_pyastar_grid(default_weight=1)
                >>> self.ground_grid = self.add_cost((100, 100), radius=15, grid=self.ground_grid, weight=50)
                >>> self.draw_influence_in_game(self.ground_grid, lower_threshold=1)

        See Also:
            * :meth:`.MapData.get_pyastar_grid`
            * :meth:`.MapData.get_climber_grid`
            * :meth:`.MapData.get_clean_air_grid`
            * :meth:`.MapData.get_air_vs_ground_grid`
            * :meth:`.MapData.add_cost`

        """
        self.debugger.draw_influence_in_game(self.bot, grid, lower_threshold, upper_threshold, color, size)

    def plot_map(
            self,
            fontdict: dict = None,
            save: Optional[bool] = None,
            figsize: int = 20) -> None:
        """

        Plot map (does not ``show`` or ``save``)

        """
        if save is not None:
            logger.warning(CustomDeprecationWarning(oldarg='save', newarg='self.save()'))
        self.debugger.plot_map(fontdict=fontdict, figsize=figsize)

    def plot_influenced_path_pyastar(self,

                             start: Union[Tuple[float, float], Point2],
                             goal: Union[Tuple[float, float], Point2],
                             weight_array: ndarray,
                             allow_diagonal=False,
                             name: Optional[str] = None,
                             fontdict: dict = None) -> None:
        """

        A useful debug utility method for experimenting with the :mod:`.Pather` module

        """

        self.debugger.plot_influenced_path_pyastar(start=start,
                                           goal=goal,
                                           weight_array=weight_array,
                                           name=name,
                                           fontdict=fontdict,
                                           allow_diagonal=allow_diagonal)

    def plot_influenced_path(self,
                               start: Union[Tuple[float, float], Point2],
                               goal: Union[Tuple[float, float], Point2],
                               weight_array: ndarray,
                               smoothing: bool = False,
                               name: Optional[str] = None,
                               fontdict: dict = None) -> None:
        """

        A useful debug utility method for experimenting with the :mod:`.Pather` module

        """

        self.debugger.plot_influenced_path(start=start,
                                             goal=goal,
                                             weight_array=weight_array,
                                             smoothing=smoothing,
                                             name=name,
                                             fontdict=fontdict)

    def _plot_regions(self, fontdict: Dict[str, Union[str, int]]) -> None:
        return self.debugger.plot_regions(fontdict=fontdict)

    def _plot_vision_blockers(self) -> None:
        self.debugger.plot_vision_blockers()

    def _plot_normal_resources(self) -> None:
        # todo: account for gold minerals and rich gas
        self.debugger.plot_normal_resources()

    def _plot_chokes(self) -> None:
        self.debugger.plot_chokes()

    def __repr__(self) -> str:
        return f"<MapData[{self.version}][{self.bot.game_info.map_name}][{self.bot}]>"
