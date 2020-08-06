import logging
import os
import random
from random import randint
from typing import Tuple, Iterable, List

import pytest
import tqdm
from _pytest.python import Metafunc
from hypothesis import given, settings, strategies as st
from loguru import logger

from MapAnalyzer.MapData import MapData
from MapAnalyzer.Region import Region
from MapAnalyzer.Polygon import Polygon
from MapAnalyzer.constructs import ChokeArea, MDRamp, VisionBlockerArea
from MapAnalyzer.utils import mock_map_data
from _pytest.logging import caplog as _caplog

# for merging pr from forks,  git push <pr-repo.git> <your-local-branch-name>:<pr-branch-name>
# pytest -v --disable-warnings
# mutmut run --paths-to-mutate test_suite.py --runner pytest
# radon cc . -a -nb  (will dump only complexity score of B and below)
# monkeytype run monkeytest.py
# monkeytype list-modules
# mutmut run --paths-to-mutate MapAnalyzer/MapData.py

def get_random_point(minx: int, maxx: int, miny: int, maxy: int) -> Tuple[int, int]:
    return (random.randint(minx, maxx), random.randint(miny, maxy))

@pytest.fixture
def caplog(_caplog=_caplog):
    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message}")
    yield _caplog
    logger.remove(handler_id)


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
