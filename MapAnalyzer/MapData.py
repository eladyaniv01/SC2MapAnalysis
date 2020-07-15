from typing import Union, Tuple

import numpy as np
from sc2 import BotAI
from sc2.position import Point2
from scipy.ndimage import binary_fill_holes, generate_binary_structure, label as ndlabel
from scipy.spatial import distance

from MapAnalyzer.constants import MIN_REGION_AREA, BINARY_STRUCTURE, MAX_REGION_AREA
from MapAnalyzer.constructs import MDRamp, VisionBlockerArea, ChokeArea
from MapAnalyzer.Region import Region
from .sc2pathlibp import Sc2Map


class MapData:
    """
    MapData DocString
    """
    def __init__(self, bot: BotAI):
        self.min_region_area = MIN_REGION_AREA
        self.max_region_area = MAX_REGION_AREA
        # store relevant data from bot instance for later use
        self.bot = bot
        self.map_name = bot.game_info.map_name
        self.placement_arr = bot.game_info.placement_grid.data_numpy
        self.path_arr = bot.game_info.pathing_grid.data_numpy
        self.base_locations = bot.expansion_locations_list
        self.map_ramps = [MDRamp(map_data=self, ramp=r, array=self.points_to_numpy_array(r.points))
                          for r in self.bot.game_info.map_ramps]
        self.terrain_height = bot.game_info.terrain_height.data_numpy
        self._vision_blockers = bot.game_info.vision_blockers
        self.map_chokes = []  # set later  on compile
        self.map_vision_blockers = []  # set later  on compile
        self.vision_blockers_labels = []  # set later  on compile
        self.vision_blockers_grid = []  # set later  on compile
        self.region_grid = None
        self.regions = {}
        nonpathable_indices = np.where(bot.game_info.pathing_grid.data_numpy == 0)
        self.nonpathable_indices_stacked = np.column_stack((nonpathable_indices[1], nonpathable_indices[0]))
        self.mineral_fields = bot.mineral_field
        self.normal_geysers = bot.vespene_geyser
        self.pathlib_map = None
        self._get_pathlib_map()
        self.compile_map()  # this is called on init, but allowed to be called again every step

    def save_plot(self):
        """
        Will save the plot to a file names after the map name

        :return: None

        """
        self.plot_map(save=True)

    def _get_pathlib_map(self):
        """
        Will initialize the sc2pathlib `SC2Map` object for future use
        :return: None

        """
        self.pathlib_map = Sc2Map(
            self.path_arr,
            self.placement_arr,
            self.terrain_height,
            self.bot.game_info.playable_area,
        )

    def where_all(self, point: Union[Point2, Tuple]):
        """
        region query 21.5 µs ± 652 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
        choke query 18 µs ± 1.25 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        ramp query  22 µs ± 982 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
        :param point:
        :type point:
        :return:
        :rtype:
        """
        results = []
        if isinstance(point, Point2):
            point = point.rounded
        if isinstance(point, Tuple):
            point = int(point[0]), int(point[1])

        for region in self.regions.values():
            if region.inside_p(point):
                results.append(region)
        for ramp in self.map_ramps:
            if ramp.is_inside_point(point):
                results.append(ramp)
        for vba in self.map_vision_blockers:
            if vba.is_inside_point(point):
                results.append(vba)
        return results

    def where(self, point: Union[Point2, Tuple]):
        """
        region query 7.09 µs ± 329 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        choke query  17.9 µs ± 1.22 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        ramp query 11.7 µs ± 1.13 µs per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        :param point:
        :type point:
        :return:
        :rtype:
        """
        if isinstance(point, Point2):
            point = point.rounded
        if isinstance(point, Tuple):
            point = int(point[0]), int(point[1])

        for region in self.regions.values():
            if region.inside_p(point):
                return region
        for ramp in self.map_ramps:
            if ramp.is_inside_point(point):
                return ramp
        for vba in self.map_vision_blockers:

            if vba.is_inside_point(point):
                return vba

    def in_region_p(self, point: Union[Point2, Tuple]):
        """
        time benchmark 4.35 µs ± 27.5 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        as long as polygon points is of type set, not list
        :param point:
        :type point: :class:`sc2.position.Point2` / Tuple
        :return: :class:`Region` object, or None
        :rtype:
        """
        if isinstance(point, Point2):
            point = point.rounded
        if isinstance(point, Tuple):
            point = int(point[0]), int(point[1])
        for region in self.regions.values():
            if region.inside_p(point):
                return region

    def in_region_i(self, point: Union[Point2, Tuple]):
        """
        time benchmark 18.6 µs ± 197 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
        :param point:
        :type point: :class:`sc2.position.Point2` / Tuple
        :return: :class:`Region` object, or None
        :rtype:
        """
        if isinstance(point, Point2):
            point = point.rounded
        if isinstance(point, Tuple):
            point = int(point[0]), int(point[1])
        for region in self.regions.values():
            if region.inside_i(point):
                return region

    @staticmethod
    def indices_to_points(indices):
        return set([(indices[0][i], indices[1][i]) for i in range(len(indices[0]))])

    @staticmethod
    def points_to_indices(points):
        return (
            (np.array(
                [p[0] for p in points]),
             np.array(
                 [p[1] for p in points])
            )
        )

    def points_to_numpy_array(self, points):
        rows, cols = self.path_arr.shape
        arr = np.zeros((rows, cols), dtype=np.uint8)
        for p in points:
            arr[p] = 1
        return arr

    @staticmethod
    def _distance(p1, p2):
        return abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])

    @staticmethod
    def _closest_node_idx(node, nodes):
        closest_index = distance.cdist([node], nodes).argmin()
        return closest_index

    @staticmethod
    def _clean_ramps(region):
        to_remove = []
        for mramp in region.region_ramps:
            if len(mramp.regions) < 2:
                to_remove.append(mramp)
        for mramp in to_remove:
            region.region_ramps.remove(mramp)

    def _calc_grid(self):
        # cleaning the grid and then searching for 2x2 patterned regions
        grid = binary_fill_holes(self.placement_arr).astype(int)

        s = generate_binary_structure(BINARY_STRUCTURE, BINARY_STRUCTURE)
        labeled_array, num_features = ndlabel(grid, structure=s)

        # for some operations the array must have same numbers or rows and cols,  adding
        # zeros to fix that
        # rows, cols = labeled_array.shape
        # self.region_grid = np.append(labeled_array, np.zeros((abs(cols - rows), cols)), axis=0)
        self.region_grid = labeled_array.astype(int)
        self.regions_labels = np.unique(self.region_grid)
        points = self._vision_blockers

        if len(points):
            vision_blockers_indices = ((np.array([p[0] for p in points]),
                                        np.array([p[1] for p in points])))
            vision_blockers_array = np.zeros(self.region_grid.shape, dtype='int')
            vision_blockers_array[vision_blockers_indices] = 1
            vb_labeled_array, vb_num_features = ndlabel(vision_blockers_array)
            self.vision_blockers_grid = vb_labeled_array
            self.vision_blockers_labels = np.unique(vb_labeled_array)

    def _calc_ramps(self, region, i):
        ramp_nodes = [ramp.center for ramp in self.map_ramps]
        perimeter_nodes = region.polygon.perimeter
        result_ramp_indexes = list(set([self._closest_node_idx(n, ramp_nodes) for n in perimeter_nodes]))
        for rn in result_ramp_indexes:
            # and distance from perimeter is less than ?
            ramp = [r for r in self.map_ramps if r.center == ramp_nodes[rn]][0]
            """for ramp in map ramps  if ramp exists,  append the region if not,  create new one"""
            if region not in ramp.regions:
                ramp.regions.append(region)
            region.region_ramps.append(ramp)
        li = []

        for ramp in region.region_ramps:
            for p in region.polygon.perimeter:
                if self._distance(p, ramp.bottom_center) < 8 or self._distance(p, ramp.top_center) < 8:
                    li.append(ramp)
        li = list(set(li))
        for ramp in region.region_ramps:
            if ramp not in li:
                region.region_ramps.remove(ramp)
                ramp.regions.remove(region)
        region.region_ramps = list(set(region.region_ramps))
        self._clean_ramps(region)

    def _calc_vision_blockers(self):
        for i in range(len(self.vision_blockers_labels)):
            indices = np.where(self.vision_blockers_grid == i)
            points = self.indices_to_points(indices)
            vb_arr = self.points_to_numpy_array(points)
            if len(indices[0]):
                vba = VisionBlockerArea(map_data=self, array=vb_arr)
                region = self.in_region_p(vba.center)

                if region and 5 < vba.area < 200:
                    vba.regions.append(region)
                    region.region_vision_blockers.append(vba)
                self.map_vision_blockers.append(vba)

    def _calc_chokes(self):
        chokes = self.pathlib_map.chokes
        for choke in chokes:
            points = [Point2(p) for p in choke.pixels]
            if len(points) > 0:
                new_choke_array = self.points_to_numpy_array(points)
                new_choke = ChokeArea(map_data=self, array=new_choke_array, main_line=choke.main_line)
                region = self.in_region_p(new_choke.center)
                if region:
                    region.region_chokes.append(new_choke)
                    new_choke.regions.append(region)
                if region is None and self.where(new_choke.center) is None:
                    print(
                        f"<{self.bot.game_info.map_name}>: please report bug no region found for choke area with center {new_choke.center}")
                self.map_chokes.append(new_choke)

    def _calc_regions(self):
        # some regions are with area of 1, 2 ,5   these are not what we want,
        # so we filter those out
        pre_regions = {}
        for i in range(len(self.regions_labels)):
            region = Region(array=np.where(self.region_grid == i, 1, 0).T, label=i, map_data=self,
                            map_expansions=self.base_locations)
            pre_regions[i] = region
            # gather the regions that are bigger than self.min_region_area
        j = 0
        for region in pre_regions.values():
            if self.max_region_area > region.get_area > self.min_region_area:
                region.label = j
                self.regions[j] = region
                self._calc_ramps(region=region, i=j)
                j += 1

    def compile_map(self):
        self._calc_grid()
        self._calc_regions()
        self._calc_vision_blockers()
        self._calc_chokes()

    def plot_map(self, fontdict: dict = None, save=False, figsize=20):
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')
        if not fontdict:
            fontdict = {'family': 'serif',
                        'weight': 'bold',
                        'size': 25}

        plt.figure(figsize=(figsize, figsize))
        plt.imshow(self.region_grid, origin="lower")


        for lbl, reg in self.regions.items():
            # flipping the axes,  needs debugging
            plt.text(reg.center[0],
                     reg.center[1],
                     reg.label,
                     bbox=dict(fill=True, alpha=0.5, edgecolor='red', linewidth=2),
                     fontdict=fontdict)
            # random color for each perimeter
            x, y = zip(*reg.polygon.perimeter)
            plt.scatter(x, y, cmap="accent", marker="1", s=300)
            for corner in reg.polygon.corner_points:
                plt.scatter(corner[0],
                            corner[1],
                            marker="v",
                            c='red',
                            s=150)

        for ramp in self.map_ramps:
            plt.text(ramp.top_center[0],
                     ramp.top_center[1],
                     f"R<{[r.label for r in set(ramp.regions)]}>",
                     bbox=dict(fill=True, alpha=0.3, edgecolor='cyan', linewidth=8),
                     )
            x, y = zip(*ramp.points)
            plt.scatter(x, y, color="w")
        # some maps has no vision blockers
        if len(self._vision_blockers) > 0:
            for vb in self._vision_blockers:
                plt.text(vb[0],
                         vb[1],
                         "X")

            x, y = zip(*self._vision_blockers)
            plt.scatter(x, y, color="r")

        plt.imshow(self.terrain_height, alpha=1, origin="lower", cmap='terrain')
        x, y = zip(*self.nonpathable_indices_stacked)
        plt.scatter(x, y, color="grey")

        for mfield in self.mineral_fields:
            plt.scatter(mfield.position[0], mfield.position[1], color="blue")

        for gasgeyser in self.normal_geysers:
            plt.scatter(gasgeyser.position[0], gasgeyser.position[1], color="yellow", marker=r'$\spadesuit$', s=500,
                        edgecolors="g")

        for choke in self.map_chokes:
            x, y = zip(*choke.points)
            plt.scatter(x, y, marker=r'$\heartsuit$', s=100,
                        edgecolors="g")
        fontsize = 14
        ax = plt.gca()

        for tick in ax.xaxis.get_major_ticks():
            tick.label1.set_fontsize(fontsize)
            tick.label1.set_fontweight('bold')
        for tick in ax.yaxis.get_major_ticks():
            tick.label1.set_fontsize(fontsize)
            tick.label1.set_fontweight('bold')

        plt.grid()
        if save:
            map_name = self.bot.game_info.map_name
            plt.savefig(f'{map_name}.png')
            plt.close()
        else:
            plt.show()
