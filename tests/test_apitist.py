class TestApitist:
    def test_(self):
        from apitist import apitist

        assert getattr(apitist, "__author__", None)
        assert getattr(apitist, "__license__", None)
        assert getattr(apitist, "__copyright__", None)
