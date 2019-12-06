from jinja2 import Environment, PackageLoader


class GenerationBackend:
    def __init__(self):
        self.env = Environment(
            loader=PackageLoader("apitist", "/generation/templates"),
            keep_trailing_newline=True,
        )
        self.vars = {}

    def add_variable(self, var, val):
        self.vars[var] = val

    def render_template(self, template_name):
        return self.env.get_template(template_name).render(**self.vars)
