import numpy as np
from scipy.ndimage import center_of_mass

class Area:
    def __init__(self):
        pass


class MDRamp(Area):
    def __init__(self, map_data, ramp):
        self.regions = []
        self.ramp = ramp
        self.map_data = map_data
        super().__init__()

    @property
    def array(self):
        mask = np.zeros(self.map_data.region_grid.shape, dtype='int')
        mask[self.indices] = 1
        return mask

    @property
    def center(self):
        cm = center_of_mass(self.array)
        return np.int(cm[1]), np.int(cm[0])

    @property
    def top_center(self):
        return self.ramp.top_center

    @property
    def indices(self):
        points = self.ramp.points
        return (
            (np.array(
                [p[0] for p in points]),
             np.array(
                 [p[1] for p in points])
            )
        )

    def __repr__(self):
        return f'MDRamp{self.ramp} of {self.regions}'


class VisionBlockerArea(Area):
    def __init__(self, indices, regions):
        self.regions = regions
        self.indices = indices

    @property
    def area(self):
        return len(self.indices)

    def __repr__(self):
        return f'<VisionBlockerArea;{self.area}> of {[r for r in self.regions]}'


class ChokeArea(MDRamp, VisionBlockerArea):
    def __init__(self, regions, ramp=None, vision_blocker=None):
        self.regions = regions
        self.ramp = ramp
        self.vision_blocker = vision_blocker

    @property
    def is_ramp(self):
        return self.ramp is not None

    @property
    def is_vision_blocker(self):
        return self.vision_blocker is not None
