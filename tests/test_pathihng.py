import os

from _pytest.logging import LogCaptureFixture
from _pytest.python import Metafunc

from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import get_map_files_folder, mock_map_data
from tests.mocksetup import get_map_datas, get_random_point, logger

logger = logger


# From https://docs.pytest.org/en/latest/example/parametrize.html#a-quick-port-of-testscenarios
def pytest_generate_tests(metafunc: Metafunc) -> None:
    global argnames
    idlist = []
    argvalues = []
    if metafunc.cls is not None:
        for scenario in metafunc.cls.scenarios:
            idlist.append(scenario[0])
            items = scenario[1].items()
            argnames = [x[0] for x in items]
            argvalues.append(([x[1] for x in items]))
        metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


def test_climber_grid() -> None:
    """assert that we can path through climb cells with climber grid,
    but not with normal grid"""
    import pathlib
    li = sorted(pathlib.Path('..').glob('**/*GoldenWallLE.xz'))
    path = li[0].absolute()
    map_data = mock_map_data(path)
    start = (150, 95)
    goal = (110, 40)
    grid = map_data.get_pyastar_grid()
    path = map_data.pathfind(start=start, goal=goal, grid=grid)
    assert (path is None)
    grid = map_data.get_climber_grid()
    path = map_data.pathfind(start=start, goal=goal, grid=grid)
    assert (path is None)


def test_minerals_walls() -> None:
    # attempting to path through mineral walls in goldenwall should fail
    import pathlib
    li = sorted(pathlib.Path('..').glob('**/*GoldenWallLE.xz'))
    # path = os.path.join(get_map_files_folder(), 'GoldenWallLE.xz')
    path = li[0].absolute()
    # logger.info(path)
    map_data = mock_map_data(path)
    start = (110, 95)
    goal = (110, 40)
    grid = map_data.get_pyastar_grid()
    path = map_data.pathfind(start=start, goal=goal, grid=grid)
    assert (path is None)
    # also test climber grid for nonpathables
    grid = map_data.get_climber_grid()
    path = map_data.pathfind(start=start, goal=goal, grid=grid)
    assert (path is None)

    # attempting to path through tight pathways near destructables should work
    path = os.path.join(get_map_files_folder(), 'AbyssalReefLE.xz')
    map_data = mock_map_data(path)
    start = (130, 25)
    goal = (125, 47)
    grid = map_data.get_pyastar_grid()
    path = map_data.pathfind(start=start, goal=goal, grid=grid)
    assert (path is not None)


class TestPathing:
    """
    Test DocString
    """
    scenarios = [(f"Testing {md.bot.game_info.map_name}", {"map_data": md}) for md in get_map_datas()]

    def test_region_connectivity(self, map_data: MapData) -> None:
        base = map_data.bot.townhalls[0]
        region = map_data.where(base.position_tuple)
        destination = map_data.where(map_data.bot.enemy_start_locations[0].position)
        all_possible_paths = map_data.region_connectivity_all_paths(start_region=region,
                                                                    goal_region=destination)
        for p in all_possible_paths:
            assert (destination in p), f"destination = {destination}"

        bad_request = map_data.region_connectivity_all_paths(start_region=region,
                                                             goal_region=destination,
                                                             not_through=[destination])
        assert (bad_request == [])

    def test_handle_illegal_values(self, map_data: MapData) -> None:
        base = map_data.bot.townhalls[0]
        reg_start = map_data.where(base.position_tuple)
        reg_end = map_data.where(map_data.bot.enemy_start_locations[0].position)
        p0 = reg_start.center
        p1 = reg_end.center
        pts = []
        r = 10
        for i in range(50):
            pts.append(get_random_point(-500, -250, -500, -250))

        arr = map_data.get_pyastar_grid()
        for p in pts:
            arr = map_data.add_influence(p, r, arr)
        path = map_data.pathfind(p0, p1, grid=arr)
        assert (path is not None), f"path = {path}"

    def test_grid_types(self, map_data: MapData) -> None:
        # new feat - grid without rocks
        pass

    def test_sensitivity(self, map_data: MapData) -> None:
        base = map_data.bot.townhalls[0]
        reg_start = map_data.where(base.position_tuple)
        reg_end = map_data.where(map_data.bot.enemy_start_locations[0].position)
        p0 = reg_start.center
        p1 = reg_end.center
        arr = map_data.get_pyastar_grid()
        path_pure = map_data.pathfind(p0, p1, grid=arr)
        path_sensitive_5 = map_data.pathfind(p0, p1, grid=arr, sensitivity=5)
        path_sensitive_1 = map_data.pathfind(p0, p1, grid=arr, sensitivity=1)
        assert (len(path_sensitive_5) < len(path_pure))
        assert (p in path_pure for p in path_sensitive_5)
        assert (path_sensitive_1 == path_pure)

    def test_pathing_influence(self, map_data: MapData, caplog: LogCaptureFixture) -> None:
        logger.info(map_data)
        base = map_data.bot.townhalls[0]
        reg_start = map_data.where(base.position_tuple)
        reg_end = map_data.where(map_data.bot.enemy_start_locations[0].position)
        p0 = reg_start.center
        p1 = reg_end.center
        pts = []
        r = 10
        for i in range(50):
            pts.append(get_random_point(0, 200, 0, 200))

        arr = map_data.get_pyastar_grid()
        for p in pts:
            arr = map_data.add_influence(p, r, arr)
        path = map_data.pathfind(p0, p1, grid=arr)
        assert (path is not None)
