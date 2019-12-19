import attr

from apitist.hooks import PrepRequestInfoLoggingHook, ResponseInfoLoggingHook
from apitist.requests import Session


def init_session():
    s = Session()
    s.add_hook(PrepRequestInfoLoggingHook)
    s.add_hook(ResponseInfoLoggingHook)
    return s


@attr.s
class TestClient:
    hostname: str = attr.ib()
    _s: Session = attr.ib(factory=attr.Factory(init_session))

    def get_request(self, **kwargs):
        return self._s.get(self.hostname + "/get", **kwargs)
