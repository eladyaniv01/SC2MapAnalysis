:orphan:

:mod:`MapAnalyzer.MapData`
==========================

.. py:module:: MapAnalyzer.MapData


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   MapAnalyzer.MapData.MapData



.. py:class:: MapData(bot: BotAI, loglevel: str = 'ERROR', arcade: bool = False, corner_distance: int = CORNER_MIN_DISTANCE)

   Entry point for the user

   .. method:: vision_blockers(self)
      :property:


      Exposing the computed method

      ``vision_blockers`` are not to be confused with :data:`self.map_vision_blockers`
      ``vision_blockers`` are the raw data received from ``burnysc2`` and will be processed later on.


   .. method:: get_pyastar_grid(self, default_weight: float = 1, include_destructables: bool = True)


      :rtype: numpy.ndarray
      .. note::

         To query what is the cost in a certain point, simple do ``my_grid[certain_point]`` where `certain_point`
         
         is a :class:`tuple` or a :class:`sc2.position.Point2`

      Requests a new pathing grid.

      This grid will have all non pathable cells set to :class:`numpy.inf`.

      pathable cells will be set to the ``default_weight`` which it's default is ``1``.

      After you get the grid, you can add your own ``cost`` (also known as ``weight`` or ``influence``)

      This grid can, and **should** be reused in the duration of the frame,
      and should be regenerated(**once**) on each frame.

      .. note::

         destructables that has been destroyed will be updated by default,
         
         the only known use case for ``include_destructables`` usage is illustrated in the first example below

      .. admonition:: Example

         We want to check if breaking the destructables in our path will make it better,
         
         so we treat destructables as if they were pathable
         
         >>> no_destructables_grid = self.get_pyastar_grid(default_weight = 1, include_destructables= False)
         >>> # 2 set up a grid with default weight of 300
         >>> custom_weight_grid = self.get_pyastar_grid(default_weight = 300)

      .. seealso::

         * :meth:`.MapData.get_climber_grid`
         * :meth:`.MapData.get_air_vs_ground_grid`
         * :meth:`.MapData.get_clean_air_grid`
         * :meth:`.MapData.add_cost`
         * :meth:`.MapData.pathfind`
         * :meth:`.MapData.find_lowest_cost_points`


   .. method:: find_lowest_cost_points(self, from_pos: Point2, radius: float, grid: np.ndarray)


      :rtype:  Union[List[:class:`sc2.position.Point2`], None]

      Given an origin point and a radius,  will return a list containing the lowest cost points
      (if there are more than one)

      .. admonition:: Example

         >>> my_grid = self.get_air_vs_ground_grid()
         >>> position = (100, 80)
         >>> my_radius = 10
         >>> self.find_lowest_cost_points(from_pos=position, radius=my_radius, grid=my_grid)
         [(90, 80), (91, 76), (91, 77), (91, 78), (91, 79), (91, 80), (91, 81), (92, 74), (92, 75), (92, 76), (92, 77), (92, 78), (92, 79), (92, 80), (92, 81), (93, 73), (93, 74), (93, 75), (93, 76), (93, 77), (93, 78), (93, 79), (93, 80), (93, 81), (94, 72), (94, 73), (94, 74), (94, 75), (94, 76), (94, 77), (95, 73), (95, 74), (95, 75), (95, 76), (96, 74), (96, 75), (97, 74), (97, 75), (98, 74), (98, 75), (99, 74), (99, 75), (100, 74), (100, 75), (101, 74), (101, 75), (102, 74), (102, 75), (103, 74), (103, 75), (104, 74), (104, 75), (105, 74), (105, 75), (106, 74), (106, 75), (107, 74), (107, 75), (108, 74), (108, 75)]

      .. seealso::

         * :meth:`.MapData.get_pyastar_grid`
         * :meth:`.MapData.get_climber_grid`
         * :meth:`.MapData.get_air_vs_ground_grid`
         * :meth:`.MapData.get_clean_air_grid`
         * :meth:`.MapData.add_cost`
         * :meth:`.MapData.pathfind`


   .. method:: lowest_cost_points_array(self, from_pos: Point2, radius: float, grid: np.ndarray)


      :rtype:    Union[:class:`numpy.ndarray`, None]
      Same as find_lowest_cost_points, but returns points in ndarray for use

      with numpy/scipy/etc


   .. method:: get_climber_grid(self, default_weight: float = 1, include_destructables: bool = True)


      :rtype: numpy.ndarray
      Climber grid is a grid modified by the c extension, and is used for units that can climb,

      such as Reaper, Colossus

      This grid can be reused in the duration of the frame,

      and should be regenerated(once) on each frame.

      This grid also gets updated with all nonpathables when requested

      such as structures, and destructables

      .. admonition:: Example

         >>> updated_climber_grid = self.get_climber_grid(default_weight = 1)

      .. seealso::

         * :meth:`.MapData.get_pyastar_grid`
         * :meth:`.MapData.get_air_vs_ground_grid`
         * :meth:`.MapData.get_clean_air_grid`
         * :meth:`.MapData.add_cost`
         * :meth:`.MapData.pathfind`
         * :meth:`.MapData.find_lowest_cost_points`


   .. method:: get_air_vs_ground_grid(self, default_weight: float = 100)


      :rtype: numpy.ndarray
      ``air_vs_ground`` grid is computed in a way that lowers the cost of nonpathable terrain,

       making air units naturally "drawn" to it.

      .. caution::

         Requesting a grid with a ``default_weight`` of 1 is pointless,
         
         and  will result in a :meth:`.MapData.get_clean_air_grid`

      .. admonition:: Example

         >>> air_vs_ground_grid = self.get_air_vs_ground_grid()

      .. seealso::

         * :meth:`.MapData.get_pyastar_grid`
         * :meth:`.MapData.get_climber_grid`
         * :meth:`.MapData.get_clean_air_grid`
         * :meth:`.MapData.add_cost`
         * :meth:`.MapData.pathfind`
         * :meth:`.MapData.find_lowest_cost_points`


   .. method:: get_clean_air_grid(self, default_weight: float = 1)


      :rtype: numpy.ndarray

      Will return a grid marking every cell as pathable with ``default_weight``

      .. seealso:: * :meth:`.MapData.get_air_vs_ground_grid`


   .. method:: pathfind_pyastar(self, start: Union[Tuple[float, float], Point2], goal: Union[Tuple[float, float], Point2], grid: Optional[ndarray] = None, allow_diagonal: bool = False, sensitivity: int = 1)


      :rtype: Union[List[:class:`sc2.position.Point2`], None]
      Will return the path with lowest cost (sum) given a weighted array (``grid``), ``start`` , and ``goal``.


      **IF NO** ``grid`` **has been provided**, will request a fresh grid from :class:`.Pather`

      If no path is possible, will return ``None``

      .. tip::

         ``sensitivity`` indicates how to slice the path,
         just like doing: ``result_path = path[::sensitivity]``
             where ``path`` is the return value from this function
         
         this is useful since in most use cases you wouldn't want
         to get each and every single point,
         
         getting every  n-``th`` point works better in practice

      .. caution::

         ``allow_diagonal=True`` will result in a slight performance penalty.
         
         `However`, if you don't over-use it, it will naturally generate shorter paths,
         
         by converting(for example) ``move_right + move_up`` into ``move_top_right`` etc.

      .. todo:: more examples for different usages available

      .. admonition:: Example

         >>> my_grid = self.get_pyastar_grid()
         >>> # start / goal could be any tuple / Point2
         >>> st, gl = (50,75) , (100,100)
         >>> path = self.pathfind_pyastar(start=st,goal=gl,grid=my_grid,allow_diagonal=True, sensitivity=3)

      .. seealso::

         * :meth:`.MapData.get_pyastar_grid`
         * :meth:`.MapData.find_lowest_cost_points`


   .. method:: pathfind(self, start: Union[Tuple[float, float], Point2], goal: Union[Tuple[float, float], Point2], grid: Optional[ndarray] = None, large: bool = False, smoothing: bool = False, sensitivity: int = 1)


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

      `` large`` is a boolean that determines whether we are doing pathing with large unit sizes
      like Thor and Ultralisk. When it's false the pathfinding is using unit size 1, so if
      you want to a guarantee that a unit with size > 1 fits through the path then large should be True.

      ``smoothing`` tries to do a similar thing on the c side but to the maximum extent possible.
      it will skip all the waypoints it can if taking the straight line forward is better
      according to the influence grid

      .. admonition:: Example

         >>> my_grid = self.get_pyastar_grid()
         >>> # start / goal could be any tuple / Point2
         >>> st, gl = (50,75) , (100,100)
         >>> path = self.pathfind(start=st,goal=gl,grid=my_grid, large=False, smoothing=False, sensitivity=3)

      .. seealso::

         * :meth:`.MapData.get_pyastar_grid`
         * :meth:`.MapData.find_lowest_cost_points`


   .. method:: add_cost(self, position: Tuple[float, float], radius: float, grid: ndarray, weight: float = 100, safe: bool = True, initial_default_weights: float = 0)


      :rtype: numpy.ndarray

      Will add cost to a `circle-shaped` area with a center ``position`` and radius ``radius``

      weight of 100

      .. warning:: When ``safe=False`` the Pather will not adjust illegal values below 1 which could result in a crash`


   .. method:: save(self, filename)


      Save Plot to a file, much like ``plt.save(filename)``


   .. method:: show(self)


      Calling debugger to show, just like ``plt.show()``  but in case there will be changes in debugger,

      This method will always be compatible


   .. method:: close(self)


      Close an opened plot, just like ``plt.close()``  but in case there will be changes in debugger,

      This method will always be compatible


   .. method:: indices_to_points(indices: Union[ndarray, Tuple[ndarray, ndarray]])
      :staticmethod:


      :rtype: :class:`.set` (Union[:class:`.tuple` (:class:`.int`, :class:`.int`), :class:`sc2.position.Point2`)

      Convert indices to a set of points(``tuples``, not ``Point2`` )

      Will only work when both dimensions are of same length


   .. method:: points_to_indices(points: Set[Tuple[float, float]])
      :staticmethod:


      :rtype: Tuple[numpy.ndarray, numpy.ndarray]

      Convert a set / list of points to a tuple of two 1d numpy arrays


   .. method:: points_to_numpy_array(self, points: Union[Set[Tuple[int64, int64]], List[Point2], Set[Point2]], default_value: int = 1)


      :rtype: numpy.ndarray

      Convert points to numpy ndarray

      .. caution:: Will handle safely(by ignoring) points that are ``out of bounds``, without warning


   .. method:: distance(p1: Point2, p2: Point2)
      :staticmethod:


      :rtype: float64

      Euclidean distance


   .. method:: distance_squared(p1: Point2, p2: Point2)
      :staticmethod:


      :rtype: float64

      Euclidean distance squared


   .. method:: closest_node_idx(node: Union[Point2, ndarray], nodes: Union[List[Tuple[int, int]], ndarray])
      :staticmethod:


      :rtype: int

      Given a list of ``nodes``  and a single ``node`` ,

      will return the index of the closest node in the list to ``node``


   .. method:: closest_towards_point(self, points: List[Point2], target: Union[Point2, tuple])


      :rtype: :class:`sc2.position.Point2`

      Given a list/set of points, and a target,

      will return the point that is closest to that target

      .. admonition:: Example

         Calculate a position for tanks in direction to the enemy forces
         passing in the Area's corners as points and enemy army's location as target
         
         >>> enemy_army_position = (50,50)
         >>> my_base_location = self.bot.townhalls[0].position
         >>> my_region = self.where_all(my_base_location)[0]
         >>> best_siege_spot = self.closest_towards_point(points=my_region.corner_points, target=enemy_army_position)
         >>> best_siege_spot
         (49, 52)


   .. method:: region_connectivity_all_paths(self, start_region: Region, goal_region: Region, not_through: Optional[List[Region]] = None)


      :param start_region: :mod:`.Region`
      :param goal_region: :mod:`.Region`
      :param not_through: Optional[List[:mod:`.Region`]]
      :rtype: List[List[:mod:`.Region`]]

      Returns all possible paths through all :mod:`.Region` (via ramps),

      can exclude a region by passing it in a not_through list


   .. method:: where_all(self, point: Union[Point2, tuple])


      :rtype: List[Union[:class:`.Region`, :class:`.ChokeArea`, :class:`.VisionBlockerArea`, :class:`.MDRamp`]]

      Will return a list containing all :class:`.Polygon` that occupy the given point.

      If a :class:`.Region` exists in that list, it will be the first item

      .. caution::

         Not all points on the map belong to a :class:`.Region` ,
         some are in ``border`` polygons such as :class:`.MDRamp`

      .. admonition:: Example

         >>> # query in which region is the enemy main
         >>> position = self.bot.enemy_start_locations[0].position
         >>> all_polygon_areas_in_position = self.where_all(position)
         >>> all_polygon_areas_in_position
         [Region 4]
         
         >>> enemy_main_base_region = all_polygon_areas_in_position[0]
         >>> enemy_main_base_region
         Region 4
         
         >>> # now it is very easy to know which region is the enemy's natural
         >>> # connected_regions is a property of a Region
         >>> enemy_natural_region = enemy_main_base_region.connected_regions[0]
         >>> # will return Region 1 or 6 for goldenwall depending on starting position

      .. tip::

         *avg performance*
         
         * :class:`.Region` query 21.5 µs ± 652 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
         * :class:`.ChokeArea` ``query 18 µs`` ± 1.25 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)
         * :class:`.MDRamp` query  22 µs ± 982 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)


   .. method:: where(self, point: Union[Point2, tuple])


      :rtype: Union[:mod:`.Region`, :class:`.ChokeArea`, :class:`.VisionBlockerArea`, :class:`.MDRamp`]

      Will query a point on the map and will return the first result in the following order:

          * :class:`.Region`
          * :class:`.MDRamp`
          * :class:`.ChokeArea`

      .. tip::

         *avg performance*
         
         * :class:`.Region` query 7.09 µs ± 329 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
         * :class:`.ChokeArea` query  17.9 µs ± 1.22 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)
         * :class:`.MDRamp` ``query 11.7 µs`` ± 1.13 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)


   .. method:: in_region_p(self, point: Union[Point2, tuple])


      :rtype: Optional[:class:`.Region`]

      Will query if a point is in, and in which Region using Set of Points <fast>

      .. tip::

         time benchmark 4.35 µs ± 27.5 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
         
         as long as polygon points is of type :class:`.set`, not :class:`.list`


   .. method:: draw_influence_in_game(self, grid: ndarray, lower_threshold: int = 1, upper_threshold: int = 1000, color: Tuple[int, int, int] = (201, 168, 79), size: int = 13)


      :rtype: None
      Draws influence (cost) values of a grid in game.

      .. caution::

         Setting the lower threshold too low impacts performance since almost every value will get drawn.
         
         It's recommended that this is set to the relevant grid's default weight value.

      .. admonition:: Example

         >>> self.ground_grid = self.get_pyastar_grid(default_weight=1)
         >>> self.ground_grid = self.add_cost((100, 100), radius=15, grid=self.ground_grid, weight=50)
         >>> # self.draw_influence_in_game(self.ground_grid, lower_threshold=1) # commented out for doctest

      .. seealso::

         * :meth:`.MapData.get_pyastar_grid`
         * :meth:`.MapData.get_climber_grid`
         * :meth:`.MapData.get_clean_air_grid`
         * :meth:`.MapData.get_air_vs_ground_grid`
         * :meth:`.MapData.add_cost`


   .. method:: plot_map(self, fontdict: dict = None, save: Optional[bool] = None, figsize: int = 20)


      Plot map (does not ``show`` or ``save``)


   .. method:: plot_influenced_path_pyastar(self, start: Union[Tuple[float, float], Point2], goal: Union[Tuple[float, float], Point2], weight_array: ndarray, allow_diagonal=False, name: Optional[str] = None, fontdict: dict = None)


      A useful debug utility method for experimenting with the :mod:`.Pather` module


   .. method:: plot_influenced_path(self, start: Union[Tuple[float, float], Point2], goal: Union[Tuple[float, float], Point2], weight_array: ndarray, large: bool = False, smoothing: bool = False, name: Optional[str] = None, fontdict: dict = None)


      A useful debug utility method for experimenting with the :mod:`.Pather` module



