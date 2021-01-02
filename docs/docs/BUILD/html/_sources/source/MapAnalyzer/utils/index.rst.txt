:orphan:

:mod:`MapAnalyzer.utils`
========================

.. py:module:: MapAnalyzer.utils


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   MapAnalyzer.utils.change_destructable_status_in_grid
   MapAnalyzer.utils.fix_map_ramps
   MapAnalyzer.utils.import_bot_instance
   MapAnalyzer.utils.get_map_file_list


.. function:: change_destructable_status_in_grid(grid: np.ndarray, unit: Unit, status: int)

   Set destructable positions to status, modifies the grid in place


.. function:: fix_map_ramps(bot: BotAI)

   following https://github.com/BurnySc2/python-sc2/blob/ffb9bd43dcbeb923d848558945a8c59c9662f435/sc2/game_info.py#L246
   to fix burnysc2 ramp objects by removing destructables


.. function:: import_bot_instance(raw_game_data: Response, raw_game_info: Response, raw_observation: ResponseObservation) -> BotAI

   import_bot_instance DocString


.. function:: get_map_file_list() -> List[str]

   easy way to produce less than all maps,  for example if we want to test utils, we only need one MapData object


