from typing import List

import sc2
from sc2.player import Bot, Computer
from sc2.position import Point3

from MapAnalyzer import MapData, Point2

GREEN = Point3((0, 255, 0))
RED = Point3((255, 0, 0))
BLUE = Point3((0, 0, 255))
BLACK = Point3((0, 0, 0))


class MATester(sc2.BotAI):

    def __init__(self):
        super().__init__()
        self.map_data = None
        self.logger = None

    async def on_start(self):
        self.map_data = MapData(self)
        self.logger = self.map_data.logger

    async def on_step(self, iteration: int):
        # enemy_ground_units = enemies.filter(
        #         lambda unit: unit.distance_to(r) < 5 and not unit.is_flying

        base = self.townhalls[0]
        reg_start = self.map_data.where(base.position_tuple)
        # self.logger.info(regstart)
        reg_end = self.map_data.where(self.enemy_start_locations[0].position)
        # self.logger.info(regend)
        p0 = reg_start.center
        p1 = reg_end.center
        path = self.map_data.pathfind(start=p0, goal=p1)
        self.client.debug_text_world(
                "\n".join([f"start {p0}", ]), Point2(p0), color=RED, size=30,
        )
        self.client.debug_text_world(
                "\n".join([f"end {p1}", ]), Point2(p1), color=RED, size=30,
        )
        self._draw_point_list(path, text='*')

    def _draw_point_list(self, point_list: List = None, color=None, text=None, box_r=None) -> bool:
        if not color:
            color = GREEN
        for p in point_list:
            p = Point2(p)
            h = self.get_terrain_z_height(p)
            pos = Point3((p.x, p.y, h))
            if box_r:
                p0 = Point3((pos.x - box_r, pos.y - box_r, pos.z + box_r)) + Point2((0.5, 0.5))
                p1 = Point3((pos.x + box_r, pos.y + box_r, pos.z - box_r)) + Point2((0.5, 0.5))
                self.client.debug_box_out(p0, p1, color=color)
            if text:
                self.client.debug_text_world(
                        "\n".join([f"{text}", ]), pos, color=color, size=30,
                )


def main():
    map = "AutomatonLE"
    sc2.run_game(
            sc2.maps.get(map),
            [Bot(sc2.Race.Terran, MATester()), Computer(sc2.Race.Zerg, sc2.Difficulty.VeryEasy)],
            realtime=False
    )


if __name__ == "__main__":
    main()
