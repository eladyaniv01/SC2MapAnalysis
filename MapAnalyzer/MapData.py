from typing import Union, Tuple

import numpy as np
from sc2 import BotAI
from sc2.position import Point2
from scipy.ndimage import binary_fill_holes, generate_binary_structure, label as ndlabel
from scipy.spatial import distance

from MapAnalyzer.constants import MIN_REGION_AREA, BINARY_STRUCTURE, MAX_REGION_AREA
from MapAnalyzer.constructs import MDRamp
from MapAnalyzer.Region import Region


# todo - assert that all ramps are accounted for
class MapData:
    def __init__(self, bot: BotAI):
        self.min_region_area = MIN_REGION_AREA
        self.max_region_area = MAX_REGION_AREA
        # store relevant data from bot instance for later use
        self.bot = bot
        self.map_name = bot.game_info.map_name
        self.placement_arr = bot.game_info.placement_grid.data_numpy
        self.path_arr = bot.game_info.pathing_grid.data_numpy
        self.base_locations = bot.expansion_locations_list
        self.map_ramps = [MDRamp(self, r) for r in bot.game_info.map_ramps]
        self.terrain_height = bot.game_info.terrain_height.data_numpy
        self.vision_blockers = bot.game_info.vision_blockers
        self.region_grid = None
        self.regions = {}
        nonpathable_indices = np.where(bot.game_info.pathing_grid.data_numpy == 0)
        self.nonpathable_indices_stacked = np.column_stack((nonpathable_indices[1], nonpathable_indices[0]))
        self.mineral_fields = bot.mineral_field
        self.normal_geysers = bot.vespene_geyser
        self.compile_map()  # this is called on init, but allowed to be called again every step


    def in_region(self, point: Union[Point2, Tuple]):
        if isinstance(point, Point2):
            point = point.rounded
        if isinstance(point, Tuple):
            point = int(point[0]), int(point[1])
        for region in self.regions.values():
            if region.inside(point):
                return region

    def _distance(self, p1, p2):
        return abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])

    def _closest_node_idx(self, node, nodes):
        closest_index = distance.cdist([node], nodes).argmin()
        return closest_index

    def _clean_ramps(self, region):
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
        rows, cols = labeled_array.shape
        self.region_grid = np.append(labeled_array, np.zeros((abs(cols - rows), cols)), axis=0)
        self.regions_labels = np.unique(labeled_array)

    def _calc_ramps(self, region, i):
        ramp_nodes = [ramp.top_center for ramp in self.map_ramps]
        perimeter_nodes = region.polygon.perimeter

        result_ramp_indexes = []
        for n in perimeter_nodes:
            result_ramp_indexes.append(self._closest_node_idx(n, ramp_nodes))
        result_ramp_indexes = list(set(result_ramp_indexes))
        for rn in result_ramp_indexes:
            # and distance from perimeter is less than ?
            ramp = [r for r in self.map_ramps if r.top_center == ramp_nodes[rn]][0]
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

    def _calc_regions(self):
        # some regions are with area of 1, 2 ,5   these are not what we want,
        # so we filter those out
        pre_regions = {}
        for i in range(len(self.regions_labels)):
            region = Region(array=np.where(self.region_grid == i, 1, 0), label=i, map_data=self,
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

    def plot_map(self, fontdict: dict = None):
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')
        if not fontdict:
            fontdict = {'family': 'serif',
                        'weight': 'bold',
                        'size': 25}

        # colormap for regions
        values = list(self.regions.keys())
        plt.figure(figsize=(20, 20))
        im = plt.imshow(self.region_grid, origin="lower")
        colors = [im.cmap(im.norm(value)) for value in values]

        for lbl, reg in self.regions.items():
            plt.text(reg.polygon.center[0],
                     reg.polygon.center[1],
                     reg.label,
                     bbox=dict(fill=True, alpha=0.5, edgecolor='red', linewidth=2),
                     fontdict=fontdict)

        for ramp in self.map_ramps:
            plt.text(ramp.top_center[0],
                     ramp.top_center[1],
                     f"R<{[r.label for r in set(ramp.regions)]}>",
                     bbox=dict(fill=True, alpha=0.3, edgecolor='cyan', linewidth=8),
                     )
            x, y = zip(ramp.indices)
            # plt.fill(x, y, color="w")
            plt.scatter(x, y, color="w")

        for vb in self.vision_blockers:
            plt.text(vb[0],
                     vb[1],
                     "X")
        x, y = zip(*self.vision_blockers)
        plt.scatter(x, y, color="r")

        plt.imshow(self.terrain_height, alpha=1, origin="lower", cmap='terrain')
        x, y = zip(*self.nonpathable_indices_stacked)
        plt.scatter(x, y, color="grey")

        for mfield in self.mineral_fields:
            plt.scatter(mfield.position[0], mfield.position[1], color="blue")

        for gasgeyser in self.normal_geysers:
            #         plt.text(gasgeyser.position[1],
            #         gasgeyser.position[0],
            #          "G", color="orange", fontdict=fontdict, )

            plt.scatter(gasgeyser.position[0], gasgeyser.position[1], color="yellow", marker=r'$\spadesuit$', s=500,
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
        plt.show()

