:orphan:

:mod:`MapAnalyzer.Region`
=========================

.. py:module:: MapAnalyzer.Region


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   MapAnalyzer.Region.Region



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



