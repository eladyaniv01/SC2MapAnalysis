import pytest
from tests.test_docs import map_data

#
# def pytest_collection_finish(session):
#     """Handle the pytest collection finish hook: configure pyannotate.
#     Explicitly delay importing `collect_types` until all tests have
#     been collected.  This gives gevent a chance to monkey patch the
#     world before importing pyannotate.
#     """
#     from pyannotate_runtime import collect_types
#
#     collect_types.init_types_collection()
#
#
# @pytest.fixture(autouse=True)
# def collect_types_fixture():
#     from pyannotate_runtime import collect_types
#
#     collect_types.start()
#     yield
#     collect_types.stop()
#
#
# def pytest_sessionfinish(session, exitstatus):
#     from pyannotate_runtime import collect_types
#
#     collect_types.dump_stats("type_info.json")


@pytest.fixture(autouse=True)
def add_map_data(doctest_namespace):
    doctest_namespace["self"] = map_data
