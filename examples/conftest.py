import pytest

from apitist.hooks import ResponseMonitoringHook
from apitist.requests import session


@pytest.fixture(scope="session")
def api():
    s = session()
    s.add_hook(ResponseMonitoringHook)
    return s
