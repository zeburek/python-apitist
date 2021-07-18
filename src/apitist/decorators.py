import functools

from apitist.requests import Session


def request(method, url, **deco_kwargs):
    print(url)

    def _decorate(function):
        @functools.wraps(function)
        def wrapped_function(*args, **kwargs):
            if len(args) < 1 or function.__repr__ in dir(args[0]):
                raise Exception(
                    "You should decorate only methods of the class"
                )
            obj = args[0]
            if not getattr(obj, "session", None):
                raise Exception("Base class should define `session`")
            s: Session = getattr(obj, "session")
            modificator = function(*args, **kwargs)
            if not isinstance(modificator, dict) and modificator is not None:
                raise Exception(
                    "Modificator should be a dict of request parameters, not:",
                    modificator,
                )
            return s.request(
                method,
                url,
                **(modificator if isinstance(modificator, dict) else {}),
                **deco_kwargs,
            )

        return wrapped_function

    return _decorate


def get(url, **kwargs):
    return request("GET", url, **kwargs)


def options(url, **kwargs):
    return request("OPTIONS", url, **kwargs)


def head(url, **kwargs):
    return request("HEAD", url, **kwargs)


def post(url, **kwargs):
    return request("POST", url, **kwargs)


def put(url, **kwargs):
    return request("PUT", url, **kwargs)


def patch(url, **kwargs):
    return request("PATCH", url, **kwargs)


def delete(url, **kwargs):
    return request("DELETE", url, **kwargs)