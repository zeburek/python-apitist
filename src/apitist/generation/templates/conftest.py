import pytest

from api.client import TestClient


def pytest_addoption(parser):
    group = parser.getgroup("TestClient tests configuration")
    group.addoption("--hostname", help="TestClient hostname")


@pytest.fixture(scope="session")
def client(request):
    hostname = request.config.getoption("--hostname")
    client = TestClient(hostname)
    return client
