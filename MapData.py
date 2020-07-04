import numpy as np
from scipy.ndimage import binary_fill_holes, generate_binary_structure, label
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sc2.game_info import GameInfo
from sc2.position import Point2
from Region import Region
from typing import List


class MapData:
    def __init__(self, bot):

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
        self.nonpathable_indices = np.column_stack((nonpathable_indices[0], nonpathable_indices[1]))
        self.mineral_fields = bot.mineral_field
        self.normal_geysers = bot.vespene_geyser
        self.compile_map()

    def compile_map(self):
        grid = binary_fill_holes(self.placement_arr).astype(int)
        # chokes = np.where
        # compiled_grid = grid * (np.abs(scipy.ndimage.laplace(grid)) > 0)
        compiled_grid = grid

        s = generate_binary_structure(2, 2)
        labeled_array, num_features = label(compiled_grid, structure=s)

        rows, cols = labeled_array.shape
        region_grid = np.append(labeled_array, np.zeros((abs(cols - rows), cols)), axis=0)
        regions_labels = np.unique(labeled_array)

        for i in range(len(regions_labels)):
            region = Region(array=np.where(region_grid == i, 1, 0), label=i, map_data=self, map_expansions=self.base_locations)
            self.regions[i] = region
        self.region_grid = region_grid

    def plot_map(self, fontdict=None):
        if not fontdict:
            fontdict = {'family': 'normal',
                        'weight': 'bold',
                        'size': 25}

        values = list(self.regions.keys())

        plt.figure(figsize=(20, 20))
        im = plt.imshow(self.region_grid.T, origin="lower")
        colors = [im.cmap(im.norm(value)) for value in values]

        # create a patch (proxy artist) for every color
        patches = [mpatches.Patch(color=colors[i], label="Region {l}".format(
            l=str(values[i]) + " Size: " + str(self.regions[i].get_area))) for i in range(len(values))]

        # put those patched as legend-handles into the legend
        # plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        for key, value in self.regions.items():
            plt.text(value.polygon.center[0],
                     value.polygon.center[1],
                     value.label,
                     bbox=dict(fill=True, edgecolor='red', linewidth=2),
                     fontdict=fontdict)
        for ramp in self.map_ramps:
            plt.text(ramp.top_center.rounded[1],
                     ramp.top_center.rounded[0],
                     "^",
                     bbox=dict(fill=False, edgecolor='w', linewidth=1),
                     fontdict=fontdict)
            y, x = zip(*ramp.points)
            plt.fill(x, y, color="w")
            plt.scatter(x, y, color="w")

        for vb in self.vision_blockers:
            plt.text(vb[1],
                     vb[0],
                     "X")
        y, x = zip(*self.vision_blockers)
        plt.scatter(x, y, color="r")

        plt.imshow(self.terrain_height.T, alpha=0.9, origin="lower")
        x, y = zip(*self.nonpathable_indices)
        plt.scatter(x, y, color="black")

        for mfield in self.mineral_fields:
            plt.scatter(mfield.position[1], mfield.position[0], color="blue")

        for gasgeyser in self.normal_geysers:
            #         plt.text(gasgeyser.position[1],
            #         gasgeyser.position[0],
            #          "G", color="orange", fontdict=fontdict, )

            plt.scatter(gasgeyser.position[1], gasgeyser.position[0], color="yellow", marker=r'$\spadesuit$', s=500,
                        edgecolors="g")

        plt.show()
