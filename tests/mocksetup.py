import logging
import os
import random
from typing import Iterable, List

import pytest
from _pytest.logging import caplog as _caplog
from loguru import logger

from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import mock_map_data


def get_random_point(minx, maxx, miny, maxy):
    return (random.randint(minx, maxx), random.randint(miny, maxy))


@pytest.fixture
def caplog(_caplog=_caplog):
    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message}")
    yield _caplog
    logger.remove(handler_id)


def get_map_file_list() -> List[str]:
    """
    easy way to produce less than all maps,  for example if we want to test utils, we only need one MapData object
    """
    subfolder = "MapAnalyzer"
    subfolder2 = "pickle_gameinfo"
    subfolder = os.path.join(subfolder, subfolder2)
    folder = os.path.abspath(".")
    map_files_folder = os.path.join(folder, subfolder)
    map_files = os.listdir(map_files_folder)
    li = []
    for map_file in map_files:
        li.append(os.path.join(map_files_folder, map_file))
    return li


def get_map_datas() -> Iterable[MapData]:
    subfolder = "MapAnalyzer"
    subfolder2 = "pickle_gameinfo"
    subfolder = os.path.join(subfolder, subfolder2)
    if "tests" in os.path.abspath("."):
        folder = os.path.dirname(os.path.abspath("."))
    else:
        folder = os.path.abspath(".")
    map_files_folder = os.path.join(folder, subfolder)
    map_files = os.listdir(map_files_folder)
    for map_file in map_files:
        yield mock_map_data(map_file=os.path.join(map_files_folder, map_file))
