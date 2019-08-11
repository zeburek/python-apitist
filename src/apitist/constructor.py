import attr
import cattr
import pendulum


def _subclass(typ):
    """ a shortcut """
    return lambda cls: issubclass(cls, typ)


def _structure_date_time(isostring, _):
    """Structure hook for :class:`pendulum.DateTime`"""
    if isinstance(isostring, str):
        return pendulum.parse(isostring)
    else:
        return None


def _unstructure_date_time(dt):
    """Unstructure hook for :class:`pendulum.DateTime`"""
    if isinstance(dt, pendulum.DateTime):
        return dt.to_rfc3339_string()
    else:
        return None


class Converter(cattr.Converter):
    """Converts between structured and unstructured data."""

    def set_dict_factory(self, dict_factory):
        self._dict_factory = dict_factory

    def register_hooks(self, cls, structure, unstructure):
        """
        Register primitive-to-class and class-to-primitive converter
        functions for a class.

        The structure function should take two arguments:
          * a Python object to be converted,
          * the type to convert to

        and return the instance of the class. The type may seem redundant, but
        is sometimes needed (for example, when dealing with generic classes).

        The unstructure function should take an instance of the class and
        return its Python equivalent.

        """
        self.register_structure_hook(cls, structure)
        self.register_unstructure_hook(cls, unstructure)

    def register_hooks_funcs(self, check_func, structure, unstructure):
        """
        Register primitive-to-class and class-to-primitive converter functions
        for a class, using a function to check if it's a match.
        """
        self.register_structure_hook_func(check_func, structure)
        self.register_unstructure_hook_func(check_func, unstructure)

    def register_additional_hooks(self):
        """
        Register additional hooks:

        * :class:`str` - all its instances would be structured
          and unstructured as :class:`str`
        * :class:`pendulum.DateTime` - datetime would be parsed using pendulum
          and unstructured in RFC3339 format
        """
        self.register_hooks_funcs(
            _subclass(str), self._unstructure_identity, self._structure_call
        )
        self.register_hooks(
            pendulum.DateTime, _structure_date_time, _unstructure_date_time
        )


class NothingDict(dict):
    """
    Default dict for unstructuring

    It is used for unstructuring Type with ignoring some fields.
    If given field is :class:`attr.NOTHING` - it would not be unstructured in
    dict.
    """

    def __setitem__(self, key, value):
        if value == attr.NOTHING:
            return
        super().__setitem__(key, value)


converter = Converter()
converter.set_dict_factory(NothingDict)
converter.register_additional_hooks()
