# python-apitist

Brand new way to test your API

# Installation

Actually project is not published on PyPi,
so the only way:
```bash
pip install python-apitist
```

# Default hooks

- RequestDebugLoggingHook
- RequestInfoLoggingHook
- PrepRequestDebugLoggingHook
- PrepRequestInfoLoggingHook
- ResponseDebugLoggingHook
- ResponseInfoLoggingHook

## Example usage

```python
from apitist.hooks import PrepRequestInfoLoggingHook, ResponseInfoLoggingHook
from apitist.requests import session


s = session()
PrepRequestInfoLoggingHook.formatter = "Best formatter {req.method} {req.url}"

s.add_prep_request_hook(PrepRequestInfoLoggingHook)
s.add_response_hook(ResponseInfoLoggingHook)

s.post("https://httpbin.org/post", params={"q": "test"})
```

# Custom Hooks

```python
from requests import Request, PreparedRequest, Response

from apitist.requests import session, RequestHook, PreparedRequestHook, ResponseHook

s = session()

class ReqHook(RequestHook):

    def run(self, request: Request) -> Request:
        print(request.url)
        return request

class PrepReqHook(PreparedRequestHook):

    def run(self, request: PreparedRequest) -> PreparedRequest:
        print(request.url)
        return request


class RespHook(ResponseHook):

    def run(self, response: Response) -> Response:
        print(response.url)
        return response

s.add_request_hook(ReqHook)
s.add_prep_request_hook(PrepReqHook)
s.add_response_hook(RespHook)

s.get("https://ya.ru", params={"q": "test"})
```

# Working with constructor

```python
import attr
import typing

from apitist.constructor import converter
from apitist.hooks import RequestConverterHook, ResponseConverterHook
from apitist.requests import session


class ExampleType:
    test = None

@attr.s
class ExampleStructure:
    test: ExampleType = attr.ib()

@attr.s
class TestResponse:
    args: typing.Dict = attr.ib()
    data: str = attr.ib()
    files: typing.Dict = attr.ib()
    form: typing.Dict = attr.ib()
    headers: typing.Dict = attr.ib()
    json: ExampleStructure = attr.ib()
    origin: str = attr.ib()
    url: str = attr.ib()

s = session()
s.add_hook(RequestConverterHook)
s.add_hook(ResponseConverterHook)

def structure_example_type(data, type_):
    example = ExampleType()
    example.test = data
    return example

def unstructure_example_type(data):
    return data.test

converter.register_hooks(
    ExampleType, structure_example_type, unstructure_example_type
)

t = ExampleType()
t.test = "test"

struc = ExampleStructure(t)

res = s.post("https://httpbin.org/post", data=struc).structure(TestResponse)
print(res.structured.json.test.test) # test
```
