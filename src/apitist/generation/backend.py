import ast
from typing import Union

from astor import to_source
from black import FileMode, format_str

from apitist.generation.formatter import CodeFormatter
from apitist.generation.templates import code


class GenerationBackend:
    def __init__(self, line_length=79):
        self.module = ast.Module(body=[])
        self.module.body = []
        self.imports = []
        self.black_mode = FileMode(line_length=line_length)
        self.f = self.formatter = CodeFormatter()

    def add_import(self, *value: Union[ast.Import, ast.ImportFrom]):
        self.imports.extend(value)

    def add_node(self, *function: ast.stmt):
        self.module.body.extend(function)

    def _get_last_field_position(self, cls: ast.ClassDef):
        no_func = 0
        for node in cls.body:
            if isinstance(node, ast.FunctionDef):
                return no_func
            no_func += 1
        return no_func

    def add_new_api_function(self, api_cls: ast.ClassDef, method, name, path):
        name = name.replace(" ", "_")
        endpoint_path = code.endpoint_path(method, name, path)
        endpoint_func = code.endpoint_func(method, name)
        api_cls.body.insert(
            self._get_last_field_position(api_cls), endpoint_path
        )
        api_cls.body.append(endpoint_func)

    def get_code(self, debug=False):
        self.module.body = self.imports + self.module.body

        ast.fix_missing_locations(self.module)

        code = to_source(
            self.module, indent_with=" " * 4, add_line_information=debug
        )
        code = format_str(code, mode=self.black_mode)
        return code
