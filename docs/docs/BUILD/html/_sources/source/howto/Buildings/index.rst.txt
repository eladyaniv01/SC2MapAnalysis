Building Grid - Recipes
=======================

Find wall off building positions in a :class:`.Region`
------------------------------------------------------

* :class:`.Polygon.BuildablePoints`
* :meth:`.BuildablePoints.polygon`
* :meth:`.BuildablePoints.points`
* :meth:`.BuildablePoints.free_pct`
* :meth:`.Region.region_ramps`

.. code-block::

        >>> my_base_raw_location = map_data.bot.townhalls[0].position
        >>> my_region = map_data.where(my_base_raw_location)
        >>> my_region
        Region 1
        >>> # in most cases  region will have only one ramp,  but there are cases of more than one
        >>> my_region.region_ramps # ramps also describe which regions border
        [<MDRamp[size=32]: [Region 3, Region 1]>]
        >>> my_region_ramp = my_region.region_ramps[0]
        >>> my_region_ramp
        <MDRamp[size=32]: [Region 3, Region 1]>
        >>> # buildable_points is a class! not a list of points, probably needs a rename
        >>> my_region_ramp.buildable_points
        <MapAnalyzer.Polygon.BuildablePoints object at 0x000001B5208DD2C8>
        >>> # you can also see that these buildable points only belong
        >>> # to this specific Polygon, in our case MDRamp
        >>> my_region_ramp.buildable_points.polygon # you can also see that these buildable points only belong to this specific Polygon, in our case MDRamp
        <MDRamp[size=32]: [Region 3, Region 1]>
        >>> # low buildable percent makes sense, most of the ramp's Polygon is not buildable
        >>> my_region_ramp.buildable_points.free_pct # low buildable percent makes sense, most of the ramp's Polygon is not buildable
        0.21875
        >>> # finally,  the buildable points,  which are the ramp wall-off positions
        >>> my_region_ramp.buildable_points.points # finally,  the buildable points,  which are the ramp wall-off positions
        [(146, 26), (141, 30), (143, 23), (145, 24), (144, 23), (140, 29), (146, 25)]
        >>> # lets plot those buildable points
        >>> x,y = zip(*my_region_ramp.buildable_points.points)
        >>> map_data.debugger.scatter(x,y,color="red",marker=r"$\heartsuit$", s=500, edgecolors="r")
        >>> map_data.show()

.. image:: ramp_buildable_raw.png
   :width: 50%

**Hmm, it seems that these points look like they are the upper and lower end of a ramp, lets make sure:**

.. code-block::

        >>> # the perimeter is red by default so we will
        >>> # also,  lets change the heart suit to a simple Star marker and remove the edge color
        >>> map_data.debugger.scatter(x,y,color="purple",marker='*', s=500)
        >>> my_region.plot()
        >>> map_data.show()

.. image:: region_ramp_buildpoints.png
   :width: 75%
