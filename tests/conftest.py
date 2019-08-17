import logging

import pytest

from testfixtures import LogCapture

from apitist import logging as log
from apitist.constructor import Converter
from apitist.random import Randomer
from apitist.requests import Session


@pytest.fixture
def converter():
    return Converter()


@pytest.fixture
def session():
    return Session()


@pytest.fixture
def randomer():
    return Randomer()


@pytest.fixture
def random():
    rand = Randomer()
    rand.add_type(str, lambda: "test")
    rand.add_type(int, lambda: 50)
    return rand


@pytest.fixture()
def capture():
    with LogCapture() as capture:
        yield capture


@pytest.fixture()
def enable_debug_logging():
    log._logger.setLevel(logging.DEBUG)
    yield
    log._logger.setLevel(log.LOG_LEVEL)
