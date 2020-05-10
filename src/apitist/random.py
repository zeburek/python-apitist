import inspect
import random as rnd
import typing

import attr

from apitist.utils import (
    has_args,
    is_attrs_class,
    is_sequence,
    is_tuple,
    is_union_type,
)

from .logging import Logging

T = typing.TypeVar("T")


class Randomer:
    _types_dict = None

    def __init__(self):
        self._types_dict = dict()

    @property
    def available_hooks(self):
        return self._types_dict

    def get_hook(self, t: typing.Type):
        """Get function for given type"""
        func = self._types_dict.get(t)
        if func is None:
            raise TypeError("Unable to find hook for {} type".format(t))
        return func

    def run_hook(self, t: typing.Type, **set_params):
        """Generate random data for given type"""
        func = self.get_hook(t)
        if inspect.getfullargspec(func).varkw:
            Logging.logger.debug(
                "All additional params will be passed to hook: %s", set_params
            )
            res = func(**set_params)
        else:
            res = func()
        Logging.logger.debug("Generated data for type %s: %s", t, res)
        return res

    def add_type(self, t: typing.Type[T], func: typing.Callable[[], T]):
        """
        Add new type for random generation.
        Function should return given type.
        """
        if t in self._types_dict:
            Logging.logger.warning(
                "Type %s already exists in dict, overriding", t
            )
        Logging.logger.debug("Registering type %s with function %s", t, func)
        self._types_dict[t] = func

    def add_types(
        self, types_dict: typing.Dict[typing.Type[T], typing.Callable[[], T]]
    ):
        """
        Add new types for random generation.
        Functions should return given type.
        """
        Logging.logger.debug("Registering list of types: %s", types_dict)
        self._types_dict.update(types_dict)

    def random_object(
        self,
        t: typing.Type[T],
        required_only=False,
        ignore: typing.List[str] = None,
        only: typing.List[str] = None,
        inverse=False,
        **set_params,
    ) -> T:
        """
        Create object of given type with random data

        Be careful, random object does not use converter to create a type
        It may lead to types missmatch

        :param t: Type which would me generated randomly
        :param required_only: Use only fields which do not have default values
        :param ignore: List of fields which should be ignored
            (will be passed to hook kwargs)
        :param only: List of fields which should be used
            (just a workaround near ignore + inverse)
        :param inverse: Inverse ignore list (will be passed to hook kwargs)
        :param set_params: Custom params which would be manually set to type
            (will be passed to hook kwargs)
        :return: Object of given type
        """
        Logging.logger.debug("Generating random data for type %s", t)
        if only and ignore:
            raise ValueError(
                "Only one of parameters - only or ignore should be used"
            )
        if only:
            ignore = only
            inverse = True
        if ignore is None:
            ignore = list()
        if t in self.available_hooks:
            return self.run_hook(
                t, ignore=ignore, inverse=inverse, **set_params
            )
        elif is_attrs_class(t):
            data = {}
            for field in attr.fields(t):
                f_name = field.name
                has_default = field.default is not attr.NOTHING
                if f_name in set_params:
                    data[f_name] = set_params[f_name]
                    continue
                if (
                    (f_name in ignore and inverse is False)
                    or (ignore and f_name not in ignore and inverse is True)
                    or (required_only and has_default)
                ):
                    data[f_name] = field.default if has_default else None
                    continue
                data[f_name] = self.random_object(
                    field.type,
                    required_only=required_only,
                    ignore=ignore,
                    inverse=inverse,
                    **set_params,
                )
            data = t(**data)
            Logging.logger.debug(
                "Generating random data for attrs type %s", data
            )
            return data
        elif is_union_type(t) and has_args(t):
            return self.random_object(
                rnd.choice(t.__args__),
                required_only=required_only,
                ignore=ignore,
                inverse=inverse,
                **set_params,
            )
        elif is_tuple(t) and has_args(t):
            return (
                self.random_object(
                    t.__args__[0],
                    required_only=required_only,
                    ignore=ignore,
                    inverse=inverse,
                    **set_params,
                ),
            )
        elif is_sequence(t) and has_args(t):
            return [
                self.random_object(
                    t.__args__[0],
                    required_only=required_only,
                    ignore=ignore,
                    inverse=inverse,
                    **set_params,
                )
            ]
        return None

    object = random_object

    def random_partial(
        self, t: typing.Type[T], use: list = (), **set_params
    ) -> T:
        """
        Create object of given type with random data with only given fields.
        """
        if t in self.available_hooks:
            return self.run_hook(t, use=use, **set_params)
        elif "__attrs_attrs__" in dir(t):
            data = {}
            for field in attr.fields(t):
                key = field.name

                if set_params and key in set_params:
                    data[key] = set_params[key]
                    continue

                if (
                    use
                    and key not in use
                    and (
                        "__attrs_attrs__" not in dir(field.type)
                        or (
                            "__attrs_attrs__" in dir(field.type)
                            and field.type in self.available_hooks
                        )
                    )
                ):
                    data[key] = attr.NOTHING
                    continue

                data[key] = self.random_partial(field.type, use, **set_params)

            if not all(v == attr.NOTHING for _, v in data.items()):
                return t(**data)
            return attr.NOTHING

        elif is_union_type(t) and has_args(t):
            return self.random_partial(
                rnd.choice(t.__args__), use=use, **set_params
            )
        elif is_tuple(t) and has_args(t):
            return (self.random_partial(t.__args__[0], use=use, **set_params),)
        elif is_sequence(t) and has_args(t):
            return [self.random_partial(t.__args__[0], use=use, **set_params)]
        return None

    partial = random_partial
