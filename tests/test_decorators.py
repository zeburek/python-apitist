import pytest

from apitist.decorators import transform


class TestDecorators:
    def test_transform_error(self):
        @transform
        class Test:
            pass

        with pytest.raises(TypeError):
            Test().to_type(str)
