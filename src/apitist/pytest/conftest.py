from apitist.pytest.plugin import ApitistPlugin


def pytest_configure(config):
    if not hasattr(config, "workerinput"):
        config._apitist = ApitistPlugin()
        config.pluginmanager.register(config._apitist)
