from tests.mocksetup import get_map_datas, get_random_point, logger, MapData, Metafunc


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


class TestPathing:
    """
    Test DocString
    """
    scenarios = [(f"Testing {md.bot.game_info.map_name}", {"map_data": md}) for md in get_map_datas()]

    def test_handle_illegal_values(self, map_data: MapData):
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
        assert (path is not None)

    def test_grid_types(self, map_data: MapData):
        # new feat - grid without rocks
        pass

    def test_sensitivity(self, map_data: MapData):
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

    def test_pathing_influence(self, map_data: MapData, caplog) -> None:
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
