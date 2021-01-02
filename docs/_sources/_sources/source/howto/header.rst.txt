.. important::
        **Recipe Terminology:**

            * ``self``  = :class:`sc2.bot_ai.BotAI`
            * ``map_data`` = :class:`.MapData`

        **PathFinding Terminology:**

            * ``cost`` : How much is it going to cost the pather to walk through this cell
            * ``weight_array`` : a finalized grid(with added cost) passed to plotting

        * the optimal cost will be 1,
        * the worst cost would be  :data:`numpy.inf` (for non pathable cells)

        **you should keep that in mind if you want to create a complex influence map with different weights**


        **Be sure to check out** :data:`dummybot.py` **for example bot usage with some handy debug methods**
