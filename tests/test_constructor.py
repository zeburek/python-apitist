from dataclasses import MISSING, dataclass, field
from typing import List

import pytest

import attr
import pendulum

from apitist.constructor import (
    ConverterType,
    MissingDict,
    NothingDict,
    _structure_date_time,
    _subclass,
    _unstructure_date_time,
)
from apitist.decorators import transform


class TypeStr(str):
    pass


@attr.s
class ExampleData:
    test: TypeStr = attr.ib()
    example: pendulum.DateTime = attr.ib(default=None)


@dataclass
class ExampleDataclass:
    test: TypeStr
    example: pendulum.DateTime = field(default=None)


class TestConstructor:
    @pytest.mark.parametrize(
        "t,verify_type,result",
        [
            (str, str, True),
            (str, TypeStr, True),
            (int, str, False),
            (int, TypeStr, False),
        ],
    )
    def test_subclass(self, t, verify_type, result):
        assert _subclass(t)(verify_type) == result

    def test_structure_date_time(self):
        isostring = "2019-03-06T14:58:10.123+0500"
        datetime = _structure_date_time(isostring, None)
        assert datetime

    @pytest.mark.parametrize("value", [0, {}, [], None])
    def test_structure_date_time_none(self, value):
        datetime = _structure_date_time(value, None)
        assert datetime is None

    @pytest.mark.parametrize(
        "datetime,result",
        [
            (
                pendulum.parse("2019-03-06T14:58:10.123+0500"),
                "2019-03-06T14:58:10.123000+05:00",
            ),
            (
                pendulum.parse("2019-03-06T14:58:10"),
                "2019-03-06T14:58:10+00:00",
            ),
            (pendulum.parse("2019-03-06"), "2019-03-06T00:00:00+00:00"),
        ],
    )
    def test_unstructure_date_time(self, datetime, result):
        datetime = _unstructure_date_time(datetime)
        assert datetime == result

    @pytest.mark.parametrize("value", [0, {}, [], None])
    def test_unstructure_date_time_none(self, value):
        datetime = _unstructure_date_time(value)
        assert datetime is None

    def test_converter_additional_hooks(self, converter):
        data = {"test": TypeStr("test"), "example": "2019-03-06T14:58:10"}
        _type = (
            ExampleData
            if converter._converter_type == ConverterType.ATTRS
            else ExampleDataclass
        )
        with pytest.raises(ValueError):
            converter.structure(data, _type)
        converter.register_additional_hooks()
        assert converter.structure(data, _type)

    def test_converter_list(self, converter):
        data = [{"test": TypeStr("test"), "example": "2019-03-06T14:58:10"}]
        _type = (
            ExampleData
            if converter._converter_type == ConverterType.ATTRS
            else ExampleDataclass
        )
        converter.register_additional_hooks()
        assert converter.structure(data, List[_type])

    @pytest.mark.parametrize(
        "value,result", [("test", True), (0, True), (attr.NOTHING, False)]
    )
    def test_nothing_dict_set_item(self, value, result):
        dict_ = NothingDict()
        dict_["test"] = value
        assert bool(dict_) == result

    @pytest.mark.parametrize(
        "value,result", [("test", True), (0, True), (MISSING, False)]
    )
    def test_missing_dict_set_item(self, value, result):
        dict_ = MissingDict()
        dict_["test"] = value
        assert bool(dict_) == result

    @pytest.mark.parametrize(
        "value,result", [("test", "test"), (0, "0"), (None, None)]
    )
    def test_structure_call(self, converter, value, result):
        assert converter._structure_call(value, str) == result


class TestToType:
    def test_attrs(self):
        @transform
        @attr.s
        class Type1:
            field1: str = attr.ib()
            field2: int = attr.ib()
            field3: List[str] = attr.ib()

        @transform
        @attr.s
        class Type2:
            field2: int = attr.ib()
            field3: List[str] = attr.ib()

        @transform
        @attr.s
        class Type3:
            field1: str = attr.ib()
            field2: Type1 = attr.ib()
            field3: List[str] = attr.ib()

        @transform
        @attr.s
        class Type4:
            field2: Type2 = attr.ib()
            field3: List[str] = attr.ib()

        t1 = Type1("one", 2, ["three"])
        t2 = Type2(2, ["three"])
        t3 = Type3("one", t1, ["three"])
        t4 = Type4(t2, ["three"])

        assert t1.to_type(Type2) == t2
        assert t3.to_type(Type4) == t4

    def test_dataclass(self):
        @transform
        @dataclass
        class Type1:
            field1: str
            field2: int
            field3: List[str]

        @transform
        @dataclass
        class Type2:
            field2: int
            field3: List[str]

        @transform
        @dataclass
        class Type3:
            field1: str
            field2: Type1
            field3: List[str]

        @transform
        @dataclass
        class Type4:
            field2: Type2
            field3: List[str]

        t1 = Type1("one", 2, ["three"])
        t2 = Type2(2, ["three"])
        t3 = Type3("one", t1, ["three"])
        t4 = Type4(t2, ["three"])

        assert t1.to_type(Type2) == t2
        assert t3.to_type(Type4) == t4
