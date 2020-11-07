from functools import lru_cache
from typing import Optional, TYPE_CHECKING

import numpy as np
from loguru import logger
from sc2.game_info import Ramp as sc2Ramp
from sc2.position import Point2

from .Polygon import Polygon

if TYPE_CHECKING:  # pragma: no cover
    from .MapData import MapData
    from .sc2pathlibp.choke import Choke


class PathLibChoke:
    """

    wrapper to the data returned by :mod:`.sc2pathlibp`

    with a bit of added fields / data type for convenience

    """

    # noinspection PyProtectedMember
    def __init__(self, pathlib_choke: "Choke", pk: int):
        self.id = pk
        self.pixels = set(pathlib_choke.pixels)
        self.main_line = pathlib_choke.pixels
        self.pathlib_choke = pathlib_choke

    def __repr__(self) -> str:
        return f"[{self.id}]PathLibChoke; {len(self.pixels)}"


class ChokeArea(Polygon):
    """

    Base class for all chokes

    """

    def __init__(
            self, array: np.ndarray, map_data: "MapData", pathlibchoke: Optional[PathLibChoke] = None
    ) -> None:
        super().__init__(map_data=map_data, array=array)
        self.main_line = None
        self.id = 'Unregistered'
        self.md_pl_choke = None
        if pathlibchoke:
            self.main_line = pathlibchoke.main_line
            self.id = pathlibchoke.id
            self.md_pl_choke = pathlibchoke
        self.is_choke = True
        self.ramp = None

    @property
    def left(self):
        return min(self.points)

    @property
    def right(self):
        return max(self.points)

    @property
    def corner_walloff(self):
        return sorted(list(self.points), key=lambda x: x.distance_to_point2(self.center), reverse=True)[:2]

    @lru_cache()
    def same_height(self, p1, p2):
        return self.map_data.terrain_height[p1] == self.map_data.terrain_height[p2]

    def __repr__(self) -> str:  # pragma: no cover
        return f"<[{self.id}]ChokeArea[size={self.area}]>"


class MDRamp(ChokeArea):
    """

    Wrapper for :class:`sc2.game_info.Ramp`,

    is responsible for calculating the relevant :class:`.Region`
    """

    def __init__(self, map_data: "MapData", array: np.ndarray, ramp: sc2Ramp) -> None:
        super().__init__(map_data=map_data, array=array)
        self.is_ramp = True
        self.ramp = ramp
        self.x_offset = 0.5
        self.y_offset = 0.5

    @property
    def corner_walloff(self):
        raw_points = sorted(list(self.points), key=lambda x: x.distance_to_point2(self.bottom_center), reverse=True)[:2]
        offset_points = [p.offset((self.x_offset, self.y_offset)) for p in raw_points]
        offset_points.extend(raw_points)
        return offset_points

    @property
    def middle_walloff_depot(self):
        raw_points = sorted(list(self.points), key=lambda x: x.distance_to_point2(self.bottom_center), reverse=True)
        # TODO  its white board time,  need to figure out some geometric intuition here
        intersects = raw_points[0].circle_intersection(p=raw_points[1], r=2.5 ** 0.5)
        # p = self.map_data.closest_towards_point(points=self.buildables.points, target=self.top_center)
        p = max(intersects, key=lambda p: p.distance_to_point2(self.bottom_center))
        return p

    def closest_region(self, region_list):
        """

        Will return the closest region with respect to self

        """
        return min(region_list,
                   key=lambda area: min(self.map_data.distance(area.center, point) for point in self.perimeter_points))

    def set_regions(self):
        """

        Method for calculating the relevant :class:`.Region`

        TODO:
             Make this a private method

        """
        from MapAnalyzer.Region import Region
        for p in self.perimeter_points:
            areas = self.map_data.where_all(p)
            for area in areas:
                # edge case  = its a VisionBlockerArea (and also on the perimeter) so we grab the touching Regions
                if isinstance(area, VisionBlockerArea):
                    for sub_area in area.areas:
                        # add it to our Areas
                        if isinstance(sub_area, Region) and sub_area not in self.areas:
                            self.areas.append(sub_area)
                        # add ourselves to it's Areas
                        if isinstance(sub_area, Region) and self not in sub_area.areas:
                            sub_area.areas.append(self)

                # standard case
                if isinstance(area, Region) and area not in self.areas:
                    self.areas.append(area)
                    # add ourselves to the Region Area's
                if isinstance(area, Region) and self not in area.areas:
                    area.areas.append(self)

        if len(self.regions) < 2:
            region_list = list(self.map_data.regions.values())
            region_list.remove(self.regions[0])
            closest_region = self.closest_region(region_list=region_list)
            assert (closest_region not in self.regions)
            self.areas.append(closest_region)

    @property
    def top_center(self) -> Point2:
        """

        Alerts when sc2 fails to provide a top_center, and fallback to  :meth:`.center`

        """
        if self.ramp.top_center is not None:
            return self.ramp.top_center
        else:
            logger.debug(f"No top_center found for {self}, falling back to `center`")
            return self.center

    @property
    def bottom_center(self) -> Point2:
        """

        Alerts when sc2 fails to provide a bottom_center, and fallback to  :meth:`.center`

        """
        if self.ramp.bottom_center is not None:
            return self.ramp.bottom_center
        else:
            logger.debug(f"No bottom_center found for {self}, falling back to `center`")
            return self.center

    def __repr__(self) -> str:  # pragma: no cover
        return f"<MDRamp[size={self.area}] {str(self.regions)}>"

    def __str__(self):
        return f"R[{self.area}]"


class VisionBlockerArea(ChokeArea):
    """

    VisionBlockerArea are areas containing tiles that hide the units that stand in it,

    (for example,  bushes)

    Units that attack from within a :class:`VisionBlockerArea`

    cannot be targeted by units that do not stand inside
    """

    def __init__(self, map_data: "MapData", array: np.ndarray) -> None:
        super().__init__(map_data=map_data, array=array)
        self.is_vision_blocker = True

    def __repr__(self):  # pragma: no cover
        return f"<VisionBlockerArea[size={self.area}]: {self.regions}>"
