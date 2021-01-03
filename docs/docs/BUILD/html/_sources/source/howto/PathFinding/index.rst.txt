.. include:: ../header.rst

Pathfinding - Recipes
=====================


Pathfinding - from our main to the enemy's main
-------------------------------------------------

* :meth:`.MapData.where_all`
* :meth:`.MapData.pathfind`

.. code-block::

        >>> my_base_raw_location = self.bot.townhalls[0].position
        >>> my_region = self.where_all(my_base_raw_location)[0]
        >>> enemy_main_region = self.where_all(self.bot.enemy_start_locations[0].position)[0]
        >>> start = my_region.center
        >>> goal = enemy_main_region.center
        >>> grid = self.get_pyastar_grid()
        >>> path = self.pathfind(start=start, goal=goal, grid=grid, sensitivity=3)
        >>> path
        [(37, 55), (40, 58), (43, 61), (44, 64), (47, 67), (50, 70), (52, 73), (52, 76), (52, 79), (54, 82), (57, 82), (60, 82), (63, 82), (66, 82), (69, 82), (72, 82), (75, 82), (78, 82), (81, 82), (84, 82), (87, 82), (90, 82), (93, 82), (96, 82), (99, 82), (102, 82), (105, 82), (108, 82), (111, 82), (114, 82), (117, 82), (120, 82), (123, 82), (126, 82), (129, 82), (132, 82), (135, 82), (138, 82), (141, 82), (144, 82), (147, 82), (150, 82), (153, 82), (155, 79), (155, 76), (155, 73), (157, 70), (160, 67), (163, 64), (164, 61), (167, 58), (170, 55), (173, 52)]


Plot and Debug the Pather - In Game
-----------------------------------

* Contributed by `rasper (github) <https://github.com/raspersc2>`_

.. code-block::

         >>> grid = self.get_air_vs_ground_grid()
         >>> # self.draw_influence_in_game(grid) # commented out to not fail doc tests

Plot and Debug the Pather
-------------------------

* :meth:`.MapData.where_all`
* :meth:`.MapData.plot_influenced_path`

.. code-block::

        >>> my_base_raw_location = self.bot.townhalls[0].position
        >>> my_region = self.where_all(my_base_raw_location)[0]
        >>> enemy_main_region = self.where_all(self.bot.enemy_start_locations[0].position)[0]
        >>> start = my_region.center
        >>> goal = enemy_main_region.center
        >>> grid = self.get_pyastar_grid()
        >>> # commented out for doc tests
        >>> # path = self.plot_influenced_path(start=start, goal=goal, weight_array=grid)
        >>> # self.show()


.. image:: pathing_simple.png
   :width: 75%


Plotting our custom Cost
-------------------------

* :meth:`.MapData.where_all`
* :meth:`.MapData.plot_influenced_path`
* :meth:`.MapData.add_cost`

**Let's add a cost with a big radius (25)  and the default weight of 100,  in a point we know is in our path**

.. code-block::

        >>> my_base_raw_location = self.bot.townhalls[0].position
        >>> my_region = self.where_all(my_base_raw_location)[0]
        >>> enemy_main_region = self.where_all(self.bot.enemy_start_locations[0].position)[0]
        >>> start = my_region.center
        >>> goal = enemy_main_region.center
        >>> grid = self.get_pyastar_grid()
        >>> p = (100,60) # the center point of which to add cost
        >>> grid = self.add_cost(position=p,radius=25, grid=grid )
        >>> # commented out for doc tests
        >>> # path = self.plot_influenced_path(start=start, goal=goal, weight_array=grid)
        >>> # self.show()


.. image:: path_with_cost.png
   :width: 75%


Influenced paths plots:
-----------------------

.. image:: https://user-images.githubusercontent.com/40754127/89323316-299bd500-d68e-11ea-8f98-24e7d9e78e1e.png
.. image:: https://user-images.githubusercontent.com/40754127/89323320-299bd500-d68e-11ea-8b89-d59d1387adca.png
.. image:: https://user-images.githubusercontent.com/40754127/89323322-2a346b80-d68e-11ea-8de6-996565e40c6b.png
.. image:: https://user-images.githubusercontent.com/40754127/89323304-24d72100-d68e-11ea-9ffc-8e835ea8c505.png
.. image:: https://user-images.githubusercontent.com/40754127/89323311-27d21180-d68e-11ea-97c4-99d6acd3cfa3.png
.. image:: https://user-images.githubusercontent.com/40754127/89323312-286aa800-d68e-11ea-854b-cfbb7beb261a.png
.. image:: https://user-images.githubusercontent.com/40754127/89323315-29033e80-d68e-11ea-97cb-17957ee9675c.png
