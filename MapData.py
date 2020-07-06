import matplotlib.pyplot as plt
import numpy as np
from sc2 import BotAI
from scipy.ndimage import binary_fill_holes, generate_binary_structure, label as ndlabel
from scipy.spatial import distance

from constants import MIN_REGION_AREA, BINARY_STRUCTURE, MAX_REGION_AREA
from Region import Region


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
        self.map_ramps = bot.game_info.map_ramps
        self.terrain_height = bot.game_info.terrain_height.data_numpy
        self.vision_blockers = bot.game_info.vision_blockers
        self.region_grid = None
        self.regions = {}
        nonpathable_indices = np.where(bot.game_info.pathing_grid.data_numpy == 0)
        self.nonpathable_indices = np.column_stack((nonpathable_indices[1], nonpathable_indices[0]))
        self.mineral_fields = bot.mineral_field
        self.normal_geysers = bot.vespene_geyser
        self.compile_map()  # this is called on init, but allowed to be called again every step

    def closest_node_idx(self, node, nodes):
        closest_index = distance.cdist([node], nodes).argmin()
        return closest_index



    def compile_map(self):
        # cleaning the grid and then searching for 2x2 patterned regions
        grid = binary_fill_holes(self.placement_arr).astype(int)
        s = generate_binary_structure(BINARY_STRUCTURE, BINARY_STRUCTURE)
        labeled_array, num_features = ndlabel(grid, structure=s)

        # for some operations the array must have same numbers or rows and cols,  adding
        # zeros to fix that
        rows, cols = labeled_array.shape
        region_grid = np.append(labeled_array, np.zeros((abs(cols - rows), cols)), axis=0)
        regions_labels = np.unique(labeled_array)

        # some regions are with area of 1, 2 ,5   these are not what we want,
        # so we filter those out
        pre_regions = {}
        for i in range(len(regions_labels)):
            region = Region(array=np.where(region_grid == i, 1, 0), label=i, map_data=self,
                            map_expansions=self.base_locations)
            pre_regions[i] = region

        # gather the regions that are bigger than 50 cells
        i = 0
        for region in pre_regions.values():
            if self.max_region_area > region.get_area > self.min_region_area:
                region.label = i
                self.regions[i] = region
                ramp_nodes = [ramp.top_center for ramp in self.map_ramps]
                perimeter_nodes = region.polygon.perimeter[:, [1, 0]]
                result_ramp_indexes = []
                for n in perimeter_nodes:
                    result_ramp_indexes.append(self.closest_node_idx(n, ramp_nodes))
                result_ramp_indexes = list(set(result_ramp_indexes))
                for rn in result_ramp_indexes:
                    ramp = [r for r in self.map_ramps if r.top_center == ramp_nodes[rn]]
                    region.region_ramps.append(ramp[0])
                i += 1

        self.region_grid = region_grid

    def plot_map(self, fontdict: dict = None):

        plt.style.use('ggplot')
        if not fontdict:
            fontdict = {'family': 'normal',
                        'weight': 'bold',
                        'size': 25}

        # colormap for regions
        values = list(self.regions.keys())
        plt.figure(figsize=(20, 20))
        im = plt.imshow(self.region_grid, origin="lower")
        colors = [im.cmap(im.norm(value)) for value in values]

        for key, value in self.regions.items():
            if value.label == 0:
                continue

            print(len(value.region_ramps))
            plt.text(value.polygon.center[0],
                     value.polygon.center[1],
                     value.label,
                     bbox=dict(fill=True, alpha=0.5, edgecolor='red', linewidth=2),
                     fontdict=fontdict)
            if value.label:
                for ramp in value.region_ramps:
                    ramp = ramp
                    plt.text(ramp.top_center[0],
                             ramp.top_center[1],
                             f"{value.label} : {ramp.top_center.rounded[0]}, {ramp.top_center.rounded[1]}",
                             bbox=dict(fill=True, alpha=0.3, edgecolor='red', linewidth=8),
                             )
        # for ramp in self.map_ramps:
        #     plt.text(ramp.top_center.rounded[0],
        #              ramp.top_center.rounded[1],
        #              f"{ramp.top_center.rounded[0]}, {ramp.top_center.rounded[1]}",
        #              bbox=dict(fill=False, edgecolor='w', linewidth=1),
        #              fontdict=fontdict)
        # x, y = zip(*ramp.points)
        # # plt.fill(x, y, color="w")
        # plt.scatter(x, y, color="w")

        for vb in self.vision_blockers:
            plt.text(vb[0],
                     vb[1],
                     "X")
        x, y = zip(*self.vision_blockers)
        plt.scatter(x, y, color="r")

        plt.imshow(self.terrain_height, alpha=1, origin="lower", cmap='terrain')
        x, y = zip(*self.nonpathable_indices)
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
