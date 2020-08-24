:orphan:

:mod:`MapAnalyzer`
==================

.. py:module:: MapAnalyzer


Submodules
----------
.. toctree::
   :titlesonly:
   :maxdepth: 1

   destructibles/index.rst


Package Contents
----------------

Classes
~~~~~~~

.. autoapisummary::

   MapAnalyzer.MapData
   MapAnalyzer.Polygon
   MapAnalyzer.Region
   MapAnalyzer.ChokeArea
   MapAnalyzer.MDRamp
   MapAnalyzer.VisionBlockerArea



.. py:class:: MapData(bot: BotAI, loglevel: str = 'ERROR')

   Entry point for the user

   .. method:: vision_blockers(self)
      :property:


      Exposing the computed method

      ``vision_blockers`` are not to be confused with :data:`self.map_vision_blockers`
      ``vision_blockers`` are the raw data received from ``burnysc2`` and will be processed later on.


   .. method:: get_pyastar_grid(self, default_weight: int = 1, include_destructables: bool = True, air_pathing: Optional[bool] = None)


      :rtype: numpy.ndarray
      .. warning:: ``air_pathing`` is deprecated, use :meth:`.MapData.get_clean_air_grid` or :meth:`.MapData.get_air_vs_ground_grid`

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
         
         >>> # 1
         >>> no_destructables_grid = self.get_pyastar_grid(default_weight = 1, include_destructables= False)
         
         >>> # 2 set up a grid with default weight of 300
         >>> custom_weight_grid = self.get_pyastar_grid(default_weight = 300)

      .. seealso::

         * :meth:`.MapData.get_climber_grid`
         * :meth:`.MapData.get_air_vs_ground_grid`
         * :meth:`.MapData.get_clean_air_grid`
         * :meth:`.MapData.add_cost`
         * :meth:`.MapData.pathfind`


   .. method:: get_climber_grid(self, default_weight: int = 1)


      :rtype: numpy.ndarray
      Climber grid is a grid modified by :mod:`sc2pathlibp`, and is used for units that can climb,

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


   .. method:: get_air_vs_ground_grid(self, default_weight: int = 100)


      :rtype: numpy.ndarray
      ``air_vs_ground`` grid is computed in a way that lowers the cost of nonpathable terrain,

       making air units naturally "drawn" to it.

      .. caution:: Requesting a grid with a ``default_weight`` of 1 is pointless, and  will result in a :meth:`.MapData.get_clean_air_grid`

      .. admonition:: Example

         >>> air_vs_ground_grid = self.get_air_vs_ground_grid()

      .. seealso::

         * :meth:`.MapData.get_pyastar_grid`
         * :meth:`.MapData.get_climber_grid`
         * :meth:`.MapData.get_clean_air_grid`
         * :meth:`.MapData.add_cost`
         * :meth:`.MapData.pathfind`


   .. method:: get_clean_air_grid(self, default_weight: int = 1)


      :rtype: numpy.ndarray

      Will return a grid marking every cell as pathable with ``default_weight``

      .. seealso:: * :meth:`.MapData.get_air_vs_ground_grid`


   .. method:: pathfind(self, start: Union[Tuple[int, int], Point2], goal: Union[Tuple[int, int], Point2], grid: Optional[ndarray] = None, allow_diagonal: bool = False, sensitivity: int = 1)


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

         >>> grid = self.get_pyastar_grid()
         >>> # start / goal could be any tuple / Point2
         >>> path = self.pathfind(start=start,goal=goal,grid=grid,allow_diagonal=True, sensitivity=3)

      .. seealso:: * :meth:`.MapData.get_pyastar_grid`


   .. method:: add_cost(self, position: Tuple[int, int], radius: int, grid: ndarray, weight: int = 100, safe: bool = True)


      :rtype: numpy.ndarray

      Will add cost to a `circle-shaped` area with a center ``position`` and radius ``radius``

      weight of 100

      .. warning:: When ``safe=False`` the Pather will not adjust illegal values below 1 which could result in a crash`


   .. method:: log(self, msg)


      Lazy logging


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


   .. method:: points_to_indices(points: Set[Tuple[int, int]])
      :staticmethod:


      :rtype: Tuple[numpy.ndarray, numpy.ndarray]

      Convert a set / list of points to a tuple of two 1d numpy arrays


   .. method:: points_to_numpy_array(self, points: Union[Set[Tuple[int64, int64]], List[Point2], Set[Point2]])


      :rtype: numpy.ndarray

      Convert points to numpy ndarray

      .. caution:: Will handle safely(by ignoring) points that are ``out of bounds``, without warning


   .. method:: distance(p1: Point2, p2: Point2)
      :staticmethod:


      :rtype: float64

      Euclidean distance


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
         
         >>> enemy_army_position = Point2((50,50)) # random point for this example
         >>> my_base_location = self.bot.townhalls[0]
         >>> my_region = self.where(my_base_location)
         >>> corners = my_region.corner_points
         >>> best_siege_spot = self.closest_towards_point(points=corners, target=enemy_army_position)
         (57,120)


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

      .. caution:: Not all points on the map belong to a :class:`.Region` , some are in ``border`` polygons such as :class:`.MDRamp`

      .. admonition:: Example

         >>> # query in which region is the enemy main
         >>> position = self.bot.enemy_start_locations[0].position
         >>> all_polygon_areas_in_position = self.where_all(position)
         [Region 0]
         
         >>> enemy_main_base_region = all_polygon_areas_in_position[0]
         >>> enemy_main_base_region
         Region 0
         
         >>> # now it is very easy to know which region is the enemy's natural
         >>> enemy_natural_region = enemy_main_base_region.connected_regions[0] # connected_regions is a property of a Region
         >>> enemy_natural_region
         Region 3

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


   .. method:: in_region_i(self, point: Union[Point2, tuple])


      :rtype: Optional[:class:`.Region`]

      Will query a if a point is in, and in which Region using Indices <slower>



      .. tip::

         :meth:`.in_region_p` performs better,  and should be used.
         
         time benchmark 18.6 µs ± 197 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)


   .. method:: plot_map(self, fontdict: dict = None, save: Optional[bool] = None, figsize: int = 20)


      Plot map (does not ``show`` or ``save``)


   .. method:: plot_influenced_path(self, start: Union[Tuple[int, int], Point2], goal: Union[Tuple[int, int], Point2], weight_array: ndarray, allow_diagonal=False, plot: Optional[bool] = None, save: Optional[bool] = None, name: Optional[str] = None, fontdict: dict = None)


      A useful debug utility method for experimenting with the :mod:`.Pather` module



.. py:class:: Polygon(map_data: MapData, array: ndarray)

   Base Class for Representing an "Area"

   .. method:: buildable_points(self)
      :property:


      :rtype: :class:`.BuildablePoints`

      Is a responsible for holding and updating the buildable points of it's respected :class:`.Polygon`


   .. method:: regions(self)
      :property:


      :rtype: List[:class:`.Region`]

      Filters out every Polygon that is not a region, and is inside / bordering with ``self``


   .. method:: plot(self, testing: bool = False)


      plot


   .. method:: nodes(self)
      :property:


      List of :class:`.Point2`


   .. method:: corner_array(self)
      :property:


      This is how the corners are calculated

      TODO
          make this adjustable to the user


   .. method:: width(self)
      :property:


      Lazy width calculation,   will be approx 0.5 < x < 1.5 of real width


   .. method:: corner_points(self)
      :property:


      :rtype: List[:class:`.Point2`]


   .. method:: center(self)
      :property:


      Since the center is always going to be a ``float``,

      and for performance considerations we use integer coordinates.

      We will return the closest point registered


   .. method:: is_inside_point(self, point: Union[Point2, tuple])


      Query via Set(Point2)  ''fast''


   .. method:: is_inside_indices(self, point: Union[Point2, tuple])


      Query via 2d np.array  ''slower''


   .. method:: perimeter(self)
      :property:


      The perimeter is interpolated between inner and outer cell-types using broadcasting


   .. method:: perimeter_points(self)
      :property:


      Useful method for getting  perimeter points


   .. method:: area(self)
      :property:


      Sum of all points



.. py:class:: Region(map_data: MapData, array: np.ndarray, label: int, map_expansions: List[Point2])

   Bases: :class:`MapAnalyzer.Polygon.Polygon`

   Higher order "Area" , all of the maps can be summed up by it's :class:`.Region`

   .. tip::

      A :class:`.Region` may contain other :class:`.Polygon` inside it,
      
      Such as :class:`.ChokeArea` and :class:`.MDRamp`.
      
      But it will never share a point with another :class:`.Region`

   .. method:: region_ramps(self)
      :property:


      Property access to :class:`.MDRamp` of this region


   .. method:: region_chokes(self)
      :property:


      Property access to :class:`.ChokeArea` of this region


   .. method:: connected_regions(self)
      :property:


      Provides a list of :class:`.Region` that are connected by chokes to ``self``


   .. method:: plot_perimeter(self, self_only: bool = True)


      Debug Method plot_perimeter


   .. method:: plot(self, self_only: bool = True, testing: bool = False)


      Debug Method plot


   .. method:: base_locations(self)
      :property:


      base_locations inside ``self``



.. py:class:: ChokeArea(array: np.ndarray, map_data: MapData, pathlibchoke: Optional[PathLibChoke] = None)

   Bases: :class:`MapAnalyzer.Polygon.Polygon`

   Base class for all chokes


.. py:class:: MDRamp(map_data: MapData, array: np.ndarray, ramp: sc2Ramp)

   Bases: :class:`MapAnalyzer.constructs.ChokeArea`

   Wrapper for :class:`sc2.game_info.Ramp`,

   is responsible for calculating the relevant :class:`.Region`

   .. method:: closest_region(self, region_list)


      Will return the closest region with respect to self


   .. method:: set_regions(self)


      Method for calculating the relevant :class:`.Region`

      .. todo:: Make this a private method


   .. method:: top_center(self)
      :property:


      Alerts when sc2 fails to provide a top_center, and fallback to  :meth:`.center`


   .. method:: bottom_center(self)
      :property:


      Alerts when sc2 fails to provide a bottom_center, and fallback to  :meth:`.center`



.. py:class:: VisionBlockerArea(map_data: MapData, array: np.ndarray)

   Bases: :class:`MapAnalyzer.constructs.ChokeArea`

   VisionBlockerArea are areas containing tiles that hide the units that stand in it,

   (for example,  bushes)

   Units that attack from within a :class:`VisionBlockerArea`

   cannot be targeted by units that do not stand inside


