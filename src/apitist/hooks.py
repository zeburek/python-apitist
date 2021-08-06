import dataclasses
import types
from typing import Type

import attr
from requests import PreparedRequest, Request, Response

from apitist.utils import is_attrs_class

from .constructor import convclass, converter
from .logging import Logging
from .requests import PreparedRequestHook, RequestHook, ResponseHook


class RequestDebugLoggingHook(RequestHook):
    formatter = "Request {req.method} {req.url} {req.data}"

    def run(self, request: Request) -> Request:
        formatter = self.formatter
        if request.name:
            formatter = self.formatter.replace("req.url", "req.name", 1)
        Logging.logger.debug(formatter.format(req=request))
        return request


class RequestInfoLoggingHook(RequestHook):
    formatter = "Request {req.method} {req.url} {req.data}"

    def run(self, request: Request) -> Request:
        formatter = self.formatter
        if request.name:
            formatter = self.formatter.replace("req.url", "req.name", 1)
        Logging.logger.info(formatter.format(req=request))
        return request


class PrepRequestDebugLoggingHook(PreparedRequestHook):
    formatter = "Request {req.method} {req.url} {req.body}"

    def run(self, request: PreparedRequest) -> PreparedRequest:
        formatter = self.formatter
        if request.name:
            formatter = self.formatter.replace("req.url", "req.name", 1)
        Logging.logger.debug(formatter.format(req=request))
        return request


class PrepRequestInfoLoggingHook(PreparedRequestHook):
    formatter = "Request {req.method} {req.url} {req.body}"

    def run(self, request: PreparedRequest) -> PreparedRequest:
        formatter = self.formatter
        if request.name:
            formatter = self.formatter.replace("req.url", "req.name", 1)
        Logging.logger.info(formatter.format(req=request))
        return request


class ResponseDebugLoggingHook(ResponseHook):
    formatter = (
        "Response {res.status_code} {res.request.method} "
        "{res.url} {res.content}"
    )

    def run(self, response: Response) -> Response:
        formatter = self.formatter
        if response.name:
            formatter = self.formatter.replace("res.url", "res.name", 1)
        Logging.logger.debug(formatter.format(res=response))
        return response


class ResponseInfoLoggingHook(ResponseHook):
    formatter = (
        "Response {res.status_code} {res.request.method} "
        "{res.url} {res.content}"
    )

    def run(self, response: Response) -> Response:
        formatter = self.formatter
        if response.name:
            formatter = self.formatter.replace("res.url", "res.name", 1)
        Logging.logger.info(formatter.format(res=response))
        return response


def request_converter_hook(conv) -> Type[RequestHook]:
    class _RequestHook(RequestHook):
        def run(self, request: Request) -> Request:
            if is_attrs_class(request.data):
                request.json = conv.unstructure(request.data)
                request.data = None
            elif dataclasses.is_dataclass(request.data):
                request.json = conv.unstructure(request.data)
                request.data = None
            return request

    return _RequestHook


RequestAttrsConverterHook: Type[RequestHook] = request_converter_hook(
    converter
)
RequestDataclassConverterHook: Type[RequestHook] = request_converter_hook(
    convclass
)
RequestConverterHook = RequestAttrsConverterHook


def throw_response_missmatch(fields, res: Response, exp):
    raise TypeError(
        f"Got miss-matched parameters in dicts. "
        f"Info about first level:"
        f"\n\tExpect: {sorted(fields)}"
        f"\n\tActual: {sorted(dict(res.json()).keys())}"
        f"\n\nOriginal exception: {exp}"
    )


def response_converter_hook(conv) -> Type[ResponseHook]:
    class _ResponseHook(ResponseHook):
        def run(self, response: Response) -> Response:
            def func(self, t: Type) -> Response:
                try:
                    self.data = conv.structure(self.json(), t)
                except (TypeError, ValueError) as e:
                    if is_attrs_class(t):
                        fields = attr.fields_dict(t)
                        throw_response_missmatch(fields, self, e)
                    elif dataclasses.is_dataclass(t):
                        fields = dataclasses.fields(t)
                        throw_response_missmatch(
                            [f.name for f in fields], self, e
                        )
                    raise e
                return self

            response.structure = types.MethodType(func, response)
            return response

    return _ResponseHook


ResponseAttrsConverterHook: Type[ResponseHook] = response_converter_hook(
    converter
)
ResponseDataclassConverterHook: Type[ResponseHook] = response_converter_hook(
    convclass
)
ResponseConverterHook = ResponseAttrsConverterHook
