import random
from typing import List

import sc2
from sc2.player import Bot, Computer
from sc2.position import Point3, Point2

from loguru import logger

from MapAnalyzer import MapData

GREEN = Point3((0, 255, 0))
RED = Point3((255, 0, 0))
BLUE = Point3((0, 0, 255))
BLACK = Point3((0, 0, 0))


class MATester(sc2.BotAI):

    def __init__(self):
        super().__init__()
        self.map_data = None
        # local settings for easy debug
        self.target = None
        self.base = None
        self.sens = 4
        self.hero_tag = None
        self.p0 = None
        self.p1 = None
        self.influence_grid = None
        self.ramp = None
        self.influence_points = None
        self.path = None
        logger.remove()  # avoid duplicate logging

    async def on_start(self):
        self.map_data = MapData(self, loglevel="DEBUG", arcade=True)

        base = self.townhalls[0]
        self.base = reg_start = self.map_data.where_all(base.position_tuple)[0]
        reg_end = self.map_data.where_all(self.enemy_start_locations[0].position)[0]
        self.p0 = reg_start.center
        self.p1 = reg_end.center
        self.influence_grid = self.map_data.get_pyastar_grid()
        ramps = reg_end.region_ramps
        logger.error(ramps)
        if len(ramps) > 1:
            if self.map_data.distance(ramps[0].top_center, reg_end.center) < self.map_data.distance(ramps[1].top_center,
                                                                                                    reg_end.center):
                self.ramp = ramps[0]
            else:
                self.ramp = ramps[1]
        else:
            self.ramp = ramps[0]

        self.influence_points = [(self.ramp.top_center, 2), (Point2((66, 66)), 18)]

        self.influence_points = self._get_random_influence(25, 5)
        """Uncomment this code block to add random costs and make the path more complex"""
        # for tup in self.influence_points:
        #     p = tup[0]
        #     r = tup[1]
        #     self.map_data.add_cost(p, r=r, arr=self.influence_grid)

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

    def _draw_point_list(self, point_list: List = None, color=None, text=None, box_r=None) -> bool:
        if not color:
            color = GREEN
        h = self.get_terrain_z_height(self.townhalls[0])
        for p in point_list:
            p = Point2(p)

            pos = Point3((p.x, p.y, h))
            if box_r:
                p0 = Point3((pos.x - box_r, pos.y - box_r, pos.z + box_r)) + Point2((0.5, 0.5))
                p1 = Point3((pos.x + box_r, pos.y + box_r, pos.z - box_r)) + Point2((0.5, 0.5))
                self.client.debug_box_out(p0, p1, color=color)
            if text:
                self.client.debug_text_world(
                        "\n".join([f"{text}", ]), pos, color=color, size=30,
                )

    def _draw_path_box(self, p, color):
        h = self.get_terrain_z_height(p)
        pos = Point3((p.x, p.y, h))
        box_r = 1
        p0 = Point3((pos.x - box_r, pos.y - box_r, pos.z + box_r)) + Point2((0.5, 0.5))
        p1 = Point3((pos.x + box_r, pos.y + box_r, pos.z - box_r)) + Point2((0.5, 0.5))
        self.client.debug_box_out(p0, p1, color=color)

    async def on_step(self, iteration: int):

        pos = self.map_data.bot.townhalls.ready.first.position
        areas = self.map_data.where_all(pos)
        # logger.debug(areas) # uncomment this to get the areas of starting position
        region = areas[0]
        # logger.debug(region)
        # logger.debug(region.points)
        list_points = list(region.points)
        logger.debug(type(list_points))  # uncomment this to log the region points Type
        logger.debug(list_points)  # uncomment this to log the region points
        hero = self.workers.by_tag(self.hero_tag)
        dist = 1.5 * hero.calculate_speed() * 1.4
        if self.target is None:
            self.target = self.path.pop(0)
        logger.info(f"Distance to next step : {self.map_data.distance(hero.position, self.target)}")
        if self.map_data.distance(hero.position, self.target) > 1:
            hero.move(self.target)

        if self.map_data.distance(hero.position, self.target) <= dist:
            if len(self.path) > 0:
                self.target = self.path.pop(0)
            else:
                logger.info("Path Complete")

        self._draw_path_box(p=hero.position, color=GREEN)  # draw scouting SCV position
        self._draw_path_box(p=self.target, color=RED)  # draw scouting SCV next move point in the path

        self.client.debug_text_world(
                "\n".join([f"start {self.p0}", ]), Point2(self.p0), color=BLUE, size=30,
        )
        self.client.debug_text_world(
                "\n".join([f"end {self.p1}", ]), Point2(self.p1), color=RED, size=30,
        )

        """
        Drawing Buildable points of our home base ( Region ) 
        Feel free to try lifting the Command Center,  or building structures to see how it updates
        """
        self._draw_point_list(self.base.buildables.points, text='*')

        """
        Drawing the path for our scouting SCV  from our base to enemy's Main
        """
        self._draw_point_list(self.path, text='*', color=RED)


def main():
    map = "DeathAuraLE"
    sc2.run_game(
            sc2.maps.get(map),
            [Bot(sc2.Race.Terran, MATester()), Computer(sc2.Race.Zerg, sc2.Difficulty.VeryEasy)],
            realtime=True
    )


if __name__ == "__main__":
    main()
