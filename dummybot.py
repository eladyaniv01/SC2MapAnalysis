import random
from typing import List

import sc2
from sc2.player import Bot, Computer
from sc2.position import Point3, Point2

import numpy as np

from MapAnalyzer import MapData

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
        self.sens = 4
        self.hero_tag = None
        self.p0 = None
        self.p1 = None
        self.influence_grid = None
        self.ramp = None
        self.influence_points = None
        self.path = None

    async def on_start(self):
        self.map_data = MapData(self, loglevel="DEBUG", arcade=True)
        self.logger = self.map_data.logger
        base = self.townhalls[0]
        self.base = reg_start = self.map_data.where_all(base.position_tuple)[0]
        reg_end = self.map_data.where_all(self.enemy_start_locations[0].position)[0]
        self.p0 = reg_start.center
        self.p1 = reg_end.center
        self.influence_grid = self.map_data.get_pyastar_grid()
        ramps = reg_end.region_ramps
        self.logger.error(ramps)
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

    def _plot_influence(self, units):
        for unit in units:
            p = unit.position
            r = unit.radius
            h = self.get_terrain_z_height(p)
            pos = Point3((p.x, p.y, h))
            self.client.debug_sphere_out(p=pos, r=r, color=RED)

    def _draw_influence(self, grid: np.ndarray, threshold: int = 1) -> None:
        from math import floor

        def get_height(_x, _y) -> float:
            return (
                    -16
                    + 32 * self.game_info.terrain_height[(floor(_x), floor(_y))] / 255
            )

        for x, y in zip(*np.where(grid > threshold)):
            pos: Point3 = Point3((x, y, get_height(x, y)))
            val: float = grid[x, y]
            color = (201, 168, 79)
            self.client.debug_text_world(str(val), pos, color)

    async def on_step(self, iteration: int):
        # grid = self.map_data.get_pyastar_grid()
        # self.map_data.draw_influence_in_game(grid=grid, lower_threshold=0)
        # self.map_data.logger.error(np.unique(self.map_data.path_arr))
        # points = self.map_data.indices_to_points(np.where(self.map_data.path_arr.T))
        # points = self.map_data.indices_to_points(np.where(self.map_data.placement_arr.T))
        # grid = np.fmax(self.map_data.path_arr, self.map_data.placement_arr).T
        grid = self.map_data.get_pyastar_grid(default_weight=1)
        points = self.map_data.indices_to_points(np.where(grid))
        self._draw_point_list(point_list=points, text='*')
        return
        pass
        # self.map_data.logger.info(iteration)
        # grid = self.map_data.get_air_vs_ground_grid()
        # self._draw_influence(grid=grid)
        # pass
        # nonpathables = self.map_data.bot.structures
        # nonpathables.extend(self.map_data.bot.enemy_structures)
        # nonpathables.extend(self.map_data.mineral_fields)
        # nonpathables.extend(self.map_data.bot.vespene_geyser)
        # destructables_filtered = [d for d in self.map_data.bot.destructables if "plates" not in d.name.lower()]
        # nonpathables.extend(destructables_filtered)
        # self.influence_points = nonpathables
        # self._plot_influence(nonpathables)
        pos = self.map_data.bot.townhalls.ready.first.position
        areas = self.map_data.where_all(pos)
        self.logger.debug(areas)
        region = areas[0]
        self.logger.debug(region)
        self.logger.debug(region.points)
        list_points = list(region.points)
        self.logger.debug(type(list_points))
        self.logger.debug(list_points)
        # self._plot_influence()
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
        self._draw_point_list(self.base.buildables.points, text='*')

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


def main():
    map = "GoldenWallLE"
    map = "GoldenWallLE"
    map = "AbyssalReefLE"
    map = "SubmarineLE"
    map = "DeathAuraLE"
    # map = "aiarena_kingofthehill_1"
    sc2.run_game(
            sc2.maps.get(map),
            [Bot(sc2.Race.Terran, MATester()), Computer(sc2.Race.Zerg, sc2.Difficulty.VeryEasy)],
            realtime=True
    )


if __name__ == "__main__":
    main()
