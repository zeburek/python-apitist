import ast

from apitist.generation.formatter import CodeFormatter

f = formatter = CodeFormatter()


def dummy_parse(string):
    return ast.parse(string).body[0]


def init_session():
    return dummy_parse(
        """\\
    def init_session():
        s = Session()
        s.add_hook(PrepRequestInfoLoggingHook)
        s.add_hook(ResponseInfoLoggingHook)
        return s
    """
    ).body[0]


def api_client(project):
    return dummy_parse(
        f.format(
            """\\
    class {project}Client:
        host: str = attr.ib()
        _s: Session = attr.ib(factory=attr.Factory(init_session))
    """,
            project=project,
        )
    )


def endpoint_path(method, name, path):
    return dummy_parse(
        f.format(
            """\\
    {method!u}_{name!u} = "{path}"
    """,
            method=method,
            name=name,
            path=path,
        )
    )


def endpoint_func(
    method, name, arguments="", additional_funcs="", req_args=""
):
    return dummy_parse(
        f.format(
            """\\
            def {method!l}_{name!l}(self{arguments}):
                {additional_funcs}
                return self._s.{method!l}(self.host + self.{method!u}_{name!u}\
                {req_args})
            """,
            method=method,
            name=name,
            arguments=arguments,
            additional_funcs=additional_funcs,
            req_args=req_args,
        )
    )
