:orphan:

:mod:`MapAnalyzer.constructs`
=============================

.. py:module:: MapAnalyzer.constructs


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   MapAnalyzer.constructs.PathLibChoke
   MapAnalyzer.constructs.ChokeArea
   MapAnalyzer.constructs.MDRamp
   MapAnalyzer.constructs.VisionBlockerArea



.. py:class:: PathLibChoke(pathlib_choke: Choke, pk: int)

   wrapper to the data returned by :mod:`.sc2pathlibp`

   with a bit of added fields / data type for convenience


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


