from string import Formatter


class CodeFormatter(Formatter):
    """
    An extended format string formatter

    Formatter with extended conversion symbol
    """

    def convert_field(self, value, conversion):
        """
        Extend conversion symbol

        Following additional symbol has been added

        * l: convert to string and low case
        * u: convert to string and up case

        default are:

        * s: convert with str()
        * r: convert with repr()
        * a: convert with ascii()
        """

        if conversion == "u":
            return str(value).upper()
        elif conversion == "l":
            return str(value).lower()
        # Do the default conversion
        # or raise error if no matching conversion found
        super().convert_field(value, conversion)

        return value
