import numpy as np


class Area:
    def __init__(self):
        pass


class MDRamp(Area):
    def __init__(self, ramp):
        self.regions = []
        self.ramp = ramp
        super().__init__()

    @property
    def top_center(self):
        return self.ramp.top_center

    @property
    def indices(self):
        points = self.ramp.points
        return np.column_stack(
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
