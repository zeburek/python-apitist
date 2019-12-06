import os
from pathlib import Path

from apitist.generation.backend import GenerationBackend


class Combinator:
    def create_dirs(self, path, exist_ok=False):
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        os.makedirs(path, exist_ok)
        os.chmod(path, 0o777)

    def touch_file(self, file_path, exist_ok=False):
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        Path(file_path).touch(exist_ok=exist_ok)

    def save_template(self, file_path, content):
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        Path(file_path).write_text(content, encoding="utf-8")

    def create_single_service_project(
        self,
        project_dir,
        project_name,
        tox_config=True,
        tests_dir=True,
        tests_example=True,
    ):
        self.create_dirs(project_dir)
        self.touch_file(os.path.join(project_dir, "conftest.py"))
        self.create_dirs(os.path.join(project_dir, "api"))
        self.touch_file(os.path.join(project_dir, "api", "client.py"))
        if tests_dir:
            self.create_dirs(os.path.join(project_dir, "tests"))
            if tests_example:
                self.touch_file(
                    os.path.join(project_dir, "tests", "test_example.py")
                )
        if tox_config:
            self.touch_file(os.path.join(project_dir, "tox.ini"))
        gen = GenerationBackend()
        gen.add_variable("project_name", project_name)
        self.save_template(
            os.path.join(project_dir, "api", "client.py"),
            gen.render_template("client_single_service.py.j2"),
        )
        self.save_template(
            os.path.join(project_dir, "conftest.py"),
            gen.render_template("conftest.py.j2"),
        )
        if tox_config:
            self.save_template(
                os.path.join(project_dir, "tox.ini"),
                gen.render_template("tox.ini.j2"),
            )
        self.save_template(
            os.path.join(project_dir, "requirements.txt"),
            gen.render_template("requirements.txt.j2"),
        )
