import json
from urllib import parse

from requests import Response

from apitist.hooks import ResponseMonitoringHook


class ApitistPlugin:
    base = {}
    requests = {}

    def __init__(self):
        self.base = {
            "openapi": "3.0.1",
            "info": {
                "title": "Example API",
                "description": "Example API produced by Apitist",
                "version": "0.1.0",
            },
        }

    def parse_url(self, response: Response) -> parse.ParseResultBytes:
        return parse.urlparse(response.request.url)

    def add_request(self, response: Response):
        parsed = self.parse_url(response)
        path = parsed.path
        method = response.request.method.lower()
        status = response.status_code
        try:
            content = response.content.decode("utf-8")
            try:
                content = json.dumps(json.loads(content), indent=4)
            except Exception:
                content = "non-parsable"
        except Exception:
            content = "binary"
        if path in self.requests:
            methods = self.requests.get(path)
            if method in methods:
                statuses = methods.get(method).get("responses")
                if status in statuses:
                    return
                else:
                    statuses[status] = {"description": content}
            else:
                methods[method] = {
                    "responses": {status: {"description": content}}
                }
        else:
            self.requests[path] = {
                method: {"responses": {status: {"description": content}}}
            }

    def pytest_sessionfinish(self, session, exitstatus):
        responses = ResponseMonitoringHook._responses
        for response in responses:
            self.add_request(response)
        result = {**self.base, "paths": self.requests}
        print(json.dumps(result, indent=4))
