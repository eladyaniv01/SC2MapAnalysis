import random
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

        # local settings for easy debug
        self.target = None
        self.sens = 1
        self.hero_tag = None
        self.p0 = None
        self.p1 = None
        self.influence_grid = None
        self.ramp = None
        self.influence_points = None
        self.path = None

    async def on_start(self):
        self.map_data = MapData(self)
        self.logger = self.map_data.logger
        base = self.townhalls[0]
        reg_start = self.map_data.where(base.position_tuple)
        reg_end = self.map_data.where(self.enemy_start_locations[0].position)
        self.p0 = reg_start.center
        self.p1 = reg_end.center
        self.influence_grid = self.map_data.get_pyastar_grid()
        ramps = reg_end.region_ramps
        # self.logger.error(ramps)
        if len(ramps) > 1:
            if self.map_data.distance(ramps[0].top_center, reg_end.center) < self.map_data.distance(ramps[1].top_center,
                                                                                                    reg_end.center):
                self.ramp = ramps[0]
            else:
                self.ramp = ramps[1]
        else:
            self.ramp = ramps[0]

        # self.influence_points = [(self.ramp.top_center, 2), (Point2((66, 66)), 18)]

        self.influence_points = self._get_random_influence(25, 5)
        for tup in self.influence_points:
            p = tup[0]
            r = tup[1]
            self.map_data.add_influence(p, r=r, arr=self.influence_grid)
        self.path = self.map_data.pathfind(start=self.p0, goal=self.p1, grid=self.influence_grid, sensitivity=self.sens,
                                           allow_diagonal=True)
        self.hero_tag = self.workers[0].tag

    def get_random_point(self, minx, maxx, miny, maxy):
        return (random.randint(minx, maxx), random.randint(miny, maxy))

    def _get_random_influence(self, n, r):
        pts = []
        for i in range(n):
            pts.append(
                    (Point2(self.get_random_point(50, 130, 25, 175)), r))
        return pts

    def _plot_influence(self):
        for tup in self.influence_points:
            p = tup[0]
            r = tup[1]
            h = self.get_terrain_z_height(p)
            pos = Point3((p.x, p.y, h))
            self.client.debug_sphere_out(p=pos, r=r - 1, color=RED)

    async def on_step(self, iteration: int):
        self._plot_influence()
        hero = self.workers.by_tag(self.hero_tag)
        dist = 1.5 * hero.calculate_speed() * 1.4
        if self.target is None:
            self.target = self.path.pop(0)
        self.logger.info(f"Distance to next step : {self.map_data.distance(hero.position, self.target)}")
        if self.map_data.distance(hero.position, self.target) > 1:
            hero.move(self.target)

        if self.map_data.distance(hero.position, self.target) <= dist:
            if len(self.path) > 0:
                self.target = self.path.pop(0)
            else:
                self.logger.info("Path Complete")

        p = hero.position
        h = self.get_terrain_z_height(p)
        pos = Point3((p.x, p.y, h))
        box_r = 1
        color = GREEN
        p0 = Point3((pos.x - box_r, pos.y - box_r, pos.z + box_r)) + Point2((0.5, 0.5))
        p1 = Point3((pos.x + box_r, pos.y + box_r, pos.z - box_r)) + Point2((0.5, 0.5))
        self.client.debug_box_out(p0, p1, color=color)

        p = self.target
        h = self.get_terrain_z_height(p)
        pos = Point3((p.x, p.y, h))
        box_r = 1
        color = RED
        p0 = Point3((pos.x - box_r, pos.y - box_r, pos.z + box_r)) + Point2((0.5, 0.5))
        p1 = Point3((pos.x + box_r, pos.y + box_r, pos.z - box_r)) + Point2((0.5, 0.5))
        self.client.debug_box_out(p0, p1, color=color)

        self.client.debug_text_world(
                "\n".join([f"start {self.p0}", ]), Point2(self.p0), color=BLUE, size=30,
        )
        self.client.debug_text_world(
                "\n".join([f"end {self.p1}", ]), Point2(self.p1), color=RED, size=30,
        )
        self._draw_point_list(self.path, text='*')

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
    map = "AbyssalReefLE"
    sc2.run_game(
            sc2.maps.get(map),
            [Bot(sc2.Race.Terran, MATester()), Computer(sc2.Race.Zerg, sc2.Difficulty.VeryEasy)],
            realtime=False
    )


if __name__ == "__main__":
    main()
