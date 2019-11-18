import types
from typing import Type

import attr
from requests import PreparedRequest, Request, Response

from apitist.utils import is_attrs_class

from .constructor import converter
from .logging import Logging
from .requests import PreparedRequestHook, RequestHook, ResponseHook


class RequestDebugLoggingHook(RequestHook):
    formatter = "Request {req.method} {req.url} {req.data}"

    def run(self, request: Request) -> Request:
        Logging.logger.debug(self.formatter.format(req=request))
        return request


class RequestInfoLoggingHook(RequestHook):
    formatter = "Request {req.method} {req.url} {req.data}"

    def run(self, request: Request) -> Request:
        Logging.logger.info(self.formatter.format(req=request))
        return request


class PrepRequestDebugLoggingHook(PreparedRequestHook):
    formatter = "Request {req.method} {req.url} {req.body}"

    def run(self, request: PreparedRequest) -> PreparedRequest:
        Logging.logger.debug(self.formatter.format(req=request))
        return request


class PrepRequestInfoLoggingHook(PreparedRequestHook):
    formatter = "Request {req.method} {req.url} {req.body}"

    def run(self, request: PreparedRequest) -> PreparedRequest:

        Logging.logger.info(self.formatter.format(req=request))
        return request


class ResponseDebugLoggingHook(ResponseHook):
    formatter = (
        "Response {res.status_code} {res.request.method} "
        "{res.url} {res.content}"
    )

    def run(self, response: Response) -> Response:
        Logging.logger.debug(self.formatter.format(res=response))
        return response


class ResponseInfoLoggingHook(ResponseHook):
    formatter = (
        "Response {res.status_code} {res.request.method} "
        "{res.url} {res.content}"
    )

    def run(self, response: Response) -> Response:
        Logging.logger.info(self.formatter.format(res=response))
        return response


class RequestConverterHook(RequestHook):
    def run(self, request: Request) -> Request:
        if is_attrs_class(request.data):
            request.json = converter.unstructure(request.data)
            request.data = None
        return request


class ResponseConverterHook(ResponseHook):
    def run(self, response: Response) -> Response:
        def func(self, t: Type) -> Response:
            try:
                self.data = converter.structure(self.json(), t)
            except TypeError as e:
                fields = attr.fields_dict(t)
                raise TypeError(
                    f"Got miss-matched parameters in dicts. "
                    f"Info about first level:"
                    f"\n\tExpect: {sorted(fields)}"
                    f"\n\tActual: {sorted(dict(self.json()).keys())}"
                    f"\n\nOriginal exception: {e}"
                )
            return self

        response.structure = types.MethodType(func, response)
        return response
