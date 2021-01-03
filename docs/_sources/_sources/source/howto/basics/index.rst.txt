.. include:: ../header.rst

Basic - Recipes
===============


Get our Starting :class:`.Region`
---------------------------------

* :meth:`.MapData.where`

.. code-block::

        >>> my_base_raw_location = self.bot.townhalls[0].position
        >>> my_region = self.where_all(my_base_raw_location)[0]
        >>> my_region
        Region 3


Get Enemy Main and Natural :class:`.Region`
--------------------------------------------

* :meth:`.MapData.where_all`
* :meth:`.Region.connected_regions`

.. code-block::

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
        >>> enemy_natural_region = enemy_main_base_region.connected_regions[0] # connected_regions is a property of a Region
        >>> enemy_natural_region.label == 6 or enemy_natural_region.label == 1 # doctest expects this to be true and it changes based on positions
        True


:class:`.Region` connectivity
-------------------------------

* :meth:`.Region.connected_regions`

.. code-block::

        >>> my_base_location = self.bot.townhalls[0].position
        >>> my_region = self.where_all(my_base_location)[0]
        >>> my_region
        Region 3
        >>> # returns a list
        >>> my_region.connected_regions.sort(key=lambda x: x.label) # sorting for doctest
        >>> my_region.connected_regions
        [Region 0, Region 5]



