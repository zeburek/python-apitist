import logging
import typing

import pytest

import attr

from apitist.constructor import converter


class TypeStr(str):
    pass


@attr.s
class Child:
    value1: int = attr.ib()
    value2: typing.List[str] = attr.ib()
    value3: typing.Tuple[str] = attr.ib(default=tuple())
    value4: str = attr.ib(default=None)
    value5: typing.Union[int] = attr.ib(default=None)


@attr.s
class Data:
    val1: str = attr.ib()
    val2: Child = attr.ib()
    val3: str = attr.ib(default=None)


class TestRandomer:
    def test_add_type(self, randomer):
        def func():
            return "test"

        randomer.add_type(str, func)
        assert randomer.available_hooks == {str: func}

    def test_add_type_exists(self, randomer, capture):
        def func():
            return "test"

        randomer.add_type(str, func)
        randomer.add_type(str, func)
        assert capture.records[0].levelno == logging.WARN

    def test_add_types(self, randomer):
        def func():
            return "test"

        randomer.add_types({str: func})
        assert randomer.available_hooks == {str: func}

    def test_get_hook_exists(self, random):
        assert random.get_hook(str)

    def test_get_hook_not_exists(self, random):
        with pytest.raises(TypeError):
            random.get_hook(list)

    def test_run_hook_exists(self, random):
        assert random.run_hook(str)

    def test_run_hook_not_exists(self, random):
        with pytest.raises(TypeError):
            random.run_hook(list)

    def test_run_hook_one_subclass(self, randomer):
        def func():
            return "test"

        def func2():
            return "test2"

        randomer.add_type(str, func)
        randomer.add_type(TypeStr, func2)
        assert randomer.run_hook(str) == "test"
        assert randomer.run_hook(TypeStr) == "test2"

    @pytest.mark.parametrize(
        "key,value",
        [
            ("str", "str"),
            ("int", 10),
            ("list", ["some", "data"]),
            ("dict", {"key": 100, "val": {10, 12, 13}}),
        ],
    )
    def test_run_hook_kwargs_pass(self, randomer, key, value):
        def func(**kwargs):
            if kwargs.get(key):
                return kwargs.get(key)
            return "test"

        randomer.add_type(str, func)
        assert randomer.run_hook(str) == "test"
        assert randomer.run_hook(str, **{key: value}) == value

    @pytest.mark.parametrize(
        "type_,object_",
        [
            (Child, Child(50, ["test"], ("test",), "test", 50)),
            (
                Data,
                Data(
                    "test", Child(50, ["test"], ("test",), "test", 50), "test"
                ),
            ),
        ],
    )
    def test_random_object(self, random, type_, object_):
        assert random.object(type_) == object_

    def test_random_object_missing_type(self, random):
        assert random.object(dict) is None

    @pytest.mark.parametrize(
        "type_,object_",
        [
            (Child, Child(50, ["test"], tuple(), None)),
            (Data, Data("test", Child(50, ["test"], tuple(), None), None)),
        ],
    )
    def test_random_object_required_only(self, random, type_, object_):
        assert random.object(type_, required_only=True) == object_

    @pytest.mark.parametrize(
        "type_,ignore,object_",
        [
            (Child, ["value1"], Child(None, ["test"], ("test",), "test", 50)),
            (
                Data,
                ["value1", "val1"],
                Data(
                    None, Child(None, ["test"], ("test",), "test", 50), "test"
                ),
            ),
            (Data, ["value1", "val2"], Data("test", None, "test")),
        ],
    )
    def test_random_object_ignore(self, random, type_, ignore, object_):
        assert random.object(type_, ignore=ignore) == object_

    @pytest.mark.parametrize(
        "type_,ignore,object_",
        [
            (Child, ["value1"], Child(50, None, tuple(), None)),
            (Data, ["value1", "val1"], Data("test", None, None)),
            (
                Data,
                ["value1", "val2"],
                Data(None, Child(50, None, tuple(), None), None),
            ),
        ],
    )
    def test_random_object_ignore_inverse(
        self, random, type_, ignore, object_
    ):
        assert random.object(type_, ignore=ignore, inverse=True) == object_

    @pytest.mark.parametrize(
        "type_,ignore,object_",
        [
            (Child, ["value1"], Child(50, None, tuple(), None)),
            (Data, ["value1", "val1"], Data("test", None, None)),
            (
                Data,
                ["value1", "val2"],
                Data(None, Child(50, None, tuple(), None), None),
            ),
        ],
    )
    def test_random_object_only(self, random, type_, ignore, object_):
        assert random.object(type_, only=ignore) == object_

    def test_random_object_only_ignore(self, random):
        with pytest.raises(ValueError):
            random.object(Data, only=["value1"], ignore=["value2"])

    @pytest.mark.parametrize(
        "type_,object_,params",
        [
            (
                Child,
                Child(560, ["test"], ("test",), "test", 50),
                {"value1": 560},
            ),
            (
                Data,
                Data(
                    "rest", Child(560, ["test"], ("test",), "test", 50), "test"
                ),
                {"value1": 560, "val1": "rest"},
            ),
        ],
    )
    def test_random_object_set_params(self, random, type_, object_, params):
        assert random.object(type_, **params) == object_

    def test_random_object_union(self, random):
        @attr.s
        class NewObj:
            value1: typing.Union[int, str] = attr.ib()
            value2: typing.Optional[str] = attr.ib()

        for _ in range(20):
            assert converter.unstructure(random.object(NewObj)).get(
                "value1"
            ) in ["test", 50]
            assert converter.unstructure(random.object(NewObj)).get(
                "value2"
            ) in ["test", None]

    @pytest.mark.parametrize(
        "type_,use,exp_data",
        [
            (Child, ["value1"], {"value1": 50}),
            (Child, ["value2"], {"value2": ["test"]}),
            (Child, ["value3"], {"value3": ("test",)}),
            (Child, ["value4"], {"value4": "test"}),
            (Child, ["value5"], {"value5": 50}),
            (Data, ["val1"], {"val1": "test"}),
            (
                Data,
                ["val1", "value2"],
                {"val1": "test", "val2": {"value2": ["test"]}},
            ),
        ],
    )
    def test_random_partial(self, random, type_, use, exp_data):
        data = random.partial(type_, use=use)
        assert converter.unstructure(data) == exp_data

    def test_random_partial_missing_type(self, random):
        assert random.partial(dict) is None

    @pytest.mark.parametrize(
        "type_,use,params,exp_data",
        [
            (
                Child,
                ["value1"],
                {"value2": "rest"},
                {"value1": 50, "value2": "rest"},
            ),
            (
                Data,
                ["val1"],
                {"value2": "rest"},
                {"val1": "test", "val2": {"value2": "rest"}},
            ),
        ],
    )
    def test_random_partial_set_param(
        self, random, type_, use, params, exp_data
    ):
        data = random.partial(type_, use=use, **params)
        assert converter.unstructure(data) == exp_data

    @pytest.mark.parametrize(
        "use,exp_data",
        [
            (["value4"], {"value4": "test"}),
            (
                ["value3", "value6"],
                {"value5": {"value3": {"data": 120}}, "value6": {"data": 120}},
            ),
        ],
    )
    def test_random_partial_attrs_custom_hook(self, random, use, exp_data):
        @attr.s
        class Child2:
            value1: int = attr.ib()

        @attr.s
        class Child1:
            value2: int = attr.ib()
            value3: Child2 = attr.ib()

        @attr.s
        class Parent:
            value4: str = attr.ib()
            value5: Child1 = attr.ib()
            value6: Child2 = attr.ib()

        random.add_type(Child2, lambda: {"data": 120})

        data = random.partial(Parent, use=use)
        assert converter.unstructure(data) == exp_data

    def test_random_partial_union(self, random):
        @attr.s
        class NewObj:
            value1: typing.Union[int, str] = attr.ib()
            value2: int = attr.ib()

        for _ in range(10):
            assert converter.unstructure(
                random.partial(NewObj, use=["value1"])
            ) in [{"value1": 50}, {"value1": "test"}]
