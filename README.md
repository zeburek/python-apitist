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
