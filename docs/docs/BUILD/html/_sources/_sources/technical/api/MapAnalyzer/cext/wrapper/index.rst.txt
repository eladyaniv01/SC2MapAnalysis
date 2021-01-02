:orphan:

:mod:`MapAnalyzer.cext.wrapper`
===============================

.. py:module:: MapAnalyzer.cext.wrapper


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   MapAnalyzer.cext.wrapper.CMapChoke



.. py:class:: CMapChoke(choke_id, main_line, lines, side1, side2, pixels, min_length)

   CMapChoke holds the choke data coming from c extension
   main_line pair of floats representing the middle points of the sides of the choke
   lines all the lines from side to side
   side1 points on side1
   side2 points on side2
   pixels all the points inside the choke area, should include the sides and the points inside
   min_length minimum distance between the sides of the choke
   id an integer to represent the choke


