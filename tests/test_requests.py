import pytest

import requests_mock
from requests_mock import NoMockAddress

from apitist import decorators as deco
from apitist import session


class ExampleClient:
    def __init__(self, hostname):
        self.session = session(hostname)

    @deco.get("/get")
    def get(self):
        ...

    @deco.delete("/delete")
    def delete(self):
        ...

    @deco.options("/options")
    def options(self):
        ...

    @deco.head("/head")
    def head(self):
        ...

    @deco.patch("/patch")
    def patch(self):
        ...

    @deco.patch("/patch", headers={"Accept-type": "text/plain"})
    def patch_with_headers(self):
        ...

    @deco.post("/post")
    def post(self):
        return {
            "data": "hello world",
        }

    @deco.put("/put")
    def put(self, json=None):
        return {"json": json}


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

    @pytest.mark.parametrize(
        "method", ["get", "post", "put", "delete", "options", "head", "patch"]
    )
    def test_decorators(self, method):
        host = "https://httpbin.org"
        client = ExampleClient(host)

        with requests_mock.Mocker() as m:
            m.register_uri(method.upper(), f"{host}/{method}", text="mocked")
            res = getattr(client, method)()
            assert res.text == "mocked"

    def test_decorators_modificators(self):
        host = "https://httpbin.org"
        client = ExampleClient(host)

        with requests_mock.Mocker() as m:
            m.register_uri("POST", f"{host}/post", text="mocked")
            client.post()
            req = m.request_history[0]
            assert req.text == "hello world"

    def test_passing_function_parameters(self):
        host = "https://httpbin.org"
        client = ExampleClient(host)

        with requests_mock.Mocker() as m:
            m.register_uri("PUT", f"{host}/put", text="mocked")
            data = {"data": "Hello world!"}
            client.put(data)
            req = m.request_history[0]
            assert req.json() == data

    def test_passing_deco_parameters(self):
        host = "https://httpbin.org"
        client = ExampleClient(host)

        with requests_mock.Mocker() as m:
            m.register_uri("PATCH", f"{host}/patch", text="mocked")
            client.patch_with_headers()
            req = m.request_history[0]
            assert req.headers["Accept-type"] == "text/plain"
