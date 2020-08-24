:orphan:

:mod:`MapAnalyzer.Polygon`
==========================

.. py:module:: MapAnalyzer.Polygon


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   MapAnalyzer.Polygon.BuildablePoints
   MapAnalyzer.Polygon.Polygon



.. py:class:: BuildablePoints(polygon)

   Represents the Buildable Points in a :class:`.Polygon`,

   "Lazy" class that will only update information when it is needed

   .. tip:: :class:`.BuildablePoints` that belong to a :class:`.ChokeArea`  are always the edges, this is useful for walling off

   .. method:: free_pct(self)
      :property:


      A simple method for knowing what % of the points is left available out of the total


   .. method:: update(self)


      To be called only by :class:`.Polygon`, this ensures that updates are done in a lazy fashion,

      the update is evaluated only when there is need for the information, otherwise it is ignored



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



