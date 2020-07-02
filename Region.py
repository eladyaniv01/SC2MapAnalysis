from Polygon import Polygon
import matplotlib.pyplot as plt

class Region:
    def __init__(self, array, label):
        self.array = array
        self.label = label
        self.polygon = Polygon(self)

    def plot_perimeter(self):
        x, y = zip(*self.polygon.perimeter)
        plt.scatter(x, y)
        plt.title(f"Region {self.label}")
        plt.show()

    @property
    def choke_points(self):
        pass

    @property
    def base_locations(self):
        pass

    @property
    def is_reachable(self, region):  # is connected to another region directly ?
        pass

    @property
    def get_reachable_regions(self):
        pass

    @property
    def get_area(self):
        return self.polygon.area

    def __repr__(self):
        return "Region " + str(self.label)

