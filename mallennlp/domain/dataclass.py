import attr


def dataclass(cls):
    """
    Decorator for quickly creating defining data classes.

    Really just wrapper around `attr.s`, an alternative to the std libs dataclasses.
    """
    if not attr.has(cls):
        cls = attr.s(auto_attribs=True, slots=True)(cls)
    return cls
