.. include:: ../header.rst

Plotting - Recipes
==================

Plot the map and view it in memory
----------------------------------

* :meth:`.MapData.plot_map`
* :meth:`.MapData.show`

.. code-block::

        >>> map_data.plot_map()
        >>> map_data.show()

.. image:: map_plot.png
   :width: 75%

Plot the map and save it to a file
----------------------------------

* :meth:`.MapData.plot_map`
* :meth:`.MapData.save`

.. code-block::

        >>> map_data.plot_map()
        >>> map_data.save(filename='myplot.png')



Plot any  Polygon
-----------------

.. code-block::

        >>> my_base_raw_location = map_data.bot.townhalls[0].position
        >>> my_region = map_data.where_all(my_base_raw_location)[0]
        >>> my_region.plot()
        >>> map_data.show()

.. image:: region1_plot.png
   :width: 75%


