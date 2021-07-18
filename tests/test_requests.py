import pytest

import requests_mock
from requests_mock import NoMockAddress

from apitist import session


class TestRequests:
    def test_creation(self):
        host = "hello-world"
        s = session(host)
        assert s.base_url == host

    @pytest.mark.parametrize(
        "path",
        [
            "/get",
            "http/get/else",
            "//hello",
        ],
    )
    def test_request_append_base_url(self, path):
        host = "https://httpbin.org"
        s = session(host)
        with requests_mock.Mocker() as m:
            m.get(f"{host}/{path.lstrip('/')}", text="mocked")
            res = s.get(path)
            assert res.text == "mocked"

    @pytest.mark.parametrize(
        "path",
        [
            "http://get",
            "https://hrl.ru",
            "ssh://hello",
        ],
    )
    def test_request_not_append_base_url(self, path):
        host = "https://httpbin.org"
        s = session(host)
        with requests_mock.Mocker() as m:
            with pytest.raises(NoMockAddress):
                m.get(f"{host}/{path.lstrip('/')}", text="mocked")
                s.get(path)
