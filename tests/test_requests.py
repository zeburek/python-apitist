import pytest

import requests_mock
from requests_mock import NoMockAddress
from tests.test_hooks import ExampleResponseDataclass

from apitist import ResponseDataclassConverterHook
from apitist import decorators as deco
from apitist import session
from apitist.requests import SharedSession


class ExampleClient:
    def __init__(self, hostname):
        self.session = session(hostname)
        self.session.add_hook(ResponseDataclassConverterHook)

    @deco.get("/get")
    def get(self):
        ...

    @deco.get("/get/{}")
    def get_id(self, id):
        ...

    @deco.get("/get/{}?well={well}")
    def get_id_and_query(self, id, well=None):
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

    @deco.post("/post", structure_type=ExampleResponseDataclass)
    def post_with_converter(self):
        ...

    @deco.post("/post", structure_type=SharedSession)
    def post_with_wrong_converter(self, **kwargs):
        return dict(**kwargs)

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

    def test_formatting(self):
        host = "https://httpbin.org"
        client = ExampleClient(host)

        with requests_mock.Mocker() as m:
            m.register_uri("GET", f"{host}/get/1", text="mocked")
            res = client.get_id(1)
            assert res.text == "mocked"

    def test_formatting_2(self):
        host = "https://httpbin.org"
        client = ExampleClient(host)

        with requests_mock.Mocker() as m:
            m.register_uri("GET", f"{host}/get/1?well=known", text="mocked")
            res = client.get_id_and_query(1, well="known")
            assert res.text == "mocked"

    def test_structuring(self):
        host = "https://httpbin.org"
        client = ExampleClient(host)

        res = client.post_with_converter()
        assert isinstance(res.data, ExampleResponseDataclass)

    def test_structuring_override(self):
        host = "https://httpbin.org"
        client = ExampleClient(host)

        res = client.post_with_wrong_converter(
            structure_type=ExampleResponseDataclass
        )
        assert isinstance(res.data, ExampleResponseDataclass)

    def test_shared_state(self):
        s1 = session("https://google.com")
        s2 = session("https://yandex.ru")

        ss = SharedSession(s1)
        ss.add_sessions(s2)

        s2.get("/?q=2113")

        assert s1.cookies == s2.cookies

        s1.get("/?q=124")

        assert s1.cookies == s2.cookies

    def test_shared_state_incorrect_session(self):
        s1 = session("https://google.com")
        s2 = "123"

        ss = SharedSession(s1)
        with pytest.raises(ValueError):
            ss.add_sessions(s2)

    def test_non_class_function(self):
        @deco.get("/test")
        def test():
            ...

        with pytest.raises(Exception):
            test()

    def test_class_miss_session(self):
        class Test:
            @deco.get("/test")
            def test(self):
                ...

        with pytest.raises(Exception):
            Test().test()

    def test_class_wrong_modificators_returned(self):
        class Test:
            session = session("https://httpbin.org")

            @deco.get("/get")
            def test(self):
                return list()

        with pytest.raises(Exception):
            Test().test()
