import json
import logging
import typing

import pytest

import attr

from apitist.hooks import (
    PrepRequestDebugLoggingHook,
    PrepRequestInfoLoggingHook,
    RequestConverterHook,
    RequestDebugLoggingHook,
    RequestInfoLoggingHook,
    ResponseConverterHook,
    ResponseDebugLoggingHook,
    ResponseInfoLoggingHook,
)


@attr.s
class ExampleData:
    test: str = attr.ib()


@attr.s
class ExampleResponse:
    args: typing.Dict = attr.ib()
    data: str = attr.ib()
    files: typing.Dict = attr.ib()
    form: typing.Dict = attr.ib()
    headers: typing.Dict = attr.ib()
    json: typing.Any = attr.ib()
    origin: str = attr.ib()
    url: str = attr.ib()


class TestHooks:
    @pytest.mark.usefixtures("enable_debug_logging")
    @pytest.mark.parametrize(
        "hook,text",
        [
            (RequestDebugLoggingHook, "Request"),
            (PrepRequestDebugLoggingHook, "Request"),
            (ResponseDebugLoggingHook, "Response"),
        ],
    )
    def test_debug_logging_hooks(self, session, hook, text, capture):
        session.add_hook(hook)
        session.get("http://httpbin.org/get")
        assert len(capture.records) == 2
        assert capture.records[1].levelno == logging.DEBUG
        assert text in capture.records[1].msg

    @pytest.mark.parametrize(
        "hook,text",
        [
            (RequestInfoLoggingHook, "Request"),
            (PrepRequestInfoLoggingHook, "Request"),
            (ResponseInfoLoggingHook, "Response"),
        ],
    )
    def test_info_logging_hooks(self, session, hook, text, capture):
        session.add_hook(hook)
        session.get("http://httpbin.org/get")
        assert len(capture.records) == 1
        assert capture.records[0].levelno == logging.INFO
        assert text in capture.records[0].msg

    def test_request_converter_attrs_class(self, session):
        session.add_hook(RequestConverterHook)
        res = session.get("http://httpbin.org/get", data=ExampleData("test"))
        assert res.request.body == json.dumps({"test": "test"}).encode("utf-8")

    def test_request_converter_non_attrs(self, session):
        session.add_hook(RequestConverterHook)
        res = session.get("http://httpbin.org/get", data="test")
        assert res.request.body == "test"

    def test_response_converter_adding_function(self, session):
        session.add_hook(ResponseConverterHook)
        res = session.get("http://httpbin.org/get")
        assert getattr(res, "structure")

    def test_response_converter_correct_type(self, session):
        session.add_hook(ResponseConverterHook)
        res = session.post("http://httpbin.org/post")
        res.structure(ExampleResponse)
        assert isinstance(res.structured, ExampleResponse)

    def test_response_converter_incorrect_type(self, session):
        session.add_hook(ResponseConverterHook)
        res = session.post("http://httpbin.org/post")
        with pytest.raises(AttributeError):
            res.structure(ExampleData)
